import CLibs as CLibs

def getFullFileTree():
    return CLibs.PathTools.createFullFileTree(CLibs.PathTools.getPath())

def checkMissingFiles(TargetFiles = [""]):
    fullFileTree = getFullFileTree()
    missingFiles = []
    for file in TargetFiles:
        if not file in fullFileTree:
            if not file.startswith(".git"):
                missingFiles.append(file)
    return missingFiles