class KLMember:

    def __init__(self, access, type, name):
        self.__access = access
        self.__type = type
        self.__name = name

    def getAccess(self):
        return self.__access

    def getType(self):
        return self.__type

    def getName(self):
        return self.__name