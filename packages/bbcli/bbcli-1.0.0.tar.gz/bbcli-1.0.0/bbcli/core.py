import sys

def live():
    """Display deprecation notice and exit."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                         ⚠️  DEPRECATION NOTICE ⚠️                          ║
║                                                                            ║
║  The Python version of bbcli is DEPRECATED and no longer maintained.       ║
║                                                                            ║
║  Please uninstall this version and install the new Rust version:           ║
║                                                                            ║
║  UNINSTALL:                                                                ║
║    pip uninstall bbcli                                                     ║
║                                                                            ║
║  INSTALL NEW VERSION:                                                      ║
║    eget hako/bbcli                                                         ║
║                                                                            ║
║  OR                                                                        ║
║    cargo binstall bbc-news-cli                                             ║
║                                                                            ║
║  OR                                                                        ║
║    cargo install bbc-news-cli                                              ║
║                                                                            ║
║  Repository: https://github.com/hako/bbcli                                 ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    sys.exit(0)
