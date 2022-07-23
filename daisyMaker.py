import threading
from comtypes import CoInitialize
import time
from pydub import AudioSegment
import documentParser
import voiceMaker
import daisyBuilder


class daisyMaker(threading.Thread):
    def __init__(self, inputFile):
        threading.Thread.__init__(self)
        self.inputFile = inputFile
        self.total = 0
        self.count = 0
        self.finished = False
    
    def run(self):
        CoInitialize()
        files, index = documentParser.parseEpub("input.epub", phrase=True)

        for i in index:
            self.total += len(i["texts"])
        
        _counter = 1
        _outputCounter = 1
        for i in index:
            audioTmps = []
            i["beginSeconds"] = []
            i["endSeconds"] = []
            i["durationSecond"] = 0.0
            i["audioFile"] = None
            audioOutput = None
            for t in i["texts"]:
                fileName = ".\\outputTmp\\%08d.wav" %(_counter,)
                result = voiceMaker.outputSapiSpeech(t, fileName)
                audioTmps.append(fileName)
                _counter += 1
                self.count += 1
                time.sleep(0.001)
            for f in audioTmps:
                audioTmp = AudioSegment.from_file(f, "wav")
                if audioOutput == None:
                    i["beginSeconds"].append(0.0)
                    audioOutput = audioTmp
                else:
                    i["beginSeconds"].append(audioOutput.duration_seconds)
                    audioOutput = audioOutput + audioTmp
                i["endSeconds"].append(audioOutput.duration_seconds)
            if audioOutput != None:
                outputFile = ".\\output\\audio%08d.mp3" %(_outputCounter,)
                audioOutput.export(outputFile, format="mp3")
                i["audioFile"] = outputFile
                i["durationSecond"] = i["endSeconds"][-1]
                _outputCounter += 1

        builder = daisyBuilder.DaisyBuilder()
        builder.build(index)
        self.finished = True

