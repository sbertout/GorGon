from KLFunction import KLFunction

class KLAlias:

    def __init__(self, name, sourceName):
        self.__name = name
        self.__sourceName = sourceName
        self.__methods = []
        self.__operators = []

    def getName(self):
        return self.__name

    def getSourceName(self):
        return self.__sourceName

    def getMethodCount(self):
        return len(self.__methods)

    def _addMethod(self, methodName, returnType, params, access):
        methodFunc = KLFunction(methodName, returnType=returnType, access=access)
        methodFunc._addParams(params)
        self.__methods.append(methodFunc)

    def getMethod(self, idx):
        return self.__methods[idx]

    def getOperatorCount(self):
        return len(self.__operators)

    def _addOperator(self, operatorName, params, access):
        operatorFunc = KLFunction(operatorName, access=access)
        operatorFunc._addParams(params)
        self.__operators.append(operatorFunc)

    def getOperator(self, idx):
        return self.__operators[idx]
