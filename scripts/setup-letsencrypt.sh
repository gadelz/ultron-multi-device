#!/bin/bash
# Let's Encrypt SSL Setup for Production
# Requires a domain name and port 80 open

set -e

echo "🔐 Let's Encrypt SSL Setup"
echo "=========================="

# Check root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (sudo)"
    exit 1
fi

# Check domain
if [ -z "$1" ]; then
    echo "Usage: $0 your-domain.com"
    echo "Example: $0 ultron.example.com"
    exit 1
fi

DOMAIN=$1
echo "📋 Setting up SSL for: $DOMAIN"
echo ""

# Check if domain resolves
echo "🔍 Checking DNS resolution..."
if ! dig +short "$DOMAIN" | grep -q .; then
    echo "❌ DNS not resolving for $DOMAIN"
    echo "   Please ensure A record points to your server IP"
    exit 1
fi
echo "✅ DNS OK"

# Install certbot
echo ""
echo "📦 Installing certbot..."
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Stop nginx temporarily for certbot
echo ""
echo "⚙️  Stopping nginx..."
systemctl stop nginx

# Get certificate
echo ""
echo "🔑 Requesting certificate..."
certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email admin@"$DOMAIN"

# Start nginx
echo ""
echo "🚀 Starting nginx..."
systemctl start nginx

echo ""
echo "${GREEN}✅ SSL Certificate Installed!${NC}"
echo ""
echo "📊 Certificate details:"
certbot certificates | grep -A 5 "$DOMAIN"
echo ""
echo "🔄 Auto-renewal:"
echo "   Certbot will automatically renew before expiry"
echo "   Test renewal: sudo certbot renew --dry-run"
echo ""
echo "🌐 Your site:"
echo "   https://$DOMAIN"
