#!/bin/bash

# Update system
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv nginx -y

# Create application directory
sudo mkdir -p /var/www/top50songs
sudo chown -R $USER:$USER /var/www/top50songs

# Copy application files
sudo cp -r * /var/www/top50songs/

# Setup virtual environment
cd /var/www/top50songs
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Setup systemd service
sudo cp top50songs.service /etc/systemd/system/
sudo systemctl start top50songs
sudo systemctl enable top50songs

# Setup Nginx
sudo cp nginx_config /etc/nginx/sites-available/top50songs
sudo ln -s /etc/nginx/sites-available/top50songs /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

# Setup firewall
sudo ufw allow 'Nginx Full'
sudo ufw enable

echo "Deployment completed! Don't forget to:"
echo "1. Update the domain name in /etc/nginx/sites-available/top50songs"
echo "2. Set up SSL with Certbot"
echo "3. Update the SECRET_KEY in the application"
