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
data = pd.read_csv('./app/machineModels/dataSetsOriginals/UNR-IDD.csv')

# Filtrar solo las filas con etiquetas "Normal" y "TCP-SYN"
data = data[data['Label'].isin(['Normal', 'TCP-SYN'])].copy()

# Convertir etiquetas a binarias: 0 para "Normal", 1 para "TCP-SYN"
data['Label'] = data['Label'].apply(lambda x: 0 if x == 'Normal' else 1)

# ── Parsear la columna 'Port Number' a enteros ───────────
# Extraemos el número del puerto (ej. "Port#:1" -> 1) y lo convertimos a entero
data['Port Number'] = data['Port Number'].str.extract(r'(\d+)').astype(int)

# ── Seleccionar columnas relevantes ───────────
relevant_columns = [
    'Port Number', 'Received Packets', 'Sent Packets', 'Received Bytes', 'Sent Bytes',
    'Delta Received Packets', 'Delta Received Bytes', 'Delta Sent Packets', 'Delta Sent Bytes',
    'Label'
]

final_data = data[relevant_columns].copy()

# Verificar que no haya valores no numéricos en las columnas seleccionadas
final_data = final_data.dropna()  # Eliminar filas con valores faltantes

# ── Guardar el dataset modificado ───────────
csv_output_path = './app/machineModels/dataSetsTransformed/tcpSYN.csv'
final_data.to_csv(csv_output_path, index=False)
print(f"Dataset modificado guardado en: {csv_output_path}")

# ── Balanceo de clases (undersampling de la clase mayoritaria) ───────────
class_0 = final_data[final_data['Label'] == 0]  # Normal
class_1 = final_data[final_data['Label'] == 1]  # TCP-SYN

print(f"Tamaño original - Clase 0 (Normal): {len(class_0)}, Clase 1 (TCP-SYN): {len(class_1)}")

minority_size = min(len(class_0), len(class_1))

if len(class_0) > len(class_1):
    class_0_resampled = resample(class_0, replace=False, n_samples=minority_size, random_state=42)
    final_data = pd.concat([class_0_resampled, class_1]).sample(frac=1, random_state=42)
else:
    class_1_resampled = resample(class_1, replace=False, n_samples=minority_size, random_state=42)
    final_data = pd.concat([class_0, class_1_resampled]).sample(frac=1, random_state=42)

print(f"Tamaño balanceado - Clase 0: {len(final_data[final_data['Label'] == 0])}, Clase 1: {len(final_data[final_data['Label'] == 1])}")

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
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test), callbacks=[early_stopping])

# ── Evaluar el modelo en el conjunto de prueba ───────────
y_pred = (model.predict(X_test) > 0.5).astype("int32")
print("\nReporte de clasificación en el conjunto de prueba:")
print(classification_report(y_test, y_pred, target_names=['Normal', 'TCP-SYN']))

# ── Guardar el modelo y el escalador ───────────
model_path = './app/machineModels/models/tcpSYN.h5'
scaler_path = './app/machineModels/models/tcpSYN.pkl'

model.save(model_path)
joblib.dump(scaler, scaler_path)

print(f"Modelo guardado en: {model_path}")
print(f"Scaler guardado en: {scaler_path}")