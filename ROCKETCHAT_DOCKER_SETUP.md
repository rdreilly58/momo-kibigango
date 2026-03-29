# Rocket.Chat Docker Setup for OpenClaw Access

**Objective:** Self-hosted Rocket.Chat server on Docker to enable OpenClaw access from your work computer

**Setup Date:** March 29, 2026  
**Status:** Guide ready to implement  

---

## 📋 Overview

**What we're setting up:**
- Self-hosted Rocket.Chat instance in Docker
- Secure TLS/HTTPS with Let's Encrypt
- OpenClaw integration via bot user
- Access from work computer via mobile/desktop app
- Production-ready configuration

**Benefits:**
- ✅ Full control over data (no cloud provider)
- ✅ Access OpenClaw from work computer via chat app
- ✅ Integrate with OpenClaw bot
- ✅ Free (Community Edition)
- ✅ Can federate with other Rocket.Chat instances

---

## 🚀 Quick Start (5-10 minutes)

### Step 1: Prerequisites

**Required:**
- Docker & Docker Compose installed
- Domain name (or use sslip.io for local testing)
- Port 80 and 443 accessible (for TLS)

**Check Docker installation:**
```bash
docker --version
docker compose version
```

### Step 2: Create Docker Compose Configuration

Create a directory and file:
```bash
mkdir -p ~/rocketchat
cd ~/rocketchat
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  rocketchat:
    image: rocketchat/rocket.chat:latest
    container_name: rocketchat
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      MONGO_URL: mongodb://mongodb:27017/rocketchat
      MONGO_OPLOG_URL: mongodb://mongodb:27017/local
      ROOT_URL: http://localhost:3000  # Change to your domain for HTTPS
      Accounts_UseDNSDomainCheck: "false"
      DEPLOY_METHOD: docker
      DEPLOY_PLATFORM: ${DEPLOY_PLATFORM:-docker}
    depends_on:
      - mongodb
    networks:
      - rocketchat-network

  mongodb:
    image: mongo:6.0
    container_name: rocketchat-mongo
    restart: unless-stopped
    volumes:
      - ./data/db:/data/db
      - ./data/configdb:/data/configdb
    environment:
      MONGO_INITDB_ROOT_USERNAME: rocketchat
      MONGO_INITDB_ROOT_PASSWORD: rocketchat_password
    networks:
      - rocketchat-network

networks:
  rocketchat-network:
    driver: bridge
```

### Step 3: Start Rocket.Chat

```bash
cd ~/rocketchat
docker compose up -d
```

**Verify it's running:**
```bash
docker compose ps
docker compose logs -f rocketchat
```

**Access the server:**
- Open browser: `http://localhost:3000`
- Complete the setup wizard
- Create admin account

---

## 🔒 Production Setup (With TLS/HTTPS)

### For External Access (Work Computer)

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    container_name: rocketchat-traefik
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    environment:
      TRAEFIK_API_INSECURE: "true"
      TRAEFIK_API_DASHBOARD: "true"
      TRAEFIK_PROVIDERS_DOCKER: "true"
      TRAEFIK_PROVIDERS_DOCKER_EXPOSEDBYDEFAULT: "false"
      TRAEFIK_ENTRYPOINTS_WEB_ADDRESS: ":80"
      TRAEFIK_ENTRYPOINTS_WEBSECURE_ADDRESS: ":443"
      TRAEFIK_CERTIFICATESRESOLVERS_LETSENCRYPT_ACME_HTTPCHALLENGE: "true"
      TRAEFIK_CERTIFICATESRESOLVERS_LETSENCRYPT_ACME_HTTPCHALLENGE_ENTRYPOINT: "web"
      TRAEFIK_CERTIFICATESRESOLVERS_LETSENCRYPT_ACME_EMAIL: your-email@example.com
      TRAEFIK_CERTIFICATESRESOLVERS_LETSENCRYPT_ACME_STORAGE: "/letsencrypt/acme.json"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./letsencrypt:/letsencrypt
    networks:
      - rocketchat-network

  rocketchat:
    image: rocketchat/rocket.chat:latest
    container_name: rocketchat
    restart: unless-stopped
    environment:
      MONGO_URL: mongodb://mongodb:27017/rocketchat
      MONGO_OPLOG_URL: mongodb://mongodb:27017/local
      ROOT_URL: https://chat.example.com  # Change to your domain
      Accounts_UseDNSDomainCheck: "false"
      DEPLOY_METHOD: docker
    depends_on:
      - mongodb
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.rocketchat.rule=Host(`chat.example.com`)"
      - "traefik.http.routers.rocketchat.entrypoints=web,websecure"
      - "traefik.http.routers.rocketchat.tls.certresolver=letsencrypt"
      - "traefik.http.services.rocketchat.loadbalancer.server.port=3000"
    networks:
      - rocketchat-network

  mongodb:
    image: mongo:6.0
    container_name: rocketchat-mongo
    restart: unless-stopped
    volumes:
      - ./data/db:/data/db
      - ./data/configdb:/data/configdb
    environment:
      MONGO_INITDB_ROOT_USERNAME: rocketchat
      MONGO_INITDB_ROOT_PASSWORD: rocketchat_password
    networks:
      - rocketchat-network

networks:
  rocketchat-network:
    driver: bridge
```

**To use production setup:**
```bash
# Update domain in docker-compose.prod.yml
nano docker-compose.prod.yml  # Change chat.example.com and email

# Start with Traefik
docker compose -f docker-compose.prod.yml up -d

# View Traefik dashboard
# Open: http://localhost:8080
```

---

## 🤖 OpenClaw Integration

### Step 1: Create Bot User in Rocket.Chat

1. Log in as admin to Rocket.Chat (http://localhost:3000 or your domain)
2. Go to **Administration** → **Users**
3. Click **Create new**
4. Fill in:
   - **Name:** Momotaro (or your OpenClaw name)
   - **Username:** momotaro
   - **Email:** momotaro@openclaw.local
   - **Password:** Generate a strong password
   - **Role:** Bot
5. Click **Create**

### Step 2: Get Bot Authentication Token

```bash
# Get bot auth token (via API)
curl -X POST http://localhost:3000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"user":"momotaro","password":"YOUR_BOT_PASSWORD"}'
```

**Response will include:**
```json
{
  "authToken": "YOUR_AUTH_TOKEN",
  "userId": "YOUR_USER_ID"
}
```

**Save these credentials** — you'll need them for OpenClaw configuration.

### Step 3: Configure OpenClaw for Rocket.Chat

**Option A: Using OpenClaw CLI**

```bash
openclaw plugins install @cloudrise/openclaw-channel-rocketchat

openclaw config set channels.rocketchat.enabled true
openclaw config set channels.rocketchat.baseUrl "https://chat.example.com"
openclaw config set channels.rocketchat.userId "YOUR_USER_ID"
openclaw config set channels.rocketchat.authToken "YOUR_AUTH_TOKEN"

openclaw restart
```

**Option B: Manual Configuration**

Edit `~/.openclaw/config.json`:

```json
{
  "channels": {
    "rocketchat": {
      "enabled": true,
      "baseUrl": "https://chat.example.com",
      "userId": "YOUR_USER_ID",
      "authToken": "YOUR_AUTH_TOKEN",
      "directMessages": true,
      "rooms": ["general", "random"]
    }
  }
}
```

### Step 4: Test the Integration

1. In Rocket.Chat, send a DM to Momotaro (your bot)
2. Message: `hello`
3. OpenClaw should respond

---

## 📱 Access from Work Computer

### Mobile App Setup

**iOS:**
1. Download "Rocket.Chat" from App Store
2. Tap **Create new server**
3. Enter: `https://chat.example.com` (or your domain)
4. Log in with your account
5. Join channels or start DMs with Momotaro

**Android:**
1. Download "Rocket.Chat" from Google Play
2. Tap **Connect to server**
3. Enter: `https://chat.example.com`
4. Log in and access

### Desktop App Setup

**macOS/Windows:**
1. Download from https://rocket.chat/download
2. Add server: `https://chat.example.com`
3. Log in
4. Start using OpenClaw from your work computer

### Web Access

Simply visit `https://chat.example.com` in any browser from your work computer.

---

## 🔐 Security Best Practices

### 1. Change Default Passwords

```bash
# Update MongoDB password
docker compose exec mongodb mongosh admin \
  --eval "db.changeUserPassword('rocketchat', 'NEW_SECURE_PASSWORD')"
```

### 2. Enable 2FA for Admin

In Rocket.Chat Admin Panel:
- **Security** → **Two-Factor Authentication**
- Enable for all users or just admin

### 3. Restrict User Registration

In Rocket.Chat Admin Panel:
- **Accounts** → **Registration**
- Set "Disable User Registration" = ON
- Add users manually

### 4. Enable HTTPS

Already done with Traefik setup above.

### 5. Firewall Configuration

Only allow:
- Port 80 (HTTP, for Let's Encrypt)
- Port 443 (HTTPS, for access)
- SSH for management (not exposed to web)

### 6. Backup MongoDB Data

```bash
# Backup
docker compose exec mongodb mongodump --archive=/backup/rocketchat-$(date +%Y%m%d).gz --gzip

# Restore
docker compose exec mongodb mongorestore --archive=/backup/rocketchat-YYYYMMDD.gz --gzip
```

---

## 📊 Monitoring & Maintenance

### View Logs

```bash
# Rocket.Chat logs
docker compose logs rocketchat -f

# MongoDB logs
docker compose logs mongodb -f

# Traefik logs
docker compose logs traefik -f
```

### Check Disk Usage

```bash
# See data directory size
du -sh ~/rocketchat/data/

# Clean up old backups
find ~/rocketchat/backups -mtime +30 -delete
```

### Update Rocket.Chat

```bash
# Pull latest image
docker compose pull rocketchat

# Restart service
docker compose up -d rocketchat
```

---

## 🔧 Troubleshooting

### Issue: Can't access from work computer

**Solution:**
1. Verify domain DNS resolves: `ping chat.example.com`
2. Check firewall ports open: `sudo lsof -i :443`
3. Verify Traefik logs: `docker compose logs traefik`

### Issue: TLS certificate not generating

**Solution:**
1. Check email address in Traefik config
2. Verify domain is accessible: `curl http://chat.example.com`
3. Check Let's Encrypt rate limits (50/week per domain)
4. Use `staging` Let's Encrypt URL for testing

### Issue: OpenClaw not responding in Rocket.Chat

**Solution:**
1. Verify bot user exists: Check admin → users
2. Verify auth token correct: Re-run login API call
3. Check OpenClaw logs: `openclaw logs`
4. Restart OpenClaw: `openclaw restart`

### Issue: MongoDB connection failed

**Solution:**
1. Check MongoDB is running: `docker compose ps`
2. Verify credentials match: Check env vars
3. Check disk space: `df -h`
4. Restart MongoDB: `docker compose restart mongodb`

---

## 📚 Resources

**Official Documentation:**
- Rocket.Chat Docker: https://docs.rocket.chat/deploy/docker-and-docker-compose
- OpenClaw Channels: https://docs.openclaw.ai/channels
- OpenClaw Rocket.Chat Plugin: https://github.com/openclaw/skills/rocketchat

**Community Guides:**
- Self-hosting Rocket.Chat: https://selfhosting.sh/apps/rocket-chat/
- Traefik + Rocket.Chat: https://heyvaldemar.com/install-rocket-chat-using-docker-compose/

**API Documentation:**
- Rocket.Chat API: https://docs.rocket.chat/api
- WebSocket DDP: https://docs.rocket.chat/api/realtime-api

---

## ✅ Deployment Checklist

- [ ] Docker & Docker Compose installed
- [ ] Directory created: `~/rocketchat`
- [ ] `docker-compose.yml` created
- [ ] Rocket.Chat started and accessible
- [ ] Admin account created
- [ ] Domain configured (for HTTPS)
- [ ] Traefik/TLS setup (if needed)
- [ ] Bot user created in Rocket.Chat
- [ ] Auth token obtained
- [ ] OpenClaw configured with bot credentials
- [ ] Mobile app installed and tested
- [ ] First message sent to Momotaro bot
- [ ] Security hardening applied
- [ ] Backup strategy in place

---

## 🚀 Next Steps

1. **Day 1:** Set up basic Docker Rocket.Chat (5 min)
2. **Day 2:** Configure HTTPS with domain (10 min)
3. **Day 3:** Create bot user & integrate with OpenClaw (10 min)
4. **Day 4:** Test from work computer (5 min)
5. **Ongoing:** Monitor logs, backup data, update regularly

---

**Status:** Ready to implement  
**Complexity:** Medium (Docker + configuration)  
**Time to production:** ~30 minutes  
**Cost:** $0 (Community Edition + free TLS)

