import time
import wx
import threading

import views
from views import mkProgress
import daisyMaker


def createDaisyOutputPanel(viewMode, parent, creator, sapiDefault, sapiSelection, sapiActivateEvent, outputVoiceConfigEvent, startEvent):
    horizontalCreator = views.ViewCreator.ViewCreator(viewMode, parent.GetPanel(), parent.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
    dirInput, tmp = horizontalCreator.inputbox(_("出力先"), style=0, proportion=1, sizerFlag=wx.ALIGN_CENTER_VERTICAL)
    dirInput.hideScrollBar(wx.HORIZONTAL)
    browseButton = horizontalCreator.button(_("参照"))
    horizontalCreator = views.ViewCreator.ViewCreator(viewMode, parent.GetPanel(), parent.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
    sapiCombo, tmp = horizontalCreator.combobox(_("音声エンジン"), state=sapiDefault, selection=sapiSelection)
    configButton = horizontalCreator.button(_("詳細設定"), outputVoiceConfigEvent)
    horizontalCreator = views.ViewCreator.ViewCreator(viewMode, parent.GetPanel(), parent.GetSizer(), wx.HORIZONTAL, style=wx.ALL | wx.EXPAND, space=10)
    controlButton = horizontalCreator.button(_("開始"), startEvent)

def updateConvertProgressThread(progress, tBuild):
    countTmp = 0
    while tBuild.finished == False:
        time.sleep(0.1)
        count = tBuild.count
        if countTmp != count:
            countTmp = count
            wx.YieldIfNeeded()
            progress.update(count, None, tBuild.total)
    progress.Destroy()

def daisyOutputEvent(sapi5Voice, input, output="output"):
    voices = daisyMaker.getSapiVoices()
    pointer = None
    for v in voices:
        if v["name"] == sapi5Voice: pointer = v["pointer"]
    if pointer == None: return
    tBuild = daisyMaker.daisyMaker(input, daisyMaker.SAPI, {
        "voicePointer": pointer
    })
    tBuild.start()
    progress = mkProgress.Dialog("convertProgress")
    progress.Initialize("", _("処理中"))
    t = threading.Thread(target=updateConvertProgressThread, args=(progress, tBuild))
    t.start()
    progress.Show()
