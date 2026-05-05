"""High-level SPPL command helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Iterable, Tuple, Union

from .protocol import GT_SEPARATOR, SPPLCommand, build_batch, build_command
from .template import Template


DataLines = Union[str, Iterable[Any]]
PairInput = Union[Mapping[str, Any], Iterable[Tuple[str, Any]]]


def _lines(data: DataLines) -> str:
    if isinstance(data, str):
        return data
    return "\n".join(str(item) for item in data)


def _pairs(items: PairInput) -> Tuple[Any, ...]:
    source = items.items() if isinstance(items, Mapping) else items
    values = []
    for key, value in source:
        values.extend([key, _lines(value)])
    return tuple(values)


class SPPLCommands:
    """Factory for all SPPL commands listed in the Rev.11 command table."""

    def command(self, code: str, *params: Any, separator: str = ">", raw_params: str = None) -> SPPLCommand:
        return build_command(code, *params, separator=separator, raw_params=raw_params)

    def batch(self, *commands: Union[str, SPPLCommand]) -> str:
        return build_batch(commands)

    # Configuration commands
    def set_system_datetime(
        self, day: int, month: int, year: int, hour: int, minute: int, second: int, offset: int
    ) -> SPPLCommand:
        return self.command("SPCSDT", day, month, year, hour, minute, second, offset)

    def get_system_datetime(self) -> SPPLCommand:
        return self.command("SPCGDT")

    def set_network_configuration(
        self, ip_address: str, subnet_mask: str, gateway: str, port_number: int
    ) -> SPPLCommand:
        return self.command("SPCSNC", ip_address, subnet_mask, gateway, port_number)

    def get_network_configuration(self) -> SPPLCommand:
        return self.command("SPCGNC")

    def set_rs232_configuration(
        self, baud_rate: int, parity: str, data_bits: int, stop_bits: int
    ) -> SPPLCommand:
        return self.command("SPCSSC", baud_rate, parity, data_bits, stop_bits)

    def get_rs232_configuration(self) -> SPPLCommand:
        return self.command("SPCGSC")

    def set_print_speed(self, print_speed: int) -> SPPLCommand:
        return self.command("SPCSPS", print_speed)

    def get_print_speed(self) -> SPPLCommand:
        return self.command("SPCGPS")

    def set_print_delay(self, print_delay: int) -> SPPLCommand:
        return self.command("SPCSPD", print_delay)

    def get_print_delay(self) -> SPPLCommand:
        return self.command("SPCGPD")

    def set_darkness(self, contrast: int) -> SPPLCommand:
        return self.command("SPCSDV", contrast)

    set_contrast = set_darkness

    def get_darkness(self) -> SPPLCommand:
        return self.command("SPCGDV")

    get_contrast = get_darkness

    def set_print_rotation(self, rotation: int) -> SPPLCommand:
        return self.command("SPCSPR", rotation)

    def get_print_rotation(self) -> SPPLCommand:
        return self.command("SPCGPR")

    def set_horizontal_position(self, position: int) -> SPPLCommand:
        return self.command("SPCSHP", position)

    def get_horizontal_position(self) -> SPPLCommand:
        return self.command("SPCGHP")

    def set_vertical_position(self, position: int) -> SPPLCommand:
        return self.command("SPCSVP", position)

    def get_vertical_position(self) -> SPPLCommand:
        return self.command("SPCGVP")

    def set_mirroring_option(self, option: int) -> SPPLCommand:
        return self.command("SPCSMO", option)

    def get_mirroring_option(self) -> SPPLCommand:
        return self.command("SPCGMO")

    def set_ribbon_save_mode(
        self, direction: int, column_no: int, shifting_length: int
    ) -> SPPLCommand:
        return self.command("SPCSRS", direction, column_no, shifting_length)

    def get_ribbon_save_mode(self) -> SPPLCommand:
        return self.command("SPCGRS")

    def set_internal_contact_mode(self, state: int, package_length: int) -> SPPLCommand:
        return self.command("SPCSIC", state, package_length)

    def get_internal_contact_mode(self) -> SPPLCommand:
        return self.command("SPCGIC")

    def set_trigger_contact_mode(
        self, state: int, print_count: int, package_length: int
    ) -> SPPLCommand:
        return self.command("SPCSTC", state, print_count, package_length)

    def get_trigger_contact_mode(self) -> SPPLCommand:
        return self.command("SPCGTC")

    def set_all_settings(
        self,
        print_speed: int,
        print_delay: int,
        darkness_value: int,
        ribbon_save_direction: int,
        ribbon_save_column_no: int,
        ribbon_save_package_length: int,
        internal_contact_state: int,
        internal_contact_package_length: int,
        trigger_contact_state: int,
        trigger_contact_print_count: int,
        trigger_contact_package_length: int,
    ) -> SPPLCommand:
        return self.command(
            "SPCSAS",
            print_speed,
            print_delay,
            darkness_value,
            ribbon_save_direction,
            ribbon_save_column_no,
            ribbon_save_package_length,
            internal_contact_state,
            internal_contact_package_length,
            trigger_contact_state,
            trigger_contact_print_count,
            trigger_contact_package_length,
        )

    def get_all_settings(self) -> SPPLCommand:
        return self.command("SPCGAS")

    def set_system_parameter(self, parameter_no: int, parameter_value: Any) -> SPPLCommand:
        return self.command("SPCSSP", parameter_no, parameter_value)

    def get_system_parameter(self, parameter_no: int) -> SPPLCommand:
        return self.command("SPCGSP", parameter_no)

    def set_all_system_parameters(self, parameters: Sequence[Any]) -> SPPLCommand:
        return self.command("SPCSPA", *parameters)

    def get_all_system_parameters(self) -> SPPLCommand:
        return self.command("SPCGPA")

    def set_system_language(self, language_code: Union[str, int]) -> SPPLCommand:
        return self.command("SPCSSL", language_code)

    def get_system_language(self) -> SPPLCommand:
        return self.command("SPCGSL")

    def set_administrator_password(self, password: Union[str, int]) -> SPPLCommand:
        return self.command("SPCSAP", password)

    def get_administrator_password(self) -> SPPLCommand:
        return self.command("SPCGAP")

    def return_to_factory_settings(self) -> SPPLCommand:
        return self.command("SPCSFS")

    def set_print_request_message(self, active: Union[bool, int], message: str) -> SPPLCommand:
        return self.command("SPCSPM", active, message)

    def get_print_request_message(self) -> SPPLCommand:
        return self.command("SPCGPM")

    # Label designing commands
    def create_template_data(self, template_data: Union[str, Template]) -> SPPLCommand:
        raw = template_data.to_xml() if isinstance(template_data, Template) else str(template_data)
        return self.command("SPLTDS", raw_params=raw)

    def load_template_file(self, template_file_name: str) -> SPPLCommand:
        return self.command("SPLLTF", template_file_name)

    def get_active_template(self) -> SPPLCommand:
        return self.command("SPLGAT")

    def get_stored_templates(self) -> SPPLCommand:
        return self.command("SPLGST")

    def get_stored_data_files(self) -> SPPLCommand:
        return self.command("SPLGSD")

    def create_data_file(self, data_file_name: str, content: str) -> SPPLCommand:
        return self.command("SPLCDF", data_file_name, content, separator=GT_SEPARATOR)

    def delete_template_file(self, template_file_name: str) -> SPPLCommand:
        return self.command("SPLDTF", template_file_name)

    def delete_all_templates(self) -> SPPLCommand:
        return self.command("SPLDTA")

    def delete_data_file(self, data_file_name: str) -> SPPLCommand:
        return self.command("SPLDDF", data_file_name)

    def delete_all_data_files(self) -> SPPLCommand:
        return self.command("SPLDDA")

    def clear_data_buffer(self) -> SPPLCommand:
        return self.command("SPLCDB")

    def get_field_names(self, template_file_name: str) -> SPPLCommand:
        return self.command("SPLGFN", template_file_name)

    def get_field_value(self, field_name: str) -> SPPLCommand:
        return self.command("SPLGFV", field_name)

    def append_queue_data(self, field_name: str, data: DataLines) -> SPPLCommand:
        return self.command("SPLAQD", field_name, _lines(data), separator=GT_SEPARATOR)

    append_queue_datas = append_queue_data

    def append_multi_queue_data(self, items: PairInput) -> SPPLCommand:
        return self.command("SPLAMQ", *_pairs(items), separator=GT_SEPARATOR)

    append_multi_queue_datas = append_multi_queue_data

    def get_queue_capacity(self, field_name: str) -> SPPLCommand:
        return self.command("SPLGQC", field_name)

    def get_multi_queue_capacity(self, *field_names: str) -> SPPLCommand:
        return self.command("SPLGMQ", *field_names, separator=GT_SEPARATOR)

    def clear_queue_data(self, field_name: str) -> SPPLCommand:
        return self.command("SPLCQD", field_name)

    clear_queue_datas = clear_queue_data

    def clear_multi_queue_data(self, *field_names: str) -> SPPLCommand:
        return self.command("SPLCMQ", *field_names, separator=GT_SEPARATOR)

    clear_multi_queue_datas = clear_multi_queue_data

    # Modification commands
    def change_text_value(self, object_name: str, text_value: str) -> SPPLCommand:
        return self.command("SPMCTV", object_name, text_value, separator=GT_SEPARATOR)

    def change_barcode_value(self, object_name: str, barcode_value: str) -> SPPLCommand:
        return self.command("SPMCBV", object_name, barcode_value, separator=GT_SEPARATOR)

    def change_2d_barcode_value(self, object_name: str, barcode_value: str) -> SPPLCommand:
        return self.command("SPMC2D", object_name, barcode_value, separator=GT_SEPARATOR)

    def change_counter_value(self, object_name: str, counter_value: Union[str, int]) -> SPPLCommand:
        return self.command("SPMCCV", object_name, counter_value, separator=GT_SEPARATOR)

    def change_logo_value(self, object_name: str, base64_data: str) -> SPPLCommand:
        return self.command("SPMCLV", object_name, base64_data, separator=GT_SEPARATOR)

    def change_selected_values(self, items: PairInput) -> SPPLCommand:
        return self.command("SPMCSV", *_pairs(items), separator=GT_SEPARATOR)

    # Print commands
    def start_print(self) -> SPPLCommand:
        return self.command("SPPSAP")

    def set_limited_print_count(self, print_quantity: int) -> SPPLCommand:
        return self.command("SPPSLQ", print_quantity)

    def get_limited_print_count(self, use_document_typo: bool = False) -> SPPLCommand:
        return self.command("SPCGLQ" if use_document_typo else "SPPGLQ")

    def stop_print(self) -> SPPLCommand:
        return self.command("SPPSTP")

    def one_test_print(self) -> SPPLCommand:
        return self.command("SPPOTP")

    def get_printer_status(self) -> SPPLCommand:
        return self.command("SPPSTA")

    # General commands
    def send_user_message(self, message: str) -> SPPLCommand:
        return self.command("SPGSUM", message)

    def general_response(self, response: str) -> SPPLCommand:
        return self.command("SPGRES", response)

    def get_total_print_count(self) -> SPPLCommand:
        return self.command("SPGGTP")

    def get_firmware_version(self, use_document_typo: bool = False) -> SPPLCommand:
        return self.command("SPGGFW" if use_document_typo else "SPGGFV")

    def get_remaining_ribbon(self) -> SPPLCommand:
        return self.command("SPGGRR")

    def get_serial_number(self) -> SPPLCommand:
        return self.command("SPGGSN")

    def get_current_print_count(self) -> SPPLCommand:
        return self.command("SPGGCP")

    def set_lock_interface(self, locked: Union[bool, int]) -> SPPLCommand:
        return self.command("SPGSLI", locked)

    def get_lock_interface(self) -> SPPLCommand:
        return self.command("SPGGLI")

    # Traverse commands
    def set_pack_size(self, pack_size_mm: int) -> SPPLCommand:
        return self.command("SPTSPS", pack_size_mm)

    def get_pack_size(self) -> SPPLCommand:
        return self.command("SPTGPS")

    def set_traverse_print_count(self, print_count: int) -> SPPLCommand:
        return self.command("SPTSPC", print_count)

    def get_traverse_print_count(self) -> SPPLCommand:
        return self.command("SPTGPC")

    def set_print_position(self, print_position_mm: int) -> SPPLCommand:
        return self.command("SPTSPP", print_position_mm)

    def get_print_position(self) -> SPPLCommand:
        return self.command("SPTGPP")

    def set_pack_distance(self, pack_distance_mm: int) -> SPPLCommand:
        return self.command("SPTSPD", pack_distance_mm)

    def get_pack_distance(self) -> SPPLCommand:
        return self.command("SPTGPD")

    def set_printing_area(self, printing_area: int) -> SPPLCommand:
        return self.command("SPTSPA", printing_area)

    def get_printing_area(self) -> SPPLCommand:
        return self.command("SPTGPA")

    def set_all_traverse_parameters(
        self,
        pack_size: int,
        print_count: int,
        print_position: int,
        pack_distance: int,
        printing_area: int,
    ) -> SPPLCommand:
        return self.command(
            "SPTSTP", pack_size, print_count, print_position, pack_distance, printing_area
        )

    def get_all_traverse_parameters(self) -> SPPLCommand:
        return self.command("SPTGTP")

