Aave V2 Wallet Credit Scoring
=============================

Overview
--------

This project assigns credit scores (0-1000) to wallets interacting with the Aave V2 protocol based on transaction behavior. Higher scores indicate reliable usage (high deposits, repayments); lower scores reflect risky behavior (liquidations, over-leveraging).

Methodology
-----------

*   **Data**: JSON file with transaction records (fields: userWallet, action, actionData with amount, assetPriceUSD, etc.).
    
*   **Features**:
    
    *   Transaction frequency: Number of transactions.
        
    *   Total deposit (USD): Sum of deposit amounts.
        
    *   Total borrow (USD): Sum of borrow amounts.
        
    *   Repayment ratio: Repaid amount divided by borrowed amount.
        
    *   Liquidation count: Number of liquidation events.
        
*   **Model**: Linear scoring model using normalized features:
    
    *   Base score: 200
        
    *   +300 \* (normalized deposit / (normalized borrow + 1))
        
    *   +400 \* normalized repayment ratio
        
    *   \-100 \* normalized liquidation count
        
    *   +50 \* normalized transaction frequency
        
    *   Scores clipped to \[0, 1000\].
        
*   **Validation**: Score distribution plot and analysis of wallet behaviors in analysis.md.
    

Architecture
------------

1.  **Data Loading**: Parse JSON, extract actionData fields, compute amount\_usd (amount \* assetPriceUSD).
    
2.  **Feature Engineering**: Group by userWallet, compute features, handle missing values.
    
3.  **Scoring**: Normalize features, apply linear scoring formula, clip to \[0, 1000\].
    
4.  **Output**: Save scores to wallet\_credit\_scores.csv, plot distribution to score\_distribution.png.
    

Processing Flow
---------------

1.  Run generate\_credit\_scores.py with transactions.json as input.
    
2.  Script processes data, generates features, computes scores, and saves outputs.
    
3.  Review wallet\_credit\_scores.csv for scores and score\_distribution.png for distribution.
    
4.  Check analysis.md for insights on score ranges and wallet behaviors.
    

Setup
-----

1.  Install dependencies: pip install pandas numpy scikit-learn matplotlib seaborn
    
2.  Place transactions.json in the repository root.
    
3.  Run: python generate\_credit\_scores.py
    

Files
-----

*   generate\_credit\_scores.py: Main script.
    
*   README.md: This file.
    
*   analysis.md: Score distribution and wallet behavior analysis.
    
*   wallet\_credit\_scores.csv: Output scores.
    
*   score\_distribution.png: Score distribution plot.
    

Extensibility
-------------

*   Add features (e.g., transaction recency, asset diversity).
    
*   Adjust scoring weights for specific priorities.
    
*   Use clustering or supervised models with labeled data.