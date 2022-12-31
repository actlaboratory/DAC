# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.

from . import epub
from . import markdown
from . import documentParserInterface


def getParsers():
	return [epub.epub, markdown.markdown]
