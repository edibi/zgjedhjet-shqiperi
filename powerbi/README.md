# Power BI

| Skedari | Përmbajtja |
| --- | --- |
| `Zgjedhjet-Shqiperi.pbip` | Hape këtë skedar në Power BI Desktop |
| `Zgjedhjet-Shqiperi.Report/` | Faqet dhe vizualet e raportit |
| `Zgjedhjet-Shqiperi.SemanticModel/` | Modeli, tabelat dhe matjet |

## Nëse projekti është në një dosje tjetër

Power BI nuk pranon shtigje relative, ndaj vendndodhja e të dhënave ruhet te parametri `DataFolder`. Vlera e parazgjedhur është `C:\zgjedhjet-shqiperi\data\`.

1. Hap **Transform data > Edit parameters**.
2. Vendos shtegun e plotë të dosjes `data`, me `\` në fund.
3. Zgjidh **Close & Apply**, pastaj **Refresh**.


Kopja lokale e të dhënave (`cache.abf`) nuk ruhet në GitHub, ndaj pas shkarkimit duhet **Refresh**.
