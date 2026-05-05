"""Command-line smoke test for a real Savema SPPL printer."""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, TextIO, Union

from .client import SavemaPrinterClient
from .commands import SPPLCommands
from .exceptions import SPPLError
from .protocol import SPPLCommand, SPPLResponse


@dataclass(frozen=True)
class SmokeStep:
    label: str
    command: Union[str, SPPLCommand]
    expect_response: bool = True
    delay_before_seconds: float = 0.0

    @property
    def frame(self) -> str:
        return self.command.frame if isinstance(self.command, SPPLCommand) else str(self.command)


def build_smoke_steps(
    include_configuration: bool = False,
    unsafe_one_test_print: bool = False,
    unsafe_start_stop: bool = False,
    unsafe_commands: Optional[Sequence[str]] = None,
    start_stop_delay: float = 1.0,
) -> List[SmokeStep]:
    """Build the real-printer smoke plan.

    The default plan is read-only. Anything that may print or mutate state is
    opt-in and named as unsafe in the CLI flags.
    """

    c = SPPLCommands()
    steps = [
        SmokeStep("printer status", c.get_printer_status()),
        SmokeStep("firmware version", c.get_firmware_version()),
        SmokeStep("serial number", c.get_serial_number()),
        SmokeStep("remaining ribbon", c.get_remaining_ribbon()),
        SmokeStep("current print count", c.get_current_print_count()),
        SmokeStep("total print count", c.get_total_print_count()),
        SmokeStep("active template", c.get_active_template()),
        SmokeStep("stored templates", c.get_stored_templates()),
    ]

    if include_configuration:
        steps.extend(
            [
                SmokeStep("system date/time", c.get_system_datetime()),
                SmokeStep("network configuration", c.get_network_configuration()),
                SmokeStep("rs232 configuration", c.get_rs232_configuration()),
                SmokeStep("print speed", c.get_print_speed()),
                SmokeStep("print delay", c.get_print_delay()),
                SmokeStep("darkness", c.get_darkness()),
            ]
        )

    if unsafe_one_test_print:
        steps.append(SmokeStep("UNSAFE one test print", c.one_test_print()))

    if unsafe_start_stop:
        steps.extend(
            [
                SmokeStep("UNSAFE start print", c.start_print()),
                SmokeStep(
                    "UNSAFE stop print",
                    c.stop_print(),
                    delay_before_seconds=max(0.0, start_stop_delay),
                ),
            ]
        )

    for index, command in enumerate(unsafe_commands or (), start=1):
        steps.append(SmokeStep(f"UNSAFE raw command {index}", command))

    return steps


def run_smoke(
    client: SavemaPrinterClient,
    steps: Iterable[SmokeStep],
    stream: TextIO = sys.stdout,
) -> int:
    """Execute a smoke plan against an already configured client."""

    with client:
        for index, step in enumerate(steps, start=1):
            if step.delay_before_seconds:
                print(f"[{index:02d}] waiting {step.delay_before_seconds:g}s before {step.label}", file=stream)
                time.sleep(step.delay_before_seconds)

            print(f"[{index:02d}] {step.label}: {step.frame}", file=stream)
            response = client.execute(step.command, expect_response=step.expect_response)
            _print_response(response, stream)

    return 0


def _print_response(response: Optional[SPPLResponse], stream: TextIO) -> None:
    if response is None:
        print("     response: <not requested>", file=stream)
        return
    print(f"     response: {response.raw}", file=stream)
    if response.source_command:
        print(f"     source: {response.source_command}", file=stream)
    if response.values:
        print(f"     values: {', '.join(response.values)}", file=stream)
    print(f"     ok: {response.ok}", file=stream)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a real-printer SPPL smoke test over TCP or RS-232.",
    )
    transport = parser.add_mutually_exclusive_group(required=True)
    transport.add_argument("--host", help="Printer IP/hostname for Ethernet TCP.")
    transport.add_argument("--serial-port", help="Serial port, for example COM3.")
    parser.add_argument("--port", type=int, default=9100, help="TCP port, default 9100.")
    parser.add_argument("--baudrate", type=int, default=115200, help="Serial baudrate, default 115200.")
    parser.add_argument("--timeout", type=float, default=5.0, help="Transport timeout in seconds.")
    parser.add_argument("--encoding", default="ascii", help="Command encoding, default ascii.")
    parser.add_argument(
        "--include-configuration",
        action="store_true",
        help="Also run read-only configuration get commands.",
    )
    parser.add_argument(
        "--unsafe-one-test-print",
        action="store_true",
        help="Also send SPPOTP one-test-print.",
    )
    parser.add_argument(
        "--unsafe-start-stop",
        action="store_true",
        help="Also send SPPSAP then SPPSTP after --start-stop-delay seconds.",
    )
    parser.add_argument(
        "--start-stop-delay",
        type=float,
        default=1.0,
        help="Delay between unsafe start and stop print commands.",
    )
    parser.add_argument(
        "--unsafe-command",
        action="append",
        default=[],
        help="Raw framed SPPL command to append, for example '~SPCGNC^'. May mutate printer state.",
    )
    return parser


def make_client(args: argparse.Namespace) -> SavemaPrinterClient:
    if args.host:
        return SavemaPrinterClient.tcp(
            args.host,
            port=args.port,
            timeout=args.timeout,
            encoding=args.encoding,
        )
    return SavemaPrinterClient.serial(
        args.serial_port,
        baudrate=args.baudrate,
        timeout=args.timeout,
        encoding=args.encoding,
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    steps = build_smoke_steps(
        include_configuration=args.include_configuration,
        unsafe_one_test_print=args.unsafe_one_test_print,
        unsafe_start_stop=args.unsafe_start_stop,
        unsafe_commands=args.unsafe_command,
        start_stop_delay=args.start_stop_delay,
    )

    try:
        return run_smoke(make_client(args), steps)
    except SPPLError as exc:
        print(f"SPPL smoke test failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
