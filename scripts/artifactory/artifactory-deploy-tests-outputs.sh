#!/bin/sh

for folder in `find ci -name outputs`;
do
    echo "Deploying ${folder} to Artifactory";
    for file in `find ${folder} -name '*'`;
    do
        ./scripts/artifactory/artifactory-deploy.sh ${file};
    done
done

