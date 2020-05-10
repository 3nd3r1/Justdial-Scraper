# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.pyw'],
             pathex=['D:\\Coding\\freelancer\\DataScraper\\Apps\\justdial'],
             binaries=[],
             datas=[],
             hiddenimports = [
    'pygubu.builder.tkstdwidgets',
    'pygubu.builder.ttkstdwidgets',
    'pygubu.builder.widgets.dialog',
    'pygubu.builder.widgets.editabletreeview',
    'pygubu.builder.widgets.scrollbarhelper',
    'pygubu.builder.widgets.scrolledframe',
    'pygubu.builder.widgets.tkscrollbarhelper',
    'pygubu.builder.widgets.tkscrolledframe',
    'pygubu.builder.widgets.pathchooserinput',
],
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
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
