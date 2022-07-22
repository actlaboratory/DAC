from pydub import AudioSegment
import documentParser
import voiceMaker
import daisyBuilder


files, index = documentParser.parseEpub("input.epub", phrase=True)

_counter = 1
_outputCounter = 1
for i in index:
    audioTmps = []
    i["durations"] = []
    i["audioFile"] = None
    audioOutput = None
    for t in i["texts"]:
        fileName = ".\\outputTmp\\%08d.wav" %(_counter,)
        result = voiceMaker.outputVoicevoxSpeech(t, fileName)
        audioTmps.append(fileName)
        _counter += 1
    for f in audioTmps:
        audioTmp = AudioSegment.from_file(f, "wav")
        if audioOutput == None:
            audioOutput = audioTmp
        else:
            audioOutput = audioOutput + audioTmp
        i["durations"].append(audioTmp.duration_seconds)
    if audioOutput != None:
        outputFile = ".\\output\\audio%08d.mp3" %(_outputCounter,)
        audioOutput.export(outputFile, format="mp3")
        i["audioFile"] = outputFile
        _outputCounter += 1

builder = daisyBuilder.DaisyBuilder()
builder.build(index)

