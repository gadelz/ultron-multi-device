#!/bin/bash
# ULTron Firewall Setup Script
# Configures UFW firewall rules for secure access

set -e

echo "🛡️  ULTron Firewall Setup"
echo "========================="

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

echo ""
echo "📋 Current firewall status..."
ufw status verbose || echo "UFW not installed"

echo ""
echo "🔧 Installing UFW..."
apt-get update
apt-get install -y ufw
echo "✅ UFW installed"

echo ""
echo "🚫 Setting default policies (deny all incoming, allow all outgoing)..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
echo "✅ Default policies set"

# Get local network interface and subnet
echo ""
echo "🌐 Detecting network configuration..."
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "   Local IP: $LOCAL_IP"

# Detect subnet (assume /24 for home network)
if [[ "$LOCAL_IP" == 192.168.* ]]; then
    SUBNET="192.168.0.0/16"
elif [[ "$LOCAL_IP" == 10.* ]]; then
    SUBNET="10.0.0.0/8"
else
    SUBNET="192.168.1.0/24"
fi
echo "   Network subnet: $SUBNET"

echo ""
echo "📝 Adding firewall rules..."

# Allow SSH (important!)
ufw allow 22/tcp comment 'Allow SSH'
echo "   ✅ SSH (port 22)"

# Allow HTTP (redirect to HTTPS)
ufw allow 80/tcp comment 'Allow HTTP'
echo "   ✅ HTTP (port 80)"

# Allow HTTPS
ufw allow 443/tcp comment 'Allow HTTPS'
echo "   ✅ HTTPS (port 443)"

# Allow ULTron Gateway (internal only)
ufw allow from $SUBNET to any port 8080 comment 'Allow ULTron Gateway from LAN'
echo "   ✅ ULTron Gateway port 8080 (LAN only)"

# Allow Tasker ports (internal only)
ufw allow from $SUBNET to any port 1820 comment 'Allow Tasker HTTP'
ufw allow from $SUBNET to any port 1880 comment 'Allow MacroDroid HTTP'
echo "   ✅ Tasker/MacroDroid ports (LAN only)"

echo ""
echo "🚀 Enabling firewall..."
ufw --force enable
echo "✅ Firewall enabled"

echo ""
echo "📊 Final firewall status..."
ufw status verbose

echo ""
echo "${GREEN}✅ Firewall Setup Complete!${NC}"
echo ""
echo "🔒 Security summary:"
echo "   - All incoming connections blocked by default"
echo "   - Only necessary ports open (22, 80, 443, 8080, 1820, 1880)"
echo "   - Gateway ports restricted to local network ($SUBNET)"
echo "   - SSH access preserved"
echo ""
echo "⚠️  Important:"
echo "   - Keep this terminal open until you verify SSH access"
echo "   - If you lose connection, SSH might be blocked"
echo "   - To revert: sudo ufw disable"
echo ""
echo "📋 Test connectivity:"
echo "   From another device on same network:"
echo "   curl https://$LOCAL_IP/health"
echo "   curl https://$LOCAL_IP/device/register"
