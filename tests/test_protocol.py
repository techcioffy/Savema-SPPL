import pytest

from sppl import SPPLCommand, build_batch, build_command, parse_response
from sppl.exceptions import SPPLProtocolError


def test_build_command_without_parameters():
    assert str(build_command("SPCGNC")) == "~SPCGNC^"


def test_build_command_with_parameters():
    command = build_command("SPCSNC", "192.168.1.123", "255.255.255.0", "192.168.1.1", 9100)

    assert command.body == "SPCSNC{192.168.1.123>255.255.255.0>192.168.1.1>9100}"
    assert str(command) == "~SPCSNC{192.168.1.123>255.255.255.0>192.168.1.1>9100}^"


def test_build_command_with_raw_parameters():
    command = build_command("SPLTDS", raw_params="<Template><General></General></Template>")

    assert str(command) == "~SPLTDS{<Template><General></General></Template>}^"


def test_build_batch_strips_frames():
    batch = build_batch([SPPLCommand("SPPSLQ", [1000]), "~SPPSAP^"])

    assert batch == "~SPPSLQ{1000}|SPPSAP^"


def test_invalid_command_code_raises():
    with pytest.raises(SPPLProtocolError):
        build_command("BAD")


def test_reserved_separator_in_parameter_raises():
    with pytest.raises(SPPLProtocolError):
        str(build_command("SPCSAP", "12>34"))


def test_parse_simple_response():
    response = parse_response("~SPGRES{SPCGSC:115200<None<8<1}^")

    assert response.code == "SPGRES"
    assert response.source_command == "SPCGSC"
    assert response.values == ("115200", "None", "8", "1")
    assert response.ok


def test_parse_failure_response():
    response = parse_response("~SPGRES{FAIL}^")

    assert not response.ok

