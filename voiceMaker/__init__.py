# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.

from . import sapi
from . import voicevox
from . import coeiroink

def getVoices():
	return [sapi.sapi,voicevox.voicevox, coeiroink.Coeiroink]
