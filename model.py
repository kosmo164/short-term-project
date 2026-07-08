import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import InputLayer, Dense, LSTM
from datetime import datetime
from io import BytesIO
import base64

def run_prediction(TICKER):
    PAST_DAYS = 12
    TRAIN_RATIO = 0.8
    FUTURE_DAYS = 90
    START_DATE = "2025-07-01"
    END_DATE = datetime.today().strftime("%Y-%m-%d")

    data = yf.download(TICKER, start=START_DATE, end=END_DATE, progress=False)
    if data.empty:
        raise ValueError(f"{TICKER} 데이터 수집 실패")

    df = data[["Close"]].dropna().copy()
    dates = pd.to_datetime(df.index)
    prices = df["Close"].values.reshape(-1, 1)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(prices)

    X, Y = [], []
    for i in range(len(scaled) - PAST_DAYS):
        X.append(scaled[i:i + PAST_DAYS])
        Y.append(scaled[i + PAST_DAYS])
    X, Y = np.array(X), np.array(Y)

    split = int(len(X) * TRAIN_RATIO)
    X_train, X_test = X[:split], X[split:]
    Y_train, Y_test = Y[:split], Y[split:]

    model = Sequential([
        InputLayer(shape=(PAST_DAYS, 1)),
        LSTM(64),
        Dense(1, activation="linear")
    ])
    model.compile(optimizer="adam", loss="mse")
    model.fit(X_train, Y_train, epochs=10, batch_size=16, verbose=0)

    pred_test = model.predict(X_test, verbose=0)
    pred_test = scaler.inverse_transform(pred_test).flatten()
    test_dates = dates[PAST_DAYS + split:PAST_DAYS + split + len(pred_test)]

    seq = scaled[-PAST_DAYS:].reshape(1, PAST_DAYS, 1)
    future_vals = []
    for _ in range(FUTURE_DAYS):
        p = model.predict(seq, verbose=0)
        future_vals.append(p[0, 0])
        seq = np.append(seq[:, 1:, :], p.reshape(1, 1, 1), axis=1)
    future_pred = scaler.inverse_transform(np.array(future_vals).reshape(-1, 1)).flatten()
    future_dates = pd.bdate_range(start=dates[-1] + pd.Timedelta(days=1), periods=FUTURE_DAYS)

    # 그래프를 메모리에 저장
    fig, ax = plt.subplots(figsize=(15, 7))
    ax.plot(dates, prices.flatten(), color="gray", linewidth=2.5, alpha=0.9, label="Past Actual")
    ax.plot(test_dates, pred_test, color="royalblue", linewidth=2.2, label="Past Predicted")
    ax.plot(future_dates, future_pred, color="crimson", linewidth=2.8, label="Future Predicted")
    ax.axvline(dates[-1], color="black", linestyle="--", linewidth=1.3, alpha=0.8, label="Last Actual Date")
    ax.scatter([dates[-1]], [prices[-1][0]], color="black", s=60, zorder=7, label="Current Price")
    ax.set_title(f"{TICKER} Stock Price Forecast", fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(True, linestyle=":", alpha=0.35)
    plt.tight_layout()

    # BytesIO로 변환 후 base64 인코딩
    img = BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode("utf-8")
    plt.close()

    return plot_url


