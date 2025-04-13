import joblib
import numpy as np
import pandas as pd
from sklearn.utils import resample
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Dense  # type: ignore
from tensorflow.keras.models import Sequential  # type: ignore
from tensorflow.keras.callbacks import EarlyStopping  # type: ignore

# ── Cargar el dataset ───────────
data = pd.read_csv('./app/machineModels/dataSetsOriginals/udpPortScan.csv')

# ── Filtrar solo paquetes UDP ───────────
udpData = data[data['prot'] == 17].copy()

# ── Ordenar por timestamp ───────────
udpData.sort_values(by='#:unix_secs', inplace=True)

# ── Feature: segundos desde el anterior paquete UDP ───────────
udpData['segundosDesdeAnteriorPaquete'] = udpData['#:unix_secs'].diff().fillna(0)

# ── Feature: número de puertos únicos contactados por IP ──────
puertosPorIP = udpData.groupby('srcaddr')['dstport'].nunique().reset_index()
puertosPorIP.rename(columns={'dstport': 'numeroPuertosPorIP'}, inplace=True)
udpData = udpData.merge(puertosPorIP, on='srcaddr', how='left')

# ── Seleccionar columnas finales ───────────
finalColumns = [
    'dpkts',
    'doctets',
    'srcaddr',
    'dstaddr',
    'dstport',
    'segundosDesdeAnteriorPaquete',
    'numeroPuertosPorIP',
    'Label'
]
udpData = udpData[finalColumns]

# ── Seleccionar features para entrenamiento ───────────
features = [
    'dpkts',
    'doctets',
    'dstport',
    'segundosDesdeAnteriorPaquete',
    'numeroPuertosPorIP'
]
X = udpData[features]
y = udpData['Label']

# ── Normalizar datos ───────────
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ── Dividir en entrenamiento y prueba ───────────
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# ── Definir modelo secuencial ───────────
model = Sequential([
    Dense(16, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(8, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# ── Entrenar con EarlyStopping ───────────
earlyStopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

model.fit(
    X_train, y_train,
    validation_split=0.2,
    epochs=100,
    batch_size=64,
    callbacks=[earlyStopping],
    verbose=1
)

# ── Evaluar el modelo en el conjunto de prueba ───────────
y_pred = (model.predict(X_test) > 0.5).astype("int32")
print("\nReporte de clasificación en el conjunto de prueba:")
print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))

# ── Guardar el modelo y el escalador ───────────
model_path = './app/machineModels/models/udpPortScan.h5'
scaler_path = './app/machineModels/models/udpPortScan.pkl'
transformed_csv_path = './app/machineModels/dataSetsTransformed/udpPortScan.csv'

udpData.to_csv(transformed_csv_path, index=False)
print(f"📂 Dataset transformado guardado en: {transformed_csv_path}")

model.save(model_path)
joblib.dump(scaler, scaler_path)
print(f"✅ Modelo guardado en: {model_path}")
print(f"✅ Scaler guardado en: {scaler_path}")
