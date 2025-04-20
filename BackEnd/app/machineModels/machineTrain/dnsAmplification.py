import joblib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Dense  # type: ignore
from tensorflow.keras.models import Sequential  # type: ignore
from sklearn.utils import resample  # Para balancear las clases
from tensorflow.keras.callbacks import EarlyStopping  # type: ignore

# Cargar el dataset
data = pd.read_csv('./app/machineModels/dataSetsOriginals/dnsAmplification.csv', sep=';')

# Seleccionar columnas finales (sin 'dpkts')
final_columns = [
    'dbytes', 'ct_dst_ltm', 'ct_src_dport_ltm', 'ct_dst_src_ltm', 'label'
]
final_data = data[final_columns].copy()
final_data.rename(columns={'label': 'Label'}, inplace=True)

# Balanceo de clases (undersampling exacto)
class_0 = final_data[final_data['Label'] == 0]
class_1 = final_data[final_data['Label'] == 1]
minority_size = min(len(class_0), len(class_1))

if len(class_0) > len(class_1):
    class_0_resampled = resample(class_0, replace=False, n_samples=minority_size, random_state=42)
    final_data = pd.concat([class_0_resampled, class_1])
else:
    class_1_resampled = resample(class_1, replace=False, n_samples=minority_size, random_state=42)
    final_data = pd.concat([class_0, class_1_resampled])

final_data = final_data.sample(frac=1, random_state=42).reset_index(drop=True)

# Guardar dataset balanceado
csv_output_path = './app/machineModels/dataSetsTransformed/dnsAmplification.csv'
final_data.to_csv(csv_output_path, index=False)

# Entrenamiento
X = final_data.drop('Label', axis=1)
y = final_data['Label']
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

model = Sequential([
    Dense(16, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(1, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
model.fit(X_train, y_train, epochs=2, batch_size=32, validation_data=(X_test, y_test), callbacks=[early_stopping])

model.save('./app/machineModels/models/dnsAmplification.h5')
joblib.dump(scaler, './app/machineModels/models/dnsAmplification.pkl')