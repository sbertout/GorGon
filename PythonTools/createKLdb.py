#!/usr/bin/env python

import os, argparse
from GorGon.KLWrapper.KLCodeEnv import KLCodeEnv
from GorGon.KLWrapper.KLDatabase import KLDatabase
from GorGon.Utils.coloredString import ColoredString

def processExtension(klExtensionName, klEnv, outputPath):
    klExtension = KLDatabase.loadExtension(klExtensionName, klEnv, outputPath)
    if klExtension is None:
        print "Something wrong with", ColoredString.Red(klExtensionName)

def main(args):
    klEnv = KLCodeEnv()
    klExtensionName = args.extension
    klEnv.parseSourceCode('require {};'.format(klExtensionName))
    klExtensionNames = klEnv.getExtensionNames()
    for klExtensionName in klExtensionNames:
        if klEnv.isRTExtension(klExtensionName):
            continue
        print 'Create KL database for', klExtensionName
        processExtension(klExtensionName, klEnv, args.output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create KL database')
    parser.add_argument('-e', '--extension', action="store", help='extension name')
    parser.add_argument('-o', '--output', action="store", help='output folder')
    args = parser.parse_args()
    main(args)
