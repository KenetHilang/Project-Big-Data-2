from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import joblib
import numpy as np

app = FastAPI()

# ========================
# LOAD MODEL DAN ENCODERS
# ========================
model1 = joblib.load("models/is_fraud_model/model.pkl")
model2 = joblib.load("models/fraud_type_model/model.pkl")
model3 = joblib.load("models/payment_channel_model/model.pkl")

indexers1 = joblib.load("models/is_fraud_model/label_indexers.pkl")
indexers2 = joblib.load("models/fraud_type_model/label_indexers.pkl")
indexers3 = joblib.load("models/payment_channel_model/label_indexers.pkl")

fraud_type_labels = joblib.load("models/fraud_type_model/label_indexer.pkl")
payment_channel_labels = joblib.load("models/payment_channel_model/label_indexer.pkl")

# ========================
# INPUT MODEL
# ========================
class BaseTransactionInput(BaseModel):
    amount: float
    time_since_last_transaction: float
    spending_deviation_score: float
    velocity_score: float
    geo_anomaly_score: float
    merchant_category: str

    device_used: Optional[str] = None
    location: Optional[str] = None
    transaction_type: Optional[str] = None
    sender_account: Optional[str] = None
    receiver_account: Optional[str] = None
    payment_channel: Optional[str] = None

class FraudInput(BaseTransactionInput):
    payment_channel: str  # ini wajib karena dipakai di model fraud

class FraudTypeInput(BaseTransactionInput):
    payment_channel: str  # ini juga wajib karena dipakai di model fraud_type

class PaymentChannelInput(BaseTransactionInput):
    pass  # tanpa payment_channel, karena ini targetnya

# ========================
# UTILITAS
# ========================
def index_kategori(label_list, val: str) -> int:
    try:
        return int(label_list.index(val))
    except ValueError:
        raise HTTPException(status_code=400, detail=f"'{val}' tidak termasuk dalam label yang dikenal.")

def prepare_features(data: BaseModel, skip_field: str = None, indexers: dict = {}) -> np.ndarray:
    fields = data.dict()
    numeric = [
        fields["amount"],
        fields["time_since_last_transaction"],
        fields["spending_deviation_score"],
        fields["velocity_score"],
        fields["geo_anomaly_score"]
    ]
    categorical = []
    for col in ["payment_channel", "device_used", "location", "transaction_type", "merchant_category", "sender_account", "receiver_account"]:
        if col == skip_field:
            continue
        label_list = indexers.get(col)
        if label_list is None:
            raise HTTPException(status_code=500, detail=f"Indexer untuk {col} belum dimuat.")

        val = fields.get(col)
        if val is None:
            # Jika val None, pakai index default 0
            idx = 0
        else:
            idx = index_kategori(label_list, val)
        categorical.append(idx)

    return np.array([numeric + categorical])

# ========================
# ENDPOINTS
# ========================

@app.post("/predict-fraud")
def predict_fraud(data: FraudInput):
    features = prepare_features(data, skip_field=None, indexers=indexers1)
    pred = model1.predict(features)
    return {"is_fraud": bool(pred[0])}

@app.post("/predict-fraud-type")
def predict_fraud_type(data: FraudTypeInput):
    features = prepare_features(data, skip_field="fraud_type", indexers=indexers2)
    pred = model2.predict(features)
    label = fraud_type_labels[int(pred[0])]
    return {"fraud_type_index": int(pred[0]), "fraud_type": label}

@app.post("/predict-payment-channel")
def predict_payment_channel(data: PaymentChannelInput):
    features = prepare_features(data, skip_field="payment_channel", indexers=indexers3)
    pred = model3.predict(features)
    label = payment_channel_labels[int(pred[0])]
    return {"payment_channel_index": int(pred[0]), "payment_channel": label}
