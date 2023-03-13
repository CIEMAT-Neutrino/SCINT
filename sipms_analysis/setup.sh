#!/bin/bash

if [ ! -d "../fit_data" ]; then
mkdir ../fit_data
fi

pip install --upgrade pip
pip3 install xlrd==1.2.0