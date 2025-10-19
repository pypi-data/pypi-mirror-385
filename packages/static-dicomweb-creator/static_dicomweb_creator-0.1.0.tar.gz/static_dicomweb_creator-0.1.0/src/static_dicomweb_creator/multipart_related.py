#!/usr/bin/env python
# coding: UTF-8

from collections import defaultdict

TransferSyntaxUID_TO_MIME = defaultdict(lambda: "application/octet-stream")
TransferSyntaxUID_TO_MIME.update({
    # Implicit/Explicit LE/BE
    "1.2.840.10008.1.2":       "application/octet-stream",  # Implicit VR LE
    "1.2.840.10008.1.2.1":     "application/octet-stream",  # Explicit VR LE
    "1.2.840.10008.1.2.2":     "application/octet-stream",  # Explicit VR BE
    "1.2.840.10008.1.2.5":     "image/dicom-rle",  # RLE Lossless (no specified mime)

    # JPEG
    "1.2.840.10008.1.2.4.50":  "image/jpeg",   # JPEG Baseline
    "1.2.840.10008.1.2.4.51":  "image/jpeg",   # JPEG Extended
    "1.2.840.10008.1.2.4.57":  "image/jpeg",   # Lossless (not recommended)
    "1.2.840.10008.1.2.4.70":  "image/jpeg",   # Lossless (SV1)

    # JPEG-LS
    "1.2.840.10008.1.2.4.80":  "image/jls",  # JPEG-LS Lossless
    "1.2.840.10008.1.2.4.81":  "image/jls",  # JPEG-LS Near-Lossless

    # JPEG 2000
    "1.2.840.10008.1.2.4.90":  "image/jp2",  # J2K Lossless
    "1.2.840.10008.1.2.4.91":  "image/jp2",  # J2K Lossy
})

DEFAULT_BOUNDARY = "BOUNDARY_Wd42U4ChxrwWG0qM0QzuR0vR"


def create_content_type_for_response_header(boundary=DEFAULT_BOUNDARY):
    text = f"multipart/related; type=\"application/octet-stream\"; boundary={boundary}"
    return text


def create_part_header_for_multipart_related(transfer_syntax_uid: str,
                                             boundary=DEFAULT_BOUNDARY):
    text = ""
    text += f"--{boundary}\r\n"
    text += f'Content-Type: {TransferSyntaxUID_TO_MIME[transfer_syntax_uid]};transfer-syntax={transfer_syntax_uid}\r\n'
    text += "\r\n"

    return text
