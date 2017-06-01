import unittest
from GorGon.KLWrapper.KLEnv import KLEnv

class KLWrapper(unittest.TestCase):

    def test_IsSetter(self):
        self.assertEqual(KLEnv.isSetter('doSomething'), False)
        self.assertEqual(KLEnv.isSetter('Set'), False)
        self.assertEqual(KLEnv.isSetter('SetSomething'), False)
        self.assertEqual(KLEnv.isSetter('set'), False)
        self.assertEqual(KLEnv.isSetter('setSomething'), True)
        self.assertEqual(KLEnv.isSetter('setX'), True)
        self.assertEqual(KLEnv.isSetter('setup'), False)

    def test_IsGetter(self):
        self.assertEqual(KLEnv.isGetter('doSomething'), False)
        self.assertEqual(KLEnv.isGetter('Get'), False)
        self.assertEqual(KLEnv.isGetter('GetSomething'), False)
        self.assertEqual(KLEnv.isGetter('get'), False)
        self.assertEqual(KLEnv.isGetter('getSomething'), True)
        self.assertEqual(KLEnv.isGetter('getX'), True)
        self.assertEqual(KLEnv.isGetter('getup'), False)

    def test_KLObject(self):
        sourceCode = '''
            object Foo {};
            '''
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getObjectCount(), 1)
        self.assertEqual(str(klEnv.getGlobalNamespace().getObjectNames()), "[u'Foo']")
        klObject = klEnv.getGlobalNamespace().getObject('Foo')
        self.assertEqual(klObject.getName(), 'Foo')


    def test_KLStruct(self):
        sourceCode = '''
            struct Foo {};
            '''
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getStructCount(), 1)
        self.assertEqual(str(klEnv.getGlobalNamespace().getStructNames()), "[u'Foo']")
        klStruct = klEnv.getGlobalNamespace().getStruct('Foo')
        self.assertEqual(klStruct.getName(), 'Foo')


    def test_KLObjectWithinNamespace(self):
        sourceCode = '''
            namespace NS { object Foo {}; }
            '''
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getObjectCount(), 0)
        self.assertEqual(klEnv.getNamespaceCount(), 1)
        klNamespace = klEnv.getNamespace('NS')
        self.assertEqual(klNamespace.getName(), 'NS')
        self.assertEqual(klNamespace.getObjectCount(), 1)
        self.assertEqual(str(klNamespace.getObjectNames()), "[u'Foo']")
        self.assertEqual(klNamespace.hasObject('Foo'), True)


    def test_KLStructWithinNamespace(self):
        sourceCode = '''
            namespace NS { struct Foo {}; }
            '''
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getStructCount(), 0)
        self.assertEqual(klEnv.getNamespaceCount(), 1)
        klNamespace = klEnv.getNamespace('NS')
        self.assertEqual(klNamespace.getName(), 'NS')
        self.assertEqual(klNamespace.getStructCount(), 1)
        self.assertEqual(str(klNamespace.getStructNames()), "[u'Foo']")
        self.assertEqual(klNamespace.hasStruct('Foo'), True)


    def test_KLGlobalFunctions(self):
        sourceCode = '''
            function Hello(String s) {}
            function Boolean You() {}
            '''
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getObjectCount(), 0)
        self.assertEqual(str(klEnv.getGlobalNamespace().getObjectNames()), "[]")
        self.assertEqual(klEnv.getGlobalNamespace().getFunctionCount(), 2)
        self.assertEqual(klEnv.getGlobalNamespace().hasFunction('Hello'), True)
        self.assertEqual(klEnv.getGlobalNamespace().getFunction('Hello').getName(), 'Hello')
        self.assertEqual(klEnv.getGlobalNamespace().getFunction('Hello').getReturnType(), None)
        self.assertEqual(klEnv.getGlobalNamespace().getFunction('Hello').getParamCount(), 1)
        self.assertEqual(klEnv.getGlobalNamespace().getFunction('Hello').getParam(0).getName(), 's')
        self.assertEqual(klEnv.getGlobalNamespace().getFunction('Hello').getParam(0).getType(), 'String')
        self.assertEqual(klEnv.getGlobalNamespace().hasFunction('You'), True)
        self.assertEqual(klEnv.getGlobalNamespace().getFunction('You').getName(), 'You')
        self.assertEqual(klEnv.getGlobalNamespace().getFunction('You').getReturnType(), 'Boolean')
        self.assertEqual(klEnv.getGlobalNamespace().getFunction('You').getParamCount(), 0)


    def test_KLGlobalFunctionsWithinNamespace(self):
        sourceCode = '''
            namespace NS {
                function Hello(String s) {}
                function Boolean You() {}
            }
            '''
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getObjectCount(), 0)
        self.assertEqual(klEnv.getGlobalNamespace().getFunctionCount(), 0)
        self.assertEqual(klEnv.getNamespaceCount(), 1)
        klNamespace = klEnv.getNamespace('NS')
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


    def test_KLObjectManyNamespaces(self):
        sourceCode = '''
            namespace NS { object Foo {}; }
            namespace NS2 { object Bar {}; }
            object Outside {};
            '''
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getObjectCount(), 1)
        self.assertEqual(klEnv.getNamespaceCount(), 2)
        self.assertEqual(str(klEnv.getNamespaceNames()), "[u'NS2', u'NS']")
        klNamespace = klEnv.getNamespace('NS')
        self.assertEqual(klNamespace.getName(), 'NS')
        self.assertEqual(klNamespace.getObjectCount(), 1)
        self.assertEqual(klNamespace.hasObject('Foo'), True)
        klNamespace = klEnv.getNamespace('NS2')
        self.assertEqual(klNamespace.getName(), 'NS2')
        self.assertEqual(klNamespace.getObjectCount(), 1)
        self.assertEqual(klNamespace.hasObject('Bar'), True)


    def test_KLStructManyNamespaces(self):
        sourceCode = '''
            namespace NS { struct Foo {}; }
            namespace NS2 { struct Bar {}; }
            struct Outside {};
            '''
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getStructCount(), 1)
        self.assertEqual(klEnv.getNamespaceCount(), 2)
        self.assertEqual(str(klEnv.getNamespaceNames()), "[u'NS2', u'NS']")
        klNamespace = klEnv.getNamespace('NS')
        self.assertEqual(klNamespace.getName(), 'NS')
        self.assertEqual(klNamespace.getStructCount(), 1)
        self.assertEqual(klNamespace.hasStruct('Foo'), True)
        klNamespace = klEnv.getNamespace('NS2')
        self.assertEqual(klNamespace.getName(), 'NS2')
        self.assertEqual(klNamespace.getStructCount(), 1)
        self.assertEqual(klNamespace.hasStruct('Bar'), True)


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
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getObjectCount(), 1)
        klObject = klEnv.getGlobalNamespace().getObject('Foo')
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
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getStructCount(), 1)
        klStruct = klEnv.getGlobalNamespace().getStruct('Foo')
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
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getObjectCount(), 1)
        klObject = klEnv.getGlobalNamespace().getObject('Foo')
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
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getObjectCount(), 1)
        klObject = klEnv.getGlobalNamespace().getObject('Foo')
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
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getStructCount(), 1)
        klStruct = klEnv.getGlobalNamespace().getStruct('Foo')
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
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getStructCount(), 1)
        klStruct = klEnv.getGlobalNamespace().getStruct('Foo')
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
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getObjectCount(), 1)
        klObject = klEnv.getGlobalNamespace().getObject('Foo')
        self.assertEqual(klObject.getName(), 'Foo')
        self.assertEqual(klObject.getConstructorCount(), 2)


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
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getStructCount(), 1)
        klStruct = klEnv.getGlobalNamespace().getStruct('Foo')
        self.assertEqual(klStruct.getName(), 'Foo')
        self.assertEqual(klStruct.getConstructorCount(), 2)


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
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getObjectCount(), 1)
        klObject = klEnv.getGlobalNamespace().getObject('Foo')
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


    def __test_KLStructGettersAndSetters(self):
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
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getStructCount(), 1)
        klStruct = klEnv.getGlobalNamespace().getStruct('Foo')
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
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getObjectCount(), 1)
        klObject = klEnv.getGlobalNamespace().getObject('Foo')
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


    def __test_RequireGorGonCore(self):
        sourceCode = '''
            require GorGon_Core;
            '''
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getObjectCount(), 9)
        self.assertEqual(klEnv.getGlobalNamespace().getStructCount(), 26)
        self.assertEqual(str(klEnv.getGlobalNamespace().getObjectNames()), "[u'InitializeBracket', u'MultithreadAdvisor', u'ComputeContext', u'AsyncTask', u'FewObjectsRecyclingAllocator', u'FastReadersWriterLock', u'SimpleLock', u'Float32', u'IndexArray', u'LightReentrantLock', u'SingletonHandle', u'ActiveWaitLoopControl', u'AsyncTaskQueue', u'AsyncTaskCircularBuffer', u'ReadersWriterLock_writeLock', u'LightLock', u'MultithreadAdvisorBracket', u'MultithreadAdvisorBatchBracket', u'ReadersWriterLock_readLock', u'LightReadersWriterLock', u'LockedInitialize', u'ThreadSafeAttachedData', u'ComputeContextRTValWrapper', u'StringArray']")
        # self.assertEqual(klEnv.getNamespaceCount(), 1)
        # self.assertEqual(str(klEnv.getNamespaceNames()), "[u'GorGon::Core']")
        # klNamespace = klEnv.getNamespace('GorGon::Core')
        # self.assertEqual(klNamespace.getObjectCount(), 5)
        # self.assertEqual(klNamespace.getFunctionCount(), 19)


    def __test_RequireFabricMaths(self):
        sourceCode = '''
            require Math;
            '''
        klEnv = KLEnv(sourceCode)
        # self.assertEqual(klEnv.getGlobalNamespace().getObjectCount(), 66)
        # self.assertEqual(klEnv.getGlobalNamespace().getFunctionCount(), 137)


if __name__ == '__main__':
    unittest.main()
