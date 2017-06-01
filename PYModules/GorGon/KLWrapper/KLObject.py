from  KLStruct import KLStruct

class KLObject(KLStruct):

    def __init__(self, name, members=None):
        KLStruct.__init__(self, name, members)
        self.__hasDestructor = False

    def setHasDestructor(self, b):
        self.__hasDestructor = b

    def getHasDestructor(self):
        return self.__hasDestructor
