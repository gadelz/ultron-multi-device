#!/bin/bash
# Complete ULTron Security Setup
# Runs HTTPS + Firewall configuration

set -e

echo "🔐 ULTron Complete Security Setup"
echo "================================="
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (sudo ./setup-security.sh)"
    exit 1
fi

echo "📋 This script will:"
echo "   1. Generate SSL certificate"
echo "   2. Configure nginx reverse proxy"
echo "   3. Set up UFW firewall"
echo "   4. Verify configuration"
echo ""
echo "⚠️  WARNING: This will block all incoming connections except allowed ports"
echo ""
read -p "Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Setup cancelled"
    exit 0
fi

echo ""
echo "🚀 Starting security setup..."
echo ""

# Step 1: HTTPS Setup
echo "━━━ Step 1/2: HTTPS Setup ━━━"
bash "$(dirname "$0")/setup-https.sh"
echo ""

# Step 2: Firewall Setup
echo "━━━ Step 2/2: Firewall Setup ━━━"
bash "$(dirname "$0")/setup-firewall.sh"
echo ""

echo "🎉 Complete security setup finished!"
echo ""
echo "📋 Next steps:"
echo "   1. Update your .env file with HTTPS gateway URL"
echo "   2. Restart ULTron gateway"
echo "   3. Update Tasker/MacroDroid to use HTTPS"
echo ""
echo "💡 Test connectivity:"
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "   curl -k https://$LOCAL_IP/health"
echo ""
