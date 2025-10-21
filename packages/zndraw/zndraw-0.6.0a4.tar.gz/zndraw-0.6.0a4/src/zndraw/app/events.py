import json
import logging
import typing as t

from flask import current_app, request
from flask_socketio import emit

from zndraw.server import socketio

from .constants import SocketEvents
from .redis_keys import ExtensionKeys

log = logging.getLogger(__name__)

# for crash handling.
TOKEN_EXPIRY_SECONDS = 10


def _get_len() -> dict:
    sid = request.sid
    r = current_app.extensions["redis"]
    room = get_project_room_from_session(sid)

    if not room:
        return {"success": False, "error": "Client has not joined a room."}

    try:
        indices_key = f"room:{room}:trajectory:indices"
        # Count is the number of entries in the mapping (logical frames)
        frame_count = r.zcard(indices_key)
        return {"success": True, "count": frame_count}
    except Exception as e:
        log.error(f"Failed to get frame count: {e}")
        return {"success": False, "error": "Failed to get frame count"}


# --- Helper Functions ---
def get_project_room_from_session(sid: str) -> t.Optional[str]:
    """Finds the project room a client has joined from Redis using the new schema."""
    r = current_app.extensions["redis"]
    # Get clientId from sid
    client_id = r.get(f"sid:{sid}")
    if not client_id:
        return None
    # Get room from client data
    room_name = r.hget(f"client:{client_id}", "currentRoom")
    return room_name if room_name else None


def get_client_id_from_sid(sid: str) -> t.Optional[str]:
    """Gets the client_id for a given Socket.IO sid using the new schema."""
    r = current_app.extensions["redis"]
    client_id = r.get(f"sid:{sid}")
    return client_id if client_id else None


def get_lock_key(room: str, target: str) -> str:
    """Constructs a standardized Redis key for a lock."""
    return f"room:{room}:lock:{target}"


@socketio.on("connect")
def handle_connect(auth):
    """Handle socket connection with token-based authentication."""
    from flask_socketio import join_room

    sid = request.sid
    r = current_app.extensions["redis"]

    # Get join token from auth
    join_token = auth.get("token") if auth else None

    if not join_token:
        log.warning(f"Client {sid} connected without join token")
        return {"status": "error", "message": "Join token required"}

    # Validate token and get client info
    token_key = f"join_token:{join_token}"
    token_data = r.get(token_key)

    if not token_data:
        log.error(f"Invalid or expired join token: {join_token}")
        return {"status": "error", "message": "Invalid or expired join token"}

    # Parse token data
    token_info = json.loads(token_data)
    client_id = token_info["clientId"]
    room_id = token_info["roomId"]
    user_name = token_info["userName"]

    # Delete token (one-time use)
    r.delete(token_key)

    # Update connection lookup: sid -> clientId
    r.set(f"sid:{sid}", client_id)

    # Update client's currentSid
    client_key = f"client:{client_id}"
    r.hset(client_key, "currentSid", sid)

    # Join socket rooms
    join_room(f"room:{room_id}")
    join_room(f"user:{user_name}")

    log.info(
        f"Client {client_id} ({user_name}) connected to room {room_id} (sid: {sid})"
    )

    return {"status": "ok"}


@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    r = current_app.extensions["redis"]

    # Get client_id from connection lookup
    client_id = r.get(f"sid:{sid}")

    if not client_id:
        log.info(f"Client disconnected: {sid} (no clientId found)")
        return

    # Get client data
    client_key = f"client:{client_id}"
    user_name = r.hget(client_key, "userName")
    room_name = r.hget(client_key, "currentRoom")

    log.info(
        f"Client disconnected: sid={sid}, clientId={client_id}, user={user_name}, room={room_name}"
    )

    # Clean up connection lookup
    r.delete(f"sid:{sid}")

    # Update client's currentSid to empty (client still exists but disconnected)
    r.hset(client_key, "currentSid", "")

    # Note: We don't remove the client from the room or delete client data
    # The client may reconnect and rejoin the same room
    # Only when a client explicitly joins a different room do we remove them from the old room

    if room_name:
        # Notify room that a user has disconnected (but not left)
        clients_in_room = r.smembers(f"room:{room_name}:clients")
        emit(
            "room_clients_update",
            {"clients": list(clients_in_room)},
            to=f"room:{room_name}",
        )
    else:
        log.info(f"Client {client_id} disconnected (was not in a room)")

    # --- Existing Lock Cleanup Logic ---
    lock_keys = r.scan_iter("*:lock:*")
    for key in lock_keys:
        if r.get(key) == sid:
            log.warning(
                f"Cleaning up orphaned lock '{key}' held by disconnected client {sid}"
            )
            r.delete(key)

    if room_name:
        lock_key = f"room:{room_name}:presenter_lock"
        presenter_sid = r.get(lock_key)
        if presenter_sid and presenter_sid == sid:
            r.delete(lock_key)
            # Inform everyone that the presenter left
            emit("presenter_update", {"presenterSid": None}, to=f"room:{room_name}")

    # Extension cleanup - use client_id if available, otherwise fall back to sid for backwards compatibility
    worker_id = client_id if client_id else sid
    extension_categories = ["modifiers", "selections", "analysis"]
    log.info(
        f"Cleaning up extensions for worker_id={worker_id} in room '{room_name}'..."
    )

    for category in extension_categories:
        user_extensions_key = f"room:{room_name}:extensions:{category}:{worker_id}"
        # This key tells us which extensions this worker_id was providing
        user_extensions = r.smembers(user_extensions_key)

        if not user_extensions:
            continue

        log.info(
            f"Worker {worker_id} was providing extensions in '{category}': {user_extensions}"
        )

        extensions_to_delete = []

        with r.pipeline() as pipe:
            for ext_name in user_extensions:
                keys = ExtensionKeys.for_extension(room_name, category, ext_name)
                idle_key = keys.idle_workers
                progressing_key = keys.progressing_workers

                # Remove the worker_id from both possible state sets
                pipe.srem(idle_key, worker_id)
                pipe.srem(progressing_key, worker_id)

                # Check the combined cardinality of both sets to see if the extension is orphaned
                pipe.scard(idle_key)
                pipe.scard(progressing_key)

            # Each extension now produces 4 results in the pipeline
            results = pipe.execute()

        # Iterate through the results to decide which extensions to delete
        for i, ext_name in enumerate(user_extensions):
            # Get the scard results for this extension
            remaining_idle = results[i * 4 + 2]
            remaining_progressing = results[i * 4 + 3]
            total_remaining = remaining_idle + remaining_progressing

            log.info(
                f"Extension '{ext_name}': {total_remaining} workers remaining after removing {worker_id}."
            )

            # Only delete extension if no workers AND no jobs in queue
            if total_remaining == 0:
                keys = ExtensionKeys.for_extension(room_name, category, ext_name)
                queue_length = r.llen(keys.queue)

                if queue_length == 0:
                    extensions_to_delete.append(ext_name)
                    log.info(
                        f"Extension '{ext_name}' marked for deletion: no workers, no queued jobs"
                    )
                else:
                    log.info(
                        f"Extension '{ext_name}' kept despite no workers: {queue_length} jobs in queue"
                    )

        # If any extensions are now orphaned, delete them and their state sets
        if extensions_to_delete:
            print(
                f"Deleting orphaned extensions in '{category}': {extensions_to_delete}"
            )
            with r.pipeline() as pipe:
                for ext_name in extensions_to_delete:
                    keys = ExtensionKeys.for_extension(room_name, category, ext_name)
                    # Delete the state sets
                    pipe.delete(keys.idle_workers)
                    pipe.delete(keys.progressing_workers)
                    # Delete the schema from the main hash
                    pipe.hdel(keys.schema, ext_name)
                pipe.execute()

        # Clean up the user-specific reverse-lookup key
        r.delete(user_extensions_key)
        print(f"Cleaned up user-specific extension list: {user_extensions_key}")

        # Notify clients about worker count changes
        # We always invalidate if this worker had any extensions, not just when deleting
        if user_extensions:
            print(
                f"Invalidating schema for category '{category}' in room '{room_name}' "
                f"due to worker disconnect."
            )
            socketio.emit(
                SocketEvents.INVALIDATE_SCHEMA,
                {"roomId": room_name, "category": category},
                to=f"room:{room_name}",
            )


@socketio.on("set_frame_atomic")
def handle_set_frame_atomic(data):
    """
    Handles a single frame jump. REJECTED if a presenter is active.
    """
    room = get_project_room_from_session(request.sid)
    lock_key = f"room:{room}:presenter_lock"
    redis_client = current_app.extensions["redis"]

    if redis_client.get(lock_key) not in [request.sid, None]:
        return {
            "success": False,
            "error": "LockError",
            "message": "Cannot set frame while presenter is active",
        }

    frame = data.get("frame")
    if frame is not None:
        try:
            # Validate and convert to int (Plotly may send float)
            frame_int = int(frame)
            if frame_int < 0:
                return {"success": False, "error": "Frame must be non-negative"}
            redis_client.set(f"room:{room}:current_frame", frame_int)
            emit("frame_update", {"frame": frame_int}, to=f"room:{room}", skip_sid=request.sid)
            return {"success": True}
        except (ValueError, TypeError) as e:
            log.error(f"Invalid frame value: {frame} - {e}")
            return {"success": False, "error": f"Invalid frame value: {frame}"}

    return {"success": False, "error": "Frame parameter missing"}


@socketio.on("set_frame_continuous")
def handle_set_frame_continuous(data):
    """
    Handles continuous frame updates. REQUIRES sender to be the presenter.
    """
    room = get_project_room_from_session(request.sid)
    lock_key = f"room:{room}:presenter_lock"
    redis_client = current_app.extensions["redis"]

    presenter_sid = redis_client.get(lock_key)

    if presenter_sid and presenter_sid == request.sid:
        frame = data.get("frame")
        if frame is not None:
            try:
                # Validate and convert to int (Plotly may send float)
                frame_int = int(frame)
                if frame_int < 0:
                    log.warning(f"Negative frame rejected: {frame_int}")
                    return {"success": False, "error": "Frame must be non-negative"}
                redis_client.set(f"room:{room}:current_frame", frame_int)
                emit(
                    "frame_update",
                    {"frame": frame_int},
                    to=f"room:{room}",
                    skip_sid=request.sid,
                )
                return {"success": True}
            except (ValueError, TypeError) as e:
                log.error(f"Invalid frame value in continuous: {frame} - {e}")
                return {"success": False, "error": f"Invalid frame value: {frame}"}


@socketio.on("request_presenter_token")
def handle_request_presenter_token():
    sid = request.sid
    room = get_project_room_from_session(sid)
    print(f"Presenter token requested by {sid} in room {room}")
    if not room:
        return {"success": False, "reason": "Not in a valid room"}

    lock_key = f"room:{room}:presenter_lock"
    r = current_app.extensions["redis"]

    # --- UPDATED LOGIC ---
    # Get the current holder of the lock
    current_holder = r.get(lock_key)

    # Case 1: No one has the lock, or the requester already has it (renewal)
    if current_holder is None or current_holder == sid:
        # Set (or reset) the lock with the new expiry
        r.set(lock_key, sid, ex=TOKEN_EXPIRY_SECONDS)

        # If this is a brand new presenter, inform the room
        if current_holder is None:
            emit(
                "presenter_update",
                {"presenterSid": sid},
                to=f"room:{room}",
                skip_sid=sid,
            )

        return {"success": True}
    else:
        # Case 2: Someone else has the lock
        return {"success": False, "reason": "Presenter lock is held by another user"}


@socketio.on("release_presenter_token")
def handle_release_presenter_token():
    room = get_project_room_from_session(request.sid)
    lock_key = f"room:{room}:presenter_lock"
    print(f"Presenter token release requested by {request.sid} in room {room}")
    r = current_app.extensions["redis"]

    presenter_sid = r.get(lock_key)

    if presenter_sid and presenter_sid == request.sid:
        r.delete(lock_key)
        emit(
            "presenter_update",
            {"presenterSid": None},
            to=f"room:{room}",
            skip_sid=request.sid,
        )
        return {"success": True}
    else:
        return {"success": False, "error": "Not the current presenter"}


@socketio.on("lock:acquire")
def acquire_lock(data):
    sid = request.sid
    r = current_app.extensions["redis"]
    target = data.get("target")
    ttl = data.get("ttl", 60)  # Default to 60 seconds if not specified
    room = get_project_room_from_session(sid)
    client_id = get_client_id_from_sid(sid)

    if not room or not target or not client_id:
        return {"success": False, "error": "Room, target, or client_id missing"}
    
    # Validate TTL - must not exceed 300 seconds (5 minutes)
    if not isinstance(ttl, (int, float)) or ttl <= 0:
        return {"success": False, "error": "TTL must be a positive number"}
    if ttl > 300:
        return {"success": False, "error": "TTL cannot exceed 300 seconds (5 minutes)"}

    lock_key = get_lock_key(room, target)
    # Store client_id in lock (not sid) so HTTP endpoints can verify
    if r.set(lock_key, client_id, nx=True, ex=int(ttl)):
        log.debug(f"Lock acquired for '{target}' in room '{room}' by client {client_id} (sid:{sid}) with TTL {ttl}s")
        return {"success": True}
    else:
        lock_holder = r.get(lock_key)
        log.info(
            f"Lock for '{target}' in room '{room}' already held by {lock_holder}, denied for {client_id} (sid:{sid})"
        )
        return {"success": False}


@socketio.on("lock:release")
def release_lock(data):
    sid = request.sid
    r = current_app.extensions["redis"]
    target = data.get("target")
    room = get_project_room_from_session(sid)
    client_id = get_client_id_from_sid(sid)

    if not room or not target or not client_id:
        return {"success": False, "error": "Room, target, or client_id missing"}

    lock_key = get_lock_key(room, target)
    lock_holder = r.get(lock_key)
    # Compare with client_id (not sid) since that's what we store
    if lock_holder == client_id:
        r.delete(lock_key)

        log.debug(f"Lock released for '{target}' in room '{room}' by client {client_id} (sid:{sid})")
        return {"success": True}

    log.warning(
        f"Failed release: Lock for '{target}' in room '{room}' held by {lock_holder}, not by {client_id} (sid:{sid})"
    )
    return {"success": False}


@socketio.on("lock:refresh")
def refresh_lock(data):
    """Refresh the TTL of an existing lock to prevent expiration during long operations."""
    sid = request.sid
    r = current_app.extensions["redis"]
    target = data.get("target")
    ttl = data.get("ttl", 60)  # Default to 60 seconds if not specified
    room = get_project_room_from_session(sid)
    client_id = get_client_id_from_sid(sid)

    if not room or not target or not client_id:
        return {"success": False, "error": "Room, target, or client_id missing"}
    
    # Validate TTL - must not exceed 300 seconds (5 minutes)
    if not isinstance(ttl, (int, float)) or ttl <= 0:
        return {"success": False, "error": "TTL must be a positive number"}
    if ttl > 300:
        return {"success": False, "error": "TTL cannot exceed 300 seconds (5 minutes)"}

    lock_key = get_lock_key(room, target)
    lock_holder = r.get(lock_key)
    
    # Only refresh if the lock is held by this client (compare with client_id)
    if lock_holder == client_id:
        # Reset the TTL
        r.expire(lock_key, int(ttl))
        log.debug(f"Lock refreshed for '{target}' in room '{room}' by client {client_id} (sid:{sid}) with TTL {ttl}s")
        return {"success": True}
    
    log.warning(
        f"Failed refresh: Lock for '{target}' in room '{room}' not held by {sid}"
    )
    return {"success": False}


@socketio.on("chat:message:create")
def handle_chat_message_create(data):
    """
    Create a new chat message.
    Payload: { "content": "message text" }
    Returns: { "success": bool, "message": Message | None, "error": str | None }
    """
    from .chat_utils import create_message

    sid = request.sid
    r = current_app.extensions["redis"]
    room = get_project_room_from_session(sid)

    if not room:
        return {"success": False, "error": "Client has not joined a room."}

    content = data.get("content")
    if not content or not isinstance(content, str):
        return {"success": False, "error": "Message content is required"}

    # Get user ID from session using new schema: sid -> clientId -> userName
    client_id = get_client_id_from_sid(sid)
    if not client_id:
        return {"success": False, "error": "Client not found"}

    user_id = r.hget(f"client:{client_id}", "userName")
    if not user_id:
        return {"success": False, "error": "User not found"}

    try:
        # Create message using helper function
        message = create_message(r, room, user_id, content)

        # Emit to room (excluding sender)
        emit("chat:message:new", message, to=f"room:{room}", include_self=True)

        return {"success": True, "message": message}
    except Exception as e:
        log.error(f"Failed to create chat message: {e}")
        return {"success": False, "error": str(e)}


@socketio.on("chat:message:edit")
def handle_chat_message_edit(data):
    """
    Edit an existing chat message.
    Payload: { "messageId": "msg_room_42", "content": "new text" }
    Returns: { "success": bool, "message": Message | None, "error": str | None }
    """
    from .chat_utils import get_message, update_message

    sid = request.sid
    r = current_app.extensions["redis"]
    room = get_project_room_from_session(sid)

    if not room:
        return {"success": False, "error": "Client has not joined a room."}

    message_id = data.get("messageId")
    content = data.get("content")

    if not message_id or not isinstance(message_id, str):
        return {"success": False, "error": "Message ID is required"}

    if not content or not isinstance(content, str):
        return {"success": False, "error": "Message content is required"}

    # Get user ID from session using new schema: sid -> clientId -> userName
    client_id = get_client_id_from_sid(sid)
    if not client_id:
        return {"success": False, "error": "Client not found"}

    user_id = r.hget(f"client:{client_id}", "userName")
    if not user_id:
        return {"success": False, "error": "User not found"}

    try:
        # Fetch existing message
        existing_message = get_message(r, room, message_id)
        if not existing_message:
            return {"success": False, "error": "Message not found"}

        # Authorization check: verify user owns the message
        if existing_message["author"]["id"] != user_id:
            return {
                "success": False,
                "error": "You can only edit your own messages",
            }

        # Update message
        updated_message = update_message(r, room, message_id, content)

        # Emit to room
        emit("chat:message:updated", updated_message, to=f"room:{room}")

        return {"success": True, "message": updated_message}
    except Exception as e:
        log.error(f"Failed to edit chat message: {e}")
        return {"success": False, "error": str(e)}
