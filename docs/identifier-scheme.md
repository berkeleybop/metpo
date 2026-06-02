# METPO Identifier and IRI Scheme

**Purpose:** The canonical form of METPO identifiers and ontology IRIs, how they resolve,
and where the values are configured. Follow this when minting terms, building releases,
or editing ODK configuration.

---

## The Short Version

- **Term IRIs** are `https://w3id.org/metpo/<7-digit id>` (prefix `METPO:` →
  `https://w3id.org/metpo/`). Classes are `METPO:1xxxxxx`, properties `METPO:2xxxxxx`.
- **`https://w3id.org/metpo/` is the canonical, resolvable base.** w3id delegates only the
  `/metpo/` path, so *everything* — terms, the ontology document, version IRIs, and
  release products — must live under it.
- **METPO does not use `purl.obolibrary.org` PURLs.** METPO is not registered in the OBO
  Foundry, so `http://purl.obolibrary.org/obo/METPO_<id>` returns HTTP 404. Do not mint,
  advertise, or filter on obolibrary IRIs.

---

## Canonical IRIs

| Thing | IRI |
|---|---|
| Term (class/property) | `https://w3id.org/metpo/<id>` |
| Main ontology document | `https://w3id.org/metpo/metpo.owl` |
| Version IRI | `https://w3id.org/metpo/releases/<date>/metpo.owl` |
| Products (`-base`, `-full`) | `https://w3id.org/metpo/metpo-base.owl`, `https://w3id.org/metpo/metpo-full.owl` |

All of these are under `https://w3id.org/metpo/`. An IRI **above** that path (e.g.
`https://w3id.org/metpo.owl`) is **not resolvable** — it falls outside w3id's `/metpo/`
delegation and 404s — so it must never be used as the ontology IRI.

## Resolution

The `/metpo/` catch-all in [`perma-id/w3id.org`](https://github.com/perma-id/w3id.org)
redirects `https://w3id.org/metpo/*`:

- `https://w3id.org/metpo/metpo.owl` → the raw release OWL on GitHub.
- `https://w3id.org/metpo/<id>` → the BioPortal class page. This works in **browsers**
  (BioPortal sits behind a Cloudflare bot challenge that only blocks non-browser clients;
  human resolution is the design goal). Machine/linked-data dereferenceability would come
  from OLS once METPO is loaded there (see #213).

## Where the values are configured

The IRI base lives in **`src/ontology/metpo-odk.yaml`** (`uribase`) and flows into the
**generated** `src/ontology/Makefile` as `URIBASE` / `ONTBASE` and the report/base-artifact
`--base-iri`. The **target** values that produce the scheme above are:

```
URIBASE  = https://w3id.org/metpo
ONTBASE  = https://w3id.org/metpo
--base-iri = $(URIBASE)        # i.e. https://w3id.org/metpo, which matches term IRIs
```

> Current state: the repo ships `uribase: https://w3id.org` in `metpo-odk.yaml` and a
> generated `URIBASE = https://w3id.org` (with `ONTBASE = https://w3id.org/metpo`), which
> makes the main ontology IRI resolve *above* the delegation as the non-resolving
> `https://w3id.org/metpo.owl`. Aligning the generated values with the target above is
> tracked in #465 (it must be done via `odk.yaml` regeneration, not a Makefile edit).

**Do not hand-edit `src/ontology/Makefile`.** It is ODK-generated ("DO NOT EDIT THIS
FILE"); `make update_repo` regenerates it and would overwrite manual edits. Configure the
scheme in `metpo-odk.yaml` and regenerate. Note that ODK's IRI machinery is OBO-PURL
oriented (it assumes `<base>/ONT_<id>` underscore terms and a registry-root ontology IRI),
which does not map cleanly onto METPO's w3id slash scheme; reconciling this is tracked in
**#465** (the ODK upgrade). Vestiges such as a `$(URIBASE)/METPO_` base-IRI in the report
recipe come from that mismatch and match no real METPO term.

See also: `docs/synonym-conventions.md`, `docs/deprecation-workflow.md`, and the
"Identifiers and resolution" section of the top-level `README.md`.
