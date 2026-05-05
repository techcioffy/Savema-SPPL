"""XML template builder for SPLTDS commands."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, List, Mapping, Optional, Sequence
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

