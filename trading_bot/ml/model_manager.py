"""ML model management with automatic retraining."""

from typing import Optional, Dict
from datetime import datetime, timedelta
import logging
import pandas as pd
from trading_bot.ml.lstm_model import LSTMModel

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages ML models with automatic retraining."""
    
    def __init__(
        self,
        model_path: str = "models/lstm_model.h5",
        retraining_threshold: float = 55.0,
        retraining_interval_hours: int = 24,
    ):
        self.model_path = model_path
        self.retraining_threshold = retraining_threshold
        self.retraining_interval = timedelta(hours=retraining_interval_hours)
        
        self.model = LSTMModel()
        self.last_retraining = None
        self.prediction_history = []
        self.accuracy_history = []
    
    def should_retrain(self) -> bool:
        """Check if model should be retrained."""
        # Check accuracy threshold
        if self.model.get_accuracy() < self.retraining_threshold:
            logger.warning(
                f"Model accuracy {self.model.get_accuracy():.2f}% "
                f"below threshold {self.retraining_threshold}%"
            )
            return True
        
        # Check retraining interval
        if self.last_retraining is None:
            return True
        
        if datetime.now() - self.last_retraining > self.retraining_interval:
            logger.info("Retraining interval reached")
            return True
        
        return False
    
    def retrain(self, df: pd.DataFrame) -> bool:
        """
        Retrain model on latest data.
        
        Args:
            df: DataFrame with recent OHLCV data
        
        Returns:
            True if retraining successful
        """
        try:
            logger.info("Starting model retraining...")
            
            # Prepare data
            X_train, X_test, y_train, y_test = self.model.prepare_data(df)
            
            if X_train is None:
                logger.warning("Could not prepare data for retraining")
                return False
            
            # Train model
            history = self.model.train(
                X_train, y_train,
                X_test, y_test,
                epochs=50,
                batch_size=32,
            )
            
            if not history:
                logger.warning("Training failed")
                return False
            
            # Save model
            self.model.save(self.model_path)
            self.last_retraining = datetime.now()
            
            logger.info(
                f"Model retrained successfully. "
                f"Accuracy: {self.model.get_accuracy():.2f}%"
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Retraining error: {e}")
            return False
    
    def predict_signal(
        self,
        df: pd.DataFrame,
        confidence_threshold: float = 40.0,
    ) -> Optional[Dict]:
        """
        Generate trading signal from ML prediction.
        
        Args:
            df: DataFrame with recent OHLCV data
            confidence_threshold: Minimum confidence for signal
        
        Returns:
            Signal dict or None
        """
        predicted_price, confidence = self.model.predict_next_price(df)
        
        if predicted_price is None:
            return None
        
        # Filter low confidence predictions
        if confidence < confidence_threshold:
            logger.debug(f"Prediction confidence {confidence:.2f}% below threshold")
            return None
        
        current_price = df['close'].iloc[-1]
        atr = df['atr'].iloc[-1] if 'atr' in df.columns else current_price * 0.005
        
        # Generate signal
        if predicted_price > current_price * 1.002:  # 0.2% threshold
            signal = {
                'direction': 'BUY',
                'entry_price': current_price,
                'stop_loss': current_price - (atr * 2),
                'take_profit': current_price + (atr * 3),
                'confidence': confidence,
                'predicted_price': predicted_price,
            }
        elif predicted_price < current_price * 0.998:  # 0.2% threshold
            signal = {
                'direction': 'SELL',
                'entry_price': current_price,
                'stop_loss': current_price + (atr * 2),
                'take_profit': current_price - (atr * 3),
                'confidence': confidence,
                'predicted_price': predicted_price,
            }
        else:
            return None
        
        # Track prediction
        self.prediction_history.append({
            'timestamp': datetime.now(),
            'predicted_price': predicted_price,
            'actual_price': current_price,
            'confidence': confidence,
        })
        
        return signal
    
    def update_accuracy(self, actual_price: float, predicted_price: float):
        """Update model accuracy tracking."""
        error = abs(actual_price - predicted_price) / actual_price
        accuracy = max(0, 100 - (error * 100))
        
        self.accuracy_history.append({
            'timestamp': datetime.now(),
            'accuracy': accuracy,
        })
        
        # Keep only last 100 accuracy measurements
        if len(self.accuracy_history) > 100:
            self.accuracy_history = self.accuracy_history[-100:]
    
    def get_average_accuracy(self) -> float:
        """Get average prediction accuracy."""
        if not self.accuracy_history:
            return 0.0
        
        accuracies = [a['accuracy'] for a in self.accuracy_history]
        return sum(accuracies) / len(accuracies)
    
    def load_model(self) -> bool:
        """Load saved model."""
        return self.model.load(self.model_path)
    
    def save_model(self) -> bool:
        """Save current model."""
        return self.model.save(self.model_path)
