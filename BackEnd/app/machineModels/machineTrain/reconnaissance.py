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

# ── Cargar y filtrar el dataset ───────────
data = pd.read_csv('./app/machineModels/dataSetsOriginals/reconnaissance.csv')

# ── Filtrar solo registros normales o reconnaissance ───────────
data = data[data['attack_cat'].isin(['Reconnaissance', 'Normal'])].copy()
data['Label'] = data['attack_cat'].apply(lambda x: 1 if x == 'Reconnaissance' else 0)

# ── Seleccionar columnas finales relevantes ───────────
final_columns = [
    'dur',               # duración del flujo
    'spkts', 'dpkts',    # paquetes origen/destino
    'sbytes', 'dbytes',  # bytes origen/destino
    'rate',              # tasa de envío
    'sttl', 'dttl',      # TTLs
    'sinpkt', 'dinpkt',  # interpacket time
    'smean', 'dmean',    # tamaño medio de paquetes
    'ct_dst_ltm',        # conexiones recientes a destino
    'ct_src_dport_ltm',  # nº puertos distintos desde mismo origen
    'Label'              # clase binaria
]

final_data = data[final_columns].copy()

# ── Separar clases ───────────
normal_data = final_data[final_data['Label'] == 0]
attack_data = final_data[final_data['Label'] == 1]

# ── Sobremuestrear ataques para igualar la cantidad de normales ───────────
attack_upsampled = resample(
    attack_data,
    replace=True,                # sample con reemplazo
    n_samples=len(normal_data),  # igualar número de muestras
    random_state=42
)

# ── Concatenar datos balanceados ───────────
balanced_data = pd.concat([normal_data, attack_upsampled])
balanced_data = balanced_data.sample(frac=1, random_state=42).reset_index(drop=True)  # Mezclar

# ── Preparar datos para el entrenamiento ───────────
X = balanced_data.drop('Label', axis=1)
y = balanced_data['Label']

# Escalado de características
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# División de los datos
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

# ── Construcción y entrenamiento del modelo ───────────
model = Sequential([
    Dense(16, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

model.fit(X_train, y_train, epochs=15, batch_size=32,
          validation_data=(X_test, y_test), callbacks=[early_stopping])

# ── Evaluar el modelo ───────────
y_pred = (model.predict(X_test) > 0.5).astype("int32")
print("\n📊 Reporte de clasificación en el conjunto de prueba:")
print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))

# ── Guardar el modelo y el escalador ───────────
model_path = './app/machineModels/models/reconnaissance.h5'
scaler_path = './app/machineModels/models/reconnaissance.pkl'
transformed_csv_path = './app/machineModels/dataSetsTransformed/reconnaissance.csv'

final_data.to_csv(transformed_csv_path, index=False)
model.save(model_path)
joblib.dump(scaler, scaler_path)

print(f"📂 Dataset transformado guardado en: {transformed_csv_path}")
print(f"💾 Modelo guardado en: {model_path}")
print(f"🧪 Scaler guardado en: {scaler_path}")
