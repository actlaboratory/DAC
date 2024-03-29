﻿# -*- coding: utf-8 -*-
#main view
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2021 yamahubuki <itiro.ishino@gmail.com>
# Copyright (C) 2022 Hiroki Fujii <hfujii@hisystron.com>

import time, threading
import wx

import constants
import documentParser
import globalVars
import update
import menuItemsStore

from .base import *
from simpleDialog import *

from views import globalKeyConfig
from views import settingsDialog
from views import versionDialog
from views import daisyOutputPanel


class MainView(BaseView):
	def __init__(self):
		# support file categories
		self.INPUT_FILE_CATEGORY_DEFAULT = 0
		self.OUTPUT_FILE_CATEGORY_DEFAULT = 0
		self.OUTPUT_FILE_CATEGORIES = [_("音声DAISY図書 Ver2.02"),]
		self.outputPanels = [daisyOutputPanel.daisyOutputPanel(self)]

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

	def getInputFileCategories(self):
		result = []
		for i in documentParser.getParsers():
			result.append(i.getDocumentTypeName())
		return result

	def InstallControls(self):
		verticalCreator = views.ViewCreator.ViewCreator(self.viewMode, self.creator.GetPanel(), self.creator.GetSizer(), wx.VERTICAL, style=wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, space=10)
		horizontalCreator = views.ViewCreator.ViewCreator(self.viewMode, verticalCreator.GetPanel(), verticalCreator.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
		self.inputCategoryCombo, tmp = horizontalCreator.combobox(_("変換元データの種類"), state=self.INPUT_FILE_CATEGORY_DEFAULT, selection=self.getInputFileCategories())
		horizontalCreator = views.ViewCreator.ViewCreator(self.viewMode, verticalCreator.GetPanel(), verticalCreator.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
		self.inputPathInput, tmp = horizontalCreator.inputbox(_("変換元"), style=0, proportion=1, sizerFlag=wx.ALIGN_CENTER_VERTICAL)
		self.inputPathInput.hideScrollBar(wx.HORIZONTAL)
		self.inputBrowseButton = horizontalCreator.button(_("参照"), self.events.inputBrowse)
		horizontalCreator = views.ViewCreator.ViewCreator(self.viewMode, verticalCreator.GetPanel(), verticalCreator.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
		self.outputCategoryCombo, tmp = horizontalCreator.combobox(_("出力データの種類"), state=self.OUTPUT_FILE_CATEGORY_DEFAULT, selection=self.OUTPUT_FILE_CATEGORIES)
		self.outputCreator = views.ViewCreator.ViewCreator(self.viewMode, verticalCreator.GetPanel(), verticalCreator.GetSizer(), wx.VERTICAL, style=wx.EXPAND, space=0)
		self.outputPanels[0].setCreator(self.outputCreator)
		self.outputPanels[0].create()



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
		self.RegisterMenuCommand(self.hFileMenu,{
			"FILE_EXIT": self.parent.events.exit,
		})

		#オプションメニュー
		self.RegisterMenuCommand(self.hOptionMenu,{
			"OPTION_OPTION": Events.option,
			#"OPTION_KEY_CONFIG":events.keyConfig,
		})

		#ヘルプメニュー
		self.RegisterMenuCommand(self.hHelpMenu,{
			"HELP_UPDATE": Events.checkUpdate,
			"HELP_VERSIONINFO": Events.version,
		})

		#メニューバーの生成
		self.hMenuBar.Append(self.hFileMenu,_("ファイル(&F))"))
		self.hMenuBar.Append(self.hOptionMenu,_("オプション(&O)"))
		self.hMenuBar.Append(self.hHelpMenu,_("ヘルプ(&H)"))
		target.SetMenuBar(self.hMenuBar)

class Events(BaseEvents):
	def exit(self, event):
		self.parent.hFrame.Close()

	def inputBrowse(self, evt):
		selected = self.parent.inputCategoryCombo.GetSelection()
		if selected < 0: #未選択
			return
		if documentParser.getParsers()[selected].isFromDirectory():
			d = wx.DirDialog(None, _("変換元フォルダの選択"))
		else:
			d = wx.FileDialog(None, _("変換元ファイルの選択"), wildcard=documentParser.getParsers()[selected].getWildCardString())
		r = d.ShowModal()
		if r == wx.ID_CANCEL: return
		path = d.GetPath()
		if path == "" or path == "": return
		self.parent.inputPathInput.SetLabel(path)
	
	def option(self,event=None):
		d = settingsDialog.Dialog()
		d.Initialize()
		d.Show()

	def keyConfig(self,event):
		if self.setKeymap(self.parent.identifier,_("ショートカットキーの設定"),filter=keymap.KeyFilter().SetDefault(False,False)):
			#ショートカットキーの変更適用とメニューバーの再描画
			self.parent.menu.InitShortcut()
			self.parent.menu.ApplyShortcut(self.parent.hFrame)
			self.parent.menu.Apply(self.parent.hFrame)

	def checkUpdate(self,event=None):
		update.checkUpdate()

	def version(self,event=None):
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
