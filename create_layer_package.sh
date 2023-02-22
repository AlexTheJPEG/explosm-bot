#!/bin/bash

touch layer.zip && rm layer.zip
poetry export --without-hashes > requirements.txt
pip install --upgrade -t packages/python -r requirements.txt
cd packages
zip -r ../layer.zip .
cd ..
rm -r packages
rm requirements.txt