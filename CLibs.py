import os
import pathlib

folderInUser = "HallFileShare"
global fileTree
fileTree = []
class PathTools:
    def getPath():
        return os.path.join("C:\\Users",os.getlogin(),folderInUser)

    def removeUserFromPath(path):
        p = pathlib.Path(path)
        nP = pathlib.Path(*p.parts[4:])
        return str(nP)

    def createFullFileTree(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                fileTree.append(PathTools.removeUserFromPath(os.path.join(root, file)))
        return fileTree