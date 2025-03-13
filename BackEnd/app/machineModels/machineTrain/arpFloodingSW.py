import joblib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Dense  # type: ignore
from tensorflow.keras.models import Sequential  # type: ignore
from tensorflow.keras.callbacks import EarlyStopping  # type: ignore

# ── Cargar y filtrar el dataset antes de cualquier otra operación ───────────
data = pd.read_csv('./app/machineModels/dataSetsOriginals/arpFlooding+.csv')

# Eliminar todo lo que no sea ARP (columna "protocol")
data = data[data['protocol'] == 'ARP'].copy()

# Filtrar filas donde label sea 0 o 2 y renombrar 2 → 1
data = data[data['label'].isin([0, 2])].copy()
data['label'] = data['label'].replace({2: 1})  # Convertir 2 en 1 (problema binario)

# ── Añadir columna: Conteo de ARP en los últimos 2 minutos (ventana deslizante) ───────────
# Asegurarse de que 'frame.number' y 'frame.time_delta' son numéricos y ordenar por 'frame.number'
data['frame.number'] = pd.to_numeric(data['frame.number'], errors='coerce')
data['frame.time_delta'] = pd.to_numeric(data['frame.time_delta'], errors='coerce')
data = data.sort_values(by='frame.number').reset_index(drop=True)

# Calcular el tiempo absoluto acumulado a partir de 'frame.time_delta'
data['abs_time'] = data['frame.time_delta'].cumsum()

# Calcular el número total de paquetes en los últimos 2 minutos (para cualquier MAC)
times = data['abs_time'].values
window_counts = np.empty_like(times, dtype=int)
start = 0
for i in range(len(times)):
    while times[i] - times[start] > 120:
        start += 1
    window_counts[i] = i - start + 1
data['arp_count_sliding_window'] = window_counts

# ── Calcular las métricas ARP con ventana deslizante ───────────────────────────────────────
# Función para normalizar una dirección MAC
def normalize_mac(mac):
    if isinstance(mac, str):
        return mac.strip().upper()
    return ""

n = len(data)
arp_packets_por_mac_sliding = np.empty(n, dtype=int)
arp_request_count_sliding = np.empty(n, dtype=int)
arp_reply_count_sliding = np.empty(n, dtype=int)
unique_dst_ip_count_sliding = np.empty(n, dtype=int)
ratio_request_reply_sliding = np.empty(n, dtype=float)

start = 0
for i in range(n):
    # Ajustar la ventana: avanzar el puntero mientras la diferencia de tiempo sea mayor a 120 segundos
    while data.loc[i, 'abs_time'] - data.loc[start, 'abs_time'] > 120:
        start += 1

    # Normalizar la MAC de origen del paquete actual
    current_mac = normalize_mac(data.loc[i, 'arp.src.hw_mac'])
    
    # Extraer la ventana: filas de start hasta i (incluyendo la actual)
    window = data.iloc[start:i+1]
    # Filtrar las filas de la ventana que correspondan a la misma MAC
    window_mac = window[ window['arp.src.hw_mac'].astype(str).str.strip().str.upper() == current_mac ]
    
    # Número total de paquetes para esa MAC en la ventana
    arp_packets_por_mac_sliding[i] = len(window_mac)
    
    # Para las columnas de request y reply, usaremos la columna 'op_code(arp)' que vamos a definir a continuación
    # Primero, definimos la versión numérica de op_code:
    # 1 si es 'request', 2 si es 'reply', de lo contrario se conserva el valor
    # Se asume que en el dataset original la columna 'arp.opcode' es texto.
    window_mac = window_mac.copy()
    window_mac['op_code(arp)'] = window_mac['arp.opcode'].astype(str).apply(
        lambda x: 1 if x.lower() == 'request' else (2 if x.lower() == 'reply' else x)
    )
    
    # Contar requests y replies en la ventana para esa MAC
    count_request = (window_mac['op_code(arp)'] == 1).sum()
    count_reply = (window_mac['op_code(arp)'] == 2).sum()
    arp_request_count_sliding[i] = count_request
    arp_reply_count_sliding[i] = count_reply

    # Calcular el ratio (añadimos 1e-6 para evitar división por cero)
    ratio_request_reply_sliding[i] = count_request / (count_reply + 1e-6)
    
    # Contar IPs destino únicas para las requests (excluyendo "0.0.0.0")
    unique_ips = window_mac.loc[window_mac['op_code(arp)'] == 1, 'arp.dst.proto_ipv4'].dropna().unique()
    unique_ips = [ip for ip in unique_ips if ip != "0.0.0.0"]
    unique_dst_ip_count_sliding[i] = len(unique_ips)

# ── Agregar las métricas calculadas al dataframe ─────────────────────────────
data['arp_packets_por_mac'] = arp_packets_por_mac_sliding
data['arp_request_count'] = arp_request_count_sliding
data['arp_reply_count'] = arp_reply_count_sliding
data['ratio_request_reply'] = ratio_request_reply_sliding
data['unique_dst_ip_count'] = unique_dst_ip_count_sliding

# ── Calcular la columna mac_diferente_eth_arp ─────────────────────────────
data['mac_diferente_eth_arp'] = data.apply(
    lambda row: 1 if normalize_mac(row['eth.src']) != normalize_mac(row['arp.src.hw_mac']) else 0,
    axis=1
)

# Definir la columna op_code(arp) en todo el dataframe (para tenerla disponible)
data['op_code(arp)'] = data['arp.opcode'].astype(str).apply(
    lambda x: 1 if x.lower() == 'request' else (2 if x.lower() == 'reply' else x)
)

# Seleccionar columnas finales (las métricas ahora son las calculadas con ventana deslizante)
final_columns = [
    'op_code(arp)', 'mac_diferente_eth_arp', 'arp_packets_por_mac',
    'arp_request_count', 'arp_reply_count', 'ratio_request_reply',
    'unique_dst_ip_count', 'arp_count_sliding_window', 'label'  
]
final_data = data[final_columns].copy()
final_data.rename(columns={'label': 'Label'}, inplace=True)

# ── Guardar el dataset transformado ─────────────────────────────────────────────
csv_output_path = './app/machineModels/dataSetsTransformed/arpFloodingSW.csv'
final_data.to_csv(csv_output_path, index=False)
print(f"Dataset actualizado guardado correctamente en: {csv_output_path}")

# ── Entrenamiento del modelo ─────────────────────────────────────────────
# Separar características y etiqueta
X = final_data.drop('Label', axis=1)
y = final_data['Label']

# Escalado
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Dividir en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

# Construir y entrenar el modelo
model = Sequential([
    Dense(16, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
model.fit(X_train, y_train, epochs=2, batch_size=32, validation_data=(X_test, y_test), callbacks=[early_stopping])

# ── Guardar el modelo y el escalador ─────────────────────────────────────────────
model_path = './app/machineModels/models/arpFloodingSW.h5'
scaler_path = './app/machineModels/models/arpFloodingSW.pkl'

model.save(model_path)
joblib.dump(scaler, scaler_path)

print(f"Modelo guardado en: {model_path}")
print(f"Scaler guardado en: {scaler_path}")
