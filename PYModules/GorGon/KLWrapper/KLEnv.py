import json
import FabricEngine.Core as FECore
from KLNamespace import KLNamespace
from KLObject import KLObject
from KLFunction import KLFunction

class KLEnv:
    def __init__(self, sourceCode):
        self.__fabricClient = FECore.createClient()
        self.__globalNamespace = KLNamespace('global')
        self.__namespaces = {}
        ast = self.__fabricClient.getKLJSONAST('AST.kl', sourceCode, True)
        data = json.loads(ast.getStringCString())['ast']
        # print len(data)
        for ext in data:
            for d in ext:
                self.__parse(d, self.__globalNamespace)

    def getGlobalNamespace(self):
        return self.__globalNamespace

    def getNamespaceCount(self):
        return len(self.__namespaces)

    def getNamespace(self, name):
        if name not in self.__namespaces:
            return None
        return self.__namespaces[name]

    def addNamespace(self, namespaceName):
        namespace = KLNamespace(namespaceName)
        self.__namespaces[namespaceName] = namespace
        return namespace

    def getNamespaceNames(self):
        return self.__namespaces.keys()

    @staticmethod
    def isSetter(funcName):
        if funcName.startswith('set') is False: return False
        if len(funcName) < 4: return False
        if funcName[3].islower(): return False
        return True

    @staticmethod
    def isGetter(funcName):
        if funcName.startswith('get') is False: return False
        if len(funcName) < 4: return False
        if funcName[3].islower(): return False
        return True

    def __parse(self, data, currentKLNamespace):
        if isinstance(data, dict):
            if 'globalList' in data:
                self.__parse(data['globalList'], currentKLNamespace)
        elif isinstance(data, list):
            for elementList in data:
                elementType = elementList['type']

                if elementType == 'ASTNamespaceGlobal':
                    klNamespaceName = elementList['namespacePath']
                    klNamespace = self.getNamespace(klNamespaceName)
                    if klNamespace is None:
                        klNamespace = self.addNamespace(klNamespaceName)
                    print klNamespace
                    print type(klNamespace)
                    self.__parse(elementList['globalList'], klNamespace)

                elif elementType == 'ASTObjectDecl':
                    objectName = elementList['name']
                    objectMembers = elementList['members'] if 'members' in elementList else []
                    if not currentKLNamespace.hasObject(objectName):
                        currentKLNamespace.addObject(KLObject(objectName, objectMembers))
                    else:
                        currentKLNamespace.getObject(objectName).setMembers(objectMembers)

                elif elementType == 'Function':
                    functionName = elementList['name']
                    access = elementList['access']
                    returnType = elementList['returnType'] if 'returnType' in elementList else None
                    params = elementList['params'] if 'params' in elementList else None
                    klFunction = KLFunction(functionName, returnType=returnType, access=access)
                    if params:
                        klFunction.addParams(params)

                    if currentKLNamespace.hasObject(functionName):
                        klObject = currentKLNamespace.getObject(functionName)
                        klObject.addConstructor(klFunction)
                    else:
                        currentKLNamespace.addFunction(klFunction)

                elif elementType == 'MethodOpImpl':
                    methodName = elementList['name']
                    objectName = elementList['thisType']
                    if not currentKLNamespace.hasObject(objectName):
                        currentKLNamespace.addObject(KLObject(objectName))
                    klObject = currentKLNamespace.getObject(objectName)

                    access = elementList['access']
                    returnType = elementList['returnType'] if 'returnType' in elementList else None
                    params = elementList['params'] if 'params' in elementList else None

                    if KLEnv.isGetter(methodName):
                        klObject.addGetter(methodName, returnType, access)
                    elif KLEnv.isSetter(methodName):
                        klObject.addSetter(methodName, params, access)
                    else:
                        klObject.addMethod(methodName, returnType, params, access)

                else:
                    print '================ Unsupported AST element type:', elementType
                    # print elementList.keys()
                    # print elementList.values()
        else:
            for d in data:
                self.__parse(d, klNamespace)
