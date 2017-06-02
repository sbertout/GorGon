class KLExtension:

    def __init__(self, name):
        self.__name = name
        self.__extensionDependencies = []

    def addExtensionDependency(self, otherExtension):
        if otherExtension not in self.__extensionDependencies:
            self.__extensionDependencies.append(otherExtension)

    def getName(self):
        return self.__name

    def getExtensionDependencies(self):
        return self.__extensionDependencies