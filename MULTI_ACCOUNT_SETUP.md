# Multi-Account Setup Guide

## Executive Summary

Bob is transitioning from `rdreilly2010@gmail.com` to `reillyrd58@gmail.com`. This guide provides a comprehensive strategy for managing both accounts during transition and determining the optimal long-term setup.

## Decision Tree

```
Start: Do you need true account isolation?
│
├─ YES → Dual-Account Setup
│   └─ Reasons:
│       • Work/personal separation required
│       • Legal/compliance needs
│       • Different security levels
│       • Separate billing/resources
│
└─ NO → Migration Path (Recommended)
    └─ Reasons:
        • Simpler management
        • Less context switching
        • Unified history
        • Easier automation
```

## Recommended Architecture

### For Bob's Case: **Migration Path with Transition Period**

**Why:** Bob is already planning to migrate to reillyrd58. A dual-account setup adds unnecessary complexity for personal use.

**Architecture:**
1. **Primary:** reillyrd58@gmail.com (new default)
2. **Legacy:** rdreilly2010@gmail.com (forward to primary, monitor for 6-12 months)
3. **Single context:** One set of SSH keys, one Git config, unified tools

## Comparison Table: Dual vs Consolidated

| Aspect | Dual-Account | Consolidated (Recommended) |
|--------|--------------|---------------------------|
| **Complexity** | High - constant switching | Low - single context |
| **Git Management** | Multiple SSH keys, config profiles | One SSH key, simple config |
| **GitHub CLI** | Multiple auth contexts | Single auth |
| **Google Services** | Separate calendars, drives | Unified, with sharing |
| **Password Manager** | Multiple vaults | Single vault with folders |
| **OpenClaw** | Profile switching needed | Single session |
| **Maintenance** | Ongoing sync issues | Minimal |
| **Security** | Good isolation | Adequate for personal use |
| **Migration Effort** | Low initial, high ongoing | Medium initial, low ongoing |

## Implementation Strategies

### A. Migration Path (Recommended)

#### Phase 1: Transition Setup (Current)
```bash
# 1. Set up email forwarding
# rdreilly2010 → reillyrd58 (via Gmail settings)

# 2. Update primary Git config
git config --global user.email "reillyrd58@gmail.com"
git config --global user.name "Bob Reilly"

# 3. Add both emails to GitHub account
# GitHub Settings → Emails → Add reillyrd58@gmail.com
# Keep rdreilly2010 for commit association

# 4. Update GitHub CLI
gh auth logout
gh auth login
# Choose: reillyrd58@gmail.com

# 5. Google CLI migration
gog login reillyrd58@gmail.com
# Keep rdreilly2010 token for transition
```

#### Phase 2: Service Migration Checklist
- [ ] Update primary email on all services
- [ ] Export/import Google Calendar
- [ ] Migrate Drive files (or share to new account)
- [ ] Update 1Password account email
- [ ] Update SSH key comment: `ssh-keygen -c -f ~/.ssh/id_ed25519`
- [ ] Notify contacts of new email

### B. Dual-Account Setup (If Needed)

#### 1. Git Configuration

**~/.gitconfig:**
```ini
# Global fallback
[user]
    name = Bob Reilly
    email = reillyrd58@gmail.com

# Include profile configs
[includeIf "gitdir:~/personal/"]
    path = ~/.gitconfig-personal
[includeIf "gitdir:~/legacy/"]
    path = ~/.gitconfig-legacy
```

**~/.gitconfig-personal:**
```ini
[user]
    email = reillyrd58@gmail.com
[core]
    sshCommand = ssh -i ~/.ssh/id_ed25519_personal
```

**~/.gitconfig-legacy:**
```ini
[user]
    email = rdreilly2010@gmail.com
[core]
    sshCommand = ssh -i ~/.ssh/id_ed25519_legacy
```

#### 2. SSH Configuration

**~/.ssh/config:**
```ssh
# Personal GitHub
Host github-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal
    IdentitiesOnly yes

# Legacy GitHub
Host github-legacy
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_legacy
    IdentitiesOnly yes

# Default
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal
    IdentitiesOnly yes
```

#### 3. GitHub CLI Multi-Account

```bash
# Add both accounts
gh auth login --hostname github.com
# Login with reillyrd58@gmail.com

# Create alias for legacy
gh alias set legacy-auth 'auth switch -u rdreilly2010'
gh alias set personal-auth 'auth switch -u reillyrd58'

# Quick switching
gh legacy-auth  # switches to rdreilly2010
gh personal-auth  # switches to reillyrd58
```

#### 4. Google Account Strategy

```bash
# Multiple account support in gog
gog login reillyrd58@gmail.com
gog login rdreilly2010@gmail.com

# Usage with -a flag
gog calendar list -a reillyrd58@gmail.com
gog gmail search -a rdreilly2010@gmail.com "important"

# Set default
export GOG_DEFAULT_ACCOUNT=reillyrd58@gmail.com
```

## OpenClaw Integration

### Recommended: Single Session with Migration Awareness

**TOOLS.md update:**
```markdown
## Account Status (March 2024)
- **Primary:** reillyrd58@gmail.com (default for all new operations)
- **Legacy:** rdreilly2010@gmail.com (checking during transition)
- **Migration deadline:** September 2024
```

**Memory organization:**
```
memory/
├── account-migration.md  # Track migration progress
├── legacy-services.md    # List of services still on old email
└── YYYY-MM-DD.md        # Daily memories (unified)
```

### Alternative: Profile Switching (Not Recommended)

```bash
# Create profile switcher
cat > ~/.openclaw/workspace/scripts/switch-account.sh << 'EOF'
#!/bin/bash
ACCOUNT=$1
if [[ "$ACCOUNT" == "legacy" ]]; then
    export GIT_AUTHOR_EMAIL="rdreilly2010@gmail.com"
    export GOG_DEFAULT_ACCOUNT="rdreilly2010@gmail.com"
    echo "Switched to legacy account"
else
    export GIT_AUTHOR_EMAIL="reillyrd58@gmail.com"
    export GOG_DEFAULT_ACCOUNT="reillyrd58@gmail.com"
    echo "Switched to personal account"
fi
EOF

chmod +x ~/.openclaw/workspace/scripts/switch-account.sh
```

## Password Manager Organization

### Recommended: Single Vault with Folders

**1Password Structure:**
```
OpenClaw Secrets/
├── Active Services/
│   ├── GitHub (reillyrd58)
│   ├── Google (reillyrd58)
│   └── APIs and Tokens
├── Legacy Access/
│   ├── Old Gmail App Passwords
│   └── Services pending migration
└── Shared Resources/
    └── Family shared items
```

**Naming Convention:**
- Format: `Service - Account (Email)`
- Example: `GitHub - Personal (reillyrd58)`
- Legacy: `GitHub - Legacy (rdreilly2010)`

## Context Switching Mechanisms

### For Migration Path (Recommended)
```bash
# No switching needed - everything uses reillyrd58
# Legacy email forwards automatically
# Check legacy occasionally:
gog gmail search -a rdreilly2010@gmail.com "is:unread"
```

### For Dual-Account (If Needed)

**Quick Switcher Script:**
```bash
#!/bin/bash
# ~/.openclaw/workspace/scripts/account-context.sh

case "$1" in
    "status")
        echo "Git: $(git config user.email)"
        echo "GitHub: $(gh auth status | grep 'Logged in' | head -1)"
        echo "Google: ${GOG_DEFAULT_ACCOUNT:-not set}"
        ;;
    "personal")
        git config --global user.email "reillyrd58@gmail.com"
        gh auth switch -u reillyrd58
        export GOG_DEFAULT_ACCOUNT="reillyrd58@gmail.com"
        echo "Switched to personal context"
        ;;
    "legacy")
        git config --global user.email "rdreilly2010@gmail.com"
        gh auth switch -u rdreilly2010
        export GOG_DEFAULT_ACCOUNT="rdreilly2010@gmail.com"
        echo "Switched to legacy context"
        ;;
esac
```

## Migration Timeline

### Immediate (Week 1)
1. Set up email forwarding
2. Add reillyrd58 to GitHub account
3. Update Git global config
4. Configure gog for both accounts

### Short-term (Month 1)
1. Update top 10 most-used services
2. Migrate active projects
3. Update OpenClaw defaults
4. Test automation with new account

### Medium-term (Months 2-6)
1. Gradually update remaining services
2. Monitor legacy inbox via forwarding
3. Update contacts
4. Archive old account data

### Long-term (Month 12)
1. Consider closing legacy account
2. Or keep as permanent forward
3. Archive final state

## Gotchas and Troubleshooting

### Common Issues

**1. Git commits with wrong email:**
```bash
# Fix last commit
git commit --amend --author="Bob Reilly <reillyrd58@gmail.com>"

# Fix multiple commits
git filter-branch --env-filter '
OLD_EMAIL="rdreilly2010@gmail.com"
NEW_EMAIL="reillyrd58@gmail.com"
if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]; then
    export GIT_COMMITTER_EMAIL="$NEW_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]; then
    export GIT_AUTHOR_EMAIL="$NEW_EMAIL"
fi
' --tag-name-filter cat -- --branches --tags
```

**2. GitHub push rejection:**
```bash
# If using wrong SSH key
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_personal" git push
```

**3. Google token confusion:**
```bash
# Clear and re-auth
rm -rf ~/.config/gog/
gog login reillyrd58@gmail.com
gog login rdreilly2010@gmail.com  # if needed
```

**4. OpenClaw memory confusion:**
- Always document which account was used for what
- Use explicit -a flags during transition
- Keep migration log in memory/

### Security Best Practices

1. **Different passwords** for each account (use 1Password)
2. **2FA on both** accounts (different methods if possible)
3. **Regular audit** of what has access to each account
4. **Revoke tokens** on old account after migration
5. **Download data** from old account before closure

## Decision: Recommended Path for Bob

**Go with Migration Path because:**
1. You're already planning to migrate to reillyrd58
2. Personal use doesn't require strict isolation
3. Simpler is better for long-term maintenance
4. One identity reduces cognitive overhead
5. Email forwarding handles the transition gracefully

**Implementation Priority:**
1. ✅ Set up forwarding today
2. ✅ Update Git config now
3. ⏱️ Migrate services gradually
4. 📊 Track progress in memory/account-migration.md
5. 🎯 Target 6-month transition

## Quick Reference Card

```bash
# Current email check
gog gmail search -a rdreilly2010@gmail.com "is:unread"

# New email default
gog calendar list  # uses reillyrd58 by default

# Git check
git config user.email  # should show reillyrd58

# GitHub check  
gh auth status  # should show reillyrd58

# Quick legacy check
alias legacy-check='gog gmail search -a rdreilly2010@gmail.com "is:unread newer_than:1d"'
```

## Conclusion

For Bob's use case, a **migration path** is strongly recommended over maintaining dual accounts. The complexity of dual-account management isn't justified for personal use. Focus energy on migrating services to reillyrd58@gmail.com while maintaining rdreilly2010@gmail.com as a forwarding address during transition.

The dual-account setup documentation is provided for completeness, but should only be considered if true account isolation becomes necessary (e.g., if Bob later needs work/personal separation with a corporate account).