# -*- coding: utf-8 -*-
#voicevox settings dialog
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>
# Copyright (C) 2022 Hiroki Fujii <hfujii@hisystron.com>


from email.policy import default
import wx
import traceback

import constants
import simpleDialog
import views.ViewCreator
from voiceMaker import voicevox

from enum import Enum,auto
from views.baseDialog import *
from errors import *
from views import mkDialog


class configType(Enum):
	BOOL = auto()
	INT = auto()
	STRING = auto()
	DIC = auto()


class Dialog(BaseDialog):
	def __init__(self):
		self.voiceSelection = {}
		super().__init__("settingsDialog")
		self.iniDic = {}			#iniファイルと作ったオブジェクトの対応

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("設定"))
		self.hasError = False
		try:
			voices = ([ v["name"] for v in voicevox.voicevox.getVoiceSelections() ])
		except connectionError as e:
			self.log.error(traceback.format_exc())
			d = mkDialog.Dialog("error dialog")
			d.Initialize(_("エラー"), _("Voicevoxに接続できません。Voicevoxが正しく起動しているか確認してください。"), ("OK",))
			d.Show()
			self.hasError = True
			return
		except Exception as e:
			self.log.error(traceback.format_exc())
			d = mkDialog.Dialog("error dialog")
			d.Initialize(_("エラー"), _("Voicevoxとの接続中にエラーが発生しました。"), ("OK",))
			d.Show()
			self.hasError = True
			return
		voices.sort()
		for v in voices:
			self.voiceSelection[v] = v
		self.InstallControls()
		self.load()
		return True

	def Show(self):
		if self.hasError == False:
			super().Show()
	
	def InstallControls(self):
		"""いろんなwidgetを設置する。"""

		# tab
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.voice, damy = self.creator.combobox(_("声"), list(self.voiceSelection.values()))
		#self.kana = self.creator.checkbox(_("英語をカタカナに変換する"))

		# buttons
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,style=wx.ALIGN_RIGHT)
		self.okbtn = creator.okbutton("OK", self.onOkButton, proportion=1)
		self.cancelBtn = creator.cancelbutton(_("キャンセル"), proportion=1)

	def load(self):
		self._setValue(self.voice, "Voicevox","voice", configType.DIC, self.voiceSelection, list(self.voiceSelection.keys())[0])
		#self._setValue(self.kana, "Voicevox", "kanaConvert", configType.BOOL, False)


	def onOkButton(self, event):
		result = self._save()
		event.Skip()

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
