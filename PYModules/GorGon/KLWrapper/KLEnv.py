import json
import FabricEngine.Core as FECore
from KLNamespace import KLNamespace
from KLObject import KLObject
from KLStruct import KLStruct
from KLFunction import KLFunction
from KLAlias import KLAlias

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
                self.__preparse(d, self.__globalNamespace)
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

    def __preparse(self, data, currentKLNamespace):
        elementTypeToSkip = ['Function', 'MethodOpImpl']
        elementTypeToSkip.append('Destructor') # for now
        elementTypeToSkip.append('Operator') # for now
        elementTypeToSkip.append('GlobalConstDecl') # for now
        elementTypeToSkip.append('ASTUsingGlobal') # for now
        elementTypeToSkip.append('AssignOpImpl') # for now
        elementTypeToSkip.append('ASTInterfaceDecl') # for now
        elementTypeToSkip.append('RequireGlobal') # for now
        # elementTypeToSkip.append('Alias') # for now
        elementTypeToSkip.append('ComparisonOpImpl') # for now
        elementTypeToSkip.append('BinOpImpl') # for now
        elementTypeToSkip.append('ASTUniOpDecl') # for now
        if isinstance(data, dict):
            if 'globalList' in data:
                self.__preparse(data['globalList'], currentKLNamespace)
        elif isinstance(data, list):
            for elementList in data:
                elementType = elementList['type']

                if elementType == 'ASTNamespaceGlobal':
                    klNamespaceName = elementList['namespacePath']
                    klNamespace = self.getNamespace(klNamespaceName)
                    if klNamespace is None:
                        klNamespace = self.addNamespace(klNamespaceName)
                    self.__preparse(elementList['globalList'], klNamespace)

                elif elementType == 'ASTObjectDecl':
                    objectName = elementList['name']
                    objectMembers = elementList['members'] if 'members' in elementList else []
                    if not currentKLNamespace.hasObject(objectName):
                        currentKLNamespace.addObject(KLObject(objectName, objectMembers))
                    else:
                        currentKLNamespace.getObject(objectName).setMembers(objectMembers)

                elif elementType == 'ASTStructDecl':
                    structName = elementList['name']
                    structMembers = elementList['members'] if 'members' in elementList else []
                    if not currentKLNamespace.hasStruct(structName):
                        currentKLNamespace.addStruct(KLStruct(structName, structMembers))
                    else:
                        currentKLNamespace.getStruct(structName).setMembers(structMembers)

                elif elementType == 'Alias':
                    print 'YEAH'
                    print elementList.keys()
                    print elementList.values()
                    aliasName = elementList['newUserName']
                    aliasSourceName = elementList['oldUserName']
                    if not currentKLNamespace.hasAlias(aliasName):
                        currentKLNamespace.addAlias(KLAlias(aliasName, aliasSourceName))
                    else:
                        print 'Alias defined again? WTF?'


                elif elementType not in elementTypeToSkip:
                    print '================ Unsupported AST element type:', elementType
                    print elementList.keys()
                    print elementList.values()

        else:
            for d in data:
                self.__preparse(d, currentKLNamespace)

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
                    self.__parse(elementList['globalList'], klNamespace)

                elif elementType == 'ASTObjectDecl':
                    pass # already processed in __preparse

                elif elementType == 'ASTStructDecl':
                    pass # already processed in __preparse

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
                        if currentKLNamespace.hasStruct(functionName):
                            klStruct = currentKLNamespace.getStruct(functionName)
                            klStruct.addConstructor(klFunction)
                        else:
                            # not an object or a struct so it's a global function
                            currentKLNamespace.addFunction(klFunction)

                elif elementType == 'MethodOpImpl':
                    methodName = elementList['name']
                    objectName = elementList['thisType']

                    if currentKLNamespace.hasObject(objectName):
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

                    elif currentKLNamespace.hasStruct(objectName):
                        klStruct = currentKLNamespace.getStruct(objectName)

                        access = elementList['access']
                        returnType = elementList['returnType'] if 'returnType' in elementList else None
                        params = elementList['params'] if 'params' in elementList else None

                        if KLEnv.isGetter(methodName):
                            klStruct.addGetter(methodName, returnType, access)
                        elif KLEnv.isSetter(methodName):
                            klStruct.addSetter(methodName, params, access)
                        else:
                            klStruct.addMethod(methodName, returnType, params, access)

                    elif currentKLNamespace.hasAlias(objectName):
                        klAlias = currentKLNamespace.getAlias(objectName)

                        access = elementList['access']
                        returnType = elementList['returnType'] if 'returnType' in elementList else None
                        params = elementList['params'] if 'params' in elementList else None

                        klAlias.addMethod(methodName, returnType, params, access)
                    else:
                        print '******** WTF (alias?) ?? cant find', objectName, methodName

                else:
                    pass
                    # print '================ Unsupported AST element type:', elementType
                    # print elementList.keys()
                    # print elementList.values()
        else:
            for d in data:
                self.__parse(d, currentKLNamespace)
