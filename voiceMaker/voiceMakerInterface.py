# -*- coding: utf-8 -*-
# voice maker interface
# Copyright (C) 2022 yamahubuki <itiro.ishino@gmail.com>

from abc import ABCMeta, abstractmethod, ABC

class voiceMakerInterface(metaclass=ABCMeta):
	@classmethod
	@abstractmethod
	def generateWave(cls, text, fileName):
		raise NotImplemented()

	@classmethod
	@abstractmethod
	def getName(cls):
		raise NotImplemented()

	@classmethod
	def getSettingDialog(cls):
		return None

	@classmethod
	def validateSettings(cls):
		return True
