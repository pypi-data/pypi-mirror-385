"""Main entry point into the dicom-info CLI."""

# ruff: noqa: T201

from __future__ import annotations

# Python imports
import argparse
import sys

# Module imports
import pydicom


def print_stats(files: list[str]) -> None:
    """Print DICOM information for the files."""
    try:
        dcms = [pydicom.dcmread(f) for f in files]

    except (FileNotFoundError, pydicom.errors.InvalidDicomError) as err:
        print(f"Files could not be read due to {err}")
        sys.exit(1)

    for f, dcm in zip(files, dcms, strict=True):
        banner = "*" * 5 + f" {f} " + "*" * 5
        print(banner, dcm, sep="\n")


def main() -> None:
    """Entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Print DICOM file information.",
     )

    parser.add_argument(
        "file",
        help="Path to the DICOM file(s).",
        nargs="+",
        type=str,
    )

    args = parser.parse_args()

    # Print dicom info
    print_stats(args.file)


if __name__ == "__main__":
    main()
