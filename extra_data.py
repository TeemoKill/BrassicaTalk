import os

# This is for pyinstaller --onefile to include the app icon into the exe file
BASE_DIR = os.path.dirname(__file__)
ICON_PATH = os.path.join(BASE_DIR, "brassica_icon.ico")
