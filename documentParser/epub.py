import io
import re
import sys
import os       
import ebooklib
import json
from ebooklib import epub
import bs4
from bs4 import BeautifulSoup
from errors import *

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
            sources, indexes = _parseEpubNavPoint(t, (level + 1), sources, indexes, False)
        except Exception as e: pass
    if finalize:
        sources = sorted(sources)
        sources = [item[1] for item in sources]
        sources = sorted(set(sources), key=sources.index)
        return (sources, indexes)
    return (sources, indexes)

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
            results += _getAllTags(t)
    return results

def _getTextListWithID(xmlText, startID, endID=False):
    soup = BeautifulSoup(xmlText, "lxml-xml")
    tags = soup.body
    texts = []
    start = False
    for t in tags.descendants:
        if type(t) != bs4.element.Tag: continue
        if t.get("id") == startID and t.get("id") == endID and endID != False:
            return _splitText(t.string)
        if t.get("id") == endID and endID != False:
            return texts
        if t.get("id") == startID and start == False:
            texts += _splitText(t.string)
            start = True
        elif start:
            texts += _splitText(t.string)
    return texts

def _appendText2EpubIndex(book, index, phrase=False):
    fileTmp = ""
    tags = None
    for i, v in enumerate(index):
        if v["file"] != fileTmp:
            fileTmp = v["file"]
            tags = _parseFileWithHref(book, fileTmp)
        if i < len(index) - 1 and index[i + 1]["file"] == fileTmp:
            texts = _getTextListWithID(tags, index[i]["id"], index[i + 1]["id"])
        else:
            texts = _getTextListWithID(tags, index[i]["id"])
        index[i]["texts"] = (texts if phrase else [". ".join(texts)])
    return index


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def parseEpub(source, phrase=False):
    try: book = epub.read_epub(source)
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
        print(item.get_name())
        try:
            xml = item.get_content().decode()
            soup = BeautifulSoup(xml, "lxml-xml")
            tags = soup.navMap
            sources, indexes = _parseEpubNavPoint(tags)
        except Exception as e:
            raise inputError(str(e))
    _appendText2EpubIndex(book, indexes, phrase=phrase)
    if sources != [] and indexes != []:
        return (sources, indexes)
    items = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
    sources = []
    indexes = []
    for item in items:
        print(item.get_name())
        try:
            xml = item.get_content().decode()
            soup = BeautifulSoup(xml, "lxml-xml")
        except Exception as e:
            raise inputError(str(e))
    

if __name__ == '__main__':
    s, i = parseEpub("input.epub") 
    print(json.dumps(i, indent=2, ensure_ascii=False))
    total = 0
    for v in i:
        total += len(v["texts"])
    print('\n%d phrases《' %(total,))
