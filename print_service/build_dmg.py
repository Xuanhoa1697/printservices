import os
import subprocess
import PyInstaller.__main__

def build_app():
    # Build với PyInstaller
    PyInstaller.__main__.run([
        'app/main.py',
        '--name=PrintService',
        '--windowed',
        '--add-data=app/templates:templates',
        '--add-data=app/static:static',
        '--icon=app/static/icon.icns',
        '--clean',
        '--noconfirm'
    ])

    # Tạo DMG
    subprocess.run([
        'create-dmg',
        '--volname', 'Print Service',
        '--window-pos', '200', '120',
        '--window-size', '800', '400',
        '--icon-size', '100',
        '--icon', 'PrintService.app', '200', '190',
        '--hide-extension', 'PrintService.app',
        '--app-drop-link', '600', '185',
        'PrintService.dmg',
        'dist/'
    ])

if __name__ == '__main__':
    build_app()