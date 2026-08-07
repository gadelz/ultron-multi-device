# ULTron Security Setup Guide

## 🔒 Complete Security Implementation

This guide covers HTTPS setup and firewall configuration for production deployment.

---

## Option 1: Quick Setup (Development/Testing)

### Auto-Setup Script

```bash
# Run as root
sudo bash scripts/setup-security.sh
```

This will:
1. Generate self-signed SSL certificate (valid 10 years)
2. Configure nginx reverse proxy with SSL
3. Set up UFW firewall with proper rules
4. Enable HTTPS on port 443

### Manual Steps

#### 1. Generate Self-Signed Certificate
```bash
sudo mkdir -p /etc/ssl/certs /etc/ssl/private
sudo openssl req -x509 -newkey rsa:4096 \
    -keyout /etc/ssl/private/ultron.key \
    -out /etc/ssl/certs/ultron.crt \
    -days 3650 -nodes \
    -subj "/CN=localhost"
```

#### 2. Configure nginx
```bash
sudo cp config/nginx/ultron.conf /etc/nginx/sites-available/ultron
sudo ln -sf /etc/nginx/sites-available/ultron /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

#### 3. Setup Firewall
```bash
sudo apt-get install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow from 192.168.0.0/16 to any port 8080  # Gateway LAN only
sudo ufw enable
```

---

## Option 2: Production Setup (Let's Encrypt)

### Requirements
- Domain name pointing to your server
- Port 80 open (for certificate validation)

### Run Setup
```bash
sudo bash scripts/setup-letsencrypt.sh your-domain.com
```

### Manual Steps
```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com --non-interactive --agree-tos --email admin@your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

---

## 📋 Post-Setup Configuration

### 1. Update Environment Variables
```bash
# Edit .env
ULTRON_GATEWAY=https://your-server-ip:443
ULTRON_API_KEY=$(openssl rand -hex 32)
```

### 2. Restart Gateway
```bash
# Stop current gateway
pkill -f "uvicorn src.gateway.server"

# Start with HTTPS
ULTRON_GATEWAY=https://your-ip:443 \
ULTRON_API_KEY=your-new-key \
python -m uvicorn src.gateway.server:app --host 0.0.0.0 --port 8080
```

### 3. Update Android Apps

#### Tasker
1. Go to HTTP Server profile
2. Change URL from `http://` to `https://`
3. Enable "Ignore SSL Errors" for self-signed cert
4. Or install certificate on device for production

#### MacroDroid
1. HTTP Trigger settings
2. Change to HTTPS
3. Same certificate handling as Tasker

---

## 🔍 Verification

### Test HTTPS
```bash
# Self-signed cert (ignore warnings)
curl -k https://your-ip/health

# Let's Encrypt (valid cert)
curl https://your-domain.com/health
```

### Test Firewall
```bash
# From external network (should fail)
curl http://your-ip:8080/health  # Blocked

# From local network (should work)
curl https://your-ip/health      # Allowed
```

### Check Service Status
```bash
sudo systemctl status nginx
sudo ufw status verbose
curl -k https://localhost/health
```

---

## 🚨 Troubleshooting

### Cannot SSH After Firewall
```bash
# If locked out, use console/VNC to access server
sudo ufw disable
# Then reconfigure with SSH allowed
sudo ufw allow 22/tcp
sudo ufw enable
```

### SSL Certificate Errors
```bash
# Check certificate validity
openssl x509 -in /etc/ssl/certs/ultron.crt -text -noout

# Renew if expired
sudo certbot renew
```

### nginx Configuration Error
```bash
# Test config
sudo nginx -t

# View config
sudo nano /etc/nginx/sites-available/ultron
```

---

## 📊 Security Checklist

Before going production:

- [ ] HTTPS enabled with valid certificate
- [ ] API key changed from default
- [ ] Firewall configured (only necessary ports open)
- [ ] IP whitelist set (if needed)
- [ ] SSL certificate auto-renewal configured
- [ ] Backup and recovery plan documented
- [ ] Monitoring/logging enabled

---

## 🔐 Security Best Practices

### Network Security
1. **Use VPN** for remote management
2. **Keep services on private network** (192.168.x.x)
3. **Use VLAN** to isolate IoT devices
4. **Monitor network traffic** for anomalies

### Application Security
1. **Rotate API keys** quarterly
2. **Update dependencies** regularly
3. **Enable logging** and review periodically
4. **Use strong passwords** for all services

### Device Security
1. **Use unique tokens** per device
2. **Enable HTTPS** on all device connections
3. **Remove unused devices** promptly
4. **Update firmware** regularly

---

## 📞 Support

- **GitHub Issues**: https://github.com/gadelz/ultron-multi-device/issues
- **Documentation**: https://github.com/gadelz/ultron-multi-device/tree/main/docs
