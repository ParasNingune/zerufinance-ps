Aave V2 Wallet Credit Scoring
=============================

Overview
--------

This project assigns credit scores (0-1000) to wallets interacting with the Aave V2 protocol based on transaction behavior. Higher scores indicate reliable usage (high deposits, repayments, frequent activity); lower scores reflect risky behavior (liquidations, low activity). The model uses a GradientBoostingRegressor trained on heuristic pseudo-scores to achieve a wider score distribution.

Methodology
-----------

*   **Data**: JSON file with transaction records (fields: userWallet, action, actionData with amount, assetPriceUSD, etc.).
    
*   **Features**:
    
    *   Transaction frequency: Number of transactions.
        
    *   Total deposit (USD): Sum of deposit amounts.
        
    *   Total borrow (USD): Sum of borrow amounts.
        
    *   Repayment ratio: Repaid amount divided by borrowed amount.
        
    *   Liquidation count: Number of liquidation events.
        
*   **Model**:
    
    1.  **Pseudo-Score**: Heuristic score to bootstrap training:
        
        *   Base: 100
            
        *   +300 \* log1p(total\_deposit)
            
        *   \-200 \* log1p(liquidation\_count)
            
        *   +300 \* repayment\_ratio
            
        *   +150 \* log1p(tx\_frequency)
            
        *   +200 \* tanh(borrow \* repayment / (deposit + 1))
            
        *   Clipped to \[0, 1000\].
            
    2.  **GradientBoostingRegressor**: Trained on features and pseudo-scores to predict final scores, clipped to \[0, 1000\].
        
*   **Validation**: Score distribution plot (score\_distribution.png) and analysis in analysis.md.
    

Architecture
------------

1.  **Data Loading**: Parse JSON, extract actionData fields, compute amount\_usd (amount \* assetPriceUSD).
    
2.  **Feature Engineering**: Group by userWallet, compute features, handle missing values with zeros, clip repayment ratio to \[0, 1\].
    
3.  **Scoring**:
    
    *   Generate pseudo-scores using heuristic formula with non-linear transformations (log1p, tanh).
        
    *   Train GradientBoostingRegressor on normalized features and pseudo-scores.
        
    *   Predict final scores for all wallets.
        
4.  **Output**: Save scores to wallet\_credit\_scores.csv, plot distribution with mean/median and bin counts to score\_distribution.png.
    

Processing Flow
---------------

        ┌──────────────────────────────┐
        │ 1. Place JSON in ./data/     │
        │ user-wallet-transactions.json
        └────────────┬─────────────────┘
                     │
                     ▼
        ┌──────────────────────────────┐
        │ 2. Run model.py              │
        │    → Data is loaded          │
        │    → Features extracted      │
        │    → ML model predicts score │
        └────────────┬─────────────────┘
                     │
                     ▼
        ┌──────────────────────────────┐
        │ 3. Review Outputs            │
        │    ✔ wallet_credit_scores.csv│
        │    ✔ score_distribution.png  │
        └────────────┬─────────────────┘
                     │
                     ▼
        ┌──────────────────────────────┐
        │ 4. Update analysis.md        │
        │    → Add insights/plots      │
        │    → Explain score patterns  │
        └──────────────────────────────┘

Setup
-----

1.  pip install -r requirements.txt
    
2.  Ensure user-wallet-transactions.json is in ./data/.
    
3.  python model.py
    

Files
-----

*   model.py: Main script for scoring and plotting.
    
*   README.md: This file.
    
*   analysis.md: Score distribution and wallet behavior analysis.
    
*   wallet\_credit\_scores.csv: Output scores (userWallet, credit\_score).
    
*   score\_distribution.png: Histogram of scores with mean/median and bin counts.
