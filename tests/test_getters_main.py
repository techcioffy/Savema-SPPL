import io
import main as root_main

from sppl import SavemaPrinterClient
from sppl.getters_main import main as getters_main
from sppl.getters_main import DEFAULT_TEMPLATE_FILE
from sppl.getters_main import build_getter_steps, build_parser, main, run_getters


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


def test_root_main_py_delegates_to_getters_main():
    assert root_main.main is getters_main


def test_build_getter_steps_contains_all_canonical_getters():
    frames = [step.frame for step in build_getter_steps()]

    assert frames == [
        "~SPCGDT^",
        "~SPCGNC^",
        "~SPCGSC^",
        "~SPCGPS^",
        "~SPCGPD^",
        "~SPCGDV^",
        "~SPCGPR^",
        "~SPCGHP^",
        "~SPCGVP^",
        "~SPCGMO^",
        "~SPCGRS^",
        "~SPCGIC^",
        "~SPCGTC^",
        "~SPCGAS^",
        "~SPCGSP{1}^",
        "~SPCGPA^",
        "~SPCGOA{1}^",
        "~SPCGAA^",
        "~SPCGSL^",
        "~SPCGAP^",
        "~SPCGPM^",
        "~SPLGAT^",
        "~SPLGST^",
        "~SPLGSD^",
        "~SPLGFF^",
        f"~SPLGFN{{{DEFAULT_TEMPLATE_FILE}}}^",
        "~SPLGFV{TextCSV}^",
        "~SPLGQC{TextCSV}^",
        "~SPLGMQ{TextCSV}^",
        "~SPPGLQ^",
        "~SPPSTA^",
        "~SPGGTP^",
        "~SPGGFV^",
        "~SPGGRR^",
        "~SPGGSN^",
        "~SPGGCP^",
        "~SPGGLI^",
        "~SPTGPS^",
        "~SPTGPC^",
        "~SPTGPP^",
        "~SPTGPD^",
        "~SPTGPA^",
        "~SPTGTP^",
    ]


def test_build_getter_steps_uses_args_and_can_include_document_typo_aliases():
    frames = [
        step.frame
        for step in build_getter_steps(
            system_parameter=7,
            additional_setting=8,
            template_file="label.ronx",
            field_name="BatchNo",
            queue_fields=("PRDNAME", "BATCH NO"),
            include_document_typo_aliases=True,
        )
    ]

    assert "~SPCGSP{7}^" in frames
    assert "~SPCGOA{8}^" in frames
    assert "~SPLGFN{label.ronx}^" in frames
    assert "~SPLGFV{BatchNo}^" in frames
    assert "~SPLGQC{BatchNo}^" in frames
    assert "~SPLGMQ{PRDNAME~gt~BATCH NO}^" in frames
    assert frames[-2:] == ["~SPCGLQ^", "~SPGGFW^"]


def test_run_getters_sends_commands_and_prints_responses():
    steps = build_getter_steps()[:3]
    transport = QueueTransport(
        [
            b"~SPGRES{SPCGDT:05<05<2026<12<00<00<00}^",
            b"~SPGRES{SPCGNC:192.168.1.123<255.255.255.0<192.168.1.1<9100}^",
            b"~SPGRES{SPCGSC:115200<None<8<1}^",
        ]
    )
    stream = io.StringIO()

    result = run_getters(SavemaPrinterClient(transport), steps, stream=stream)

    assert result == 0
    assert transport.opened
    assert transport.closed
    assert transport.sent == [b"~SPCGDT^", b"~SPCGNC^", b"~SPCGSC^"]
    assert "get network configuration" in stream.getvalue()


def test_run_getters_can_stop_on_fail_response():
    steps = build_getter_steps()[:2]
    transport = QueueTransport(
        [
            b"~SPGRES{FAIL}^",
            b"~SPGRES{SPCGNC:192.168.1.123<255.255.255.0<192.168.1.1<9100}^",
        ]
    )

    result = run_getters(
        SavemaPrinterClient(transport),
        steps,
        stream=io.StringIO(),
        continue_on_error=False,
    )

    assert result == 1
    assert transport.sent == [b"~SPCGDT^"]


def test_parser_accepts_printer_ip_and_getter_parameters():
    args = build_parser().parse_args(
        [
            "--host",
            "192.168.1.123",
            "--port",
            "9100",
            "--template-file",
            "label.ronx",
            "--field-name",
            "BatchNo",
            "--queue-field",
            "PRDNAME",
            "--queue-field",
            "BATCH NO",
            "--system-parameter",
            "7",
            "--additional-setting",
            "8",
        ]
    )

    assert args.host == "192.168.1.123"
    assert args.queue_fields == ["PRDNAME", "BATCH NO"]
    assert args.system_parameter == 7
    assert args.additional_setting == 8


def test_parser_default_template_file_matches_c998_test_template():
    args = build_parser().parse_args(["--host", "192.168.1.123"])

    assert args.template_file == "C998 - TEST2_53.rox"


def test_main_builds_tcp_client(monkeypatch):
    captured = {}

    def fake_tcp(host, port=9100, timeout=5.0, encoding="ascii"):
        captured.update(host=host, port=port, timeout=timeout, encoding=encoding)
        return "client"

    def fake_run_getters(client, steps, continue_on_error=True):
        captured.update(client=client, count=len(list(steps)), continue_on_error=continue_on_error)
        return 0

    monkeypatch.setattr(SavemaPrinterClient, "tcp", fake_tcp)
    monkeypatch.setattr("sppl.getters_main.run_getters", fake_run_getters)

    assert main(["--host", "192.168.1.123"]) == 0
    assert captured["host"] == "192.168.1.123"
    assert captured["client"] == "client"
    assert captured["count"] == 43
    assert captured["continue_on_error"] is True
