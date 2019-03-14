#!/bin/sh

ZIP_NAME=outputs.zip

cd ./ci

for folder in `find . -name outputs`;
do
    echo "Adding ${folder} to ${ZIP_NAME}";
    zip -ru ${ZIP_NAME} ${folder}
done

cd ../
./scripts/artifactory/artifactory-deploy.sh ci/${ZIP_NAME}

