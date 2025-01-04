#!/bin/bash

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create directories for SSL certificates
mkdir -p certbot/conf certbot/www

# Update environment variables
read -p "Enter your domain (e.g., example.com): " DOMAIN
read -p "Enter your email: " EMAIL
read -p "Enter a secure secret key (or press enter to generate one): " SECRET_KEY

if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -hex 32)
fi

# Update configuration files
sed -i "s/yourdomain.com/$DOMAIN/g" docker-compose.yml nginx.conf
sed -i "s/your@email.com/$EMAIL/g" docker-compose.yml
sed -i "s/your-secret-key-change-this/$SECRET_KEY/g" docker-compose.yml

# Start the application
docker-compose up -d

echo "Deployment completed!"
echo "Your application is now running at https://$DOMAIN"
echo "Please wait a few minutes for SSL certificate to be generated"
echo ""
echo "Default admin credentials:"
echo "Username: admin"
echo "Password: admin123"
echo ""
echo "IMPORTANT: Change the admin password immediately after first login!"
