#!/bin/bash

# Saner programming env: these switches turn some bugs into errors
set -o errexit -o pipefail -o noclobber -o nounset
# Argument parsing
while [[ "$#" -gt 0 ]]; do case $1 in
  -p|--project) project="$2"; shift;;
  -n|--name) name="$2"; shift;;
  -e|--env) env="$2"; shift;;
esac; shift; done

[ -n "${project-}" ] || (echo "Missing required argument '--project'" && exit 1)
[ -n "${name-}" ] || (echo "Missing required argument '--name'" && exit 1)
[ -n "${env-}" ] || (echo "Missing required argument '--env'" && exit 1)

echo "Building the docker image..."
gcloud builds submit ../api -t eu.gcr.io/${project}/${name} --project ${project}

echo "Deploying the image to Cloud Run..."
gcloud run deploy ${name} --image eu.gcr.io/${project}/${name} --region europe-west1

