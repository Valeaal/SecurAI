import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import joblib

# === RUTAS ABSOLUTAS ===
# Ruta base del script actual
baseDir = os.path.dirname(os.path.abspath(__file__))

# Rutas absolutas
datasetPath = os.path.join(baseDir, '..', 'dataSetsOriginals', 'arpFlooding.csv')
modelPath = os.path.join(baseDir, '..', 'models', 'arpFloodingSVMmodel.pkl')
scalerPath = os.path.join(baseDir, '..', 'models', 'arpFloodingSVMscaler.pkl')
transformedDatasetPath = os.path.join(baseDir, '..', 'dataSetsTransformed', 'arpFloodingSVM.csv')

# === CARGA Y PREPROCESADO ===

# Cargar el dataset
data = pd.read_csv(datasetPath)

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
    
    if src_mac not in arp_counts:
        arp_counts[src_mac] = 0
        arp_request_counts[src_mac] = 0
        arp_reply_counts[src_mac] = 0
        unique_dst_ips[src_mac] = set()
    
    arp_counts[src_mac] += 1
    
    if op_code == 1:
        arp_request_counts[src_mac] += 1
        dst_ip = row['dst_ip(arp)']
        if pd.notna(dst_ip) and dst_ip != "0.0.0.0":
            unique_dst_ips[src_mac].add(dst_ip)
    elif op_code == 2:
        arp_reply_counts[src_mac] += 1
    
    ratio_request_reply = arp_request_counts[src_mac] / (arp_reply_counts[src_mac] + 1e-6)
    unique_ip_count = len(unique_dst_ips[src_mac])
    
    return pd.Series({
        'arp_packets_por_mac': arp_counts[src_mac],
        'arp_request_count': arp_request_counts[src_mac],
        'arp_reply_count': arp_reply_counts[src_mac],
        'ratio_request_reply': ratio_request_reply,
        'unique_dst_ip_count': unique_ip_count
    })

data[['arp_packets_por_mac', 'arp_request_count', 'arp_reply_count', 
      'ratio_request_reply', 'unique_dst_ip_count']] = data.apply(calculate_arp_metrics, axis=1)

# Eliminar columnas innecesarias
data = data.drop(columns=['src_mac_addr(eth)', 'src_mac_addr(arp)', 
                          'dst_mac_addr(eth)', 'dst_ip(arp)'])

# Reordenar columnas
columnas = [col for col in data.columns if col != 'Label'] + ['Label']
data = data[columnas]

# Filtrar benigno y ARP Flooding
filtered_data = data[data['Label'].isin([0, 2])].copy()

# Mapear etiquetas: 2 -> 1
filtered_data['Label'] = filtered_data['Label'].replace({2: 1})

# Análisis de clases
class_counts = filtered_data['Label'].value_counts()
print("\nDistribución original de clases:")
print(class_counts)

# Balanceo
min_count = min(class_counts[0], class_counts[1])
class_0 = filtered_data[filtered_data['Label'] == 0].sample(n=min_count, random_state=42)
class_1 = filtered_data[filtered_data['Label'] == 1].sample(n=min_count, random_state=42)
balanced_data = pd.concat([class_0, class_1], axis=0).sample(frac=1, random_state=42).reset_index(drop=True)

# Visualización
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
sns.countplot(x='Label', data=filtered_data)
plt.title('Distribución Original\n(0: Benigno, 1: ARP Flooding)')
plt.xlabel('Clase')
plt.ylabel('Cantidad')

plt.subplot(1, 2, 2)
sns.countplot(x='Label', data=balanced_data)
plt.title('Distribución Balanceada')
plt.xlabel('Clase')
plt.ylabel('Cantidad')

plt.tight_layout()
plt.show()

# Preparación para el modelo
X = balanced_data.drop(columns=['Label'])
y = balanced_data['Label']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

# Modelo SVM
model = SVC(kernel='rbf', probability=True, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nPrecisión del modelo SVM: {accuracy * 100:.2f}%")

# Guardar modelo y scaler
joblib.dump(model, modelPath)
joblib.dump(scaler, scalerPath)

# Guardar dataset transformado
data.to_csv(transformedDatasetPath, index=False)

print("\n✅ Dataset actualizado guardado correctamente.")
print("Primeras filas del dataset:")
print(data.head())
