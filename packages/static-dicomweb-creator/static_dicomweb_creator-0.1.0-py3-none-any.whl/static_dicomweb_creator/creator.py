#!/usr/bin/env python
# coding: UTF-8

from itertools import groupby
import os
from pathlib import Path
import re
from typing import Optional, Sequence, cast

import pydicom
from pydicom.encaps import generate_frames

from .utils import read_json, write_json, write_binary
from . import multipart_related


class StaticDICOMWebCreator:
    def __init__(self, output_path: str | Path,
                 root_uri="/",
                 bulkdata_dirname="bulkdata",
                 bulkdata_threshold=1024 * 50,  # 50KB
                 write_bulkdata_pixeldata=False,
                 included_fields_for_study: Sequence[str | int] = [],
                 included_fields_for_series: Sequence[str | int] = [],
                 write_json_fmt=True,
                 write_gzip_fmt=False,
                 verbose=False
                 ):
        self.output_path = Path(output_path)
        self.root_uri = str(root_uri)
        self.bulk_data_dirname = str(bulkdata_dirname)
        self.bulk_data_threshold = int(bulkdata_threshold)
        self.write_bulkdata_pixeldata = write_bulkdata_pixeldata
        self.write_json_fmt = write_json_fmt
        self.write_gzip_fmt = write_gzip_fmt
        self.verbose = verbose

        self.included_fields_for_study = self.validate_included_fields(included_fields_for_study)
        self.included_fields_for_series = self.validate_included_fields(included_fields_for_series)

    def validate_included_fields(self, fields: Sequence[str | int]) -> list[str]:
        validated_fields = []
        for field in fields:
            if isinstance(field, int):
                field_str = f"{field:08X}"
            else:
                field_str = str(field).upper()

            assert len(field_str) == 8, f"Field string must be 8 characters: {field_str}"
            assert field_str == f"{int(field_str, 16):08X}", f"Field string must be hexadecimal: {field_str}"

            validated_fields.append(field_str)

        return validated_fields

    def add_dcm_instance(self, dcm: pydicom.Dataset):
        assert isinstance(dcm, pydicom.Dataset), f"Expected pydicom.Dataset, got {type(dcm)}"

        json_dict, bulkdata_elem_list = self.dcm_to_json_dict(dcm)

        # Write bulk data
        for elem in bulkdata_elem_list:
            # In case of pixel data
            if elem.tag == 0x7FE00010:
                number_of_frames = dcm.get('NumberOfFrames', 1)
                transfer_syntax_uid = str(dcm.file_meta.TransferSyntaxUID)

                for i, frame in enumerate(generate_frames(dcm.PixelData)):
                    frame_path = self.build_path_instance_frame(dcm, i + 1)
                    self.write_binary(frame_path, frame, transfer_syntax_uid)

                    if self.verbose:
                        print(f"Writing frame {i + 1}/{number_of_frames} to {frame_path}")

                if self.write_bulkdata_pixeldata:
                    bulkdata_path = self.build_path_instance_bulk(dcm, elem)
                    self.write_binary(bulkdata_path, elem.value)

                    bulkdata_uri = self.build_uri_instance_bulk(dcm, elem)
                    json_dict["7FE00010"] = {
                        "vr": "OB",
                        "BulkDataURI": bulkdata_uri
                    }

                    if self.verbose:
                        print(f"Writing bulk pixel data to {bulkdata_path}")
                else:
                    del json_dict["7FE00010"]
            else:
                bulkdata_path = self.build_path_instance_bulk(dcm, elem)
                bulk_data = elem.value
                self.write_binary(bulkdata_path, bulk_data)

                bulkdata_uri = self.build_uri_instance_bulk(dcm, elem)
                json_dict[f"{elem.tag:08X}"] = {
                    "vr": "OB",
                    "BulkDataURI": bulkdata_uri
                }

        # Write metadata
        instance_metadata_path = self.build_path_instance_metadata(dcm)
        self.write_json(instance_metadata_path, json_dict)

    def create_json(self):
        for study_dir_path in self.list_study_dirs():
            print(study_dir_path)

            for series_dir_path in self.list_series_dirs(study_dir_path):
                print(" ", series_dir_path)

                self.create_series_json(series_dir_path)
                self.create_series_metadata_json(series_dir_path)

            self.create_all_series_json(study_dir_path)

        self.create_all_studies_json()

    def create_series_json(self, series_dir_path: str | Path):
        series_dir_path = Path(series_dir_path)
        json_dict = {}
        instance_metadata_dir_path_list = self.list_instance_metadata_dirs(series_dir_path)
        for instance_metadata_dir_path in instance_metadata_dir_path_list:
            json_dict = self.read_json(instance_metadata_dir_path / "index.json")
            json_dict = cast(dict, json_dict)
            break

        series_dict = self.filter_json_dict_for_series(json_dict)
        series_dict["00201209"] = {
            "Value": len(instance_metadata_dir_path_list),
            "vr": "IS"}  # Number of Series Related Instances

        series_json_path = series_dir_path / "index.json"
        self.write_json(series_json_path, series_dict)

    def create_series_metadata_json(self, series_dir_path: str | Path):
        series_dir_path = Path(series_dir_path)

        series_metadata_list = []
        instance_metadata_dir_path_list = self.list_instance_metadata_dirs(series_dir_path)

        assert len(instance_metadata_dir_path_list) > 0, f"No instance metadata found in series {series_dir_path}"
        json_dict = {}

        for instance_metadata_dir_path in instance_metadata_dir_path_list:
            json_dict = self.read_json(instance_metadata_dir_path / "index.json")
            json_dict = cast(dict, json_dict)
            series_metadata_list.append(json_dict)

        dcm = pydicom.Dataset.from_json(json_dict)
        series_metadata_path = self.build_path_series_metadata_json(dcm)
        self.write_json(series_metadata_path, series_metadata_list)

    def create_all_series_json(self, study_dir_path: str | Path):
        study_dir_path = Path(study_dir_path)

        all_series_json_dict_list = []
        modalities = set()
        num_series = 0
        num_instances = 0
        series_dir_path_list = self.list_series_dirs(study_dir_path)

        # Get study-level metadata from the first instance metadata
        study_json_dict = {}
        for series_dir_path in series_dir_path_list:
            instance_metadata_dir_path_list = self.list_instance_metadata_dirs(series_dir_path)
            if len(instance_metadata_dir_path_list) > 0:
                first_instance_metadata_path = instance_metadata_dir_path_list[0] / "index.json"
                instance_json_dict = self.read_json(first_instance_metadata_path)
                instance_json_dict = cast(dict, instance_json_dict)
                study_json_dict = self.filter_json_dict_for_study(instance_json_dict)
                break

        assert len(study_json_dict.keys()) > 0, f"No instance metadata found in study {study_dir_path}"

        # Read series metadata
        for series_dir_path in series_dir_path_list:
            series_json_path = series_dir_path / "index.json"

            if not series_json_path.is_file() and not series_json_path.with_suffix(".gz").is_file():
                self.create_series_json(series_dir_path)

            series_json_dict = self.read_json(series_json_path)
            series_json_dict = cast(dict, series_json_dict)
            series_json_dict.update(study_json_dict)  # Add study-level metadata
            all_series_json_dict_list.append(series_json_dict)
            num_series += 1
            num_instances += series_json_dict.get("00201209", {}).get("Value", 0)

            modality = series_json_dict.get("00080060", {}).get("Value", [""])[0]
            if modality != "":
                modalities.add(modality)

        # Set values for dicomweb standard tags
        for json_dict in all_series_json_dict_list:
            json_dict["00080061"]["Value"] = list(modalities)
            json_dict["00201206"]["Value"] = num_series  # Number of Study Related Series
            json_dict["00201208"]["Value"] = num_instances  # Number of Study Related Instances

        dcm = pydicom.Dataset()
        dcm.StudyInstanceUID = study_dir_path.name
        all_series_json_path = self.build_path_all_series_json(dcm)
        self.write_json(all_series_json_path, all_series_json_dict_list)

    def create_all_studies_json(self):
        all_studies_json_dict_list = []
        study_dir_path_list = self.list_study_dirs()

        for study_dir_path in study_dir_path_list:
            dcm = pydicom.Dataset()
            dcm.StudyInstanceUID = study_dir_path.name
            all_series_json_path = self.build_path_all_series_json(dcm)

            if not all_series_json_path.is_file() and not all_series_json_path.with_suffix(".gz").is_file():
                self.create_all_series_json(study_dir_path)

            all_series_json_dict_list = self.read_json(all_series_json_path)
            series_json_dict = self.filter_json_dict_for_study(all_series_json_dict_list[0])
            all_studies_json_dict_list.append(series_json_dict)

        all_studies_json_path = self.output_path / "studies" / "index.json"
        self.write_json(all_studies_json_path, all_studies_json_dict_list)

    def filter_json_dict_for_study(self, json_dict: dict) -> dict:
        json_dict_filtered = {
            # Tags defined in DICOMweb standard
            "00080020": json_dict.get("00080020", ""),  # Study Date
            "00080030": json_dict.get("00080030", ""),  # Study Time
            "00080050": json_dict.get("00080050", ""),  # Accession Number
            "00080061": {"Value": [], "vr": "CS"},  # Modalities in Study
            "00080090": json_dict.get("00080090", ""),  # Referring Physician's Name
            "00100010": json_dict.get("00100010", ""),  # Patient's Name
            "00100020": json_dict.get("00100020", ""),  # Patient ID
            "00100030": json_dict.get("00100030", ""),  # Patient's Birth Date
            "00100040": json_dict.get("00100040", ""),  # Patient's Sex
            "0020000D": json_dict.get("0020000D", ""),  # Study Instance UID
            "00200010": json_dict.get("00200010", ""),  # Study ID
            "00201206": json_dict.get("00201206", {"Value": 0, "vr": "IS"}),  # Number of Study Related Series
            "00201208": json_dict.get("00201208", {"Value": 0, "vr": "IS"}),  # Number of Study Related Instances
        }

        for field in self.included_fields_for_study:
            if isinstance(field, int):
                field = f"{field:08X}"
            field = str(field)

            if field not in json_dict_filtered:
                json_dict_filtered[field] = json_dict.get(field, "")

        return json_dict_filtered

    def filter_json_dict_for_series(self, json_dict: dict) -> dict:
        json_dict_filtered = {
            # Tags defined in DICOMweb standard
            "00080060": json_dict.get("00080060", ""),  # Modality
            "00081190": json_dict.get("00081190", {"Value": [], "vr": "UR"}),  # Retrieve URL
            "0020000E": json_dict.get("0020000E", ""),  # Series Instance UID
            "00200011": json_dict.get("00200011", ""),  # Series Number
            "00201209": json_dict.get("00201209", {"Value": 0, "vr": "IS"}),  # Number of Series Related Instances
        }

        for field in self.included_fields_for_series:
            if isinstance(field, int):
                field = f"{field:08X}"
            field = str(field)

            if field not in json_dict_filtered:
                json_dict_filtered[field] = json_dict.get(field, "")

        return json_dict_filtered

    def dcm_to_json_dict(self, dcm: pydicom.Dataset) -> tuple[dict, list[pydicom.DataElement]]:
        bulkdata_list: list[pydicom.DataElement] = []

        def handler(elem: pydicom.DataElement) -> str:
            bulkdata_list.append(elem)
            return ""

        json_dict = dcm.to_json_dict(bulk_data_threshold=self.bulk_data_threshold,
                                     bulk_data_element_handler=handler)

        return json_dict, bulkdata_list

    def read_json(self, path: Path) -> list[dict] | dict:
        path_gz = Path(str(path) + ".gz")

        if path.is_file() and path.stat().st_size > 0:
            ret = read_json(path)
        elif path_gz.is_file():
            ret = read_json(path, is_gzip=True)
        else:
            raise FileNotFoundError(f"JSON file not found: {path} or {path_gz}")

        return ret

    def write_json(self, path: Path, json_dict: list[dict] | dict):
        if self.write_json_fmt:
            write_json(path, json_dict, write_json_fmt=True, write_gzip_fmt=False)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()

        if self.write_gzip_fmt:
            write_json(path, json_dict, write_json_fmt=False, write_gzip_fmt=True)

    def write_binary(self, path: Path, data: bytes, transfer_syntax_uid=""):
        data_to_write = bytes()
        data_to_write += multipart_related.create_part_header_for_multipart_related(transfer_syntax_uid).encode(encoding="ascii")
        data_to_write += data
        data_to_write += f"\r\n--{multipart_related.DEFAULT_BOUNDARY}".encode("ascii")

        write_binary(path, data_to_write)

    def is_dicom_uid_format(self, s: str) -> bool:
        return re.match(r"^[1-9]+(\.[0-9]+)*$", s) is not None

    def list_study_dirs(self) -> list[Path]:
        study_dir_path_list = []

        for dir_path in (self.output_path / "studies").glob("*"):
            if dir_path.is_dir() and self.is_dicom_uid_format(dir_path.name):
                study_dir_path_list.append(dir_path)

        return study_dir_path_list

    def list_series_dirs(self, study_dir_path: str | Path) -> list[Path]:
        study_dir_path = Path(study_dir_path)
        series_dir_path_list = []

        for dir_path in study_dir_path.glob("series/*"):
            if dir_path.is_dir() and self.is_dicom_uid_format(dir_path.name):
                series_dir_path_list.append(dir_path)

        return series_dir_path_list

    def list_instance_metadata_dirs(self, series_dir_path: str | Path) -> list[Path]:
        series_dir_path = Path(series_dir_path)
        instance_metadata_dir_path_list = []

        for dir_path in series_dir_path.glob("instances/*/metadata"):
            if dir_path.is_dir() and self.is_dicom_uid_format(dir_path.parent.name):
                instance_metadata_dir_path_list.append(dir_path)

        return instance_metadata_dir_path_list

    def build_path_study(self, dcm: pydicom.Dataset) -> Path:
        return self.output_path / "studies" / dcm.StudyInstanceUID

    def build_path_all_studies_json(self) -> Path:
        return self.output_path / "studies" / "index.json"

    def build_path_all_series_json(self, dcm: pydicom.Dataset) -> Path:
        return self.build_path_study(dcm) / "series" / "index.json"

    def build_path_series(self, dcm: pydicom.Dataset) -> Path:
        return self.build_path_study(dcm) / "series" / dcm.SeriesInstanceUID

    def build_path_series_json(self, dcm: pydicom.Dataset) -> Path:
        return self.build_path_series(dcm) / "index.json"

    def build_path_series_metadata_json(self, dcm: pydicom.Dataset) -> Path:
        return self.build_path_series(dcm) / "metadata" / "index.json"

    def build_path_instance(self, dcm: pydicom.Dataset) -> Path:
        return self.build_path_series(dcm) / "instances" / dcm.SOPInstanceUID

    def build_path_instance_metadata(self, dcm: pydicom.Dataset) -> Path:
        return self.build_path_instance(dcm) / "metadata" / "index.json"

    def build_path_instance_frame(self, dcm: pydicom.Dataset, frame_number: Optional[int] = None) -> Path:
        dir_path = self.build_path_instance(dcm) / "frames"
        if frame_number is None:
            frame_number = dcm.get('FrameNumber', 1)
        return dir_path / str(frame_number) / "index.bin"

    def build_uri_instance_frame(self, dcm: pydicom.Dataset, frame_number: Optional[int] = None) -> str:
        filepath = self.build_path_instance_frame(dcm, frame_number)
        uri = os.path.join(self.root_uri, filepath.relative_to(self.output_path))
        return uri

    def build_path_instance_bulk(self, dcm: pydicom.Dataset, elem: pydicom.DataElement) -> Path:
        return self.build_path_instance(dcm) / self.bulk_data_dirname / f"{int(elem.tag):08X}" / "index.bin"

    def build_uri_instance_bulk(self, dcm: pydicom.Dataset, elem: pydicom.DataElement) -> str:
        filepath = self.build_path_instance_bulk(dcm, elem)
        uri = os.path.join(self.root_uri, filepath.relative_to(self.output_path))
        return uri


class StaticDICOMWebCreatorForOHIFViewer(StaticDICOMWebCreator):
    def __init__(self, output_path: str | Path,
                 root_uri="/",
                 bulkdata_dirname="bulkdata",
                 bulkdata_threshold=1024 * 50,  # 50KB
                 write_bulkdata_pixeldata=False,
                 included_fields_for_study: Sequence[str | int] = [],
                 included_fields_for_series: Sequence[str | int] = [],
                 patient_study_dirname="patients",
                 verbose=False
                 ):
        # Set default included fields for OHIF viewer
        included_fields_for_study = [
            "00080060",  # Modality
        ]
        included_fields_for_series = [
            "00080021",  # Series Date
            "00080031",  # Series Time
            "0008103E",  # Series Description
        ]
        self.patient_study_dirname = str(patient_study_dirname)

        write_json_fmt = False
        write_gzip_fmt = True

        super().__init__(output_path,
                         root_uri,
                         bulkdata_dirname,
                         bulkdata_threshold,
                         write_bulkdata_pixeldata,
                         included_fields_for_study,
                         included_fields_for_series,
                         write_json_fmt,
                         write_gzip_fmt,
                         verbose)

    def create_json(self):
        super().create_json()
        self.create_patient_study_json()

    def create_patient_study_json(self):
        all_studies_json_dict: list[dict] = self.read_json(self.build_path_all_studies_json())  # type: ignore

        # (0010, 0020) Patient ID
        def get_patient_id(json_dict: dict) -> str:
            return json_dict.get("00100020", {}).get("Value", [""])[0]

        all_studies_json_dict = sorted(all_studies_json_dict, key=get_patient_id)
        for patient_id, patient_json_dict_list in groupby(all_studies_json_dict, key=get_patient_id):
            studies_json_dict_list = list(patient_json_dict_list)

            patient_study_json_path = self.build_path_patient_study_json(patient_id)
            self.write_json(patient_study_json_path, studies_json_dict_list)

    def build_path_patient_study_json(self, patient_id: str) -> Path:
        return self.output_path / self.patient_study_dirname / patient_id / "index.json"
