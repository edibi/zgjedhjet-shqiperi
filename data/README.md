# Të dhënat

Të dhënat janë të ndara sipas burimit. Dosjet `raw/` ruajnë përgjigjet origjinale të burimit. Dosjet `normalized/` kanë CSV të pastruara në UTF-8.

| Dosja | Përmbajtja | Burimi |
| --- | --- | --- |
| [`kuvend-2025/`](kuvend-2025/) | Rezultatet e Kuvendit 2025, nga niveli kombëtar deri te qendra e votimit, deputetët dhe preferencat | KQZ |
| [`vendore-2023/`](vendore-2023/) | Rezultatet vendore 2023 dhe nxjerrja për Tiranën | KQZ |
| [`krahasime/`](krahasime/) | Krahasimi i Tiranës 2023–2025: votat dhe pjesëmarrja | Të përpunuara nga të dhënat e KQZ-së |
| [`popullsia/`](popullsia/) | Vlerësimi i zgjedhësve rezidentë sipas qarkut, 1 janar 2025 | Të përpunuara nga të dhënat e INSTAT-it |
| [`gjeografi/`](gjeografi/) | Kufijtë dhe qendrat e njësive të Tiranës, adresat e qendrave të votimit | Shih më poshtë |

## Gjeografia

| Skedari | Përmbajtja | Burimi |
| --- | --- | --- |
| `tirana_njesite_administrative.topojson` | Kufijtë e 24 njësive administrative të Bashkisë Tiranë | OpenStreetMap |
| `adresat_njesia_administrative.csv` | Qendrat e njësive, të llogaritura nga kufijtë | OpenStreetMap |
| `qv_adresat.csv` | Adresat e qendrave të votimit | Burimi duhet konfirmuar |

## Shënime

- Dokumentimi i plotë i rezultateve të 2025 është te [`kuvend-2025/README.md`](kuvend-2025/README.md).
- Burimet dhe hash-et SHA-256 janë te `kuvend-2025/manifest.json` dhe `vendore-2023/raw/manifest.json`.
- Zgjedhësit rezidentë janë vlerësim: struktura moshore kombëtare zbatohet njësoj në çdo qark. Metoda është te `popullsia/popullsia_2025_qarqe.json`.
- Krahasimi 2023–2025 lidh dy zgjedhje të ndryshme: këshillin bashkiak 2023 dhe Kuvendin 2025.
