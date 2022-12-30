# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.

import globalVars

from comtypes.client import CreateObject
from errors import *
from views import sapi5SettingsDialog
from .voiceMakerInterface import *

class sapi(voiceMakerInterface):
    @classmethod
    def generateWave(cls, text, fileName):
        try:
            text = text.replace("<", "&lt;")
            engine = CreateObject('SAPI.SpVoice')
            stream = CreateObject('SAPI.SpFileStream')
            from comtypes.gen import SpeechLib
            stream.Open(fileName, SpeechLib.SSFMCreateForWrite)
            tmp = engine.Voice
            engine.Voice = cls.getVoicePointer()
            engine.AudioOutputStream = stream
            engine.speak(text)
            engine.Voice = tmp
            stream.close()
            return True
        except Exception as e:
            raise engineError("%s => %s" %(str(text), str(e)))

    @classmethod
    def getSapiVoices(cls):
        try: engine = CreateObject('SAPI.SpVoice')
        except Exception as e: raise engineError(str(e))
        return [t for t in engine.GetVoices()]

    @classmethod
    def getSapiVoiceNames(cls):
        return [v.GetDescription() for v in cls.getSapiVoices()]

    @classmethod
    def getVoicePointer(cls):
        for v in cls.getSapiVoices():
            if v.GetDescription() == globalVars.app.config["SAPI5"]["voice"]:
                return v
        raise engineError("selected voice not found")

    @classmethod
    def getName(cls):
        return _("Microsoft SAPI5")

    @classmethod
    def getSettingDialog(cls):
        return sapi5SettingsDialog.Dialog(sapi.getSapiVoiceNames())

    @classmethod
    def validateSettings(cls):
        voices = cls.getSapiVoiceNames()
        for v in voices:
            if v == globalVars.app.config["SAPI5"]["voice"]:
                return True
        return False

if __name__ == "__main__":
    for v in sapi.getSapiVoices():
        print(v.GetAttribute("Name"))
