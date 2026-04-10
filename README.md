# Telegram bot for Marvel Contest of Champions orders

## Features

- Creates service orders via Telegram dialog
- Opens a styled Telegram Web App mini application
- Stores orders in SQLite
- Sends each order to admins
- Lets admins change order status with inline buttons

## Setup

1. Create and activate a virtual environment
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in:

- `BOT_TOKEN`
- `ADMIN_IDS` as comma-separated Telegram user IDs
- `WEBAPP_URL`
- `WEB_HOST`
- `WEB_PORT`

4. Run the bot:

```bash
python3 main.py
```

The bot runs both Telegram polling and the built-in web server for the mini app.

## User flow

- `/start` shows the main menu with an app button
- User can open the mini app inside Telegram
- User fills in the styled order form
- Bot saves the order and sends it to admins

## Admin flow

- Admin receives each new order
- Admin can change the status to:
  - `new`
  - `in_progress`
  - `done`
  - `canceled`

## Telegram Web App note

For the mini app to open inside Telegram on real devices, `WEBAPP_URL` should be a public HTTPS URL.
For local browser testing, `http://127.0.0.1:8080` is enough.

## Render

This project includes [render.yaml](/Users/erni/Desktop/telegram.bot/render.yaml).

For Render deployment:

- `BOT_TOKEN` = your bot token
- `ADMIN_IDS` = your numeric Telegram ID
- `WEBAPP_URL` = your Render HTTPS URL, for example `https://telegram-mcoc-bot.onrender.com`

`PORT` is provided by Render automatically. The app already supports it.
# MrSmoke.bot
