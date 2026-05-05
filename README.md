# Savema SPPL Python

Python library for building and sending Savema Printer Programming Language (SPPL)
commands over Ethernet or RS-232.

The implementation targets the commands listed in
`docs/Savema Printer - SPPL - Rev11.pdf` (Revision 11, 2022-05-10). The library
exposes typed helpers for the documented command set plus generic command
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

## Real printer smoke test

After installing the package, run a real-printer smoke test over TCP:

```powershell
sppl-smoke --host 192.168.1.123 --port 9100
```

Or through Python directly:

```powershell
python -m sppl.smoke --host 192.168.1.123
```

The default smoke plan is read-only: printer status, firmware, serial number,
ribbon, counters, active template, and stored templates. To include additional
read-only configuration reads:

```powershell
sppl-smoke --host 192.168.1.123 --include-configuration
```

Print-affecting probes are explicit:

```powershell
sppl-smoke --host 192.168.1.123 --unsafe-one-test-print
```

For RS-232, install the serial extra first:

```powershell
python -m pip install -e .[serial]
sppl-smoke --serial-port COM3 --baudrate 115200
```

## All getters on a real printer

For a full read-only getter pass against a printer IP:

```powershell
python main.py --host 192.168.1.123
```

If installed as a package, the same runner is available as:

```powershell
sppl-getters --host 192.168.1.123
```

Some getters require a template, field, queue field, or system parameter number.
Defaults are provided, but you can override them:

```powershell
python main.py --host 192.168.1.123 --template-file "C998 - TEST2_53.rox" --field-name TextCSV --queue-field PRDNAME --queue-field "BATCH NO" --system-parameter 1 --additional-setting 1
```

Known typo aliases from the PDF examples are skipped by default. Include them
only when you want to verify the controller behavior:

```powershell
python main.py --host 192.168.1.123 --include-document-typo-aliases
```

The Rev11 text also contains `SPGDTP` in one `SPGRES` response example, but the
actual documented total-print-count command is `SPGGTP`; `SPGDTP` is not exposed
as a command helper.

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

## Updating Date objects

Rev11 modification commands (`SPMCTV`, `SPMCBV`, `SPMC2D`, `SPMCSV`) are for
Text, Barcode, and 2D barcode objects whose source is External. The PDF does not
define a modification command for a `Date` object.

To keep a field as `ObjectType` `Date`, update the template XML Date object's
`<Data>` value and send the template with `SPLTDS`, then load it with `SPLLTF`.
For a fixed date field whose format is `dd/MM/yyyy` and separator is `/`, pass
the value as `26/10/2026`.

```python
from sppl import SPPLCommands, SavemaPrinterClient, set_date_object_value_from_file

commands = SPPLCommands()
xml = set_date_object_value_from_file(
    "docs/C999 - TEST1_53.rox",
    "test",
    "26/10/2026",
)

with SavemaPrinterClient.tcp("192.168.3.136", timeout=10) as printer:
    print(printer.execute(commands.create_template_data(xml)).raw)
    print(printer.execute(commands.load_template_file("C999 - TEST1_53.rox")).raw)
```

## Version and release flow

Development branches use `dev_x.y.z`, matching the version in `pyproject.toml`.
Pull requests run the test suite. Merges to `main` or `master` run tests first and
create a GitHub release from the package version only when tests pass.

