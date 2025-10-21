"""
⚠️ DEPRECATED: json-scout has been renamed to json-anatomy

This package has been renamed to 'json-anatomy'.
Please uninstall 'json-scout' and install 'json-anatomy' instead.

Migration Steps
---------------
1. Uninstall: pip uninstall json-scout
2. Install: pip install json-anatomy
3. Update imports: import jsonscout → import jsonanatomy

For detailed instructions, see:
https://github.com/deamonpog/json-anatomy/blob/main/MIGRATION.md

New Package Information
-----------------------
- PyPI: https://pypi.org/project/json-anatomy/
- Docs: https://deamonpog.github.io/json-anatomy/
- Repo: https://github.com/deamonpog/json-anatomy

All functionality remains identical. Only the package name changed!
"""

import warnings
import sys

# Show deprecation warning immediately on import
_DEPRECATION_MESSAGE = """
╔════════════════════════════════════════════════════════════════════╗
║  ⚠️  DEPRECATION WARNING: json-scout → json-anatomy               ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  The 'json-scout' package has been renamed to 'json-anatomy'.     ║
║                                                                    ║
║  Please migrate to the new package:                               ║
║                                                                    ║
║    1. pip uninstall json-scout                                    ║
║    2. pip install json-anatomy                                    ║
║    3. Update imports: import jsonscout → import jsonanatomy       ║
║                                                                    ║
║  Migration Guide:                                                 ║
║  https://github.com/deamonpog/json-anatomy/blob/main/MIGRATION.md ║
║                                                                    ║
║  All functionality remains identical. Only names changed!         ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
"""

# Print to stderr so it's visible even if stdout is redirected
print(_DEPRECATION_MESSAGE, file=sys.stderr)

# Also issue a proper Python warning
warnings.warn(
    "The 'json-scout' package has been renamed to 'json-anatomy'. "
    "Please uninstall json-scout and install json-anatomy instead. "
    "See https://github.com/deamonpog/json-anatomy/blob/main/MIGRATION.md for details.",
    DeprecationWarning,
    stacklevel=2
)

__version__ = "0.1.1"
__author__ = "Chathura Jayalath"
__email__ = "chathura@example.com"

# Provide helpful error messages for common imports
def _create_deprecation_error(name):
    """Create a helpful error for deprecated imports."""
    raise ImportError(
        f"Cannot import '{name}' from deprecated 'jsonscout' package. "
        f"Please install 'json-anatomy' and use: from jsonanatomy import {name}"
    )

# Make common imports fail with helpful messages
class _DeprecatedModule:
    """Placeholder that raises helpful errors on attribute access."""
    
    def __getattr__(self, name):
        _create_deprecation_error(name)

# Replace this module with the deprecation wrapper
sys.modules[__name__] = _DeprecatedModule()
