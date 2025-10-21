# ⚠️ DEPRECATED: json-scout

## This package has been renamed to `json-anatomy`

**Please uninstall `json-scout` and install `json-anatomy` instead.**

---

## Why was it renamed?

The package has been rebranded to better reflect its purpose of dissecting and analyzing JSON structures, similar to how anatomical analysis examines biological structures in detail.

---

## Migration Instructions

### Quick Migration

```bash
# Uninstall the old package
pip uninstall json-scout -y

# Install the new package
pip install json-anatomy
```

### Update Your Code

**Before (json-scout):**
```python
import jsonscout as js

explorer = js.Xplore(data)
```

**After (json-anatomy):**
```python
import jsonanatomy as ja

explorer = ja.Xplore(data)
```

### Complete Migration Guide

For detailed migration instructions, including automated scripts and troubleshooting:

**📖 [View Complete Migration Guide](https://github.com/deamonpog/json-anatomy/blob/main/MIGRATION.md)**

---

## New Package Information

- **PyPI**: https://pypi.org/project/json-anatomy/
- **Documentation**: https://deamonpog.github.io/json-anatomy/
- **Repository**: https://github.com/deamonpog/json-anatomy
- **Issues**: https://github.com/deamonpog/json-anatomy/issues

---

## What Changed?

### Package Names
- **Distribution**: `json-scout` → `json-anatomy`
- **Import**: `jsonscout` → `jsonanatomy`

### What Stayed the Same?
✅ **All functionality remains identical**
- Same classes: `Explore`, `Maybe`, `SimpleXML`, `Xplore`
- Same methods and API
- Same features

**Only the names changed!**

---

## Support

If you encounter any issues during migration:

1. Check the [Migration Guide](https://github.com/deamonpog/json-anatomy/blob/main/MIGRATION.md)
2. Review the [CHANGELOG](https://github.com/deamonpog/json-anatomy/blob/main/CHANGELOG.md)
3. Open an [Issue](https://github.com/deamonpog/json-anatomy/issues)

---

## Timeline

- **v0.1.0**: Original release as `json-scout`
- **v0.1.1**: Deprecation notice (this version)
- **Future**: Package renamed to `json-anatomy`

---

## License

Apache License 2.0 - See [LICENSE](https://github.com/deamonpog/json-anatomy/blob/main/LICENSE)

---

**⚠️ This package will not receive further updates. All development continues as `json-anatomy`.**
