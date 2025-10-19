"""Main module for Static DICOM Web Creator."""

import argparse
import sys

import pydicom

from .utils import list_dicom_files
from .creator import StaticDICOMWebCreator, StaticDICOMWebCreatorForOHIFViewer


def main() -> int:
    p = argparse.ArgumentParser(description="Create static DICOMweb (wado-rs) assets.")
    p.add_argument("dicomdir", help="Directory containing DICOM files")
    p.add_argument("url", help="Base URL of static dicomweb assets (e.g., https://example.com/dicom-web/, or /dicomweb/)")
    p.add_argument("outdir", help="Output directory")
    p.add_argument("--ohif", action="store_true", help="Create assets for OHIF Viewer")
    args = p.parse_args()

    if args.ohif:
        creator = StaticDICOMWebCreatorForOHIFViewer(
            output_path=args.outdir,
            root_uri=args.url
        )
    else:
        creator = StaticDICOMWebCreator(
            output_path=args.outdir,
            root_uri=args.url
        )

    for dcm_path in list_dicom_files(args.dicomdir):
        dcm = pydicom.dcmread(dcm_path)
        creator.add_dcm_instance(dcm)
    creator.create_json()

    return 0


if __name__ == "__main__":
    sys.exit(main())
