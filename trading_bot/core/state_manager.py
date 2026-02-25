"""State persistence for crash recovery."""

import json
import pickle
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class StateManager:
    """Manages system state persistence for crash recovery."""
    
    def __init__(self, state_dir: str = "state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "system_state.json"
        self.positions_file = self.state_dir / "positions.json"
        self.last_save_time = None
    
    def save_state(
        self,
        positions: List[Dict[str, Any]],
        open_orders: List[Dict[str, Any]],
        metrics: Dict[str, Any],
    ) -> bool:
        """
        Save system state to persistent storage.
        
        Args:
            positions: List of open positions
            open_orders: List of open orders
            metrics: Current performance metrics
        
        Returns:
            True if save successful
        """
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'positions': positions,
                'open_orders': open_orders,
                'metrics': metrics,
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            
            self.last_save_time = datetime.now()
            logger.debug(f"State saved: {len(positions)} positions, {len(open_orders)} orders")
            return True
        except Exception as e:
            logger.error(f"Error saving state: {e}")
            return False
    
    def load_state(self) -> Optional[Dict[str, Any]]:
        """
        Load system state from persistent storage.
        
        Returns:
            State dictionary or None if not found
        """
        try:
            if not self.state_file.exists():
                logger.info("No saved state found")
                return None
            
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            logger.info(
                f"State loaded: {len(state.get('positions', []))} positions, "
                f"{len(state.get('open_orders', []))} orders"
            )
            return state
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return None
    
    def save_positions(self, positions: List[Dict[str, Any]]) -> bool:
        """Save open positions separately."""
        try:
            with open(self.positions_file, 'w') as f:
                json.dump(positions, f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Error saving positions: {e}")
            return False
    
    def load_positions(self) -> List[Dict[str, Any]]:
        """Load saved positions."""
        try:
            if not self.positions_file.exists():
                return []
            
            with open(self.positions_file, 'r') as f:
                positions = json.load(f)
            
            return positions
        except Exception as e:
            logger.error(f"Error loading positions: {e}")
            return []
    
    def verify_state_consistency(
        self,
        saved_state: Dict[str, Any],
        current_positions: List[Dict[str, Any]],
    ) -> bool:
        """
        Verify consistency between saved and current state.
        
        Args:
            saved_state: Previously saved state
            current_positions: Current open positions
        
        Returns:
            True if consistent
        """
        if not saved_state:
            return True
        
        saved_positions = saved_state.get('positions', [])
        saved_ids = {p.get('id') for p in saved_positions}
        current_ids = {p.get('id') for p in current_positions}
        
        # Check for missing positions
        missing = saved_ids - current_ids
        if missing:
            logger.warning(f"Missing positions after recovery: {missing}")
        
        # Check for new positions
        new = current_ids - saved_ids
        if new:
            logger.info(f"New positions created: {new}")
        
        # Verify position details
        for saved_pos in saved_positions:
            pos_id = saved_pos.get('id')
            current_pos = next(
                (p for p in current_positions if p.get('id') == pos_id),
                None
            )
            
            if current_pos:
                # Check entry price consistency
                if abs(saved_pos.get('entry_price', 0) - current_pos.get('entry_price', 0)) > 0.01:
                    logger.warning(
                        f"Position {pos_id} entry price mismatch: "
                        f"saved={saved_pos.get('entry_price')}, "
                        f"current={current_pos.get('entry_price')}"
                    )
        
        return True
    
    def clear_state(self) -> bool:
        """Clear saved state."""
        try:
            if self.state_file.exists():
                self.state_file.unlink()
            if self.positions_file.exists():
                self.positions_file.unlink()
            logger.info("State cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing state: {e}")
            return False
    
    def get_state_age(self) -> Optional[float]:
        """Get age of saved state in seconds."""
        try:
            if not self.state_file.exists():
                return None
            
            file_time = datetime.fromtimestamp(self.state_file.stat().st_mtime)
            age = (datetime.now() - file_time).total_seconds()
            return age
        except Exception as e:
            logger.error(f"Error getting state age: {e}")
            return None
