import wx

import views


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
