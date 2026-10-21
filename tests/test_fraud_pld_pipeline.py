from src.fraud_pld_pipeline import FraudAndPLDPipeline


def test_explainable_fraud_and_pld_rules():
    pipeline = FraudAndPLDPipeline()
    pipeline.load_sample_transactions()
    res = pipeline.run_explainable_rules_sql().set_index("tx_id")

    # TX 5 must trigger velocity (3rd tx in 9 mins)
    assert "VELOCITY_3TX_15M" in res.loc[5, "alert_explanation"]
    # TX 7 must trigger both high amount and impossible geographic jump
    assert "IMPOSSIBLE_GEO_JUMP" in res.loc[7, "alert_explanation"]
    assert "HIGH_AMOUNT" in res.loc[7, "alert_explanation"]
    # TX 10 must trigger PLD structuring / smurfing rule
    assert "PLD_CASH_STRUCTURING_SMURFING" in res.loc[10, "alert_explanation"]
    # Normal TX 1 & 2 must remain CLEAN
    assert res.loc[1, "alert_explanation"] == "CLEAN"
