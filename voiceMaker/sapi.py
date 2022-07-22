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
