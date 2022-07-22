import os
from . import fileMetas

class DaisyBuilder:
    def __init__(self):
        self.totalDuration = 0
        self.nccIDCounter = 0
        self.smilFileCounter = 0
        self.nccTexts = [fileMetas.NCC_DEFINE]
        self.directory = ""

    def _getNccID(self): return "ncc%08d" %(self.nccIDCounter,)
    def _getSmilID(self): return "smil%08d" %(self.smilFileCounter,)
    def _getSmilFileName(self): return "smil%08d.smil" %(self.smilFileCounter,)
    
    def _appendNcc(self, text, indent=0):
        self.nccTexts.append("%s%s" %(" " * indent, text))
    
    def _makeSmil(self, item):
        smilDuration = sum(item["durations"])
        
        text = fileMetas.SMIL_DEFINE
        text += fileMetas.makeSmilHead("test", self.totalDuration, smilDuration)
        text += ('<body>\n'
            + '<seq dur="%ss">\n' %(smilDuration,)
            + '  <par endsync="last">\n'
            + '    <text src="ncc.html#%s" id="%s"/>\n' %(self._getNccID(), self._getSmilID())
            + '    <seq>\n'
        )
        
        beginDuration = 0
        endDuration = 0
        phraseIDCounter = 0
        for d in item["durations"]:
            endDuration += d
            text += '      <audio src="%s" clip-begin="npt=%ds" clip-end="npt=%ds" id="phrase_%08d"/>\n' %(os.path.basename(item["audioFile"]), beginDuration, endDuration, phraseIDCounter)
            beginDuration += d
            phraseIDCounter += 1
        
        text += ('    </seq>\n'
            + '  </par>\n'
            + '</seq>\n'
            + '</body>\n'
            + '</smil>\n'
        )

        self._appendNcc('<h%d id="%s" class="section"><a href="%s#%s">%s</a></h%d>' %(item["level"], self._getNccID(), self._getSmilFileName(), self._getSmilID(), item["label"], item["level"]), 1)
        with open(self.directory + self._getSmilFileName(), "w", encoding="UTF-8") as f:
            f.write(text)

        self.smilFileCounter += 1
        self.nccIDCounter += 1
        self.totalDuration += smilDuration


    def build(self, index, outputDir="output"):
        self.directory = ".\\%s\\" %(outputDir,)

        self._appendNcc("<body>")
        
        for i in index:
            self._makeSmil(i)
        self._appendNcc("</body>")
        self._appendNcc("</html>")
        self.nccTexts.insert(1, fileMetas.makeNccHead("test", "any", self.smilFileCounter, self.totalDuration))
        with open(self.directory + "ncc.html", "w", encoding="UTF-8") as f:
            f.write("\n".join(self.nccTexts))


