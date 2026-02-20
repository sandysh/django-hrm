#!/bin/bash

# HRM Application Quick Start Script
# This script helps you get the HRM application up and running quickly

set -e

echo "========================================="
echo "HRM Application Quick Start"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker Compose is available (either as plugin or standalone)
if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not available${NC}"
    echo "Please install Docker Compose"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed${NC}"
echo -e "${GREEN}✓ Docker Compose is available${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo ""
    echo -e "${YELLOW}IMPORTANT: Please update the BIOMETRIC_DEVICE_IP in .env file${NC}"
    echo "Current IP: 192.168.1.201"
    echo ""
    read -p "Enter your biometric device IP address (or press Enter to use default): " device_ip
    
    if [ ! -z "$device_ip" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/BIOMETRIC_DEVICE_IP=.*/BIOMETRIC_DEVICE_IP=$device_ip/" .env
        else
            sed -i "s/BIOMETRIC_DEVICE_IP=.*/BIOMETRIC_DEVICE_IP=$device_ip/" .env
        fi
        echo -e "${GREEN}✓ Updated device IP to $device_ip${NC}"
    fi
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""
echo "Building Docker images..."
docker compose build

echo ""
echo "Starting services..."
docker compose up -d

echo ""
echo "Waiting for database to be ready..."
sleep 10

echo ""
echo "Running database migrations..."
docker compose exec -T web python manage.py migrate

echo ""
echo "Initializing HRM system with default data..."
docker compose exec -T web python manage.py init_hrm

echo ""
echo -e "${YELLOW}Creating superuser account...${NC}"
echo "Please provide the following information:"
docker compose exec web python manage.py createsuperuser

echo ""
echo "========================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "========================================="
echo ""
echo "Your HRM application is now running!"
echo ""
echo "Access the application at:"
echo "  - Admin Panel: http://localhost:8000/admin"
echo "  - API Root: http://localhost:8000/api/"
echo ""
echo "Useful commands:"
echo "  - View logs: docker compose logs -f"
echo "  - Stop services: docker compose down"
echo "  - Restart services: docker compose restart"
echo ""
echo "Next steps:"
echo "  1. Login to admin panel with your superuser credentials"
echo "  2. Test biometric device connection"
echo "  3. Create your first employee"
echo "  4. Check the SETUP_GUIDE.md for detailed instructions"
echo ""
echo -e "${YELLOW}Note: Make sure your biometric device is accessible at the configured IP address${NC}"
echo ""
