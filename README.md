# Explainable Fraud & AML/PLD Monitoring Pipeline (SQL & Python)

**Author:** Wembley Emmanuel Ibarra Tepato ([github.com/Wembley003](https://github.com/Wembley003))  
**Focus:** Digital Payments Fraud Detection, ABM PLD/FT (Anti-Money Laundering Structuring), and Economic Cost-Matrix Calibration.

## Overview
Auditable rule engine written in **SQL (`sqlite3`)** and **Python (`pandas`)** where every alert records the exact rules that triggered it for Operations and Compliance (PLD/FT) auditability:
- **Velocity Rule**: $\ge 3$ transactions within a rolling 15-minute window via correlated subqueries and window partitioning.
- **Geographic Impossibility**: Detects consecutive transactions across distinct cities within $\le 60$ minutes using `LAG() OVER`.
- **PLD/AML Cash Structuring (*Smurfing*)**: Flags fractional cash deposits just under reporting thresholds that accumulate $\ge \$300,000	ext{ MXN}$ intra-day.
- **Precision vs. Customer Friction**: Evaluates rule precision, recall, prevented loss, and false-positive customer friction cost.

```bash
pip install -r requirements.txt
python -m src.fraud_pld_pipeline
pytest -v
```

---

## Executive Business Intelligence Module (`bi_powerbi_tableau/`)

This repository includes a real-time operational risk & AML/PLD Business Intelligence module for **Power BI** and **Tableau Desktop**:

* **`bi_powerbi_tableau/datasets_estrella/Fact_Alertas_Fraude_PLD.csv`**: Star-schema dataset tracking evaluated transactions, triggered alerts, True Positives, False Positives, gross prevented fraud (USD), false-positive friction cost (USD), and response SLA across rule families (velocity, impossible travel, $4\sigma$ amount anomalies, and AML structuring).
* **`bi_powerbi_tableau/powerbi/Medidas_DAX_Fraude_PLD.dax`**: DAX measures for Gross Prevented Fraud, False-Positive Friction Cost, Net Mitigation Benefit, Alert Precision %, and False-Positive-to-True-Positive ratios.
* **`bi_powerbi_tableau/powerbi/Tema_Ejecutivo_Fraude_PLD.json`**: Operational risk & AML color theme for Power BI Desktop.
* **`bi_powerbi_tableau/tableau/Tablero_Monitoreo_Fraude_PLD.twb`**: Native Tableau Desktop workbook comparing rule precision vs. customer friction and net fraud savings by typology.
