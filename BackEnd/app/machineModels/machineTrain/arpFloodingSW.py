import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
from tensorflow.keras.models import Sequential  # type: ignore
from tensorflow.keras.layers import Dense  # type: ignore
from tensorflow.keras.callbacks import EarlyStopping  # type: ignore

# ── Rutas base ──────────────────────────────────────────────────────────────
baseDir = os.path.dirname(os.path.abspath(__file__))
datasetPath = os.path.join(baseDir, '..', 'dataSetsOriginals', 'arpFlooding+.csv')
csvOutputPath = os.path.join(baseDir, '..', 'dataSetsTransformed', 'arpFloodingSW_balanced.csv')
modelPath = os.path.join(baseDir, '..', 'models', 'arpFloodingSW.h5')
scalerPath = os.path.join(baseDir, '..', 'models', 'arpFloodingSW.pkl')

# ── Cargar y filtrar el dataset ─────────────────────────────────────────────
data = pd.read_csv(datasetPath)
data = data[data['protocol'] == 'ARP'].copy()
data = data[data['label'].isin([0, 2])].copy()
data['label'] = data['label'].replace({2: 1})

# ── Preprocesado temporal ───────────────────────────────────────────────────
data['frame.number'] = pd.to_numeric(data['frame.number'], errors='coerce')
data['frame.time_delta'] = pd.to_numeric(data['frame.time_delta'], errors='coerce')
data = data.sort_values(by='frame.number').reset_index(drop=True)
data['abs_time'] = data['frame.time_delta'].cumsum()

times = data['abs_time'].values
windowCounts = np.empty_like(times, dtype=int)
start = 0
for i in range(len(times)):
    while times[i] - times[start] > 90:
        start += 1
    windowCounts[i] = i - start + 1
data['arp_count_sliding_window'] = windowCounts

# ── Función para normalizar MAC ─────────────────────────────────────────────
def normalizeMac(mac):
    if isinstance(mac, str):
        return mac.strip().upper()
    return ""

# ── Métricas ARP por MAC ────────────────────────────────────────────────────
n = len(data)
arpPacketsPorMac = np.empty(n, dtype=int)
arpRequestCount = np.empty(n, dtype=int)
arpReplyCount = np.empty(n, dtype=int)
uniqueDstIpCount = np.empty(n, dtype=int)
ratioRequestReply = np.empty(n, dtype=float)

start = 0
for i in range(n):
    while data.loc[i, 'abs_time'] - data.loc[start, 'abs_time'] > 90:
        start += 1
    currentMac = normalizeMac(data.loc[i, 'arp.src.hw_mac'])
    window = data.iloc[start:i+1]
    windowMac = window[window['arp.src.hw_mac'].astype(str).str.strip().str.upper() == currentMac].copy()

    windowMac['op_code(arp)'] = windowMac['arp.opcode'].astype(str).apply(
        lambda x: 1 if x.lower() == 'request' else (2 if x.lower() == 'reply' else x)
    )

    arpPacketsPorMac[i] = len(windowMac)
    countRequest = (windowMac['op_code(arp)'] == 1).sum()
    countReply = (windowMac['op_code(arp)'] == 2).sum()
    arpRequestCount[i] = countRequest
    arpReplyCount[i] = countReply
    ratioRequestReply[i] = countRequest / (countReply + 1e-6)
    uniqueIps = windowMac.loc[windowMac['op_code(arp)'] == 1, 'arp.dst.proto_ipv4'].dropna().unique()
    uniqueIps = [ip for ip in uniqueIps if ip != "0.0.0.0"]
    uniqueDstIpCount[i] = len(uniqueIps)

data['arp_packets_por_mac'] = arpPacketsPorMac
data['arp_request_count'] = arpRequestCount
data['arp_reply_count'] = arpReplyCount
data['ratio_request_reply'] = ratioRequestReply
data['unique_dst_ip_count'] = uniqueDstIpCount

# ── Otras métricas ──────────────────────────────────────────────────────────
data['mac_diferente_eth_arp'] = data.apply(
    lambda row: 1 if normalizeMac(row['eth.src']) != normalizeMac(row['arp.src.hw_mac']) else 0,
    axis=1
)
data['op_code(arp)'] = data['arp.opcode'].astype(str).apply(
    lambda x: 1 if x.lower() == 'request' else (2 if x.lower() == 'reply' else x)
)

finalColumns = [
    'op_code(arp)', 'mac_diferente_eth_arp', 'arp_packets_por_mac',
    'arp_request_count', 'arp_reply_count', 'ratio_request_reply',
    'unique_dst_ip_count', 'arp_count_sliding_window', 'label'
]
finalData = data[finalColumns].copy()
finalData.rename(columns={'label': 'Label'}, inplace=True)

# ── Balanceo de clases ──────────────────────────────────────────────────────
class0 = finalData[finalData['Label'] == 0]
class1 = finalData[finalData['Label'] == 1]
reductionFactor = 0.8

if len(class0) < len(class1):
    newSize = int(len(class1) * reductionFactor)
    class1Resampled = resample(class1, replace=False, n_samples=newSize, random_state=42)
    finalData = pd.concat([class0, class1Resampled]).sample(frac=1, random_state=42)
else:
    newSize = int(len(class0) * reductionFactor)
    class0Resampled = resample(class0, replace=False, n_samples=newSize, random_state=42)
    finalData = pd.concat([class0Resampled, class1]).sample(frac=1, random_state=42)

# ── Guardar dataset balanceado ──────────────────────────────────────────────
finalData.to_csv(csvOutputPath, index=False)
print(f"Dataset balanceado guardado correctamente en: {csvOutputPath}")

# ── Entrenamiento del modelo ────────────────────────────────────────────────
X = finalData.drop('Label', axis=1)
y = finalData['Label']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

model = Sequential([
    Dense(16, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(1, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
earlyStopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
model.fit(X_train, y_train, epochs=2, batch_size=32, validation_data=(X_test, y_test), callbacks=[earlyStopping])

# ── Guardar modelo y escalador ──────────────────────────────────────────────
model.save(modelPath)
joblib.dump(scaler, scalerPath)

print(f"Modelo guardado en: {modelPath}")
print(f"Scaler guardado en: {scalerPath}")
