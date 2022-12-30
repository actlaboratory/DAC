from . import voicevox
from views import voicevoxSettingsDialog

class Coeiroink(voicevox.voicevox):
	_PORT = 50031
	_CONFIG_SECTION = "Coeiroink"

	@classmethod
	def getName(cls):
		return "COEIROINK"
