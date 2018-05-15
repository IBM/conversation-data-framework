#!/bin/sh

stopIfFailed() {
    if (($? != 0)); then
        echo "Previous command failed, stop the build"
        exit(2)
    fi
}

echo "Dialog, intents from XLS to XML, CSV"
mkdir -p tests/data/dialog/generated
python scripts/dialog_xls2xml.py -x tests/data/dialog/xls/WEATHER-FAQ-CZ.xlsx -gd tests/data/dialog/generated -gi "tests/data/intents" -v
./scripts/artifactory-deploy.sh tests/data/dialog/generated/*
stopIfFailed()

echo "Dialog from XML to JSON"
mkdir -p outputs
python scripts/dialog_xml2json.py -dm tests/data/dialog/main.xml -of outputs -od dialog.json -s ../data_spec/dialog_schema.xml -v
./scripts/artifactory-deploy.sh outputs/dialog.json
stopIfFailed()

echo "Entities from CSV to JSON"
mkdir -p outputs
python scripts/entities_csv2json.py -ie tests/data/entities/ -oe entities.json -od outputs -v
./scripts/artifactory-deploy.sh outputs/entities.json
stopIfFailed()

echo "Intents from CSV to JSON"
mkdir -p outputs
python scripts/intents_csv2json.py -ii tests/data/intents/ -od outputs -oi intents.json -v
./scripts/artifactory-deploy.sh outputs/intents.json
stopIfFailed()

echo "Compose workspace"
python scripts/workspace_compose.py -of outputs -ow workspace.json -oe entities.json -od dialog.json -oi intents.json -v
./scripts/artifactory-deploy.sh outputs/workspace.json
stopIfFailed()

echo "Decompose workspace"
python scripts/workspace_decompose.py outputs/workspace.json -i outputs/intentsOut.json -e outputs/entitiesOut.json -d outputs/dialogOut.json -v
./scripts/artifactory-deploy.sh outputs/intentsOut.json
./scripts/artifactory-deploy.sh outputs/entitiesOut.json
./scripts/artifactory-deploy.sh outputs/dialogOut.json
stopIfFailed()

echo "Intents from JSON to CSV"
mkdir -p outputs/intents
python scripts/intents_json2csv.py outputs/intentsOut.json outputs/intents/ -v
./scripts/artifactory-deploy.sh outputs/intents/*
stopIfFailed()

echo "Entities from JSON to CSV"
mkdir -p outputs/entities
python scripts/entities_json2csv.py outputs/entitiesOut.json outputs/entities -v
./scripts/artifactory-deploy.sh outputs/entities/*
stopIfFailed()

echo "Dialog from JSON to XML"
mkdir -p outputs/dialog
python scripts/dialog_json2xml.py outputs/dialogOut.json -d outputs/dialog/ -v
./scripts/artifactory-deploy.sh outputs/dialog/*
stopIfFailed()

echo "Deploy test workspace"
python scripts/workspace_deploy.py -of outputs -ow workspace.json -c tests/test.cfg -v -cn $WA_USERNAME -cp $WA_PASSWORD -cid $WA_WORKSPACE_ID_TEST
stopIfFailed()

echo "Test workspace"
# TODO Get rid of this when workspace_test.py allows cmd params
echo "username = ${WA_USERNAME}" >> tests/test.cfg
echo "password = ${WA_PASSWORD}" >> tests/test.cfg
echo "workspace_id = ${WA_WORKSPACE_ID_TEST}" >> tests/test.cfg
mkdir -p outputs/dialog
python scripts/workspace_test.py tests/test.cfg tests/test_more_outputs.test outputs/test_more_outputs.out -v
./scripts/artifactory-deploy.sh outputs/test_more_outputs.out
stopIfFailed()

echo "Evaluate tests"
python scripts/evaluate_tests.py tests/test_more_outputs.test outputs/test_more_outputs.out -o outputs/test_more_outputs.junit.xml
./scripts/artifactory-deploy.sh outputs/test_more_outputs.junit.xml
stopIfFailed()

echo "Deploy master workspace"
python scripts/workspace_deploy.py -of outputs -ow workspace.json -c tests/test.cfg -v -cn $WA_USERNAME -cp $WA_PASSWORD -cid $WA_WORKSPACE_ID_MASTER
stopIfFailed()

