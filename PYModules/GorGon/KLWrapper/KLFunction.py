from KLParam import KLParam

class KLFunction:
    def __init__(self, name, returnType=None, access=None):
        self.__name = name
        self.__returnType = returnType
        self.__access = access
        self.__params = []

    def _addParams(self, params):
        if isinstance(params, list):
            for p in params:
                self.__params.append(KLParam(p['typeUserName'], p['name']))
        else:
            self.__params.append(KLParam(params['typeUserName'], params['name']))

    def getParamCount(self):
        return len(self.__params)

    def getParam(self, idx):
        return self.__params[idx]

    def getName(self):
        return self.__name

    def getReturnType(self):
        return self.__returnType

    def getAccess(self):
        return self.__access
