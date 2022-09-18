# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.

import os
import winsound
import time
import wx
import threading

import constants
import views
from errors import *
from views import mkDialog
from views import mkProgress
from views import sapi5SettingsDialog
from views import voicevoxSettingsDialog
import daisyMaker


class daisyOutputPanel:
    def __init__(self, parent):
        self.parent = parent
        self.created = False
        # SAPI settings
        self.sapiSelection = [_("Microsoft SAPI5"), _("Voicevox")]
        self.sapiSelected = 0

    def setCreator(self, creator):
        self.creator = creator
    
    def create(self):
        horizontalCreator = views.ViewCreator.ViewCreator(self.parent.viewMode, self.creator.GetPanel(), self.creator.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
        self.dirInput, tmp = horizontalCreator.inputbox(_("出力先"), style=0, proportion=1, sizerFlag=wx.ALIGN_CENTER_VERTICAL)
        self.dirInput.hideScrollBar(wx.HORIZONTAL)
        browseButton = horizontalCreator.button(_("参照"), self._onBrowseButton)
        horizontalCreator = views.ViewCreator.ViewCreator(self.parent.viewMode, self.creator.GetPanel(), self.creator.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
        sapiCombo, tmp = horizontalCreator.combobox(_("音声エンジン"), self.sapiSelection, None, self.sapiSelected)
        sapiCombo.Bind(wx.EVT_COMBOBOX, self._onSapiSelected)
        configButton = horizontalCreator.button(_("設定"), self._onConfigButton)
        horizontalCreator = views.ViewCreator.ViewCreator(self.parent.viewMode, self.creator.GetPanel(), self.creator.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
        controlButton = horizontalCreator.button(_("開始"), self._onStartButton)
        self.created = True


    def clear(self):
        if self.created:
            self.creator.GetSizer().Clear(True)
            self.created = False
        else:
            return

    
    def updateConvertProgressThread(self,progress, tBuild):
        countTmp = 0
        message = False
        showProgress = True
        while tBuild.exited == False:
            time.sleep(0.1)
            count = tBuild.count
            if countTmp != count:
                countTmp = count
                wx.CallAfter(progress.update, count, None, tBuild.total)
            if tBuild.error != None and message == False:
                message = True
                wx.CallAfter(self.errorDialog, tBuild)
            if tBuild.finished == True and message == False:
                message = True
                wx.CallAfter(self.successDialog, tBuild)
            if progress.status == wx.CANCEL:
                tBuild.cancel()
        wx.CallAfter(progress.Destroy)

    def daisyOutputEvent(self, category, voice, input, output="output"):
        try:
            if category == daisyMaker.SAPI:
                voices = daisyMaker.getSapiVoices()
                pointer = None
                for v in voices:
                    if v["name"] == voice: pointer = v["pointer"]
                if pointer == None: raise engineError("SAPI voice not found")
                tBuild = daisyMaker.daisyMaker(input, output, daisyMaker.SAPI, {
                    "voicePointer": pointer
                })
            elif category == daisyMaker.VOICEVOX:
                voices = daisyMaker.getVoicevoxVoices()
                id = None
                for v in voices:
                    if v["name"] == voice: id = v["id"]
                if id == None: raise engineError("Voicevox voice not found")
                tBuild = daisyMaker.daisyMaker(input, output, daisyMaker.VOICEVOX, {
                    "voiceID": id,
                    "kanaConvert": False, #self.parent.app.config["Voicevox"]["kanaConvert"]
                })
            else:
                return
        except connectionError as e:
            d = mkDialog.Dialog("error dialog")
            d.Initialize(_("エラー"), _("音声エンジンに接続できませんでした。"), ("OK",))
            return d.Show()
        except engineError as e:
            d = mkDialog.Dialog("error dialog")
            d.Initialize(_("エラー"), _("音声の呼び出しに失敗しました。DACから音声エンジンの設定を行ってください。"), ("OK",))
            return d.Show()
        except Exception as e:
            d = mkDialog.Dialog("error dialog")
            d.Initialize(_("エラー"), _("音声の呼び出し中にエラーが発生しました。"), ("OK",))
            return d.Show()

        tBuild.start()
        progress = mkProgress.Dialog("convertProgress")
        progress.Initialize("", _("処理中"))
        t = threading.Thread(target=self.updateConvertProgressThread, args=(progress, tBuild))
        t.start()
        progress.Show()


    def _onSapiSelected(self, evt):
        selected = evt.GetSelection()
        self.sapiSelected = selected

    def _onBrowseButton(self, evt):
        d = wx.DirDialog(None, _("出力先フォルダの選択"), style=wx.FD_SAVE)
        r = d.ShowModal()
        if r != wx.ID_OK: return
        path = d.GetPath()
        if path == None or path == "": return
        self.dirInput.SetLabel(path)
    
    def _onStartButton(self, evt):
        message = []
        if os.path.exists(self.parent.inputPathInput.GetValue()) == False: message.append(_("変換元が正しく指定されていません。"))
        if self.dirInput.GetValue() == "": message.append(_("出力先が指定されていません。"))
        if len(message) != 0:
            message.insert(0, _("変換できません。設定内容を確認してください。"))
            d = mkDialog.Dialog("error dialog")
            d.Initialize(_("エラー"), "\n".join(message), ("OK",))
            return d.Show()
        if self.sapiSelected == 0: self.daisyOutputEvent(daisyMaker.SAPI, self.parent.app.config["SAPI5"]["voice"], self.parent.inputPathInput.GetValue(), self.dirInput.GetValue())
        elif self.sapiSelected == 1: self.daisyOutputEvent(daisyMaker.VOICEVOX, self.parent.app.config["Voicevox"]["voice"], self.parent.inputPathInput.GetValue(), self.dirInput.GetValue())

    def _onConfigButton(self, evt):
        if self.sapiSelected == 0:
            d = sapi5SettingsDialog.Dialog()
            d.Initialize()
            d.Show()
        elif self.sapiSelected == 1:
            d = voicevoxSettingsDialog.Dialog()
            d.Initialize()
            d.Show()

    def errorDialog(self, tBuild):
        d = mkDialog.Dialog("error dialog")
        d.Initialize(_("エラー"), _("変換中にエラーが発生しました。処理を中止します。"), ("OK",))
        r = d.Show()
        tBuild.exit()
        print(tBuild.error, flush=True)

    def successDialog(self, tBuild):
        winsound.PlaySound(constants.SOUND_SUCCESS, winsound.SND_ASYNC)
        d = mkDialog.Dialog("convert success dialog")
        d.Initialize(_("完了"), _("変換が完了しました。"), ("OK",))
        r = d.Show()
        tBuild.exit()
        print("convert success.", flush=True)

