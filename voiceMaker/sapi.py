from comtypes.client import CreateObject
from errors import *

def outputSapiSpeech(text, fileName, options):
	try:
		text = text.replace("<", "&lt;")
		engine = CreateObject('SAPI.SpVoice')
		stream = CreateObject('SAPI.SpFileStream')
		from comtypes.gen import SpeechLib
		stream.Open(fileName, SpeechLib.SSFMCreateForWrite)
		tmp = engine.Voice
		engine.Voice = options["voicePointer"]
		engine.AudioOutputStream = stream
		engine.speak(text)
		engine.Voice = tmp
		stream.close()
		return True
	except Exception as e:
		raise engineError("%s => %s" %(str(text), str(e)))

def getSapiVoices():
	try: engine = CreateObject('SAPI.SpVoice')
	except Exception as e: engineError(str(e))
	voices = [t for t in engine.GetVoices() ]
	return voices

if __name__ == "__main__":
	for v in getSapiVoices():
		print(v.GetAttribute("Name"))