# -*- coding: utf-8 -*-
#Application Main

import AppBase
import update
import globalVars
import proxyUtil

class Main(AppBase.MainBase):
	def __init__(self):
		super().__init__()

	def initialize(self):
		self.setGlobalVars()
		# プロキシの設定を適用
		self.proxyEnviron = proxyUtil.virtualProxyEnviron()
		self.setProxyEnviron()
		# アップデートを実行
		if self.config.getboolean("general", "update"):
			globalVars.update.update(True)
		# メインビューを表示
		from views import main
		self.hMainView=main.MainView()
		self.hMainView.Show()
		return True

	def setProxyEnviron(self):
		if self.config.getboolean("proxy", "usemanualsetting", False) == True:
			self.proxyEnviron.set_environ(self.config["proxy"]["server"], self.config.getint("proxy", "port", 8080, 0, 65535))
		else:
			self.proxyEnviron.set_environ()

	def setGlobalVars(self):
		globalVars.update = update.update()
		return

	def OnExit(self):
		#設定の保存やリソースの開放など、終了前に行いたい処理があれば記述できる
		#ビューへのアクセスや終了の抑制はできないので注意。

		# アップデート
		globalVars.update.runUpdate()

		#戻り値は無視される
		return 0
