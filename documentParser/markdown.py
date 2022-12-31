# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.
# Copyright (C) 2022 yamahubuki <itiro.ishino@gmail.com>

import bs4
import json
import markdown as md
import os
import re

from bs4 import BeautifulSoup

from documentParser.documentParserInterface import *
from errors import *

class markdown(documentParserInterface):
	def _splitText(text):
		if text == None or text == "":
			return []
		split = re.split(r'[。\n]|(?:\. )', text)
		ret = []
		for s in split:
			if s.strip() != "":
				ret.append(s + ".")
		return ret

	def parse(source, phrase=True):
		try: 
			with open(source,"r", encoding="utf8") as f:
				document = md.markdown(f.read())
		except UnicodeDecodeError:
			try:
				with open(source,"r", encoding="cp932") as f:
					document = md.markdown(f.read())
			except Exception as e: raise inputError(str(e))
		except Exception as e: raise inputError(str(e))

		try:
			dummy, indexes = markdown.parseHtml(BeautifulSoup("<body>"+document+"</body>", "lxml-xml").find("body"), None, [])
		except Exception as e:
			raise inputError(str(e))

		meta = {
			"title": os.path.basename(source),
			"publisher": "markdown file publisher",
			"creator": "markdown file author"
		}

		if len(indexes) >= 2 and indexes[1]["level"] == 1 and not indexes[0]["label"] and indexes[1]["label"]:
			meta["title"] = indexes[1]["label"]
		return (indexes, meta)

	def parseHtml(soup, item=None, results=[]):
		if not item:
			item={
				"label" : None,
				"level" : 1,
				"texts" : [],
			}
			results.append(item)
		for i in soup.contents:
			if type(i) == bs4.element.NavigableString:
				text = i.string.strip()
				if not text:
					continue
				item["texts"] += (markdown._splitText(text))
			elif i.name in ("h1","h2","h3","h4","h5","h6"):
					item={
						"label" : i.string,
						"level" : int(i.name[1]),
						"texts" : [],
					}
					results.append(item)
					item["texts"] += (markdown._splitText(i.string))
			elif i.name=="input" and "value" in i:
					item["texts"] += (markdown._splitText(i["value"]))
			elif i.name in ("img","i") and "alt" in i:
					item["texts"] += (markdown._splitText(i["alt"]))
			else:
				item,results = markdown.parseHtml(i, item, results)
		return item, results

	def getDocumentTypeName():
		return _("markdownファイル")

	def getWildCardString():
		return _("markdownファイル (.md)") + "|*.md"

if __name__ == '__main__':
	s, i, m = markdown.parse("input.md")
	print(json.dumps(i, indent=2, ensure_ascii=False))
	total = 0
	for v in i:
		total += len(v["texts"])
	print('\n%d phrases《' %(total,))
