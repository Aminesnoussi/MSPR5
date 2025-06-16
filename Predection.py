import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# 1. Chargement et nettoyage des données
df = pd.read_csv("qualite_air.csv")
df.fillna(method='ffill', inplace=True)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

# 2. Feature engineering
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day
df['weekday'] = df['date'].dt.weekday
df['is_weekend'] = (df['weekday'] >= 5).astype(int)

# Encodage des villes
le = LabelEncoder()
df['Ville_encoded'] = le.fit_transform(df['Ville'])

# 3. Sélection d'une ville
ville_cible = 'Toulouse'
df_ville = df[df['Ville'] == ville_cible].copy()

# 4. Caractéristiques et polluants
features = ['year', 'month', 'day', 'weekday', 'is_weekend']
polluants = ['PM25', 'PM10', 'O3', 'NO2', 'SO2', ' co']

# 5. Normalisation
scaler = MinMaxScaler()
df_scaled = df_ville.copy()
df_scaled[polluants] = scaler.fit_transform(df_scaled[polluants])

# 6. Séquences pour LSTM
def create_sequences(data, seq_len=15):
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i:i+seq_len])
        y.append(data[i+seq_len])
    return np.array(X), np.array(y)

X_lstm, y_lstm = create_sequences(df_scaled[polluants].values, seq_len=15)
X_train_lstm, X_test_lstm = X_lstm[:-10], X_lstm[-10:]
y_train_lstm, y_test_lstm = y_lstm[:-10], y_lstm[-10:]

# 7. LSTM optimisé
model_lstm = Sequential()
model_lstm.add(LSTM(64, activation='tanh', return_sequences=True, input_shape=(X_train_lstm.shape[1], X_train_lstm.shape[2])))
model_lstm.add(LSTM(32, activation='tanh'))
model_lstm.add(Dense(6))
model_lstm.compile(optimizer='adam', loss='mse')

model_lstm.fit(X_train_lstm, y_train_lstm, epochs=100, batch_size=16, verbose=1)

# 8. Évaluation LSTM
y_pred_lstm = model_lstm.predict(X_test_lstm)
y_pred_lstm_rescaled = scaler.inverse_transform(y_pred_lstm)
y_test_lstm_rescaled = scaler.inverse_transform(y_test_lstm)

r2_lstm = r2_score(y_test_lstm_rescaled, y_pred_lstm_rescaled)
print(f"\n📈 R² Score LSTM (global) : {r2_lstm:.2%}")

# 9. Modèle XGBoost optimisé
X_tab = df_ville[features]
predictions_xgb = {}

print("\n📊 XGBoost Résultats par polluant :")
for target in polluants:
    y = df_ville[target]
    X_train, X_test, y_train, y_test = train_test_split(X_tab, y, test_size=0.2, shuffle=False)

    model = XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred, squared=False)

    print(f"{target} - RMSE: {rmse:.2f}, R²: {r2:.2%}")
    predictions_xgb[target] = model

# 10. Prédiction future avec XGBoost
future_date = pd.to_datetime("2025-06-13")
future_features = pd.DataFrame([{
    'year': future_date.year,
    'month': future_date.month,
    'day': future_date.day,
    'weekday': future_date.weekday(),
    'is_weekend': int(future_date.weekday() >= 5)
}])

future_pred = {target: model.predict(future_features)[0] for target, model in predictions_xgb.items()}
print("\n🔮 Prédiction XGBoost pour le 2025-06-13 à Toulouse :")
for k, v in future_pred.items():
    print(f"{k}: {v:.2f}")

# 11. Visualisation pour un polluant
polluant_cible = "PM10"
index = polluants.index(polluant_cible)

valeurs_reelles = y_test_lstm_rescaled[:, index]
valeurs_predites = y_pred_lstm_rescaled[:, index]
jours = [f"J+{i+1}" for i in range(10)]

plt.figure(figsize=(10, 5))
plt.plot(jours, valeurs_reelles, label="Valeurs réelles", marker='o', color='blue')
plt.plot(jours, valeurs_predites, label="Valeurs prédites", marker='x', color='orange')
plt.axhline(y=50, color='red', linestyle='--', label='Seuil PM10 (50)')

plt.title(f"Prévision {polluant_cible} à {ville_cible} - Prochains jours")
plt.xlabel("Jour")
plt.ylabel("Concentration (µg/m³)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
