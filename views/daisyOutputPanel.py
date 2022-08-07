import time
import wx
import threading

import views
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
        dirInput, tmp = horizontalCreator.inputbox(_("出力先"), style=0, proportion=1, sizerFlag=wx.ALIGN_CENTER_VERTICAL)
        dirInput.hideScrollBar(wx.HORIZONTAL)
        browseButton = horizontalCreator.button(_("参照"))
        horizontalCreator = views.ViewCreator.ViewCreator(self.parent.viewMode, self.creator.GetPanel(), self.creator.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
        sapiCombo, tmp = horizontalCreator.combobox(_("音声エンジン"), self.sapiSelection, None, self.sapiSelected)
        sapiCombo.Bind(wx.EVT_COMBOBOX, self._onSapiSelected)
        configButton = horizontalCreator.button(_("詳細設定"), self._onConfigButton)
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
        while tBuild.finished == False:
            time.sleep(0.1)
            count = tBuild.count
            if countTmp != count:
                countTmp = count
                wx.YieldIfNeeded()
                progress.update(count, None, tBuild.total)
        progress.Destroy()

    def daisyOutputEvent(self, category, voice, input, output="output"):
        if category == daisyMaker.SAPI:
            voices = daisyMaker.getSapiVoices()
            pointer = None
            for v in voices:
                if v["name"] == voice: pointer = v["pointer"]
            if pointer == None: return
            tBuild = daisyMaker.daisyMaker(input, daisyMaker.SAPI, {
                "voicePointer": pointer
            })
        elif category == daisyMaker.VOICEVOX:
            voices = daisyMaker.getVoicevoxVoices()
            id = None
            for v in voices:
                if v["name"] == voice: id = v["id"]
            if id == None: return
            tBuild = daisyMaker.daisyMaker(input, daisyMaker.VOICEVOX, {
                "voiceID": id
            })
        else:
            return
        tBuild.start()
        progress = mkProgress.Dialog("convertProgress")
        progress.Initialize("", _("処理中"))
        t = threading.Thread(target=self.updateConvertProgressThread, args=(progress, tBuild))
        t.start()
        progress.Show()


    def _onSapiSelected(self, evt):
        selected = evt.GetSelection()
        self.sapiSelected = selected

    def _onStartButton(self, evt):
        if self.sapiSelected == 0: self.daisyOutputEvent(daisyMaker.SAPI, self.parent.app.config["SAPI5"]["voice"], self.parent.inputPathInput.GetValue())
        elif self.sapiSelected == 1: self.daisyOutputEvent(daisyMaker.VOICEVOX, self.parent.app.config["Voicevox"]["voice"], self.parent.inputPathInput.GetValue())

    def _onConfigButton(self, evt):
        if self.sapiSelected == 0:
            d = sapi5SettingsDialog.Dialog()
            d.Initialize()
            d.Show()
        elif self.sapiSelected == 1:
            d = voicevoxSettingsDialog.Dialog()
            d.Initialize()
            d.Show()
