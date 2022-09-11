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
