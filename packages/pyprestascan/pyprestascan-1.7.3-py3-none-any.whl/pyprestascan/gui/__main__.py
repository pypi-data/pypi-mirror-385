"""
Entry point per avvio GUI tramite python -m pyprestascan.gui
"""
import sys
from .main_window import main

if __name__ == '__main__':
    sys.exit(main())
