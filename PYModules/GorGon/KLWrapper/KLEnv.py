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

class KLEnv:

    def __init__(self):
        self.__fabricClient = FECore.createClient()
        self.reset()

    def reset(self):
        self.__globalNamespace = KLNamespace('global')
        self.__namespaces = {}

    def parseSourceCode(self, sourceCode):
        ast = self.__fabricClient.getKLJSONAST('AST.kl', sourceCode, True)
        data = json.loads(ast.getStringCString())['ast']
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
        elementTypeToSkip = ['Function', 'MethodOpImpl', 'Destructor', 'AssignOpImpl', 'BinOpImpl', 'ComparisonOpImpl', 'ASTUniOpDecl', 'GlobalConstDecl'] # supported in __parse
        elementTypeToSkip.append('Operator') # for now
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

                elif elementType == 'ASTInterfaceDecl':
                    interfaceName = elementList['name']
                    interfaceMembers = elementList['members'] if 'members' in elementList else []
                    if not currentKLNamespace.hasInterface(interfaceName):
                        currentKLNamespace.addInterface(KLInterface(interfaceName))
                    currentKLNamespace.getInterface(interfaceName).setMembers(interfaceMembers)

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
                    aliasName = elementList['newUserName']
                    aliasSourceName = elementList['oldUserName']
                    if not currentKLNamespace.hasAlias(aliasName):
                        currentKLNamespace.addAlias(KLAlias(aliasName, aliasSourceName))
                    else:
                        print 'Alias defined again? WTF?'

                elif elementType == 'ASTUsingGlobal':
                    extensionName = elementList['owningExtName']
                    if currentKLNamespace.hasExtension(extensionName) is False:
                        currentKLNamespace.addExtension(KLExtension(extensionName))
                    currentKLNamespace.getExtension(extensionName).addExtensionDependency(elementList['namespacePath'])

                elif elementType == 'RequireGlobal':
                    if 'owningExtName' in elementList:
                        extensionName = elementList['owningExtName']
                        if currentKLNamespace.hasExtension(extensionName) is False:
                            currentKLNamespace.addExtension(KLExtension(extensionName))
                        for d in elementList['requires']:
                            currentKLNamespace.getExtension(extensionName).addExtensionDependency(d['name'])
                    else:
                        for d in elementList['requires']:
                            extensionName = d['name']
                            if currentKLNamespace.hasExtension(extensionName) is False:
                                currentKLNamespace.addExtension(KLExtension(extensionName))

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
                    # no namespace to create but we still need to parse it!
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

                elif elementType == "Destructor":
                    objectName = elementList['thisType']

                    if currentKLNamespace.hasObject(objectName):
                        klObject = currentKLNamespace.getObject(objectName)
                        klObject.setHasDestructor(True)
                    elif currentKLNamespace.hasStruct(objectName):
                        klStruct = currentKLNamespace.getStruct(objectName)
                        klStruct.setHasDestructor(True)
                    else:
                        print '******** WTF (destructor on unknown type??) ??', objectName

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
                        print '******** WTF.MethodOpImpl (alias or builtin type?) ?? cant find', objectName, methodName

                elif elementType == 'AssignOpImpl':
                    opName = elementList['assignOpType']
                    objectName = elementList['thisType']

                    if currentKLNamespace.hasObject(objectName):
                        klObject = currentKLNamespace.getObject(objectName)
                        access = elementList['access']
                        params = elementList['rhs']
                        klObject.addOperator(opName, params, access)

                    elif currentKLNamespace.hasStruct(objectName):
                        klStruct = currentKLNamespace.getStruct(objectName)
                        access = elementList['access']
                        params = elementList['rhs']
                        klStruct.addOperator(opName, params, access)

                    elif currentKLNamespace.hasAlias(objectName):
                        klAlias = currentKLNamespace.getAlias(objectName)
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
                    currentKLNamespace.addOperator(klOp)

                elif elementType == 'ASTUniOpDecl':

                    opName = elementList['uniOpType']
                    returnType = elementList['returnType']
                    access = elementList['access']

                    klOp = KLFunction(opName, returnType=returnType, access=access)
                    currentKLNamespace.addOperator(klOp)

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

                    currentKLNamespace.addConstant(KLConstant(constType, constName, constValue))

                else:
                    pass # parse should let us know if/when something is not supported!

        else:
            for d in data:
                self.__parse(d, currentKLNamespace)
