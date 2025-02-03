import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential  # type: ignore
from tensorflow.keras.layers import Dense  # type: ignore
from tensorflow.keras.callbacks import EarlyStopping  # type: ignore
import joblib

# ---------------------------
# Cargar y procesar el dataset
# ---------------------------
data = pd.read_csv('./app/machineModels/dataSets/arpSpoofing.csv')

# Filtrar solo las filas donde Protocol == 0
data = data[data['Protocol'] == 0]

# Eliminar las columnas no necesarias
columns_to_drop = [
    'Protocol', 'switch_id', 'in_port', 'outport', 'packet_in_count', 'Pkt loss', 'rtt (avg)', 'total_time',
    'src_ip(arp)', 'dst_ip(arp)', 'dst_mac_addr(arp)'
]
data = data.drop(columns=columns_to_drop, errors='ignore')

# Convertir las direcciones MAC en números enteros
def mac_to_int(mac_address):
    return int(mac_address.replace(":", ""), 16) if isinstance(mac_address, str) else 0

data['src_mac_addr(eth)'] = data['src_mac_addr(eth)'].apply(mac_to_int)
data['src_mac_addr(arp)'] = data['src_mac_addr(arp)'].apply(mac_to_int)
data['dst_mac_addr(eth)'] = data['dst_mac_addr(eth)'].apply(mac_to_int)

# Característica: Diferencia entre MAC de Ethernet y ARP
data['mac_diferente_eth_arp'] = (data['src_mac_addr(eth)'] != data['src_mac_addr(arp)']).astype(int)

# Variables para métricas ARP
arp_counts = {}
arp_request_counts = {}
arp_reply_counts = {}

def calculate_arp_metrics(row):
    src_mac = row['src_mac_addr(arp)']
    op_code = row['op_code(arp)']
    
    if src_mac not in arp_counts:
        arp_counts[src_mac] = 0
        arp_request_counts[src_mac] = 0
        arp_reply_counts[src_mac] = 0

    arp_counts[src_mac] += 1

    if op_code == 1:
        arp_request_counts[src_mac] += 1
    elif op_code == 2:
        arp_reply_counts[src_mac] += 1

    ratio_request_reply = arp_request_counts[src_mac] / (arp_reply_counts[src_mac] + 1)

    return pd.Series({
        'arp_packets_por_mac': arp_counts[src_mac],
        'arp_request_count': arp_request_counts[src_mac],
        'arp_reply_count': arp_reply_counts[src_mac],
        'ratio_request_reply': ratio_request_reply
    })

# Aplicar la función a cada fila
data[['arp_packets_por_mac', 'arp_request_count', 'arp_reply_count', 'ratio_request_reply']] = data.apply(calculate_arp_metrics, axis=1)

# Eliminar columnas de MAC después de extraer las características
data = data.drop(columns=['src_mac_addr(eth)', 'src_mac_addr(arp)', 'dst_mac_addr(eth)'])

# Reordenar columnas para que 'Label' esté al final
cols = [col for col in data.columns if col != 'Label'] + ['Label']
data = data[cols]

# Filtrar datos: solo benigno (0) y ARP Flooding (2)
filtered_data = data[data['Label'].isin([0, 2])]

# ---------------------------
# Visualización sin balancear
# ---------------------------
plt.figure(figsize=(6, 4))
orig_counts = filtered_data['Label'].value_counts()
sns.barplot(x=orig_counts.index, y=orig_counts.values, palette='viridis')
plt.xlabel('Label (0 = Benigno, 2 = Flooding)')
plt.ylabel('Cantidad de muestras')
plt.title('Distribución de las clases (sin balancear)')
for i, v in enumerate(orig_counts.values):
    plt.text(i, v + 5, str(v), ha='center', fontsize=12)
plt.show()

# ---------------------------
# Balanceo de clases
# ---------------------------
# Dividir en benignos y flooding
benign_data = filtered_data[filtered_data['Label'] == 0]
flooding_data = filtered_data[filtered_data['Label'] == 2]

# Usar el número mínimo de muestras entre ambas clases
n_samples = min(len(benign_data), len(flooding_data))
benign_data_balanced = benign_data.sample(n=n_samples, random_state=42)
flooding_data_balanced = flooding_data.sample(n=n_samples, random_state=42)

# Concatenar para formar el dataset balanceado
balanced_data = pd.concat([benign_data_balanced, flooding_data_balanced])

# ---------------------------
# Visualización balanceada
# ---------------------------
plt.figure(figsize=(6, 4))
bal_counts = balanced_data['Label'].value_counts()
sns.barplot(x=bal_counts.index, y=bal_counts.values, palette='viridis')
plt.xlabel('Label (0 = Benigno, 2 = Flooding)')
plt.ylabel('Cantidad de muestras')
plt.title('Distribución de las clases (balanceado)')
for i, v in enumerate(bal_counts.values):
    plt.text(i, v + 5, str(v), ha='center', fontsize=12)
plt.show()

# ---------------------------
# Preparar datos para el entrenamiento
# ---------------------------
X = balanced_data.drop(columns=['Label'])
y = balanced_data['Label']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

y_encoded = (y == 2).astype(int)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.3, random_state=42)

# ---------------------------
# Construir y entrenar el modelo
# ---------------------------
model = Sequential([
    Dense(16, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
model.fit(X_train, y_train, epochs=1, batch_size=32, validation_data=(X_test, y_test), callbacks=[early_stopping])

# Guardar modelo y escalador
model.save('./app/machineModels/models/arpSpoofing_flooding.h5')
joblib.dump(scaler, './app/machineModels/models/arpSpoofing_flooding.pkl')

# Guardar el dataset balanceado transformado
balanced_data.to_csv('./app/machineModels/dataSets/arpSpoofing_transformed.csv', index=False)

# Mensajes de confirmación
print("✅ Dataset balanceado guardado en './app/machineModels/dataSets/arpSpoofing_transformed.csv'")
print("📊 Gráficos de distribución generados (sin balancear y balanceado).")
print("📂 Modelo y escalador guardados en ./models")
