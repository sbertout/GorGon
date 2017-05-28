#!/usr/bin/env bash

python PythonTools/codegenKLFile.py -t KLExtensions/maths/assert.tkl -e GorGon::Maths -c Vec3,Quat,Xfo -o KLExtensions/maths/assert.kl
python PythonTools/codegenKLFile.py -t KLExtensions/scene/_init.tkl -e GorGon::Scene -c MaterialSet,CCTextureSet -o KLExtensions/scene/_init.kl
