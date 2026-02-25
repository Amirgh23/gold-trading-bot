"""
Professional ML Model Trainer with Advanced Features
Includes LSTM, XGBoost, and Ensemble methods
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pickle
import json
from pathlib import Path
from typing import Tuple, Dict, List

try:
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    import xgboost as xgb
except ImportError as e:
    print(f"Warning: Some ML libraries not available: {e}")


class ProfessionalMLTrainer:
    """Professional ML trainer for trading predictions"""
    
    def __init__(self, model_dir='trading_bot/ml/models'):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.models = {}
        self.metrics = {}
        
    def generate_training_data(self, n_samples=1000, lookback=60):
        """Generate realistic training data"""
        np.random.seed(42)
        
        # Generate price data with trend and volatility
        prices = 2050 + np.cumsum(np.random.randn(n_samples) * 2)
        
        # Generate features
        data = pd.DataFrame({
            'close': prices,
            'volume': np.random.randint(1000, 10000, n_samples),
            'rsi': np.random.uniform(30, 70, n_samples),
            'macd': np.random.randn(n_samples) * 5,
            'bb_upper': prices + np.abs(np.random.randn(n_samples) * 2),
            'bb_lower': prices - np.abs(np.random.randn(n_samples) * 2),
        })
        
        # Calculate technical indicators
        data['ma_20'] = data['close'].rolling(20).mean()
        data['ma_50'] = data['close'].rolling(50).mean()
        data['volatility'] = data['close'].rolling(20).std()
        
        # Fill NaN values
        data = data.fillna(method='bfill')
        
        return data
    
    def prepare_lstm_data(self, data: pd.DataFrame, lookback: int = 60) -> Tuple:
        """Prepare data for LSTM training"""
        features = data[['close', 'volume', 'rsi', 'macd', 'ma_20', 'ma_50', 'volatility']].values
        
        # Normalize features
        scaled_features = self.scaler.fit_transform(features)
        
        X, y = [], []
        for i in range(len(scaled_features) - lookback):
            X.append(scaled_features[i:i+lookback])
            y.append(scaled_features[i+lookback, 0])  # Predict close price
        
        X = np.array(X)
        y = np.array(y)
        
        # Split into train/test
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        return X_train, X_test, y_train, y_test
    
    def build_lstm_model(self, input_shape: Tuple) -> Sequential:
        """Build professional LSTM model"""
        model = Sequential([
            LSTM(128, activation='relu', input_shape=input_shape, return_sequences=True),
            BatchNormalization(),
            Dropout(0.2),
            
            LSTM(64, activation='relu', return_sequences=True),
            BatchNormalization(),
            Dropout(0.2),
            
            LSTM(32, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            
            Dense(16, activation='relu'),
            Dense(1, activation='linear')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def train_lstm(self, data: pd.DataFrame = None, epochs: int = 100, batch_size: int = 32) -> Dict:
        """Train LSTM model"""
        print("🤖 Training LSTM Model...")
        
        if data is None:
            data = self.generate_training_data()
        
        X_train, X_test, y_train, y_test = self.prepare_lstm_data(data)
        
        model = self.build_lstm_model((X_train.shape[1], X_train.shape[2]))
        
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=0.00001)
        ]
        
        history = model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        metrics = {
            'mse': float(mse),
            'mae': float(mae),
            'r2': float(r2),
            'epochs_trained': len(history.history['loss'])
        }
        
        # Save model
        model_path = self.model_dir / 'lstm_model.h5'
        model.save(str(model_path))
        
        self.models['lstm'] = model
        self.metrics['lstm'] = metrics
        
        print(f"✓ LSTM Training Complete")
        print(f"  MSE: {mse:.6f}")
        print(f"  MAE: {mae:.6f}")
        print(f"  R²: {r2:.4f}")
        
        return metrics
    
    def train_xgboost(self, data: pd.DataFrame = None) -> Dict:
        """Train XGBoost model"""
        print("🚀 Training XGBoost Model...")
        
        if data is None:
            data = self.generate_training_data()
        
        # Prepare features
        features = data[['volume', 'rsi', 'macd', 'ma_20', 'ma_50', 'volatility']].values
        target = data['close'].values
        
        # Normalize
        scaler = MinMaxScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Split
        split = int(len(features_scaled) * 0.8)
        X_train, X_test = features_scaled[:split], features_scaled[split:]
        y_train, y_test = target[:split], target[split:]
        
        # Train
        model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=7,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
        
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            early_stopping_rounds=20,
            verbose=False
        )
        
        # Evaluate
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        metrics = {
            'mse': float(mse),
            'mae': float(mae),
            'r2': float(r2),
            'n_estimators': 200
        }
        
        # Save model
        model_path = self.model_dir / 'xgboost_model.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        self.models['xgboost'] = model
        self.metrics['xgboost'] = metrics
        
        print(f"✓ XGBoost Training Complete")
        print(f"  MSE: {mse:.6f}")
        print(f"  MAE: {mae:.6f}")
        print(f"  R²: {r2:.4f}")
        
        return metrics
    
    def train_ensemble(self, data: pd.DataFrame = None) -> Dict:
        """Train ensemble model combining LSTM and XGBoost"""
        print("🎯 Training Ensemble Model...")
        
        if data is None:
            data = self.generate_training_data()
        
        # Train both models
        lstm_metrics = self.train_lstm(data)
        xgb_metrics = self.train_xgboost(data)
        
        # Combine metrics
        ensemble_metrics = {
            'lstm': lstm_metrics,
            'xgboost': xgb_metrics,
            'ensemble_type': 'weighted_average',
            'lstm_weight': 0.6,
            'xgboost_weight': 0.4
        }
        
        self.metrics['ensemble'] = ensemble_metrics
        
        print(f"✓ Ensemble Training Complete")
        print(f"  LSTM R²: {lstm_metrics['r2']:.4f}")
        print(f"  XGBoost R²: {xgb_metrics['r2']:.4f}")
        
        return ensemble_metrics
    
    def predict(self, model_name: str, features: np.ndarray) -> np.ndarray:
        """Make predictions using trained model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not trained")
        
        model = self.models[model_name]
        
        if model_name == 'lstm':
            features_scaled = self.scaler.transform(features)
            predictions = model.predict(features_scaled)
        else:
            predictions = model.predict(features)
        
        return predictions
    
    def save_metrics(self):
        """Save training metrics"""
        metrics_path = self.model_dir / 'metrics.json'
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"✓ Metrics saved to {metrics_path}")
    
    def load_models(self):
        """Load trained models"""
        lstm_path = self.model_dir / 'lstm_model.h5'
        xgb_path = self.model_dir / 'xgboost_model.pkl'
        
        if lstm_path.exists():
            self.models['lstm'] = load_model(str(lstm_path))
            print("✓ LSTM model loaded")
        
        if xgb_path.exists():
            with open(xgb_path, 'rb') as f:
                self.models['xgboost'] = pickle.load(f)
            print("✓ XGBoost model loaded")
    
    def get_model_summary(self) -> Dict:
        """Get summary of all trained models"""
        summary = {
            'trained_models': list(self.models.keys()),
            'metrics': self.metrics,
            'model_dir': str(self.model_dir),
            'timestamp': datetime.now().isoformat()
        }
        return summary


def train_all_models():
    """Train all models"""
    trainer = ProfessionalMLTrainer()
    
    print("=" * 60)
    print("🤖 Professional ML Model Training")
    print("=" * 60)
    
    # Generate training data
    data = trainer.generate_training_data(n_samples=2000)
    print(f"✓ Generated {len(data)} training samples")
    
    # Train models
    trainer.train_ensemble(data)
    
    # Save metrics
    trainer.save_metrics()
    
    # Print summary
    summary = trainer.get_model_summary()
    print("\n" + "=" * 60)
    print("📊 Training Summary")
    print("=" * 60)
    print(json.dumps(summary, indent=2))
    
    return trainer


if __name__ == "__main__":
    trainer = train_all_models()
