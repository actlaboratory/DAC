# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.

import os
import threading
import time
import traceback
import winsound
import wx

import constants
import daisyMaker
import documentParser
import views
import voiceMaker

from errors import *
from views import mkDialog
from views import mkProgress

class daisyOutputPanel:
    def __init__(self, parent):
        self.parent = parent
        self.created = False

    def setCreator(self, creator):
        self.creator = creator
    
    def create(self):
        horizontalCreator = views.ViewCreator.ViewCreator(self.parent.viewMode, self.creator.GetPanel(), self.creator.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
        self.dirInput, tmp = horizontalCreator.inputbox(_("出力先"), style=0, proportion=1, sizerFlag=wx.ALIGN_CENTER_VERTICAL)
        self.dirInput.hideScrollBar(wx.HORIZONTAL)
        browseButton = horizontalCreator.button(_("参照"), self._onBrowseButton)
        horizontalCreator = views.ViewCreator.ViewCreator(self.parent.viewMode, self.creator.GetPanel(), self.creator.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
        self.voiceCombo, tmp = horizontalCreator.combobox(_("音声エンジン"), self.getVoiceSelections(), None, 0)
        configButton = horizontalCreator.button(_("設定"), self._onConfigButton)
        horizontalCreator = views.ViewCreator.ViewCreator(self.parent.viewMode, self.creator.GetPanel(), self.creator.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.ALIGN_RIGHT, space=10)
        controlButton = horizontalCreator.button(_("開始"), self._onStartButton)
        self.created = True

    def getVoiceSelections(self):
        result = []
        for i in voiceMaker.getVoices():
            result.append(i.getName())
        return result

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

    def daisyOutputEvent(self):
        parserIndex = self.parent.inputCategoryCombo.GetSelection()
        voiceIndex = self.voiceCombo.GetSelection()
        if parserIndex < 0 or voiceIndex < 0: #未選択
            return
        parser = documentParser.getParsers()[parserIndex]
        voice = voiceMaker.getVoices()[voiceIndex]
        try:
            if not voice.validateSettings():
                d = mkDialog.Dialog("error dialog")
                d.Initialize(_("エラー"), _("音声エンジンの設定に問題があります。音声エンジンの設定をご確認ください。"), ("OK",))
                d.Show()
                return
        except (engineError, connectionError):
            d = mkDialog.Dialog("error dialog")
            d.Initialize(_("エラー"), _("音声エンジンの初期化でエラーが発生しました。音声エンジンの設定をご確認ください。"), ("OK",))
            d.Show()
            return

        inputPath = self.parent.inputPathInput.GetValue()
        outputDir = self.dirInput.GetValue()
        if not outputDir:
            outputDir = "output"

        try:
            tBuild = daisyMaker.daisyMaker(inputPath, outputDir, parser, voice)
        except connectionError as e:
            self.parent.log.error(traceback.format_exc())
            d = mkDialog.Dialog("error dialog")
            d.Initialize(_("エラー"), _("音声エンジンに接続できませんでした。"), ("OK",))
            return d.Show()
        except engineError as e:
            self.parent.log.error(traceback.format_exc())
            d = mkDialog.Dialog("error dialog")
            d.Initialize(_("エラー"), _("音声の呼び出しに失敗しました。DACから音声エンジンの設定を行ってください。"), ("OK",))
            return d.Show()
        except Exception as e:
            self.parent.log.error(traceback.format_exc())
            d = mkDialog.Dialog("error dialog")
            d.Initialize(_("エラー"), _("音声の呼び出し中にエラーが発生しました。"), ("OK",))
            return d.Show()

        tBuild.start()
        progress = mkProgress.Dialog("convertProgress")
        progress.Initialize("", _("処理中"))
        t = threading.Thread(target=self.updateConvertProgressThread, args=(progress, tBuild))
        t.start()
        progress.Show()

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
        self.daisyOutputEvent()

    def _onConfigButton(self, evt):
        voiceIndex = self.voiceCombo.GetSelection()
        if voiceIndex < 0: #未選択
            return
        voice = voiceMaker.getVoices()[voiceIndex]
        d = voice.getSettingDialog()
        if not d:
            return
        d.Initialize()
        d.Show()

    def errorDialog(self, tBuild):
        d = mkDialog.Dialog("error dialog")
        d.Initialize(_("エラー"), _("変換中にエラーが発生しました。処理を中止します。"), ("OK",))
        r = d.Show()
        tBuild.exit()
        self.parent.log.error(tBuild.error)

    def successDialog(self, tBuild):
        winsound.PlaySound(constants.SOUND_SUCCESS, winsound.SND_ASYNC)
        d = mkDialog.Dialog("convert success dialog")
        d.Initialize(_("完了"), _("変換が完了しました。"), ("OK",))
        r = d.Show()
        tBuild.exit()
        self.parent.log.debug("convert success.")
