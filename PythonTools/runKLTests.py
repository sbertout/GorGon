import os, sys, argparse, json, shutil, collections
import FabricEngine.Core as FECore
from subprocess import Popen, PIPE, STDOUT
from GorGon.Utils import ColoredString

testRootDir = '.kltest'

class KLObject:
    def __init__(self, name, parentObjectName):
        self.name = name
        self.parentObjectNames = parentObjectName
        self.methods = []
    def addMethod(self, methodName):
        self.methods.append(methodName)
    def getMethods(self):
        return self.methods
    def getTestMethods(self):
        testMethods = []
        for method in self.methods:
            if method.startswith('test'): testMethods.append(method)
        testMethods.sort()
        return testMethods
    def inheritsFromTestCase(self, klObjects):
        inheritsFromTestCase = 'CCTestCase' in self.parentObjectNames
        if inheritsFromTestCase == False:
            for parentObjectName in self.parentObjectNames:
                if parentObjectName in klObjects and klObjects[parentObjectName].inheritsFromTestCase(klObjects):
                    inheritsFromTestCase = True
        return inheritsFromTestCase
    def canBeTested(self, klObjects):
        inheritsFromTestCase = self.inheritsFromTestCase(klObjects)
        if inheritsFromTestCase == False:
            return False
        nbTestMethod = 0
        for method in self.methods:
            if str(method.lower()).startswith('test'): nbTestMethod += 1
        return nbTestMethod > 0

def rmTestRootDir():
    if os.path.exists(testRootDir): 
        shutil.rmtree(testRootDir, ignore_errors=True)

def initTestRootDir():
    rmTestRootDir()
    os.makedirs(testRootDir)

def findKLFiles(rootDir, mask):
    klFiles = []
    for dirName, subdirList, fileList in os.walk(rootDir):
        for fname in fileList:
            klFile = os.path.join(dirName, fname)
            lfname = fname.lower()
            if lfname.endswith('.kl'):
                if mask != '' and (mask not in klFile.lower()):
                    continue
                klFiles.append(klFile)
    return klFiles

def generateKLFilesToTest(klFiles, returnBool=True, verbose=False):
    klTestFiles = []
    c = FECore.createClient()
    for klFile in klFiles:
        file = open(klFile, 'r')
        sourceCode = file.read()
        file.close()
        ast = c.getKLJSONAST('AST.kl', sourceCode, False)
        data = json.loads(ast.getStringCString())['ast']
        data = data[0]['globalList']

        klObjects = {}
        for elementList in data:
            type = elementList['type']
            if type == 'ASTObjectDecl':
                objectName = elementList['name']
                parentObjectName = [] if 'parentsAndInterfaces' not in elementList else elementList['parentsAndInterfaces']
                klObjects[objectName] = KLObject(objectName, parentObjectName)
            elif type == 'MethodOpImpl':
                klObjects[elementList['thisType']].addMethod(elementList['name'])    

        ordererdKlObjects = collections.OrderedDict(sorted(klObjects.items(), key=lambda t: t[0]))
        ignoreThisTest = True
        for klObjectName in ordererdKlObjects:
            klObject = ordererdKlObjects[klObjectName]
            if klObject.canBeTested(ordererdKlObjects):
                ignoreThisTest = False
        if ignoreThisTest: continue

        klTmpFilePrefix = testRootDir + '/kltest_'
        newFileName = klTmpFilePrefix + klFile.replace('/', '_').replace('.', '_') + ".kl"
        newFile = open(newFileName, 'w')
        newFile.write(sourceCode)

        newFile.write('\n\n')
        newFile.write('require GGtestFramework;\n')
        newFile.write('require GGcore;\n')
        if returnBool:
            newFile.write('Boolean operator entry() { \n')
        else:
            newFile.write('operator entry() { \n')
        newFile.write('\tSize testCount = 0; Size invalidTestCount = 0; report("[GG_KLTEST] Executing " + AnsiEscapeCode_Blue("%s") + ".."); \n' % os.path.splitext(klFile)[0])
        for klObjectName in ordererdKlObjects:
            klObject = ordererdKlObjects[klObjectName]
            if klObject.canBeTested(ordererdKlObjects):
                newFile.write('\n{\n\treport("[GG_KLTEST] - %s:");\n' % (klObjectName))
                newFile.write('\t%s tst(); tst.setOutFile("%s");\n' % (klObjectName, klFile.replace('.kl', '.out')))
                # if verbose:
                #     newFile.write('tst.verbose();')
                for method in klObject.getTestMethods():
                    newFile.write('\treport("[GG_KLTEST]   - executing.. " + AnsiEscapeCode_Blue("%s"));\n' % (method))
                    newFile.write('\ttst.setTestFuncName("%s").setUp().%s().tearDown();\n' % (method, method))
                newFile.write('\tinvalidTestCount += tst.isValid() ? 0 : 1; testCount ++;\n}\n')
        newFile.write('\n\tif (invalidTestCount == 0) report("[GG_KLTEST] Ran " + testCount + " test case(s).. OK!");\n')
        newFile.write('\telse report("[GG_KLTEST]" + AnsiEscapeCode_Red("Failed test case(s) " + invalidTestCount + "/" + testCount));\n')
        if returnBool:
            newFile.write('\treturn invalidTestCount == 0; \n')
        newFile.write('}')
        newFile.close()
        klTestFiles.append(newFileName)
    return klTestFiles

def execKL(klFile):
    print '[GG_PYTEST] Testing ' + klFile
    output = Popen('kl ' + klFile, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()
    if args.quiet == False: print output
    errorCount = output.count('KL stack trace:')
    if errorCount > 0:
        if args.quiet: print output
        print "[GG_PYTEST] " + ColoredString.Red('%s Error(s) found!!\n' % errorCount)
    return errorCount > 0#    returnCode = 1

parser = argparse.ArgumentParser(description='Run KL test files')
parser.add_argument('-q', '--quiet', action="store_true", default=False, help='quiet mode')
parser.add_argument('-c', '--consolidate', action="store_true", default=False, help='consolidate KL files into a master one to run single kl command')
parser.add_argument('-d', '--debugMode', action="store_true", default=False, help='Debug mode: generated kl files wont be deleted')
parser.add_argument('-m', '--mask', action="store", default='', help='mask KL test files')
parser.add_argument('-r', '--rootDir', action="store", default='.', help='search for KL test files from the specified rootDir')
args = parser.parse_args()

returnCode = 0
initTestRootDir()
klFiles = findKLFiles(args.rootDir, args.mask)
if args.consolidate:
    klFilesToTest = generateKLFilesToTest(klFiles, returnBool=True, verbose=not args.quiet)
    consolidatedKLFileName = testRootDir + '/kltest_consolidated.kl'
    consolidatedKLFile = open(consolidatedKLFileName, 'w')
    funcs = []
    for klFileToTest in klFilesToTest:
        klFileBase = os.path.splitext(os.path.basename(klFileToTest))[0]
        funcs.append(klFileBase)
        klFile = open(klFileToTest, 'r')
        klFileContent = klFile.read()
        klFile.close()
        klFileContent = klFileContent.replace('operator entry', klFileBase)
        consolidatedKLFile.write(klFileContent + '\n\n')
    consolidatedKLFile.write('operator entry() {\n')
    consolidatedKLFile.write('Boolean stillOK = true;\n')
    for func in funcs:
        consolidatedKLFile.write('\tif (stillOK) {stillOK = %s();}\n' % func)
    consolidatedKLFile.write('}\n')
    consolidatedKLFile.close()
    returnCode |= execKL(consolidatedKLFileName)
else:
    klFilesToTest = generateKLFilesToTest(klFiles, returnBool=False, verbose=not args.quiet)
    for klFileToTest in klFilesToTest:
        returnCode |= execKL(klFileToTest)
if args.debugMode == False: rmTestRootDir()
if args.quiet and returnCode == 0: print '[GG_PYTEST] OK!'
sys.exit(returnCode)
