# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.

import json
import requests
import time

import globalVars

from errors import *
#from englishToKanaConverter. englishToKanaConverter import EnglishToKanaConverter
from views import voicevoxSettingsDialog
from .voiceMakerInterface import *

class voicevox(voiceMakerInterface):
	_PORT = 50031
	_CONFIG_SECTION = "voicevox"

	@classmethod
	def generateWave(cls, text, fileName):
		# カナ処理
		#cnv = EnglishToKanaConverter(False)
		#if kanaConvert: text = cnv.process(text)

		# Internal Server Error(500)が出ることがあるのでリトライする
		# （HTTPAdapterのretryはうまくいかなかったので独自実装）
		# connect timeoutは10秒、read timeoutは3000秒に設定（長文対応）
		# audio_query
		query_payload = {"text": text, "speaker": cls.getSpeakerId()}
		for query_i in range(globalVars.app.config.getint(cls._CONFIG_SECTION, "max_retry", 10)):
			r = requests.post(f"http://localhost:{ cls._PORT }/audio_query", 
				params=query_payload, timeout=(10.0, 3000.0))
			if r.status_code == 200:
				query_data = r.json()
				break
			time.sleep(1)
		else:
			raise connectionError("Make audio query faild.")

		# synthesis
		synth_payload = {"speaker": cls.getSpeakerId()}
		for synth_i in range(globalVars.app.config.getint(cls._CONFIG_SECTION, "max_retry", 10)):
			r = requests.post(f"http://localhost:{ cls._PORT }/synthesis", params=synth_payload, 
				data=json.dumps(query_data), timeout=(1000.0, 30000.0))
			if r.status_code == 200:
				with open(fileName, "wb") as fp:
					fp.write(r.content)
				print(f"{fileName} は query={query_i+1}回, synthesis={synth_i+1}回のリトライで正常に保存されました")
				return True
			time.sleep(1)
		else:
			raise engineError("voicevox speak failed.")

	@classmethod
	def getVoicevoxVoices(cls):
		try: r = requests.get(f"http://localhost:{ cls._PORT }/speakers", timeout=(10.0, 30.0))
		except Exception as e: raise connectionError("get voicevox speakers failed. " + str(e))
		if r.status_code == 200:
			return r.json()
		else:
			raise connectionError("Get voicevox speakers failed.")

	@classmethod
	def getVoiceSelections(cls):
		result = cls.getVoicevoxVoices()
		voices = []
		for v in result:
			for s in v["styles"]:
				voices.append({"name": "%s(%s)" %(v["name"], s["name"]), "id": s["id"]})
		return voices

	@classmethod
	def getSpeakerId(cls):
		return globalVars.app.config.getint(cls._CONFIG_SECTION, "voice", 0)

	@classmethod
	def getName(cls):
		return _("Voicevox")

	@classmethod
	def getSettingDialog(cls):
		return voicevoxSettingsDialog.Dialog(cls._CONFIG_SECTION)

	@classmethod
	def validateSettings(cls):
		voices = cls.getVoiceSelections()
		for v in voices:
			if v["id"] == cls.getSpeakerId():
				return True
		return False

if __name__ == "__main__":
	print(voicevox.getVoicevoxVoices())
