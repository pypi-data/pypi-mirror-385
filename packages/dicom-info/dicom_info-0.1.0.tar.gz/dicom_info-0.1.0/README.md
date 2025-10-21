# dicom-info

A command-line tool for displaying DICOM file information.

## Description

dicom-info is a simple Python utility that reads and displays information from DICOM (Digital Imaging and Communications in Medicine) files. It provides a straightforward way to inspect DICOM file metadata from the command line.

## Requirements

- Python >= 3.13
- pydicom >= 3.0.1

## Installation

With uv:

```bash
uvx dicom-info
```

or pip

```bash
pip install dicom-info
```

## Usage

The basic syntax is:

```
dicom-info FILE [FILE ...]
```

Example:

```
dicom-info path/to/file.dcm
dicom-info file1.dcm file2.dcm file3.dcm
```

The tool will display information for each DICOM file, including all available metadata and attributes.

## Error Handling

The tool will exit with status code 1 if:
- Files are not found
- Files are not valid DICOM files

## License

This project is licensed under the GNU GPL version 3 license which can be found [here](LICENSE).

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
