# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.

import daisyMaker
import time

makerThread = daisyMaker.daisyMaker("input.epub")
print("created", flush=True)
makerThread.start()
print("started", flush=True)

closing = False
while makerThread.finished == False:
    time.sleep(0.1)
    if closing == False: print("%d / %d processed." %(makerThread.count, makerThread.total), end="\r", flush=True)
    if makerThread.count == makerThread.total and makerThread.total >= 1 and closing == False:
        print("\nclosing...", flush=True)
        closing = True

