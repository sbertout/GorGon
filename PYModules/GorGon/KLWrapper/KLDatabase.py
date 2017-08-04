import os
from KLCodeEnv import KLCodeEnv
from KLExtension import KLExtension

class KLDatabase:

    @staticmethod
    def loadExtension(klExtensionName, klEnv = None, outputPath = ''):
        kldb_filepath = (outputPath if outputPath is not None else '.klDB/') + klExtensionName + '.klDB.yaml'

        if not os.path.exists(kldb_filepath):
            if klEnv is None: klEnv = KLCodeEnv()
            klEnv.parseSourceCode('require {};'.format(klExtensionName))
            klExtension = klEnv.getExtension(klExtensionName)
            klExtension.toYamlFile(kldb_filepath)
            return klExtension
        return KLExtension.fromYamlFile(kldb_filepath)
