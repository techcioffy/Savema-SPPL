"""Command-line runner for all SPPL getter/status commands."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, TextIO

from .client import SavemaPrinterClient
from .commands import SPPLCommands
from .exceptions import SPPLError
from .protocol import SPPLCommand, SPPLResponse


DEFAULT_TEMPLATE_FILE = "C998 - TEST2_53.rox"
DEFAULT_FIELD_NAME = "TextCSV"


@dataclass(frozen=True)
class GetterStep:
    label: str
    command: SPPLCommand

    @property
    def frame(self) -> str:
        return self.command.frame


def build_getter_steps(
    system_parameter: int = 1,
    template_file: str = DEFAULT_TEMPLATE_FILE,
    field_name: str = DEFAULT_FIELD_NAME,
    queue_fields: Sequence[str] = (DEFAULT_FIELD_NAME,),
    include_document_typo_aliases: bool = False,
) -> List[GetterStep]:
    """Build all read-only getter/status commands available in the library."""

    c = SPPLCommands()
    steps = [
        GetterStep("get system date/time and offset", c.get_system_datetime()),
        GetterStep("get network configuration", c.get_network_configuration()),
        GetterStep("get RS-232 configuration", c.get_rs232_configuration()),
        GetterStep("get print speed", c.get_print_speed()),
        GetterStep("get print delay", c.get_print_delay()),
        GetterStep("get darkness/contrast", c.get_darkness()),
        GetterStep("get print rotation", c.get_print_rotation()),
        GetterStep("get horizontal position", c.get_horizontal_position()),
        GetterStep("get vertical position", c.get_vertical_position()),
        GetterStep("get mirroring option", c.get_mirroring_option()),
        GetterStep("get RibbonSave mode", c.get_ribbon_save_mode()),
        GetterStep("get internal contact mode", c.get_internal_contact_mode()),
        GetterStep("get trigger contact mode", c.get_trigger_contact_mode()),
        GetterStep("get all settings", c.get_all_settings()),
        GetterStep(f"get system parameter {system_parameter}", c.get_system_parameter(system_parameter)),
        GetterStep("get all system parameters", c.get_all_system_parameters()),
        GetterStep("get system language", c.get_system_language()),
        GetterStep("get administrator password", c.get_administrator_password()),
        GetterStep("get print request message", c.get_print_request_message()),
        GetterStep("get active template", c.get_active_template()),
        GetterStep("get stored templates", c.get_stored_templates()),
        GetterStep("get stored data files", c.get_stored_data_files()),
        GetterStep(f"get field names for {template_file}", c.get_field_names(template_file)),
        GetterStep(f"get field value for {field_name}", c.get_field_value(field_name)),
        GetterStep(f"get queue capacity for {field_name}", c.get_queue_capacity(field_name)),
        GetterStep(
            "get multi queue capacity for " + ", ".join(queue_fields),
            c.get_multi_queue_capacity(*queue_fields),
        ),
        GetterStep("get limited print count", c.get_limited_print_count()),
        GetterStep("printer status", c.get_printer_status()),
        GetterStep("get total print count", c.get_total_print_count()),
        GetterStep("get firmware version", c.get_firmware_version()),
        GetterStep("get remaining ribbon", c.get_remaining_ribbon()),
        GetterStep("get serial number", c.get_serial_number()),
        GetterStep("get current print count", c.get_current_print_count()),
        GetterStep("get lock interface", c.get_lock_interface()),
        GetterStep("get traverse pack size", c.get_pack_size()),
        GetterStep("get traverse print count", c.get_traverse_print_count()),
        GetterStep("get traverse print position", c.get_print_position()),
        GetterStep("get traverse pack distance", c.get_pack_distance()),
        GetterStep("get traverse printing area", c.get_printing_area()),
        GetterStep("get all traverse parameters", c.get_all_traverse_parameters()),
    ]

    if include_document_typo_aliases:
        steps.extend(
            [
                GetterStep("get limited print count (document typo alias)", c.get_limited_print_count(use_document_typo=True)),
                GetterStep("get firmware version (document typo alias)", c.get_firmware_version(use_document_typo=True)),
            ]
        )

    return steps


def run_getters(
    client: SavemaPrinterClient,
    steps: Iterable[GetterStep],
    stream: TextIO = sys.stdout,
    continue_on_error: bool = True,
) -> int:
    failures = 0
    with client:
        for index, step in enumerate(steps, start=1):
            print(f"[{index:02d}] {step.label}: {step.frame}", file=stream)
            try:
                response = client.execute(step.command)
            except SPPLError as exc:
                failures += 1
                print(f"     error: {exc}", file=stream)
                if not continue_on_error:
                    return 1
                continue

            _print_response(response, stream)
            if response is not None and not response.ok:
                failures += 1
                if not continue_on_error:
                    return 1

    return 1 if failures else 0


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
        description="Run every available SPPL getter/status command against a real printer.",
    )
    parser.add_argument("--host", required=True, help="Printer IP address or hostname.")
    parser.add_argument("--port", type=int, default=9100, help="Printer TCP port, default 9100.")
    parser.add_argument("--timeout", type=float, default=5.0, help="Transport timeout in seconds.")
    parser.add_argument("--encoding", default="ascii", help="Command encoding, default ascii.")
    parser.add_argument(
        "--system-parameter",
        type=int,
        default=1,
        help="Parameter number for SPCGSP, default 1.",
    )
    parser.add_argument(
        "--template-file",
        default=DEFAULT_TEMPLATE_FILE,
        help=f"Template filename for SPLGFN, default {DEFAULT_TEMPLATE_FILE}.",
    )
    parser.add_argument(
        "--field-name",
        default=DEFAULT_FIELD_NAME,
        help=f"Field name for SPLGFV and SPLGQC, default {DEFAULT_FIELD_NAME}.",
    )
    parser.add_argument(
        "--queue-field",
        action="append",
        dest="queue_fields",
        default=None,
        help=f"Field name for SPLGMQ. Repeat for multiple fields. Default {DEFAULT_FIELD_NAME}.",
    )
    parser.add_argument(
        "--include-document-typo-aliases",
        action="store_true",
        help="Also try known typo aliases from the PDF examples: SPCGLQ and SPGGFW.",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop at the first transport/protocol error or FAIL response.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    queue_fields = tuple(args.queue_fields or [DEFAULT_FIELD_NAME])
    steps = build_getter_steps(
        system_parameter=args.system_parameter,
        template_file=args.template_file,
        field_name=args.field_name,
        queue_fields=queue_fields,
        include_document_typo_aliases=args.include_document_typo_aliases,
    )
    client = SavemaPrinterClient.tcp(
        args.host,
        port=args.port,
        timeout=args.timeout,
        encoding=args.encoding,
    )
    return run_getters(client, steps, continue_on_error=not args.stop_on_error)


if __name__ == "__main__":
    raise SystemExit(main())
