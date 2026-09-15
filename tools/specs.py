"""Validate QuestShift spec files exist and keep the v1 freeze language."""

from __future__ import annotations

import re
from pathlib import Path

REQUIRED_SPECS = (
    "docs/PRD.md",
    "docs/ARCHITECTURE.md",
    "docs/ARCHITECTURE-ESSENTIALS.md",
    "docs/UX.md",
    "docs/GAME-DESIGN.md",
    "docs/API-CONTRACT.md",
    "docs/PLAN.md",
    "docs/WORKFLOWS.md",
    "docs/CAMPAIGN-AUTHORING.md",
    "docs/INSTALL.md",
    "docs/QUALITY.md",
    "docs/decisions.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
)

SECRET_PATTERNS = (
    re.compile(r"BEGIN PRIVATE KEY"),
    re.compile(r"BEGIN OPENSSH PRIVATE KEY"),
    re.compile(r"BEGIN CERTIFICATE"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+\."),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"hf_[A-Za-z0-9]{16,}"),
    re.compile(r"openshift-v4/"),
    re.compile(r"opentlc\.com"),
)

FREEZE_NEEDLES = (
    "vLLM",
    "ibm-granite/granite-3.2-8b-instruct",
    "No Ollama",
    "nvidia.com/gpu",
)


def iter_markdown(root: Path) -> list[Path]:
    files = [root / name for name in REQUIRED_SPECS]
    files.extend(sorted((root / "docs").glob("*.md")))
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in files:
        if path in seen:
            continue
        seen.add(path)
        unique.append(path)
    return unique


def validate_required_files(root: Path) -> None:
    missing = [name for name in REQUIRED_SPECS if not (root / name).is_file()]
    if missing:
        raise ValueError(f"missing required specs: {missing}")


def validate_no_secrets(root: Path) -> None:
    for path in iter_markdown(root):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                raise ValueError(
                    f"{path.relative_to(root)}: looks like a secret ({pattern.pattern})"
                )


def validate_freeze(root: Path) -> None:
    essentials = (root / "docs/ARCHITECTURE-ESSENTIALS.md").read_text(encoding="utf-8")
    missing = [needle for needle in FREEZE_NEEDLES if needle not in essentials]
    if missing:
        raise ValueError(f"ARCHITECTURE-ESSENTIALS.md missing freeze text: {missing}")


def validate_specs(root: Path) -> None:
    validate_required_files(root)
    validate_no_secrets(root)
    validate_freeze(root)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    validate_specs(root)
    print("docs specs ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
