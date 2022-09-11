import os
import re
import globalVars
import errors

def getTempDir():
    try:
        dir = globalVars.app.config["general"]["temp_directory"]
    except Exception as e:
        raise errors.outputError(str(e))
    
    if os.path.isdir(dir):
        return os.path.join(dir, "actlab-DAC-temp")
    else:
        return os.path.join(os.environ["temp"], "actlab-DAC-temp")

def addDirNameSuffix(path):
    dir = os.path.dirname(path)
    file = os.path.basename(path)
    num = 0
    while os.path.exists(path):
        path = os.path.join(dir, "%s (%d)" %(file, num))
        num += 1
    return path

