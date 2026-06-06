#!/usr/bin/env python
"""
SimpleFeed++ Management Utility.
Acts as the command-line entry point for database migrations, testing, and operational tasks.
"""
import os
import sys

def main():
    """Run administrative tasks."""
    # Explicitly point to the config.settings module we defined for the stateless gateway.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "CRITICAL: Failed to initialize the SimpleFeed++ environment.\n"
            "Django could not be imported. Verify that the Python 3.14+ virtual environment "
            "is active and that requirements.txt has been successfully installed."
        ) from exc
        
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
