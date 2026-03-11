// ONIGASHIMA BACKEND STARTER
// Node.js + Express server setup

const express = require('express');
const jwt = require('jsonwebtoken');
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
const app = express();

// Middleware
app.use(bodyParser.json());
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header(
    'Access-Control-Allow-Headers',
    'Origin, X-Requested-With, Content-Type, Accept, Authorization'
  );
  next();
});

// Configuration (example)
const config = {
  port: process.env.PORT || 3000,
  dbUri: process.env.DB_URI,
  jwtSecret: process.env.JWT_SECRET || 'your-secret-key'
};

// Database connection
mongoose.connect(config.dbUri, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('Database connected'))
  .catch(err => console.error('Database connection error:', err));

// Routes
app.get('/api/health', (req, res) => {
  res.status(200).send('OK');
});

// Auth Middleware
const authenticate = (req, res, next) => {
  const token = req.header('Authorization');
  if (!token) return res.status(401).send('Access denied. No token provided.');

  try {
    const decoded = jwt.verify(token, config.jwtSecret);
    req.user = decoded;
    next();
  } catch (ex) {
    res.status(400).send('Invalid token.');
  }
};

// Example route with authentication
app.get('/api/private', authenticate, (req, res) => {
  res.status(200).send(`Hello ${req.user.email}, welcome to the private route!`);
});

// Start server
app.listen(config.port, () => console.log(`Server running on port ${config.port}`));

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

// Export for testing
module.exports = app;

// Note: Ensure to set up environment variables like DB_URI and JWT_SECRET for secure operation...
(300-350 lines including additional routes and configurations)