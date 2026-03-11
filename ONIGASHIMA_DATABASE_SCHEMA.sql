-- ONIGASHIMA DATABASE SCHEMA

-- Table `users`
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Table `devices`
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    installation_id VARCHAR(100) NOT NULL UNIQUE,
    device_name VARCHAR(255),
    mac_address VARCHAR(17),
    os_version VARCHAR(50),
    tailscale_ip INET,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMPTZ
);

-- Table `pairings`
CREATE TABLE pairings (
    id SERIAL PRIMARY KEY,
    device_id INT NOT NULL REFERENCES devices(id),
    pairing_code VARCHAR(10) NOT NULL,
    expires_at TIMESTAMPTZ,
    verified_at TIMESTAMPTZ
);

-- Table `backups`
CREATE TABLE backups (
    id SERIAL PRIMARY KEY,
    device_id INT NOT NULL REFERENCES devices(id),
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    size BIGINT,
    encrypted_key BYTEA,
    s3_path TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Table `support_messages`
CREATE TABLE support_messages (
    id SERIAL PRIMARY KEY,
    device_id INT NOT NULL REFERENCES devices(id),
    user_message TEXT,
    agent_message TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ
);

-- Table `versions`
CREATE TABLE versions (
    id SERIAL PRIMARY KEY,
    version_string VARCHAR(20),
    release_date TIMESTAMPTZ,
    download_url TEXT,
    release_notes TEXT,
    is_latest BOOLEAN DEFAULT FALSE
);

-- Indexes and Constraints
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_device_user ON devices(user_id);

/* Comments for clarity: Each table includes appropriate primary, foreign keys, and indexes for performance optimization. */

-- Notes: Ensure PostgreSQL extension for UUID and network address types is enabled if needed...
(300-400 lines including further constraints and indexes)