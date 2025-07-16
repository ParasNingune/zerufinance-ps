import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.preprocessing import StandardScaler
import seaborn as sns

def load_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    df = pd.DataFrame(data)
    df['amount'] = df['actionData'].apply(lambda x: float(x.get('amount', 0)))
    df['assetPriceUSD'] = df['actionData'].apply(lambda x: float(x.get('assetPriceUSD', 0)))
    df['amount_usd'] = df['amount'] * df['assetPriceUSD']
    
    return df


def feature_extraction(df):
    features = df.groupby('userWallet').agg({
        'txHash': 'count',
        'amount_usd': [
            ('total_deposit', lambda x: x[df['action'] == 'deposit'].sum()),
            ('total_borrow', lambda x: x[df['action'] == 'borrow'].sum())
        ],
        'action': [('liquidation_count', lambda x: (x == 'liquidationcall').sum())]
    }).reset_index()

    features.columns = ['userWallet', 'tx_frequency', 'total_deposit', 'total_borrow', 'liquidation_count']

    repay = df[df['action'] == 'repay'].groupby('userWallet')['amount_usd'].sum()
    features['repayment_ratio'] = repay / features['total_borrow']
    features['repayment_ratio'] = features['repayment_ratio'].fillna(0).clip(0, 1)

    features.fillna(0, inplace=True)

    
    return features


def calculate_scores(features):
    
    feature_cols = ['tx_frequency', 'total_deposit', 'total_borrow', 'liquidation_count', 'repayment_ratio']
    
    scaler = StandardScaler()
    X = scaler.fit_transform(features[feature_cols])
    
    scores = (
        200 + 
        300 * X[:, 1] / (X[:, 2] + 1) +  # Deposit-to-borrow ratio
        400 * X[:, 4] -                  # Repayment ratio
        100 * X[:, 3] +                  # Liquidation count
        50 * X[:, 0]                     # Transaction frequency
    )
    
    features['credit_score'] = np.clip(scores, 0, 1000)

    return features[['userWallet', 'credit_score']]


def plot_distribution(scores, output_path):
    plt.figure(figsize=(10, 6))
    bins = range(0, 1100, 100)
    sns.histplot(scores['credit_score'], bins=bins, kde=True)
    plt.title('Credit Score Distribution')
    plt.xlabel('Credit Score')
    plt.ylabel('Number of Wallets')
    plt.xticks(bins)
    plt.savefig(output_path)
    plt.close()


def main(file_path, output_path, plot_path):
    df = load_data(file_path)
    features = feature_extraction(df)
    scores = calculate_scores(features)
    scores.to_csv(output_path, index=False)
    plot_distribution(scores, plot_path)
    print(f"Credit scores saved to {output_path}")
    print(f"Score distribution plot saved to {plot_path}")


if __name__ == "__main__":
    main("./data/user-wallet-transactions.json", "wallet_credit_scores.csv", "score_distribution.png")