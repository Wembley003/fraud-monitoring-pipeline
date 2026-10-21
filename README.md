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
