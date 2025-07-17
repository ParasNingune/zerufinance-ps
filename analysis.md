Credit Score Analysis
=====================

Score Distribution
------------------

The credit scores range from 0 to 1000, with higher scores indicating reliable behavior. The distribution plot (score\_distribution.png) shows the number of wallets in each 100-point range (0-100, 100-200, ..., 900-1000), with mean and median lines and bin counts.

_Current Observation_ (based on score\_distribution.png):

*   Total wallets: Approximately 3,400 (sum of bin counts: 1 + 87 + 50 + 20 + 8 + 3,331).
    
*   Distribution:
    
    *   0-100: 1 wallet
        
    *   100-200: 87 wallets
        
    *   200-300: 50 wallets
        
    *   300-400: 20 wallets
        
    *   400-500: 8 wallets
        
    *   900-1000: 3,331 wallets
        
*   Mean score: 966.6
    
*   Median score: 1000.0
    
*   The vast majority (97.7%) of wallets score 1000, indicating a strong right skew.
    

_Analysis of Skew_:

*   The GradientBoostingRegressor, trained on heuristic pseudo-scores with non-linear transformations (log1p, tanh), appears to overfit or assign maximum scores to most wallets. This could result from:
    
    *   A dataset with uniformly high repayment ratios, low liquidation counts, and high deposits, leading to consistently high pseudo-scores.
        
    *   Insufficient penalty or differentiation in the model for risky behaviors.
        
    *   Non-linear terms (e.g., log1p, tanh) not capturing enough variance in the features.
        

_Expected Adjustment_: The model should be tuned to better differentiate wallet behaviors, potentially by adjusting feature weights, adding regularization, or incorporating more diverse features.

Low-Scoring Wallets (0-200)
---------------------------

*   **Behavior**:
    
    *   Extremely low scores (e.g., 0-100: 1 wallet) likely indicate severe issues:
        
        *   High liquidation counts (penalized by -200 \* log1p(liquidation\_count)).
            
        *   Zero or near-zero repayment ratios, suggesting defaults or no debt activity.
            
        *   Very low transaction frequency, possibly bot-like or inactive wallets.
            
    *   Scores in 100-200 (87 wallets) may reflect:
        
        *   Minimal deposits or borrows with no repayments.
            
        *   Moderate liquidation events or short activity spans.
            
*   **Example**: A wallet with multiple liquidationcall actions, no repay actions, and few transactions (e.g., one-time borrow).
    
*   **Implications**: These wallets are high-risk for lending protocols. The single wallet at 0-100 may be an outlier (e.g., exploitative bot), while 100-200 wallets require closer monitoring for potential over-leveraging.
    

High-Scoring Wallets (800-1000)
-------------------------------

*   **Behavior**:
    
    *   Scores of 900-1000 (3,331 wallets) dominate, driven by:
        
        *   High total deposits (boosted by 300 \* log1p(total\_deposit)).
            
        *   High repayment ratios (boosted by 300 \* repayment\_ratio).
            
        *   Frequent transactions (boosted by 150 \* log1p(tx\_frequency)).
            
        *   Balanced borrowing (positive contribution from 200 \* tanh(borrow \* repayment / deposit)).
            
    *   The mean (966.6) and median (1000) suggest most wallets exhibit responsible behavior, with minimal liquidations.
        
*   **Example**: A wallet with frequent deposit and repay actions, high USD deposit amounts, and no liquidationcall events.
    
*   **Implications**: These wallets are highly reliable for lending protocols, suitable for higher borrowing limits or incentives (e.g., lower fees). However, the near-uniform 1000 scores indicate the model may not distinguish top performers effectively.
    

Observations
------------

*   **Skew Issue**: The 97.7% of wallets at 1000 suggest the model overestimates reliability, possibly due to:
    
    *   A dataset lacking risky behaviors (e.g., few liquidations or defaults).
        
    *   Overly generous pseudo-score formula or GradientBoostingRegressor overfitting to high pseudo-scores.
        
    *   Insufficient feature variance to penalize risky wallets.
        
*   **Key Drivers**: Repayment ratio and deposit amounts are the strongest predictors, with liquidation count having limited impact due to rarity.
    
*   **Model Performance**: The mean (966.6) and median (1000) indicate a ceiling effect. The model needs adjustment to spread scores more evenly (e.g., 0-800 range).
    
*   **Data Dependency**: Scores reflect the dataset’s composition. If most wallets are well-behaved (high repayments, no liquidations), this distribution is expected but not ideal for risk assessment.