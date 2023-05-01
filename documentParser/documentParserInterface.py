# -*- coding: utf-8 -*-
# Document parser interface
# Copyright (C) 2022 yamahubuki <itiro.ishino@gmail.com>

from abc import ABCMeta, abstractmethod, ABC

class documentParserInterface(metaclass=ABCMeta):

	@abstractmethod
	def getDocumentTypeName():
		raise NotImplemented()

	@abstractmethod
	def getWildCardString():
		raise NotImplemented()
	
	@abstractmethod
	def isDirectory():
		raise NotImplemented()

