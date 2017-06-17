from KLNamespace import KLNamespace

class KLExtension:

    def __init__(self, name):
        self.__name = name
        self.__globalNamespace = KLNamespace('global')
        self.__namespaces = {}
        self.__extensionDependencies = []

    def addExtensionDependency(self, otherExtension):
        if otherExtension not in self.__extensionDependencies:
            self.__extensionDependencies.append(otherExtension)

    def getName(self):
        return self.__name

    def getExtensionDependencies(self):
        return self.__extensionDependencies

    def getGlobalNamespace(self):
        return self.__globalNamespace

    def getNamespaceCount(self):
        return len(self.__namespaces)

    def getNamespace(self, name, addNamespaceIfMissing=False):
        if name == 'global': # todo use better unique name! <GLOBAL>
            return self.__globalNamespace
        if addNamespaceIfMissing:
            if name not in self.getNamespaceNames():
                self.addNamespace(name)
        else:
            if name not in self.__namespaces:
                return None
        return self.__namespaces[name]

    def addNamespace(self, namespaceName):
        namespace = KLNamespace(namespaceName)
        self.__namespaces[namespaceName] = namespace
        return namespace

    def getNamespaceNames(self):
        return self.__namespaces.keys()