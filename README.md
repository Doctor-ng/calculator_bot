🤖 Crypto Calculator Telegram Bot

A powerful Telegram bot that supports:

- 🧮 Math calculations
- 📊 Percentage calculations
- 🪙 Crypto price (USD + INR)
- 📈 Charts (TradingView)
- 🔔 Price alerts
- 🔍 Inline Search Mode
- 🏆 Calculation leaderboard
- 📢 Admin broadcast system
_________________________________
https://t.me/KaIcuIator_Bot
___________________________________

📦 Requirements

- Python 3.10+
- VPS (Ubuntu recommended)
- Telegram Bot Token
______________________________

Install dependencies:

pip install -r requirements.txt
__________________________________________

⚙️ Configuration

Create a "config.py" file:

BOT_TOKEN = "YOUR_BOT_TOKEN"
COINGECKO_API_KEY = "YOUR_API_KEY"
ADMIN_ID = YOUR_TELEGRAM_ID
DB_FILE = "bot.db"
CACHE_TTL = 60

CHANNEL_LINKS = [
    "https://t.me/Doc_Tools"
]

🏆 Leaderboard

Use `/leaderboard` or `/lb` to show the top users by successful math and crypto calculations.

▶️ Run Bot

python main.py
_______________________

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
