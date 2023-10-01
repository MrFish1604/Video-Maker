def readconfig(filename:str) -> dict:
    with open(filename, "r") as rfile:
        lines = rfile.readlines()
    rtn = {}
    for line in lines:
        data = line.strip().split('=')
        if len(data)!=2:
            raise Exception("Syntaxe error")
        rtn[data[0]] = data[1]
    return rtn