# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.

import os
import shutil
import threading
import time
import traceback

import constants
import daisyBuilder
import utils
import voiceMaker

from comtypes import CoInitialize
from pydub import AudioSegment
from logging import getLogger

from errors import inputError, outputError


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
    def __init__(self, inputFile, outputDir, parser, mode=SAPI, options={}):
        threading.Thread.__init__(self)
        self.inputFile = inputFile
        self.outputDir = outputDir
        self.parser = parser
        self.mode = mode
        self.options = options
        self.total = 0
        self.count = 0
        self.finished = False
        self.exited = False
        self.canceled = False
        self.error = None
        self.log=getLogger("%s.%s" % (constants.LOG_PREFIX, "daisyMaker"))

    def cancel(self):
        self.canceled = True
        self.exited = True

    def exit(self):
        self.exited = True
    
    def run(self):
        CoInitialize()
        try: files, index, meta = self.parser.parse(self.inputFile, phrase=True)
        except Exception as e:
            self.log.error(traceback.format_exc())
            self.error = inputError(str(e))
            return

        outputDir = utils.addDirNameSuffix(os.path.join(self.outputDir, utils.makeFileName(meta["title"], "_")))
        
        for i in index:
            self.total += len(i["texts"])
        
        _counter = 1
        _outputCounter = 1
        try:
            os.makedirs(outputDir)
            os.makedirs(utils.getTempDir(), exist_ok=True)
        except Exception as e:
            self.log.error(traceback.format_exc())
            self.error = outputError(str(e))
            return
        for i in index:
            if self.canceled: return
            audioTmps = []
            i["beginSeconds"] = []
            i["endSeconds"] = []
            i["durationSecond"] = 0.0
            i["audioFile"] = None
            audioOutput = None
            for t in i["texts"]:
                if self.canceled: return
                fileName = os.path.join(utils.getTempDir(), "%08d.wav" %(_counter,))
                try:
                    if self.mode == SAPI: result = voiceMaker.outputSapiSpeech(t, fileName, self.options)
                    elif self.mode == VOICEVOX: result = voiceMaker.outputVoicevoxSpeech(t, fileName, self.options["voiceID"], self.options["kanaConvert"])
                    else: return
                except Exception as e:
                    self.log.error(traceback.format_exc())
                    self.error = e
                    return
                audioTmps.append(fileName)
                _counter += 1
                self.count += 1
                time.sleep(0.001)
            for f in audioTmps:
                if self.canceled: return
                try:
                    audioTmp = (AudioSegment.from_file(f, "wav")) + (AudioSegment.silent(duration=500))
                except Exception as e:
                    self.log.error(traceback.format_exc())
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
                outputFile = os.path.join(outputDir, "audio%08d.mp3" %(_outputCounter,))
                try: audioOutput.export(outputFile, format="mp3")
                except Exception as e:
                    self.log.error(traceback.format_exc())
                    self.error = outputError(str(e))
                    return
                i["audioFile"] = outputFile
                i["durationSecond"] = i["endSeconds"][-1]
                _outputCounter += 1

        try:
            shutil.rmtree(utils.getTempDir())
            os.makedirs(utils.getTempDir())
        except Exception as e:
            self.log.error(traceback.format_exc())
            self.error = outputError(str(e))
            return
        
        builder = daisyBuilder.DaisyBuilder()
        builder.build(index, meta, outputDir)
        self.finished = True

