import os
import shutil
import threading
from comtypes import CoInitialize
import time
from pydub import AudioSegment
import documentParser
from errors import inputError, outputError
import voiceMaker
import daisyBuilder


# const
SAPI = 0
VOICEVOX = 1

def getSapiVoices():
    result = voiceMaker.getSapiVoices()
    if result:
        return [ {"name": r.GetDescription(), "pointer": r} for r in result ]
    else:
        return []

def getVoicevoxVoices():
    result = voiceMaker.getVoicevoxVoices()
    voices = []
    for v in result:
        for s in v["styles"]:
            voices.append({"name": "%s(%s)" %(v["name"], s["name"]), "id": s["id"]})
    return voices


class daisyMaker(threading.Thread):
    def __init__(self, inputFile, outputDir, mode=SAPI, options={}):
        threading.Thread.__init__(self)
        self.inputFile = inputFile
        self.outputDir = outputDir
        self.mode = mode
        self.options = options
        self.total = 0
        self.count = 0
        self.finished = False
        self.error = None
    
    def run(self):
        CoInitialize()
        try: files, index = documentParser.parseEpub(self.inputFile, phrase=True)
        except Exception as e:
            self.error = inputError(str(e))
            return

        for i in index:
            self.total += len(i["texts"])
        
        _counter = 1
        _outputCounter = 1
        try:
            os.makedirs(self.outputDir, exist_ok=True)
            shutil.rmtree(self.outputDir)
            os.makedirs(".\outputTmp", exist_ok=True)
            os.makedirs(self.outputDir)
        except Exception as e:
            self.error = outputError(str(e))
            return
        for i in index:
            audioTmps = []
            i["beginSeconds"] = []
            i["endSeconds"] = []
            i["durationSecond"] = 0.0
            i["audioFile"] = None
            audioOutput = None
            for t in i["texts"]:
                fileName = ".\\outputTmp\\%08d.wav" %(_counter,)
                if self.mode == SAPI: result = voiceMaker.outputSapiSpeech(t, fileName, self.options)
                elif self.mode == VOICEVOX: result = voiceMaker.outputVoicevoxSpeech(t, fileName, self.options["voiceID"])
                else: return
                audioTmps.append(fileName)
                _counter += 1
                self.count += 1
                time.sleep(0.001)
            for f in audioTmps:
                try:
                    audioTmp = (AudioSegment.from_file(f, "wav")) + (AudioSegment.silent(duration=500))
                except Exception as e:
                    self.error = outputError(str(e))
                    return
                if audioOutput == None:
                    i["beginSeconds"].append(0.0)
                    audioOutput = audioTmp
                else:
                    i["beginSeconds"].append(audioOutput.duration_seconds)
                    audioOutput = audioOutput + audioTmp
                i["endSeconds"].append(audioOutput.duration_seconds)
            
            if audioOutput != None:
                outputFile = os.path.join(self.outputDir, "audio%08d.mp3" %(_outputCounter,))
                try: audioOutput.export(outputFile, format="mp3")
                except Exception as e:
                    self.error = outputError(str(e))
                    return
                i["audioFile"] = outputFile
                i["durationSecond"] = i["endSeconds"][-1]
                _outputCounter += 1

        try:
            shutil.rmtree(".\\outputTmp")
            os.makedirs(".\outputTmp")
        except Exception as e:
            self.error = outputError(str(e))
            return
        
        builder = daisyBuilder.DaisyBuilder()
        builder.build(index, self.outputDir)
        self.finished = True

