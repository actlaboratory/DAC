# -*- coding: utf-8 -*-
# Document parser interface
# Copyright (C) 2022 yamahubuki <itiro.ishino@gmail.com>
# Copyright (c)2023 Hiroki Fujii,ACT laboratory All rights reserved.

from abc import ABCMeta, abstractmethod, ABC

class documentParserInterface(metaclass=ABCMeta):

	@abstractmethod
	def getDocumentTypeName():
		raise NotImplemented()

	@abstractmethod
	def getWildCardString():
		raise NotImplemented()
	
	@abstractmethod
	# 入力元がフォルダかどうか
	def isFromDirectory():
		raise NotImplemented()

