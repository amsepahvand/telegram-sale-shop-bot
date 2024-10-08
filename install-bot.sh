#!/bin/bash

echo -e "\e[32m

████████  █████  ███    ███       ██████   ██████  ████████ ███████ 
   ██    ██   ██ ████  ████       ██   ██ ██    ██    ██    ██      
   ██    ███████ ██ ████ ██ █████ ██████  ██    ██    ██    ███████ 
   ██    ██   ██ ██  ██  ██       ██   ██ ██    ██    ██         ██ 
   ██    ██   ██ ██      ██       ██████   ██████     ██    ███████ 
                                                                    
\033[0m"

sudo apt-get update

sudo apt-get install -y git

if ! command -v docker &> /dev/null
then
    echo "Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
else
    echo "Docker is already installed."
fi

if ! command -v docker-compose &> /dev/null
then
    echo "Docker Compose is not installed. Installing Docker Compose..."
    sudo apt-get install -y docker-compose
else
    echo "Docker Compose is already installed."
fi

if ! command -v sqlite3 &> /dev/null
then
    echo "sqlite3 is not installed. Installing sqlite3..."
    sudo apt-get install -y sqlite3
else
    echo "sqlite3 is already installed."
fi

 if [ ! -d "telegram-sale-shop-bot" ]; then
     git clone https://github.com/amsepahvand/telegram-sale-shop-bot.git
 fi

cd telegram-sale-shop-bot

read -p "Please enter your Telegram Bot API token: " BOT_API_TOKEN
read -p "Please enter the shop name: " SHOP_NAME
read -p "Please enter the admin username: " ADMIN_USERNAME
read -p "Please enter the admin Telegram user ID: " ADMIN_USER_ID

sqlite3 botdb.db "INSERT INTO bot_api_token (id, api_key) VALUES (1, '$BOT_API_TOKEN');"
sqlite3 botdb.db "INSERT INTO shop_info (shop_name, support_username, phone_number) VALUES ('$SHOP_NAME', '', '');"
sqlite3 botdb.db "INSERT INTO admins_id (username, user_id) VALUES ('$ADMIN_USERNAME', '$ADMIN_USER_ID');"

sudo docker compose up -d

echo "Installation complete! The bot is now running. Enjoy it ;)"

