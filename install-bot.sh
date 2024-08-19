#!/bin/bash
sudo apt-get install figlet
figlet TAM-Bots

sudo apt-get update
sudo apt-get install -y git

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
rm get-docker.sh

sudo apt-get install -y docker-compose

git clone https://github.com/amsepahvand/telegram-sale-shop-bot.git

cd telegram-sale-shop-bot

sudo docker-compose up -d

echo "Installation complete! The bot is now running , Enjoy it ;)"



