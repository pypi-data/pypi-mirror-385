# Static DICOMweb Creator

[![PyPI version](https://badge.fury.io/py/static-dicomweb-creator.svg)](https://badge.fury.io/py/static-dicomweb-creator)
[![Python Support](https://img.shields.io/pypi/pyversions/static-dicomweb-creator.svg)](https://pypi.org/project/static-dicomweb-creator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library and CLI tool for generating static DICOMweb endpoints from DICOM files. Create self-contained, deployable medical imaging web applications without requiring a PACS server or database.

## ✨ Features

- 🚀 **Zero Server Requirements**: Generate static files that can be served from any web server or CDN
- 🔒 **Self-Contained**: All DICOM metadata and images converted to web-friendly formats
- 📊 **DICOMweb Compatible**: Generates standard DICOMweb API endpoints (WADO-RS)
- 🌐 **OHIF Viewer Ready**: Works out-of-the-box with OHIF Viewer for viewing medical images
- 📦 **Easy Deployment**: Includes docker templates

## 📋 Requirements

- Python 3.9 or higher
- Frontend viewer: [OHIF Viewer](https://ohif.org/) (recommended) or any DICOMweb-compatible viewer

## 🚀 Installation

### From PyPI

```bash
pip install static-dicomweb-creator
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## 📖 Usage

### Command Line Interface

Basic usage:

```bash
static-dicomweb-creator input_dicom_dir base_url output_web_dir
```

For OHIF viewer:

```bash
static-dicomweb-creator --ohif input_dicom_dir base_url output_web_dir
```

### Python API

```python
from static_dicomweb_creator.creator import StaticDICOMWebCreator
from static_dicomweb_creator.utils import list_dicom_files

creator = StaticDICOMWebCreator(
    output_path="/path/to/web",
    root_uri="https://example.com/dicomweb/"
)

for dcm_path in list_dicom_files("/path/to/dicom_files"):
    dcm = pydicom.dcmread(dcm_path)
    creator.add_dcm_instance(dcm)
creator.create_json()
```

## 🏗️ Architecture

```
Input DICOM Files
       ↓
Static DICOMweb Creator
       ↓
Generated Output:
└ studies/
    ├ index.json
    └ {StudyInstanceUID}/
         └ series/
              ├ index.json
              └ {SeriesInstanceUID}/
                   ├ index.json
                   ├ metadata
                   │   └ index.json
                   └ instances/
                        └ {SOPInstanceUID}/
                            ├ metadata
                            │  └ index.json
                            ├ frame
                            │  └ {frame_number}/
                            │       └ index.json
                            └ bulkdata
                                └ {tag}/
                                    └ index.json
```

## 🌐 Deployment

### With Docker Compose (Recommended)

This repository includes a ready-to-use Docker Compose setup with OHIF Viewer and Nginx:

```bash
# use samle_docker/docker-compose.yml placing your generated output in static_dicomweb/
docker-compose up
```

Access the viewer at `http://localhost`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OHIF Viewer](https://ohif.org/) - Open Health Imaging Foundation
- [pydicom](https://pydicom.github.io/) - Python library for DICOM files
- [DICOMweb](https://www.dicomstandard.org/using/dicomweb) - Web standard for medical imaging
