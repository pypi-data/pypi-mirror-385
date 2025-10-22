# Copyright (C) 2020-2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from datetime import datetime
import hashlib
from importlib.metadata import version
import logging
import math
from types import TracebackType
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union, cast

from pyorc import (
    BigInt,
    Binary,
    CompressionKind,
    Int,
    SmallInt,
    String,
    Struct,
    Timestamp,
    TypeKind,
    Writer,
)
from pyorc.converters import ORCConverter

from swh.model.hashutil import hash_to_hex
from swh.model.model import (
    Content,
    Directory,
    Origin,
    OriginVisit,
    OriginVisitStatus,
    Release,
    Revision,
    SkippedContent,
    Snapshot,
    TimestampWithTimezone,
)

from ..exporter import ExporterDispatch
from ..relational import BLOOM_FILTER_COLUMNS, MAIN_TABLES, TABLES
from ..utils import remove_pull_requests, subdirectories_for_object_type

ObjNotFoundError: Type[Exception]
get_objstorage: Optional[Callable]
try:
    from swh.objstorage.factory import get_objstorage
    from swh.objstorage.objstorage import ObjNotFoundError
except ImportError:
    get_objstorage = None
    ObjNotFoundError = Exception  # helps keep mypy happy


ORC_TYPE_MAP = {
    "string": String,
    "smallint": SmallInt,
    "int": Int,
    "bigint": BigInt,
    "timestamp": Timestamp,
    "binary": Binary,
}

EXPORT_SCHEMA = {
    table_name: Struct(
        **{
            column_name: ORC_TYPE_MAP[column_type]()
            for column_name, column_type in columns
        }
    )
    for table_name, columns in TABLES.items()
}


logger = logging.getLogger(__name__)


def hash_to_hex_or_none(hash):
    return hash_to_hex(hash) if hash is not None else None


def swh_date_to_tuple(
    obj: Optional[TimestampWithTimezone],
) -> Union[Tuple[None, None, None], Tuple[Tuple[int, int], int, bytes]]:
    if obj is None or obj.timestamp is None:
        return (None, None, None)
    return (
        (obj.timestamp.seconds, obj.timestamp.microseconds),
        obj.offset_minutes(),
        obj.offset_bytes,
    )


def datetime_to_tuple(obj: Optional[datetime]) -> Optional[Tuple[int, int]]:
    if obj is None:
        return None
    return (math.floor(obj.timestamp()), obj.microsecond)


class SWHTimestampConverter:
    """This is an ORCConverter compatible class to convert timestamps from/to ORC files

    timestamps in python are given as a couple (seconds, microseconds) and are
    serialized as a couple (seconds, nanoseconds) in the ORC file.

    Reimplemented because we do not want the Python object to be converted as
    ORC timestamp to be Python datatime objects, since swh.model's Timestamp
    cannot be converted without loss a Python datetime objects.
    """

    # use Any as timezone annotation to make it easier to run mypy on python <
    # 3.9, plus we do not use the timezone argument here...
    @staticmethod
    def from_orc(
        seconds: int,
        nanoseconds: int,
        timezone: Any,
    ) -> Tuple[int, int]:
        return (seconds, nanoseconds // 1000)

    @staticmethod
    def to_orc(
        obj: Optional[Tuple[int, int]],
        timezone: Any,
    ) -> Optional[Tuple[int, Optional[int]]]:
        if obj is None:
            return None
        return (obj[0], obj[1] * 1000 if obj[1] is not None else None)


class ORCExporter(ExporterDispatch):
    """
    Implementation of an exporter which writes the entire graph dataset as
    ORC files. Useful for large scale processing, notably on cloud instances
    (e.g BigQuery, Amazon Athena, Azure).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = self.config.get("orc", {})
        self.max_rows = config.get("max_rows", {})
        invalid_tables = [
            table_name for table_name in self.max_rows if table_name not in MAIN_TABLES
        ]
        if invalid_tables:
            raise ValueError(
                "Limiting the number of secondary table (%s) is not supported "
                "for now.",
                invalid_tables,
            )
        self.with_data = config.get("with_data", False)
        self.objstorage = None
        if self.with_data:
            if get_objstorage is None:
                raise EnvironmentError(
                    "The swh-objstorage dependency package must be installed "
                    "when 'with_data' is set. Please install 'swh.export[with-content]'"
                )
            if "objstorage" not in config:
                raise ValueError(
                    "The 'objstorage' configuration entry is mandatory when 'with_data' is set."
                )
            self.objstorage = get_objstorage(**config["objstorage"])

        for object_type in self.object_types:
            for subdir in subdirectories_for_object_type(object_type.lower()):
                (self.export_path / subdir).mkdir(parents=True, exist_ok=True)

        self._reset()

    def _reset(self):
        self.writers = {}
        self.writer_files = {}
        self.uuids = {}
        self.uuid_main_table = {}

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        for writer in self.writers.values():
            writer.close()
        for fileobj in self.writer_files.values():
            fileobj.close()
        self._reset()
        return super().__exit__(exc_type, exc_value, traceback)

    def maybe_close_writer_for(self, table_name: str):
        uuid = self.uuids.get(table_name)
        if (
            uuid is not None
            and table_name in self.max_rows
            and self.writers[table_name].current_row >= self.max_rows[table_name]
        ):
            main_table = self.uuid_main_table[uuid]
            if table_name != main_table:
                logger.warning(
                    "Limiting the number of secondary table (%s) is not supported "
                    "for now (size limit ignored).",
                    table_name,
                )
            else:
                # sync/close all tables having the current uuid (aka main and
                # related tables)
                for table in [
                    tname for tname, tuuid in self.uuids.items() if tuuid == uuid
                ]:
                    # close the writer and remove from the writers dict
                    self.writers.pop(table).close()
                    self.writer_files.pop(table).close()
                    # and clean uuids dicts
                    self.uuids.pop(table)
                    self.uuid_main_table.pop(uuid, None)

    def get_writer_for(self, table_name: str, unique_id=None):
        self.maybe_close_writer_for(table_name)
        if table_name not in self.writers:
            object_type_dir = self.export_path / table_name
            if unique_id is None:
                unique_id = self.get_unique_file_id()
                self.uuid_main_table[unique_id] = table_name
            export_file = object_type_dir / (f"{table_name}-{unique_id}.orc")
            export_obj = export_file.open("wb")
            self.writer_files[table_name] = export_obj
            self.writers[table_name] = Writer(
                export_obj,
                EXPORT_SCHEMA[table_name],
                compression=CompressionKind.ZSTD,
                converters={
                    TypeKind.TIMESTAMP: cast(Type[ORCConverter], SWHTimestampConverter)
                },
                bloom_filter_columns=BLOOM_FILTER_COLUMNS[table_name],
            )

            self.writers[table_name].set_user_metadata(
                swh_object_type=table_name.encode(),
                swh_uuid=unique_id.encode(),
                swh_model_version=version("swh.model").encode(),
                swh_export_version=version("swh.export").encode(),
                # maybe put a copy of the config (redacted) also?
            )
            self.uuids[table_name] = unique_id

        return self.writers[table_name]

    def process_origin(self, origin: Origin):
        origin_writer = self.get_writer_for("origin")
        origin_writer.write(
            (
                hashlib.sha1(origin.url.encode()).hexdigest(),
                origin.url,
            )
        )

    def process_origin_visit(self, visit: OriginVisit):
        origin_visit_writer = self.get_writer_for("origin_visit")
        origin_visit_writer.write(
            (
                visit.origin,
                visit.visit,
                datetime_to_tuple(visit.date),
                visit.type,
            )
        )

    def process_origin_visit_status(self, visit_status: OriginVisitStatus):
        origin_visit_status_writer = self.get_writer_for("origin_visit_status")
        origin_visit_status_writer.write(
            (
                visit_status.origin,
                visit_status.visit,
                datetime_to_tuple(visit_status.date),
                visit_status.status,
                hash_to_hex_or_none(visit_status.snapshot),
                # missing from old messages
                visit_status.type if hasattr(visit_status, "type") else None,
            )
        )

    def process_snapshot(self, snapshot: Snapshot):
        if self.config.get("orc", {}).get("remove_pull_requests"):
            snapshot = remove_pull_requests(snapshot)
        snapshot_writer = self.get_writer_for("snapshot")
        snapshot_writer.write((hash_to_hex_or_none(snapshot.id),))

        # we want to store branches in the same directory as snapshot objects,
        # and have both files have the same UUID.
        snapshot_branch_writer = self.get_writer_for(
            "snapshot_branch",
            unique_id=self.uuids["snapshot"],
        )
        for branch_name, branch in snapshot.branches.items():
            if branch is None:
                continue
            snapshot_branch_writer.write(
                (
                    hash_to_hex_or_none(snapshot.id),
                    branch_name,
                    hash_to_hex_or_none(branch.target),
                    branch.target_type.value,
                )
            )

    def process_release(self, release: Release):
        release_writer = self.get_writer_for("release")
        release_writer.write(
            (
                hash_to_hex_or_none(release.id),
                release.name,
                release.message,
                hash_to_hex_or_none(release.target),
                release.target_type.value,
                (release.author.fullname if release.author is not None else None),
                *swh_date_to_tuple(release.date),
                release.raw_manifest,
            )
        )

    def process_revision(self, revision: Revision):
        release_writer = self.get_writer_for("revision")
        release_writer.write(
            (
                hash_to_hex_or_none(revision.id),
                revision.message,
                (revision.author.fullname if revision.author is not None else None),
                *swh_date_to_tuple(revision.date),
                (
                    revision.committer.fullname
                    if revision.committer is not None
                    else None
                ),
                *swh_date_to_tuple(revision.committer_date),
                hash_to_hex_or_none(revision.directory),
                revision.type.value,
                revision.raw_manifest,
            )
        )

        revision_history_writer = self.get_writer_for(
            "revision_history",
            unique_id=self.uuids["revision"],
        )
        for i, parent_id in enumerate(revision.parents):
            revision_history_writer.write(
                (
                    hash_to_hex_or_none(revision.id),
                    hash_to_hex_or_none(parent_id),
                    i,
                )
            )

        revision_header_writer = self.get_writer_for(
            "revision_extra_headers",
            unique_id=self.uuids["revision"],
        )
        for key, value in revision.extra_headers:
            revision_header_writer.write((hash_to_hex_or_none(revision.id), key, value))

    def process_directory(self, directory: Directory):
        directory_writer = self.get_writer_for("directory")
        directory_writer.write(
            (
                hash_to_hex_or_none(directory.id),
                directory.raw_manifest,
            )
        )

        directory_entry_writer = self.get_writer_for(
            "directory_entry",
            unique_id=self.uuids["directory"],
        )
        for entry in directory.entries:
            directory_entry_writer.write(
                (
                    hash_to_hex_or_none(directory.id),
                    entry.name,
                    entry.type,
                    hash_to_hex_or_none(entry.target),
                    entry.perms,
                )
            )

    def process_content(self, content: Content):
        content_writer = self.get_writer_for("content")
        data = None
        if self.with_data:
            obj_id = cast(Dict[str, bytes], content.hashes())
            try:
                data = self.objstorage.get(obj_id)
            except ObjNotFoundError:
                if logger.isEnabledFor(logging.WARNING):
                    formatted_id = ";".join(
                        f"{algo}:{hash.hex()}" for algo, hash in sorted(obj_id.items())
                    )

                    logger.warning("Missing object %s", formatted_id)

        content_writer.write(
            (
                hash_to_hex_or_none(content.sha1),
                hash_to_hex_or_none(content.sha1_git),
                hash_to_hex_or_none(content.sha256),
                hash_to_hex_or_none(content.blake2s256),
                content.length,
                content.status,
                data,
            )
        )

    def process_skipped_content(self, skipped_content: SkippedContent):
        skipped_content_writer = self.get_writer_for("skipped_content")
        skipped_content_writer.write(
            (
                hash_to_hex_or_none(skipped_content.sha1),
                hash_to_hex_or_none(skipped_content.sha1_git),
                hash_to_hex_or_none(skipped_content.sha256),
                hash_to_hex_or_none(skipped_content.blake2s256),
                skipped_content.length,
                skipped_content.status,
                skipped_content.reason,
            )
        )
