"""Conventions and review-flag collection.

Every non-deterministic mapping choice lives here so it is configurable and
auditable (methodology doc, section 1.2). Anything *judgement-based* must emit a
:class:`ReviewFlag` rather than guess silently; the flags are collected into a
:class:`ReviewReport` and surfaced at the end of a conversion run.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ReviewSeverity(str, Enum):
    """How much human attention a flagged decision needs."""

    INFO = "info"          # a convention was applied; recorded for transparency
    REVIEW = "review"      # a defensible default was chosen; should be checked
    BLOCKING = "blocking"  # no safe default exists; output is incomplete


@dataclass
class ReviewFlag:
    """A single judgement-based or convention-driven decision worth recording."""

    code: str                       # stable machine key, e.g. "ismetric.ambiguous"
    message: str                    # human-readable explanation
    artefact: str = ""              # the DPM/SDMX artefact id the flag concerns
    severity: ReviewSeverity = ReviewSeverity.REVIEW
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["severity"] = self.severity.value
        return d


@dataclass
class ReviewReport:
    """Collects :class:`ReviewFlag`s produced during a conversion."""

    flags: List[ReviewFlag] = field(default_factory=list)

    def add(
        self,
        code: str,
        message: str,
        *,
        artefact: str = "",
        severity: ReviewSeverity = ReviewSeverity.REVIEW,
        **context: Any,
    ) -> ReviewFlag:
        flag = ReviewFlag(code, message, artefact, severity, dict(context))
        self.flags.append(flag)
        return flag

    @property
    def has_blocking(self) -> bool:
        return any(f.severity is ReviewSeverity.BLOCKING for f in self.flags)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "count": len(self.flags),
            "has_blocking": self.has_blocking,
            "flags": [f.to_dict() for f in self.flags],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


@dataclass
class Conventions:
    """Configurable, deterministic-once-fixed mapping choices.

    Defaults are conservative (see ``open_questions.md``): same owner throughout,
    one ConceptScheme/Codelist grouping per framework, EBA as the default agency.
    """

    # Owner (DPM) <-> Agency (SDMX) correspondence. DPM owners are short codes
    # ("EBA", "eba"); SDMX agency ids must be valid SDMX ids.
    default_agency: str = "EBA"
    owner_to_agency: Dict[str, str] = field(default_factory=dict)
    agency_to_owner: Dict[str, str] = field(default_factory=dict)

    # Human-readable names for the SDMX agencies the converter emits. FMR
    # requires every referenced Agency to exist, so the converter bundles an
    # AgencyScheme; this supplies the Name (falls back to the agency id).
    agency_names: Dict[str, str] = field(
        default_factory=lambda: {"EBA": "European Banking Authority"}
    )

    # DPM Categories whose codes start with any of these prefixes are internal
    # plumbing and are not emitted as SDMX Codelists (e.g. the "_PR" property
    # category from the reference dpm_to_sdmx repo).
    internal_category_prefixes: tuple = ("_",)

    # IsMetric derivation when importing SDMX Concepts (convention-driven):
    #   numeric core representation -> metric; enumerated -> dimension;
    #   ambiguous -> use this default and emit a ReviewFlag.
    ismetric_default_when_ambiguous: bool = False

    # Default-item selection when importing an SDMX Codelist that lacks a
    # DPM_DEFAULT_ITEM annotation: try these well-known total/wildcard codes in
    # order before synthesising one (and flagging).
    default_item_candidates: tuple = ("_T", "_X", "_Z")

    # ConceptScheme grouping policy for DPM Properties exported to SDMX.
    #   "per_framework": one ConceptScheme per DPM Framework (default convention)
    #   "single":        one standalone ConceptScheme for all Properties
    conceptscheme_grouping: str = "per_framework"

    # SDMX->DPM tables are flat by default (DSD is inherently flat).
    produce_flat_tables: bool = True

    def agency_for(self, owner: Optional[str]) -> str:
        if not owner:
            return self.default_agency
        return self.owner_to_agency.get(owner, owner)

    def agency_name_for(self, agency: str) -> str:
        return self.agency_names.get(agency, agency)

    def owner_for(self, agency: Optional[str]) -> str:
        if not agency:
            return self.default_agency
        return self.agency_to_owner.get(agency, agency)

    def is_internal_category(self, code: Optional[str]) -> bool:
        return bool(code) and code.startswith(tuple(self.internal_category_prefixes))
