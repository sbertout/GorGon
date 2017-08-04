import os, sys, unittest
from GorGon.KLWrapper.KLCodeEnv import KLCodeEnv
from GorGon.KLWrapper.KLDatabase import KLDatabase


class KLDBTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(KLDBTests, self).__init__(*args, **kwargs)

    def test_GorGon_Core(self):
        gorgonPyTestsPath = os.path.expandvars('$GORGON_PYTESTS_PATH')
        yamlPath = gorgonPyTestsPath + '/_out/'
        extensionName = 'GorGon_Core'
        yamlFilePath = yamlPath + extensionName + '.klDB.yaml'
        if os.path.exists(yamlFilePath):
            os.remove(yamlFilePath)
        klExt = KLDatabase.loadExtension(extensionName, outputPath = yamlPath)
        self.assertFalse(klExt is None)
        klExt2 = KLDatabase.loadExtension(extensionName, outputPath = yamlPath)
        self.assertFalse(klExt2 is None)
        self.assertEquals(klExt.getName(), klExt2.getName())
        self.assertEquals(klExt.getExtensionDependencies(), klExt2.getExtensionDependencies())
        self.assertEquals(klExt.getNamespaceNames(), klExt2.getNamespaceNames())


if __name__ == '__main__':
    unittest.main()
