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

## api
