import json

import plotly.graph_objs as go
import pytest
import requests

from zndraw import ZnDraw

# --- Test Data ---
# Dummy figure data for testing purposes.
FIGURE_1 = {"type": "line", "points": [0, 0, 1, 1], "color": "#FF0000"}
FIGURE_2 = {"type": "circle", "center": [5, 5], "radius": 10, "color": "#0000FF"}


# --- Tests for POST /api/rooms/<room_id>/figures ---


def test_create_figure_success(server):
    """
    Tests successful creation of a new figure.
    """
    room_id = "room-create-success"
    figure_key = "line-01"

    response = requests.post(
        f"{server}/api/rooms/{room_id}/figures",
        json={"key": figure_key, "figure": FIGURE_1},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success"}


def test_create_figure_missing_key(server):
    """
    Tests API response when 'key' is missing from the POST body.
    """
    room_id = "room-create-no-key"

    response = requests.post(
        f"{server}/api/rooms/{room_id}/figures",
        json={"figure": FIGURE_1},  # 'key' is missing
    )

    assert response.status_code == 400
    data = response.json()
    assert data["type"] == "ValueError"
    assert "Both 'key' and 'figure' are required" in data["error"]


def test_create_figure_missing_figure_data(server):
    """
    Tests API response when 'figure' data is missing from the POST body.
    """
    room_id = "room-create-no-figure"
    figure_key = "line-01"

    response = requests.post(
        f"{server}/api/rooms/{room_id}/figures",
        json={"key": figure_key},  # 'figure' is missing
    )

    assert response.status_code == 400
    data = response.json()
    assert data["type"] == "ValueError"
    assert "Both 'key' and 'figure' are required" in data["error"]


def test_overwrite_existing_figure(server):
    """
    Tests that creating a figure with an existing key overwrites the old data.
    """
    room_id = "room-overwrite"
    figure_key = "shape-to-overwrite"

    # Create initial figure
    requests.post(
        f"{server}/api/rooms/{room_id}/figures",
        json={"key": figure_key, "figure": FIGURE_1},
    )

    # Overwrite with new data
    response = requests.post(
        f"{server}/api/rooms/{room_id}/figures",
        json={"key": figure_key, "figure": FIGURE_2},
    )
    assert response.status_code == 200

    # Verify that the data was updated
    response = requests.get(f"{server}/api/rooms/{room_id}/figures/{figure_key}")
    assert response.status_code == 200
    assert response.json()["figure"] == FIGURE_2


# --- Tests for GET /api/rooms/<room_id>/figures/<key> ---


def test_get_figure_success(server):
    """
    Tests successful retrieval of a single, existing figure.
    """
    room_id = "room-get-success"
    figure_key = "circle-01"

    # Setup: Create the figure first
    requests.post(
        f"{server}/api/rooms/{room_id}/figures",
        json={"key": figure_key, "figure": FIGURE_2},
    )

    # Test: Retrieve the figure
    response = requests.get(f"{server}/api/rooms/{room_id}/figures/{figure_key}")

    assert response.status_code == 200
    assert response.json() == {"key": figure_key, "figure": FIGURE_2}


def test_get_figure_not_found(server):
    """
    Tests API response when requesting a figure key that does not exist.
    """
    room_id = "room-get-not-found"
    non_existent_key = "does-not-exist"

    response = requests.get(f"{server}/api/rooms/{room_id}/figures/{non_existent_key}")

    assert response.status_code == 404
    data = response.json()
    assert data["type"] == "KeyError"
    assert f"Figure with key '{non_existent_key}' not found" in data["error"]


# --- Tests for DELETE /api/rooms/<room_id>/figures/<key> ---


def test_delete_figure_success(server):
    """
    Tests successful deletion of an existing figure.
    """
    room_id = "room-delete-success"
    figure_key = "figure-to-delete"

    # Setup: Create the figure
    requests.post(
        f"{server}/api/rooms/{room_id}/figures",
        json={"key": figure_key, "figure": FIGURE_1},
    )

    # Test: Delete the figure
    response = requests.delete(f"{server}/api/rooms/{room_id}/figures/{figure_key}")
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # Verify: Try to get the deleted figure
    verify_response = requests.get(f"{server}/api/rooms/{room_id}/figures/{figure_key}")
    assert verify_response.status_code == 404


def test_delete_figure_not_found(server):
    """
    Tests API response when attempting to delete a non-existent figure.
    """
    room_id = "room-delete-not-found"
    non_existent_key = "does-not-exist"

    response = requests.delete(
        f"{server}/api/rooms/{room_id}/figures/{non_existent_key}"
    )

    assert response.status_code == 404
    data = response.json()
    assert data["type"] == "KeyError"
    assert f"Figure with key '{non_existent_key}' does not exist" in data["error"]


# --- Tests for GET /api/rooms/<room_id>/figures ---


def test_list_figures_success(server):
    """
    Tests listing all figure keys in a room with multiple figures.
    """
    room_id = "room-list-success"
    keys_to_create = {"line-1", "circle-5", "line-8"}

    # Setup: Create multiple figures
    for key in keys_to_create:
        requests.post(
            f"{server}/api/rooms/{room_id}/figures",
            json={"key": key, "figure": FIGURE_1},
        )

    # Test: Get the list of all figure keys
    response = requests.get(f"{server}/api/rooms/{room_id}/figures")

    assert response.status_code == 200
    data = response.json()
    # Use sets to compare keys regardless of order
    assert set(data["figures"]) == keys_to_create


def test_list_figures_empty(server):
    """
    Tests listing figures from a room that has no figures.
    """
    room_id = "room-list-empty"

    response = requests.get(f"{server}/api/rooms/{room_id}/figures")

    assert response.status_code == 200
    assert response.json() == {"figures": []}


def test_vis_figures(server):
    vis = ZnDraw(url=server, room="test-vis-figures", user="tester")
    fig1 = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))
    fig2 = go.Figure(data=go.Bar(x=[1, 2, 3], y=[6, 5, 4]))
    vis.figures["fig1"] = fig1
    vis.figures["fig2"] = fig2

    assert set(list(vis.figures)) == {"fig1", "fig2"}
    assert vis.figures.keys() == {"fig1", "fig2"}

    assert vis.figures["fig1"].to_dict() == fig1.to_dict()
    assert vis.figures["fig2"].to_dict() == fig2.to_dict()

    del vis.figures["fig1"]
    assert set(list(vis.figures)) == {"fig2"}

    response = requests.get(f"{server}/api/rooms/test-vis-figures/figures/fig2")
    assert response.status_code == 200
    assert response.json()["figure"]["type"] == "plotly"
    # stored as json, because fig.to_json() is save to serialize, fig.to_dict() is not
    assert json.loads(response.json()["figure"]["data"]) == fig2.to_dict()
    assert response.json()["key"] == "fig2"


def test_vis_figures_sync(server):
    vis1 = ZnDraw(url=server, room="test-vis-figures-sync", user="tester1")
    vis2 = ZnDraw(url=server, room="test-vis-figures-sync", user="tester2")

    fig1 = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))
    fig2 = go.Figure(data=go.Bar(x=[1, 2, 3], y=[6, 5, 4]))
    vis1.figures["fig1"] = fig1
    vis1.figures["fig2"] = fig2

    assert set(list(vis1.figures)) == {"fig1", "fig2"}
    assert set(list(vis2.figures)) == {"fig1", "fig2"}

    assert vis1.figures["fig1"].to_dict() == fig1.to_dict()
    assert vis1.figures["fig2"].to_dict() == fig2.to_dict()
    assert vis2.figures["fig1"].to_dict() == fig1.to_dict()
    assert vis2.figures["fig2"].to_dict() == fig2.to_dict()

    del vis1.figures["fig1"]
    assert set(list(vis1.figures)) == {"fig2"}
    assert set(list(vis2.figures)) == {"fig2"}

    del vis2.figures["fig2"]
    assert set(list(vis1.figures)) == set()
    assert set(list(vis2.figures)) == set()


def test_vis_figures_errors(server):
    vis = ZnDraw(url=server, room="test-vis-figures-errors", user="tester")

    with pytest.raises(ValueError):
        vis.figures["nonexistent"] = "not a figure"

    with pytest.raises(KeyError):
        _ = vis.figures["nonexistent"]

    with pytest.raises(KeyError):
        del vis.figures["nonexistent"]
