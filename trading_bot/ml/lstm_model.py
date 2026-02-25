"""LSTM model for price prediction."""

import numpy as np
import pandas as pd
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class LSTMModel:
    """LSTM neural network for price prediction."""
    
    def __init__(
        self,
        sequence_length: int = 60,
        lstm_units: int = 50,
        dropout_rate: float = 0.2,
        learning_rate: float = 0.001,
    ):
        self.sequence_length = sequence_length
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        
        self.model = None
        self.scaler = None
        self.is_trained = False
        self.training_history = []
        self.validation_accuracy = 0.0
        
        self._build_model()
    
    def _build_model(self):
        """Build LSTM model architecture."""
        try:
            import tensorflow as tf
            from tensorflow import keras
            from tensorflow.keras import layers
            
            self.model = keras.Sequential([
                layers.LSTM(
                    self.lstm_units,
                    activation='relu',
                    input_shape=(self.sequence_length, 5),
                    return_sequences=True,
                ),
                layers.Dropout(self.dropout_rate),
                layers.LSTM(self.lstm_units, activation='relu'),
                layers.Dropout(self.dropout_rate),
                layers.Dense(25, activation='relu'),
                layers.Dense(1),
            ])
            
            self.model.compile(
                optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
                loss='mse',
                metrics=['mae'],
            )
            
            logger.info("LSTM model built successfully")
        except ImportError:
            logger.warning("TensorFlow not installed, using mock model")
            self.model = None
    
    def prepare_data(
        self,
        df: pd.DataFrame,
        train_split: float = 0.8,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare data for training.
        
        Args:
            df: DataFrame with OHLCV data
            train_split: Train/test split ratio
        
        Returns:
            X_train, X_test, y_train, y_test
        """
        try:
            from sklearn.preprocessing import MinMaxScaler
            
            # Use close price and volume
            data = df[['open', 'high', 'low', 'close', 'volume']].values
            
            # Normalize data
            self.scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_data = self.scaler.fit_transform(data)
            
            # Create sequences
            X, y = [], []
            for i in range(len(scaled_data) - self.sequence_length):
                X.append(scaled_data[i:i + self.sequence_length])
                y.append(scaled_data[i + self.sequence_length, 3])  # Close price
            
            X = np.array(X)
            y = np.array(y)
            
            # Split data
            split_idx = int(len(X) * train_split)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            logger.info(
                f"Data prepared: Train {len(X_train)}, Test {len(X_test)}"
            )
            
            return X_train, X_test, y_train, y_test
        
        except ImportError:
            logger.warning("scikit-learn not installed")
            return None, None, None, None
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        epochs: int = 50,
        batch_size: int = 32,
    ) -> dict:
        """
        Train the LSTM model.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            epochs: Number of training epochs
            batch_size: Batch size
        
        Returns:
            Training history
        """
        if self.model is None:
            logger.warning("Model not available for training")
            return {}
        
        try:
            history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                verbose=0,
            )
            
            self.is_trained = True
            self.training_history = history.history
            
            # Calculate validation accuracy
            val_loss = history.history['val_loss'][-1]
            self.validation_accuracy = max(0, 100 - (val_loss * 100))
            
            logger.info(
                f"Model trained: Validation Accuracy: {self.validation_accuracy:.2f}%"
            )
            
            return history.history
        
        except Exception as e:
            logger.error(f"Training error: {e}")
            return {}
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Input features
        
        Returns:
            Predictions
        """
        if self.model is None or not self.is_trained:
            logger.warning("Model not trained")
            return np.array([])
        
        try:
            predictions = self.model.predict(X, verbose=0)
            return predictions.flatten()
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return np.array([])
    
    def predict_next_price(
        self,
        df: pd.DataFrame,
    ) -> Tuple[Optional[float], float]:
        """
        Predict next price.
        
        Args:
            df: DataFrame with recent OHLCV data
        
        Returns:
            Predicted price and confidence
        """
        if self.model is None or not self.is_trained:
            return None, 0.0
        
        try:
            # Prepare last sequence
            data = df[['open', 'high', 'low', 'close', 'volume']].values
            scaled_data = self.scaler.transform(data)
            
            if len(scaled_data) < self.sequence_length:
                return None, 0.0
            
            X = scaled_data[-self.sequence_length:].reshape(1, self.sequence_length, 5)
            
            # Make prediction
            prediction = self.model.predict(X, verbose=0)[0][0]
            
            # Inverse transform
            dummy = np.zeros((1, 5))
            dummy[0, 3] = prediction
            predicted_price = self.scaler.inverse_transform(dummy)[0, 3]
            
            # Calculate confidence based on validation accuracy
            confidence = self.validation_accuracy
            
            return predicted_price, confidence
        
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None, 0.0
    
    def save(self, filepath: str) -> bool:
        """Save model to file."""
        try:
            if self.model is not None:
                self.model.save(filepath)
                logger.info(f"Model saved to {filepath}")
                return True
        except Exception as e:
            logger.error(f"Error saving model: {e}")
        
        return False
    
    def load(self, filepath: str) -> bool:
        """Load model from file."""
        try:
            import tensorflow as tf
            self.model = tf.keras.models.load_model(filepath)
            self.is_trained = True
            logger.info(f"Model loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
        
        return False
    
    def get_accuracy(self) -> float:
        """Get model accuracy."""
        return self.validation_accuracy
