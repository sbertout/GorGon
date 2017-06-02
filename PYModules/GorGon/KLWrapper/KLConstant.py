class KLConstant:

    def __init__(self, typ, name, value):
        self.__type = typ
        self.__name = name
        self.__value = value

    def getType(self):
        return self.__type

    def getName(self):
        return self.__name

    def getValue(self):
        return self.__value
