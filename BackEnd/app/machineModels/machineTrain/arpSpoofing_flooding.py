import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import EarlyStopping
import joblib

# Cargar el dataset
data = pd.read_csv('./app/machineModels/dataSets/arpSpoofing.csv')

# Filtrar solo las filas donde Protocol == 0
data = data[data['Protocol'] == 0]

# Eliminar columnas no necesarias (conservar dst_ip(arp))
columns_to_drop = [
    'Protocol', 'switch_id', 'in_port', 'outport', 'packet_in_count',
    'Pkt loss', 'rtt (avg)', 'total_time', 'src_ip(arp)', 'dst_mac_addr(arp)'
]
data = data.drop(columns=columns_to_drop, errors='ignore')

# Función para convertir MAC a entero
def mac_to_int(mac_address):
    if isinstance(mac_address, str):
        return int(mac_address.replace(":", ""), 16)
    return 0

# Convertir las direcciones MAC en enteros
data['src_mac_addr(eth)'] = data['src_mac_addr(eth)'].apply(mac_to_int)
data['src_mac_addr(arp)'] = data['src_mac_addr(arp)'].apply(mac_to_int)
data['dst_mac_addr(eth)'] = data['dst_mac_addr(eth)'].apply(mac_to_int)

# Característica: Diferencia entre MAC de Ethernet y ARP
data['mac_diferente_eth_arp'] = (data['src_mac_addr(eth)'] != data['src_mac_addr(arp)']).astype(int)

# Variables para métricas ARP
arp_counts = {}
arp_request_counts = {}
arp_reply_counts = {}
unique_dst_ips = {}  # {src_mac: set(dst_ips)}

def calculate_arp_metrics(row):
    src_mac = row['src_mac_addr(arp)']
    op_code = row['op_code(arp)']
    
    # Inicializar estructuras si es la primera vez que vemos esta MAC
    if src_mac not in arp_counts:
        arp_counts[src_mac] = 0
        arp_request_counts[src_mac] = 0
        arp_reply_counts[src_mac] = 0
        unique_dst_ips[src_mac] = set()
    
    arp_counts[src_mac] += 1
    
    # Actualizar conteos y conjunto de IPs destino únicas
    if op_code == 1:
        arp_request_counts[src_mac] += 1
        dst_ip = row['dst_ip(arp)']
        if pd.notna(dst_ip) and dst_ip != "0.0.0.0":  # Filtrar IPs inválidas
            unique_dst_ips[src_mac].add(dst_ip)
    elif op_code == 2:
        arp_reply_counts[src_mac] += 1
    
    # Calcular métricas
    ratio_request_reply = arp_request_counts[src_mac] / (arp_reply_counts[src_mac] + 1e-6)  # Evitar división por 0
    unique_ip_count = len(unique_dst_ips[src_mac])
    
    return pd.Series({
        'arp_packets_por_mac': arp_counts[src_mac],
        'arp_request_count': arp_request_counts[src_mac],
        'arp_reply_count': arp_reply_counts[src_mac],
        'ratio_request_reply': ratio_request_reply,
        'unique_dst_ip_count': unique_ip_count
    })

# Aplicar la función
data[['arp_packets_por_mac', 'arp_request_count', 'arp_reply_count', 
      'ratio_request_reply', 'unique_dst_ip_count']] = data.apply(calculate_arp_metrics, axis=1)

# Eliminar columnas de MAC e IP que ya no se necesitan
data = data.drop(columns=['src_mac_addr(eth)', 'src_mac_addr(arp)', 
                          'dst_mac_addr(eth)', 'dst_ip(arp)'])

# Reordenar columnas para que 'Label' esté al final
columnas = [col for col in data.columns if col != 'Label'] + ['Label']
data = data[columnas]

# Filtrar datos: solo benigno (0) y ARP Flooding (2)
filtered_data = data[data['Label'].isin([0, 2])]

# Filtrar datos: solo benigno (0) y ARP Flooding (2)
filtered_data = data[data['Label'].isin([0, 2])].copy()

# Mapear etiquetas: 2 -> 1 (ARP flooding)
filtered_data['Label'] = filtered_data['Label'].replace({2: 1})

# 1. Analizar el balance de clases
class_counts = filtered_data['Label'].value_counts()
print("\nDistribución original de clases:")
print(class_counts)

# 2. Balancear las clases
# Encontrar la clase minoritaria
min_count = min(class_counts[0], class_counts[1])

# Crear DataFrames balanceados
class_0 = filtered_data[filtered_data['Label'] == 0].sample(n=min_count, random_state=42)
class_1 = filtered_data[filtered_data['Label'] == 1].sample(n=min_count, random_state=42)

# Combinar los datos balanceados
balanced_data = pd.concat([class_0, class_1], axis=0)

# Mezclar los datos
balanced_data = balanced_data.sample(frac=1, random_state=42).reset_index(drop=True)

# 3. Visualizar el balance
plt.figure(figsize=(10, 5))

# Antes del balanceo
plt.subplot(1, 2, 1)
sns.countplot(x='Label', data=filtered_data)
plt.title('Distribución Original\n(0: Benigno, 1: ARP Flooding)')
plt.xlabel('Clase')
plt.ylabel('Cantidad')

# Después del balanceo
plt.subplot(1, 2, 2)
sns.countplot(x='Label', data=balanced_data)
plt.title('Distribución Balanceada')
plt.xlabel('Clase')
plt.ylabel('Cantidad')

plt.tight_layout()
plt.show()

# 4. Usar los datos balanceados para el modelo
X = balanced_data.drop(columns=['Label'])
y = balanced_data['Label']

# ... (el resto del código igual a partir de aquí)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Dividir en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

# Construir y entrenar el modelo (igual que antes)
model = Sequential([
    Dense(16, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
model.fit(X_train, y_train, epochs=2, batch_size=32, validation_data=(X_test, y_test), callbacks=[early_stopping])

model.save('./app/machineModels/models/arpSpoofing_flooding.h5')
joblib.dump(scaler, './app/machineModels/models/arpSpoofing_flooding.pkl')

data.to_csv('./app/machineModels/dataSets/arpSpoofing_transformed.csv', index=False)

print("Dataset actualizado guardado correctamente")
print("Primeras filas del dataset:")
print(data.head())