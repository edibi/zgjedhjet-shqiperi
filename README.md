# Zgjedhjet në Shqipëri

Të dhëna të hapura dhe një raport Power BI për zgjedhjet parlamentare të Shqipërisë 2025, me krahasim për Tiranën me zgjedhjet vendore 2023.

*Open data and a Power BI report on Albania's 2025 parliamentary election, with a Tirana comparison against the 2023 local election. The report is in Albanian.*

## Çfarë ka këtu

| Dosja | Përmbajtja |
| --- | --- |
| [`powerbi/`](powerbi/) | Raporti Power BI, modeli, skripti i hartës dhe prezantimi |
| [`data/`](data/) | Të dhënat burimore dhe të pastruara, të ndara sipas burimit |

Raporti përfshin:

- Përmbledhjen kombëtare
- Analizën territoriale
- Analizën gjinore
- Hartën zgjedhore të Tiranës
- Krahasimin 2023–2025
- Skenarin 2027

## Si ta hapësh

1. Instalo [Power BI Desktop](https://www.microsoft.com/power-bi/desktop).
2. Vendose projektin te `C:\zgjedhjet-shqiperi`, ose ndrysho parametrin `DataFolder`, siç shpjegohet te [`powerbi/README.md`](powerbi/README.md).
3. Hap `powerbi/Zgjedhjet-Shqiperi.pbip` dhe zgjidh **Refresh**.

## Skenari 2027

Faqja **Skenari 2027** dhe prezantimi te [`powerbi/prezantimi/`](powerbi/prezantimi/) janë analizë hipotetike mbi votat e 2025, jo parashikim dhe jo rezultate zyrtare.

- **Kualicioni Sheshit** është një emër pune për NISMA-SHB + MUNDESIA + BASHKE. Nuk është koalicion zyrtar.
- PS dhe PSD trajtohen si një koalicion.
- X dhe Y janë përqindje të supozuara të votave që kalojnë nga PS + PSD dhe PD-ASHM.

## Burimet

| Burimi | Të dhënat | Lidhja |
| --- | --- | --- |
| Komisioni Qendror i Zgjedhjeve (KQZ) | Rezultatet e Kuvendit 2025 | [iemis.kqz.gov.al](https://iemis.kqz.gov.al/results2025-finale/?lang=AL&v1=ALL) |
| Komisioni Qendror i Zgjedhjeve (KQZ) | Rezultatet vendore 2023 | [iemis.kqz.gov.al](https://iemis.kqz.gov.al/results2023/results2023.htm?lang=AL) |
| INSTAT | Popullsia 2025 dhe Census 2023 | [instat.gov.al](https://www.instat.gov.al/) |
| OpenStreetMap | Kufijtë e njësive administrative të Tiranës | [openstreetmap.org](https://www.openstreetmap.org/copyright) |

Hollësitë e çdo skedari janë te [`data/README.md`](data/README.md).

## Licenca

- Kodi: [MIT](LICENSE)
- Raporti dhe të dhënat e përpunuara: [CC BY 4.0](LICENSE-DATA.md)
- Të dhënat e palëve të treta mbeten nën kushtet e burimit të tyre. Shih [`LICENSE-DATA.md`](LICENSE-DATA.md).

Ky projekt është i pavarur dhe nuk lidhet me KQZ-në, INSTAT-in apo ndonjë subjekt politik.
