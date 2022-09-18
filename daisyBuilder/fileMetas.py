# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.

import re

SMIL_DEFINE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE smil PUBLIC "-//W3C//DTD SMIL 1.0//EN" "http://www.w3.org/TR/REC-SMIL/SMIL10.dtd">
<smil>
"""

def formatedTime(sec):
    inputInt = int(sec)
    inputHour = int(inputInt / 3600)
    inputMin = int((inputInt - (inputHour * 3600)) / 60)
    inputSecInt = int(inputInt - (inputHour * 3600) - (inputMin * 60))
    inputSecPStr = re.sub(r'^.*\.', "", str(sec))
    return "%d:%02d:%02d.%s" %(inputHour, inputMin, inputSecInt, inputSecPStr)

def makeSmilHead(title, totalElapsed, smilDuration):
    totalElapsedStr = formatedTime(totalElapsed)
    smilDurationStr = formatedTime(smilDuration)
    
    return """<head>
  <meta name="dc:title" content="%s"/>
  <meta name="dc:format" content="Daisy 2.02"/>
  <meta name="ncc:generator" content="DAC"/>
  <meta name="title" content="%s"/>
  <meta name="ncc:totalElapsedTime" content="%s"/>
  <meta name="ncc:timeInThisSmil" content="%s"/>
  <layout>
    <region id="txtView"/>
  </layout>
</head>
""" %(title, title, totalElapsedStr, smilDurationStr)


NCC_DEFINE = """<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE smil PUBLIC "-//W3C//DTD SMIL 1.0//EN" "http://www.w3.org/TR/REC-smil/SMIL10.dtd">
<html>
"""

def makeNccHead(title, publisher, totalSmilItems, totalDuration):
  durationStr = formatedTime(totalDuration)
  
  return """<head>
  <title>%s</title>
  <meta http-equiv="Content-type" content="text/html" charset="UTF-8"/>
  <meta name="dc:creator" content="DAC"/>
  <meta name="dc:date" content="2022-07-20" scheme="yyyy-mm-dd"/>
  <meta name="dc:format" content="Daisy 2.02"/>
  <meta name="dc:identifier" content="DAC"/>
  <meta name="dc:language" content="ja" scheme="ISO 639"/>
  <meta name="dc:publisher" content="%s"/>
  <meta name="dc:title"%s"/>
  <meta name="ncc:charset" content="UTF-8"/>
  <meta name="ncc:generator" content="DAC"/>
  <meta name="ncc:pageFront" content="0"/>
  <meta name="ncc:pageNormal" content="0"/>
  <meta name="ncc:pageSpecial" content="0"/>
  <meta name="ncc:tocItems" content="%d"/>
  <meta name="ncc:totalTime" content="%s"/>
  <meta name="ncc:multimediaType" content="audioNCC"/>
</head>
""" %(title, publisher, title, totalSmilItems, durationStr)
