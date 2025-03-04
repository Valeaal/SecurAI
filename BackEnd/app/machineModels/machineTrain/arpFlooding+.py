import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping  # type: ignore
from tensorflow.keras import Sequential, regularizers  # type: ignore
from tensorflow.keras.layers import Dense, LSTM, Dropout  # type: ignore
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import confusion_matrix, classification_report


# Cargar el dataset
data = pd.read_csv('./app/machineModels/dataSets/arpFlooding+.csv')
data = data.sort_values(by="frame.number").reset_index(drop=True)

# Eliminar solo direcciones MAC e IP
columns_to_drop = ['eth.src', 'eth.dst', 'arp.dst.hw_mac', 
                   'arp.src.hw_mac', 'arp.src.proto_ipv4', 'arp.dst.proto_ipv4', 
                   'ip.src', 'ip.dst']
data = data.drop(columns=columns_to_drop, errors='ignore')
data = data[data['label'] != 1]

# Filtrar solo los paquetes ARP antes de codificar
arp_data = data[data['protocol'] == 'ARP']
other_data = data[data['protocol'] != 'ARP']

# Ver cuentas de clases antes de balancear
print("Distribucion de label en ARP antes del balanceo:")
print(arp_data['label'].value_counts())

# Obtener la cuenta mínima de las clases presentes en los datos
min_count_arp_0 = arp_data['label'].value_counts().get(0, 0)
min_count_arp_2 = arp_data['label'].value_counts().get(2, 0)

# Encuentra el número mínimo de muestras entre las clases 0 y 2
min_count_arp = min(min_count_arp_0, min_count_arp_2)

# Ajustar todas las clases al tamaño de la clase minoritaria
arp_data_balanced = arp_data.groupby('label', group_keys=False).apply(
    lambda x: x.sample(n=min_count_arp, random_state=42)
).reset_index(drop=True)

# Ver cuentas de clases después del balanceo
print("Distribución de label en ARP tras el balanceo:")
print(arp_data_balanced['label'].value_counts())

# Crear un diccionario para almacenar los LabelEncoders de todas las columnas de tipo string
encoders = {}

for col in data.columns:
    if data[col].dtype == 'object':  # Si la columna es string
        # Si la columna tiene valores hexadecimales, los convertimos a enteros sin usar LabelEncoder
        if data[col].str.startswith("0x", na=False).any():
            data[col] = data[col].apply(lambda x: int(x, 16) if isinstance(x, str) and x.startswith('0x') else x)
        else:
            # Usamos un LabelEncoder y lo almacenamos en el diccionario
            le = LabelEncoder()
            data[col] = le.fit_transform(data[col])
            encoders[col] = le

# Convertir 'arp.opcode' en valores numéricos (por si acaso)
data['arp.opcode'] = data['arp.opcode'].replace({'request': 1, 'reply': 2}).astype(float)

# Rellenar valores NaN con 0
data.fillna(0, inplace=True)

# Balancear las clases (0, 1, 2, 3, 4)
min_count = data['label'].value_counts().min()
balanced_data = data.groupby('label', group_keys=False)\
                    .apply(lambda x: x.sample(n=min_count, random_state=42))\
                    .reset_index(drop=True)

# Después de realizar el balanceo, aplicar el refactoring a balanced_data
balanced_data['label'] = balanced_data['label'].replace({2: 1, 3: 2, 4: 3}).astype(int)

# Normalizar datos
X = balanced_data.drop(columns=['label'])
y = balanced_data['label'].astype(int)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Crear secuencias de 128 paquetes
sequence_length = 128
X_sequences = []
y_sequences = []

for i in range(len(X_scaled) - sequence_length):
    X_sequences.append(X_scaled[i:i + sequence_length])
    y_sequences.append(y[i:i + sequence_length])

X_sequences = np.array(X_sequences)
y_sequences = np.array(y_sequences).astype(int)

# Dividir en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X_sequences, y_sequences, test_size=0.3, random_state=42)

# Construcción del modelo LSTM para clasificación multiclase
model = Sequential([
    LSTM(32, return_sequences=True, input_shape=(sequence_length, X_train.shape[2]), 
         kernel_regularizer=regularizers.l2(0.01)),
    Dropout(0.4),
    LSTM(16, return_sequences=True, 
         kernel_regularizer=regularizers.l2(0.01)),
    Dropout(0.6),
    Dense(4, activation='softmax', 
          kernel_regularizer=regularizers.l2(0.01))
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
early_stopping = EarlyStopping(monitor='val_loss', patience=2, restore_best_weights=True)

model.fit(X_train, y_train, epochs=4, batch_size=300, validation_data=(X_test, y_test), callbacks=[early_stopping])

# Evaluación en el conjunto de prueba
y_pred = model.predict(X_test)

# Convertir las probabilidades de salida a clases, tomando la clase con la mayor probabilidad
y_pred_classes = np.argmax(y_pred, axis=-1)

# Imprimir el reporte de clasificación con detalles como precision, recall y f1-score
print("Reporte de clasificación:")
print(classification_report(y_test.flatten(), y_pred_classes.flatten()))

# Guardar modelo, scaler y los encoders
model.save('./app/machineModels/models/arpFlooding+.h5')
joblib.dump(scaler, './app/machineModels/models/arpFlooding+.pkl')
joblib.dump(encoders, './app/machineModels/models/arpFlooding+_encoders.pkl')

balanced_data.to_csv('./app/machineModels/dataSets/arpFlooding+_transformed.csv', index=False)

print("Modelo LSTM multiclase entrenado y guardado correctamente.")
