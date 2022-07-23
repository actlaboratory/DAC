# -*- coding: utf-8 -*-
# settings dialog
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>


import wx

import constants
import simpleDialog
import views.ViewCreator

from enum import Enum,auto
from views.baseDialog import *


class configType(Enum):
	BOOL = auto()
	INT = auto()
	STRING = auto()
	DIC = auto()


class Dialog(BaseDialog):
	readerSelection = {
		"NOSPEECH": _("音声なし"),
		"AUTO": _("自動選択"),
		"SAPI5": "SAPI5",
		"CLIPBOARD": _("クリップボード出力"),
		"PCTK": "PC-Talker",
		"NVDA": "NVDA",
		"JAWS": "JAWS for Windows"
	}
	logLevelSelection = {
		"50":"CRITICAL",
		"40":"ERROR",
		"30":"WARNING",
		"20":"INFO",
		"10":"DEBUG",
		"0":"NOTSET"
	}
	colorModeSelection = {
		"white": _("標準"),
		"dark": _("ダーク")
	}
	textWrappingSelection = {
		"on":_("画面幅で折り返し"),
		"off":_("折り返さない")
	}
	languageSelection = constants.SUPPORTING_LANGUAGE

	def __init__(self):
		super().__init__("settingsDialog")
		self.iniDic = {}			#iniファイルと作ったオブジェクトの対応

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("設定"))
		self.InstallControls()
		self.load()
		self.checkBoxStatusChanged()	#初期値を反映する為一度呼び出しておく
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""

		# tab
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.tab = self.creator.tabCtrl(_("カテゴリ選択"))

		# general
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,views.ViewCreator.GridBagSizer,label=_("一般"),style=wx.ALL|wx.EXPAND,proportion=1,margin=20)
		self.logLevel,dummy = creator.combobox(_("ログ記録レベル(&L)"),list(self.logLevelSelection.values()))
		self.reader, static = creator.combobox(_("出力先(&O)"), list(self.readerSelection.values()))

		# view
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,views.ViewCreator.GridBagSizer,label=_("表示/言語"),style=wx.ALL,margin=20)
		self.language, static = creator.combobox(_("言語(&L)"), list(self.languageSelection.values()))
		self.colormode, static = creator.combobox(_("画面表示モード(&D)"), list(self.colorModeSelection.values()))
		self.textwrapping, static = creator.combobox(_("テキストの折り返し(&W)"), list(self.textWrappingSelection.values()))

		# network
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("ネットワーク"),style=wx.ALL,margin=20)
		self.update = creator.checkbox(_("起動時に更新を確認(&U)"))
		self.usemanualsetting = creator.checkbox(_("プロキシサーバーの情報を手動で設定する(&M)"), self.checkBoxStatusChanged)
		self.server, static = creator.inputbox(_("サーバーURL"))
		self.server.hideScrollBar(wx.HORIZONTAL)
		self.port, static = creator.spinCtrl(_("ポート番号"), 0, 65535, defaultValue=8080)

		# buttons
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,style=wx.ALIGN_RIGHT)
		self.okbtn = creator.okbutton("OK", self.onOkButton, proportion=1)
		self.cancelBtn = creator.cancelbutton(_("キャンセル"), proportion=1)

	def load(self):
		# general
		self._setValue(self.reader,"speech","reader",configType.DIC,self.readerSelection)
		self._setValue(self.logLevel,"general","log_level",configType.DIC,self.logLevelSelection)

		# view
		self._setValue(self.language,"general","language",configType.DIC,self.languageSelection)
		self._setValue(self.colormode,"view","colormode",configType.DIC,self.colorModeSelection)
		self._setValue(self.textwrapping,"view","textwrapping",configType.DIC,self.textWrappingSelection)

		# network
		self._setValue(self.update, "general", "update", configType.BOOL)
		self._setValue(self.usemanualsetting, "proxy", "usemanualsetting", configType.BOOL)
		self._setValue(self.server, "proxy", "server", configType.STRING)
		self._setValue(self.port, "proxy", "port", configType.STRING)

	def onOkButton(self, event):
		result = self._save()
		event.Skip()

	def checkBoxStatusChanged(self, event=None):
		result = self.usemanualsetting.GetValue()
		self.server.Enable(result)
		self.port.Enable(result)

	def _setValue(self, obj, section, key, t, prm=None, prm2=None):
		assert isinstance(obj,wx.Window)
		assert type(section)==str
		assert type(key)==str
		assert type(t)==configType

		conf=self.app.config

		if t==configType.DIC:
			assert type(prm) == dict
			assert isinstance(obj,wx.ComboBox)
			obj.SetValue(prm[conf.getstring(section,key,prm2,prm.keys())])
		elif t==configType.BOOL:
			if prm==None:
				prm = True
			assert type(prm) == bool
			obj.SetValue(conf.getboolean(section,key,prm))
		elif t==configType.STRING:
			if prm==None:
				prm = ""
			assert type(prm) == str
			obj.SetValue(conf.getstring(section,key,prm,prm2))
		self.iniDic[obj]=(t,section,key,prm,prm2)

	def _save(self):
		conf = self.app.config
		for obj,v in self.iniDic.items():
			if v[0]==configType.DIC:
				conf[v[1]][v[2]] = list(v[3].keys())[obj.GetSelection()]
			else:
				conf[v[1]][v[2]] = obj.GetValue()
		self.app.InitSpeech()
		self.app.setProxyEnviron()
