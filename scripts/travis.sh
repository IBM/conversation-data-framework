#!/bin/sh

export API_KEY=AKCp5aU5jWcMLvD2ViDN3jV2dtitVbrg2cq1aftQTUXCyGdAc3DjWXBemYFsuduFsAhnpcJ8o
export WA_PASSWORD=ptFbCMZ2hCC1
export WA_USERNAME=02045182-1793-440c-b28c-7da07dca3117
export WA_WORKSPACE_ID_MASTER=4a64f694-0608-4e38-8ccc-eba2dcd30c7e
export WA_WORKSPACE_ID_TEST=f2e3f277-61a3-40d2-92f9-c3c77f34fb31
export TRAVIS_BRANCH=local
export TRAVIS_BUILD_NUMBER=2

stopIfFailed() 
{
    if [ "$1" -ne "0" ]; then
        echo "--------------------------------------------------------------------------------";
echo "-- Previous command failed, stop the build!";
echo "--------------------------------------------------------------------------------";
        exit 2
    fi
}

echo "--------------------------------------------------------------------------------";
echo "-- Dialog, intents from XLS to XML, CSV";
echo "--------------------------------------------------------------------------------";
mkdir -p tests/data/dialog/generated;
python scripts/dialog_xls2xml.py -x tests/data/dialog/xls/WEATHER-FAQ-CZ.xlsx -gd tests/data/dialog/generated -gi "tests/data/intents" -v;
stopIfFailed $?;
./scripts/artifactory-deploy.sh "tests/data/dialog/generated/*";

echo "--------------------------------------------------------------------------------";
echo "-- Dialog from XML to JSON";
echo "--------------------------------------------------------------------------------";
mkdir -p outputs;
python scripts/dialog_xml2json.py -dm tests/data/dialog/main.xml -of outputs -od dialog.json -s ../data_spec/dialog_schema.xml -v;
stopIfFailed $?;
./scripts/artifactory-deploy.sh outputs/dialog.json;

echo "--------------------------------------------------------------------------------";
echo "-- Entities from CSV to JSON";
echo "--------------------------------------------------------------------------------";
mkdir -p outputs
python scripts/entities_csv2json.py -ie tests/data/entities/ -oe entities.json -od outputs -v
stopIfFailed $?;
./scripts/artifactory-deploy.sh outputs/entities.json

echo "--------------------------------------------------------------------------------";
echo "-- Intents from CSV to JSON";
echo "--------------------------------------------------------------------------------";
mkdir -p outputs
python scripts/intents_csv2json.py -ii tests/data/intents/ -od outputs -oi intents.json -v
stopIfFailed $?;
./scripts/artifactory-deploy.sh outputs/intents.json

echo "--------------------------------------------------------------------------------";
echo "-- Compose workspace";
echo "--------------------------------------------------------------------------------";
python scripts/workspace_compose.py -of outputs -ow workspace.json -oe entities.json -od dialog.json -oi intents.json -v
stopIfFailed $?;
./scripts/artifactory-deploy.sh outputs/workspace.json

echo "--------------------------------------------------------------------------------";
echo "-- Decompose workspace";
echo "--------------------------------------------------------------------------------";
python scripts/workspace_decompose.py outputs/workspace.json -i outputs/intentsOut.json -e outputs/entitiesOut.json -d outputs/dialogOut.json -v
stopIfFailed $?;
./scripts/artifactory-deploy.sh outputs/intentsOut.json
./scripts/artifactory-deploy.sh outputs/entitiesOut.json
./scripts/artifactory-deploy.sh outputs/dialogOut.json

echo "--------------------------------------------------------------------------------";
echo "-- Intents from JSON to CSV";
echo "--------------------------------------------------------------------------------";
mkdir -p outputs/intents
python scripts/intents_json2csv.py outputs/intentsOut.json outputs/intents/ -v
stopIfFailed $?;
./scripts/artifactory-deploy.sh "outputs/intents/*";

echo "--------------------------------------------------------------------------------";
echo "-- Entities from JSON to CSV";
echo "--------------------------------------------------------------------------------";
mkdir -p outputs/entities
python scripts/entities_json2csv.py outputs/entitiesOut.json outputs/entities -v
stopIfFailed $?;
./scripts/artifactory-deploy.sh "outputs/entities/*";

echo "--------------------------------------------------------------------------------";
echo "-- Dialog from JSON to XML";
echo "--------------------------------------------------------------------------------";
mkdir -p outputs/dialog
python scripts/dialog_json2xml.py outputs/dialogOut.json -d outputs/dialog/ -v
stopIfFailed $?;
./scripts/artifactory-deploy.sh "outputs/dialog/*";

echo "--------------------------------------------------------------------------------";
echo "-- Deploy test workspace";
echo "--------------------------------------------------------------------------------";
python scripts/workspace_deploy.py -of outputs -ow workspace.json -c tests/test.cfg -v -cn $WA_USERNAME -cp $WA_PASSWORD -cid $WA_WORKSPACE_ID_TEST
stopIfFailed $?;

echo "--------------------------------------------------------------------------------";
echo "-- Test workspace";
echo "--------------------------------------------------------------------------------";
# TODO Get rid of this when workspace_test.py allows cmd params
cp tests/test.cfg tests/tmp.cfg;
echo "username = ${WA_USERNAME}" >> tests/tmp.cfg;
echo "password = ${WA_PASSWORD}" >> tests/tmp.cfg;
echo "workspace_id = ${WA_WORKSPACE_ID_TEST}" >> tests/tmp.cfg;
mkdir -p outputs/dialog
python scripts/workspace_test.py tests/tmp.cfg tests/test_more_outputs.test outputs/test_more_outputs.out -v
stopIfFailed $?;
./scripts/artifactory-deploy.sh outputs/test_more_outputs.out
rm -f tests/tmp.cfg;

echo "--------------------------------------------------------------------------------";
echo "-- Evaluate tests";
echo "--------------------------------------------------------------------------------";
python scripts/evaluate_tests.py tests/test_more_outputs.test outputs/test_more_outputs.out -o outputs/test_more_outputs.junit.xml
stopIfFailed $?;
./scripts/artifactory-deploy.sh outputs/test_more_outputs.junit.xml

echo "--------------------------------------------------------------------------------";
echo "-- Deploy master workspace";
echo "--------------------------------------------------------------------------------";
python scripts/workspace_deploy.py -of outputs -ow workspace.json -c tests/test.cfg -v -cn $WA_USERNAME -cp $WA_PASSWORD -cid $WA_WORKSPACE_ID_MASTER
stopIfFailed $?;

