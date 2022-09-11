import requests
import json
import time
from errors import *
from englishToKanaConverter. englishToKanaConverter import EnglishToKanaConverter

def outputVoicevoxSpeech(text, filename, speaker=2, kanaConvert=False, max_retry=10):
    # カナ処理
    cnv = EnglishToKanaConverter(False)
    if kanaConvert: text = cnv.process(text)
    
    # Internal Server Error(500)が出ることがあるのでリトライする
    # （HTTPAdapterのretryはうまくいかなかったので独自実装）
    # connect timeoutは10秒、read timeoutは3000秒に設定（長文対応）
    # audio_query
    query_payload = {"text": text, "speaker": speaker}
    for query_i in range(max_retry):
        r = requests.post("http://localhost:50021/audio_query", 
            params=query_payload, timeout=(10.0, 3000.0))
        if r.status_code == 200:
            query_data = r.json()
            break
        time.sleep(1)
    else:
        raise connectionError("Make audio query faild.")

    # synthesis
    synth_payload = {"speaker": speaker}    
    for synth_i in range(max_retry):
        r = requests.post("http://localhost:50021/synthesis", params=synth_payload, 
            data=json.dumps(query_data), timeout=(1000.0, 30000.0))
        if r.status_code == 200:
            with open(filename, "wb") as fp:
                fp.write(r.content)
            print(f"{filename} は query={query_i+1}回, synthesis={synth_i+1}回のリトライで正常に保存されました")
            return True
        time.sleep(1)
    else:
        raise engineError("voicevox speak failed.")

def getVoicevoxVoices():
    try: r = requests.get("http://localhost:50021/speakers", timeout=(10.0, 30.0))
    except Exception as e: raise connectionError("get voicevox speakers failed. " + str(e))
    if r.status_code == 200:
        return r.json()
    else:
        raise connectionError("Get voicevox speakers failed.")

if __name__ == "__main__":
    print(getVoicevoxVoices())
