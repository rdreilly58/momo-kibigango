// ONIGASHIMA BACKEND — SOLO BOOTSTRAP VERSION
// Node.js + Express + PostgreSQL
// Minimal implementation for MVP (6 endpoints only)

const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const { Pool } = require('pg');
const WebSocket = require('ws');
const http = require('http');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// ─────────────────────────────────────────────────────────────────
// CONFIGURATION
// ─────────────────────────────────────────────────────────────────

const config = {
  port: process.env.PORT || 3000,
  db: new Pool({
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD,
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 5432,
    database: process.env.DB_NAME || 'onigashima'
  }),
  jwt_secret: process.env.JWT_SECRET || 'your-secret-key-change-this'
};

// ─────────────────────────────────────────────────────────────────
// MIDDLEWARE
// ─────────────────────────────────────────────────────────────────

app.use(express.json());

// CORS headers
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  next();
});

// JWT Authentication Middleware
const authenticate = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: 'Missing authorization header' });

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, config.jwt_secret);
    req.user_id = decoded.user_id;
    next();
  } catch (err) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

// ─────────────────────────────────────────────────────────────────
// ERROR HANDLING
// ─────────────────────────────────────────────────────────────────

const handleError = (res, error, statusCode = 500) => {
  console.error('Error:', error);
  res.status(statusCode).json({ error: error.message || 'Server error' });
};

// ─────────────────────────────────────────────────────────────────
// ROUTES — AUTHENTICATION (2)
// ─────────────────────────────────────────────────────────────────

// POST /register — Create new user account
app.post('/register', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password required' });
    }

    // Hash password
    const password_hash = await bcrypt.hash(password, 10);

    // Insert user
    const result = await config.db.query(
      'INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING id',
      [email, password_hash]
    );

    const user_id = result.rows[0].id;
    const token = jwt.sign({ user_id }, config.jwt_secret, { expiresIn: '7d' });

    res.status(201).json({ user_id, token });
  } catch (err) {
    if (err.code === '23505') { // Unique constraint violation
      return res.status(400).json({ error: 'Email already registered' });
    }
    handleError(res, err);
  }
});

// POST /login — Authenticate user
app.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password required' });
    }

    // Find user
    const result = await config.db.query(
      'SELECT id, password_hash FROM users WHERE email = $1',
      [email]
    );

    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const user_id = result.rows[0].id;
    const password_hash = result.rows[0].password_hash;

    // Verify password
    const valid = await bcrypt.compare(password, password_hash);
    if (!valid) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Generate token
    const token = jwt.sign({ user_id }, config.jwt_secret, { expiresIn: '7d' });

    res.json({ user_id, token });
  } catch (err) {
    handleError(res, err);
  }
});

// ─────────────────────────────────────────────────────────────────
// ROUTES — DEVICES (2)
// ─────────────────────────────────────────────────────────────────

// POST /devices/register — Register a new device (Mac or iPhone)
app.post('/devices/register', authenticate, async (req, res) => {
  try {
    const { device_name, device_type } = req.body; // device_type: 'mac' or 'iphone'
    const user_id = req.user_id;

    // Generate simple 6-digit pairing code
    const pairing_code = Math.floor(100000 + Math.random() * 900000).toString();

    const result = await config.db.query(
      'INSERT INTO devices (user_id, device_name, device_type, pairing_code) VALUES ($1, $2, $3, $4) RETURNING id',
      [user_id, device_name, device_type, pairing_code]
    );

    const device_id = result.rows[0].id;

    res.status(201).json({ device_id, pairing_code });
  } catch (err) {
    handleError(res, err);
  }
});

// GET /devices/{id} — Get device info
app.get('/devices/:id', authenticate, async (req, res) => {
  try {
    const device_id = req.params.id;
    const user_id = req.user_id;

    const result = await config.db.query(
      'SELECT id, device_name, device_type, last_seen FROM devices WHERE id = $1 AND user_id = $2',
      [device_id, user_id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Device not found' });
    }

    res.json(result.rows[0]);
  } catch (err) {
    handleError(res, err);
  }
});

// ─────────────────────────────────────────────────────────────────
// ROUTES — MESSAGES (2)
// ─────────────────────────────────────────────────────────────────

// POST /messages/send — Send a message from one device to another
app.post('/messages/send', authenticate, async (req, res) => {
  try {
    const { from_device_id, to_device_id, content } = req.body;
    const user_id = req.user_id;

    // Verify both devices belong to user
    const devicesResult = await config.db.query(
      'SELECT id FROM devices WHERE id IN ($1, $2) AND user_id = $3',
      [from_device_id, to_device_id, user_id]
    );

    if (devicesResult.rows.length !== 2) {
      return res.status(403).json({ error: 'One or both devices not found or not yours' });
    }

    // Insert message
    const result = await config.db.query(
      'INSERT INTO messages (from_device_id, to_device_id, content, status) VALUES ($1, $2, $3, $4) RETURNING id',
      [from_device_id, to_device_id, content, 'sent']
    );

    const message_id = result.rows[0].id;

    // TODO: Notify listening WebSocket connections that new message arrived
    broadcastMessageToDevice(to_device_id, { message_id, from_device_id, content });

    res.status(201).json({ message_id });
  } catch (err) {
    handleError(res, err);
  }
});

// GET /messages/{device_id} — Get messages for a device
app.get('/messages/:device_id', authenticate, async (req, res) => {
  try {
    const device_id = req.params.device_id;
    const user_id = req.user_id;

    // Verify device belongs to user
    const deviceResult = await config.db.query(
      'SELECT id FROM devices WHERE id = $1 AND user_id = $2',
      [device_id, user_id]
    );

    if (deviceResult.rows.length === 0) {
      return res.status(403).json({ error: 'Device not found or not yours' });
    }

    // Get messages (unread first, then recent)
    const result = await config.db.query(
      'SELECT id, from_device_id, to_device_id, content, status, created_at FROM messages WHERE to_device_id = $1 ORDER BY status ASC, created_at DESC LIMIT 100',
      [device_id]
    );

    res.json(result.rows);
  } catch (err) {
    handleError(res, err);
  }
});

// ─────────────────────────────────────────────────────────────────
// WEBSOCKET — Real-time message delivery
// ─────────────────────────────────────────────────────────────────

const deviceConnections = new Map(); // device_id -> WebSocket connection

wss.on('connection', (ws) => {
  console.log('WebSocket client connected');

  // Wait for device registration message
  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data);
      
      // First message should be: { type: 'register', device_id: '123', token: 'jwt...' }
      if (msg.type === 'register') {
        const device_id = msg.device_id;
        const token = msg.token;

        // Verify token (simple check)
        try {
          jwt.verify(token, config.jwt_secret);
          deviceConnections.set(device_id, ws);
          console.log(`Device ${device_id} registered for WebSocket`);
          ws.send(JSON.stringify({ type: 'registered', device_id }));
        } catch (err) {
          ws.send(JSON.stringify({ type: 'error', error: 'Invalid token' }));
          ws.close();
        }
      }
    } catch (err) {
      console.error('WebSocket message error:', err);
    }
  });

  ws.on('close', () => {
    // Remove from connections
    for (const [device_id, conn] of deviceConnections.entries()) {
      if (conn === ws) {
        deviceConnections.delete(device_id);
        console.log(`Device ${device_id} disconnected`);
      }
    }
  });
});

// Broadcast message to device's WebSocket connection
function broadcastMessageToDevice(device_id, message) {
  const ws = deviceConnections.get(device_id.toString());
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'message', payload: message }));
  }
}

// ─────────────────────────────────────────────────────────────────
// HEALTH CHECK
// ─────────────────────────────────────────────────────────────────

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// ─────────────────────────────────────────────────────────────────
// SERVER STARTUP
// ─────────────────────────────────────────────────────────────────

server.listen(config.port, () => {
  console.log(`Onigashima backend running on port ${config.port}`);
  console.log('WebSocket server ready for connections');
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('Shutting down...');
  await config.db.end();
  process.exit(0);
});

module.exports = app;

// ─────────────────────────────────────────────────────────────────
// ENVIRONMENT VARIABLES (.env file)
// ─────────────────────────────────────────────────────────────────

/*
PORT=3000
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=onigashima
JWT_SECRET=your-secret-key-change-this-in-production
*/

// ─────────────────────────────────────────────────────────────────
// DATABASE SETUP (Run once to initialize)
// ─────────────────────────────────────────────────────────────────

/*
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE devices (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id),
  device_name VARCHAR(255),
  device_type VARCHAR(50), -- 'mac' or 'iphone'
  pairing_code VARCHAR(10),
  registered_at TIMESTAMP DEFAULT NOW(),
  last_seen TIMESTAMP
);

CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  from_device_id INT NOT NULL REFERENCES devices(id),
  to_device_id INT NOT NULL REFERENCES devices(id),
  content TEXT,
  status VARCHAR(50), -- 'sent', 'delivered', 'read'
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_device_user ON devices(user_id);
CREATE INDEX idx_message_to_device ON messages(to_device_id);
*/
