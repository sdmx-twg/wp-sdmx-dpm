# FMR: Codelist maintainable ids are upper-cased on load, but references to them are not — breaking reference resolution for lower-case ids

## Summary

When a structure submission contains a `Codelist` whose `id` has lower-case
letters (e.g. `qEC`), FMR **stores the codelist with an upper-cased id** (`QEC`).
References to that codelist — a `Concept` `CoreRepresentation`, a DSD `Dimension`
`Enumeration`, a `Hierarchy` `HierarchicalCode` — are **left exactly as
submitted** (still `qEC`). The submission appears to succeed (the lower-case
id matches the stored one case-insensitively), but a later **strict reference
resolution fails**, e.g.:

```
Could not resolve reference from structure Concept 'EBA:CS_EBA(1.0).ei366'
to structure Codelist 'urn:sdmx:org.sdmx.infomodel.codelist.Codelist=EBA:qEC(1.0)'
```

Lower-case ids are valid per the SDMX `IDType` lexical space
(`[A-Za-z0-9_@$\-]+`), so FMR should preserve them — or, if it normalises the
maintainable id, it must normalise the references identically so the graph stays
internally consistent.

## Environment

- **Product:** Fusion Metadata Registry 12.1.0 (`/ws/fusion/info/product` reports
  `"Version":"12.1.0"`, ReleaseDate `2026-06-18`)
- **Image:** `sdmxio/fmr-mysql:latest` (all-in-one, bundled MySQL), run with
  `docker run -d --name fmr -p 8080:8080 sdmxio/fmr-mysql:latest`
- **Submission endpoint:** `POST /ws/secure/sdmxapi/rest` (`Action: Replace`,
  `Content-Type: application/xml`, HTTP Basic auth)
- **Payload:** SDMX-ML 3.0 structure message

## Steps to reproduce

### A. Minimal — the upper-casing itself

1. Start a fresh container; ensure the `EBA` agency exists.
2. Submit a single codelist with a mixed/lower-case id:

   ```xml
   <str:Codelists>
     <str:Codelist id="zTestCamelCl" version="1.0" agencyID="EBA" isExternalReference="false">
       <com:Name xml:lang="en">case test</com:Name>
       <str:Code id="x1"><com:Name xml:lang="en">x1</com:Name></str:Code>
     </str:Codelist>
   </str:Codelists>
   ```
3. Read it back:
   `GET /ws/public/sdmxapi/rest/codelist/EBA/zTestCamelCl/1.0`

   **Result:** the codelist is returned with
   `urn="…Codelist=EBA:ZTESTCAMELCL(1.0)"` — the entire id has been
   upper-cased. The `Code` id `x1` inside is preserved (only the maintainable
   id is changed).

### B. The breakage — reference to a lower-case codelist

1. Fresh container; agency `EBA` present.
2. Submit, in dependency order:
   - a `Codelist` `EBA:qEC(1.0)`;
   - a `ConceptScheme` `EBA:CS_EBA(1.0)` containing a `Concept` (`ei366`) whose
     `CoreRepresentation`/`Enumeration` references
     `urn:sdmx:org.sdmx.infomodel.codelist.Codelist=EBA:qEC(1.0)`;
   - a `DataStructure` `EBA:DSD_C_27_00(1.0)` whose dimension's `ConceptIdentity`
     points at that concept scheme.
3. Query the constrained codelist for a dimension:
   `GET /ws/registry/json/getConstrainedCodelist?urn=urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=EBA:DSD_C_27_00(1.0)&id=qBEA`

   **Result:** HTTP 404 with
   `Could not resolve reference from structure Concept 'EBA:CS_EBA(1.0).ei366'
   to structure Codelist 'urn:sdmx:org.sdmx.infomodel.codelist.Codelist=EBA:qEC(1.0)'`.

   The codelist is present — but stored as `QEC`, while the concept's reference
   is still `qEC`, so strict resolution fails.

## Expected

Either:
- **(preferred)** FMR preserves the submitted Codelist id case (`qEC` stays
  `qEC`), so references resolve; **or**
- if FMR deliberately normalises Codelist ids to upper case, it applies the
  **same** normalisation to every reference to a Codelist (Concept
  `CoreRepresentation`, DSD `Enumeration`, Hierarchy code URNs) so the stored
  graph remains internally consistent and reference resolution succeeds.

## Actual

- The Codelist **maintainable id** is upper-cased on load.
- **References to it are not** upper-cased.
- **Code ids inside the codelist** are preserved (not changed).
- **Other maintainable ids** (`ConceptScheme`, `DataStructure`, `Dimension`,
  `Hierarchy`) are preserved (not changed).
- Load-time validation passes (case-insensitive match, MySQL collation), but
  query-time strict resolution (`getConstrainedCodelist`, and any traversal that
  resolves the Concept's representation) fails.

## Impact

Any producer that uses lower-case (or mixed-case) Codelist ids — which are valid
SDMX — generates structures that load without error but are silently broken:
`getConstrainedCodelist`, schema generation, and other reference-resolving
operations fail. The failure surfaces far from the cause (at query time, naming
a *Concept → Codelist* reference), making it hard to diagnose. The asymmetry
(maintainable id changed, references not) is the core defect.

## Workaround (consumer side)

Emit Codelist ids in upper case, and route **every** reference to a codelist
through the same upper-casing, so the artefact and all references match what FMR
persists. Preserve the original id (e.g. in an annotation) for round-tripping.
This is purely a workaround for the behaviour above; lower-case ids should not
require it.

## Suggested fix

Make Codelist id handling on load **consistent**: do not normalise the
maintainable id at all (preferred — lower-case is valid SDMX), or, if
normalisation is intended, apply it uniformly to the maintainable id, to every
reference targeting it, and (consistently) to the contained Code ids — so the
stored structure graph resolves regardless of the case used at submission.
