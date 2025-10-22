# muse2wfdb
### Convert GE MUSE XML ECG exports to WFDB format

`muse2wfdb` is a lightweight Python library that converts ECG data exported from the GE MUSE Resting ECG System (in XML format) into WFDB (WaveForm DataBase) format, compatible with PhysioNet tools and the wfdb Python package.

## Installation

Install directly from PyPI:

```bash
pip install muse2wfdb
```

Or install locally from source:

```bash
git clone https://github.com/nagyl1999/muse2wfdb.git
cd muse2wfdb
pip install .
```

## Usage

An example is provided in the `examples` folder.

```python
from muse2wfdb.converter import muse_to_wfdb
import wfdb

muse_export = "examples/anonim_pac_xml_export.txt"
wfdb_filename = "patient001_ecg"

annotations = muse_to_wfdb(muse_export, wfdb_filename, ['Age: 75', 'Dx: 316998'])

record = wfdb.rdrecord(wfdb_filename)
annotation = None

if annotations:
    annotation = wfdb.rdann(wfdb_filename, 'atr')

wfdb.plot_wfdb(record=record, annotation=annotation, title="MUSE exported ECG")
```
