#!/bin/bash
# ULTron HTTPS Setup Script
# Generates self-signed SSL certificate and configures nginx

set -e

echo "🔒 ULTron HTTPS Setup"
echo "====================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (sudo)"
    exit 1
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Directories
SSL_DIR="/etc/ssl"
NGINX_CONF="/etc/nginx/sites-available/ultron"
NGINX_ENABLED="/etc/nginx/sites-enabled/ultron"

echo ""
echo "📋 Checking prerequisites..."

# Check nginx
if ! command -v nginx &> /dev/null; then
    echo "${YELLOW}Installing nginx...${NC}"
    apt-get update
    apt-get install -y nginx
fi
echo "✅ nginx installed"

# Check openssl
if ! command -v openssl &> /dev/null; then
    echo "${YELLOW}Installing openssl...${NC}"
    apt-get install -y openssl
fi
echo "✅ openssl installed"

echo ""
echo "🔑 Generating self-signed SSL certificate..."
SSL_CERT="$SSL_DIR/certs/ultron-selfsigned.crt"
SSL_KEY="$SSL_DIR/private/ultron-selfsigned.key"

# Create directories
mkdir -p "$SSL_DIR/certs"
mkdir -p "$SSL_DIR/private"

# Generate certificate (valid for 10 years)
openssl req -x509 -newkey rsa:4096 \
    -keyout "$SSL_KEY" \
    -out "$SSL_CERT" \
    -days 3650 \
    -nodes \
    -subj "/C=ID/ST=Jakarta/L=Jakarta/O=ULTron/OU=IoT/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

chmod 600 "$SSL_KEY"
chmod 644 "$SSL_CERT"
echo "✅ SSL certificate generated"

echo ""
echo "⚙️  Configuring nginx..."
cp config/nginx/ultron.conf "$NGINX_CONF"

# Enable site
ln -sf "$NGINX_CONF" "$NGINX_ENABLED"

# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Test configuration
nginx -t
echo "✅ nginx configuration valid"

echo ""
echo "🚀 Restarting nginx..."
systemctl restart nginx
systemctl enable nginx
echo "✅ nginx started"

echo ""
echo "${GREEN}✅ HTTPS Setup Complete!${NC}"
echo ""
echo "📊 Configuration:"
echo "   HTTP:  http://<your-ip>:80 (redirects to HTTPS)"
echo "   HTTPS: https://<your-ip>:443"
echo ""
echo "🔐 Certificate:"
echo "   Cert: $SSL_CERT"
echo "   Key:  $SSL_KEY"
echo ""
echo "⚠️  Note: This is a self-signed certificate."
echo "   For production, use Let's Encrypt:"
echo "   sudo certbot --nginx -d your-domain.com"
echo ""
echo "📋 Next steps:"
echo "   1. Update .env: ULTRON_GATEWAY=https://your-ip:443"
echo "   2. Configure Tasker/MacroDroid to use HTTPS"
echo "   3. Test: curl -k https://your-ip/health"
