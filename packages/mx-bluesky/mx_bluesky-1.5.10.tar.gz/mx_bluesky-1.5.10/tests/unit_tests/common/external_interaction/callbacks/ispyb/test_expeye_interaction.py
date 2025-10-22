from typing import Any
from unittest.mock import ANY, patch

import pytest
from event_model.documents import Event
from requests import JSONDecodeError

from mx_bluesky.common.external_interaction.ispyb.exp_eye_store import (
    BearerAuth,
    BLSampleStatus,
    ExpeyeInteraction,
    _get_base_url_and_token,
    create_update_data_from_event_doc,
)
from mx_bluesky.common.utils.exceptions import ISPyBDepositionNotMade


def test_get_url_and_token_returns_expected_data():
    url, token = _get_base_url_and_token()
    assert url == "http://blah"
    assert token == "notatoken"


@patch("mx_bluesky.common.external_interaction.ispyb.exp_eye_store.post")
def test_when_start_load_called_then_correct_expected_url_posted_to_with_expected_data(
    mock_post,
):
    expeye_interactor = ExpeyeInteraction()
    expeye_interactor.start_robot_action("LOAD", "test", 3, 700)

    mock_post.assert_called_once()
    assert (
        mock_post.call_args.args[0]
        == "http://blah/proposals/test/sessions/3/robot-actions"
    )
    expected_data = {
        "startTimestamp": ANY,
        "actionType": "LOAD",
        "sampleId": 700,
    }
    assert mock_post.call_args.kwargs["json"] == expected_data


@patch("mx_bluesky.common.external_interaction.ispyb.exp_eye_store.post")
def test_when_start_called_then_returns_id(mock_post):
    mock_post.return_value.json.return_value = {"robotActionId": 190}
    expeye_interactor = ExpeyeInteraction()
    robot_id = expeye_interactor.start_robot_action("LOAD", "test", 3, 700)
    assert robot_id == 190


@patch("mx_bluesky.common.external_interaction.ispyb.exp_eye_store.post")
def test_when_bad_response_no_json_handled_correctly(mock_post):
    mock_post.return_value.ok = False
    mock_post.return_value.json.side_effect = JSONDecodeError("Unable to decode", "", 0)

    expeye_interactor = ExpeyeInteraction()
    with pytest.raises(ISPyBDepositionNotMade):
        expeye_interactor.start_robot_action("LOAD", "test", 3, 700)


@patch("mx_bluesky.common.external_interaction.ispyb.exp_eye_store.post")
def test_when_start_load_called_then_use_correct_token(
    mock_post,
):
    expeye_interactor = ExpeyeInteraction()
    expeye_interactor.start_robot_action("LOAD", "test", 3, 700)

    assert isinstance(auth := mock_post.call_args.kwargs["auth"], BearerAuth)
    assert auth.token == "notatoken"


@patch("mx_bluesky.common.external_interaction.ispyb.exp_eye_store.post")
def test_given_server_does_not_respond_when_start_load_called_then_error(mock_post):
    mock_post.return_value.ok = False

    expeye_interactor = ExpeyeInteraction()
    with pytest.raises(ISPyBDepositionNotMade):
        expeye_interactor.start_robot_action("LOAD", "test", 3, 700)


@patch("mx_bluesky.common.external_interaction.ispyb.exp_eye_store.patch")
def test_when_end_robot_action_called_with_success_then_correct_expected_url_posted_to_with_expected_data(
    # mocks HTTP PATCH
    mock_patch,
):
    expeye_interactor = ExpeyeInteraction()
    expeye_interactor.end_robot_action(3, "success", "")

    mock_patch.assert_called_once()
    assert mock_patch.call_args.args[0] == "http://blah/robot-actions/3"
    expected_data = {
        "endTimestamp": ANY,
        "status": "SUCCESS",
        "message": "",
    }
    assert mock_patch.call_args.kwargs["json"] == expected_data


@patch("mx_bluesky.common.external_interaction.ispyb.exp_eye_store.patch")
def test_when_end_robot_action_called_with_failure_then_correct_expected_url_posted_to_with_expected_data(
    mock_patch,
):
    expeye_interactor = ExpeyeInteraction()
    expeye_interactor.end_robot_action(3, "fail", "bad")

    mock_patch.assert_called_once()
    assert mock_patch.call_args.args[0] == "http://blah/robot-actions/3"
    expected_data = {
        "endTimestamp": ANY,
        "status": "ERROR",
        "message": "bad",
    }
    assert mock_patch.call_args.kwargs["json"] == expected_data


@patch("mx_bluesky.common.external_interaction.ispyb.exp_eye_store.patch")
def test_when_end_robot_action_called_then_use_correct_token(
    mock_patch,
):
    expeye_interactor = ExpeyeInteraction()
    expeye_interactor.end_robot_action(3, "success", "")

    assert isinstance(auth := mock_patch.call_args.kwargs["auth"], BearerAuth)
    assert auth.token == "notatoken"


@patch("mx_bluesky.common.external_interaction.ispyb.exp_eye_store.patch")
def test_given_server_does_not_respond_when_end_robot_action_called_then_error(
    mock_patch,
):
    mock_patch.return_value.ok = False

    expeye_interactor = ExpeyeInteraction()
    with pytest.raises(ISPyBDepositionNotMade):
        expeye_interactor.end_robot_action(1, "", "")


@patch("mx_bluesky.common.external_interaction.ispyb.exp_eye_store.patch")
def test_when_update_robot_action_called_with_success_then_correct_expected_url_posted_to_with_expected_data(
    mock_patch,
):
    expeye_interactor = ExpeyeInteraction()
    expected_data = {
        "sampleBarcode": "test",
        "xtalSnapshotBefore": "/tmp/before.jpg",
        "xtalSnapshotAfter": "/tmp/after.jpg",
    }
    expeye_interactor.update_robot_action(3, expected_data)

    mock_patch.assert_called_once()
    assert mock_patch.call_args.args[0] == "http://blah/robot-actions/3"
    assert mock_patch.call_args.kwargs["json"] == expected_data


@patch("mx_bluesky.common.external_interaction.ispyb.exp_eye_store.patch")
def test_update_sample_status(
    mock_patch,
):
    expeye = ExpeyeInteraction()
    expected_json = {"blSampleStatus": "LOADED"}
    expeye.update_sample_status(12345, BLSampleStatus.LOADED)
    mock_patch.assert_called_with(
        "http://blah/samples/12345", auth=ANY, json=expected_json
    )


def event_with_data(data: dict[str, Any]):
    return Event(
        {
            "data": data,
            "time": 0,
            "uid": "",
            "timestamps": {},
            "descriptor": "",
            "seq_num": 0,
        }
    )


def test_update_data_from_event_single_entry():
    mapping = {"device-reading": "ispybEntry"}
    data = event_with_data({"device-reading": 100})
    update = create_update_data_from_event_doc(mapping, data)
    assert update == {"ispybEntry": 100}


def test_update_data_from_event_all_entries_present():
    mapping = {"device-reading": "ispybEntry", "device-reading-2": "ispybEntry2"}
    data = event_with_data({"device-reading": 100, "device-reading-2": 200})
    update = create_update_data_from_event_doc(mapping, data)
    assert update == {"ispybEntry": 100, "ispybEntry2": 200}


def test_update_data_from_event_some_entries_present():
    mapping = {"device-reading": "ispybEntry", "device-reading-2": "ispybEntry2"}
    data = event_with_data({"device-reading": 100})
    update = create_update_data_from_event_doc(mapping, data)
    assert update == {"ispybEntry": 100}
