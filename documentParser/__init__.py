# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.

from . import epub
from . import documentParserInterface


def getParsers():
	return [epub.epub]
