# Telegram Announcement Bot

This Telegram bot fetches and manages announcements from a specified API, allowing users to view, like, and dislike announcements directly through Telegram interactions.

## Technology Stack

- Python
- Python-telegram-bot library
- Requests library
- dotenv for environment variable management

## Features

- Fetch and display announcements with pagination.
- Respond to user inputs via custom Telegram commands and inline buttons.
- Allow users to like or dislike announcements.
- Error handling for API communication.

## Setup Instructions

### Requirements

Ensure you have Python installed on your system. This bot is tested with Python 3.9.5.

### Creating Virtual Environment

```bash
python3 -m venv myprojectenv
```

### Activating the Virtual Environment

```bash
source myprojectenv/bin/activate
```

### Installing Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory and add your Telegram bot token & API_IP for sending requests:

```plaintext
YOUR_TELEGRAM_BOT_TOKEN='your_telegram_bot_token_here'
API_IP = 'your_api_ip'
```

### Running the Bot

To run the bot, use the following command:

```bash
python bot.py
```

This will start the bot, and it should be live on Telegram ready to interact with users.

## Bot Commands and Interactions

- `/start` - Initializes the bot and presents a welcome message along with an option to fetch new messages.
- Inline buttons for navigating through announcements, liking, and disliking posts.
- Real-time updates to user interactions to reflect like and dislike counts.

## Deployment

The bot is designed to be deployed on platforms like DigitalOcean, which supports worker-based applications. Ensure you configure the environment variables on your deployment platform to match those expected by the `.env` file.

## Logging

Logging is configured to output bot activity, which helps in monitoring interactions and debugging issues.

## Security Considerations

Ensure that the API endpoints used are secured and validate all incoming requests to the bot for authenticity and integrity.

---

Feel free to fork or contribute to this project to enhance its capabilities or improve its performance.
