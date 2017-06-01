from KLFunction import KLFunction

class KLAlias:

    def __init__(self, name, sourceName):
        self.__name = name
        self.__sourceName = sourceName
        self.__methods = []

    def getName(self):
        return self.__name

    def getSourceName(self):
        return self.__sourceName

    def getMethodCount(self):
        return len(self.__methods)

    def addMethod(self, methodName, returnType, params, access):
        methodFunc = KLFunction(methodName, returnType=returnType, access=access)
        methodFunc.addParams(params)
        self.__methods.append(methodFunc)

    def getMethod(self, idx):
        return self.__methods[idx]
