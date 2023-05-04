# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.

import bs4
import ebooklib
import io
import json
import os
import re
import sys

from bs4 import BeautifulSoup
from ebooklib import epub

from documentParser.documentParserInterface import *
from errors import *

class epub(documentParserInterface):
    def _parseEpubNavPoint(tags, level=1, sources=[], indexes=[], finalize=True):
        for t in tags:
            try:
                sources.append((int(t.get("playOrder")), re.sub(r'#.*$', "", t.content.get("src"))))
                indexes.append({
                    "id": re.sub(r'^.*#', "", t.content.get("src")) if re.search(r'#.*$', t.content.get("src")) != None else None,
                    "file": re.sub(r'#.*$', "", t.content.get("src")),
                    "label": t.navLabel.find("text").string if t.navLabel != None and t.navLabel.find("text") != None else "",
                    "level": level
                })
                sources, indexes = epub._parseEpubNavPoint(t, (level + 1), sources, indexes, False)
            except Exception as e: pass
        if finalize:
            sources = sorted(sources)
            sources = [item[1] for item in sources]
            sources = sorted(set(sources), key=sources.index)
            return (sources, indexes)
        return (sources, indexes, meta)

    def _parseFileWithHref(book, href):
        file = book.get_item_with_href(href)
        return file.get_content().decode()

    def _splitText(text):
        #print(text)
        if text == None or text == "":
            return []
        split = re.split(r'[。\n]|(?:\. )', text)
        ret = []
        for s in split:
            if s.strip() != "":
                ret.append(s + ".")
        return ret

    def _getAllTags(soupTag):
        results = []
        for t in soupTag.contents:
            if type(t) == bs4.element.NavigableString:
                results.append(t)
            elif type(t) == bs4.element.Tag:
                results.append(t)
                results += epub._getAllTags(t)
        return results

    def _getTextListWithID(xmlText, startID, endID=False):
        soup = BeautifulSoup(xmlText, "lxml-xml")
        tags = soup.body
        texts = []
        start = False
        for t in tags.descendants:
            if type(t) == bs4.element.Tag:
                if t.get("id") == startID and t.get("id") == endID and endID != False:
                    return epub._splitText(t.string)
                if t.get("id") == endID and endID != False:
                    return texts
                if t.get("id") == startID:
                    start = True
            if type(t) == bs4.element.NavigableString and start: texts += epub._splitText(t)
        return texts

    def _appendText2EpubIndex(book, index, phrase=False):
        fileTmp = ""
        tags = None
        for i, v in enumerate(index):
            if v["file"] != fileTmp:
                fileTmp = v["file"]
                tags = epub._parseFileWithHref(book, fileTmp)
            if i < len(index) - 1 and index[i + 1]["file"] == fileTmp:
                texts = epub._getTextListWithID(tags, index[i]["id"], index[i + 1]["id"])
            else:
                texts = epub._getTextListWithID(tags, index[i]["id"])
            index[i]["texts"] = (texts if phrase else [". ".join(texts)])
            #print(index[i]["texts"])
        return index

    #sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    def parse(source, phrase=False):
        try: book = ebooklib.epub.read_epub(source)
        except Exception as e: raise inputError(str(e))

        title = book.get_metadata('DC', 'title')[0][0]
        try: creator = book.get_metadata('DC', 'creator')[0][0]
        except: creator = ""
        try: publisher = book.get_metadata('DC', 'publisher')[0][0]
        except: publisher = ""

        meta = {
            "title": title,
            "publisher": publisher,
            "creator": creator
        }

        items = book.get_items_of_type(ebooklib.ITEM_NAVIGATION)
        sources = []
        indexes = []
        for item in items:
            #print(item.get_name())
            try:
                xml = item.get_content().decode()
                soup = BeautifulSoup(xml, "lxml-xml")
                tags = soup.navMap
                sources, indexes = epub._parseEpubNavPoint(tags)
            except Exception as e:
                raise inputError(str(e))
        epub._appendText2EpubIndex(book, indexes, phrase=phrase)
        if sources != [] and indexes != []:
            return (indexes, meta)
        items = book.get_items()
        indexes = []
        for item in items:
            if item.get_type() != ebooklib.ITEM_DOCUMENT: continue
            try:
                xml = item.get_content().decode()
                soup = BeautifulSoup(xml, "lxml-xml")
                labelObject = soup.find("h1")
                label = labelObject.text if labelObject != None else ""
                indexes.append({
                    "id": None,
                    "file": item.get_name(),
                    "label": label,
                    "level": 1
                })
            except Exception as e:
                raise inputError(str(e))
        epub._appendText2EpubIndex(book, indexes, phrase=phrase)
        return (indexes, meta)

    def getDocumentTypeName():
        return _("EPUBファイル")

    def getWildCardString():
        return _("EPUBファイル (.epub)") + "|*.epub"
    
    def isFromDirectory():
        return False

if __name__ == '__main__':
    s, i, m = epub.parse("input.epub") 
    print(json.dumps(i, indent=2, ensure_ascii=False))
    total = 0
    for v in i:
        total += len(v["texts"])
    print('\n%d phrases《' %(total,))
