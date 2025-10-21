"""
Setup script for deprecated json-scout package.

This setup.py is used to display deprecation warnings during pip install.
"""

from setuptools import setup
from setuptools.command.install import install
import sys


class DeprecatedInstallCommand(install):
    """Custom install command that shows deprecation warning."""
    
    def run(self):
        # Print warning before installation
        warning = """
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║  ⚠️  WARNING: You are installing a DEPRECATED package!                  ║
║                                                                          ║
║  'json-scout' has been renamed to 'json-anatomy'                        ║
║                                                                          ║
║  Please install the new package instead:                                ║
║                                                                          ║
║    pip uninstall json-scout                                             ║
║    pip install json-anatomy                                             ║
║                                                                          ║
║  This package will show errors when you try to use it.                  ║
║                                                                          ║
║  Migration Guide:                                                       ║
║  https://github.com/deamonpog/json-anatomy/blob/main/MIGRATION.md       ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
        print(warning, file=sys.stderr)
        
        # Continue with installation
        install.run(self)
        
        # Print warning after installation
        post_warning = """
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║  ⚠️  json-scout installation complete, but this package is DEPRECATED   ║
║                                                                          ║
║  To use the correct package, run:                                       ║
║    pip uninstall json-scout                                             ║
║    pip install json-anatomy                                             ║
║                                                                          ║
║  Then update your imports:                                              ║
║    import jsonscout → import jsonanatomy                                ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
        print(post_warning, file=sys.stderr)


# Read pyproject.toml for metadata (optional, for backup)
setup(
    name="json-scout",
    cmdclass={
        'install': DeprecatedInstallCommand,
    },
)
