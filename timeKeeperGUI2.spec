# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['timeKeeperGUI2.py'],
             pathex=['C:\\Users\\magnu\\OneDrive\\Documents\\Coding\\Axel_Datenbank\\timeKeeper2'],
             binaries=[],
             datas=[('C:\\Users\\magnu\\AppData\\Local\\Programs\\Python\\Python38\\Lib\\site-packages\\customtkinter', 'customtkinter/')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='timeKeeperGUI2',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
