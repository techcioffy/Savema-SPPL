import io

from sppl import SavemaPrinterClient
from sppl.smoke import build_parser, build_smoke_steps, make_client, run_smoke


class QueueTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.sent = []
        self.opened = False
        self.closed = False

    def open(self):
        self.opened = True

    def close(self):
        self.closed = True

    def send(self, payload):
        self.sent.append(payload)

    def receive_until(self, terminator=b"^", max_bytes=65536):
        return self.responses.pop(0)


def test_default_smoke_steps_are_read_only_getters():
    frames = [step.frame for step in build_smoke_steps()]

    assert frames == [
        "~SPPSTA^",
        "~SPGGFV^",
        "~SPGGSN^",
        "~SPGGRR^",
        "~SPGGCP^",
        "~SPGGTP^",
        "~SPLGAT^",
        "~SPLGST^",
    ]


def test_smoke_steps_add_optional_configuration_and_unsafe_commands():
    frames = [
        step.frame
        for step in build_smoke_steps(
            include_configuration=True,
            unsafe_one_test_print=True,
            unsafe_start_stop=True,
            unsafe_commands=["~SPCGNC^"],
            start_stop_delay=0,
        )
    ]

    assert "~SPCGDT^" in frames
    assert "~SPCGNC^" in frames
    assert "~SPPOTP^" in frames
    assert "~SPPSAP^" in frames
    assert "~SPPSTP^" in frames
    assert frames[-1] == "~SPCGNC^"


def test_run_smoke_executes_plan_and_prints_responses():
    steps = build_smoke_steps()[:2]
    transport = QueueTransport(
        [
            b"~SPGRES{SPPSTA:READY}^",
            b"~SPGRES{SPGGFV:v3.18}^",
        ]
    )
    stream = io.StringIO()

    result = run_smoke(SavemaPrinterClient(transport), steps, stream=stream)

    assert result == 0
    assert transport.opened
    assert transport.closed
    assert transport.sent == [b"~SPPSTA^", b"~SPGGFV^"]
    assert "printer status" in stream.getvalue()
    assert "READY" in stream.getvalue()


def test_parser_builds_tcp_client(monkeypatch):
    args = build_parser().parse_args(["--host", "192.168.1.123", "--port", "9100"])
    captured = {}

    def fake_tcp(host, port=9100, timeout=5.0, encoding="ascii"):
        captured.update(host=host, port=port, timeout=timeout, encoding=encoding)
        return "client"

    monkeypatch.setattr(SavemaPrinterClient, "tcp", fake_tcp)

    assert make_client(args) == "client"
    assert captured == {
        "host": "192.168.1.123",
        "port": 9100,
        "timeout": 5.0,
        "encoding": "ascii",
    }

