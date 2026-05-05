from sppl import SPPLCommands
from sppl.spec import COMMANDS


def frame(command):
    return str(command)


def test_configuration_commands_from_manual_examples():
    c = SPPLCommands()

    assert frame(c.set_system_datetime(25, 1, 2015, 11, 36, 0, 0)) == (
        "~SPCSDT{25>1>2015>11>36>0>0}^"
    )
    assert frame(c.get_system_datetime()) == "~SPCGDT^"
    assert frame(c.set_network_configuration("192.168.1.123", "255.255.255.0", "192.168.1.1", 9100)) == (
        "~SPCSNC{192.168.1.123>255.255.255.0>192.168.1.1>9100}^"
    )
    assert frame(c.get_network_configuration()) == "~SPCGNC^"
    assert frame(c.set_rs232_configuration(115200, "None", 8, 1)) == "~SPCSSC{115200>None>8>1}^"
    assert frame(c.get_rs232_configuration()) == "~SPCGSC^"
    assert frame(c.set_print_speed(200)) == "~SPCSPS{200}^"
    assert frame(c.get_print_speed()) == "~SPCGPS^"
    assert frame(c.set_print_delay(10)) == "~SPCSPD{10}^"
    assert frame(c.get_print_delay()) == "~SPCGPD^"
    assert frame(c.set_darkness(100)) == "~SPCSDV{100}^"
    assert frame(c.get_darkness()) == "~SPCGDV^"
    assert frame(c.set_print_rotation(180)) == "~SPCSPR{180}^"
    assert frame(c.get_print_rotation()) == "~SPCGPR^"
    assert frame(c.set_horizontal_position(0)) == "~SPCSHP{0}^"
    assert frame(c.get_horizontal_position()) == "~SPCGHP^"
    assert frame(c.set_vertical_position(5)) == "~SPCSVP{5}^"
    assert frame(c.get_vertical_position()) == "~SPCGVP^"
    assert frame(c.set_mirroring_option(0)) == "~SPCSMO{0}^"
    assert frame(c.get_mirroring_option()) == "~SPCGMO^"
    assert frame(c.set_ribbon_save_mode(0, 2, 4)) == "~SPCSRS{0>2>4}^"
    assert frame(c.get_ribbon_save_mode()) == "~SPCGRS^"
    assert frame(c.set_internal_contact_mode(1, 100)) == "~SPCSIC{1>100}^"
    assert frame(c.get_internal_contact_mode()) == "~SPCGIC^"
    assert frame(c.set_trigger_contact_mode(1, 3, 100)) == "~SPCSTC{1>3>100}^"
    assert frame(c.get_trigger_contact_mode()) == "~SPCGTC^"
    assert frame(c.set_all_settings(300, 2, 100, 0, 1, 0, 0, 30, 1, 3, 60)) == (
        "~SPCSAS{300>2>100>0>1>0>0>30>1>3>60}^"
    )
    assert frame(c.get_all_settings()) == "~SPCGAS^"
    assert frame(c.set_system_parameter(1, 25)) == "~SPCSSP{1>25}^"
    assert frame(c.get_system_parameter(1)) == "~SPCGSP{1}^"
    assert frame(c.set_all_system_parameters([25, 27, 300, 200])) == "~SPCSPA{25>27>300>200}^"
    assert frame(c.get_all_system_parameters()) == "~SPCGPA^"
    assert frame(c.set_system_language("02")) == "~SPCSSL{02}^"
    assert frame(c.get_system_language()) == "~SPCGSL^"
    assert frame(c.set_administrator_password(123456)) == "~SPCSAP{123456}^"
    assert frame(c.get_administrator_password()) == "~SPCGAP^"
    assert frame(c.return_to_factory_settings()) == "~SPCSFS^"
    assert frame(c.set_print_request_message(0, "OK")) == "~SPCSPM{0>OK}^"
    assert frame(c.get_print_request_message()) == "~SPCGPM^"


def test_label_commands_from_manual_examples():
    c = SPPLCommands()

    assert frame(c.load_template_file("temp1_53.ronx")) == "~SPLLTF{temp1_53.ronx}^"
    assert frame(c.get_active_template()) == "~SPLGAT^"
    assert frame(c.get_stored_templates()) == "~SPLGST^"
    assert frame(c.get_stored_data_files()) == "~SPLGSD^"
    assert frame(c.create_data_file("sample.csv", "abc\nbce\ncde")) == (
        "~SPLCDF{sample.csv~gt~abc\nbce\ncde}^"
    )
    assert frame(c.delete_template_file("temp1_53.ronx")) == "~SPLDTF{temp1_53.ronx}^"
    assert frame(c.delete_all_templates()) == "~SPLDTA^"
    assert frame(c.delete_data_file("datafile1.csv")) == "~SPLDDF{datafile1.csv}^"
    assert frame(c.delete_all_data_files()) == "~SPLDDA^"
    assert frame(c.clear_data_buffer()) == "~SPLCDB^"
    assert frame(c.get_field_names("temp1_53.rox")) == "~SPLGFN{temp1_53.rox}^"
    assert frame(c.get_field_value("BatchNo")) == "~SPLGFV{BatchNo}^"
    assert frame(c.append_queue_data("TextCSV", ["AB001", "AB002"])) == (
        "~SPLAQD{TextCSV~gt~AB001\nAB002}^"
    )
    assert frame(c.append_multi_queue_data({"PRDNAME": ["PR01", "PR02"], "BATCH NO": ["A01B", "A02B"]})) == (
        "~SPLAMQ{PRDNAME~gt~PR01\nPR02~gt~BATCH NO~gt~A01B\nA02B}^"
    )
    assert frame(c.get_queue_capacity("TextCSV")) == "~SPLGQC{TextCSV}^"
    assert frame(c.get_multi_queue_capacity("PRDNAME", "BATCH NO")) == (
        "~SPLGMQ{PRDNAME~gt~BATCH NO}^"
    )
    assert frame(c.clear_queue_data("TextCSV")) == "~SPLCQD{TextCSV}^"
    assert frame(c.clear_multi_queue_data("PRDNAME", "BATCH NO")) == (
        "~SPLCMQ{PRDNAME~gt~BATCH NO}^"
    )


def test_modification_print_general_and_traverse_commands():
    c = SPPLCommands()

    assert frame(c.change_text_value("brand_txt", "SAVEMA")) == "~SPMCTV{brand_txt~gt~SAVEMA}^"
    assert frame(c.change_barcode_value("barcodeno", "8691234567890")) == (
        "~SPMCBV{barcodeno~gt~8691234567890}^"
    )
    assert frame(c.change_2d_barcode_value("qrcodeno", "savema12345")) == (
        "~SPMC2D{qrcodeno~gt~savema12345}^"
    )
    assert frame(c.change_counter_value("counter1", "000055")) == "~SPMCCV{counter1~gt~000055}^"
    assert frame(c.change_logo_value("productlogo", "/9j/4Q==")) == "~SPMCLV{productlogo~gt~/9j/4Q==}^"
    assert frame(c.change_selected_values({"brand_txt": "SAVEMA", "qrcodeno": "savema12345"})) == (
        "~SPMCSV{brand_txt~gt~SAVEMA~gt~qrcodeno~gt~savema12345}^"
    )
    assert frame(c.start_print()) == "~SPPSAP^"
    assert frame(c.set_limited_print_count(1000)) == "~SPPSLQ{1000}^"
    assert frame(c.get_limited_print_count()) == "~SPPGLQ^"
    assert frame(c.stop_print()) == "~SPPSTP^"
    assert frame(c.one_test_print()) == "~SPPOTP^"
    assert frame(c.get_printer_status()) == "~SPPSTA^"
    assert frame(c.send_user_message("Package finished. Please stop printer")) == (
        "~SPGSUM{Package finished. Please stop printer}^"
    )
    assert frame(c.general_response("950225")) == "~SPGRES{950225}^"
    assert frame(c.get_total_print_count()) == "~SPGGTP^"
    assert frame(c.get_firmware_version()) == "~SPGGFV^"
    assert frame(c.get_firmware_version(use_document_typo=True)) == "~SPGGFW^"
    assert frame(c.get_remaining_ribbon()) == "~SPGGRR^"
    assert frame(c.get_serial_number()) == "~SPGGSN^"
    assert frame(c.get_current_print_count()) == "~SPGGCP^"
    assert frame(c.set_lock_interface(True)) == "~SPGSLI{1}^"
    assert frame(c.get_lock_interface()) == "~SPGGLI^"
    assert frame(c.set_pack_size(60)) == "~SPTSPS{60}^"
    assert frame(c.get_pack_size()) == "~SPTGPS^"
    assert frame(c.set_traverse_print_count(5)) == "~SPTSPC{5}^"
    assert frame(c.get_traverse_print_count()) == "~SPTGPC^"
    assert frame(c.set_print_position(10)) == "~SPTSPP{10}^"
    assert frame(c.get_print_position()) == "~SPTGPP^"
    assert frame(c.set_pack_distance(50)) == "~SPTSPD{50}^"
    assert frame(c.get_pack_distance()) == "~SPTGPD^"
    assert frame(c.set_printing_area(400)) == "~SPTSPA{400}^"
    assert frame(c.get_printing_area()) == "~SPTGPA^"
    assert frame(c.set_all_traverse_parameters(60, 5, 10, 50, 400)) == (
        "~SPTSTP{60>5>10>50>400}^"
    )
    assert frame(c.get_all_traverse_parameters()) == "~SPTGTP^"


def test_catalog_keeps_all_documented_codes_unique():
    assert len(COMMANDS) == len(set(COMMANDS))
    for code in COMMANDS:
        assert code.startswith("SP")
        assert len(code) == 6

