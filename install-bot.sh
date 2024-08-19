#!/bin/bash

# Update package lists and install git
sudo apt-get update
sudo apt-get install -y git curl

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
sudo apt-get install -y docker-compose

# Clone the project repository
REPO_DIR="telegram-sale-shop-bot"
if [ -d "$REPO_DIR" ]; then
    echo "Project directory already exists. Updating repository..."
    cd $REPO_DIR
    git pull origin main
else
    git clone https://github.com/amsepahvand/telegram-sale-shop-bot.git
    cd $REPO_DIR
fi

# Check if requirements.txt exists and replace if a new one is provided
if [ -f "requirements.txt" ]; then
    echo "requirements.txt found. Replacing with new one..."
    rm requirements.txt
    cp /path/to/new/requirements.txt requirements.txt
else
    echo "requirements.txt not found. Adding new one..."
    cp /path/to/new/requirements.txt requirements.txt
fi

# Run Docker Compose to start the containers
sudo docker-compose up -d

echo "Installation complete! The bot is now running, Enjoy it ;)"

