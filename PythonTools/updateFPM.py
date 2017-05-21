import os, argparse, json

parser = argparse.ArgumentParser(description='Create FPM json files recursively from folder containing KL files')
parser.add_argument('-o', '--outputFPM', action="store", default='', help='FPM json file to generate')
parser.add_argument('-r', '--rootFolder', action="store", default='.', help='Root folder where KL files are located')
parser.add_argument('-v', '--version', action="store", default='.', help='Version to set')
args = parser.parse_args()

jsonDict = {}
jsonDict['version'] = args.version

s = args.rootFolder.split('/')
klRootFolder = '/'.join(s[1:])

for root, dirs, files in os.walk(args.rootFolder):
    path = root.split(os.sep)
    for file in files:
        if 'code' not in jsonDict:
            jsonDict['code'] = []
        if os.path.splitext(file)[1] != '.kl':
            continue
        klFile = klRootFolder + os.path.join(root, file).replace(args.rootFolder, '')
        jsonDict['code'].append(klFile)

with open(args.outputFPM, 'w') as fp:
    json.dump(jsonDict, fp, indent=4)

print 'FPM json file', args.outputFPM, 'version', args.version, 'successfully generated!'
