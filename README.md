# Telegram Auto-Buy/Gift Snipper Bot
A lightweight and flexible Telegram userbot for automated purchase of gifts.
### Features

- Fast automated gift sniping on Telegram
- <b>Userbot-driven flow</b> Authenticate via your API_ID, API_HASH, and either .session file or session string for easy setup.
- Real-time monitoring of gift availability
- Notification system for successful purchases
- Rate limiting to avoid detection
- Detailed logging of all operations
- Easy configuration through environment variables
### Prerequisites
Before you begin, ensure you have the following installed:

- Python 3.8 or Docker
- pip (Python package installer)
- A Telegram account
- Telegram API credentials (API ID and API Hash)
### Getting Telegram API Credentials

1. Visit my.telegram.org
2. Log in with your phone number
3. Navigate to "API development tools"
4. Create a new application
5. Copy your api_id and api_hash
### Installation
1. Clone the repository
```bash
   git clone https://github.com/touchmeangel/autobuy.git
   cd autobuy
```
2. Set up configuration. Create a .env file in the root directory:
```
  TG_API_ID=your_api_id
  TG_API_HASH=your_api_hash
  LOGGER_TOKEN=your_bot_token
  LOGGER_CHAT_ID=your_chat_id
```
### Usage
```bash
  docker compose run --rm --build -Pit autobuy python main.py --check-every 4 --max-supply 100000 --star-amount 5000
```
Or using Python
```bash
  pip install -r requirements.txt
  python main.py --check-every 4 --max-supply 100000 --star-amount 5000
```
### Optional Flags
- --id: Target a specific gift by unique ID.
- --title: Match a gift’s title exactly (case-sensitive).
- -n / --nullable-title: Allow gifts without a title to pass filter if no title is present.
- --min-price, --max-price: Filter by exact or range of prices (in TGStars).
- --min-supply, --max-supply: Filter by supply range
- --total-amount: Match listings with a specific total supply.
- --check-every: Polling interval in seconds (defaults to 60 s).
- --amount: Number of gifts to attempt to buy on match (defaults to 1).
### Contribution
Contributions are welcome! Please feel free to submit a Pull Request.