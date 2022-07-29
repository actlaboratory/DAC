# -*- coding: utf-8 -*-
#main view
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2021 yamahubuki <itiro.ishino@gmail.com>

import wx

import constants
import globalVars
import update
import menuItemsStore

from .base import *
from simpleDialog import *

from views import globalKeyConfig
from views import sample
from views import settingsDialog
from views import versionDialog

class MainView(BaseView):
	def __init__(self):
		# support file categories
		self.INPUT_FILE_CATEGORY_DEFAULT = 0
		self.INPUT_FILE_CATEGORIES = [_("EPUBファイル")]
		self.OUTPUT_FILE_CATEGORY_DEFAULT = 0
		self.OUTPUT_FILE_CATEGORIES = [_("音声DAISY図書")]

		# SAPI settings
		self.SAPI = [_("Microsoft SAPI5"), _("Voicevox")]
		self.SAPI_DEFAULT = 0
		self.VOICE_SPEED = [_("遅い"), _("標準"), _("速い"), _("より速い")]
		self.VOICE_SPEED_DEFAULT = 1
		self.BREATHING_TIME = [_("速度に最適化"), _("短い"), _("標準"), _("長い")]
		self.BREATHING_TIME_DEFAULT = 0
		
		super().__init__("mainView")
		self.log.debug("created")
		self.events=Events(self,self.identifier)
		title=constants.APP_NAME
		super().Initialize(
			title,
			self.app.config.getint(self.identifier,"sizeX",800,400),
			self.app.config.getint(self.identifier,"sizeY",600,300),
			self.app.config.getint(self.identifier,"positionX",50,0),
			self.app.config.getint(self.identifier,"positionY",50,0)
		)
		self.InstallMenuEvent(Menu(self.identifier),self.events.OnMenuSelect)
		self.InstallControls()

	def InstallControls(self):
		verticalCreator = views.ViewCreator.ViewCreator(self.viewMode, self.creator.GetPanel(), self.creator.GetSizer(), wx.VERTICAL, style=wx.ALL | wx.EXPAND, space=10)
		horizontalCreator = views.ViewCreator.ViewCreator(self.viewMode, verticalCreator.GetPanel(), verticalCreator.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
		self.inputCategoryCombo, tmp = horizontalCreator.combobox(_("変換元データの種類"), state=self.INPUT_FILE_CATEGORY_DEFAULT, selection=self.INPUT_FILE_CATEGORIES)
		horizontalCreator = views.ViewCreator.ViewCreator(self.viewMode, verticalCreator.GetPanel(), verticalCreator.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
		self.inputPathInput, tmp = horizontalCreator.inputbox(_("変換元"), style=0, proportion=1, sizerFlag=wx.ALIGN_CENTER_VERTICAL)
		self.inputPathInput.hideScrollBar(wx.HORIZONTAL)
		self.inputBrowseButton = horizontalCreator.button(_("参照"))
		horizontalCreator = views.ViewCreator.ViewCreator(self.viewMode, verticalCreator.GetPanel(), verticalCreator.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
		self.outputCategoryCombo, tmp = horizontalCreator.combobox(_("出力データの種類"), state=self.OUTPUT_FILE_CATEGORY_DEFAULT, selection=self.OUTPUT_FILE_CATEGORIES)
		horizontalCreator = views.ViewCreator.ViewCreator(self.viewMode, verticalCreator.GetPanel(), verticalCreator.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
		self.outputDirInput, tmp = horizontalCreator.inputbox(_("出力先"), style=0, proportion=1, sizerFlag=wx.ALIGN_CENTER_VERTICAL)
		self.outputDirInput.hideScrollBar(wx.HORIZONTAL)
		self.outputBrowseButton = horizontalCreator.button(_("参照"))
		horizontalCreator = views.ViewCreator.ViewCreator(self.viewMode, verticalCreator.GetPanel(), verticalCreator.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
		self.sapiCombo, tmp = horizontalCreator.combobox(_("音声エンジン"), state=self.SAPI_DEFAULT, selection=self.SAPI)
		self.button = horizontalCreator.button(_("詳細設定"))
		horizontalCreator = views.ViewCreator.ViewCreator(self.viewMode, verticalCreator.GetPanel(), verticalCreator.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
		self.controlButton = horizontalCreator.button(_("開始"))



class Menu(BaseMenu):
	def Apply(self,target):
		"""指定されたウィンドウに、メニューを適用する。"""

		#メニュー内容をいったんクリア
		self.hMenuBar=wx.MenuBar()

		#メニューの大項目を作る
		self.hFileMenu=wx.Menu()
		self.hOptionMenu=wx.Menu()
		self.hHelpMenu=wx.Menu()

		#ファイルメニュー
		self.RegisterMenuCommand(self.hFileMenu,[
				"FILE_EXAMPLE",
		])

		#オプションメニュー
		self.RegisterMenuCommand(self.hOptionMenu,{
			#"OPTION_OPTION": events.option,
			#"OPTION_KEY_CONFIG":events.keyConfig,
		})

		#ヘルプメニュー
		self.RegisterMenuCommand(self.hHelpMenu,{
			#"HELP_UPDATE": events.checkUpdate,
			#"HELP_VERSIONINFO": events.version,
		})

		#メニューバーの生成
		self.hMenuBar.Append(self.hFileMenu,_("ファイル(&F))"))
		self.hMenuBar.Append(self.hOptionMenu,_("オプション(&O)"))
		self.hMenuBar.Append(self.hHelpMenu,_("ヘルプ(&H)"))
		target.SetMenuBar(self.hMenuBar)

class Events(BaseEvents):
	def example(self,event):
		d = sample.Dialog()
		d.Initialize()
		r = d.Show()

	def option(self,event):
		d = settingsDialog.Dialog()
		d.Initialize()
		d.Show()

	def keyConfig(self,event):
		if self.setKeymap(self.parent.identifier,_("ショートカットキーの設定"),filter=keymap.KeyFilter().SetDefault(False,False)):
			#ショートカットキーの変更適用とメニューバーの再描画
			self.parent.menu.InitShortcut()
			self.parent.menu.ApplyShortcut(self.parent.hFrame)
			self.parent.menu.Apply(self.parent.hFrame)

	def checkUpdate(self,event):
		update.checkUpdate()

	def version(self,event):
		d = versionDialog.dialog()
		d.Initialize()
		r = d.Show()

	def setKeymap(self, identifier,ttl, keymap=None,filter=None):
		if keymap:
			try:
				keys=keymap.map[identifier.upper()]
			except KeyError:
				keys={}
		else:
			try:
				keys=self.parent.menu.keymap.map[identifier.upper()]
			except KeyError:
				keys={}
		keyData={}
		menuData={}
		for refName in defaultKeymap.defaultKeymap[identifier].keys():
			title=menuItemsDic.getValueString(refName)
			if refName in keys:
				keyData[title]=keys[refName]
			else:
				keyData[title]=_("なし")
			menuData[title]=refName

		d=globalKeyConfig.Dialog(keyData,menuData,[],filter)
		d.Initialize(ttl)
		if d.Show()==wx.ID_CANCEL: return False

		keyData,menuData=d.GetValue()

		#キーマップの既存設定を置き換える
		newMap=ConfigManager.ConfigManager()
		newMap.read(constants.KEYMAP_FILE_NAME)
		for name,key in keyData.items():
			if key!=_("なし"):
				newMap[identifier.upper()][menuData[name]]=key
			else:
				newMap[identifier.upper()][menuData[name]]=""
		newMap.write()
		return True
