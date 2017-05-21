#!/usr/bin/env bash

python PythonTools/updateFPM.py -r KLExtensions/all/ -o KLExtensions/GGall.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/core/ -o KLExtensions/GGcore.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/ecs/ -o KLExtensions/GGecs.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/image/ -o KLExtensions/GGimage.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/import/ -o KLExtensions/GGimport.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/maths/ -o KLExtensions/GGmaths.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/raytracing/ -o KLExtensions/GGraytracing.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/raytracingTests/ -o KLExtensions/GGraytracingTests.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/rendering/ -o KLExtensions/GGrendering.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/scene/ -o KLExtensions/GGscene.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/testFramework/ -o KLExtensions/GGtestFramework.fpm.json -v 0.1.0
