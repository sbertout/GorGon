from  KLFunction import KLFunction
from  KLMember import KLMember

class KLStruct:

    def __init__(self, name, members=None):
        self.__name = name
        self.__members = []
        if members is not None:
            self.setMembers(members)
        self.__constructors = []
        self.__hasDestructor = False
        self.__getters = []
        self.__setters = []
        self.__methods = []
        self.__operators = []

    def getName(self):
        return self.__name

    def setHasDestructor(self, b):
        self.__hasDestructor = b

    def getHasDestructor(self):
        return self.__hasDestructor

    def getConstructorCount(self):
        return len(self.__constructors)

    def addConstructor(self, constructor):
        self.__constructors.append(constructor)

    def getConstructor(self, idx):
        return self.__constructors[idx]

    def setMembers(self, members):
        for m in members:
            self.__members.append(KLMember(m['access'], m['baseType'], m['memberDecls'][0]['name']))

    def getMemberCount(self):
        return len(self.__members)

    def getMember(self, idx):
        return self.__members[idx]

    def getGetterCount(self):
        return len(self.__getters)

    def getSetterCount(self):
        return len(self.__setters)

    def addGetter(self, methodName, returnType, access):
        self.__getters.append(KLFunction(methodName, returnType=returnType, access=access))

    def getGetter(self, idx):
        return self.__getters[idx]

    def addSetter(self, methodName, params, access):
        setterFunc = KLFunction(methodName, access=access)
        setterFunc.addParams(params)
        self.__setters.append(setterFunc)

    def getSetter(self, idx):
        return self.__setters[idx]

    def getMethodCount(self):
        return len(self.__methods)

    def addMethod(self, methodName, returnType, params, access):
        methodFunc = KLFunction(methodName, returnType=returnType, access=access)
        methodFunc.addParams(params)
        self.__methods.append(methodFunc)

    def getMethod(self, idx):
        return self.__methods[idx]

    def getOperatorCount(self):
        return len(self.__operators)

    def addOperator(self, operatorName, params, access):
        operatorFunc = KLFunction(operatorName, access=access)
        operatorFunc.addParams(params)
        self.__operators.append(operatorFunc)

    def getOperator(self, idx):
        return self.__operators[idx]
