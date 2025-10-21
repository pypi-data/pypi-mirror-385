import contextlib
import io
import json

from freezegun import freeze_time

from army_days.core import compute_results
from army_days.output import _output_color_events, _output_json_events


@freeze_time("2024-08-05T13:00:00")
def test_output_color_events(standard_test_config):
    standard_test_config.config.show_completed = True
    results = compute_results(standard_test_config)
    with io.StringIO() as buf:
        with contextlib.redirect_stdout(buf):
            _output_color_events(results)
        output_data = buf.getvalue()
    lines = output_data.split("\n")
    assert len(lines) == 8  # 8 lines of output including final \n
    assert "840 days since" in lines[1]
    assert "1 day since" in lines[2]
    assert "Today is " in lines[3]
    assert "1 day until" in lines[4]
    assert "129 days until" in lines[5]
    # testing army butt days
    standard_test_config.config.show_completed = True
    standard_test_config.config.use_army_butt_days = True
    results = compute_results(standard_test_config)
    with io.StringIO() as buf:
        with contextlib.redirect_stdout(buf):
            _output_color_events(results)
        output_data = buf.getvalue()
    lines = output_data.split("\n")
    assert len(lines) == 8  # 8 lines of output including final \n
    assert "840 days since" in lines[1]
    assert "1 day since" in lines[2]
    assert "Today is " in lines[3]
    assert "0 and a butt days until" in lines[4]
    assert "128 and a butt days until" in lines[5]


@freeze_time("2024-08-05T13:00:00")
def test_output_json_events(standard_test_config):
    results = compute_results(standard_test_config)
    with io.StringIO() as buf:
        with contextlib.redirect_stdout(buf):
            _output_json_events(results)
        output_data = buf.getvalue()
    assert output_data is not None
    data = json.loads(output_data)  # check that it's valid json
    assert data != {}
    assert data[0]["days"] == 0.0
