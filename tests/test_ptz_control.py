from __future__ import annotations

import pytest

from vapix_python import VapixResponseError


def test_get_current_position_parses_values(api, fake_session):
    fake_session.queue("pan=12.5\r\ntilt=-4.25\r\nzoom=100\r\n")
    assert api.ptz.get_current_position() == (12.5, -4.25, 100.0)


def test_get_current_position_handles_reordered_response(api, fake_session):
    fake_session.queue("zoom=1\ntilt=2\npan=3\n")
    assert api.ptz.get_current_position() == (3.0, 2.0, 1.0)


def test_get_current_position_raises_on_garbage(api, fake_session):
    fake_session.queue("pan is unavailable")
    with pytest.raises(VapixResponseError):
        api.ptz.get_current_position()


def test_camera_error_body_raises(api, fake_session):
    fake_session.queue("Error: PTZ not available")
    with pytest.raises(VapixResponseError, match="PTZ not available"):
        api.ptz.set_home()


def test_commands_include_ptz_base_args(api, fake_session):
    fake_session.queue()
    api.ptz.absolute_move(10, 20, 30, 40)
    params = fake_session.last["params"]
    assert params["camera"] == 1
    assert params["html"] == "no"
    assert "timestamp" in params


def test_absolute_move_sends_expected_params(api, fake_session):
    fake_session.queue()
    api.ptz.absolute_move(10, 20, 30, 40)
    params = fake_session.last["params"]
    assert params["pan"] == 10
    assert params["tilt"] == 20
    assert params["zoom"] == 30
    assert params["speed"] == 40


def test_ptz_enabled_queries_info_for_channel(api, fake_session):
    fake_session.queue("Available commands:\r\n...")
    api.ptz.ptz_enabled(channel=2)
    params = fake_session.last["params"]
    assert params["info"] == "1"
    assert params["camera"] == 2


def test_relative_move_sends_expected_params(api, fake_session):
    fake_session.queue()
    api.ptz.relative_move(1, 2, 3, 4)
    params = fake_session.last["params"]
    assert params["rpan"] == 1
    assert params["rtilt"] == 2
    assert params["rzoom"] == 3


def test_continuous_move_formats_pair(api, fake_session):
    fake_session.queue()
    api.ptz.continuous_move(-50, 25, 10)
    params = fake_session.last["params"]
    assert params["continuouspantiltmove"] == "-50,25"
    assert params["continuouszoommove"] == 10


def test_stop_move_zeroes_speeds(api, fake_session):
    fake_session.queue()
    api.ptz.stop_move()
    params = fake_session.last["params"]
    assert params["continuouspantiltmove"] == "0,0"
    assert params["continuouszoommove"] == "0"


def test_rename_preset_sends_number_and_name_in_correct_fields(api, fake_session):
    fake_session.queue()
    api.ptz.rename_preset_number(3, "gate")
    params = fake_session.last["params"]
    assert params["renameserverpresetno"] == 3
    assert params["newname"] == "gate"


def test_area_zoom_formats_triplet(api, fake_session):
    fake_session.queue()
    api.ptz.area_zoom(100, 200, 300, 50)
    assert fake_session.last["params"]["areazoom"] == "100,200,300"


@pytest.mark.parametrize(
    ("method", "bad_value"),
    [
        ("set_iris", -1),
        ("set_focus", 10000),
        ("set_zoom", -5),
        ("set_brightness", 12345),
    ],
)
def test_level_setters_validate_range(api, method, bad_value):
    with pytest.raises(ValueError):
        getattr(api.ptz, method)(bad_value)


def test_set_move_speed_validates_range(api):
    with pytest.raises(ValueError):
        api.ptz.set_move_speed(101)


def test_set_autofocus_translates_bool(api, fake_session):
    fake_session.queue()
    api.ptz.set_autofocus(False)
    assert fake_session.last["params"]["autofocus"] == "off"
