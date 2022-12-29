# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.

import globalVars

from comtypes.client import CreateObject
from errors import *
from views import sapi5SettingsDialog
from .voiceMakerInterface import *

class sapi(voiceMakerInterface):
    def generateWave(text, fileName):
        try:
            text = text.replace("<", "&lt;")
            engine = CreateObject('SAPI.SpVoice')
            stream = CreateObject('SAPI.SpFileStream')
            from comtypes.gen import SpeechLib
            stream.Open(fileName, SpeechLib.SSFMCreateForWrite)
            tmp = engine.Voice
            engine.Voice = sapi.getVoicePointer()
            engine.AudioOutputStream = stream
            engine.speak(text)
            engine.Voice = tmp
            stream.close()
            return True
        except Exception as e:
            raise engineError("%s => %s" %(str(text), str(e)))

    def getSapiVoices():
        try: engine = CreateObject('SAPI.SpVoice')
        except Exception as e: raise engineError(str(e))
        return [t for t in engine.GetVoices()]

    def getSapiVoiceNames():
        return [v.GetDescription() for v in sapi.getSapiVoices()]

    def getVoicePointer():
        for v in sapi.getSapiVoices():
            if v.GetDescription() == globalVars.app.config["SAPI5"]["voice"]:
                return v
        raise engineError("selected voice not found")

    def getName():
        return _("Microsoft SAPI5")

    def getSettingDialog():
        return sapi5SettingsDialog.Dialog(sapi.getSapiVoiceNames())

    def validateSettings():
        voices = sapi.getSapiVoiceNames()
        for v in voices:
            if v == globalVars.app.config["SAPI5"]["voice"]:
                return True
        return False

if __name__ == "__main__":
    for v in sapi.getSapiVoices():
        print(v.GetAttribute("Name"))
