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

    __RT_EXTENSION_NAME = '[RT]'

    def __init__(self):
        self.__fabricClient = FECore.createClient()
        self.reset()

    def isRTExtension(self, extensionName):
        return extensionName == self.__RT_EXTENSION_NAME

    def getFabricClient(self):
        return self.__fabricClient

    def reset(self):
        self.__extensions = {}

    def parseSourceCode(self, sourceCode, includeRequires = True):
        ast = self.__fabricClient.getKLJSONAST('AST.kl', sourceCode, includeRequires)
        data = json.loads(ast.getStringCString())['ast']
        # todo: something when there's a compiler error!!
        for ext in data:
            for d in ext:
                self.__preParse(d, 'global')
        for ext in data:
            for d in ext:
                self.__parse(d, 'global')
        for ext in data:
            for d in ext:
                self.__postParse(d, 'global')
        self.__linkContent()

    def __linkContent(self):
        for extensionName in self.__extensions:
            klExtension = self.getExtension(extensionName)
            namespaceNames = klExtension.getNamespaceNames(True)
            for namespaceName in namespaceNames:
                klNamespace = klExtension.getNamespace(namespaceName)
                for objectName in klNamespace.getObjectNames():
                    klObject = klNamespace.getObject(objectName)
                    newParentsAndInterfaces = []
                    for poiName in klObject._getParents():
                        poi = self.__findParent(poiName)
                        if poi:
                            newParentsAndInterfaces.append(poi)
                        else:
                            print 'WTF? cant find', poiName
                    klObject._setParents(newParentsAndInterfaces) # we override it

    def __findParent(self, poiName):
        for extensionName in self.__extensions:
            klExtension = self.getExtension(extensionName)
            for namespaceName in self.getExtension(extensionName).getNamespaceNames(True):
                klNamespace = klExtension.getNamespace(namespaceName)
                if klNamespace.hasInterface(poiName):
                    return klNamespace.getInterface(poiName)
                elif klNamespace.hasObject(poiName):
                    return klNamespace.getObject(poiName)
                elif klNamespace.hasStruct(poiName):
                    return klNamespace.getStruct(poiName)
        return None

    def getNamespaceNames(self):
        namespaceNames = []
        for ext_name in self.getExtensionNames():
            namespaceNames.extend(self.getExtension(ext_name).getNamespaceNames())
        return list(set(namespaceNames))

    def getExtensionNames(self):
        return self.__extensions.keys()

    def __addExtension(self, ext):
        self.__extensions[ext.getName()] = ext

    def getExtension(self, extensionName, addExtensionIfMissing=False):
        if addExtensionIfMissing:
            if self.hasExtension(extensionName) is False:
                self.__addExtension(KLExtension(extensionName))
        return self.__extensions[extensionName]

    def getRTExtension(self):
        return self.getExtension(KLCodeEnv.__RT_EXTENSION_NAME)

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

    def __preParse(self, data, currentKLNamespaceName):
        if isinstance(data, dict):
            if 'globalList' in data:
                self.__preParse(data['globalList'], currentKLNamespaceName)
        elif isinstance(data, list):
            for elementList in data:
                elementType = elementList['type']

                if elementType == 'RequireGlobal':
                    if 'owningExtName' in elementList:
                        extensionName = elementList['owningExtName']
                        if self.hasExtension(extensionName) is False:
                            self.__addExtension(KLExtension(extensionName))
                        for d in elementList['requires']:
                            self.getExtension(extensionName).addExtensionDependency(d['name'])
                    else:
                        for d in elementList['requires']:
                            extensionName = d['name']
                            if self.hasExtension(extensionName) is False:
                                self.__addExtension(KLExtension(extensionName))
        else:
            for d in data:
                self.__preParse(d, currentKLNamespaceName)

    def __parse(self, data, currentKLNamespaceName):
        if isinstance(data, dict):
            if 'globalList' in data:
                self.__parse(data['globalList'], currentKLNamespaceName)
        elif isinstance(data, list):
            elementTypeToSkip = ['RequireGlobal', 'Function', 'MethodOpImpl', 'Destructor', 'AssignOpImpl', 'BinOpImpl', 'ComparisonOpImpl', 'ASTUniOpDecl', 'GlobalConstDecl'] # supported in __parse
            elementTypeToSkip.append('Operator') # for now
            for elementList in data:
                elementType = elementList['type']

                functors = {
                    'ASTInterfaceDecl'  : self.__processInterface,
                    'ASTObjectDecl'     : self.__processObject,
                    'ASTStructDecl'     : self.__processStruct,
                    'Alias'             : self.__processAlias
                }

                if elementType in functors:
                    currentKLN = self.__getCurrentNamespace(elementList, currentKLNamespaceName)
                    functors[elementType](elementList, currentKLN)

                elif elementType == 'ASTNamespaceGlobal':
                    klNamespaceName = elementList['namespacePath']
                    self.__parse(elementList['globalList'], klNamespaceName)

                elif elementType == 'ASTUsingGlobal':
                    currentExt = self.__getCurrentExtension(elementList)
                    currentExt.addExtensionDependency(elementList['namespacePath'])

                elif elementType not in elementTypeToSkip:
                    print '================ Unsupported AST element type:', elementType
                    print elementList.keys()
                    print elementList.values()
        else:
            for d in data:
                self.__parse(d, currentKLNamespaceName)

    def __postParse(self, data, currentKLNamespaceName):
        if isinstance(data, dict):
            if 'globalList' in data:
                self.__postParse(data['globalList'], currentKLNamespaceName)
        elif isinstance(data, list):
            for elementList in data:
                elementType = elementList['type']

                functors = {
                    'ASTObjectDecl'  : self.__processNothing,
                    'ASTStructDecl'  : self.__processNothing,
                    'Function'  : self.__processFunction,
                    "Destructor"  : self.__processDestructor,
                    'MethodOpImpl'  : self.__processMethod,
                    'AssignOpImpl'  : self.__processAssignOp,
                    'BinOpImpl'  : self.__processBinOrComparisonOp,
                    'ComparisonOpImpl'  : self.__processBinOrComparisonOp,
                    'ASTUniOpDecl'  : self.__processUniOp,
                    'GlobalConstDecl'  : self.__processConstDecl,
                }

                if elementType in functors:
                    currentKLN = self.__getCurrentNamespace(elementList, currentKLNamespaceName)
                    functors[elementType](elementList, currentKLN)
                elif elementType == 'ASTNamespaceGlobal':
                    # no namespace to create but we still need to parse it!
                    self.__postParse(elementList['globalList'], elementList['namespacePath'])
        else:
            for d in data:
                self.__postParse(d, currentKLNamespaceName)

    @staticmethod
    def __getExtensionName(elementList):
        return elementList['owningExtName'] if 'owningExtName' in elementList else KLCodeEnv.__RT_EXTENSION_NAME

    def __getCurrentNamespace(self, elementList, currentKLNamespaceName):
        return self.getExtension(self.__getExtensionName(elementList), True).getNamespace(currentKLNamespaceName, True)

    def __getCurrentExtension(self, elementList):
        return self.getExtension(self.__getExtensionName(elementList), True)

    @staticmethod
    def __processNothing(elementList, currentKLN):
        pass

    @staticmethod
    def __processInterface(elementList, currentKLN):
        interfaceName = elementList['name']
        interfaceMembers = elementList['members'] if 'members' in elementList else []
        if not currentKLN.hasInterface(interfaceName):
            currentKLN._addInterface(KLInterface(interfaceName))
        currentKLN.getInterface(interfaceName)._setMembers(interfaceMembers)

    @staticmethod
    def __processObject(elementList, currentKLN):
        objectName = elementList['name']
        objectMembers = elementList['members'] if 'members' in elementList else []
        objectParentsAndInterfaces = elementList['parentsAndInterfaces'] if 'parentsAndInterfaces' in elementList else []
        if not currentKLN.hasObject(objectName):
            currentKLN._addObject(KLObject(objectName))
        currentKLN.getObject(objectName)._setMembers(objectMembers)
        currentKLN.getObject(objectName)._setParents(objectParentsAndInterfaces)

    @staticmethod
    def __processStruct(elementList, currentKLN):
        structName = elementList['name']
        structMembers = elementList['members'] if 'members' in elementList else []
        if not currentKLN.hasStruct(structName):
            currentKLN._addStruct(KLStruct(structName))
        currentKLN.getStruct(structName)._setMembers(structMembers)

    @staticmethod
    def __processAlias(elementList, currentKLN):
        aliasName = elementList['newUserName']
        aliasSourceName = elementList['oldUserName']
        if not currentKLN.hasAlias(aliasName):
            currentKLN._addAlias(KLAlias(aliasName, aliasSourceName))
        else:
            print 'Alias defined again? WTF?'

    @staticmethod
    def __processFunction(elementList, currentKLN):
        functionName = elementList['name']
        access = elementList['access']
        returnType = elementList['returnType'] if 'returnType' in elementList else None
        params = elementList['params'] if 'params' in elementList else None
        klFunction = KLFunction(functionName, returnType=returnType, access=access)
        if params:
            klFunction._addParams(params)
        if currentKLN.hasObject(functionName):
            klObject = currentKLN.getObject(functionName)
            klObject._addConstructor(klFunction)
        else:
            if currentKLN.hasStruct(functionName):
                klStruct = currentKLN.getStruct(functionName)
                klStruct._addConstructor(klFunction)
            else:
                # not an object or a struct so it's a global function
                currentKLN._addFunction(klFunction)

    @staticmethod
    def __processDestructor(elementList, currentKLN):
        objectName = elementList['thisType']
        if currentKLN.hasObject(objectName):
            klObject = currentKLN.getObject(objectName)
            klObject._setHasDestructor(True)
        elif currentKLN.hasStruct(objectName):
            klStruct = currentKLN.getStruct(objectName)
            klStruct._setHasDestructor(True)
        else:
            print '******** WTF (destructor on unknown type??) ??', objectName

    @staticmethod
    def __processMethod(elementList, currentKLN):
        methodName = elementList['name']
        objectName = elementList['thisType']
        if currentKLN.hasObject(objectName):
            klObject = currentKLN.getObject(objectName)

            access = elementList['access']
            returnType = elementList['returnType'] if 'returnType' in elementList else None
            params = elementList['params'] if 'params' in elementList else None

            if KLCodeEnv.isGetter(methodName):
                klObject._addGetter(methodName, returnType, access)
            elif KLCodeEnv.isSetter(methodName):
                klObject._addSetter(methodName, params, access)
            else:
                klObject._addMethod(methodName, returnType, params, access)
        elif currentKLN.hasStruct(objectName):
            klStruct = currentKLN.getStruct(objectName)

            access = elementList['access']
            returnType = elementList['returnType'] if 'returnType' in elementList else None
            params = elementList['params'] if 'params' in elementList else None

            if KLCodeEnv.isGetter(methodName):
                klStruct._addGetter(methodName, returnType, access)
            elif KLCodeEnv.isSetter(methodName):
                klStruct._addSetter(methodName, params, access)
            else:
                klStruct._addMethod(methodName, returnType, params, access)
        elif currentKLN.hasAlias(objectName):
            klAlias = currentKLN.getAlias(objectName)

            access = elementList['access']
            returnType = elementList['returnType'] if 'returnType' in elementList else None
            params = elementList['params'] if 'params' in elementList else None

            klAlias._addMethod(methodName, returnType, params, access)
        else:
            print '******** WTF.MethodOpImpl (alias or builtin type?) ?? cant find', objectName, methodName

    @staticmethod
    def __processAssignOp(elementList, currentKLN):
        opName = elementList['assignOpType']
        objectName = elementList['thisType']
        if currentKLN.hasObject(objectName):
            klObject = currentKLN.getObject(objectName)
            klObject._addOperator(opName, elementList['rhs'], elementList['access'])
        elif currentKLN.hasStruct(objectName):
            klStruct = currentKLN.getStruct(objectName)
            klStruct._addOperator(opName, elementList['rhs'], elementList['access'])
        elif currentKLN.hasAlias(objectName):
            klAlias = currentKLN.getAlias(objectName)
            klAlias._addOperator(opName, elementList['rhs'], elementList['access'])
        else:
            print '******** WTF.AssignOpImpl (alias or builtin type TODO?) ?? cant find', objectName

    @staticmethod
    def __processBinOrComparisonOp(elementList, currentKLN):
        opName = elementList['binOpType']
        klOp = KLFunction(opName, returnType=elementList['returnType'], access=elementList['access'])
        klOp._addParams(elementList['lhs'])
        klOp._addParams(elementList['rhs'])
        currentKLN._addOperator(klOp)

    @staticmethod
    def __processUniOp(elementList, currentKLN):
        opName = elementList['uniOpType']
        klOp = KLFunction(opName, returnType=elementList['returnType'], access=elementList['access'])
        currentKLN._addOperator(klOp)

    @staticmethod
    def __processConstDecl(elementList, currentKLN):
        constDeclDict = elementList['constDecl']
        val = constDeclDict['value'] if 'value' in constDeclDict else ''
        constName = constDeclDict['name']

        if val == '':
            constValue = ''
            constType = constDeclDict['type']
        else:
            constType = val['type']
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

        currentKLN.addConstant(KLConstant(constType, constName, constValue))