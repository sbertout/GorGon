import unittest
import os, sys, argparse, json, shutil, collections
import FabricEngine.Core as FECore
from subprocess import Popen, PIPE, STDOUT
from GorGon.Utils import ColoredString
from GorGon.KLWrapper.KLEnv import KLEnv
from FabricEngine.Sphinx.ASTWrapper import *

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


    def test_RequireGorGonCore(self):
        sourceCode = '''
            require GorGon_Core;
            '''
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getObjectCount(), 24)
        self.assertEqual(str(klEnv.getGlobalNamespace().getObjectNames()), "[u'InitializeBracket', u'MultithreadAdvisor', u'ComputeContext', u'AsyncTask', u'FewObjectsRecyclingAllocator', u'FastReadersWriterLock', u'SimpleLock', u'Float32', u'IndexArray', u'LightReentrantLock', u'SingletonHandle', u'ActiveWaitLoopControl', u'AsyncTaskQueue', u'AsyncTaskCircularBuffer', u'ReadersWriterLock_writeLock', u'LightLock', u'MultithreadAdvisorBracket', u'MultithreadAdvisorBatchBracket', u'ReadersWriterLock_readLock', u'LightReadersWriterLock', u'LockedInitialize', u'ThreadSafeAttachedData', u'ComputeContextRTValWrapper', u'StringArray']")
        self.assertEqual(klEnv.getNamespaceCount(), 1)
        self.assertEqual(str(klEnv.getNamespaceNames()), "[u'GorGon::Core']")
        klNamespace = klEnv.getNamespace('GorGon::Core')
        self.assertEqual(klNamespace.getObjectCount(), 5)
        self.assertEqual(str(klNamespace.getObjectNames()), "[u'TaskBase', u'TaskMasterQueue', u'TaskMaster', u'Properties', u'Context']")
        #todo add extension owner to Function&Object
        # klObject = klEnv.getGlobalNamespace().getObject('Foo')
        # self.assertEqual(klObject.getName(), 'Foo')


    def test_RequireFabricMaths(self):
        sourceCode = '''
            require Math;
            '''
        klEnv = KLEnv(sourceCode)
        self.assertEqual(klEnv.getGlobalNamespace().getObjectCount(), 66)
        self.assertEqual(str(klEnv.getGlobalNamespace().getObjectNames()), "[u'Vec3_c', u'Vec2_i', u'Complex_d', u'Vec3_d', u'Xfo', u'Vec2_c', u'Euler_d', u'Euler', u'Vec3_i', u'Mat_cd', u'Vec2_d', u'RGB', u'Complex', u'Vec', u'Vec4_i', u'Euler_i', u'ARGB', u'Float32', u'Mat_c', u'Box3', u'Mat', u'SInt64', u'Quat_i', u'Quat', u'Quat_d', u'Mat_i', u'Vec4', u'UInt16', u'Mat22_i', u'RGBA', u'Mat33_c', u'Mat22_d', u'UInt32', u'Vec_cd', u'Mat22_c', u'Mat44_cd', u'Box2', u'Mat33_i', u'Mat22_cd', u'Vec3_cd', u'Float64', u'Vec4_d', u'Vec2_cd', u'UInt8', u'Mat33_d', u'Mat44_c', u'Mat44_d', u'Vec4_cd', u'UInt64', u'Mat33_cd', u'Mat44', u'Ray', u'Mat_d', u'RotationOrder', u'Color', u'Mat44_i', u'Vec4_c', u'Vec_c', u'Scalar', u'Mat33', u'Vec2', u'Vec3', u'Vec_d', u'Mat22', u'Vec_i', u'SInt32']")
        #todo add extension owner to Function&Object
        # klObject = klEnv.getGlobalNamespace().getObject('Foo')
        # self.assertEqual(klObject.getName(), 'Foo')

if __name__ == '__main__':
    unittest.main()
