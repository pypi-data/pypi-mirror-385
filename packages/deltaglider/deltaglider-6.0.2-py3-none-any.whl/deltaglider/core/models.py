"""Core domain models."""

import logging
from dataclasses import dataclass
from datetime import datetime

# Metadata key prefix for DeltaGlider
# AWS S3 automatically adds 'x-amz-meta-' prefix, so our keys become 'x-amz-meta-dg-*'
METADATA_PREFIX = "dg-"


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeltaSpace:
    """S3 delta compression space - a prefix containing related files for delta compression."""

    bucket: str
    prefix: str

    def reference_key(self) -> str:
        """Get reference file key."""
        return f"{self.prefix}/reference.bin" if self.prefix else "reference.bin"


@dataclass(frozen=True)
class ObjectKey:
    """S3 object key."""

    bucket: str
    key: str


@dataclass(frozen=True)
class Sha256:
    """SHA256 hash."""

    hex: str

    def __post_init__(self) -> None:
        """Validate hash format."""
        if len(self.hex) != 64 or not all(c in "0123456789abcdef" for c in self.hex.lower()):
            raise ValueError(f"Invalid SHA256: {self.hex}")


@dataclass
class ReferenceMeta:
    """Reference file metadata."""

    tool: str
    source_name: str
    file_sha256: str
    created_at: datetime
    note: str = "reference"

    def to_dict(self) -> dict[str, str]:
        """Convert to S3 metadata dict with DeltaGlider namespace prefix."""
        return {
            f"{METADATA_PREFIX}tool": self.tool,
            f"{METADATA_PREFIX}source-name": self.source_name,
            f"{METADATA_PREFIX}file-sha256": self.file_sha256,
            f"{METADATA_PREFIX}created-at": self.created_at.isoformat() + "Z",
            f"{METADATA_PREFIX}note": self.note,
        }


@dataclass
class DeltaMeta:
    """Delta file metadata."""

    tool: str
    original_name: str
    file_sha256: str
    file_size: int
    created_at: datetime
    ref_key: str
    ref_sha256: str
    delta_size: int
    delta_cmd: str
    note: str | None = None

    def to_dict(self) -> dict[str, str]:
        """Convert to S3 metadata dict with DeltaGlider namespace prefix."""
        meta = {
            f"{METADATA_PREFIX}tool": self.tool,
            f"{METADATA_PREFIX}original-name": self.original_name,
            f"{METADATA_PREFIX}file-sha256": self.file_sha256,
            f"{METADATA_PREFIX}file-size": str(self.file_size),
            f"{METADATA_PREFIX}created-at": self.created_at.isoformat() + "Z",
            f"{METADATA_PREFIX}ref-key": self.ref_key,
            f"{METADATA_PREFIX}ref-sha256": self.ref_sha256,
            f"{METADATA_PREFIX}delta-size": str(self.delta_size),
            f"{METADATA_PREFIX}delta-cmd": self.delta_cmd,
        }
        if self.note:
            meta[f"{METADATA_PREFIX}note"] = self.note
        return meta

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "DeltaMeta":
        """Create from S3 metadata dict with DeltaGlider namespace prefix."""

        def _get_value(*keys: str, required: bool = True) -> str:
            for key in keys:
                if key in data and data[key] != "":
                    return data[key]
            if required:
                raise KeyError(keys[0])
            return ""

        tool = _get_value(f"{METADATA_PREFIX}tool", "dg_tool", "tool")
        original_name = _get_value(
            f"{METADATA_PREFIX}original-name", "dg_original_name", "original_name", "original-name"
        )
        file_sha = _get_value(
            f"{METADATA_PREFIX}file-sha256", "dg_file_sha256", "file_sha256", "file-sha256"
        )
        file_size_raw = _get_value(
            f"{METADATA_PREFIX}file-size", "dg_file_size", "file_size", "file-size"
        )
        created_at_raw = _get_value(
            f"{METADATA_PREFIX}created-at", "dg_created_at", "created_at", "created-at"
        )
        ref_key = _get_value(f"{METADATA_PREFIX}ref-key", "dg_ref_key", "ref_key", "ref-key")
        ref_sha = _get_value(
            f"{METADATA_PREFIX}ref-sha256", "dg_ref_sha256", "ref_sha256", "ref-sha256"
        )
        delta_size_raw = _get_value(
            f"{METADATA_PREFIX}delta-size", "dg_delta_size", "delta_size", "delta-size"
        )
        delta_cmd_value = _get_value(
            f"{METADATA_PREFIX}delta-cmd", "dg_delta_cmd", "delta_cmd", "delta-cmd", required=False
        )
        note_value = _get_value(f"{METADATA_PREFIX}note", "dg_note", "note", required=False)

        try:
            file_size = int(file_size_raw)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid file size metadata: {file_size_raw}") from None

        try:
            delta_size = int(delta_size_raw)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid delta size metadata: {delta_size_raw}") from None

        created_at_text = created_at_raw.rstrip("Z")
        try:
            created_at = datetime.fromisoformat(created_at_text)
        except ValueError as exc:
            raise ValueError(f"Invalid created_at metadata: {created_at_raw}") from exc

        if not delta_cmd_value:
            object_name = original_name or "<unknown>"
            logger.warning(
                "Delta metadata missing %s for %s; using empty command",
                f"{METADATA_PREFIX}delta-cmd",
                object_name,
            )
            delta_cmd_value = ""

        return cls(
            tool=tool,
            original_name=original_name,
            file_sha256=file_sha,
            file_size=file_size,
            created_at=created_at,
            ref_key=ref_key,
            ref_sha256=ref_sha,
            delta_size=delta_size,
            delta_cmd=delta_cmd_value,
            note=note_value or None,
        )


@dataclass
class PutSummary:
    """Summary of PUT operation."""

    operation: str  # "create_reference" or "create_delta"
    bucket: str
    key: str
    original_name: str
    file_size: int
    file_sha256: str
    delta_size: int | None = None
    delta_ratio: float | None = None
    ref_key: str | None = None
    ref_sha256: str | None = None
    cache_hit: bool = False


@dataclass
class VerifyResult:
    """Result of verification."""

    valid: bool
    expected_sha256: str
    actual_sha256: str
    message: str
