# FMR: non-deterministic reference resolution when a Codelist and a referencing DSD are submitted in the same structure message

## Summary

When a single SDMX-ML structure submission contains both a `Codelist` **and** a
`DataStructure` whose `Dimension` enumerates that codelist, the submission
**intermittently** fails with:

```
ErrorMessage code="100"
Could not resolve reference from structure Dimension 'EBA:DSD_C_29_00(1.0).qJLJ'
to structure Codelist 'urn:sdmx:org.sdmx.infomodel.codelist.Codelist=EBA:qOR(1.0)'
```
(HTTP 404)

The codelist **is** present in the same message and is a valid target. The
*identical* request sometimes succeeds and sometimes fails, which points to a
race between the persistence/indexing of the just-submitted codelist and the
referential-integrity validation of the DSD that runs in the same transaction.

## Environment

- **Product:** Fusion Metadata Registry 12.1.0 (`/ws/fusion/info/product` reports
  `"Version":"12.1.0"`, ReleaseDate `2026-06-18`)
- **Image:** `sdmxio/fmr-mysql:latest` (all-in-one, bundled MySQL), run with
  `docker run -d --name fmr -p 8080:8080 sdmxio/fmr-mysql:latest`
- **Endpoint:** `POST /ws/secure/sdmxapi/rest`
- **Headers:** `Action: Replace`, `Content-Type: application/xml`, HTTP Basic auth (`root`)
- **Payload:** SDMX-ML 3.0 structure message

## Steps to reproduce

1. Start a fresh container (so the registry store is empty apart from defaults).
2. Ensure the owning agency exists (submit `SDMX:AGENCIES(1.0)` containing the
   `EBA` agency with `Action: Replace`).
3. Submit a **single** structure message that contains, in one `<mes:Structures>`:
   - a `Codelist` `EBA:qOR(1.0)` (any number of codes — reproduced with 3 and with 208), and
   - a `ConceptScheme` providing the dimension's `ConceptIdentity`, and
   - a `DataStructure` whose `Dimension` has
     `<str:Enumeration>urn:sdmx:org.sdmx.infomodel.codelist.Codelist=EBA:qOR(1.0)</str:Enumeration>`.
4. Repeat the **exact same** POST several times (it is idempotent under `Action: Replace`).

A minimal payload (namespaces abbreviated) is:

```xml
<mes:Structure xmlns:mes=".../v3_0/message" xmlns:str=".../v3_0/structure" xmlns:com=".../v3_0/common">
  <mes:Header>...</mes:Header>
  <mes:Structures>
    <str:Codelists>
      <str:Codelist id="qOR" version="1.0" agencyID="EBA" isExternalReference="false">
        <com:Name xml:lang="en">Capital regulatory items</com:Name>
        <str:Code id="qx2000"><com:Name xml:lang="en">A</com:Name></str:Code>
      </str:Codelist>
    </str:Codelists>
    <str:ConceptSchemes>
      <str:ConceptScheme id="CSQ" version="1.0" agencyID="EBA" isExternalReference="false">
        <com:Name xml:lang="en">CSQ</com:Name>
        <str:Concept id="D1"><com:Name xml:lang="en">D1</com:Name></str:Concept>
        <str:Concept id="OBS"><com:Name xml:lang="en">OBS</com:Name></str:Concept>
      </str:ConceptScheme>
    </str:ConceptSchemes>
    <str:DataStructures>
      <str:DataStructure id="DSDQ" version="1.0" agencyID="EBA" isExternalReference="false">
        <com:Name xml:lang="en">DSDQ</com:Name>
        <str:DataStructureComponents>
          <str:DimensionList id="DimensionDescriptor">
            <str:Dimension id="D1" position="1">
              <str:ConceptIdentity>urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept=EBA:CSQ(1.0).D1</str:ConceptIdentity>
              <str:LocalRepresentation>
                <str:Enumeration>urn:sdmx:org.sdmx.infomodel.codelist.Codelist=EBA:qOR(1.0)</str:Enumeration>
              </str:LocalRepresentation>
            </str:Dimension>
          </str:DimensionList>
          <str:MeasureList id="MeasureDescriptor">
            <str:Measure id="OBS">
              <str:ConceptIdentity>urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept=EBA:CSQ(1.0).OBS</str:ConceptIdentity>
            </str:Measure>
          </str:MeasureList>
        </str:DataStructureComponents>
      </str:DataStructure>
    </str:DataStructures>
  </mes:Structures>
</mes:Structure>
```

## Expected

The DSD's enumeration reference resolves against the `Codelist` present in the
same submission; the message loads atomically and succeeds every time.

## Actual

The submission **intermittently** fails with code 100 ("Could not resolve
reference … Codelist"). The same payload posted repeatedly alternates between
`status="Success"` and the resolution error with no change to the request.
Observed concretely while loading a real EBA COREP_LE structure set (4 DSDs, 18
codelists, 1 concept scheme, 4 dataflows): the full message failed on the first
attempt, then succeeded on a later identical attempt; reduced reproducers
(single codelist + single DSD) showed the same flip-flop across runs.

Notes that helped isolate it:
- Submitting the **codelists alone** always succeeds.
- Submitting the codelists first, then the DSDs in a **separate** POST, always succeeds.
- Codelist size is not the trigger (reproduced with a 3-code codelist).
- Code-level annotations and `isFinal`/`isPartial` flags are not the trigger.
- It is not specific to a particular id (reproduced with several ids; the same id flips between runs).

## Impact

Producers that emit a complete, self-contained structure message (vocabulary +
DSDs together) cannot rely on a single submission succeeding. Automated
pipelines see spurious failures and must implement a workaround.

## Workaround

Split the submission into separate transactions, one per dependency tier, and
load (or GUI-import) them in this order:

1. **Codelists:** OrganisationSchemes/Agencies, Codelists.
2. **Hierarchies:** Hierarchies. *(Each `HierarchicalCode` references a `Code` in
   a Codelist, so a Hierarchy cannot share a submission with the Codelist it
   points at — it must load after tier 1.)*
3. **Concepts:** ConceptSchemes. *(A Concept's enumerated core representation
   references a Codelist, so the ConceptScheme cannot share a submission with the
   Codelists it points at — it must load after tier 1.)*
4. **Structures:** DataStructures, Dataflows, CategorySchemes.
5. **Constraints:** DataConstraints. *(A DataConstraint attaches to a Dataflow
   (tier 4) and lists Codelist Codes as its allowed values (tier 1), so it cannot
   share a submission with the Dataflow it constrains — it must load last.)*

With each tier's referenced artefacts persisted by the previous transaction, the
next one resolves deterministically. Because each file is a self-contained
message, this also works when importing through the FMR GUI one file at a time
(the GUI submits via the same structure API). The converter emits these as
`<base>.1_codelists.xml`, `<base>.2_hierarchies.xml`, `<base>.3_concepts.xml`,
`<base>.4_structures.xml`, `<base>.5_constraints.xml`
(`serializer.partition_stages()`); empty tiers are skipped, so a numeric gap in
the filenames is normal (`<base>` is the module code, or the agency for a
whole-glossary export).

> **Note (2026-06-20):** an earlier version of the workaround grouped Codelists
> *and* ConceptSchemes into a single "vocabulary" file. That was only safe while
> Concepts carried no representation; once the converter began emitting the
> enumerated core representation on Concepts, the ConceptScheme→Codelist
> reference hit this same race, so the vocabulary tier was split into separate
> `codelists` and `concepts` files.

## Suggested fix

Within a single submission, resolve referential integrity against the union of
(existing store ∪ artefacts in the current message), and/or ensure all
maintainables in the message are persisted/indexed before the cross-reference
validation pass runs — so that a self-contained message validates atomically and
deterministically regardless of intra-message ordering or timing.
