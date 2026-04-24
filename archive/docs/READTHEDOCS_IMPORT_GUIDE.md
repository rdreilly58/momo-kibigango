# ReadTheDocs Import - Quick Start for Bob

**Status:** All documentation is ready. Just need to import the GitHub repo on ReadTheDocs.

## One-Click Import (2 minutes)

### Step 1: Go to ReadTheDocs
- **URL:** https://readthedocs.org
- Sign in with GitHub (if not already signed in)

### Step 2: Import Project
- Click **"Import a Project"** (top right)
- Look for **"ReillyDesignStudio/momo-kiji"** in the list
- If not visible, click **"Import Manually"** and search for it

### Step 3: Create Project
- Click the repo to select it
- ReadTheDocs will auto-fill project name: **momo-kiji**
- Click **"Create Project"** button

### Step 4: Wait for Build
- ReadTheDocs automatically starts building (2-3 minutes)
- Watch the build log to confirm success
- Once "Build succeeded" appears, you're done!

### Step 5: Documentation Live!
- Your docs are now live at: https://momo-kiji.readthedocs.io
- Any future GitHub push will auto-rebuild docs

---

## What's Configured

✅ **Sphinx setup** — Professional RTD theme
✅ **Python dependencies** — All in requirements.txt
✅ **Build settings** — Python 3.11, automatic builds
✅ **Documentation** — Introduction, Installation, Quickstart
✅ **GitHub integration** — Auto-rebuild on push

---

## Expected Result

After import completes:

```
Documentation Home: https://momo-kiji.readthedocs.io
├─ Introduction
├─ Installation
├─ Quickstart
├─ How It Works (stub)
├─ API Reference (stub)
└─ Contributing
```

---

## If Build Fails

**Common issues:**
- Missing Python dependencies → Check requirements.txt
- Import errors → Check conf.py paths
- Version mismatch → Update .readthedocs.yml

See `READTHEDOCS_SETUP.md` in the repo for detailed troubleshooting.

---

## After Import is Complete

1. Update website link (currently points to GitHub)
   - Change: `https://github.com/.../docs/source/index.rst`
   - To: `https://momo-kiji.readthedocs.io`

2. Test the live documentation

3. Celebrate! 🎉

---

**Time estimate:** 5 minutes total (3 min import + 2 min verification)

Questions? Check READTHEDOCS_SETUP.md in the momo-kiji repo.
