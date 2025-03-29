import joblib
import numpy as np
import pandas as pd
from sklearn.utils import resample
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Dense # type: ignore
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.callbacks import EarlyStopping # type: ignore

# ── Cargar y filtrar el dataset ───────────
data = pd.read_csv('./app/machineModels/dataSetsOriginals/tcpSYN.csv')

# ── Eliminar Flow ID ───────────
if 'Flow ID' in data.columns:
    final_data = data.drop(columns=['Flow ID'])
else:
    final_data = data.copy()

# ── Preparar datos para el entrenamiento ───────────
X = final_data.drop('Label', axis=1)
y = final_data['Label']

# Escalado de las características
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Dividir en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

# ── Construir y entrenar el modelo ───────────
model = Sequential([
    Dense(16, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
model.fit(X_train, y_train, epochs=5, batch_size=32, validation_data=(X_test, y_test), callbacks=[early_stopping])

# ── Evaluar el modelo en el conjunto de prueba ───────────
y_pred = (model.predict(X_test) > 0.5).astype("int32")
print("\nReporte de clasificación en el conjunto de prueba:")
print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))

# ── Guardar el modelo y el escalador ───────────
model_path = './app/machineModels/models/tcpSYN.h5'
scaler_path = './app/machineModels/models/tcpSYN.pkl'

transformed_csv_path = './app/machineModels/dataSetsTransformed/tcpSYN.csv'
final_data.to_csv(transformed_csv_path, index=False)
print(f"📂 Dataset transformado guardado en: {transformed_csv_path}")

model.save(model_path)
joblib.dump(scaler, scaler_path)

print(f"Modelo guardado en: {model_path}")
print(f"Scaler guardado en: {scaler_path}")