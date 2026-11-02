---

## Executive Business Intelligence Module (`bi_powerbi_tableau/`)

This repository includes a real-time operational risk & AML/PLD Business Intelligence module for **Power BI** and **Tableau Desktop**:

* **`bi_powerbi_tableau/datasets_estrella/Fact_Alertas_Fraude_PLD.csv`**: Star-schema dataset tracking evaluated transactions, triggered alerts, True Positives, False Positives, gross prevented fraud (USD), false-positive friction cost (USD), and response SLA across rule families (velocity, impossible travel, $4\sigma$ amount anomalies, and AML structuring).
* **`bi_powerbi_tableau/powerbi/Medidas_DAX_Fraude_PLD.dax`**: DAX measures for Gross Prevented Fraud, False-Positive Friction Cost, Net Mitigation Benefit, Alert Precision %, and False-Positive-to-True-Positive ratios.
* **`bi_powerbi_tableau/powerbi/Tema_Ejecutivo_Fraude_PLD.json`**: Operational risk & AML color theme for Power BI Desktop.
* **`bi_powerbi_tableau/tableau/Tablero_Monitoreo_Fraude_PLD.twb`**: Native Tableau Desktop workbook comparing rule precision vs. customer friction and net fraud savings by typology.
