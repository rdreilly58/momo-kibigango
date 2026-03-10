# Momotaro iOS — Quick Start Guide

_Get up and running in 5 minutes_ 🍑

---

## ⚡ 5-Minute Setup

### 1. Install (2 min)

```bash
# Clone repository
git clone https://github.com/rdreilly58/momotaro-ios.git
cd momotaro-ios

# Generate project
brew install tuist
tuist generate
```

### 2. Open Xcode (30 sec)

```bash
open Momotaro.xcworkspace
```

### 3. Select Target (30 sec)

- Scheme: **Momotaro** (top left dropdown)
- Device: **iPhone 17 Pro** (simulator)

### 4. Build & Run (2 min)

Press **▶ (Play)** or `Cmd + R`

✅ **Done!** App opens on simulator.

---

## 🚀 First Steps in App

### Launch (You'll See)

1. **Welcome Screen** with Momotaro logo
2. **Create Session** button
3. **Settings** gear icon

### Your First Message

1. Tap **Create Session**
2. Name: `My First Chat`
3. Press **Start**
4. Type: `Hello Momotaro!`
5. Press **Send**

✅ **Boom** — You got your first response!

---

## 📚 Essential Docs

| Document | What's In It | Read When |
|----------|------------|-----------|
| **[INSTALLATION.md](INSTALLATION.md)** | Full setup, troubleshooting, requirements | First time setup |
| **[OPERATIONS.md](OPERATIONS.md)** | Features, subscriptions, usage tips | Using the app |
| **[TESTING.md](TESTING.md)** | Running tests, coverage, quality gates | Contributing code |

---

## 💡 Key Features

### Free Plan ✅
- 💬 100 messages/day
- 📂 3 sessions max
- 📜 100 message history
- 🔍 Search current session

### Pro Plan ($9.99/mo) 🚀
- 💬 Unlimited messages
- 📂 Unlimited sessions
- 📜 Full message history
- 🔍 Search all sessions
- 📤 Export sessions
- 📊 Analytics dashboard

---

## 🧪 Run Tests (Optional)

Verify everything works:

```bash
xcodebuild test \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination "platform=iOS Simulator,name=iPhone 17 Pro"
```

**Expected:** ✅ 248/248 tests pass

---

## ⚙️ Configuration Checklist

- [ ] Xcode 15.0+ installed
- [ ] Tuist installed (`brew install tuist`)
- [ ] `tuist generate` runs without errors
- [ ] App builds and launches
- [ ] Can create a session
- [ ] Can send a message

---

## 🆘 Common Issues (30 sec fixes)

### "tuist: command not found"
```bash
brew install tuist
```

### Build fails
```bash
tuist clean
rm -rf .xcworkspace
tuist generate
xcodebuild clean
```

### Tests fail
```bash
xcodebuild clean -workspace Momotaro.xcworkspace -scheme Momotaro
xcodebuild test -workspace Momotaro.xcworkspace -scheme Momotaro
```

### Simulator won't launch
```bash
killall "Simulator"
open -a Simulator
```

---

## 🎯 Next Steps

- **[ ] Build Project** — `tuist generate` + Press Play
- **[ ] Create Session** — "New Session" button
- **[ ] Send Message** — Type and press Send
- **[ ] Explore Settings** — Upgrade button, subscription info
- **[ ] Read OPERATIONS.md** — Full feature guide

---

## 📖 More Info

- **Full Installation:** [INSTALLATION.md](INSTALLATION.md)
- **User Guide:** [OPERATIONS.md](OPERATIONS.md)
- **Testing:** [TESTING.md](TESTING.md)
- **GitHub:** [rdreilly58/momotaro-ios](https://github.com/rdreilly58/momotaro-ios)

---

## 💬 Questions?

- Check [INSTALLATION.md](INSTALLATION.md) Troubleshooting section
- Review [OPERATIONS.md](OPERATIONS.md) FAQ
- Open issue on [GitHub](https://github.com/rdreilly58/momotaro-ios/issues)

---

✅ **You're ready!** Build Momotaro and start chatting. 🍑
