# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.

import bs4
import glob
import io
import json
import os
import re
import sys

from bs4 import BeautifulSoup
from documentParser.documentParserInterface import *
from errors import *

class textDaisy(documentParserInterface):
    # ncxのnavpointタグ内をパースしてソース一覧と階層構造を生成
    def _parseNcxNavPoint(tags, level=1, sources=[], indexes=[], finalize=True):
        for t in tags:
            try:
                sources.append((int(t.get("playOrder")), re.sub(r'#.*$', "", t.content.get("src"))))
                indexes.append({
                    "id": re.sub(r'^.*#', "", t.content.get("src")) if re.search(r'#.*$', t.content.get("src")) != None else None,
                    "file": re.sub(r'#.*$', "", t.content.get("src")),
                    "label": t.navLabel.find("text").string if t.navLabel != None and t.navLabel.find("text") != None else "",
                    "level": level
                })
                if t.find("navPoint") != None:
                    sources, indexes = textDaisy._parseNcxNavPoint(t, (level + 1), sources, indexes, False)
            except Exception as e: pass
        if finalize:
            sources = sorted(sources)
            sources = [item[1] for item in sources]
            sources = sorted(set(sources), key=sources.index)
            return (sources, indexes)
        return (sources, indexes, meta)

    # idテキスト本文取得
    _xmlTagCache = {"source": "", "tags": None}
    def _getSrcIdText(dir, srcStr):
        id = re.sub(r'^.*#', "", srcStr)
        src = re.sub(r'#.*$', "", srcStr)
        src = os.path.join(dir, src)
        if textDaisy._xmlTagCache["source"] != src:
            fileText = ""
            with open(src, "r", encoding="utf8") as f:
                fileText = f.read()
            textDaisy._xmlTagCache = {
                "source": src,
                "tags": BeautifulSoup(fileText, "lxml-xml")
            }
        soup = textDaisy._xmlTagCache["tags"]
        results = soup.select("#" + id)
        if len(results) == 0:
            text = ""
        text = results[0].text
        return text

    def _splitText(text):
        #print(text)
        if text == None or text == "":
            return []
        split = re.split(r'[。\n]|(?:\. )', text)
        ret = []
        for s in split:
            if s.strip() != "":
                s = re.sub(r'[、。,\.]$', "", s.strip())
                ret.append(s + ".")
        return ret

    def _getTextListWithID(source, startID, endID=False):
        dir = os.path.dirname(source)
        smilText = ""
        with open(source, "r", encoding="utf8") as f:
            smilText = f.read()
        soup = BeautifulSoup(smilText, "lxml-xml")
        tags = soup.body
        texts = []
        start = False
        end = False
        for t in tags.descendants:
            if type(t) == bs4.element.Tag:
                if t.get("id") == startID:
                    start = True
                if t.get("id") == endID and endID != False:
                    end = True
                if t.name == "par":
                    if start == True and (end == False or (end and len(texts) == 0)):
                        text = textDaisy._getSrcIdText(dir, t.find("text").get("src"))
                        texts += textDaisy._splitText(text)
                    elif end:
                        textDaisy._xmlTagCache = {"source": "", "tags": None}
                        return texts
        textDaisy._xmlTagCache = {"source": "", "tags": None}
        return texts

    def _appendText2Index(source, index, phrase=False):
        fileTmp = ""
        tags = None
        # smil順番にファイルパーサに投げる
        for i, v in enumerate(index):
            if v["file"] != fileTmp:
                fileTmp = v["file"]
            if i < len(index) - 1 and index[i + 1]["file"] == fileTmp:
                texts = textDaisy._getTextListWithID(os.path.join(source, fileTmp), index[i]["id"], index[i + 1]["id"])
            else:
                texts = textDaisy._getTextListWithID(os.path.join(source, fileTmp), index[i]["id"])
            index[i]["texts"] = (texts if phrase else [". ".join(texts)])
            #print(index[i]["texts"])
        return index

    # メタ情報取得
    def _getMeta(source):
        meta ={
            "title": "",
            "publisher": "",
            "creator": ""
        }
        try: opf = glob.glob(os.path.join(source, "*.opf"))[0]
        except Exception as e:
            return meta
        opfText = ""
        with open(opf, "r", encoding="utf8") as f:
            opfText = f.read()
        soup = BeautifulSoup(opfText, "lxml-xml")
        try: meta["title"] = soup.package.metadata.find("dc-metadata").find("dc:Title").string
        except Exception as e: pass
        try: meta["publisher"] = soup.package.metadata.find("dc-metadata").find("dc:Publisher").string
        except Exception as e: pass
        try: meta["creator"] = soup.package.metadata.find("dc-metadata").find("dc:Creator").string
        except Exception as e: pass
        return meta

    #sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # textdaisy パース
    def parse(source, phrase=False):
        # ソースを絶対パスに
        source = os.path.abspath(source)
        #print(source)
        # ncxインデックスファイル取得
        ncxFilePath = ""
        try: ncxFilePath = glob.glob(os.path.join(source, "*.ncx"))[0]
        except Exception as e: raise inputError(str(e))

        # ncxファイル読み込み
        ncx = ""
        try:
            with open(ncxFilePath, "r", encoding="utf8") as f:
                ncx = f.read()
        except Exception as e:
            raise inputError(str(e))

        meta = textDaisy._getMeta(source)

        sources = []
        indexes = []
        
        # パース
        try:
            soup = BeautifulSoup(ncx, "lxml-xml")
            # ncxファイルをパースしてソース込み目次階層を作成
            tags = soup.navMap
            sources, indexes = textDaisy._parseNcxNavPoint(tags)
        except Exception as e:
            raise inputError(str(e))
        
        # ソースを全パースして階層にテキストを追加
        textDaisy._appendText2Index(source, indexes, phrase=phrase)
        if sources != [] and indexes != []:
            return (indexes, meta)
        else:
            raise inputError("contents not found.")


    def getDocumentTypeName():
        return _("テキストデイジー図書")

    def getWildCardString():
        return None

    def isDirectory():
        return True

if __name__ == '__main__':
    i, m = textDaisy.parse("input") 
    print(json.dumps(i, indent=2, ensure_ascii=False))
    total = 0
    for v in i:
        total += len(v["texts"])
    print('\n%d phrases《' %(total,))
