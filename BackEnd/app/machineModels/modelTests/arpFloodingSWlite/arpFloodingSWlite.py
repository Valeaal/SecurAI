import os
import joblib
import warnings
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report
from tensorflow.keras.models import load_model  # type: ignore

warnings.filterwarnings("ignore", category=UserWarning)

# ── Función para normalizar direcciones MAC ─────────────────────────────
def normalize_mac(mac):
    if isinstance(mac, str):
        return mac.strip().upper()
    return ""

# ── Función para transformar el dataset usando ventana deslizante ─────
def transform_dataset(data, window_duration):
    """
    Adapta el dataset original (arpFlooding+.csv) a las métricas calculadas en ventana deslizante.
    Se filtran los paquetes ARP y se recalculan las métricas para cada paquete según la ventana (window_duration).
    Luego se seleccionan las columnas que el modelo espera (sin la columna 'arp_count_sliding_window').
    """
    # Filtrar solo paquetes ARP
    data = data[data['protocol'] == 'ARP'].copy()

    # Filtrar filas con etiqueta 0 o 2 y convertir 2 a 1 (problema binario)
    data = data[data['label'].isin([0, 2])].copy()
    data['label'] = data['label'].replace({2: 1})

    # Convertir a numérico y ordenar
    data['frame.number'] = pd.to_numeric(data['frame.number'], errors='coerce')
    data['frame.time_delta'] = pd.to_numeric(data['frame.time_delta'], errors='coerce')
    data = data.sort_values(by='frame.number').reset_index(drop=True)

    # Calcular tiempo absoluto acumulado a partir de 'frame.time_delta'
    data['abs_time'] = data['frame.time_delta'].cumsum()

    # Inicializar arrays para las métricas de la ventana
    n = len(data)
    window_counts = np.empty(n, dtype=int)
    arp_packets_por_mac_sliding = np.empty(n, dtype=int)
    arp_request_count_sliding = np.empty(n, dtype=int)
    arp_reply_count_sliding = np.empty(n, dtype=int)
    unique_dst_ip_count_sliding = np.empty(n, dtype=int)
    ratio_request_reply_sliding = np.empty(n, dtype=float)

    start = 0
    for i in range(n):
        while data.loc[i, 'abs_time'] - data.loc[start, 'abs_time'] > window_duration:
            start += 1
        window_counts[i] = i - start + 1

        current_mac = normalize_mac(data.loc[i, 'arp.src.hw_mac'])
        window = data.iloc[start:i+1]
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

    data['arp_count_sliding_window'] = window_counts
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
        'unique_dst_ip_count', 'label'
    ]
    final_data = data[final_columns].copy()
    final_data.rename(columns={'label': 'Label'}, inplace=True)
    return final_data

# ── Función principal ────────────────────────────────────────────────
def main():
    model_path = './app/machineModels/models/arpFlooding.h5'
    scaler_path = './app/machineModels/models/arpFlooding.pkl'
    dataset_path = './app/machineModels/dataSetsOriginals/arpFlooding+.csv'
    output_folder = "./app/machineModels/modelTests/arpFloodingSWlite/"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print("Cargando modelo y escalador...")
    model = load_model(model_path)
    scaler = joblib.load(scaler_path)

    print("Cargando dataset...")
    data = pd.read_csv(dataset_path)

    window_durations = [30, 60, 90, 120, 150, 180]
    results = []

    for window in window_durations:
        print(f"\nTransformando dataset para ventana deslizante de {window} seg...")
        final_data = transform_dataset(data, window)
        
        dataset_filename = f"{output_folder}/arpFloodingSWlite{window}.csv"
        final_data.to_csv(dataset_filename, index=False)
        
        X = final_data.drop("Label", axis=1)
        y = final_data["Label"]

        if hasattr(scaler, "feature_names_in_"):
            X = X[scaler.feature_names_in_]

        X_scaled = scaler.transform(X)
        eval_result = model.evaluate(X_scaled, y, verbose=0)
        loss, accuracy = eval_result

        y_pred_prob = model.predict(X_scaled, verbose=0)
        y_pred = (y_pred_prob > 0.5).astype(int).ravel()
        report = classification_report(y, y_pred)

        results.append({
            "window": window,
            "loss": loss,
            "accuracy": accuracy,
            "report": report
        })

    with open(f"{output_folder}/arpFloodingSWliteResults.txt", "w") as f:
        for res in results:
            f.write("=" * 60 + "\n")
            f.write(f"Ventana: {res['window']} seg. - Test Loss: {res['loss']:.4f} - Test Accuracy: {res['accuracy']:.4f}\n")
            f.write("Classification Report:\n")
            f.write(res["report"] + "\n\n")

    print(f"\nResultados guardados correctamente en: {output_folder}")

if __name__ == "__main__":
    main()
