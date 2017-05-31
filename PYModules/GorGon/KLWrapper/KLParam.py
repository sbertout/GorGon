class KLParam:
    def __init__(self, typ, name):
        self.__type = typ
        self.__name = name

    def getName(self):
        return self.__name

    def getType(self):
        return self.__type
