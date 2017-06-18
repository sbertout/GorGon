import sys, unittest
from GorGon.KLWrapper.KLCodeEnv import KLCodeEnv

class KLWrapperTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(KLWrapperTests, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        cls.klEnv = KLCodeEnv()

    def tearDown(self):
        super(KLWrapperTests, self).tearDown()
        self.klEnv.reset()

    #===================================================================================================================
    def test_IsSetter(self):
        self.assertEqual(KLCodeEnv.isSetter('doSomething'), False)
        self.assertEqual(KLCodeEnv.isSetter('Set'), False)
        self.assertEqual(KLCodeEnv.isSetter('SetSomething'), False)
        self.assertEqual(KLCodeEnv.isSetter('set'), False)
        self.assertEqual(KLCodeEnv.isSetter('setSomething'), True)
        self.assertEqual(KLCodeEnv.isSetter('setX'), True)
        self.assertEqual(KLCodeEnv.isSetter('setup'), False)

    #===================================================================================================================
    def test_IsGetter(self):
        self.assertEqual(KLCodeEnv.isGetter('doSomething'), False)
        self.assertEqual(KLCodeEnv.isGetter('Get'), False)
        self.assertEqual(KLCodeEnv.isGetter('GetSomething'), False)
        self.assertEqual(KLCodeEnv.isGetter('get'), False)
        self.assertEqual(KLCodeEnv.isGetter('getSomething'), True)
        self.assertEqual(KLCodeEnv.isGetter('getX'), True)
        self.assertEqual(KLCodeEnv.isGetter('getup'), False)

    #===================================================================================================================
    def test_KLExtensions(self):
        client = self.klEnv.getFabricClient()
        extSources = [{
            "filename": "ext.kl",
            "sourceCode": """
            """
        }]
        client.registerKLExtension(
            "ExtensionFoo",
            extSources
        )
        client.registerKLExtension(
            "ExtensionBar",
            extSources
        )
        sourceCode = '''
            require ExtensionFoo;
            require ExtensionBar;
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getExtensionNames(), [u'ExtensionFoo', u'ExtensionBar'])

    #===================================================================================================================
    def __setup(self, sourceCode, testFuncName):
        useExtension = '_E1_' in testFuncName
        useNamespace = '_N1_' in testFuncName
        if useNamespace:
            sourceCode = 'namespace FooNamespace {' + sourceCode + '}'
        if useExtension:
            client = self.klEnv.getFabricClient()
            extSources = [{
                "filename": "ext.kl",
                "sourceCode": sourceCode
            }]
            client.registerKLExtension(
                testFuncName,
                extSources
            )
            self.klEnv.parseSourceCode('require {};'.format(testFuncName))
        else:
            self.klEnv.parseSourceCode(sourceCode)
        klExtension = self.klEnv.getRTExtension() if not useExtension else self.klEnv.getExtension(testFuncName)
        klNamespace = klExtension.getGlobalNamespace() if not useNamespace else klExtension.getNamespace('FooNamespace')
        return klExtension, klNamespace

    #===================================================================================================================

    sourceCode_KLConstants = '''
            const Boolean DebugSomething = false;
            const Scalar SomeScalarConstant = 3.14;
            const Scalar TWO_SomeScalarConstant = SomeScalarConstant * 2.0;
            const Float32 SomeNegativeFloat32Constant = -10e6;
            '''

    def __test_KLConstants_Content(self, klNamespace):
        self.assertEqual(klNamespace.getConstantCount(), 4)
        self.assertEqual(klNamespace.getConstantNames(), [u'SomeNegativeFloat32Constant', u'SomeScalarConstant', u'DebugSomething', u'TWO_SomeScalarConstant'])
        self.assertEqual(klNamespace.getConstant('DebugSomething').getName(), 'DebugSomething')
        self.assertEqual(klNamespace.getConstant('DebugSomething').getType(), 'ConstBoolean')
        self.assertEqual(klNamespace.getConstant('DebugSomething').getValue(), False)
        self.assertEqual(klNamespace.getConstant('SomeScalarConstant').getName(), 'SomeScalarConstant')
        self.assertEqual(klNamespace.getConstant('SomeScalarConstant').getType(), 'ASTConstFloat')
        self.assertEqual(klNamespace.getConstant('SomeScalarConstant').getValue(), '3.14')
        self.assertEqual(klNamespace.getConstant('TWO_SomeScalarConstant').getName(), 'TWO_SomeScalarConstant')
        self.assertEqual(klNamespace.getConstant('TWO_SomeScalarConstant').getType(), 'mul')
        self.assertEqual(klNamespace.getConstant('TWO_SomeScalarConstant').getValue(), 'mul(SomeScalarConstant,2.0)')
        self.assertEqual(klNamespace.getConstant('SomeNegativeFloat32Constant').getName(), 'SomeNegativeFloat32Constant')
        self.assertEqual(klNamespace.getConstant('SomeNegativeFloat32Constant').getType(), 'NEG')
        self.assertEqual(klNamespace.getConstant('SomeNegativeFloat32Constant').getValue(), 'NEG(10e6)')

    def test_KLConstants_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLConstants, sys._getframe().f_code.co_name)
        self.assertEqual(self.klEnv.getExtensionNames(), ['test_KLConstants_E1_N1_'])
        self.assertEqual(klExtension.getNamespaceNames(), ['FooNamespace'])
        self.__test_KLConstants_Content(klNamespace)

    def test_KLConstants_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLConstants, sys._getframe().f_code.co_name)
        self.assertEqual(self.klEnv.getExtensionNames(), ['test_KLConstants_E1_N0_'])
        self.__test_KLConstants_Content(klNamespace)

    def test_KLConstants_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLConstants, sys._getframe().f_code.co_name)
        self.assertEqual(str(self.klEnv.getExtensionNames()), "['[RT]']")
        self.__test_KLConstants_Content(klNamespace)

    def test_KLConstants_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLConstants, sys._getframe().f_code.co_name)
        self.assertEqual(str(self.klEnv.getExtensionNames()), "['[RT]']")
        self.__test_KLConstants_Content(klNamespace)

    #===================================================================================================================
    sourceCode_KLAliasConstants = '''
        alias Scalar SomeScalarAlias;
        const SomeScalarAlias SomeScalarConstant = 3.14;
        '''

    def __test_KLAliasConstants_Content(self, klNamespace):
        self.assertEqual(klNamespace.getAliasCount(), 1)
        self.assertEqual(klNamespace.getConstantCount(), 1)
        self.assertEqual(klNamespace.getConstant('SomeScalarConstant').getName(), 'SomeScalarConstant')
        self.assertEqual(klNamespace.getConstant('SomeScalarConstant').getType(), 'ASTConstFloat')
        self.assertEqual(klNamespace.getConstant('SomeScalarConstant').getValue(), '3.14')

    def test_KLAliasConstants_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLAliasConstants, sys._getframe().f_code.co_name)
        self.__test_KLAliasConstants_Content(klNamespace)

    def test_KLAliasConstants_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLAliasConstants, sys._getframe().f_code.co_name)
        self.__test_KLAliasConstants_Content(klNamespace)

    def test_KLAliasConstants_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLAliasConstants, sys._getframe().f_code.co_name)
        self.__test_KLAliasConstants_Content(klNamespace)

    def test_KLAliasConstants_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLAliasConstants, sys._getframe().f_code.co_name)
        self.__test_KLAliasConstants_Content(klNamespace)

    #===================================================================================================================

    sourceCode_KLAliases = '''
            alias UInt32 SomeIntAlias;
            alias Scalar SomeScalarAlias;
            '''

    def __test_KLAliases_Content(self, klNamespace):
        self.assertEqual(klNamespace.getAliasCount(), 2)
        self.assertEqual(klNamespace.getAlias('SomeIntAlias').getName(), 'SomeIntAlias')
        self.assertEqual(klNamespace.getAlias('SomeIntAlias').getSourceName(), 'UInt32')
        self.assertEqual(klNamespace.getAlias('SomeScalarAlias').getName(), 'SomeScalarAlias')
        self.assertEqual(klNamespace.getAlias('SomeScalarAlias').getSourceName(), 'Scalar')

    def test_KLAliases_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLAliases, sys._getframe().f_code.co_name)
        self.__test_KLAliases_Content(klNamespace)

    def test_KLAliases_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLAliases, sys._getframe().f_code.co_name)
        self.__test_KLAliases_Content(klNamespace)

    def test_KLAliases_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLAliases, sys._getframe().f_code.co_name)
        self.__test_KLAliases_Content(klNamespace)

    def test_KLAliases_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLAliases, sys._getframe().f_code.co_name)
        self.__test_KLAliases_Content(klNamespace)

    #===================================================================================================================

    sourceCode_KLAliasOperators = '''
            alias UInt32 SomeIntAlias;
            SomeIntAlias. *= (Integer other) {
              this = this * other;
            }
            SomeIntAlias. += (Boolean b) {
              this += b;
            }
            SomeIntAlias. *= (Scalar k) {
              this = this * k;
            }
            '''

    def __test_KLAliasOperators_Content(self, klNamespace):
        self.assertEqual(klNamespace.getAliasCount(), 1)
        klAlias = klNamespace.getAlias('SomeIntAlias')
        self.assertEqual(klAlias.getOperatorCount(), 3)
        klOp = klAlias.getOperator(0)
        self.assertEqual(klOp.getName(), 'mul')
        self.assertEqual(klOp.getParamCount(), 1)
        self.assertEqual(klOp.getParam(0).getType(), 'Integer')
        self.assertEqual(klOp.getParam(0).getName(), 'other')
        klOp = klAlias.getOperator(1)
        self.assertEqual(klOp.getName(), 'add')
        self.assertEqual(klOp.getParamCount(), 1)
        self.assertEqual(klOp.getParam(0).getType(), 'Boolean')
        self.assertEqual(klOp.getParam(0).getName(), 'b')
        klOp = klAlias.getOperator(2)
        self.assertEqual(klOp.getName(), 'mul')
        self.assertEqual(klOp.getParamCount(), 1)
        self.assertEqual(klOp.getParam(0).getType(), 'Scalar')
        self.assertEqual(klOp.getParam(0).getName(), 'k')

    def test_KLAliasOperators_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLAliasOperators, sys._getframe().f_code.co_name)
        self.__test_KLAliasOperators_Content(klNamespace)

    def test_KLAliasOperators_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLAliasOperators, sys._getframe().f_code.co_name)
        self.__test_KLAliasOperators_Content(klNamespace)

    def test_KLAliasOperators_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLAliasOperators, sys._getframe().f_code.co_name)
        self.__test_KLAliasOperators_Content(klNamespace)

    def test_KLAliasOperators_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLAliasOperators, sys._getframe().f_code.co_name)
        self.__test_KLAliasOperators_Content(klNamespace)

    #===================================================================================================================

    sourceCode_KLAliasFunc = '''
            alias UInt32 SomeIntAlias;
            SomeIntAlias SomeIntAlias.clamp(in SomeIntAlias min, in SomeIntAlias max) {
                return (this < min ? min : (this > max ? max : this));
            }
            '''

    def __test_KLAliasFunc_Content(self, klNamespace):
        self.assertEqual(klNamespace.getAliasCount(), 1)
        self.assertEqual(klNamespace.getAlias('SomeIntAlias').getName(), 'SomeIntAlias')
        self.assertEqual(klNamespace.getAlias('SomeIntAlias').getSourceName(), 'UInt32')
        self.assertEqual(klNamespace.getAlias('SomeIntAlias').getMethodCount(), 1)
        self.assertEqual(klNamespace.getAlias('SomeIntAlias').getMethod(0).getParamCount(), 2)
        self.assertEqual(klNamespace.getAlias('SomeIntAlias').getMethod(0).getReturnType(), 'SomeIntAlias')

    def test_KLAliasFunc_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLAliasFunc, sys._getframe().f_code.co_name)
        self.__test_KLAliasFunc_Content(klNamespace)

    def test_KLAliasFunc_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLAliasFunc, sys._getframe().f_code.co_name)
        self.__test_KLAliasFunc_Content(klNamespace)

    def test_KLAliasFunc_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLAliasFunc, sys._getframe().f_code.co_name)
        self.__test_KLAliasFunc_Content(klNamespace)

    def test_KLAliasFunc_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLAliasFunc, sys._getframe().f_code.co_name)
        self.__test_KLAliasFunc_Content(klNamespace)

    #===================================================================================================================
    sourceCode_KLInterface = '''
        interface Foo {
            Boolean doSomething(Scalar s, Integer i);
            doSomethingElse(String s);
            doNothing();
        };
        '''

    def __test_KLInterface_Content(self, klNamespace):
        self.assertEqual(klNamespace.getInterfaceCount(), 1)
        self.assertEqual(str(klNamespace.getInterfaceNames()), "[u'Foo']")
        klInterface = klNamespace.getInterface('Foo')
        self.assertEqual(klInterface.getMemberCount(), 3)
        self.assertEqual(klInterface.getMember(0).getName(), 'doSomething')
        self.assertEqual(klInterface.getMember(0).getReturnType(), 'Boolean')
        self.assertEqual(klInterface.getMember(0).getParamCount(), 2)
        self.assertEqual(klInterface.getMember(0).getParam(0).getName(), 's')
        self.assertEqual(klInterface.getMember(0).getParam(0).getType(), 'Scalar')
        self.assertEqual(klInterface.getMember(0).getParam(1).getName(), 'i')
        self.assertEqual(klInterface.getMember(0).getParam(1).getType(), 'Integer')
        self.assertEqual(klInterface.getMember(1).getName(), 'doSomethingElse')
        self.assertEqual(klInterface.getMember(1).getReturnType(), None)
        self.assertEqual(klInterface.getMember(1).getParamCount(), 1)
        self.assertEqual(klInterface.getMember(1).getParam(0).getName(), 's')
        self.assertEqual(klInterface.getMember(1).getParam(0).getType(), 'String')
        self.assertEqual(klInterface.getMember(2).getName(), 'doNothing')
        self.assertEqual(klInterface.getMember(2).getReturnType(), None)
        self.assertEqual(klInterface.getMember(2).getParamCount(), 0)

    def test_KLInterface_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLInterface, sys._getframe().f_code.co_name)
        self.__test_KLInterface_Content(klNamespace)

    def test_KLInterface_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLInterface, sys._getframe().f_code.co_name)
        self.__test_KLInterface_Content(klNamespace)

    def test_KLInterface_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLInterface, sys._getframe().f_code.co_name)
        self.__test_KLInterface_Content(klNamespace)

    def test_KLInterface_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.sourceCode_KLInterface, sys._getframe().f_code.co_name)
        self.__test_KLInterface_Content(klNamespace)

    #===================================================================================================================
    source_KLObject = '''
        object FooObject {};
        '''

    def __test_KLObject_Content(self, klNamespace):
        self.assertEqual(klNamespace.getObjectCount(), 1)
        self.assertEqual(klNamespace.getObjectNames(), [u'FooObject'])
        klObject = klNamespace.getObject('FooObject')
        self.assertEqual(klObject.getName(), 'FooObject')

    def test_KLObject_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObject, sys._getframe().f_code.co_name)
        self.__test_KLObject_Content(klNamespace)

    def test_KLObject_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObject, sys._getframe().f_code.co_name)
        self.__test_KLObject_Content(klNamespace)

    def test_KLObject_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObject, sys._getframe().f_code.co_name)
        self.__test_KLObject_Content(klNamespace)

    def test_KLObject_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObject, sys._getframe().f_code.co_name)
        self.__test_KLObject_Content(klNamespace)

    #===================================================================================================================

    source_KLStruct = '''
            struct FooStruct {};
            '''

    def __test_KLStruct_Content(self, klNamespace):
        self.assertEqual(klNamespace.getStructCount(), 1)
        self.assertEqual(str(klNamespace.getStructNames()), "[u'FooStruct']")
        klStruct = klNamespace.getStruct('FooStruct')
        self.assertEqual(klStruct.getName(), 'FooStruct')

    def test_KLStruct_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStruct, sys._getframe().f_code.co_name)
        self.__test_KLStruct_Content(klNamespace)

    def test_KLStruct_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStruct, sys._getframe().f_code.co_name)
        self.__test_KLStruct_Content(klNamespace)

    def test_KLStruct_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStruct, sys._getframe().f_code.co_name)
        self.__test_KLStruct_Content(klNamespace)

    def test_KLStruct_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStruct, sys._getframe().f_code.co_name)
        self.__test_KLStruct_Content(klNamespace)

    #===================================================================================================================
    source_KLGlobalFunctions = '''
        function Hello(String s) {}
        function Boolean You() { return true; }
        '''

    def __test_KLGlobalFunctions_Content(self, klNamespace):
        self.assertEqual(klNamespace.getObjectCount(), 0)
        self.assertEqual(klNamespace.getObjectNames(), [])
        self.assertEqual(klNamespace.getFunctionCount(), 2)
        self.assertEqual(klNamespace.hasFunction('Hello'), True)
        self.assertEqual(klNamespace.getFunction('Hello').getName(), 'Hello')
        self.assertEqual(klNamespace.getFunction('Hello').getReturnType(), None)
        self.assertEqual(klNamespace.getFunction('Hello').getParamCount(), 1)
        self.assertEqual(klNamespace.getFunction('Hello').getParam(0).getName(), 's')
        self.assertEqual(klNamespace.getFunction('Hello').getParam(0).getType(), 'String')
        self.assertEqual(klNamespace.hasFunction('You'), True)
        self.assertEqual(klNamespace.getFunction('You').getName(), 'You')
        self.assertEqual(klNamespace.getFunction('You').getReturnType(), 'Boolean')
        self.assertEqual(klNamespace.getFunction('You').getParamCount(), 0)

    def test_KLGlobalFunctions_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLGlobalFunctions, sys._getframe().f_code.co_name)
        self.__test_KLGlobalFunctions_Content(klNamespace)

    def test_KLGlobalFunctions_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLGlobalFunctions, sys._getframe().f_code.co_name)
        self.__test_KLGlobalFunctions_Content(klNamespace)

    def test_KLGlobalFunctions_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLGlobalFunctions, sys._getframe().f_code.co_name)
        self.__test_KLGlobalFunctions_Content(klNamespace)

    def test_KLGlobalFunctions_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLGlobalFunctions, sys._getframe().f_code.co_name)
        self.__test_KLGlobalFunctions_Content(klNamespace)

    #===================================================================================================================
    # def test_KLObjectManyNamespaces(self):
    #     sourceCode = '''
    #         namespace NS { object Foo {}; }
    #         namespace NS2 { object Bar {}; }
    #         object Outside {};
    #         '''
    #     self.klEnv.parseSourceCode(sourceCode)
    #     self.assertEqual(self.klEnv.getGlobalNamespace().getObjectCount(), 1)
    #     self.assertEqual(self.klEnv.getNamespaceCount(), 2)
    #     self.assertEqual(str(self.klEnv.getNamespaceNames()), "[u'NS2', u'NS']")
    #     klNamespace = self.klEnv.getNamespace('NS')
    #     self.assertEqual(klNamespace.getName(), 'NS')
    #     self.assertEqual(klNamespace.getObjectCount(), 1)
    #     self.assertEqual(klNamespace.hasObject('Foo'), True)
    #     klNamespace = self.klEnv.getNamespace('NS2')
    #     self.assertEqual(klNamespace.getName(), 'NS2')
    #     self.assertEqual(klNamespace.getObjectCount(), 1)
    #     self.assertEqual(klNamespace.hasObject('Bar'), True)

    #===================================================================================================================
    # def test_KLStructManyNamespaces(self):
    #     sourceCode = '''
    #         namespace NS { struct Foo {}; }
    #         namespace NS2 { struct Bar {}; }
    #         struct Outside {};
    #         '''
    #     self.klEnv.parseSourceCode(sourceCode)
    #     self.assertEqual(self.klEnv.getGlobalNamespace().getStructCount(), 1)
    #     self.assertEqual(self.klEnv.getNamespaceCount(), 2)
    #     self.assertEqual(str(self.klEnv.getNamespaceNames()), "[u'NS2', u'NS']")
    #     klNamespace = self.klEnv.getNamespace('NS')
    #     self.assertEqual(klNamespace.getName(), 'NS')
    #     self.assertEqual(klNamespace.getStructCount(), 1)
    #     self.assertEqual(klNamespace.hasStruct('Foo'), True)
    #     klNamespace = self.klEnv.getNamespace('NS2')
    #     self.assertEqual(klNamespace.getName(), 'NS2')
    #     self.assertEqual(klNamespace.getStructCount(), 1)
    #     self.assertEqual(klNamespace.hasStruct('Bar'), True)

    #===================================================================================================================
    source_KLObjectMembers = '''
        object KLObjectMembersFooObject
        {
            public String name;
            protected Boolean enabled;
            private Integer value;
            Scalar offset;
        };
        '''

    def __test_KLObjectMembers_Content(self, klNamespace):
        self.assertEqual(klNamespace.getObjectCount(), 1)
        klObject = klNamespace.getObject('KLObjectMembersFooObject')
        self.assertEqual(klObject.getName(), 'KLObjectMembersFooObject')
        self.assertEqual(klObject.getMemberCount(), 4)
        self.assertEqual(klObject.getMember(0).getAccess(), 'public')
        self.assertEqual(klObject.getMember(0).getType(), 'String')
        self.assertEqual(klObject.getMember(0).getName(), 'name')
        self.assertEqual(klObject.getMember(1).getAccess(), 'protected')
        self.assertEqual(klObject.getMember(1).getType(), 'Boolean')
        self.assertEqual(klObject.getMember(1).getName(), 'enabled')
        self.assertEqual(klObject.getMember(2).getAccess(), 'private')
        self.assertEqual(klObject.getMember(2).getType(), 'Integer')
        self.assertEqual(klObject.getMember(2).getName(), 'value')
        self.assertEqual(klObject.getMember(3).getAccess(), 'unspecified')
        self.assertEqual(klObject.getMember(3).getType(), 'Scalar')
        self.assertEqual(klObject.getMember(3).getName(), 'offset')

    def test_KLObjectMembers_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectMembers, sys._getframe().f_code.co_name)
        self.__test_KLObjectMembers_Content(klNamespace)

    def test_KLObjectMembers_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectMembers, sys._getframe().f_code.co_name)
        self.__test_KLObjectMembers_Content(klNamespace)

    def test_KLObjectMembers_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectMembers, sys._getframe().f_code.co_name)
        self.__test_KLObjectMembers_Content(klNamespace)

    def test_KLObjectMembers_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectMembers, sys._getframe().f_code.co_name)
        self.__test_KLObjectMembers_Content(klNamespace)

    #===================================================================================================================

    source_KLStructMembers = '''
        struct KLStructMembersFooStruct
        {
            public String name;
            protected Boolean enabled;
            private Integer value;
            Scalar offset;
        };
        '''

    def __test_KLStructMembers_Content(self, klNamespace):
        self.assertEqual(klNamespace.getStructCount(), 1)
        klStruct = klNamespace.getStruct('KLStructMembersFooStruct')
        self.assertEqual(klStruct.getName(), 'KLStructMembersFooStruct')
        self.assertEqual(klStruct.getMemberCount(), 4)
        self.assertEqual(klStruct.getMember(0).getAccess(), 'public')
        self.assertEqual(klStruct.getMember(0).getType(), 'String')
        self.assertEqual(klStruct.getMember(0).getName(), 'name')
        self.assertEqual(klStruct.getMember(1).getAccess(), 'protected')
        self.assertEqual(klStruct.getMember(1).getType(), 'Boolean')
        self.assertEqual(klStruct.getMember(1).getName(), 'enabled')
        self.assertEqual(klStruct.getMember(2).getAccess(), 'private')
        self.assertEqual(klStruct.getMember(2).getType(), 'Integer')
        self.assertEqual(klStruct.getMember(2).getName(), 'value')
        self.assertEqual(klStruct.getMember(3).getAccess(), 'unspecified')
        self.assertEqual(klStruct.getMember(3).getType(), 'Scalar')
        self.assertEqual(klStruct.getMember(3).getName(), 'offset')

    def test_KLStructMembers_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructMembers, sys._getframe().f_code.co_name)
        self.__test_KLStructMembers_Content(klNamespace)

    def test_KLStructMembers_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructMembers, sys._getframe().f_code.co_name)
        self.__test_KLStructMembers_Content(klNamespace)

    def test_KLStructMembers_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructMembers, sys._getframe().f_code.co_name)
        self.__test_KLStructMembers_Content(klNamespace)

    def test_KLStructMembers_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructMembers, sys._getframe().f_code.co_name)
        self.__test_KLStructMembers_Content(klNamespace)

    #===================================================================================================================
    source_KLObjectConstructors = '''
        object KLObjectConstructorsFooObject
        {
            private String name;
            private Boolean state;
        };
        KLObjectConstructorsFooObject(String name) { this.name = name; }
        KLObjectConstructorsFooObject(String name, Boolean state) { this.name = name; this.state = state; }
        '''

    def __test_KLObjectConstructors_Setup(self, klNamespace):
        self.assertEqual(klNamespace.getObjectCount(), 1)
        klObject = klNamespace.getObject('KLObjectConstructorsFooObject')
        self.assertEqual(klObject.getName(), 'KLObjectConstructorsFooObject')
        self.assertEqual(klObject.getConstructorCount(), 2)
        klConstructor = klObject.getConstructor(0)
        self.assertEqual(klConstructor.getParamCount(), 1)
        self.assertEqual(klConstructor.getParam(0).getName(), 'name')
        self.assertEqual(klConstructor.getParam(0).getType(), 'String')
        klConstructor = klObject.getConstructor(1)
        self.assertEqual(klConstructor.getParamCount(), 2)
        self.assertEqual(klConstructor.getParam(0).getName(), 'name')
        self.assertEqual(klConstructor.getParam(0).getType(), 'String')
        self.assertEqual(klConstructor.getParam(1).getName(), 'state')
        self.assertEqual(klConstructor.getParam(1).getType(), 'Boolean')

    def test_KLObjectConstructors_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectConstructors, sys._getframe().f_code.co_name)
        self.__test_KLObjectConstructors_Setup(klNamespace)

    def test_KLObjectConstructors_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectConstructors, sys._getframe().f_code.co_name)
        self.__test_KLObjectConstructors_Setup(klNamespace)

    def test_KLObjectConstructors_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectConstructors, sys._getframe().f_code.co_name)
        self.__test_KLObjectConstructors_Setup(klNamespace)

    def test_KLObjectConstructors_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectConstructors, sys._getframe().f_code.co_name)
        self.__test_KLObjectConstructors_Setup(klNamespace)

    #===================================================================================================================
    source_KLObjectDestructor = '''
        object KLObjectDestructorFooObject
        {
            private String name;
            private Boolean state;
        };
        KLObjectDestructorFooObject(String name) { this.name = name; }
        ~KLObjectDestructorFooObject() {}
        '''

    def __test_KLObjectDestructor_Content(self, klNamespace):
        self.assertEqual(klNamespace.getObjectCount(), 1)
        klObject = klNamespace.getObject('KLObjectDestructorFooObject')
        self.assertEqual(klObject.getName(), 'KLObjectDestructorFooObject')
        self.assertEqual(klObject.getConstructorCount(), 1)
        self.assertEqual(klObject.getHasDestructor(), True)

    def test_KLObjectDestructor_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectDestructor, sys._getframe().f_code.co_name)
        self.__test_KLObjectDestructor_Content(klNamespace)

    def test_KLObjectDestructor_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectDestructor, sys._getframe().f_code.co_name)
        self.__test_KLObjectDestructor_Content(klNamespace)

    def test_KLObjectDestructor_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectDestructor, sys._getframe().f_code.co_name)
        self.__test_KLObjectDestructor_Content(klNamespace)

    def test_KLObjectDestructor_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectDestructor, sys._getframe().f_code.co_name)
        self.__test_KLObjectDestructor_Content(klNamespace)

    #===================================================================================================================
    source_KLObjectForwardDeclaredConstructors = '''
        KLObjectForwardDeclaredConstructorsFooObject(String name) { this.name = name; }
        KLObjectForwardDeclaredConstructorsFooObject(String name, Boolean state) { this.name = name; this.state = state; }
        object KLObjectForwardDeclaredConstructorsFooObject
        {
            private String name;
            private Boolean state;
        };
        '''

    def __test_KLObjectForwardDeclaredConstructors_Content(self, klNamespace):
        self.assertEqual(klNamespace.getObjectCount(), 1)
        klObject = klNamespace.getObject('KLObjectForwardDeclaredConstructorsFooObject')
        self.assertEqual(klObject.getName(), 'KLObjectForwardDeclaredConstructorsFooObject')
        self.assertEqual(klObject.getConstructorCount(), 2)
        klConstructor = klObject.getConstructor(0)
        self.assertEqual(klConstructor.getParamCount(), 1)
        self.assertEqual(klConstructor.getParam(0).getName(), 'name')
        self.assertEqual(klConstructor.getParam(0).getType(), 'String')
        klConstructor = klObject.getConstructor(1)
        self.assertEqual(klConstructor.getParamCount(), 2)
        self.assertEqual(klConstructor.getParam(0).getName(), 'name')
        self.assertEqual(klConstructor.getParam(0).getType(), 'String')
        self.assertEqual(klConstructor.getParam(1).getName(), 'state')
        self.assertEqual(klConstructor.getParam(1).getType(), 'Boolean')

    def test_KLObjectForwardDeclaredConstructors_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectForwardDeclaredConstructors, sys._getframe().f_code.co_name)
        self.__test_KLObjectForwardDeclaredConstructors_Content(klNamespace)

    def test_KLObjectForwardDeclaredConstructors_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectForwardDeclaredConstructors, sys._getframe().f_code.co_name)
        self.__test_KLObjectForwardDeclaredConstructors_Content(klNamespace)

    def test_KLObjectForwardDeclaredConstructors_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectForwardDeclaredConstructors, sys._getframe().f_code.co_name)
        self.__test_KLObjectForwardDeclaredConstructors_Content(klNamespace)

    def test_KLObjectForwardDeclaredConstructors_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectForwardDeclaredConstructors, sys._getframe().f_code.co_name)
        self.__test_KLObjectForwardDeclaredConstructors_Content(klNamespace)

    #===================================================================================================================
    source_KLStructConstructors = '''
        struct KLStructConstructorsFooStruct
        {
            private String name;
            private Boolean state;
        };
        KLStructConstructorsFooStruct(String name) { this.name = name; }
        KLStructConstructorsFooStruct(String name, Boolean state) { this.name = name; this.state = state; }
        '''

    def __test_KLStructConstructors_Content(self, klNamespace):
        self.assertEqual(klNamespace.getStructCount(), 1)
        klStruct = klNamespace.getStruct('KLStructConstructorsFooStruct')
        self.assertEqual(klStruct.getName(), 'KLStructConstructorsFooStruct')
        self.assertEqual(klStruct.getConstructorCount(), 2)
        klConstructor = klStruct.getConstructor(0)
        self.assertEqual(klConstructor.getParamCount(), 1)
        self.assertEqual(klConstructor.getParam(0).getName(), 'name')
        self.assertEqual(klConstructor.getParam(0).getType(), 'String')
        klConstructor = klStruct.getConstructor(1)
        self.assertEqual(klConstructor.getParamCount(), 2)
        self.assertEqual(klConstructor.getParam(0).getName(), 'name')
        self.assertEqual(klConstructor.getParam(0).getType(), 'String')
        self.assertEqual(klConstructor.getParam(1).getName(), 'state')
        self.assertEqual(klConstructor.getParam(1).getType(), 'Boolean')

    def test_KLStructConstructors_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructConstructors, sys._getframe().f_code.co_name)
        self.__test_KLStructConstructors_Content(klNamespace)

    def test_KLStructConstructors_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructConstructors, sys._getframe().f_code.co_name)
        self.__test_KLStructConstructors_Content(klNamespace)

    def test_KLStructConstructors_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructConstructors, sys._getframe().f_code.co_name)
        self.__test_KLStructConstructors_Content(klNamespace)

    def test_KLStructConstructors_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructConstructors, sys._getframe().f_code.co_name)
        self.__test_KLStructConstructors_Content(klNamespace)

    #===================================================================================================================
    source_KLStructForwardDeclaredConstructors = '''
        KLStructForwardDeclaredConstructorsFooStruct(String name) { this.name = name; }
        KLStructForwardDeclaredConstructorsFooStruct(String name, Boolean state) { this.name = name; this.state = state; }
        struct KLStructForwardDeclaredConstructorsFooStruct
        {
            private String name;
            private Boolean state;
        };
        '''

    def __test_KLStructForwardDeclaredConstructors_Content(self, klNamespace):
        self.assertEqual(klNamespace.getStructCount(), 1)
        klStruct = klNamespace.getStruct('KLStructForwardDeclaredConstructorsFooStruct')
        self.assertEqual(klStruct.getName(), 'KLStructForwardDeclaredConstructorsFooStruct')
        self.assertEqual(klStruct.getConstructorCount(), 2)
        klConstructor = klStruct.getConstructor(0)
        self.assertEqual(klConstructor.getParamCount(), 1)
        self.assertEqual(klConstructor.getParam(0).getName(), 'name')
        self.assertEqual(klConstructor.getParam(0).getType(), 'String')
        klConstructor = klStruct.getConstructor(1)
        self.assertEqual(klConstructor.getParamCount(), 2)
        self.assertEqual(klConstructor.getParam(0).getName(), 'name')
        self.assertEqual(klConstructor.getParam(0).getType(), 'String')
        self.assertEqual(klConstructor.getParam(1).getName(), 'state')
        self.assertEqual(klConstructor.getParam(1).getType(), 'Boolean')

    def test_KLStructForwardDeclaredConstructors_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructForwardDeclaredConstructors, sys._getframe().f_code.co_name)
        self.__test_KLStructForwardDeclaredConstructors_Content(klNamespace)

    def test_KLStructForwardDeclaredConstructors_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructForwardDeclaredConstructors, sys._getframe().f_code.co_name)
        self.__test_KLStructForwardDeclaredConstructors_Content(klNamespace)

    def test_KLStructForwardDeclaredConstructors_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructForwardDeclaredConstructors, sys._getframe().f_code.co_name)
        self.__test_KLStructForwardDeclaredConstructors_Content(klNamespace)

    def test_KLStructForwardDeclaredConstructors_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructForwardDeclaredConstructors, sys._getframe().f_code.co_name)
        self.__test_KLStructForwardDeclaredConstructors_Content(klNamespace)

    #===================================================================================================================
    source_KLStructDestructor = '''
        struct KLStructDestructorFooStruct
        {
            private String name;
            private Boolean state;
        };
        KLStructDestructorFooStruct(String name) { this.name = name; }
        ~KLStructDestructorFooStruct() {}
        '''

    def __test_KLStructDestructor_Content(self, klNamespace):
        self.assertEqual(klNamespace.getStructCount(), 1)
        klStruct = klNamespace.getStruct('KLStructDestructorFooStruct')
        self.assertEqual(klStruct.getName(), 'KLStructDestructorFooStruct')
        self.assertEqual(klStruct.getConstructorCount(), 1)
        self.assertEqual(klStruct.getHasDestructor(), True)

    def test_KLStructDestructor_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructDestructor, sys._getframe().f_code.co_name)
        self.__test_KLStructDestructor_Content(klNamespace)

    def test_KLStructDestructor_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructDestructor, sys._getframe().f_code.co_name)
        self.__test_KLStructDestructor_Content(klNamespace)

    def test_KLStructDestructor_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructDestructor, sys._getframe().f_code.co_name)
        self.__test_KLStructDestructor_Content(klNamespace)

    def test_KLStructDestructor_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructDestructor, sys._getframe().f_code.co_name)
        self.__test_KLStructDestructor_Content(klNamespace)

    #===================================================================================================================
    source_KLObjectConstructors_ObjectForwardDeclared = '''
        object KLObjectConstructors_ObjectForwardDeclaredFooObject;
        KLObjectConstructors_ObjectForwardDeclaredFooObject(String name) { this.name = name; }
        object KLObjectConstructors_ObjectForwardDeclaredFooObject
        {
            private String name;
            private Boolean state;
        };
        KLObjectConstructors_ObjectForwardDeclaredFooObject(String name, Boolean state) { this.name = name; this.state = state; }
        '''

    def __test_KLObjectConstructors_ObjectForwardDeclared_Content(self, klNamespace):
        self.assertEqual(klNamespace.getObjectCount(), 1)
        klObject = klNamespace.getObject('KLObjectConstructors_ObjectForwardDeclaredFooObject')
        self.assertEqual(klObject.getName(), 'KLObjectConstructors_ObjectForwardDeclaredFooObject')
        self.assertEqual(klObject.getConstructorCount(), 2)

    def test_KLObjectConstructors_ObjectForwardDeclared_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectConstructors_ObjectForwardDeclared, sys._getframe().f_code.co_name)
        self.__test_KLObjectConstructors_ObjectForwardDeclared_Content(klNamespace)

    def test_KLObjectConstructors_ObjectForwardDeclared_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectConstructors_ObjectForwardDeclared, sys._getframe().f_code.co_name)
        self.__test_KLObjectConstructors_ObjectForwardDeclared_Content(klNamespace)

    def test_KLObjectConstructors_ObjectForwardDeclared_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectConstructors_ObjectForwardDeclared, sys._getframe().f_code.co_name)
        self.__test_KLObjectConstructors_ObjectForwardDeclared_Content(klNamespace)

    def test_KLObjectConstructors_ObjectForwardDeclared_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectConstructors_ObjectForwardDeclared, sys._getframe().f_code.co_name)
        self.__test_KLObjectConstructors_ObjectForwardDeclared_Content(klNamespace)

    #===================================================================================================================
    source_KLStructConstructors_StructForwardDeclared = '''
        struct KLStructConstructors_StructForwardDeclaredFooStruct;
        KLStructConstructors_StructForwardDeclaredFooStruct(String name) { this.name = name; }
        struct KLStructConstructors_StructForwardDeclaredFooStruct
        {
            private String name;
            private Boolean state;
        };
        KLStructConstructors_StructForwardDeclaredFooStruct(String name, Boolean state) { this.name = name; this.state = state; }
        '''

    def __test_KLStructConstructors_StructForwardDeclared_Content(self, klNamespace):
        self.assertEqual(klNamespace.getStructCount(), 1)
        klStruct = klNamespace.getStruct('KLStructConstructors_StructForwardDeclaredFooStruct')
        self.assertEqual(klStruct.getName(), 'KLStructConstructors_StructForwardDeclaredFooStruct')
        self.assertEqual(klStruct.getConstructorCount(), 2)

    def test_KLStructConstructors_StructForwardDeclared_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructConstructors_StructForwardDeclared, sys._getframe().f_code.co_name)
        self.__test_KLStructConstructors_StructForwardDeclared_Content(klNamespace)

    def test_KLStructConstructors_StructForwardDeclared_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructConstructors_StructForwardDeclared, sys._getframe().f_code.co_name)
        self.__test_KLStructConstructors_StructForwardDeclared_Content(klNamespace)

    def test_KLStructConstructors_StructForwardDeclared_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructConstructors_StructForwardDeclared, sys._getframe().f_code.co_name)
        self.__test_KLStructConstructors_StructForwardDeclared_Content(klNamespace)

    def test_KLStructConstructors_StructForwardDeclared_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructConstructors_StructForwardDeclared, sys._getframe().f_code.co_name)
        self.__test_KLStructConstructors_StructForwardDeclared_Content(klNamespace)

    #===================================================================================================================
    source_KLObjectGettersAndSetters = '''
        object KLObjectGettersAndSettersFooObject
        {
            private String name;
            private Boolean state;
        };
        KLObjectGettersAndSettersFooObject(String name) { this.setName(name); }
        public String KLObjectGettersAndSettersFooObject.getName() { return this.name; }
        protected KLObjectGettersAndSettersFooObject.setName!(String name) { this.name = name; }
        private Boolean KLObjectGettersAndSettersFooObject.getState() { return this.state; }
        KLObjectGettersAndSettersFooObject.setState!(Boolean state) { this.state = state; }
        KLObjectGettersAndSettersFooObject.setup() {}
        KLObjectGettersAndSettersFooObject.doSomething() {}
        '''

    def __test_KLObjectGettersAndSetters_Content(self, klNamespace):
        self.assertEqual(klNamespace.getObjectCount(), 1)
        klObject = klNamespace.getObject('KLObjectGettersAndSettersFooObject')
        self.assertEqual(klObject.getName(), 'KLObjectGettersAndSettersFooObject')
        self.assertEqual(klObject.getGetterCount(), 2)
        self.assertEqual(klObject.getGetter(0).getName(), 'getName')
        self.assertEqual(klObject.getGetter(0).getReturnType(), 'String')
        self.assertEqual(klObject.getGetter(0).getAccess(), 'public')
        self.assertEqual(klObject.getGetter(1).getName(), 'getState')
        self.assertEqual(klObject.getGetter(1).getReturnType(), 'Boolean')
        self.assertEqual(klObject.getGetter(1).getAccess(), 'private')
        self.assertEqual(klObject.getSetterCount(), 2)
        self.assertEqual(klObject.getSetter(0).getName(), 'setName')
        self.assertEqual(klObject.getSetter(0).getParamCount(), 1)
        self.assertEqual(klObject.getSetter(0).getParam(0).getName(), 'name')
        self.assertEqual(klObject.getSetter(0).getParam(0).getType(), 'String')
        self.assertEqual(klObject.getSetter(0).getAccess(), 'protected')
        self.assertEqual(klObject.getSetter(1).getName(), 'setState')
        self.assertEqual(klObject.getSetter(1).getParamCount(), 1)
        self.assertEqual(klObject.getSetter(1).getParam(0).getName(), 'state')
        self.assertEqual(klObject.getSetter(1).getParam(0).getType(), 'Boolean')
        self.assertEqual(klObject.getSetter(1).getAccess(), 'unspecified')

    def test_KLObjectGettersAndSetters_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectGettersAndSetters, sys._getframe().f_code.co_name)
        self.__test_KLObjectGettersAndSetters_Content(klNamespace)

    def test_KLObjectGettersAndSetters_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectGettersAndSetters, sys._getframe().f_code.co_name)
        self.__test_KLObjectGettersAndSetters_Content(klNamespace)

    def test_KLObjectGettersAndSetters_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectGettersAndSetters, sys._getframe().f_code.co_name)
        self.__test_KLObjectGettersAndSetters_Content(klNamespace)

    def test_KLObjectGettersAndSetters_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectGettersAndSetters, sys._getframe().f_code.co_name)
        self.__test_KLObjectGettersAndSetters_Content(klNamespace)

    #===================================================================================================================
    source_KLStructGettersAndSetters = '''
        struct KLStructGettersAndSettersFooStruct
        {
            private String name;
            private Boolean state;
        };
        KLStructGettersAndSettersFooStruct(String name) { this.setName(name); }
        public String KLStructGettersAndSettersFooStruct.getName() { return this.name; }
        protected KLStructGettersAndSettersFooStruct.setName!(String name) { this.name = name; }
        private Boolean KLStructGettersAndSettersFooStruct.getState() { return this.state; }
        KLStructGettersAndSettersFooStruct.setState!(Boolean state) { this.state = state; }
        KLStructGettersAndSettersFooStruct.setup() {}
        KLStructGettersAndSettersFooStruct.doSomething() {}
        '''

    def __test_KLStructGettersAndSetters_Content(self, klNamespace):
        self.assertEqual(klNamespace.getStructCount(), 1)
        klStruct = klNamespace.getStruct('KLStructGettersAndSettersFooStruct')
        self.assertEqual(klStruct.getName(), 'KLStructGettersAndSettersFooStruct')
        self.assertEqual(klStruct.getGetterCount(), 2)
        self.assertEqual(klStruct.getGetter(0).getName(), 'getName')
        self.assertEqual(klStruct.getGetter(0).getReturnType(), 'String')
        self.assertEqual(klStruct.getGetter(0).getAccess(), 'public')
        self.assertEqual(klStruct.getGetter(1).getName(), 'getState')
        self.assertEqual(klStruct.getGetter(1).getReturnType(), 'Boolean')
        self.assertEqual(klStruct.getGetter(1).getAccess(), 'private')
        self.assertEqual(klStruct.getSetterCount(), 2)
        self.assertEqual(klStruct.getSetter(0).getName(), 'setName')
        self.assertEqual(klStruct.getSetter(0).getParamCount(), 1)
        self.assertEqual(klStruct.getSetter(0).getParam(0).getName(), 'name')
        self.assertEqual(klStruct.getSetter(0).getParam(0).getType(), 'String')
        self.assertEqual(klStruct.getSetter(0).getAccess(), 'protected')
        self.assertEqual(klStruct.getSetter(1).getName(), 'setState')
        self.assertEqual(klStruct.getSetter(1).getParamCount(), 1)
        self.assertEqual(klStruct.getSetter(1).getParam(0).getName(), 'state')
        self.assertEqual(klStruct.getSetter(1).getParam(0).getType(), 'Boolean')
        self.assertEqual(klStruct.getSetter(1).getAccess(), 'unspecified')

    def test_KLStructGettersAndSetters_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructGettersAndSetters, sys._getframe().f_code.co_name)
        self.__test_KLStructGettersAndSetters_Content(klNamespace)

    def test_KLStructGettersAndSetters_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructGettersAndSetters, sys._getframe().f_code.co_name)
        self.__test_KLStructGettersAndSetters_Content(klNamespace)

    def test_KLStructGettersAndSetters_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructGettersAndSetters, sys._getframe().f_code.co_name)
        self.__test_KLStructGettersAndSetters_Content(klNamespace)

    def test_KLStructGettersAndSetters_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructGettersAndSetters, sys._getframe().f_code.co_name)
        self.__test_KLStructGettersAndSetters_Content(klNamespace)

    #===================================================================================================================
    source_KLObjectMethods = '''
        object KLObjectMethodsFooObject
        {
            private String name;
            private Boolean state;
        };
        KLObjectMethodsFooObject(String name) { this.setName(name); }
        public String KLObjectMethodsFooObject.getName() { return this.name; }
        protected KLObjectMethodsFooObject.setName!(String name) { this.name = name; }
        private Boolean KLObjectMethodsFooObject.getState() { return this.state; }
        KLObjectMethodsFooObject.setState!(Boolean state) { this.state = state; }
        KLObjectMethodsFooObject.setup(Boolean b) {}
        String KLObjectMethodsFooObject.doSomething() { return String(""); }
        '''

    def __test_KLObjectMethods_Content(self, klNamespace):
        self.assertEqual(klNamespace.getObjectCount(), 1)
        klObject = klNamespace.getObject('KLObjectMethodsFooObject')
        self.assertEqual(klObject.getName(), 'KLObjectMethodsFooObject')
        self.assertEqual(klObject.getMethodCount(), 2)
        self.assertEqual(klObject.getMethod(0).getName(), 'setup')
        self.assertEqual(klObject.getMethod(0).getReturnType(), None)
        self.assertEqual(klObject.getMethod(0).getParamCount(), 1)
        self.assertEqual(klObject.getMethod(0).getParam(0).getName(), 'b')
        self.assertEqual(klObject.getMethod(0).getParam(0).getType(), 'Boolean')
        self.assertEqual(klObject.getMethod(1).getName(), 'doSomething')
        self.assertEqual(klObject.getMethod(1).getParamCount(), 0)
        self.assertEqual(klObject.getMethod(1).getReturnType(), 'String')

    def test_KLObjectMethods_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectMethods, sys._getframe().f_code.co_name)
        self.__test_KLObjectMethods_Content(klNamespace)

    def test_KLObjectMethods_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectMethods, sys._getframe().f_code.co_name)
        self.__test_KLObjectMethods_Content(klNamespace)

    def test_KLObjectMethods_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectMethods, sys._getframe().f_code.co_name)
        self.__test_KLObjectMethods_Content(klNamespace)

    def test_KLObjectMethods_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectMethods, sys._getframe().f_code.co_name)
        self.__test_KLObjectMethods_Content(klNamespace)

    #===================================================================================================================
    source_KLObjectOperators = '''
        object KLObjectOperatorsFooObject
        {
            private Integer value;
        };
        KLObjectOperatorsFooObject(Integer value) { this.value = value; }
        KLObjectOperatorsFooObject. *= (Integer other) {
          this.value = this.value * other;
        }
        KLObjectOperatorsFooObject. += (Boolean b) {
          this.value += b ? 1 : 0;
        }
        KLObjectOperatorsFooObject. *= (Scalar k) {
          this.value = this.value * k;
        }
        '''

    def __test_KLObjectOperators_Content(self, klNamespace):
        self.assertEqual(klNamespace.getObjectCount(), 1)
        klObject = klNamespace.getObject('KLObjectOperatorsFooObject')
        self.assertEqual(klObject.getOperatorCount(), 3)
        klOp = klObject.getOperator(0)
        self.assertEqual(klOp.getName(), 'mul')
        self.assertEqual(klOp.getParamCount(), 1)
        self.assertEqual(klOp.getParam(0).getType(), 'Integer')
        self.assertEqual(klOp.getParam(0).getName(), 'other')
        klOp = klObject.getOperator(1)
        self.assertEqual(klOp.getName(), 'add')
        self.assertEqual(klOp.getParamCount(), 1)
        self.assertEqual(klOp.getParam(0).getType(), 'Boolean')
        self.assertEqual(klOp.getParam(0).getName(), 'b')
        klOp = klObject.getOperator(2)
        self.assertEqual(klOp.getName(), 'mul')
        self.assertEqual(klOp.getParamCount(), 1)
        self.assertEqual(klOp.getParam(0).getType(), 'Scalar')
        self.assertEqual(klOp.getParam(0).getName(), 'k')

    def test_KLObjectOperators_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectOperators, sys._getframe().f_code.co_name)
        self.__test_KLObjectOperators_Content(klNamespace)

    def test_KLObjectOperators_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectOperators, sys._getframe().f_code.co_name)
        self.__test_KLObjectOperators_Content(klNamespace)

    def test_KLObjectOperators_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectOperators, sys._getframe().f_code.co_name)
        self.__test_KLObjectOperators_Content(klNamespace)

    def test_KLObjectOperators_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLObjectOperators, sys._getframe().f_code.co_name)
        self.__test_KLObjectOperators_Content(klNamespace)

    #===================================================================================================================
    source_KLStructMethods = '''
        struct KLStructMethodsFooStruct
        {
            private String name;
            private Boolean state;
        };
        KLStructMethodsFooStruct(String name) { this.setName(name); }
        public String KLStructMethodsFooStruct.getName() { return this.name; }
        protected KLStructMethodsFooStruct.setName!(String name) { this.name = name; }
        private Boolean KLStructMethodsFooStruct.getState() { return this.state; }
        KLStructMethodsFooStruct.setState!(Boolean state) { this.state = state; }
        KLStructMethodsFooStruct.setup(Boolean b) {}
        String KLStructMethodsFooStruct.doSomething() { return ""; }
        '''

    def __test_KLStructMethods_Content(self, klNamespace):
        self.assertEqual(klNamespace.getStructCount(), 1)
        klStruct = klNamespace.getStruct('KLStructMethodsFooStruct')
        self.assertEqual(klStruct.getName(), 'KLStructMethodsFooStruct')
        self.assertEqual(klStruct.getMethodCount(), 2)
        self.assertEqual(klStruct.getMethod(0).getName(), 'setup')
        self.assertEqual(klStruct.getMethod(0).getReturnType(), None)
        self.assertEqual(klStruct.getMethod(0).getParamCount(), 1)
        self.assertEqual(klStruct.getMethod(0).getParam(0).getName(), 'b')
        self.assertEqual(klStruct.getMethod(0).getParam(0).getType(), 'Boolean')
        self.assertEqual(klStruct.getMethod(1).getName(), 'doSomething')
        self.assertEqual(klStruct.getMethod(1).getParamCount(), 0)
        self.assertEqual(klStruct.getMethod(1).getReturnType(), 'String')

    def test_KLStructMethods_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructMethods, sys._getframe().f_code.co_name)
        self.__test_KLStructMethods_Content(klNamespace)

    def test_KLStructMethods_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructMethods, sys._getframe().f_code.co_name)
        self.__test_KLStructMethods_Content(klNamespace)

    def test_KLStructMethods_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructMethods, sys._getframe().f_code.co_name)
        self.__test_KLStructMethods_Content(klNamespace)

    def test_KLStructMethods_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructMethods, sys._getframe().f_code.co_name)
        self.__test_KLStructMethods_Content(klNamespace)

    #===================================================================================================================
    source_KLStructOperators = '''
        struct KLStructOperatorsFooStruct
        {
            private Integer value;
        };
        KLStructOperatorsFooStruct(Integer value) { this.value = value; }
        KLStructOperatorsFooStruct. *= (Integer other) {
          this.value = this.value * other;
        }
        KLStructOperatorsFooStruct. += (Boolean b) {
          this.value += b ? 1 : 0;
        }
        KLStructOperatorsFooStruct. *= (Scalar k) {
          this.value = this.value * k;
        }
        '''

    def __test_KLStructOperators_Content(self, klNamespace):
        self.assertEqual(klNamespace.getStructCount(), 1)
        klStruct = klNamespace.getStruct('KLStructOperatorsFooStruct')
        self.assertEqual(klStruct.getOperatorCount(), 3)
        klOp = klStruct.getOperator(0)
        self.assertEqual(klOp.getName(), 'mul')
        self.assertEqual(klOp.getParamCount(), 1)
        self.assertEqual(klOp.getParam(0).getType(), 'Integer')
        self.assertEqual(klOp.getParam(0).getName(), 'other')
        klOp = klStruct.getOperator(1)
        self.assertEqual(klOp.getName(), 'add')
        self.assertEqual(klOp.getParamCount(), 1)
        self.assertEqual(klOp.getParam(0).getType(), 'Boolean')
        self.assertEqual(klOp.getParam(0).getName(), 'b')
        klOp = klStruct.getOperator(2)
        self.assertEqual(klOp.getName(), 'mul')
        self.assertEqual(klOp.getParamCount(), 1)
        self.assertEqual(klOp.getParam(0).getType(), 'Scalar')
        self.assertEqual(klOp.getParam(0).getName(), 'k')

    def test_KLStructOperators_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructOperators, sys._getframe().f_code.co_name)
        self.__test_KLStructOperators_Content(klNamespace)

    def test_KLStructOperators_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructOperators, sys._getframe().f_code.co_name)
        self.__test_KLStructOperators_Content(klNamespace)

    def test_KLStructOperators_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructOperators, sys._getframe().f_code.co_name)
        self.__test_KLStructOperators_Content(klNamespace)

    def test_KLStructOperators_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLStructOperators, sys._getframe().f_code.co_name)
        self.__test_KLStructOperators_Content(klNamespace)

    # ===================================================================================================================

    source_KLNamespaceOperators = '''
         struct KLNamespaceOperatorsFoo
         {
             public Integer value;
         };
         KLNamespaceOperatorsFoo(Integer value) { this.value = value; }
         KLNamespaceOperatorsFoo + (KLNamespaceOperatorsFoo a, KLNamespaceOperatorsFoo b) {
           return KLNamespaceOperatorsFoo(a.value + b.value);
         }
         inline Boolean != (KLNamespaceOperatorsFoo lhs, KLNamespaceOperatorsFoo rhs) {
           return lhs.value != rhs.value;
         }
         inline KLNamespaceOperatorsFoo -KLNamespaceOperatorsFoo() {
           return KLNamespaceOperatorsFoo(-this.value);
         }
         '''

    def __test_KLNamespaceOperators_Content(self, klNamespace):
        self.assertEqual(klNamespace.getStructCount(), 1)
        self.assertEqual(klNamespace.getOperatorCount(), 3)
        klOp = klNamespace.getOperator(0)
        self.assertEqual(klOp.getName(), 'add')
        self.assertEqual(klOp.getReturnType(), 'KLNamespaceOperatorsFoo')
        self.assertEqual(klOp.getAccess(), 'unspecified')
        self.assertEqual(klOp.getParamCount(), 2)
        self.assertEqual(klOp.getParam(0).getName(), 'a')
        self.assertEqual(klOp.getParam(0).getType(), 'KLNamespaceOperatorsFoo')
        self.assertEqual(klOp.getParam(1).getName(), 'b')
        self.assertEqual(klOp.getParam(1).getType(), 'KLNamespaceOperatorsFoo')
        klOp = klNamespace.getOperator(1)
        self.assertEqual(klOp.getName(), 'ne')
        self.assertEqual(klOp.getReturnType(), 'Boolean')
        self.assertEqual(klOp.getAccess(), 'unspecified')
        self.assertEqual(klOp.getParamCount(), 2)
        self.assertEqual(klOp.getParam(0).getName(), 'lhs')
        self.assertEqual(klOp.getParam(0).getType(), 'KLNamespaceOperatorsFoo')
        self.assertEqual(klOp.getParam(1).getName(), 'rhs')
        self.assertEqual(klOp.getParam(1).getType(), 'KLNamespaceOperatorsFoo')
        klOp = klNamespace.getOperator(2)
        self.assertEqual(klOp.getName(), 'NEG')
        self.assertEqual(klOp.getReturnType(), 'KLNamespaceOperatorsFoo')
        self.assertEqual(klOp.getAccess(), 'unspecified')
        self.assertEqual(klOp.getParamCount(), 0)

    def test_KLNamespaceOperators_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLNamespaceOperators, sys._getframe().f_code.co_name)
        self.__test_KLNamespaceOperators_Content(klNamespace)

    def test_KLNamespaceOperators_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLNamespaceOperators, sys._getframe().f_code.co_name)
        self.__test_KLNamespaceOperators_Content(klNamespace)

    def test_KLNamespaceOperators_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_KLNamespaceOperators, sys._getframe().f_code.co_name)
        self.__test_KLNamespaceOperators_Content(klNamespace)

    def test_KLNamespaceOperators_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_KLNamespaceOperators, sys._getframe().f_code.co_name)
        self.__test_KLNamespaceOperators_Content(klNamespace)

    #===================================================================================================================
    source_ObjectInheritance = '''
        interface ObjectInheritanceInterface {
            DoSomething();
        };
        object ObjectInheritanceFoo : ObjectInheritanceInterface {
        };
        ObjectInheritanceFoo.DoSomething() {}
        '''

    def __test_ObjectInheritance_Content(self, klNamespace):
        self.assertEqual(klNamespace.getObjectNames(), ['ObjectInheritanceFoo'])
        klObject = klNamespace.getObject('ObjectInheritanceFoo')
        self.assertEqual(klObject.getParentsCount(), 1)
        self.assertEqual(klObject.getParent(0).getName(), 'ObjectInheritanceInterface')

    def test_ObjectInheritance_E1_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_ObjectInheritance, sys._getframe().f_code.co_name)
        self.__test_ObjectInheritance_Content(klNamespace)

    def test_ObjectInheritance_E1_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_ObjectInheritance, sys._getframe().f_code.co_name)
        self.__test_ObjectInheritance_Content(klNamespace)

    def test_ObjectInheritance_E0_N1_(self):
        klExtension, klNamespace = self.__setup(self.source_ObjectInheritance, sys._getframe().f_code.co_name)
        self.__test_ObjectInheritance_Content(klNamespace)

    def test_ObjectInheritance_E0_N0_(self):
        klExtension, klNamespace = self.__setup(self.source_ObjectInheritance, sys._getframe().f_code.co_name)
        self.__test_ObjectInheritance_Content(klNamespace)

    #===================================================================================================================
    def test_RequireGorGonCore(self):
        sourceCode = '''
            require GorGon_Core;
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getNamespaceNames(), [u'GorGon::Core'])
        self.assertEqual(self.klEnv.getExtensionNames(), [u'Singletons', u'FabricSynchronization', u'GorGon_Core'])
        klNamespace = self.klEnv.getExtension('FabricSynchronization').getGlobalNamespace()
        self.assertEqual(klNamespace.getObjectCount(), 8)
        self.assertEqual(klNamespace.getStructCount(), 26)
        self.assertEqual(klNamespace.getFunctionCount(), 35)
        self.assertEqual(klNamespace.getOperatorCount(), 0)
        self.assertEqual(klNamespace.getConstantCount(), 26)
        klNamespace = self.klEnv.getExtension('GorGon_Core').getNamespace('GorGon::Core')
        self.assertEqual(klNamespace.getObjectCount(), 5)
        self.assertEqual(klNamespace.getStructCount(), 0)
        self.assertEqual(klNamespace.getFunctionCount(), 19)
        self.assertEqual(klNamespace.getOperatorCount(), 0)
        self.assertEqual(klNamespace.getConstantCount(), 0)
        self.assertEqual(self.klEnv.getExtension('GorGon_Core').getExtensionDependencies(), [u'Singletons', u'FabricSynchronization'])

    #===================================================================================================================
    def test_RequireGorGonECS(self):
        sourceCode = '''
            require GorGon_ECS;
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getExtensionNames(), [u'GorGon_ECS', u'GorGon_Core', u'FabricSynchronization', u'Singletons', u'GorGon_Maths', u'Math'])
        self.assertEqual(self.klEnv.getExtension('GorGon_Core').getExtensionDependencies(), [u'Singletons', u'FabricSynchronization'])
        self.assertEqual(self.klEnv.getExtension('GorGon_Maths').getExtensionDependencies(), [u'Singletons', u'Math'])
        self.assertEqual(self.klEnv.getExtension('GorGon_ECS').getExtensionDependencies(), [u'Singletons', u'Math', u'GorGon_Core', u'GorGon_Maths'])

    #===================================================================================================================
    def test_RequireFabricMaths(self):
        sourceCode = '''
            require Math;
            '''
        self.klEnv.parseSourceCode(sourceCode)
        klNamespace = self.klEnv.getExtension('Math').getGlobalNamespace()
        self.assertEqual(klNamespace.getObjectCount(), 0)
        self.assertEqual(klNamespace.getStructCount(), 57)
        self.assertEqual(klNamespace.getFunctionCount(), 80)
        self.assertEqual(klNamespace.getOperatorCount(), 534)
        self.assertEqual(klNamespace.getConstantCount(), 19)


if __name__ == '__main__':
    unittest.main()
