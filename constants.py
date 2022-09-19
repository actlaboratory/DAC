# -*- coding: utf-8 -*-
#constant values
# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.

import wx

#アプリケーション基本情報
APP_FULL_NAME = "Document to Audio book Converter"#アプリケーションの完全な名前
APP_NAME="DAC"#アプリケーションの名前
APP_ICON = None
APP_VERSION="1.0.0"
APP_LAST_RELEASE_DATE="20xx-xx-xx"
APP_COPYRIGHT_YEAR="2022"
APP_LICENSE="GNU AFFERO GENERAL PUBLIC LICENSE Version3"
APP_DEVELOPERS="Hiroki Fujii - ACT Laboratory"
APP_DEVELOPERS_URL="https://actlab.org/"
APP_DETAILS_URL="https://actlab.org/software/DAC"
APP_COPYRIGHT_MESSAGE = "Copyright (c) %s %s All lights reserved." % (APP_COPYRIGHT_YEAR, APP_DEVELOPERS)

SUPPORTING_LANGUAGE={"ja-JP": "日本語","en-US": "English"}

#各種ファイル名
LOG_PREFIX="DAC"
LOG_FILE_NAME="DAC.log"
SETTING_FILE_NAME="settings.ini"
KEYMAP_FILE_NAME="keymap.ini"



#フォントの設定可能サイズ範囲
FONT_MIN_SIZE=5
FONT_MAX_SIZE=35

#３ステートチェックボックスの状態定数
NOT_CHECKED=wx.CHK_UNCHECKED
HALF_CHECKED=wx.CHK_UNDETERMINED
FULL_CHECKED=wx.CHK_CHECKED

#build関連定数
BASE_PACKAGE_URL = None
PACKAGE_CONTAIN_ITEMS = ("ffmpeg.exe", "success.wav")#パッケージに含めたいファイルやfolderがあれば指定
NEED_HOOKS = ()#pyinstallerのhookを追加したい場合は指定
STARTUP_FILE = "DAC.py"#起動用ファイルを指定
UPDATER_URL = "https://github.com/actlaboratory/updater/releases/download/1.0.0/updater.zip"

# update情報
UPDATE_URL = "https://actlab.org/api/checkUpdate"
UPDATER_VERSION = "1.0.0"
UPDATER_WAKE_WORD = "hello"



# 音声ファイル
SOUND_SUCCESS = "success.wav"
