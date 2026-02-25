# Gold Trading Bot - Deployment Guide

## 🚀 Production Deployment

This guide covers deploying the Gold Trading Bot to production.

## Prerequisites

- Python 3.9+
- pip or conda
- 2GB RAM minimum
- Stable internet connection
- Exchange API credentials (Binance, etc.)

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd trading_bot
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example configuration
cp config.example.json config.json

# Edit configuration
nano config.json  # or use your preferred editor
```

### 5. Set Environment Variables

```bash
export TRADING_BOT_API_KEY=your_api_key
export TRADING_BOT_API_SECRET=your_api_secret
export TRADING_BOT_EXCHANGE=binance
export TRADING_BOT_SYMBOL=XAUUSD
```

## Configuration

### config.json Structure

```json
{
  "risk": {
    "max_position_size_percent": 2.0,
    "max_concurrent_positions": 5,
    "max_drawdown_percent": 20.0,
    "daily_loss_limit_percent": 5.0,
    "risk_per_trade_percent": 1.0,
    "kelly_fraction": 0.25
  },
  "strategy": {
    "technical_enabled": true,
    "lstm_enabled": true,
    "dqn_enabled": true,
    "confirmation_threshold": 2,
    "high_volatility_threshold": 2.0,
    "high_volatility_confirmation": 3
  },
  "exchange": {
    "exchange": "binance",
    "symbol": "XAUUSD",
    "timeframe": "2m",
    "sandbox_mode": true
  }
}
```

## Running the Bot

### Option 1: Command Line

```bash
python -c "from trading_bot.bot import TradingBot; bot = TradingBot(); bot.start()"
```

### Option 2: Python Script

Create `run_bot.py`:

```python
from trading_bot.bot import TradingBot
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize and start bot
bot = TradingBot("config.json")
bot.start()
```

Run with:

```bash
python run_bot.py
```

### Option 3: With GUI

```python
from trading_bot.bot import TradingBot
from trading_bot.gui.dashboard import TradingDashboard

# Initialize bot
bot = TradingBot("config.json")

# Create dashboard
dashboard = TradingDashboard(bot)
dashboard.show()

# Start bot in background
bot.start()
```

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "run_bot.py"]
```

### 2. Build Image

```bash
docker build -t trading-bot:latest .
```

### 3. Run Container

```bash
docker run -d \
  -e TRADING_BOT_API_KEY=your_key \
  -e TRADING_BOT_API_SECRET=your_secret \
  -v $(pwd)/config.json:/app/config.json \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/trading_bot.db:/app/trading_bot.db \
  trading-bot:latest
```

## Systemd Service (Linux)

### 1. Create Service File

Create `/etc/systemd/system/trading-bot.service`:

```ini
[Unit]
Description=Gold Trading Bot
After=network.target

[Service]
Type=simple
User=trading
WorkingDirectory=/home/trading/trading_bot
Environment="TRADING_BOT_API_KEY=your_key"
Environment="TRADING_BOT_API_SECRET=your_secret"
ExecStart=/home/trading/trading_bot/venv/bin/python run_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot

# Check status
sudo systemctl status trading-bot

# View logs
sudo journalctl -u trading-bot -f
```

## Monitoring

### 1. Check Bot Status

```bash
# View logs
tail -f logs/trading_bot.json

# Parse JSON logs
cat logs/trading_bot.json | jq '.message'
```

### 2. Database Monitoring

```python
from trading_bot.core.database import DatabaseManager

db = DatabaseManager()

# Get recent trades
trades = db.get_trade_history(limit=10)
for trade in trades:
    print(f"Trade: {trade['pnl']:.2f}")

# Get open positions
positions = db.get_open_positions()
print(f"Open positions: {len(positions)}")
```

### 3. Performance Monitoring

```bash
# Monitor CPU and memory
top -p $(pgrep -f "python run_bot.py")

# Monitor network
netstat -an | grep ESTABLISHED
```

## Backup & Recovery

### 1. Backup Database

```bash
# Manual backup
cp trading_bot.db trading_bot_backup_$(date +%Y%m%d_%H%M%S).db

# Automated backup (cron)
0 */6 * * * cp /path/to/trading_bot.db /path/to/backups/trading_bot_$(date +\%Y\%m\%d_\%H\%M\%S).db
```

### 2. Restore Database

```python
from trading_bot.core.database import DatabaseManager

db = DatabaseManager()
db.restore_database("trading_bot_backup.db")
```

### 3. Backup Configuration

```bash
cp config.json config_backup_$(date +%Y%m%d_%H%M%S).json
```

## Troubleshooting

### Issue: Connection Timeout

**Solution:**
- Check internet connection
- Verify API credentials
- Check firewall settings
- Increase timeout in config

### Issue: Insufficient Data

**Solution:**
- Ensure at least 50 candles available
- Check symbol spelling
- Verify exchange supports symbol
- Wait for more data to accumulate

### Issue: High CPU Usage

**Solution:**
- Reduce indicator calculation frequency
- Increase cache TTL
- Reduce number of concurrent positions
- Use lower timeframe

### Issue: Database Locked

**Solution:**
- Stop bot
- Check for other processes using database
- Restore from backup if corrupted
- Restart bot

## Performance Optimization

### 1. Indicator Calculation

```python
# Cache indicators
from trading_bot.market.cache import DataCache

cache = DataCache(ttl_minutes=60)
```

### 2. Database Queries

```python
# Use indexed queries
trades = db.get_trade_history(
    start_date=datetime(2024, 1, 1),
    limit=1000,
)
```

### 3. Memory Management

```python
# Monitor memory usage
import psutil
process = psutil.Process()
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

## Security Best Practices

### 1. API Credentials

```bash
# Use environment variables (never hardcode)
export TRADING_BOT_API_KEY=your_key
export TRADING_BOT_API_SECRET=your_secret

# Use .env file (add to .gitignore)
echo "TRADING_BOT_API_KEY=your_key" > .env
```

### 2. Database Security

```bash
# Restrict database file permissions
chmod 600 trading_bot.db

# Encrypt sensitive data
# Use database encryption if available
```

### 3. Network Security

```bash
# Use VPN for API connections
# Enable firewall rules
# Use HTTPS only
```

## Maintenance Schedule

### Daily
- Monitor logs for errors
- Check bot status
- Verify positions are open

### Weekly
- Review performance metrics
- Check database size
- Backup database

### Monthly
- Optimize parameters
- Retrain ML models
- Review strategy performance
- Update dependencies

## Scaling

### Multiple Bots

```python
# Run multiple bots for different symbols
bots = []
for symbol in ['XAUUSD', 'EURUSD', 'GBPUSD']:
    config = ConfigManager()
    config.exchange.symbol = symbol
    bot = TradingBot()
    bots.append(bot)
    bot.start()
```

### Load Balancing

```bash
# Use nginx for load balancing
# Distribute API calls across multiple servers
# Use message queue for order execution
```

## Monitoring & Alerting

### 1. Email Alerts

```python
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your_email@gmail.com', 'your_password')
        server.send_message(msg)
```

### 2. Slack Notifications

```python
import requests

def send_slack_message(message):
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    requests.post(webhook_url, json={"text": message})
```

### 3. Prometheus Metrics

```python
from prometheus_client import Counter, Gauge

trades_counter = Counter('trades_total', 'Total trades')
pnl_gauge = Gauge('pnl_current', 'Current P&L')
```

## Support & Maintenance

- Check logs in `logs/` directory
- Review database in `trading_bot.db`
- Monitor performance metrics
- Update dependencies regularly
- Test changes on demo account first

## Rollback Procedure

```bash
# Stop bot
sudo systemctl stop trading-bot

# Restore previous version
git checkout previous_version

# Restore database backup
cp trading_bot_backup.db trading_bot.db

# Restart bot
sudo systemctl start trading-bot
```

## Conclusion

The Gold Trading Bot is now ready for production deployment. Follow this guide for:
- Secure installation
- Proper configuration
- Reliable operation
- Effective monitoring
- Quick recovery

For issues or questions, refer to the logs and documentation.

---

**Happy Trading! 🚀**
