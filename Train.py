import os
import random
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, VectorAssembler

# Inisialisasi Spark
spark = SparkSession.builder.appName("FraudDetectionTraining").getOrCreate()

# Path direktori batch
batch_dir = "batch_data"

# Label fraud default
fraud_labels = ["money_laundering", "account_takeover", "card_not_present", "stolen_card", "phishing"]

# Isi nilai fraud_type yang kosong
def fill_missing_fraud_type(filepath):
    df = pd.read_csv(filepath)
    df["fraud_type"] = df["fraud_type"].apply(lambda x: x if pd.notna(x) else random.choice(fraud_labels))
    df.to_csv(filepath, index=False)

# Preprocessing umum
def preprocess(filepath, label_col):
    df_pd = pd.read_csv(filepath)

    # Drop kolom tidak relevan
    df_pd = df_pd.drop(columns=["transaction_id", "timestamp", "ip_address", "device_hash"], errors="ignore")
    df = spark.createDataFrame(df_pd).na.drop()

    # Kolom kategorikal
    categorical_cols = ["sender_account", "receiver_account", "transaction_type",
                        "merchant_category", "location", "device_used", "payment_channel"]
    if label_col in categorical_cols:
        categorical_cols.remove(label_col)

    indexers = {}
    for col in categorical_cols:
        if col in df.columns:
            indexer = StringIndexer(inputCol=col, outputCol=col + "_idx", handleInvalid="keep")
            model = indexer.fit(df)
            df = model.transform(df)
            indexers[col] = model.labels

    # Tangani label kolom
    if dict(df.dtypes)[label_col] == 'string':
        label_indexer = StringIndexer(inputCol=label_col, outputCol="label", handleInvalid="keep")
        label_model = label_indexer.fit(df)
        df = label_model.transform(df)
        y_col = "label"
        label_values = label_model.labels
    else:
        y_col = label_col
        label_values = None

    # Ambil kolom fitur numerik dan kategorikal yang sudah diindex
    feature_cols = ["amount", "time_since_last_transaction", "spending_deviation_score",
                    "velocity_score", "geo_anomaly_score"]

    for col in categorical_cols:
        feature_cols.append(col + "_idx")

    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    df = assembler.transform(df)

    # Konversi ke Pandas
    pdf = df.select("features", y_col).toPandas()
    X = pdf["features"].apply(lambda x: x.toArray()).tolist()
    y = pdf[y_col]

    return X, y, indexers, label_values

# ========== MODEL 1: Predict is_fraud ==========
batch1_path = os.path.join(batch_dir, "batch_1_20250529_160241.csv")
fill_missing_fraud_type(batch1_path)
X1, y1, indexers1, _ = preprocess(batch1_path, "is_fraud")

model1 = RandomForestClassifier()
model1.fit(X1, y1)

os.makedirs("models/is_fraud_model", exist_ok=True)
joblib.dump(model1, "models/is_fraud_model/model.pkl")
joblib.dump(indexers1, "models/is_fraud_model/label_indexers.pkl")

# ========== MODEL 2: Predict fraud_type ==========
batch2_path = os.path.join(batch_dir, "batch_2_20250529_160741.csv")
fill_missing_fraud_type(batch2_path)
X2, y2, indexers2, fraud_labels = preprocess(batch2_path, "fraud_type")

model2 = LogisticRegression(max_iter=200)
model2.fit(X2, y2)

os.makedirs("models/fraud_type_model", exist_ok=True)
joblib.dump(model2, "models/fraud_type_model/model.pkl")
joblib.dump(indexers2, "models/fraud_type_model/label_indexers.pkl")
joblib.dump(fraud_labels, "models/fraud_type_model/label_indexer.pkl")

# ========== MODEL 3: Predict payment_channel ==========
batch3_path = os.path.join(batch_dir, "batch_3_20250529_161241.csv")
fill_missing_fraud_type(batch3_path)
X3, y3, indexers3, channel_labels = preprocess(batch3_path, "payment_channel")

model3 = RandomForestClassifier()
model3.fit(X3, y3)

os.makedirs("models/payment_channel_model", exist_ok=True)
joblib.dump(model3, "models/payment_channel_model/model.pkl")
joblib.dump(indexers3, "models/payment_channel_model/label_indexers.pkl")
joblib.dump(channel_labels, "models/payment_channel_model/label_indexer.pkl")

print("✅ Semua model selesai dilatih dan disimpan.")
