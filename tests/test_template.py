from datetime import date
from xml.etree import ElementTree as ET

from sppl import Font, SPPLCommands, Template, set_date_object_value


SAMPLE_ROX_DATE_OBJECT = """
<Template>
  <Object>
    <ObjectType>Date</ObjectType>
    <NameID>test</NameID>
    <Name>date8</Name>
    <Content>
      <Data>05/05/2026</Data>
      <Source>Fixed</Source>
      <Format>dd/MM/yyyy</Format>
      <Separator>/</Separator>
      <Type>Fixed</Type>
    </Content>
  </Object>
</Template>
"""


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


def test_set_date_object_value_updates_existing_rox_date_without_changing_type():
    xml = set_date_object_value(SAMPLE_ROX_DATE_OBJECT, "test", "26/10/2026")
    root = ET.fromstring(xml)
    item = next(
        obj
        for obj in root.findall("Object")
        if obj.findtext("NameID") == "test"
    )
    content = item.find("Content")

    assert item.findtext("ObjectType") == "Date"
    assert content.findtext("Data") == "26/10/2026"
    assert content.findtext("Format") == "dd/MM/yyyy"
    assert content.findtext("Separator") == "/"
    assert content.findtext("Source") == "Fixed"
    assert content.findtext("Type") == "Fixed"
    assert str(SPPLCommands().create_template_data(xml)).startswith("~SPLTDS{<Template>")


def test_set_date_object_value_formats_python_date_with_sppl_format():
    source = """
    <Template>
      <Object>
        <ObjectType>Date</ObjectType>
        <NameID>expiry</NameID>
        <Name>date1</Name>
        <Content>
          <Data>05/05/2026</Data>
          <Format>dd-MM-yyyy</Format>
          <Separator>-</Separator>
          <Source>Internal</Source>
          <Type>Fixed</Type>
        </Content>
      </Object>
    </Template>
    """

    xml = set_date_object_value(source, "expiry", date(2026, 10, 26))

    assert "<Data>26-10-2026</Data>" in xml

