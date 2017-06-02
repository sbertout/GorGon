import unittest
from GorGon.KLWrapper.KLEnv import KLEnv

class KLWrapperTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(KLWrapperTests, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        cls.klEnv = KLEnv()

    def tearDown(self):
        super(KLWrapperTests, self).tearDown()
        self.klEnv.reset()

    #=========================================================================
    def test_IsSetter(self):
        self.assertEqual(KLEnv.isSetter('doSomething'), False)
        self.assertEqual(KLEnv.isSetter('Set'), False)
        self.assertEqual(KLEnv.isSetter('SetSomething'), False)
        self.assertEqual(KLEnv.isSetter('set'), False)
        self.assertEqual(KLEnv.isSetter('setSomething'), True)
        self.assertEqual(KLEnv.isSetter('setX'), True)
        self.assertEqual(KLEnv.isSetter('setup'), False)

    #=========================================================================
    def test_IsGetter(self):
        self.assertEqual(KLEnv.isGetter('doSomething'), False)
        self.assertEqual(KLEnv.isGetter('Get'), False)
        self.assertEqual(KLEnv.isGetter('GetSomething'), False)
        self.assertEqual(KLEnv.isGetter('get'), False)
        self.assertEqual(KLEnv.isGetter('getSomething'), True)
        self.assertEqual(KLEnv.isGetter('getX'), True)
        self.assertEqual(KLEnv.isGetter('getup'), False)

    #=========================================================================
    def test_KLConstants(self):
        sourceCode = '''
            const Boolean DebugSomething = false;
            const Scalar SomeScalarConstant = 3.14;
            const Scalar TWO_SomeScalarConstant = SomeScalarConstant * 2.0;
            const Float32 SomeNegativeFloat32Constant = -10e6;
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstantCount(), 4)
        self.assertEqual(str(self.klEnv.getGlobalNamespace().getConstantNames()), "[u'SomeNegativeFloat32Constant', u'SomeScalarConstant', u'DebugSomething', u'TWO_SomeScalarConstant']")
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstant('DebugSomething').getName(), 'DebugSomething')
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstant('DebugSomething').getType(), 'ConstBoolean')
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstant('DebugSomething').getValue(), False)
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstant('SomeScalarConstant').getName(), 'SomeScalarConstant')
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstant('SomeScalarConstant').getType(), 'ASTConstFloat')
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstant('SomeScalarConstant').getValue(), '3.14')
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstant('TWO_SomeScalarConstant').getName(), 'TWO_SomeScalarConstant')
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstant('TWO_SomeScalarConstant').getType(), 'mul')
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstant('TWO_SomeScalarConstant').getValue(), 'mul(SomeScalarConstant,2.0)')
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstant('SomeNegativeFloat32Constant').getName(), 'SomeNegativeFloat32Constant')
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstant('SomeNegativeFloat32Constant').getType(), 'NEG')
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstant('SomeNegativeFloat32Constant').getValue(), 'NEG(10e6)')

    #=========================================================================
    def test_KLAliasConstants(self):
        sourceCode = '''
            alias Scalar SomeScalarAlias;
            const SomeScalarAlias SomeScalarConstant = 3.14;
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstantCount(), 1)
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstant('SomeScalarConstant').getName(), 'SomeScalarConstant')
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstant('SomeScalarConstant').getType(), 'ASTConstFloat')
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstant('SomeScalarConstant').getValue(), '3.14')

    #=========================================================================
    def test_KLAliases(self):
        sourceCode = '''
            alias UInt32 SomeIntAlias;
            alias Scalar SomeScalarAlias;
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getAliasCount(), 2)
        self.assertEqual(self.klEnv.getGlobalNamespace().getAlias('SomeIntAlias').getName(), 'SomeIntAlias')
        self.assertEqual(self.klEnv.getGlobalNamespace().getAlias('SomeIntAlias').getSourceName(), 'UInt32')
        self.assertEqual(self.klEnv.getGlobalNamespace().getAlias('SomeScalarAlias').getName(), 'SomeScalarAlias')
        self.assertEqual(self.klEnv.getGlobalNamespace().getAlias('SomeScalarAlias').getSourceName(), 'Scalar')

    #=========================================================================
    def test_KLAliasOperators(self):
        sourceCode = '''
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
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getAliasCount(), 1)
        klAlias = self.klEnv.getGlobalNamespace().getAlias('SomeIntAlias')
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

    #=========================================================================
    def test_KLAliasFunc(self):
        sourceCode = '''
            alias UInt32 SomeIntAlias;
            SomeIntAlias SomeIntAlias.clamp(in SomeIntAlias min, in SomeIntAlias max) {
                return (this < min ? min : (this > max ? max : this));
            }
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getAliasCount(), 1)
        self.assertEqual(self.klEnv.getGlobalNamespace().getAlias('SomeIntAlias').getName(), 'SomeIntAlias')
        self.assertEqual(self.klEnv.getGlobalNamespace().getAlias('SomeIntAlias').getSourceName(), 'UInt32')
        self.assertEqual(self.klEnv.getGlobalNamespace().getAlias('SomeIntAlias').getMethodCount(), 1)
        self.assertEqual(self.klEnv.getGlobalNamespace().getAlias('SomeIntAlias').getMethod(0).getParamCount(), 2)
        self.assertEqual(self.klEnv.getGlobalNamespace().getAlias('SomeIntAlias').getMethod(0).getReturnType(), 'SomeIntAlias')

    #=========================================================================
    def test_KLAliasWithinNamespace(self):
        sourceCode = '''
            namespace NS { alias UInt32 SomeIntAlias; }
            '''
        self.klEnv.parseSourceCode(sourceCode)
        klNamespace = self.klEnv.getNamespace('NS')
        self.assertEqual(klNamespace.getAliasCount(), 1)
        self.assertEqual(klNamespace.getAlias('SomeIntAlias').getName(), 'SomeIntAlias')
        self.assertEqual(klNamespace.getAlias('SomeIntAlias').getSourceName(), 'UInt32')

    #=========================================================================
    def test_KLAliasFuncWithinNamespace(self):
        sourceCode = '''
            namespace NS { 
                alias UInt32 SomeIntAlias;
                SomeIntAlias SomeIntAlias.clamp(in SomeIntAlias min, in SomeIntAlias max) {
                    return (this < min ? min : (this > max ? max : this));
                }
            }
            '''
        self.klEnv.parseSourceCode(sourceCode)
        klNamespace = self.klEnv.getNamespace('NS')
        self.assertEqual(klNamespace.getAliasCount(), 1)
        self.assertEqual(klNamespace.getAlias('SomeIntAlias').getName(), 'SomeIntAlias')
        self.assertEqual(klNamespace.getAlias('SomeIntAlias').getSourceName(), 'UInt32')
        self.assertEqual(klNamespace.getAlias('SomeIntAlias').getMethodCount(), 1)
        self.assertEqual(klNamespace.getAlias('SomeIntAlias').getMethod(0).getParamCount(), 2)
        self.assertEqual(klNamespace.getAlias('SomeIntAlias').getMethod(0).getReturnType(), 'SomeIntAlias')

    #=========================================================================
    def test_KLObject(self):
        sourceCode = '''
            object Foo {};
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getObjectCount(), 1)
        self.assertEqual(str(self.klEnv.getGlobalNamespace().getObjectNames()), "[u'Foo']")
        klObject = self.klEnv.getGlobalNamespace().getObject('Foo')
        self.assertEqual(klObject.getName(), 'Foo')

    #=========================================================================
    def test_KLStruct(self):
        sourceCode = '''
            struct Foo {};
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getStructCount(), 1)
        self.assertEqual(str(self.klEnv.getGlobalNamespace().getStructNames()), "[u'Foo']")
        klStruct = self.klEnv.getGlobalNamespace().getStruct('Foo')
        self.assertEqual(klStruct.getName(), 'Foo')

    #=========================================================================
    def test_KLObjectWithinNamespace(self):
        sourceCode = '''
            namespace NS { object Foo {}; }
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getObjectCount(), 0)
        self.assertEqual(self.klEnv.getNamespaceCount(), 1)
        klNamespace = self.klEnv.getNamespace('NS')
        self.assertEqual(klNamespace.getName(), 'NS')
        self.assertEqual(klNamespace.getObjectCount(), 1)
        self.assertEqual(str(klNamespace.getObjectNames()), "[u'Foo']")
        self.assertEqual(klNamespace.hasObject('Foo'), True)

    #=========================================================================
    def test_KLStructWithinNamespace(self):
        sourceCode = '''
            namespace NS { struct Foo {}; }
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getStructCount(), 0)
        self.assertEqual(self.klEnv.getNamespaceCount(), 1)
        klNamespace = self.klEnv.getNamespace('NS')
        self.assertEqual(klNamespace.getName(), 'NS')
        self.assertEqual(klNamespace.getStructCount(), 1)
        self.assertEqual(str(klNamespace.getStructNames()), "[u'Foo']")
        self.assertEqual(klNamespace.hasStruct('Foo'), True)

    #=========================================================================
    def test_KLGlobalFunctions(self):
        sourceCode = '''
            function Hello(String s) {}
            function Boolean You() {}
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getObjectCount(), 0)
        self.assertEqual(str(self.klEnv.getGlobalNamespace().getObjectNames()), "[]")
        self.assertEqual(self.klEnv.getGlobalNamespace().getFunctionCount(), 2)
        self.assertEqual(self.klEnv.getGlobalNamespace().hasFunction('Hello'), True)
        self.assertEqual(self.klEnv.getGlobalNamespace().getFunction('Hello').getName(), 'Hello')
        self.assertEqual(self.klEnv.getGlobalNamespace().getFunction('Hello').getReturnType(), None)
        self.assertEqual(self.klEnv.getGlobalNamespace().getFunction('Hello').getParamCount(), 1)
        self.assertEqual(self.klEnv.getGlobalNamespace().getFunction('Hello').getParam(0).getName(), 's')
        self.assertEqual(self.klEnv.getGlobalNamespace().getFunction('Hello').getParam(0).getType(), 'String')
        self.assertEqual(self.klEnv.getGlobalNamespace().hasFunction('You'), True)
        self.assertEqual(self.klEnv.getGlobalNamespace().getFunction('You').getName(), 'You')
        self.assertEqual(self.klEnv.getGlobalNamespace().getFunction('You').getReturnType(), 'Boolean')
        self.assertEqual(self.klEnv.getGlobalNamespace().getFunction('You').getParamCount(), 0)

    #=========================================================================
    def test_KLGlobalFunctionsWithinNamespace(self):
        sourceCode = '''
            namespace NS {
                function Hello(String s) {}
                function Boolean You() {}
            }
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getObjectCount(), 0)
        self.assertEqual(self.klEnv.getGlobalNamespace().getFunctionCount(), 0)
        self.assertEqual(self.klEnv.getNamespaceCount(), 1)
        klNamespace = self.klEnv.getNamespace('NS')
        self.assertEqual(klNamespace.getName(), 'NS')
        self.assertEqual(klNamespace.getObjectCount(), 0)
        self.assertEqual(str(klNamespace.getObjectNames()), "[]")
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

    #=========================================================================
    def test_KLObjectManyNamespaces(self):
        sourceCode = '''
            namespace NS { object Foo {}; }
            namespace NS2 { object Bar {}; }
            object Outside {};
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getObjectCount(), 1)
        self.assertEqual(self.klEnv.getNamespaceCount(), 2)
        self.assertEqual(str(self.klEnv.getNamespaceNames()), "[u'NS2', u'NS']")
        klNamespace = self.klEnv.getNamespace('NS')
        self.assertEqual(klNamespace.getName(), 'NS')
        self.assertEqual(klNamespace.getObjectCount(), 1)
        self.assertEqual(klNamespace.hasObject('Foo'), True)
        klNamespace = self.klEnv.getNamespace('NS2')
        self.assertEqual(klNamespace.getName(), 'NS2')
        self.assertEqual(klNamespace.getObjectCount(), 1)
        self.assertEqual(klNamespace.hasObject('Bar'), True)

    #=========================================================================
    def test_KLStructManyNamespaces(self):
        sourceCode = '''
            namespace NS { struct Foo {}; }
            namespace NS2 { struct Bar {}; }
            struct Outside {};
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getStructCount(), 1)
        self.assertEqual(self.klEnv.getNamespaceCount(), 2)
        self.assertEqual(str(self.klEnv.getNamespaceNames()), "[u'NS2', u'NS']")
        klNamespace = self.klEnv.getNamespace('NS')
        self.assertEqual(klNamespace.getName(), 'NS')
        self.assertEqual(klNamespace.getStructCount(), 1)
        self.assertEqual(klNamespace.hasStruct('Foo'), True)
        klNamespace = self.klEnv.getNamespace('NS2')
        self.assertEqual(klNamespace.getName(), 'NS2')
        self.assertEqual(klNamespace.getStructCount(), 1)
        self.assertEqual(klNamespace.hasStruct('Bar'), True)

    #=========================================================================
    def test_KLObjectMembers(self):
        sourceCode = '''
            object Foo
            {
                public String name;
                protected Boolean enabled;
                private Integer value;
                Scalar offset;
            };
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getObjectCount(), 1)
        klObject = self.klEnv.getGlobalNamespace().getObject('Foo')
        self.assertEqual(klObject.getName(), 'Foo')
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

    #=========================================================================
    def test_KLStructMembers(self):
        sourceCode = '''
            struct Foo
            {
                public String name;
                protected Boolean enabled;
                private Integer value;
                Scalar offset;
            };
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getStructCount(), 1)
        klStruct = self.klEnv.getGlobalNamespace().getStruct('Foo')
        self.assertEqual(klStruct.getName(), 'Foo')
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

    #=========================================================================
    def test_KLObjectConstructors(self):
        sourceCode = '''
            object Foo
            {
                private String name;
                private Boolean state;
            };
            Foo(String name) { this.name = name; }
            Foo(String name, Boolean state) { this.name = name; this.state = state; }
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getObjectCount(), 1)
        klObject = self.klEnv.getGlobalNamespace().getObject('Foo')
        self.assertEqual(klObject.getName(), 'Foo')
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

    #=========================================================================
    def test_KLObjectDestructor(self):
        sourceCode = '''
            object Foo
            {
                private String name;
                private Boolean state;
            };
            Foo(String name) { this.name = name; }
            ~Foo() {}
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getObjectCount(), 1)
        klObject = self.klEnv.getGlobalNamespace().getObject('Foo')
        self.assertEqual(klObject.getName(), 'Foo')
        self.assertEqual(klObject.getConstructorCount(), 1)
        self.assertEqual(klObject.getHasDestructor(), True)

    #=========================================================================
    def test_KLObjectForwardDeclaredConstructors(self):
        sourceCode = '''
            Foo(String name) { this.name = name; }
            Foo(String name, Boolean state) { this.name = name; this.state = state; }
            object Foo
            {
                private String name;
                private Boolean state;
            };
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getObjectCount(), 1)
        klObject = self.klEnv.getGlobalNamespace().getObject('Foo')
        self.assertEqual(klObject.getName(), 'Foo')
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

    #=========================================================================
    def test_KLStructConstructors(self):
        sourceCode = '''
            struct Foo
            {
                private String name;
                private Boolean state;
            };
            Foo(String name) { this.name = name; }
            Foo(String name, Boolean state) { this.name = name; this.state = state; }
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getStructCount(), 1)
        klStruct = self.klEnv.getGlobalNamespace().getStruct('Foo')
        self.assertEqual(klStruct.getName(), 'Foo')
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

    #=========================================================================
    def test_KLStructForwardDeclaredConstructors(self):
        sourceCode = '''
            Foo(String name) { this.name = name; }
            Foo(String name, Boolean state) { this.name = name; this.state = state; }
            struct Foo
            {
                private String name;
                private Boolean state;
            };
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getStructCount(), 1)
        klStruct = self.klEnv.getGlobalNamespace().getStruct('Foo')
        self.assertEqual(klStruct.getName(), 'Foo')
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

    #=========================================================================
    def test_KLStructDestructor(self):
        sourceCode = '''
            struct Foo
            {
                private String name;
                private Boolean state;
            };
            Foo(String name) { this.name = name; }
            ~Foo() {}
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getStructCount(), 1)
        klStruct = self.klEnv.getGlobalNamespace().getStruct('Foo')
        self.assertEqual(klStruct.getName(), 'Foo')
        self.assertEqual(klStruct.getConstructorCount(), 1)
        self.assertEqual(klStruct.getHasDestructor(), True)

    #=========================================================================
    def test_KLObjectConstructors_ObjectForwardDeclared(self):
        sourceCode = '''
            object Foo;
            Foo(String name) { this.name = name; }
            object Foo
            {
                private String name;
                private Boolean state;
            };
            Foo(String name, Boolean state) { this.name = name; this.state = state; }
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getObjectCount(), 1)
        klObject = self.klEnv.getGlobalNamespace().getObject('Foo')
        self.assertEqual(klObject.getName(), 'Foo')
        self.assertEqual(klObject.getConstructorCount(), 2)

    #=========================================================================
    def test_KLStructConstructors_StructForwardDeclared(self):
        sourceCode = '''
            struct Foo;
            Foo(String name) { this.name = name; }
            struct Foo
            {
                private String name;
                private Boolean state;
            };
            Foo(String name, Boolean state) { this.name = name; this.state = state; }
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getStructCount(), 1)
        klStruct = self.klEnv.getGlobalNamespace().getStruct('Foo')
        self.assertEqual(klStruct.getName(), 'Foo')
        self.assertEqual(klStruct.getConstructorCount(), 2)

    #=========================================================================
    def test_KLObjectGettersAndSetters(self):
        sourceCode = '''
            object Foo
            {
                private String name;
                private Boolean state;
            };
            Foo(String name) { this.setName(name); }
            public String Foo.getName() { return this.name; }
            protected Foo.setName!(String name) { this.name = name; }
            private Boolean Foo.getState() { return this.state; }
            Foo.setState!(Boolean state) { this.state = state; }
            Foo.setup() {}
            Foo.doSomething() {}
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getObjectCount(), 1)
        klObject = self.klEnv.getGlobalNamespace().getObject('Foo')
        self.assertEqual(klObject.getName(), 'Foo')
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

    #=========================================================================
    def test_KLStructGettersAndSetters(self):
        sourceCode = '''
            struct Foo
            {
                private String name;
                private Boolean state;
            };
            Foo(String name) { this.setName(name); }
            public String Foo.getName() { return this.name; }
            protected Foo.setName!(String name) { this.name = name; }
            private Boolean Foo.getState() { return this.state; }
            Foo.setState!(Boolean state) { this.state = state; }
            Foo.setup() {}
            Foo.doSomething() {}
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getStructCount(), 1)
        klStruct = self.klEnv.getGlobalNamespace().getStruct('Foo')
        self.assertEqual(klStruct.getName(), 'Foo')
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

    #=========================================================================
    def test_KLObjectMethods(self):
        sourceCode = '''
            object Foo
            {
                private String name;
                private Boolean state;
            };
            Foo(String name) { this.setName(name); }
            public String Foo.getName() { return this.name; }
            protected Foo.setName!(String name) { this.name = name; }
            private Boolean Foo.getState() { return this.state; }
            Foo.setState!(Boolean state) { this.state = state; }
            Foo.setup(Boolean b) {}
            String Foo.doSomething() {}
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getObjectCount(), 1)
        klObject = self.klEnv.getGlobalNamespace().getObject('Foo')
        self.assertEqual(klObject.getName(), 'Foo')
        self.assertEqual(klObject.getMethodCount(), 2)
        self.assertEqual(klObject.getMethod(0).getName(), 'setup')
        self.assertEqual(klObject.getMethod(0).getReturnType(), None)
        self.assertEqual(klObject.getMethod(0).getParamCount(), 1)
        self.assertEqual(klObject.getMethod(0).getParam(0).getName(), 'b')
        self.assertEqual(klObject.getMethod(0).getParam(0).getType(), 'Boolean')
        self.assertEqual(klObject.getMethod(1).getName(), 'doSomething')
        self.assertEqual(klObject.getMethod(1).getParamCount(), 0)
        self.assertEqual(klObject.getMethod(1).getReturnType(), 'String')

    #=========================================================================
    def test_KLObjectOperators(self):
        sourceCode = '''
            object Foo
            {
                private Integer value;
            };
            Foo(Integer value) { this.value = name; }
            Foo. *= (Integer other) {
              this.value = this.value * other;
            }
            Foo. += (Boolean b) {
              this.value += b;
            }
            Foo. *= (Scalar k) {
              this.value = this.value * k;
            }
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getObjectCount(), 1)
        klObject = self.klEnv.getGlobalNamespace().getObject('Foo')
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

    #=========================================================================
    def test_KLStructMethods(self):
        sourceCode = '''
            struct Foo
            {
                private String name;
                private Boolean state;
            };
            Foo(String name) { this.setName(name); }
            public String Foo.getName() { return this.name; }
            protected Foo.setName!(String name) { this.name = name; }
            private Boolean Foo.getState() { return this.state; }
            Foo.setState!(Boolean state) { this.state = state; }
            Foo.setup(Boolean b) {}
            String Foo.doSomething() {}
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getStructCount(), 1)
        klStruct = self.klEnv.getGlobalNamespace().getStruct('Foo')
        self.assertEqual(klStruct.getName(), 'Foo')
        self.assertEqual(klStruct.getMethodCount(), 2)
        self.assertEqual(klStruct.getMethod(0).getName(), 'setup')
        self.assertEqual(klStruct.getMethod(0).getReturnType(), None)
        self.assertEqual(klStruct.getMethod(0).getParamCount(), 1)
        self.assertEqual(klStruct.getMethod(0).getParam(0).getName(), 'b')
        self.assertEqual(klStruct.getMethod(0).getParam(0).getType(), 'Boolean')
        self.assertEqual(klStruct.getMethod(1).getName(), 'doSomething')
        self.assertEqual(klStruct.getMethod(1).getParamCount(), 0)
        self.assertEqual(klStruct.getMethod(1).getReturnType(), 'String')

    #=========================================================================
    def test_KLStructOperators(self):
        sourceCode = '''
            struct Foo
            {
                private Integer value;
            };
            Foo(Integer value) { this.value = name; }
            Foo. *= (Integer other) {
              this.value = this.value * other;
            }
            Foo. += (Boolean b) {
              this.value += b;
            }
            Foo. *= (Scalar k) {
              this.value = this.value * k;
            }
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getStructCount(), 1)
        klStruct = self.klEnv.getGlobalNamespace().getStruct('Foo')
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

        # =========================================================================

    def test_KLNamespaceOperators(self):
        sourceCode = '''
             struct Foo
             {
                 public Integer value;
             };
             Foo(Integer value) { this.value = value; }
             Foo + (Foo a, Foo b) {
               return Foo(a.value + b.value);
             }
             inline Boolean != (Foo lhs, Foo rhs) {
               return !lhs.equal(rhs);
             }
             inline Foo -Foo() {
               return Foo(-this.value);
             }
             '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getStructCount(), 1)
        self.assertEqual(self.klEnv.getGlobalNamespace().getOperatorCount(), 3)
        klOp = self.klEnv.getGlobalNamespace().getOperator(0)
        self.assertEqual(klOp.getName(), 'add')
        self.assertEqual(klOp.getReturnType(), 'Foo')
        self.assertEqual(klOp.getAccess(), 'unspecified')
        self.assertEqual(klOp.getParamCount(), 2)
        self.assertEqual(klOp.getParam(0).getName(), 'a')
        self.assertEqual(klOp.getParam(0).getType(), 'Foo')
        self.assertEqual(klOp.getParam(1).getName(), 'b')
        self.assertEqual(klOp.getParam(1).getType(), 'Foo')
        klOp = self.klEnv.getGlobalNamespace().getOperator(1)
        self.assertEqual(klOp.getName(), 'ne')
        self.assertEqual(klOp.getReturnType(), 'Boolean')
        self.assertEqual(klOp.getAccess(), 'unspecified')
        self.assertEqual(klOp.getParamCount(), 2)
        self.assertEqual(klOp.getParam(0).getName(), 'lhs')
        self.assertEqual(klOp.getParam(0).getType(), 'Foo')
        self.assertEqual(klOp.getParam(1).getName(), 'rhs')
        self.assertEqual(klOp.getParam(1).getType(), 'Foo')
        klOp = self.klEnv.getGlobalNamespace().getOperator(2)
        self.assertEqual(klOp.getName(), 'NEG')
        self.assertEqual(klOp.getReturnType(), 'Foo')
        self.assertEqual(klOp.getAccess(), 'unspecified')
        self.assertEqual(klOp.getParamCount(), 0)

    #=========================================================================
    def test_RequireGorGonCore(self):
        sourceCode = '''
            require GorGon_Core;
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getObjectCount(), 9)
        self.assertEqual(self.klEnv.getGlobalNamespace().getStructCount(), 26)
        self.assertEqual(self.klEnv.getGlobalNamespace().getFunctionCount(), 42)
        self.assertEqual(self.klEnv.getGlobalNamespace().getOperatorCount(), 0)
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstantCount(), 26)
        self.assertEqual(self.klEnv.getNamespace('GorGon::Core').getObjectCount(), 5)
        self.assertEqual(self.klEnv.getNamespace('GorGon::Core').getStructCount(), 0)
        self.assertEqual(self.klEnv.getNamespace('GorGon::Core').getFunctionCount(), 19)
        self.assertEqual(self.klEnv.getNamespace('GorGon::Core').getOperatorCount(), 0)
        self.assertEqual(self.klEnv.getNamespace('GorGon::Core').getConstantCount(), 0)

    #=========================================================================
    def test_RequireFabricMaths(self):
        sourceCode = '''
            require Math;
            '''
        self.klEnv.parseSourceCode(sourceCode)
        self.assertEqual(self.klEnv.getGlobalNamespace().getObjectCount(), 0)
        self.assertEqual(self.klEnv.getGlobalNamespace().getStructCount(), 57)
        self.assertEqual(self.klEnv.getGlobalNamespace().getFunctionCount(), 80)
        self.assertEqual(self.klEnv.getGlobalNamespace().getOperatorCount(), 534)
        self.assertEqual(self.klEnv.getGlobalNamespace().getConstantCount(), 19)


if __name__ == '__main__':
    unittest.main()
