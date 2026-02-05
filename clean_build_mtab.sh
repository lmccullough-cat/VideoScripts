#!/bin/bash
rm -r -f build
mkdir build
pushd build
"/Users/luke.mccullough/Qt/5.12.5/clang_64/bin/qmake" /Users/luke.mccullough/code/SBGSource/matchtrackeramericanfootball.pro -spec macx-clang CONFIG+=debug CONFIG+=qml_debug CONFIG+=sdk_no_version_check 
"/usr/bin/make" -f ./Makefile qmake_all
"/usr/bin/make" -j16
popd
