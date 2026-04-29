import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import sqlite_utils
import os

class NeuralLayer:
    def __init__(self, db_path="data/signals.db"):
        self.db_path = db_path
        self.model = RandomForestClassifier(n_estimators=100)
        self.is_trained = False

    def train_on_history(self):
        """
        Trains the model on past trade results stored in the database.
        """
        if not os.path.exists(self.db_path):
            return
        
        db = sqlite_utils.Database(self.db_path)
        if "signals" not in db.table_names():
            return

        # Load completed signals
        df = pd.DataFrame(list(db["signals"].rows_where("status != 'PENDING'")))
        
        if len(df) < 20: # Minimum sample size
            return

        # Feature Engineering
        X = df[['score', 'rsi', 'volume_delta']] # Example features from DB
        y = (df['status'] == 'HIT_TP').astype(int) # Target: 1 for Win, 0 for Loss

        self.model.fit(X, y)
        self.is_trained = True
        print("Neural Layer: Model optimized on latest trade history.")

    def predict_confidence(self, current_features):
        """
        Returns a probability (0.0 to 1.0) of the trade succeeding.
        """
        if not self.is_trained:
            return 1.0 # Default to full confidence if not yet trained
        
        # current_features should be [score, rsi, volume_delta]
        prob = self.model.predict_proba([current_features])[0][1]
        return float(prob)
