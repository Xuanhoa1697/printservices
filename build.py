import PyInstaller.__main__
import os
import shutil

def build_app():
    # Build với PyInstaller
    PyInstaller.__main__.run([
        'main.py',
        '--name=PrintService',
        '--windowed',
        '--add-data=.venv/Lib/site-packages/escpos/capabilities.json:escpos',
        '--hidden-import=flask',
        '--hidden-import=escpos',
        '--hidden-import=PIL',
        '--clean',
        '--onefile',
        '--noconfirm',
        '--icon=printicon.icns'
    ])

    # Tạo thư mục DMG
    dmg_folder = "PrintService.dmg"
    if os.path.exists(dmg_folder):
        shutil.rmtree(dmg_folder)
    os.makedirs(dmg_folder)

    # Copy ứng dụng vào thư mục DMG
    shutil.copytree("dist/PrintService.app", f"{dmg_folder}/PrintService.app")

    # Tạo symbolic link đến Applications
    os.symlink("/Applications", f"{dmg_folder}/Applications")

if __name__ == '__main__':
    build_app()