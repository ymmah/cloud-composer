#!/usr/bin/env bash
MY_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR=${MY_DIR}/..

TMP_DIR=$(mktemp -d)

REPOSITORY_NAME=test-o2a-repo
PROJECT_ID=$(gcloud config list --format 'value(core.project)')
REPO_URL="https://source.developers.google.com/p/${PROJECT_ID}/r/${REPOSITORY_NAME}"

echo '#!/bin/sh\n' >> ${TMP_DIR}/script.sh
echo 'echo "Hello, world! The time is $(date)."\n' >> ${TMP_DIR}/script.sh
chmod 555 ${TMP_DIR}/script.sh

gcloud source repos create ${REPOSITORY_NAME}
pushd $TMP_DIR
git init
git config user.email bot@example.com
git config user.name system-test
git config credential.https://source.developers.google.com.helper gcloud.sh
git add .
git commit -m "Initial commit"

git remote add origin ${REPO_URL}
git push origin master
echo "Repo created"
echo "Repo URL: ${REPO_URL}"
popd
