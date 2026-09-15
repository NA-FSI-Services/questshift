from __future__ import annotations

from pathlib import Path

import pytest

from tools.specs import (
    main,
    validate_freeze,
    validate_no_secrets,
    validate_required_files,
    validate_specs,
)

ROOT = Path(__file__).resolve().parents[1]


def test_canonical_specs_pass() -> None:
    validate_specs(ROOT)
    assert main() == 0


def test_rejects_missing_spec(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="missing required"):
        validate_required_files(tmp_path)


def test_rejects_secret_token(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "ARCHITECTURE-ESSENTIALS.md").write_text("ok\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("token BEGIN PRIVATE KEY\n", encoding="utf-8")
    with pytest.raises(ValueError, match="secret"):
        validate_no_secrets(tmp_path)


def test_rejects_cluster_jwt_and_lab_hostname(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "ARCHITECTURE-ESSENTIALS.md").write_text("ok\n", encoding="utf-8")
    jwt = "eyJ" + "hbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." + "eyJzdWIiOiIxIn0."
    (tmp_path / "AGENTS.md").write_text(f"oc login --token={jwt}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="secret"):
        validate_no_secrets(tmp_path)
    host = "example." + "opentlc" + ".com"
    (tmp_path / "AGENTS.md").write_text(f"https://console.apps.{host}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="secret"):
        validate_no_secrets(tmp_path)


def test_rejects_missing_freeze(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "ARCHITECTURE-ESSENTIALS.md").write_text("no freeze here\n", encoding="utf-8")
    with pytest.raises(ValueError, match="freeze"):
        validate_freeze(tmp_path)


def test_validate_specs_missing(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="missing required"):
        validate_specs(tmp_path)


def test_skips_missing_markdown(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    validate_no_secrets(tmp_path)
