#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
GORGON_PYMODULES_PATH="$DIR/PYModules"
GORGON_KLEXTENSIONS_PATH="$DIR/KLExtensions"
GORGON_CANVASPRESETS_PATH="$DIR/CanvasPresets"
GORGON_GENERATEDCANVASPRESETS_PATH="$DIR/GeneratedCanvasPresets"

echo "Patching GorGon.."
FABRIC_EXTS_PATH=$FABRIC_EXTS_PATH:$GORGON_KLEXTENSIONS_PATH
FABRIC_DFG_PATH=$FABRIC_DFG_PATH:$GORGON_CANVASPRESETS_PATH
FABRIC_DFG_PATH=$FABRIC_DFG_PATH:$GORGON_GENERATEDCANVASPRESETS_PATH
PYTHONPATH=$PYTHONPATH:$GORGON_PYMODULES_PATH


echo "Adding klc function.."
function klc()
{
  echo "KL Compiling.. "$1
  rm -f /tmp/klc$1.kl
  echo 'require '$1' ; operator entry ( ) {}' >> /tmp/klc$1.kl
  kl /tmp/klc$1.kl
}
