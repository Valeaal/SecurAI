import pandas as pd
import numpy as np
import re
import joblib
from sklearn.metrics import classification_report
from tensorflow.keras.models import load_model #type: ignore

# ── Rutas de archivos ───────────────────────────────────────────────
DATASET_PATH = "app/machineModels/dataSetsOriginals/arpFlooding+.csv"
MODEL_PATH = "app/machineModels/models/arpFlooding.h5"
SCALER_PATH = "app/machineModels/models/arpFlooding.pkl"

# ── Cargar modelo y escalador ───────────────────────────────────────────────
model = load_model(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# ── Cargar y filtrar el dataset antes de cualquier otra operación ───────────
data = pd.read_csv(DATASET_PATH)

# Eliminar todo lo que no sea ARP (columna "protocol")
data = data[data['protocol'] == 'ARP'].copy()

# Filtrar filas donde label sea 0 o 2 y renombrar 2 → 1
data = data[data['label'].isin([0, 2])].copy()
data['label'] = data['label'].replace({2: 1})  # Convertir 2 en 1 (problema binario)

# Función para normalizar una dirección MAC (quitar espacios y convertir a mayúsculas)
def normalize_mac(mac):
    if isinstance(mac, str):
        return mac.strip().upper()
    return ""

# Diccionarios globales para las métricas ARP (clave: MAC normalizada)
arp_counts = {}
arp_request_counts = {}
arp_reply_counts = {}
unique_dst_ips = {}

def calculate_arp_metrics(row):
    """
    Calcula las métricas ARP para una fila:
      - arp_packets_por_mac
      - arp_request_count
      - arp_reply_count
      - ratio_request_reply
      - unique_dst_ip_count
    Se usa la MAC normalizada.
    """
    src_mac = normalize_mac(row['arp.src.hw_mac'])
    op_code = row['arp.opcode']
    if isinstance(op_code, str):
        op_code = 1 if op_code.lower() == 'request' else 2 if op_code.lower() == 'reply' else 0

    if src_mac not in arp_counts:
        arp_counts[src_mac] = 0
        arp_request_counts[src_mac] = 0
        arp_reply_counts[src_mac] = 0
        unique_dst_ips[src_mac] = set()

    arp_counts[src_mac] += 1
    if op_code == 1:
        arp_request_counts[src_mac] += 1
        dst_ip = row['arp.dst.proto_ipv4']
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

# ── Transformación del dataset ───────────────────────────────────────

# Calcular la columna mac_diferente_eth_arp comparando 'eth.src' y 'arp.src.hw_mac' como strings
data['mac_diferente_eth_arp'] = data.apply(
    lambda row: 1 if normalize_mac(row['eth.src']) != normalize_mac(row['arp.src.hw_mac']) else 0,
    axis=1
)

# Calcular las métricas ARP
metrics = data.apply(calculate_arp_metrics, axis=1)
data = pd.concat([data, metrics], axis=1)

# Crear la columna op_code(arp) a partir de arp.opcode
data['op_code(arp)'] = data['arp.opcode'].astype(str).apply(
    lambda x: 1 if x.lower() == 'request' else (2 if x.lower() == 'reply' else x)
)

# Seleccionar las columnas finales y renombrar 'label' a 'Label'
final_columns = [
    'op_code(arp)',              # Código de operación ARP
    'mac_diferente_eth_arp',
    'arp_packets_por_mac',
    'arp_request_count',
    'arp_reply_count',
    'ratio_request_reply',
    'unique_dst_ip_count',
    'label'                     # Se renombrará a Label
]
final_data = data[final_columns].copy()
final_data.rename(columns={'label': 'Label'}, inplace=True)

# Reordenar columnas (opcional)
ordered_columns = [
    'op_code(arp)', 'mac_diferente_eth_arp', 'arp_packets_por_mac',
    'arp_request_count', 'arp_reply_count', 'ratio_request_reply',
    'unique_dst_ip_count', 'Label'
]
final_data = final_data[ordered_columns]

# Guardar el dataset final transformado
output_path = "app/machineModels/modelTests/arpFlooding_arpFlooding+.csv"
final_data.to_csv(output_path, index=False)
print(f"Dataset transformado guardado en: {output_path}")
print(final_data.head())

# ── Evaluación del modelo con el dataset transformado ───────────────────────

# Separar características y etiquetas
X = final_data.drop(columns=['Label']).to_numpy()
y_true = final_data['Label'].to_numpy()

# Escalar las características usando el scaler cargado
X_scaled = scaler.transform(X)

# Predecir con el modelo (asumiendo salida con sigmoid)
predictions = model.predict(X_scaled)
y_pred = (predictions >= 0.5).astype(int).reshape(-1)

# Imprimir reporte de clasificación
print(classification_report(y_true, y_pred))
