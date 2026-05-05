# Savema SPPL Python

Python library for building and sending Savema Printer Programming Language (SPPL)
commands over Ethernet or RS-232.

The implementation targets the commands listed in
`docs/Savema Printer - SPPL  .pdf` (Revision 11, 2022-05-10). The available PDF
contains the command table and not the later detailed pages referenced by the
table of contents, so the library exposes both typed helpers and generic command
builders for model-specific extensions.

## Install for development

```powershell
python -m pip install -e .[dev]
python -m pytest
```

Optional serial transport:

```powershell
python -m pip install -e .[serial]
```

## Quick use

```python
from sppl import SPPLCommands, SavemaPrinterClient

commands = SPPLCommands()
print(commands.set_network_configuration("192.168.1.123", "255.255.255.0", "192.168.1.1", 9100))
# ~SPCSNC{192.168.1.123>255.255.255.0>192.168.1.1>9100}^

with SavemaPrinterClient.tcp("192.168.1.123", port=9100, timeout=5) as printer:
    response = printer.execute(commands.get_printer_status())
    print(response.raw)
```

## Template builder

```python
from sppl import Font, Template

template = (
    Template(name="temp1_53.ronx", machine_type="53x70I", width=640, height=480)
    .add_text("text1", x=10, y=63, w=105, h=33, data="savema Printer",
              rotate=180, font=Font(name="Arial", size=15, style=["Bold", "Italic"]))
)

command = SPPLCommands().create_template_data(template)
print(command)
```

## Version and release flow

Development branches use `dev_x.y.z`, matching the version in `pyproject.toml`.
Pull requests run the test suite. Merges to `main` or `master` run tests first and
create a GitHub release from the package version only when tests pass.

