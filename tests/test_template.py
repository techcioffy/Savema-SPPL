from sppl import Font, SPPLCommands, Template


def test_template_builder_matches_manual_structure():
    template = (
        Template(name="temp1_53.ronx", machine_type="53x70I", width=640, height=480)
        .add_text(
            "text1",
            x=10,
            y=63,
            w=105,
            h=33,
            rotate=180,
            data="savema Printer",
            font=Font(name="Arial", size=15, style=["Bold", "Italic"]),
        )
    )

    xml = template.to_xml()

    assert xml.startswith("<Template>")
    assert "<MachineType>53x70I</MachineType>" in xml
    assert "<ObjectType>Text</ObjectType>" in xml
    assert "<Name>text1</Name>" in xml
    assert "<Data>savema Printer</Data>" in xml
    assert "<Style>Bold,Italic</Style>" in xml


def test_create_template_data_uses_raw_xml_payload():
    template = Template(name="temp.ronx", machine_type="53x70I", width=640, height=480)

    command = SPPLCommands().create_template_data(template)

    assert str(command).startswith("~SPLTDS{<Template>")
    assert str(command).endswith("</Template>}^")

