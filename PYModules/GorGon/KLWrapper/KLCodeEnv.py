import json
import FabricEngine.Core as FECore
from KLNamespace import KLNamespace
from KLInterface import KLInterface
from KLObject import KLObject
from KLStruct import KLStruct
from KLFunction import KLFunction
from KLAlias import KLAlias
from KLConstant import KLConstant
from KLExtension import KLExtension

class KLCodeEnv:

    def __init__(self):
        self.__fabricClient = FECore.createClient()
        self.reset()

    def getFabricClient(self):
        return self.__fabricClient

    def reset(self):
        self.__globalNamespace = KLNamespace('global') # to remove
        self.__namespaces = {} # to remove
        self.__extensions = {}

    def parseSourceCode(self, sourceCode):
        ast = self.__fabricClient.getKLJSONAST('AST.kl', sourceCode, True)
        data = json.loads(ast.getStringCString())['ast']
        for ext in data:
            for d in ext:
                self.__preParse(d, self.__globalNamespace)
        for ext in data:
            for d in ext:
                self.__parse(d, self.__globalNamespace)
        for ext in data:
            for d in ext:
                self.__postParse(d, self.__globalNamespace)

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

    def getExtensionNames(self):
        return self.__extensions.keys()

    def addExtension(self, ext):
        self.__extensions[ext.getName()] = ext

    def getExtension(self, extensionName, addExtensionIfMissing=False):
        if addExtensionIfMissing:
            if self.hasExtension(extensionName) is False:
                self.addExtension(KLExtension(extensionName))
        return self.__extensions[extensionName]

    def getRTExtension(self):
        return self.getExtension('[MEM]') # todo: rename this to [RT]

    def hasExtension(self, extensionName):
        return extensionName in self.__extensions

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

    def __preParse(self, data, currentKLNamespace):
        if isinstance(data, dict):
            if 'globalList' in data:
                self.__preParse(data['globalList'], currentKLNamespace)
        elif isinstance(data, list):
            for elementList in data:
                elementType = elementList['type']

                if elementType == 'RequireGlobal':
                    if 'owningExtName' in elementList:
                        extensionName = elementList['owningExtName']
                        if self.hasExtension(extensionName) is False:
                            self.addExtension(KLExtension(extensionName))
                        for d in elementList['requires']:
                            self.getExtension(extensionName).addExtensionDependency(d['name'])
                    else:
                        for d in elementList['requires']:
                            extensionName = d['name']
                            if self.hasExtension(extensionName) is False:
                                self.addExtension(KLExtension(extensionName))

        else:
            for d in data:
                self.__preParse(d, currentKLNamespace)

    def __parse(self, data, currentKLNamespace):
        elementTypeToSkip = ['RequireGlobal', 'Function', 'MethodOpImpl', 'Destructor', 'AssignOpImpl', 'BinOpImpl', 'ComparisonOpImpl', 'ASTUniOpDecl', 'GlobalConstDecl'] # supported in __parse
        elementTypeToSkip.append('Operator') # for now
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
                    self.__parse(elementList['globalList'], klNamespace)

                elif elementType == 'ASTInterfaceDecl':
                    interfaceName = elementList['name']
                    interfaceMembers = elementList['members'] if 'members' in elementList else []

                    currentKLN = self.__getCurrentNamespace(elementList, currentKLNamespace)

                    if not currentKLN.hasInterface(interfaceName):
                        currentKLN.addInterface(KLInterface(interfaceName))
                    currentKLN.getInterface(interfaceName).setMembers(interfaceMembers)

                elif elementType == 'ASTObjectDecl':
                    objectName = elementList['name']
                    objectMembers = elementList['members'] if 'members' in elementList else []

                    currentKLN = self.__getCurrentNamespace(elementList, currentKLNamespace)

                    if not currentKLN.hasObject(objectName):
                        currentKLN.addObject(KLObject(objectName, objectMembers))
                    else:
                        currentKLN.getObject(objectName).setMembers(objectMembers)

                elif elementType == 'ASTStructDecl':
                    structName = elementList['name']
                    structMembers = elementList['members'] if 'members' in elementList else []

                    currentKLN = self.__getCurrentNamespace(elementList, currentKLNamespace)

                    if not currentKLN.hasStruct(structName):
                        currentKLN.addStruct(KLStruct(structName, structMembers))
                    else:
                        currentKLN.getStruct(structName).setMembers(structMembers)

                elif elementType == 'Alias':
                    aliasName = elementList['newUserName']
                    aliasSourceName = elementList['oldUserName']

                    currentKLN = self.__getCurrentNamespace(elementList, currentKLNamespace)

                    if not currentKLN.hasAlias(aliasName):
                        currentKLN.addAlias(KLAlias(aliasName, aliasSourceName))

                    else:
                        print 'Alias defined again? WTF?'

                elif elementType == 'ASTUsingGlobal':
                    extensionName = elementList['owningExtName']

                    currentKLN = self.__getCurrentNamespace(elementList, currentKLNamespace)

                    if currentKLN.hasExtension(extensionName) is False:
                        currentKLN.addExtension(KLExtension(extensionName))
                    currentKLN.getExtension(extensionName).addExtensionDependency(elementList['namespacePath'])

                elif elementType not in elementTypeToSkip:
                    print '================ Unsupported AST element type:', elementType
                    print elementList.keys()
                    print elementList.values()

        else:
            for d in data:
                self.__parse(d, currentKLNamespace)

    def __postParse(self, data, currentKLNamespace):
        if isinstance(data, dict):
            if 'globalList' in data:
                self.__postParse(data['globalList'], currentKLNamespace)
        elif isinstance(data, list):
            for elementList in data:
                elementType = elementList['type']

                if elementType == 'ASTNamespaceGlobal':
                    klNamespaceName = elementList['namespacePath']
                    klNamespace = self.getNamespace(klNamespaceName)
                    # no namespace to create but we still need to parse it!
                    self.__postParse(elementList['globalList'], klNamespace)

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

                    currentKLN = self.__getCurrentNamespace(elementList, currentKLNamespace)  # todo use currentKLNamespaceName and refactor the code! we only need the namespace name not the object
                    if currentKLN.hasObject(functionName):
                        klObject = currentKLN.getObject(functionName)
                        klObject.addConstructor(klFunction)
                    else:
                        if currentKLN.hasStruct(functionName):
                            klStruct = currentKLN.getStruct(functionName)
                            klStruct.addConstructor(klFunction)
                        else:
                            # not an object or a struct so it's a global function
                            currentKLN.addFunction(klFunction)

                elif elementType == "Destructor":
                    objectName = elementList['thisType']

                    currentKLN = self.__getCurrentNamespace(elementList, currentKLNamespace)
                    if currentKLN.hasObject(objectName):
                        klObject = currentKLN.getObject(objectName)
                        klObject.setHasDestructor(True)
                    elif currentKLN.hasStruct(objectName):
                        klStruct = currentKLN.getStruct(objectName)
                        klStruct.setHasDestructor(True)
                    else:
                        print '******** WTF (destructor on unknown type??) ??', objectName

                elif elementType == 'MethodOpImpl':
                    methodName = elementList['name']
                    objectName = elementList['thisType']
                    currentKLN = self.__getCurrentNamespace(elementList, currentKLNamespace)  # todo use currentKLNamespaceName and refactor the code! we only need the namespace name not the object

                    if currentKLN.hasObject(objectName):
                        klObject = currentKLN.getObject(objectName)

                        access = elementList['access']
                        returnType = elementList['returnType'] if 'returnType' in elementList else None
                        params = elementList['params'] if 'params' in elementList else None

                        if KLCodeEnv.isGetter(methodName):
                            klObject.addGetter(methodName, returnType, access)
                        elif KLCodeEnv.isSetter(methodName):
                            klObject.addSetter(methodName, params, access)
                        else:
                            klObject.addMethod(methodName, returnType, params, access)

                    elif currentKLN.hasStruct(objectName):
                        klStruct = currentKLN.getStruct(objectName)

                        access = elementList['access']
                        returnType = elementList['returnType'] if 'returnType' in elementList else None
                        params = elementList['params'] if 'params' in elementList else None

                        if KLCodeEnv.isGetter(methodName):
                            klStruct.addGetter(methodName, returnType, access)
                        elif KLCodeEnv.isSetter(methodName):
                            klStruct.addSetter(methodName, params, access)
                        else:
                            klStruct.addMethod(methodName, returnType, params, access)

                    elif currentKLN.hasAlias(objectName):
                        klAlias = currentKLN.getAlias(objectName)

                        access = elementList['access']
                        returnType = elementList['returnType'] if 'returnType' in elementList else None
                        params = elementList['params'] if 'params' in elementList else None

                        klAlias.addMethod(methodName, returnType, params, access)
                    else:
                        print '******** WTF.MethodOpImpl (alias or builtin type?) ?? cant find', objectName, methodName

                elif elementType == 'AssignOpImpl':
                    opName = elementList['assignOpType']
                    objectName = elementList['thisType']

                    currentKLN = self.__getCurrentNamespace(elementList, currentKLNamespace) # todo use currentKLNamespaceName and refactor the code! we only need the namespace name not the object
                    if currentKLN.hasObject(objectName):
                        klObject = currentKLN.getObject(objectName)
                        access = elementList['access']
                        params = elementList['rhs']
                        klObject.addOperator(opName, params, access)

                    elif currentKLN.hasStruct(objectName):
                        klStruct = currentKLN.getStruct(objectName)
                        access = elementList['access']
                        params = elementList['rhs']
                        klStruct.addOperator(opName, params, access)

                    elif currentKLN.hasAlias(objectName):
                        klAlias = currentKLN.getAlias(objectName)
                        access = elementList['access']
                        params = elementList['rhs']
                        klAlias.addOperator(opName, params, access)

                    else:
                        print '******** WTF.AssignOpImpl (alias or builtin type TODO?) ?? cant find', objectName

                elif elementType == 'BinOpImpl' or elementType == 'ComparisonOpImpl':

                    opName = elementList['binOpType']
                    returnType = elementList['returnType']
                    access = elementList['access']

                    klOp = KLFunction(opName, returnType=returnType, access=access)
                    klOp.addParams(elementList['lhs'])
                    klOp.addParams(elementList['rhs'])

                    currentKLN = self.__getCurrentNamespace(elementList, currentKLNamespace)
                    currentKLN.addOperator(klOp)

                elif elementType == 'ASTUniOpDecl':

                    opName = elementList['uniOpType']
                    returnType = elementList['returnType']
                    access = elementList['access']

                    klOp = KLFunction(opName, returnType=returnType, access=access)

                    currentKLN = self.__getCurrentNamespace(elementList, currentKLNamespace)
                    currentKLN.addOperator(klOp)

                elif elementType == 'GlobalConstDecl':

                    val = elementList['constDecl']['value']
                    constType = val['type']
                    constName = elementList['constDecl']['name']

                    if 'valueBool' not in val and 'valueString' not in val:

                        if 'binOpType' in val:

                            constType = val['binOpType']
                            lhs_val = val['lhs']
                            rhs_val = val['rhs']

                            if 'valueBool' not in lhs_val and 'valueString' not in lhs_val:
                                lhs_value = lhs_val['name']
                            else:
                                lhs_value = lhs_val['valueBool'] if 'valueBool' in lhs_val else lhs_val['valueString']

                            if 'valueBool' not in val and 'valueString' not in rhs_val:
                                rhs_value = rhs_val['name']
                            else:
                                rhs_value = rhs_val['valueBool'] if 'valueBool' in rhs_val else rhs_val['valueString']

                            constValue  = '{}({},{})'.format(val['binOpType'], lhs_value, rhs_value)

                        elif 'uniOpType' in val:

                            constType = val['uniOpType']
                            constValue = '{}({})'.format(val['uniOpType'], val['child']['valueString'])

                    else:
                        constValue = val['valueBool'] if 'valueBool' in val else val['valueString']

                    currentKLN = self.__getCurrentNamespace(elementList, currentKLNamespace)
                    currentKLN.addConstant(KLConstant(constType, constName, constValue))

                else:
                    pass # parse should let us know if/when something is not supported!

        else:
            for d in data:
                self.__postParse(d, currentKLNamespace)

    @staticmethod
    def __getExtensionName(elementList):
        return elementList['owningExtName'] if 'owningExtName' in elementList else '[MEM]' # todo: store that somewhere

    def __getCurrentNamespace(self, elementList, currentKLNamespace):
        return self.getExtension(self.__getExtensionName(elementList), True).getNamespace(currentKLNamespace.getName(), True)