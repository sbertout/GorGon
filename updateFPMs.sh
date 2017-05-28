#!/usr/bin/env bash

python PythonTools/updateFPM.py -r KLExtensions/all/ -o KLExtensions/GorGon_All.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/core/ -o KLExtensions/GorGon_Core.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/ecs/ -o KLExtensions/GorGon_ECS.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/image/ -o KLExtensions/GorGon_Image.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/import/ -o KLExtensions/GorGon_Import.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/maths/ -o KLExtensions/GorGon_Maths.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/raytracing/ -o KLExtensions/GorGon_Raytracing.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/raytracingTests/ -o KLExtensions/GorGon_RaytracingTests.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/rendering/ -o KLExtensions/GorGon_Rendering.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/scene/ -o KLExtensions/GorGon_Scene.fpm.json -v 0.1.0
python PythonTools/updateFPM.py -r KLExtensions/testFramework/ -o KLExtensions/GorGon_TestFramework.fpm.json -v 0.1.0
