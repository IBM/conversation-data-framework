#!/bin/sh

# Those variables is needed to be exported or set as environment variables
# export ARTIFACTORY_API_KEY=
# export ARTIFACTORY_KEEP_DAYS=
# export WA_PASSWORD=
# export WA_USERNAME=
# export WA_WORKSPACE_ID_DEVEL=
# export WA_WORKSPACE_ID_MASTER=
# export WA_WORKSPACE_ID_TEST=
# export TRAVIS_BRANCH=
# export TRAVIS_BUILD_NUMBER=
# export TRAVIS_PULL_REQUEST=
# export TRAVIS_EVENT_TYPE=

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
echo "-- Unit Testing";
echo "--------------------------------------------------------------------------------";

PYTHONPATH=./scripts:$PYTHONPATH pytest ci/unit_tests
stopIfFailed $?;

echo "--------------------------------------------------------------------------------";
echo "-- Testing conversion from JSON to XML and back again";
echo "--------------------------------------------------------------------------------";

mkdir -p outputs/test_dialog

for i in 1 2 3
do
    echo "--------------------------------------------------------------------------------";
    echo "-- Test-dialog $i from JSON to XML";
    echo "--------------------------------------------------------------------------------";
    python scripts/dialog_json2xml.py tests/test_data/dialog_$i.json  > outputs/test_dialog/dialog_$i.xml
    stopIfFailed $?;

    echo "--------------------------------------------------------------------------------";
    echo "-- Test-dialog $i from XML to JSON";
    echo "--------------------------------------------------------------------------------";
    python scripts/dialog_xml2json.py -dm outputs/test_dialog/dialog_$i.xml -of outputs/test_dialog -od dialog_$i.json -s ../data_spec/dialog_schema.xml -c "tests/data/build.cfg";
    stopIfFailed $?;

    echo "--------------------------------------------------------------------------------";
    echo "-- Compare test-dialog $i";
    echo "--------------------------------------------------------------------------------";
    python scripts/compare_dialogs.py tests/test_data/dialog_$i.json outputs/test_dialog/dialog_$i.json -v;
    stopIfFailed $?;
done

./ci/artifactory-deploy.sh "outputs/test_dialog/*";

echo "--------------------------------------------------------------------------------";
echo "-- Dialog, intents from XLS to XML, CSV";
echo "--------------------------------------------------------------------------------";
mkdir -p "tests/data/dialog/g_dialogs";
python scripts/dialog_xls2xml.py -x "tests/data/xls/E_EN_master.xlsx" -gd "tests/data/dialog/g_dialogs" -gi "tests/data/intents" -ge "tests/data/entities" -v;
stopIfFailed $?;
python scripts/dialog_xls2xml.py -x "tests/data/xls/E_EN_tests.xlsx" -gd "tests/data/dialog/g_dialogs" -gi "tests/data/intents" -ge "tests/data/entities" -v;
stopIfFailed $?;
python scripts/dialog_xls2xml.py -x "tests/data/xls/E_EN_T2C_authoring.xlsx" -gd "tests/data/dialog/g_dialogs" -gi "tests/data/intents" -ge "tests/data/entities" -v;
stopIfFailed $?;
python scripts/dialog_xls2xml.py -x "tests/data/xls/E_CZ_T2C_authoring.xlsx" -gd "tests/data/dialog/g_dialogs" -gi "tests/data/intents" -ge "tests/data/entities" -v;
stopIfFailed $?;
./ci/artifactory-deploy.sh "tests/data/dialog/g_dialogs/*";

echo "--------------------------------------------------------------------------------";
echo "-- Testing entities in T2C (@entity:(<x>) blocks)";
echo "--------------------------------------------------------------------------------";

echo "TEST @entity:(<x>) blocks"
grep "\#CO_JE.*@PREDMET:(Z.vada)" tests/data/dialog/g_dialogs/cond_x_test.xml
stopIfFailed $?;
grep "\#CO_JE.*@PREDMET:(V.stra.n. stav)" tests/data/dialog/g_dialogs/cond_x_test.xml
stopIfFailed $?;
grep "\#CO_JE.*@PREDMET:(Vyrovn.vac. trh)" tests/data/dialog/g_dialogs/cond_x_test.xml
stopIfFailed $?;
echo "TEST buttons in @entity:(<x>) blocks"
grep "\#CO_JE.*@PREDMET:(Buttons do not belong here)" tests/data/dialog/g_dialogs/cond_x_test.xml
stopIfFailed $?;

echo "--------------------------------------------------------------------------------";
echo "-- Dialog from XML to JSON";
echo "--------------------------------------------------------------------------------";
mkdir -p outputs;
python scripts/dialog_xml2json.py -dm tests/data/dialog/main.xml -of outputs -od dialog.json -s ../data_spec/dialog_schema.xml -c "tests/data/build.cfg" -v;
stopIfFailed $?;
./ci/artifactory-deploy.sh outputs/dialog.json;

echo "--------------------------------------------------------------------------------";
echo "-- Entities from CSV to JSON";
echo "--------------------------------------------------------------------------------";
mkdir -p outputs
python scripts/entities_csv2json.py -ie tests/data/entities/ -oe entities.json -od outputs -v
stopIfFailed $?;
./ci/artifactory-deploy.sh outputs/entities.json

echo "--------------------------------------------------------------------------------";
echo "-- Intents from CSV to JSON";
echo "--------------------------------------------------------------------------------";
mkdir -p outputs
python scripts/intents_csv2json.py -ii tests/data/intents/ -od outputs -oi intents.json -v
stopIfFailed $?;
./ci/artifactory-deploy.sh outputs/intents.json

echo "--------------------------------------------------------------------------------";
echo "-- Compose workspace";
echo "--------------------------------------------------------------------------------";
python scripts/workspace_compose.py -of outputs -ow workspace.json -oe entities.json -od dialog.json -oi intents.json -v
stopIfFailed $?;
./ci/artifactory-deploy.sh outputs/workspace.json

echo "--------------------------------------------------------------------------------";
echo "-- Decompose workspace";
echo "--------------------------------------------------------------------------------";
python scripts/workspace_decompose.py outputs/workspace.json -i outputs/intentsOut.json -e outputs/entitiesOut.json -d outputs/dialogOut.json -v
stopIfFailed $?;
./ci/artifactory-deploy.sh outputs/intentsOut.json
./ci/artifactory-deploy.sh outputs/entitiesOut.json
./ci/artifactory-deploy.sh outputs/dialogOut.json

echo "--------------------------------------------------------------------------------";
echo "-- Intents from JSON to CSV";
echo "--------------------------------------------------------------------------------";
mkdir -p outputs/intents
python scripts/intents_json2csv.py outputs/intentsOut.json outputs/intents/ -v
stopIfFailed $?;
./ci/artifactory-deploy.sh "outputs/intents/*";

echo "--------------------------------------------------------------------------------";
echo "-- Entities from JSON to CSV";
echo "--------------------------------------------------------------------------------";
mkdir -p outputs/entities
python scripts/entities_json2csv.py outputs/entitiesOut.json outputs/entities -v
stopIfFailed $?;
./ci/artifactory-deploy.sh "outputs/entities/*";

echo "--------------------------------------------------------------------------------";
echo "-- Dialog from JSON to XML";
echo "--------------------------------------------------------------------------------";
mkdir -p outputs/dialog
python scripts/dialog_json2xml.py outputs/dialogOut.json -d outputs/dialog/ -v
stopIfFailed $?;
./ci/artifactory-deploy.sh "outputs/dialog/*";

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
python scripts/workspace_test.py tests/test_more_outputs.test outputs/test_more_outputs.out -c tests/tmp.cfg -v
stopIfFailed $?;
./ci/artifactory-deploy.sh outputs/test_more_outputs.out
rm -f tests/tmp.cfg;

echo "--------------------------------------------------------------------------------";
echo "-- Evaluate tests";
echo "--------------------------------------------------------------------------------";
python scripts/evaluate_tests.py tests/test_more_outputs.test outputs/test_more_outputs.out -o outputs/test_more_outputs.junit.xml
stopIfFailed $?;
./ci/artifactory-deploy.sh outputs/test_more_outputs.junit.xml

if [ "$TRAVIS_BRANCH" = "master" -a "$TRAVIS_PULL_REQUEST" = "false" ]; then
    echo "--------------------------------------------------------------------------------";
    echo "-- Deploy master workspace";
    echo "--------------------------------------------------------------------------------";
    python scripts/workspace_deploy.py -of outputs -ow workspace.json -c tests/test.cfg -v -cn $WA_USERNAME -cp $WA_PASSWORD -cid $WA_WORKSPACE_ID_MASTER
    stopIfFailed $?;
elif [ "$TRAVIS_BRANCH" = "devel" -a "$TRAVIS_PULL_REQUEST" = "false" ]; then
    echo "--------------------------------------------------------------------------------";
    echo "-- Deploy devel workspace";
    echo "--------------------------------------------------------------------------------";
    python scripts/workspace_deploy.py -of outputs -ow workspace.json -c tests/test.cfg -v -cn $WA_USERNAME -cp $WA_PASSWORD -cid $WA_WORKSPACE_ID_DEVEL
    stopIfFailed $?;
fi

if [ "$TRAVIS_BRANCH" = "devel" -a "$TRAVIS_PULL_REQUEST" = "false" -a "$TRAVIS_EVENT_TYPE" = "cron" ]; then
    echo "--------------------------------------------------------------------------------";
    echo "-- Cleanup Artifactory";
    echo "--------------------------------------------------------------------------------";
    ./ci/artifactory-cleanup.sh
fi
