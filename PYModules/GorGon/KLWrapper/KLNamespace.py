class KLNamespace:
    def __init__(self, name):
        self.__name = name
        self.__interfaces = {}
        self.__objects = {}
        self.__structs = {}
        self.__functions = {}
        self.__operators = []
        self.__aliases = {}
        self.__constants = {}
        self.__extensions = {}

    def getName(self):
        return self.__name

    def getInterfaceCount(self):
        return len(self.__interfaces)

    def getInterfaceNames(self):
        return self.__interfaces.keys()

    def _addInterface(self, interface):
        self.__interfaces[interface.getName()] = interface

    def getInterface(self, interfaceName):
        return self.__interfaces[interfaceName]

    def hasInterface(self, interfaceName):
        return interfaceName in self.__interfaces

    def getObjectCount(self):
        return len(self.__objects)

    def getObjectNames(self):
        return self.__objects.keys()

    def _addObject(self, obj):
        self.__objects[obj.getName()] = obj

    def getObject(self, objectName):
        return self.__objects[objectName]

    def hasObject(self, objectName):
        return objectName in self.__objects

    def getStructCount(self):
        return len(self.__structs)

    def getStructNames(self):
        return self.__structs.keys()

    def _addStruct(self, obj):
        self.__structs[obj.getName()] = obj

    def getStruct(self, structName):
        return self.__structs[structName]

    def hasStruct(self, structName):
        return structName in self.__structs

    def getFunctionCount(self):
        return len(self.__functions)

    def getFunctionNames(self):
        return  self.__functions.keys()

    def _addFunction(self, func):
        self.__functions[func.getName()] = func

    def getFunction(self, functionName):
        return self.__functions[functionName]

    def hasFunction(self, functionName):
        return functionName in self.__functions

    def getOperatorCount(self):
        return len(self.__operators)

    def _addOperator(self, op):
        self.__operators.append(op)

    def getOperator(self, idx):
        return self.__operators[idx]

    def getAliasCount(self):
        return len(self.__aliases)

    def getAliasNames(self):
        return self.__aliases.keys()

    def _addAlias(self, obj):
        self.__aliases[obj.getName()] = obj

    def getAlias(self, aliasName):
        return self.__aliases[aliasName]

    def hasAlias(self, aliasName):
        return aliasName in self.__aliases

    def getConstantCount(self):
        return len(self.__constants)

    def getConstantNames(self):
        return self.__constants.keys()

    def addConstant(self, obj):
        self.__constants[obj.getName()] = obj

    def getConstant(self, constantName):
        return self.__constants[constantName]

    def hasConstant(self, constantName):
        return constantName in self.__constants