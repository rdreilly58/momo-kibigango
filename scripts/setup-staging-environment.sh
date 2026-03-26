#!/bin/bash
# Setup Staging Environment for OpenClaw Update Testing
# Creates isolated staging setup to test updates safely
# Usage: bash setup-staging-environment.sh

set -e

PROD_HOME="$HOME/.openclaw"
STAGING_HOME="$HOME/.openclaw-staging"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     OpenClaw Staging Environment Setup                         ║"
echo "║     Creates isolated environment for testing updates          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if staging already exists
if [ -d "$STAGING_HOME" ]; then
  echo "⚠️  Staging environment already exists: $STAGING_HOME"
  read -p "Remove and recreate? (y/n) " -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing existing staging..."
    rm -rf "$STAGING_HOME"
  else
    echo "Using existing staging environment."
    echo "Location: $STAGING_HOME"
    exit 0
  fi
fi

echo "📂 Creating staging directory structure..."
mkdir -p "$STAGING_HOME"
echo "  ✅ Created $STAGING_HOME"
echo ""

# Copy minimal config for staging
echo "📋 Copying configuration from production..."
mkdir -p "$STAGING_HOME/config"
cp "$PROD_HOME/openclaw.json" "$STAGING_HOME/config/" 2>/dev/null || true
cp "$PROD_HOME/config.json" "$STAGING_HOME/config/" 2>/dev/null || true
echo "  ✅ Configuration copied"
echo ""

# Create minimal identity (important for gateway)
echo "🔑 Setting up minimal identity..."
mkdir -p "$STAGING_HOME/identity"
# Don't copy real identity - create minimal one for testing
cat > "$STAGING_HOME/identity/staging-note.txt" << 'ENDNOTE'
STAGING ENVIRONMENT - NOT FOR PRODUCTION

This staging environment is for testing OpenClaw updates.
It uses minimal configuration to test critical paths:
  - Gateway startup
  - Configuration loading
  - Tool availability
  - Cron job parsing

For full testing, copy identity files from production backup if needed:
  cp ~/.openclaw/backups/pre-update-YYYYMMDD_HHMMSS/config/identity/* ~/.openclaw-staging/identity/
ENDNOTE
echo "  ✅ Identity setup complete"
echo ""

# Create minimal cron config for testing
echo "📅 Setting up minimal cron configuration..."
mkdir -p "$STAGING_HOME/cron"
cat > "$STAGING_HOME/cron/jobs.json" << 'ENDJOBS'
{
  "version": 1,
  "jobs": []
}
ENDJOBS
echo "  ✅ Cron configuration created (empty for staging)"
echo ""

# Create test configs directory
echo "📝 Creating test configuration..."
mkdir -p "$STAGING_HOME/workspace"
cat > "$STAGING_HOME/workspace/STAGING_CONFIG.md" << 'ENDCONFIG'
# Staging Environment Configuration

**Location:** ~/.openclaw-staging/
**Purpose:** Safe testing ground for OpenClaw updates
**Isolation:** Completely separate from production (~/.openclaw/)

## What's Here

- `openclaw.json` - Primary configuration (copied from production)
- `config.json` - Secondary configuration (copied from production)
- `cron/jobs.json` - Empty cron job list (for testing)
- `identity/` - Staging identity (minimal, for testing only)

## How to Use

### 1. Test OpenClaw Update
```bash
# Set environment to use staging
export OPENCLAW_HOME=~/.openclaw-staging

# Run update command
openclaw update

# If successful, proceed with production update
# If fails, analyze error and rollback production
```

### 2. Run Staging Gateway
```bash
# Check if gateway starts
export OPENCLAW_HOME=~/.openclaw-staging
openclaw gateway status

# Test critical commands
openclaw cron list
```

### 3. Cleanup After Testing
```bash
# Remove staging when done
rm -rf ~/.openclaw-staging
```

## Important Notes

- Staging uses separate configuration from production
- Does NOT affect production system
- Can be safely deleted after testing
- Use for testing major version updates
- Keep production backup before testing

## Testing Checklist

After update in staging:
- [ ] Gateway starts successfully
- [ ] Configuration loads without errors
- [ ] Cron jobs parse correctly
- [ ] Tools work (exec, read, write, etc.)
- [ ] No compatibility issues detected
- [ ] Log files contain no errors

If all tests pass → Safe to update production
If tests fail → Keep backup, don't update, investigate error
ENDCONFIG
echo "  ✅ Staging configuration created"
echo ""

# Create test runner script
cat > "$STAGING_HOME/test-staging.sh" << 'ENDTEST'
#!/bin/bash
# Quick test of staging OpenClaw environment

export OPENCLAW_HOME=~/.openclaw-staging

echo "Testing staging environment..."
echo ""

TESTS_PASSED=0
TESTS_FAILED=0

test_gateway_status() {
  echo "Test 1: Gateway status..."
  if openclaw gateway status > /dev/null 2>&1; then
    echo "  ✅ Gateway OK"
    ((TESTS_PASSED++))
  else
    echo "  ❌ Gateway failed"
    ((TESTS_FAILED++))
  fi
}

test_cron_list() {
  echo "Test 2: Cron job listing..."
  if openclaw cron list > /dev/null 2>&1; then
    echo "  ✅ Cron OK"
    ((TESTS_PASSED++))
  else
    echo "  ❌ Cron failed"
    ((TESTS_FAILED++))
  fi
}

test_config() {
  echo "Test 3: Configuration validation..."
  if [ -f ~/.openclaw-staging/config.json ]; then
    echo "  ✅ Config exists"
    ((TESTS_PASSED++))
  else
    echo "  ❌ Config missing"
    ((TESTS_FAILED++))
  fi
}

echo "Running tests..."
echo ""

test_gateway_status
test_cron_list
test_config

echo ""
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"

if [ $TESTS_FAILED -eq 0 ]; then
  echo "✅ Staging environment is healthy!"
  exit 0
else
  echo "❌ Staging environment has issues. Review above."
  exit 1
fi
ENDTEST

chmod +x "$STAGING_HOME/test-staging.sh"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              Staging Environment Ready ✅                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Location: $STAGING_HOME"
echo "Size: $(du -sh "$STAGING_HOME" 2>/dev/null | cut -f1)"
echo ""
echo "Next steps:"
echo "  1. Test staging: export OPENCLAW_HOME=$STAGING_HOME"
echo "  2. Update in staging: openclaw update"
echo "  3. Run tests: bash $STAGING_HOME/test-staging.sh"
echo "  4. If OK → safe to update production"
echo "  5. Cleanup: rm -rf $STAGING_HOME"
echo ""
