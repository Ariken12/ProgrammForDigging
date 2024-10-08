import PyInstaller.__main__

PyInstaller.__main__.run([
    '.\\App\\__main__.py',
    '--onefile',
    '--windowed',
    '--clean'
])
# PyInstaller.__main__.run([
#     '.\\Installer\\installer.py',
#     '--onefile',
#     '--windowed',
#     '--clean',
#     '--uac-admin'
# ])