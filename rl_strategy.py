# استراتژی یادگیری تقویتی با PyTorch
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from collections import deque
import random
import os

class TradingEnvironment:
    """محیط معاملاتی برای آموزش"""
    
    def __init__(self, data, initial_balance=100, commission=0.001):
        self.data = data
        self.initial_balance = initial_balance
        self.commission = commission
        self.reset()
    
    def reset(self):
        """ریست محیط"""
        self.balance = self.initial_balance
        self.position = 0  # 0: خنثی, 1: خرید, -1: فروش
        self.entry_price = 0
        self.current_step = 0
        self.total_profit = 0
        self.trades = []
        return self._get_state()
    
    def _get_state(self):
        """دریافت وضعیت فعلی"""
        if self.current_step >= len(self.data) - 1:
            return None
        
        # ویژگی‌های تکنیکال
        row = self.data.iloc[self.current_step]
        
        state = [
            row['close'] / 10000,  # نرمال‌سازی قیمت
            row['volume'] / 1000,
            row.get('rsi', 50) / 100,
            row.get('ema_fast', row['close']) / 10000,
            row.get('ema_slow', row['close']) / 10000,
            self.position,
            self.balance / self.initial_balance,
            (row['close'] - self.entry_price) / 100 if self.entry_price > 0 else 0
        ]
        
        return np.array(state, dtype=np.float32)
    
    def step(self, action):
        """اجرای یک اکشن"""
        # action: 0=نگه‌داری, 1=خرید, 2=فروش
        
        if self.current_step >= len(self.data) - 1:
            return None, 0, True, {}
        
        current_price = self.data.iloc[self.current_step]['close']
        reward = 0
        
        # اجرای اکشن
        if action == 1 and self.position == 0:  # خرید
            self.position = 1
            self.entry_price = current_price
            cost = current_price * self.commission
            self.balance -= cost
            
        elif action == 2 and self.position == 1:  # فروش
            profit = current_price - self.entry_price
            profit_pct = (profit / self.entry_price) * 100
            
            # محاسبه پاداش
            reward = profit_pct * 10  # تقویت سود
            
            # کمیسیون
            cost = current_price * self.commission
            self.balance += profit - cost
            
            self.total_profit += profit
            self.trades.append({
                'entry': self.entry_price,
                'exit': current_price,
                'profit': profit,
                'profit_pct': profit_pct
            })
            
            self.position = 0
            self.entry_price = 0
        
        # جریمه برای نگه‌داشتن پوزیشن زیان‌ده
        if self.position == 1 and current_price < self.entry_price:
            loss_pct = ((self.entry_price - current_price) / self.entry_price) * 100
            reward = -loss_pct * 5  # جریمه زیان
        
        # حرکت به مرحله بعد
        self.current_step += 1
        next_state = self._get_state()
        done = self.current_step >= len(self.data) - 1
        
        info = {
            'balance': self.balance,
            'position': self.position,
            'total_profit': self.total_profit
        }
        
        return next_state, reward, done, info

class DQNNetwork(nn.Module):
    """شبکه عصبی DQN"""
    
    def __init__(self, state_size, action_size):
        super(DQNNetwork, self).__init__()
        
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, action_size)
        
        self.dropout = nn.Dropout(0.2)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = torch.relu(self.fc2(x))
        x = self.dropout(x)
        x = torch.relu(self.fc3(x))
        x = self.fc4(x)
        return x

class DQNAgent:
    """ایجنت DQN برای معاملات"""
    
    def __init__(self, state_size=8, action_size=3):
        self.state_size = state_size
        self.action_size = action_size
        
        # هایپرپارامترها
        self.gamma = 0.95  # discount factor
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.batch_size = 32
        
        # حافظه
        self.memory = deque(maxlen=2000)
        
        # شبکه‌ها
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = DQNNetwork(state_size, action_size).to(self.device)
        self.target_model = DQNNetwork(state_size, action_size).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()
        
        self.update_target_model()
    
    def update_target_model(self):
        """به‌روزرسانی مدل هدف"""
        self.target_model.load_state_dict(self.model.state_dict())
    
    def remember(self, state, action, reward, next_state, done):
        """ذخیره در حافظه"""
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state, training=True):
        """انتخاب اکشن"""
        if training and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.model(state)
        return q_values.argmax().item()
    
    def replay(self):
        """آموزش از حافظه"""
        if len(self.memory) < self.batch_size:
            return 0
        
        minibatch = random.sample(self.memory, self.batch_size)
        
        states = torch.FloatTensor([t[0] for t in minibatch]).to(self.device)
        actions = torch.LongTensor([t[1] for t in minibatch]).to(self.device)
        rewards = torch.FloatTensor([t[2] for t in minibatch]).to(self.device)
        next_states = torch.FloatTensor([t[3] if t[3] is not None else np.zeros(self.state_size) 
                                         for t in minibatch]).to(self.device)
        dones = torch.FloatTensor([t[4] for t in minibatch]).to(self.device)
        
        # محاسبه Q values
        current_q = self.model(states).gather(1, actions.unsqueeze(1))
        
        with torch.no_grad():
            next_q = self.target_model(next_states).max(1)[0]
            target_q = rewards + (1 - dones) * self.gamma * next_q
        
        # محاسبه loss
        loss = self.criterion(current_q.squeeze(), target_q)
        
        # بهینه‌سازی
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # کاهش epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return loss.item()
    
    def save(self, path='models/dqn_agent.pth'):
        """ذخیره مدل"""
        os.makedirs('models', exist_ok=True)
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'target_model_state_dict': self.target_model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon
        }, path)
        print(f"💾 مدل ذخیره شد: {path}")
    
    def load(self, path='models/dqn_agent.pth'):
        """بارگذاری مدل"""
        if os.path.exists(path):
            checkpoint = torch.load(path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.target_model.load_state_dict(checkpoint['target_model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.epsilon = checkpoint['epsilon']
            print(f"✅ مدل بارگذاری شد: {path}")
            return True
        return False
