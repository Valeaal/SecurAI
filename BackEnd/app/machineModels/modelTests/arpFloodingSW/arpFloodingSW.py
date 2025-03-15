import os
import time
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.utils import resample
from tensorflow.keras.layers import Dense  # type: ignore
from tensorflow.keras.models import Sequential  # type: ignore
from tensorflow.keras.callbacks import EarlyStopping  # type: ignore

# Función para normalizar direcciones MAC
def normalize_mac(mac):
    if isinstance(mac, str):
        return mac.strip().upper()
    return ""

# Definición de los parámetros de la ventana (en segundos)
window_values = range(30, 241, 20)

# Ruta del dataset original
DATASET_PATH = "./app/machineModels/dataSetsOriginals/arpFlooding+.csv"

# Archivo de salida para guardar los resultados
output_file = "./app/machineModels/modelTests/arpFloodingSW/arpFloodingSWresults.txt"

# Limpiar archivo anterior
with open(output_file, "w") as f:
    f.write("")

# Iterar sobre cada longitud de ventana
for window_length in window_values:
    console_output = []  # Para acumular resultados a imprimir
    
    console_output.append("\n" + "="*60)
    console_output.append(f"Evaluando modelo con ventana deslizante de {window_length} segundos")
    console_output.append("="*60)
    
    # ── Cargar y filtrar el dataset ─────────────────────────────
    data = pd.read_csv(DATASET_PATH)
    data = data[data['protocol'] == 'ARP'].copy()
    data = data[data['label'].isin([0, 2])].copy()
    data['label'] = data['label'].replace({2: 1})
    
    data['frame.number'] = pd.to_numeric(data['frame.number'], errors='coerce')
    data['frame.time_delta'] = pd.to_numeric(data['frame.time_delta'], errors='coerce')
    data = data.sort_values(by='frame.number').reset_index(drop=True)
    
    data['abs_time'] = data['frame.time_delta'].cumsum()
    
    times = data['abs_time'].values
    n = len(data)
    window_counts = np.empty(n, dtype=int)
    start_ptr = 0
    for i in range(n):
        while times[i] - times[start_ptr] > window_length:
            start_ptr += 1
        window_counts[i] = i - start_ptr + 1
    data['arp_count_sliding_window'] = window_counts
    
    arp_packets_por_mac_sliding = np.empty(n, dtype=int)
    arp_request_count_sliding = np.empty(n, dtype=int)
    arp_reply_count_sliding = np.empty(n, dtype=int)
    unique_dst_ip_count_sliding = np.empty(n, dtype=int)
    ratio_request_reply_sliding = np.empty(n, dtype=float)
    
    start_ptr = 0  
    for i in range(n):
        while data.loc[i, 'abs_time'] - data.loc[start_ptr, 'abs_time'] > window_length:
            start_ptr += 1
        
        current_mac = normalize_mac(data.loc[i, 'arp.src.hw_mac'])
        
        window = data.iloc[start_ptr:i+1]
        window_mac = window[window['arp.src.hw_mac'].astype(str).str.strip().str.upper() == current_mac]
        
        arp_packets_por_mac_sliding[i] = len(window_mac)
        
        window_mac = window_mac.copy()
        window_mac['op_code(arp)'] = window_mac['arp.opcode'].astype(str).apply(
            lambda x: 1 if x.lower() == 'request' else (2 if x.lower() == 'reply' else x)
        )
        
        count_request = (window_mac['op_code(arp)'] == 1).sum()
        count_reply = (window_mac['op_code(arp)'] == 2).sum()
        arp_request_count_sliding[i] = count_request
        arp_reply_count_sliding[i] = count_reply
        
        ratio_request_reply_sliding[i] = count_request / (count_reply + 1e-6)
        
        unique_ips = window_mac.loc[window_mac['op_code(arp)'] == 1, 'arp.dst.proto_ipv4'].dropna().unique()
        unique_ips = [ip for ip in unique_ips if ip != "0.0.0.0"]
        unique_dst_ip_count_sliding[i] = len(unique_ips)
    
    data['arp_packets_por_mac'] = arp_packets_por_mac_sliding
    data['arp_request_count'] = arp_request_count_sliding
    data['arp_reply_count'] = arp_reply_count_sliding
    data['ratio_request_reply'] = ratio_request_reply_sliding
    data['unique_dst_ip_count'] = unique_dst_ip_count_sliding
    
    data['mac_diferente_eth_arp'] = data.apply(
        lambda row: 1 if normalize_mac(row['eth.src']) != normalize_mac(row['arp.src.hw_mac']) else 0,
        axis=1
    )
    
    data['op_code(arp)'] = data['arp.opcode'].astype(str).apply(
        lambda x: 1 if x.lower() == 'request' else (2 if x.lower() == 'reply' else x)
    )
    
    final_columns = [
        'op_code(arp)', 'mac_diferente_eth_arp', 'arp_packets_por_mac',
        'arp_request_count', 'arp_reply_count', 'ratio_request_reply',
        'unique_dst_ip_count', 'arp_count_sliding_window', 'label'
    ]
    final_data = data[final_columns].copy()
    final_data.rename(columns={'label': 'Label'}, inplace=True)
    
    final_data = final_data.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Balancear las clases (usando submuestreo de la clase mayoritaria)

    class_0 = final_data[final_data['Label'] == 0]
    class_1 = final_data[final_data['Label'] == 1]

    if len(class_0) < len(class_1):
        class_1_resampled = resample(class_1, replace=False, n_samples=len(class_0), random_state=42)
        final_data = pd.concat([class_0, class_1_resampled]).sample(frac=1, random_state=42)
    else:
        class_0_resampled = resample(class_0, replace=False, n_samples=len(class_1), random_state=42)
        final_data = pd.concat([class_0_resampled, class_1]).sample(frac=1, random_state=42)

    
    X = final_data.drop('Label', axis=1)
    y = final_data['Label']
    
    scaler_model = StandardScaler()
    X_scaled = scaler_model.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)
    
    model = Sequential([
        Dense(16, activation='relu', input_shape=(X_train.shape[1],)),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    
    model.fit(X_train, y_train, epochs=2, batch_size=32,
              validation_data=(X_test, y_test),
              callbacks=[early_stopping], verbose=0)
    
    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    y_pred = (model.predict(X_test) > 0.5).astype(int)
    report = classification_report(y_test, y_pred)
    
    console_output.append(f"Ventana: {window_length} seg. - Test Loss: {loss:.4f} - Test Accuracy: {accuracy:.4f}")
    console_output.append("Classification Report:")
    console_output.append(report)
    
    print("\n".join(console_output))
    
    with open(output_file, "a") as f:
        f.write("\n".join(console_output) + "\n")
