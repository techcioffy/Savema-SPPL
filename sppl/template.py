"""XML template builder for SPLTDS commands."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, List, Mapping, Optional, Sequence, Union
from xml.etree import ElementTree as ET


def _text(value: Any) -> str:
    return "" if value is None else str(value)


def _add(parent: ET.Element, name: str, value: Any) -> ET.Element:
    element = ET.SubElement(parent, name)
    element.text = _text(value)
    return element


def _indent(element: ET.Element, level: int = 0) -> None:
    pad = "\n" + level * "  "
    child_pad = "\n" + (level + 1) * "  "
    children = list(element)
    if children:
        if not element.text or not element.text.strip():
            element.text = child_pad
        for child in children:
            _indent(child, level + 1)
        if not children[-1].tail or not children[-1].tail.strip():
            children[-1].tail = pad
    if level and (not element.tail or not element.tail.strip()):
        element.tail = pad


def _find_child(parent: ET.Element, name: str) -> Optional[ET.Element]:
    for child in parent:
        if child.tag == name:
            return child
    return None


def _ensure_child(parent: ET.Element, name: str) -> ET.Element:
    child = _find_child(parent, name)
    if child is None:
        child = ET.SubElement(parent, name)
    return child


def _child_text(parent: ET.Element, name: str) -> str:
    child = _find_child(parent, name)
    return "" if child is None or child.text is None else child.text


def _set_child_text(parent: ET.Element, name: str, value: Any) -> None:
    _ensure_child(parent, name).text = _text(value)


def _format_date(value: Union[str, date, datetime], date_format: str) -> str:
    if isinstance(value, str):
        return value
    tokens = (
        ("yyyy", "%Y"),
        ("yy", "%y"),
        ("MMMM", "%B"),
        ("MMM", "%b"),
        ("MM", "%m"),
        ("dddd", "%A"),
        ("ddd", "%a"),
        ("dd", "%d"),
    )
    python_format = date_format
    for sppl_token, python_token in tokens:
        python_format = python_format.replace(sppl_token, python_token)
    if "%" not in python_format:
        raise ValueError(f"Unsupported SPPL date format for Python date value: {date_format!r}")
    return value.strftime(python_format)


def set_date_object_value(
    template_data: str,
    object_name: str,
    value: Union[str, date, datetime],
    *,
    date_format: Optional[str] = None,
    separator: Optional[str] = None,
    source: Optional[str] = "Fixed",
    date_type: Optional[str] = "Fixed",
    pretty: bool = False,
) -> str:
    """Return template XML with a Date object's Data value changed.

    SPPL Rev.11 does not define a modification command for Date objects. Keeping
    the object type as Date requires updating the template XML and sending it via
    ``SPLTDS``.
    """

    root = ET.fromstring(template_data)
    target: Optional[ET.Element] = None
    for item in root.findall("Object"):
        if _child_text(item, "ObjectType").strip().lower() != "date":
            continue
        names = {_child_text(item, "Name").strip(), _child_text(item, "NameID").strip()}
        if object_name in names:
            target = item
            break

    if target is None:
        raise ValueError(f"Date object {object_name!r} was not found in template")

    content = _ensure_child(target, "Content")
    effective_format = date_format or _child_text(content, "Format") or "dd/MM/yyyy"
    effective_separator = separator if separator is not None else _child_text(content, "Separator")
    formatted_value = _format_date(value, effective_format)

    _set_child_text(content, "Data", formatted_value)
    if date_format is not None:
        _set_child_text(content, "Format", date_format)
    if separator is not None:
        _set_child_text(content, "Separator", separator)
    elif not effective_separator:
        _set_child_text(content, "Separator", "/")
    if source is not None:
        _set_child_text(content, "Source", source)
    if date_type is not None:
        _set_child_text(content, "Type", date_type)

    if pretty:
        _indent(root)
    return ET.tostring(root, encoding="unicode", short_empty_elements=False)


def set_date_object_value_from_file(
    path: Union[str, Path],
    object_name: str,
    value: Union[str, date, datetime],
    **kwargs: Any,
) -> str:
    return set_date_object_value(Path(path).read_text(encoding="utf-8"), object_name, value, **kwargs)


@dataclass
class Font:
    name: str
    size: int
    style: Sequence[str] = field(default_factory=list)

    def to_element(self) -> ET.Element:
        element = ET.Element("Font")
        _add(element, "Name", self.name)
        _add(element, "Size", self.size)
        if self.style:
            _add(element, "Style", ",".join(self.style))
        return element


@dataclass
class TemplateObject:
    object_type: str
    name: str
    x: int
    y: int
    w: int
    h: int
    rotate: int = 0
    content: Mapping[str, Any] = field(default_factory=dict)
    font: Optional[Font] = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    def to_element(self) -> ET.Element:
        element = ET.Element("Object")
        _add(element, "ObjectType", self.object_type)
        _add(element, "Name", self.name)
        _add(element, "X", self.x)
        _add(element, "Y", self.y)
        _add(element, "W", self.w)
        _add(element, "H", self.h)
        _add(element, "Rotate", self.rotate)
        for key, value in self.extra.items():
            _add(element, key, value)
        if self.content:
            content_el = ET.SubElement(element, "Content")
            for key, value in self.content.items():
                _add(content_el, key, value)
        if self.font is not None:
            element.append(self.font.to_element())
        return element


@dataclass
class Template:
    name: str
    machine_type: str
    width: int
    height: int
    objects: List[TemplateObject] = field(default_factory=list)
    general_extra: Mapping[str, Any] = field(default_factory=dict)

    def add_object(self, item: TemplateObject) -> "Template":
        self.objects.append(item)
        return self

    def add_text(
        self,
        name: str,
        x: int,
        y: int,
        w: int,
        h: int,
        data: str,
        rotate: int = 0,
        source: str = "Internal",
        magnification_ratio: int = 100,
        font: Optional[Font] = None,
        **extra: Any,
    ) -> "Template":
        content = {
            "Data": data,
            "Source": source,
            "MagnificationRatio": magnification_ratio,
        }
        return self.add_object(
            TemplateObject("Text", name, x, y, w, h, rotate, content=content, font=font, extra=extra)
        )

    def add_barcode(
        self,
        name: str,
        x: int,
        y: int,
        w: int,
        h: int,
        data: str,
        barcode_type: str = "EAN13",
        rotate: int = 0,
        **extra: Any,
    ) -> "Template":
        content = {"Data": data, "BarcodeType": barcode_type}
        return self.add_object(
            TemplateObject("Barcode", name, x, y, w, h, rotate, content=content, extra=extra)
        )

    def add_2d_barcode(
        self,
        name: str,
        x: int,
        y: int,
        w: int,
        h: int,
        data: str,
        barcode_type: str = "QR",
        rotate: int = 0,
        **extra: Any,
    ) -> "Template":
        content = {"Data": data, "BarcodeType": barcode_type}
        return self.add_object(
            TemplateObject("2D Barcode", name, x, y, w, h, rotate, content=content, extra=extra)
        )

    def add_counter(
        self,
        name: str,
        x: int,
        y: int,
        w: int,
        h: int,
        start_value: Any,
        rotate: int = 0,
        font: Optional[Font] = None,
        **extra: Any,
    ) -> "Template":
        return self.add_object(
            TemplateObject(
                "Counter",
                name,
                x,
                y,
                w,
                h,
                rotate,
                content={"StartValue": start_value},
                font=font,
                extra=extra,
            )
        )

    def add_logo(
        self,
        name: str,
        x: int,
        y: int,
        w: int,
        h: int,
        data: str,
        rotate: int = 0,
        **extra: Any,
    ) -> "Template":
        return self.add_object(
            TemplateObject("Logo", name, x, y, w, h, rotate, content={"Data": data}, extra=extra)
        )

    def add_generic(
        self,
        object_type: str,
        name: str,
        x: int,
        y: int,
        w: int,
        h: int,
        rotate: int = 0,
        content: Optional[Mapping[str, Any]] = None,
        font: Optional[Font] = None,
        **extra: Any,
    ) -> "Template":
        return self.add_object(
            TemplateObject(
                object_type,
                name,
                x,
                y,
                w,
                h,
                rotate,
                content=content or {},
                font=font,
                extra=extra,
            )
        )

    def to_element(self) -> ET.Element:
        template = ET.Element("Template")
        general = ET.SubElement(template, "General")
        _add(general, "MachineType", self.machine_type)
        _add(general, "Name", self.name)
        _add(general, "Width", self.width)
        _add(general, "Height", self.height)
        for key, value in self.general_extra.items():
            _add(general, key, value)
        for item in self.objects:
            template.append(item.to_element())
        return template

    def to_xml(self, pretty: bool = False) -> str:
        element = self.to_element()
        if pretty:
            _indent(element)
        return ET.tostring(element, encoding="unicode", short_empty_elements=False)

