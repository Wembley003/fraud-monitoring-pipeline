"""
Explainable Transactional Fraud & AML/PLD (Prevención de Lavado de Dinero) Monitoring Pipeline.
Combines SQL window functions (velocity, high amount, geographic jump) and PLD structuring (smurfing) rules.
Author: Wembley Emmanuel Ibarra Tepato
"""
import sqlite3
import numpy as np
import pandas as pd
from typing import Dict


class FraudAndPLDPipeline:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")

    def load_sample_transactions(self) -> pd.DataFrame:
        data = [
            # Normal customer transactions
            (1, "ACC_101", "2026-10-15 10:00:00", 450.0, "CDMX", 19.4326, -99.1332, "POS", 0),
            (2, "ACC_101", "2026-10-15 14:30:00", 620.0, "CDMX", 19.4326, -99.1332, "POS", 0),
            # Velocity attack (3+ tx within 15 minutes)
            (3, "ACC_202", "2026-10-15 11:00:00", 1200.0, "CDMX", 19.4326, -99.1332, "ECOM", 1),
            (4, "ACC_202", "2026-10-15 11:04:00", 1850.0, "CDMX", 19.4326, -99.1332, "ECOM", 1),
            (5, "ACC_202", "2026-10-15 11:09:00", 2400.0, "CDMX", 19.4326, -99.1332, "ECOM", 1),
            # Impossible geographic jump (CDMX to Monterrey in 10 minutes) + high amount
            (6, "ACC_303", "2026-10-15 12:00:00", 500.0, "CDMX", 19.4326, -99.1332, "POS", 0),
            (7, "ACC_303", "2026-10-15 12:10:00", 48000.0, "MTY", 25.6866, -100.3161, "POS", 1),
            # PLD / AML Structuring (Smurfing: multiple cash deposits just below $10,000 USD / $150,000 MXN threshold)
            (8, "ACC_404", "2026-10-15 09:15:00", 138000.0, "GDL", 20.6597, -103.3496, "CASH_DEP", 1),
            (9, "ACC_404", "2026-10-15 11:20:00", 142000.0, "GDL", 20.6597, -103.3496, "CASH_DEP", 1),
            (10, "ACC_404", "2026-10-15 15:40:00", 139000.0, "GDL", 20.6597, -103.3496, "CASH_DEP", 1),
        ]
        cols = ["tx_id", "account_id", "tx_timestamp", "amount_mxn", "city", "lat", "lon", "channel", "is_illicit"]
        df = pd.DataFrame(data, columns=cols)
        df.to_sql("transactions", self.conn, index=False, if_exists="replace")
        return df

    def run_explainable_rules_sql(self) -> pd.DataFrame:
        query = """
        WITH enriched_tx AS (
            SELECT
                t1.*,
                LAG(t1.city) OVER (PARTITION BY t1.account_id ORDER BY t1.tx_timestamp) AS prev_city,
                (
                    JULIANDAY(t1.tx_timestamp) -
                    JULIANDAY(LAG(t1.tx_timestamp) OVER (PARTITION BY t1.account_id ORDER BY t1.tx_timestamp))
                ) * 24.0 * 60.0 AS minutes_since_prev_tx,
                (
                    SELECT COUNT(*)
                    FROM transactions t2
                    WHERE t2.account_id = t1.account_id
                      AND t2.tx_timestamp <= t1.tx_timestamp
                      AND (JULIANDAY(t1.tx_timestamp) - JULIANDAY(t2.tx_timestamp)) * 24.0 * 60.0 <= 15.0
                ) AS tx_count_15m,
                SUM(CASE WHEN t1.channel = 'CASH_DEP' THEN t1.amount_mxn ELSE 0 END)
                    OVER (PARTITION BY t1.account_id, SUBSTR(t1.tx_timestamp, 1, 10)) AS daily_cash_total_mxn
            FROM transactions t1
        )
        SELECT
            tx_id,
            account_id,
            tx_timestamp,
            amount_mxn,
            channel,
            is_illicit,
            CASE WHEN amount_mxn >= 35000.0 THEN 1 ELSE 0 END AS rule_high_amount,
            CASE WHEN tx_count_15m >= 3 THEN 1 ELSE 0 END AS rule_velocity_15m,
            CASE WHEN prev_city IS NOT NULL AND prev_city != city AND minutes_since_prev_tx <= 60.0 THEN 1 ELSE 0 END AS rule_geo_jump,
            CASE WHEN channel = 'CASH_DEP' AND amount_mxn BETWEEN 120000.0 AND 149999.0 AND daily_cash_total_mxn >= 300000.0 THEN 1 ELSE 0 END AS rule_pld_smurfing
        FROM enriched_tx
        ORDER BY tx_id;
        """
        df = pd.read_sql_query(query, self.conn)
        reasons = []
        for _, r in df.iterrows():
            triggered = []
            if r["rule_high_amount"]:
                triggered.append("HIGH_AMOUNT")
            if r["rule_velocity_15m"]:
                triggered.append("VELOCITY_3TX_15M")
            if r["rule_geo_jump"]:
                triggered.append("IMPOSSIBLE_GEO_JUMP")
            if r["rule_pld_smurfing"]:
                triggered.append("PLD_CASH_STRUCTURING_SMURFING")
            reasons.append("|".join(triggered) if triggered else "CLEAN")
        df["alert_explanation"] = reasons
        df["alert_triggered"] = (df["alert_explanation"] != "CLEAN").astype(int)
        return df

    @staticmethod
    def evaluate_alert_precision_and_cost(df: pd.DataFrame, false_positive_friction_cost: float = 180.0) -> Dict[str, float]:
        tp = df[(df["alert_triggered"] == 1) & (df["is_illicit"] == 1)]
        fp = df[(df["alert_triggered"] == 1) & (df["is_illicit"] == 0)]
        fn = df[(df["alert_triggered"] == 0) & (df["is_illicit"] == 1)]

        precision = len(tp) / max(len(tp) + len(fp), 1)
        recall = len(tp) / max(len(tp) + len(fn), 1)
        fraud_prevented_mxn = float(tp["amount_mxn"].sum())
        friction_cost_mxn = float(len(fp) * false_positive_friction_cost)

        return {
            "alerts_generated": int(df["alert_triggered"].sum()),
            "precision_pct": round(precision * 100.0, 2),
            "recall_pct": round(recall * 100.0, 2),
            "fraud_and_pld_flagged_mxn": round(fraud_prevented_mxn, 2),
            "false_positive_friction_cost_mxn": round(friction_cost_mxn, 2),
            "net_economic_savings_mxn": round(fraud_prevented_mxn - friction_cost_mxn, 2),
        }


if __name__ == "__main__":
    pipeline = FraudAndPLDPipeline()
    pipeline.load_sample_transactions()
    alerts = pipeline.run_explainable_rules_sql()
    print(alerts[["tx_id", "account_id", "amount_mxn", "alert_explanation", "is_illicit"]].to_string(index=False))
    print(pipeline.evaluate_alert_precision_and_cost(alerts))
