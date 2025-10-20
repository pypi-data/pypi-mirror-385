# PyPI Name Reservation - Quick Guide

**Date**: October 20, 2025  
**Package**: `sortypy`  
**Purpose**: Reserve the package name on PyPI without exposing source code

---

## ✅ Placeholder Package Created

Location: `.pypi-placeholder/` (gitignored, kept locally)

**Contents**:
```
.pypi-placeholder/
├── pyproject.toml      # Minimal package metadata
├── README.md           # Placeholder notice
├── LICENSE             # Apache-2.0 license
└── src/
    └── sortypy/
        └── __init__.py # Minimal module with version
```

**Version**: 0.0.1 (placeholder)  
**Status**: Development Status :: 1 - Planning

---

## 🚀 Step-by-Step Upload Instructions

### Prerequisites (Already Done ✅)
- [x] You're logged into PyPI
- [x] Placeholder package created

### Step 1: Install Build Tools

```bash
# Install build and upload tools
pip install --upgrade build twine
```

### Step 2: Build the Placeholder Package

```bash
# Navigate to placeholder directory
cd .pypi-placeholder/

# Build the distribution
python -m build

# This creates:
# - dist/sortypy-0.0.1-py3-none-any.whl
# - dist/sortypy-0.0.1.tar.gz
```

### Step 3: Upload to PyPI

```bash
# Upload using twine (you're already logged in)
python -m twine upload dist/*

# You'll see:
# Uploading distributions to https://upload.pypi.org/legacy/
# Uploading sortypy-0.0.1-py3-none-any.whl
# Uploading sortypy-0.0.1.tar.gz
# View at: https://pypi.org/project/sortypy/0.0.1/
```

### Step 4: Verify

```bash
# Check that the package is live
curl -s https://pypi.org/pypi/sortypy/json | head -20

# Or visit in browser:
# https://pypi.org/project/sortypy/
```

---

## 🔒 What This Placeholder Does

✅ **Reserves** the name `sortypy` on PyPI  
✅ **Shows** your project intent and GitHub link  
✅ **Prevents** others from taking the name  
✅ **Displays** proper licensing and author information  
✅ **Warns** users this is a placeholder (DO NOT INSTALL message)

❌ **Does NOT** expose your actual source code  
❌ **Does NOT** provide any functionality  
❌ **Does NOT** appear in your Git repository (gitignored)

---

## 📝 After Upload

### Keep the Placeholder Files
The `.pypi-placeholder/` directory is gitignored and will stay on your local machine only. You can:
- Keep it for reference
- Delete it after successful upload (you won't need it again)

### Future Releases
When you're ready to publish the real package:

1. Update version in main `pyproject.toml` (e.g., to `0.1.0`)
2. Build from project root: `python -m build`
3. Upload: `python -m twine upload dist/*`
4. PyPI will replace v0.0.1 with your real release

### Verify Name Ownership

```bash
# List your packages on PyPI
# Visit: https://pypi.org/user/[your-username]/

# You should see 'sortypy' listed!
```

---

## 🎯 Expected Timeline

- **Today**: Upload placeholder v0.0.1 ✅ (THIS STEP)
- **Q1 2026**: Replace with real v0.1.0 release
- **Q4 2026**: Stable v1.0.0 release

---

## ⚠️ Important Notes

1. **Once uploaded, you cannot delete versions from PyPI** - you can only mark them as "yanked"
2. **This is intentional** - the placeholder serves its purpose and will be replaced
3. **PyPI page will show**:
   - Your name and co-author's name
   - GitHub repository link
   - Clear warning it's a placeholder
   - Apache-2.0 license

4. **Security**: The placeholder is safe to upload - it contains no sensitive information or actual code

---

## 🆘 Troubleshooting

### "Package already exists"
- The name is already taken - choose a different name
- Or you've already uploaded it successfully!

### "Invalid credentials"
- Run: `python -m twine upload dist/* --verbose`
- You may need to re-authenticate

### "Build failed"
- Ensure you're in `.pypi-placeholder/` directory
- Check that `pyproject.toml` is present
- Try: `python -m build --version` to verify build is installed

### "File already exists"
- You've already uploaded this version
- Verify at: https://pypi.org/project/sortypy/

---

## ✅ Success Checklist

After completing the upload:

- [ ] Visited https://pypi.org/project/sortypy/
- [ ] Confirmed package page shows placeholder warning
- [ ] Verified both authors listed correctly
- [ ] GitHub link works
- [ ] License shows as Apache-2.0
- [ ] Package shows "Development Status :: 1 - Planning"

---

**Ready to upload?** Follow Step 1 above! 🚀
