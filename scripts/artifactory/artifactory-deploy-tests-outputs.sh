#!/bin/sh

TAR_NAME=outputs.tar
TAR_GZ_NAME=${TAR_NAME}.gz

cd ./ci

for folder in `find . -name outputs`;
do
    if [ -e "${TAR_NAME}" ]
    then
        echo "Adding ${folder} to ${TAR_NAME}";
        tar -uvf ${TAR_NAME} ${folder};
    else
        echo "Creating ${TAR_NAME} from ${folder}";
        tar -cvf ${TAR_NAME} ${folder};
    fi
done

gzip ${TAR_NAME}

cd ../
./scripts/artifactory/artifactory-deploy.sh ci/${TAR_GZ_NAME}

