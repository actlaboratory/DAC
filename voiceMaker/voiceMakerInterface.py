# -*- coding: utf-8 -*-
# voice maker interface
# Copyright (C) 2022 yamahubuki <itiro.ishino@gmail.com>

from abc import ABCMeta, abstractmethod, ABC

class voiceMakerInterface(metaclass=ABCMeta):

	@abstractmethod
	def generateWave(text, fileName):
		raise NotImplemented()

	@abstractmethod
	def getName():
		raise NotImplemented()

	def getSettingDialog():
		return None

	def validateSettings():
		return True
