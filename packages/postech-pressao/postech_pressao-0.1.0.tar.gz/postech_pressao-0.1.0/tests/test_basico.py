from postech_pressao import train_default_model, predict_labels

def test_predicao_basica():
    m = train_default_model()
    out = predict_labels(m, [(120,80), (140,90), (100,70)])
    assert len(out) == 3
    assert set(out) <= {"BAIXA","NORMAL","ALTA"}
