# KQZ 2025 parliamentary election results

This directory contains a snapshot of the final 2025 Albanian parliamentary election results published by the Komisioni Qendror i Zgjedhjeve (KQZ). The source dashboard is [KQZ Results 2025](https://iemis.kqz.gov.al/results2025-finale/?lang=AL&v1=ALL).

The `raw/` files preserve KQZ's responses byte-for-byte. Earlier normalized CSV exports were removed from this project because the report reads the raw files directly; `manifest.json` still lists their hashes for provenance.

## Files

### Raw KQZ snapshots

| File | Information | Records |
| --- | --- | ---: |
| [`national_party_results.json`](raw/national_party_results.json) | Nationwide party votes split into domestic, abroad, and combined totals; includes seats | 1 summary + 11 party rows |
| [`regional_party_results.json`](raw/regional_party_results.json) | Party votes and seats for the 12 regions (`qark`) | 12 summaries + 132 party rows |
| [`municipality_party_results.json`](raw/municipality_party_results.json) | Domestic party votes by municipality | 61 summaries + 671 party rows |
| [`admin_unit_party_results.json`](raw/admin_unit_party_results.json) | Domestic party votes by administrative unit | 380 summaries + 4,180 party rows |
| [`polling_station_party_results.json`](raw/polling_station_party_results.json) | Domestic party votes by polling station (`QV`) | 5,225 summaries + 57,475 party rows |
| [`regional_candidate_preferences.json`](raw/regional_candidate_preferences.json) | Candidate preference results aggregated by region | 12 summaries + 2,046 candidate rows |
| [`deputies.json`](raw/deputies.json) | Final list of elected deputies | 140 rows |
| [`recount_winners.json`](raw/recount_winners.json) | Winning candidates after the recount | 140 rows |

The party-result JSON files use `data_main[0]` for geographic/counting summaries and `data_main[1]` for result rows. KQZ uses compact source keys such as `v1`, `v2`, and `v5`; these are intentionally unchanged in `raw/`.

[`manifest.json`](manifest.json) records source URLs, retrieval time, HTTP metadata, encodings, file sizes, SHA-256 hashes, row counts, and validated totals.

## Validation and provenance

Nationwide totals were checked against the summary embedded in KQZ's data:

- 1,406,097 domestic valid votes
- 199,960 valid votes from abroad
- 1,606,057 combined valid votes
- 140 seats

Every raw file has a SHA-256 digest in [`manifest.json`](manifest.json). Party abbreviations are not fully consistent across KQZ feeds, so `ballot_order` is generally a safer join key than `party_code`.

