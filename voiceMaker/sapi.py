from comtypes.client import CreateObject

def outputSapiSpeech(text, fileName):
	try:
		text = text.replace("<", "&lt;")
		engine = CreateObject('SAPI.SpVoice')
		stream = CreateObject('SAPI.SpFileStream')
		from comtypes.gen import SpeechLib
		stream.Open(fileName, SpeechLib.SSFMCreateForWrite)
		engine.AudioOutputStream = stream
		engine.speak(text)
		stream.close()
		return True
	except Exception as e:
		print("%s => %s" %(str(text), str(e)))
		return False

def getSapiVoices():
	engine = CreateObject('SAPI.SpVoice')
	category = CreateObject("SAPI.SpObjectTokenCategory")
	category.SetID(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices", False)
	voices = [t for t in category.EnumerateTokens() ]
	return voices

if __name__ == "__main__":
	for v in getSapiVoices():
		print(v.GetAttribute("Name"))