import os
import pathlib
import socket

folderInUser = "HallFileShare"
global fileTree
fileTree = []
class PathTools:
    def getPath():
        return os.path.join("C:\\TMP", folderInUser)

    def removeUserFromPath(path):
        p = pathlib.Path(path)
        nP = pathlib.Path(*p.parts[4:])
        return str(nP)

    def createFullFileTree(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                fileTree.append(PathTools.removeUserFromPath(os.path.join(root, file)))
        return fileTree
    
class NetTools:
    def getLocalIP():
        local_hostname = socket.gethostname()
        ip_addresses = socket.gethostbyname_ex(local_hostname)[2]
        filtered_ips = [ip for ip in ip_addresses if ip.startswith("10.")]
        return f"{filtered_ips[0]}"