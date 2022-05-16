# Housing area woz-price regressor

This repo contains the code to train a linear-regression model on housing area & family composition
data, and then serve the trained model as an API (locally in a docker container, or by deploying to
Cloud Run on GCP). The repo contains five directories: 'api',
'data', 'eda', 'results', and 'training'. 

The data directory contains the necessary datasets. The eda directory contains a notebook that was
used to perform exploratory data analysis and model experimentation. The notebook also contains
extensive comments that detail why certain choices where made with respect to the model being 
served.

The training directory contains a 'train_model.py' script that can be run. This will result in
a trained LR model & some metrics being saved to the results & api directory. 

The api directory contains the necessary files to deploy an API to serve the trained model either
locally in a docker container, or deploy it to Cloud Run on GCP. 

More detail on the contents of the directories is provided below. At the end of this file is 
a quick setup guide to deploy the model in a docker container. 

## eda
This notebook should be run cell for cell. The plots generated together with the comments will
explore the data and experiment with features & models. 

## training
The train_model.py script can be run from the root directory like so:

`` python training/train_model.py --model_version test_model --test_ratio 0.2 --deploy True``

If the `deploy` parameter is set to true, the model and encoder will be saved in the api/app directory.
The model, encoder, and metrics will also be saved to the results directory.

## api
The api directory contains an app directory which has all the core logic to serve the trained model.

To package the api into a docker container, the directory conatins a Dockerfile and a docker-compose.yml file which can be run.

The api directory also contains a build.py script which can be run to easily build and push the docker image to GCP,
and deploy the API to a Cloud Run instance. Take note that the correct/ relevant GCP project is defined in the ``build.py`` script.

## Quick set up guide

First run the ``train_model.py`` script, for example: `` python training/train_model.py --model_version test_model --test_ratio 0.2 --deploy True``

Then you can choose to:
#### Run the API without a docker container
1. cd to ``api/app``
2. run the command: ``uvicorn main:app``
3. Go to http://127.0.0.1:8000/docs in a browser to get a prediction. 

#### Run the API by building a docker container locally
1. cd to ``api``
2. Run the command ``docker-compose build``
3. Got to http://localhost:5001/docs in a browser to get a prediction.

#### Run the API in Cloud Run ( need to have an account on GCP)
1. Make sure you have the Google cloud SDK installed & set up.
2. Make sure to define the correct GCP projects in the ``build.py`` script.
3. cd to ``api``
4. Run the command with your chosen environment = ENV: ``python build.py --env {ENV}``. Note: this command launches a bash script. 
5. Go to Cloud Run in GCP to find the URL at which the API is hosted. 

