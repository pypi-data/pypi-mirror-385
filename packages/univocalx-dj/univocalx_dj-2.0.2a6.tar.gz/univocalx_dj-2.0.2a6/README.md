# Data Journalist

a cli/sdk cli tool for managing datasets.

## Build Desktop
### Windows
```
poetry run pyinstaller --clean --noconfirm desktop.spec
```

### Linux
```
sudo apt install python3.12-tk tk-dev
sudo apt-get update
sudo apt-get install -y \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxkbcommon-x11-0 \
    libxcb-render-util0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-shape0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xkb1 \
    libx11-xcb1

poetry run pyinstaller --clean --noconfirm desktop.spec
```