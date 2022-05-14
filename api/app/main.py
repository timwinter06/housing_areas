""" This file creates an API with fastapi to serve the trained model. """
import os
import pickle
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel


# Load model
with open(os.path.join('model'), 'rb') as file:
    model = pickle.load(file)

# Load encoder
with open(os.path.join('encoder'), 'rb') as file:
    ohc = pickle.load(file)


# Define object we classify
class HouseAreaFeatures(BaseModel):
    """ Defines input types for API post request."""
    single: float
    married_no_kids: float
    not_marred_no_kids: float
    married_w_kids: float
    not_married_w_kids: float
    single_parent: float
    other: float
    total: float
    area_code: str


def encode_area(ohc, df):
    """ Encodes the area_code column of the data-frame with
    pre-fitted OneHotEncoder.
    Args:
        ohc (OneHotEncoder): As fitted on the train-set.
        df (pd.DataFrame): Datatframe with area_code column to encode.
    Returns:
        pd.DataFrame with encoded area_code
    """
    ohe = ohc.transform(df.area_code.values.reshape(-1, 1)).toarray()
    df_one_hot = pd.DataFrame(ohe, columns=ohc.categories_[0])
    df = pd.concat([df.reset_index(drop=True), df_one_hot], axis=1)
    df = df.drop('area_code', axis=1)
    return df


def get_predictions(input_data: HouseAreaFeatures):
    """ Serves predictions for price of WOZ in certain area.
    Args:
        input_data (HouseAreaFeatures): input features
    Returns:
        dictionary with predicted woz-value.
    """
    input_dict = {
        'single': input_data.single,
        'married, no kids': input_data.married_no_kids,
        'not married, no kids': input_data.not_marred_no_kids,
        'married, with kids': input_data.married_w_kids,
        'not married, with kids': input_data.not_married_w_kids,
        'single parent': input_data.single_parent,
        'other': input_data.other,
        'total': input_data.total,
        'area_code': input_data.area_code
    }
    df_input = pd.DataFrame(input_dict, index=[0])
    df_input = encode_area(ohc, df_input)
    pred = model.predict(df_input)[0]
    pred_dict = {'predicted woz price': round(pred)}
    return pred_dict


app = FastAPI()


# Server Definition
@app.get("/")
def root():
    return {"GoTo": "/docs"}


@app.post("/housing_area_prediction")
def is_user_item(request: HouseAreaFeatures):
    return get_predictions(request)
