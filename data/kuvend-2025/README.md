# KQZ 2025 parliamentary election results

This directory contains a snapshot of the final 2025 Albanian parliamentary election results published by the Komisioni Qendror i Zgjedhjeve (KQZ). The source dashboard is [KQZ Results 2025](https://iemis.kqz.gov.al/results2025-finale/?lang=AL&v1=ALL).

The `raw/` files preserve KQZ's responses byte-for-byte. The `normalized/` files are UTF-8 CSV exports with decoded HTML entities, descriptive column names, and numeric vote fields.

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

### Normalized CSV files

| File | Information | Rows |
| --- | --- | ---: |
| [`party_results.csv`](normalized/party_results.csv) | One combined table covering national, region, municipality, administrative-unit, and polling-station party results | 62,469 |
| [`candidate_preferences_by_region.csv`](normalized/candidate_preferences_by_region.csv) | Candidate results, preference-vote totals, list positions, and mandated markers by region | 2,046 |
| [`deputies.csv`](normalized/deputies.csv) | Normalized final deputy list | 140 |
| [`recount_winners.csv`](normalized/recount_winners.csv) | Normalized post-recount winner list | 140 |
| [`manifest.json`](manifest.json) | Source URLs, retrieval time, HTTP metadata, encodings, file sizes, SHA-256 hashes, row counts, and validated totals | — |

## Short schemas

### `party_results.csv`

| Columns | Meaning |
| --- | --- |
| `level` | `national`, `region`, `municipality`, `admin_unit`, or `polling_station` |
| `region`, `municipality`, `admin_unit`, `polling_station` | Geographic identifiers; unused levels are blank |
| `ballot_order` | Subject's numeric order on the ballot |
| `party_code`, `party_name` | KQZ abbreviation and full electoral-subject name |
| `votes_domestic`, `votes_abroad`, `votes_total` | Vote counts; lower domestic-only levels have zero abroad votes |
| `seats` | Allocated seats at national/region level; blank where not applicable |
| `source_updated_at`, `source_dataset` | KQZ update time and originating raw dataset |

### `candidate_preferences_by_region.csv`

| Columns | Meaning |
| --- | --- |
| `region`, `ballot_order` | Region and electoral-subject ballot order |
| `candidate_name`, `subject_code` | Candidate and KQZ subject abbreviation |
| `votes_domestic`, `votes_abroad`, `votes_total` | Candidate preference-vote counts |
| `candidate_list_position` | Candidate's source list position |
| `mandated` | `1` when KQZ marked the candidate as elected; otherwise `0` |
| `source_v8` | Original KQZ list-type/status value, retained because the source does not document it |
| `source_updated_at` | Update timestamp embedded by KQZ |

### `deputies.csv` and `recount_winners.csv`

| Columns | Meaning |
| --- | --- |
| `source_id` | KQZ row identifier |
| `first_name`, `father_name`, `surname` | Name fields supplied by KQZ |
| `region` | Electoral region |
| `electoral_subject`, `subject_code` | Party/coalition name and abbreviation |
| `coalition_party` | Member party when applicable |
| `source_updated_at` | Update timestamp embedded by KQZ |

## Validation and provenance

Nationwide totals were checked against the summary embedded in KQZ's data:

- 1,406,097 domestic valid votes
- 199,960 valid votes from abroad
- 1,606,057 combined valid votes
- 140 seats

Every normalized and raw file has a SHA-256 digest in [`manifest.json`](manifest.json). Party abbreviations are not fully consistent across KQZ feeds, so `ballot_order` is generally a safer join key than `party_code`.

