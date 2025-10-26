# autobuy
easy to use telegram gift snipper script
### Features

- Fast automated gift sniping on Telegram
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
   git clone https://github.com/yourusername/autobuy.git
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
  docker run --name autobuy -v .env:/app/autobuy/.env:ro -v sessions:/app/autobuy/sessions:rw -it touchmeangel/autobuy:latest python main.py --check-every 4 --max-supply 100000 --star-amount 5000
```
Or using Python
```bash
  pip install -r requirements.txt
  python main.py --check-every 4 --max-supply 100000 --star-amount 5000
```
### Contribution
Contributions are welcome! Please feel free to submit a Pull Request.