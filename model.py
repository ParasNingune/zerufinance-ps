import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.preprocessing import StandardScaler
import seaborn as sns
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split

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

    deposit = features['total_deposit']
    borrow = features['total_borrow']
    repayment = features['repayment_ratio']
    liquidation = features['liquidation_count']
    tx_freq = features['tx_frequency']

    # Heuristic "pseudo" labels based on your manual formula for bootstrapping
    pseudo_scores = (
        100 + 
        300 * np.log1p(deposit) -                      # more realistic scaling
        200 * np.log1p(liquidation) +                 # non-linear penalty
        300 * repayment +                             # maintain strong signal
        150 * np.log1p(tx_freq) +                     # scale down frequency effect
        200 * np.tanh(borrow * repayment / (deposit + 1))  # responsible borrowing
    )
    
    pseudo_scores = np.clip(pseudo_scores, 0, 1000)
    features['pseudo_score'] = pseudo_scores

    feature_cols = ['tx_frequency', 'total_deposit', 'total_borrow', 'liquidation_count', 'repayment_ratio']
    X = features[feature_cols]
    y = features['pseudo_score']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)

    features['credit_score'] = np.clip(model.predict(X), 0, 1000)

    return features[['userWallet', 'credit_score']]


def plot_distribution(scores, output_path):
    plt.figure(figsize=(14, 8), dpi=120)
    sns.set_style("whitegrid")
    
    bins = np.arange(0, 1100, 100)
    hist = sns.histplot(scores['credit_score'], bins=bins, kde=True, color='skyblue', edgecolor='black')
    
    mean_score = scores['credit_score'].mean()
    median_score = scores['credit_score'].median()
    
    plt.axvline(mean_score, color='red', linestyle='--', label=f'Mean: {mean_score:.1f}')
    plt.axvline(median_score, color='green', linestyle=':', label=f'Median: {median_score:.1f}')
    
    for bar in hist.patches:
        height = bar.get_height()
        if height > 0:
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height + 1,
                f'{int(height)}',
                ha='center',
                va='bottom',
                fontsize=9,
                color='black'
            )
    
    plt.xticks(bins)
    plt.title('Wallet Credit Score Distribution', fontsize=16)
    plt.xlabel('Credit Score', fontsize=13)
    plt.ylabel('Number of Wallets', fontsize=13)
    plt.legend()

    plt.tight_layout()
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