# آموزش ایجنت یادگیری تقویتی
import pandas as pd
import numpy as np
from rl_strategy import DQNAgent, TradingEnvironment
from market_data import MarketDataProvider
import matplotlib.pyplot as plt

def prepare_data(df):
    """آماده‌سازی داده‌ها"""
    # محاسبه اندیکاتورها
    df['ema_fast'] = df['close'].ewm(span=5, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=13, adjust=False).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # حذف NaN
    df = df.dropna()
    
    return df

def train_agent(episodes=100):
    """آموزش ایجنت"""
    print("="*60)
    print("🤖 شروع آموزش ایجنت یادگیری تقویتی")
    print("="*60)
    
    # دریافت داده‌های واقعی
    print("📊 دریافت داده‌های تاریخی...")
    provider = MarketDataProvider('binance')
    df = provider.get_ohlcv(limit=1000)
    
    if df is None or len(df) < 100:
        print("❌ داده کافی دریافت نشد")
        return
    
    # آماده‌سازی
    df = prepare_data(df)
    print(f"✅ {len(df)} کندل آماده شد")
    
    # ساخت محیط و ایجنت
    env = TradingEnvironment(df, initial_balance=100)
    agent = DQNAgent(state_size=8, action_size=3)
    
    # آموزش
    episode_rewards = []
    episode_profits = []
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        done = False
        step = 0
        
        while not done and state is not None:
            # انتخاب اکشن
            action = agent.act(state, training=True)
            
            # اجرای اکشن
            next_state, reward, done, info = env.step(action)
            
            # ذخیره در حافظه
            agent.remember(state, action, reward, next_state, done)
            
            # آموزش
            if len(agent.memory) > agent.batch_size:
                loss = agent.replay()
            
            state = next_state
            total_reward += reward
            step += 1
        
        # به‌روزرسانی مدل هدف
        if episode % 10 == 0:
            agent.update_target_model()
        
        episode_rewards.append(total_reward)
        episode_profits.append(env.total_profit)
        
        # نمایش پیشرفت
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(episode_rewards[-10:])
            avg_profit = np.mean(episode_profits[-10:])
            print(f"Episode {episode + 1}/{episodes} | "
                  f"Avg Reward: {avg_reward:.2f} | "
                  f"Avg Profit: ${avg_profit:.2f} | "
                  f"Epsilon: {agent.epsilon:.3f} | "
                  f"Trades: {len(env.trades)}")
    
    # ذخیره مدل
    agent.save()
    
    # نمایش نتایج
    print("\n" + "="*60)
    print("📊 نتایج آموزش")
    print("="*60)
    print(f"میانگین پاداش: {np.mean(episode_rewards):.2f}")
    print(f"میانگین سود: ${np.mean(episode_profits):.2f}")
    print(f"بهترین سود: ${max(episode_profits):.2f}")
    
    # رسم نمودار
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(episode_rewards)
    plt.title('Episode Rewards')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(episode_profits)
    plt.title('Episode Profits')
    plt.xlabel('Episode')
    plt.ylabel('Profit ($)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('training_results.png')
    print("\n📈 نمودار نتایج در training_results.png ذخیره شد")
    
    return agent

def test_agent(agent, test_episodes=10):
    """تست ایجنت"""
    print("\n" + "="*60)
    print("🧪 تست ایجنت")
    print("="*60)
    
    provider = MarketDataProvider('binance')
    df = provider.get_ohlcv(limit=500)
    df = prepare_data(df)
    
    env = TradingEnvironment(df, initial_balance=100)
    
    test_profits = []
    
    for episode in range(test_episodes):
        state = env.reset()
        done = False
        
        while not done and state is not None:
            action = agent.act(state, training=False)
            next_state, reward, done, info = env.step(action)
            state = next_state
        
        test_profits.append(env.total_profit)
        print(f"Test {episode + 1}: Profit = ${env.total_profit:.2f}, "
              f"Trades = {len(env.trades)}, "
              f"Win Rate = {sum(1 for t in env.trades if t['profit'] > 0) / max(len(env.trades), 1) * 100:.1f}%")
    
    print(f"\n📊 میانگین سود در تست: ${np.mean(test_profits):.2f}")

if __name__ == "__main__":
    # آموزش
    agent = train_agent(episodes=100)
    
    # تست
    if agent:
        test_agent(agent, test_episodes=5)
