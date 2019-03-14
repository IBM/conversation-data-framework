#!/bin/sh

ZIP_NAME=outputs.zip

cd ./ci

for folder in `find . -name outputs`;
do
    echo "Adding ${folder} to ${ZIP_NAME}";
    zip -ru ${ZIP_NAME} ${folder};
done

ZIP_NUMBER=`zipinfo -1 outputs.zip | wc -l`

unzip ${ZIP_NAME} -d outputs/
ls -Rl outputs/

echo "Total number of files and folder in ${ZIP_NAME} is ${ZIP_NUMBER}"

cd ../
./scripts/artifactory/artifactory-deploy.sh ci/${ZIP_NAME}

