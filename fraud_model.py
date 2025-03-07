# Import necessary libraries
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import roc_auc_score
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif
import joblib
from flask import Flask, request, jsonify
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# Load Dataset
df = pd.read_csv(r"C:\Users\reddy\Downloads\FraudShield AI-Powered Fraud Detection System\fraud_dataset_500.csv")

# Rename 'time' column to 'transaction_hour'
if 'time' in df.columns:
    df.rename(columns={'time': 'transaction_hour'}, inplace=True)

# Exploratory Data Analysis (EDA)
sns.set_style("darkgrid")
plt.figure(figsize=(6, 4))
sns.countplot(x='is_fraud', data=df, palette=['green', 'red'])
plt.title("Fraud vs Non-Fraud Transactions")
plt.xlabel("Is Fraud? (0 = No, 1 = Yes)")
plt.ylabel("Count")
plt.show()

plt.figure(figsize=(6, 4))
sns.boxplot(x='is_fraud', y='amount', data=df, palette=['green', 'red'])
plt.title("Transaction Amount by Fraud Status")
plt.xlabel("Is Fraud? (0 = No, 1 = Yes)")
plt.ylabel("Amount")
plt.show()

# Encode Categorical Variables
label_encoders = {}
categorical_cols = ['location', 'device', 'transaction_type']
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# Standardize Numerical Features
scaler = StandardScaler()
numerical_cols = ['amount', 'account_age_days', 'num_transactions_last_24h']
df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

# Feature Engineering
df['hourly_fraud_rate'] = df.groupby('transaction_hour')['is_fraud'].transform('mean')

# Dimensionality Reduction
pca = PCA(n_components=5)
df_pca = pca.fit_transform(df.drop(columns=['is_fraud', 'transaction_id']))

# Feature Selection
selector = SelectKBest(score_func=f_classif, k=5)  # Selecting top 5 features
X_selected = selector.fit_transform(df.drop(columns=['is_fraud', 'transaction_id']), df['is_fraud'])

# Data Preparation
X = df.drop(columns=['is_fraud', 'transaction_id'])
y = df['is_fraud']

# Handle Class Imbalance using SMOTE
smote = SMOTE(sampling_strategy=0.5, random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

# Convert to PyTorch Tensors
X_train_tensor = torch.tensor(X_train.values, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train.values, dtype=torch.float32).view(-1, 1)
X_test_tensor = torch.tensor(X_test.values, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test.values, dtype=torch.float32).view(-1, 1)

train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

# Define LSTM Model
class FraudLSTM(nn.Module):
    def __init__(self, input_size):
        super(FraudLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, 64, batch_first=True)
        self.dropout = nn.Dropout(0.2)
        self.fc = nn.Linear(64, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x.unsqueeze(1))
        x = self.dropout(lstm_out[:, -1, :])
        x = self.fc(x)
        return self.sigmoid(x)

input_size = X_train.shape[1]
lstm_model = FraudLSTM(input_size)

# Train LSTM Model
criterion = nn.BCELoss()
optimizer = optim.Adam(lstm_model.parameters(), lr=0.001)

epochs = 10
for epoch in range(epochs):
    for inputs, labels in train_loader:
        optimizer.zero_grad()
        outputs = lstm_model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
    print(f'Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}')

# Train Traditional Models
models = {
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "XGBoost": GradientBoostingClassifier(n_estimators=100, random_state=42),
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "SVM": SVC(probability=True)
}

# Hyperparameter Tuning
param_grid = {
    'Random Forest': {'n_estimators': [50, 100, 200]},
    'XGBoost': {'n_estimators': [50, 100, 200]},
    'Logistic Regression': {'C': [0.1, 1, 10]},
    'SVM': {'C': [0.1, 1, 10]}
}

best_models = {}
for name, model in models.items():
    grid_search = GridSearchCV(model, param_grid[name], cv=5, scoring='roc_auc')
    grid_search.fit(X_train, y_train)
    best_models[name] = grid_search.best_estimator_

# Model Evaluation using ROC AUC Score
for name, model in best_models.items():
    y_pred_prob = model.predict_proba(X_test)[:, 1]
    auc_score = roc_auc_score(y_test, y_pred_prob)
    print(f"{name} ROC AUC Score: {auc_score:.4f}")

# Save Models
joblib.dump(best_models['Random Forest'], 'fraud_model.pkl')
torch.save(lstm_model.state_dict(), 'fraud_lstm_model.pth')

# Deploy API
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    df_input = pd.DataFrame([data])

    # Apply preprocessing
    for col in categorical_cols:
        if col in df_input.columns and col in label_encoders:
            df_input[col] = label_encoders[col].transform(df_input[col])
    
    if set(numerical_cols).issubset(df_input.columns):
        df_input[numerical_cols] = scaler.transform(df_input[numerical_cols])
    
    prediction = best_models['Random Forest'].predict(df_input)
    return jsonify({'fraud_prediction': int(prediction[0])})

# Run the API only if executed directly
if __name__ == '__main__':
    print("Models trained and saved successfully!")
    # app.run(debug=False, host='0.0.0.0', port=5000)
