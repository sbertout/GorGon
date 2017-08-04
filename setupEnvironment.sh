#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

GORGON_PATH="$DIR"
GORGON_PYMODULES_PATH="$DIR/PYModules"
GORGON_PYTESTS_PATH="$DIR/PYTests"
GORGON_KLEXTENSIONS_PATH="$DIR/KLExtensions"
GORGON_CANVASPRESETS_PATH="$DIR/CanvasPresets"
GORGON_GENERATEDCANVASPRESETS_PATH="$DIR/GeneratedCanvasPresets"

export GORGON_PATH
export GORGON_PYMODULES_PATH
export GORGON_PYTESTS_PATH
export GORGON_KLEXTENSIONS_PATH
export GORGON_CANVASPRESETS_PATH
export GORGON_GENERATEDCANVASPRESETS_PATH

echo "Patched GorGon."
FABRIC_EXTS_PATH=$FABRIC_EXTS_PATH:$GORGON_KLEXTENSIONS_PATH
FABRIC_DFG_PATH=$FABRIC_DFG_PATH:$GORGON_CANVASPRESETS_PATH
FABRIC_DFG_PATH=$FABRIC_DFG_PATH:$GORGON_GENERATEDCANVASPRESETS_PATH
PYTHONPATH=$PYTHONPATH:$GORGON_PYMODULES_PATH


echo "Adding klc bash function to environment"
function klc()
{
  echo "KL Compiling.. "$1
  rm -f /tmp/klc$1.kl
  echo 'require '$1' ; operator entry ( ) {}' >> /tmp/klc$1.kl
  kl /tmp/klc$1.kl
}

echo 'now launch pyCharm with:'
echo '/Applications/PyCharm\ CE.app/Contents/MacOS/pycharm&'
echo ''
