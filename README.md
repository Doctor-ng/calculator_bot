🤖 Crypto Calculator Telegram Bot

A powerful Telegram bot that supports:

- 🧮 Math calculations
- 📊 Percentage calculations
- 🪙 Crypto price (USD + INR)
- 📈 Charts (TradingView)
- 🔔 Price alerts
- 📢 Admin broadcast system


🚀 Features

🧮 Math

- "2+2"
- "(5*6)/2"
- "2²", "3³"

📊 Percentage

- "25% of 500"
- "25 is % of 500"
- "500 ↑ 10%"
- "500 ↓ 10%"

🪙 Crypto

- "1 btc"
- "2 eth"
- "/p btc" → full details

📈 Charts

- TradingView chart button
- Supports almost all coins

🔔 Alerts

- "/alert btc 70000"
- "/myalerts"

📢 Admin

- Broadcast to users/groups
- Restart bot

---

📦 Requirements

- Python 3.10+
- VPS (Ubuntu recommended)
- Telegram Bot Token

Install dependencies:

pip install -r requirements.txt

---

⚙️ Configuration

Create a "config.py" file:

BOT_TOKEN = "YOUR_BOT_TOKEN"
COINGECKO_API_KEY = "YOUR_API_KEY"
ADMIN_ID = YOUR_TELEGRAM_ID
DB_FILE = "bot.db"
CACHE_TTL = 60

CHANNEL_LINKS = [
    "https://t.me/your_channel"
]

▶️ Run Bot

python main.py


⚙️ Run with systemd (Auto start)

Create service file:

sudo nano /etc/systemd/system/calcbot.service

Paste:

[Unit]
Description=Calc Telegram Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/bots/calculator_bot
ExecStart=/home/ubuntu/bots/calculator_bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target

Then run:

sudo systemctl daemon-reload
sudo systemctl enable calcbot
sudo systemctl start calcbot
___________________________________

📁 Project Structure

calculator_bot/
│
├── handlers/
├── services/
├── config.py
├── main.py
├── bot.db
└── requirements.txt
___________________________

👨‍💻 Developer

Made by Doctor-ng

⭐ Support

If you like this project:

- Star ⭐ the repo
- Share with friends
- Contribute improvements
