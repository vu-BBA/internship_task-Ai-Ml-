import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# 1. Download data
df = yf.download('AAPL', start='2011-01-01', end='2026-05-30')

# Fix potential yfinance multi-index column names
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# 2. Create target variable (Next day's close)
df['Tomorrow_Close'] = df['Close'].shift(-1)
data = df.dropna()

# 3. Define features and target
X = data[['Open', 'High', 'Low', 'Volume']]
y = data['Tomorrow_Close']

# 4. CHRONOLOGICAL SPLIT (Critical for Time Series)
split_index = int(len(data) * 0.8)

X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

# 5. Model Training
model = LinearRegression()
model.fit(X_train, y_train)

# 6. Predictions
y_pred = model.predict(X_test)

# 7. Plotting using actual dates for the X-axis
plt.figure(figsize=(10, 6))
plt.plot(y_test.index, y_test.values, label='Actual Close', marker='o', color='blue')
plt.plot(y_test.index, y_pred, label='Predicted Close', marker='x', linestyle='--', color='orange')

plt.title('AAPL Actual vs Predicted Closing Prices (Chronological Test)')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend()
plt.grid(True)
plt.gcf().autofmt_xdate() # Rotate date labels for better readability
plt.show()