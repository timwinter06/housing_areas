""" Script to train model. The main steps are:
* load in feature data and labels.
* perform processing on data 
* Train model
* Save model, encoder, and metrics. 
"""
import os
import argparse
import json
import pickle
import numpy as np
import pandas as pd
from sklearn import linear_model
from sklearn.linear_model import Lasso
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def preprocess(df_all: pd.DataFrame, features: list, target: str):
    """ Preprocessing function to be applied to the merged dataframe consisting 
    of the 'family-composition' and 'woz-prices' data.
    The following preprocessing is done:
    * drop the 'total' row
    * drop the 'woz-value per m2' column
    * set feature columns with a '-' value to 0
    * set target column with a '.' to np.nan
    * change feature and target columns to float type
    Args:
        df_all (pd.DataFrame): the result of merging the 'family-composition' & the 'woz-prices'
        data.
        features (list): list of feature columns.
        target (str): target column.
    Returns:
        preprocessed dataframe. 
    """
    df_all = df_all.drop(481, axis=0)
    df_all = df_all.drop('woz-value per m2', axis=1)
    for feature in features:
        df_all.loc[df_all[feature] == '-', feature] = 0
        df_all[feature] = df_all[feature].astype(float)
    df_all.loc[df_all[target] == '.', target] = np.nan
    df_all[target] = df_all[target].astype(float)
    return df_all


def add_area_feature(df_all: pd.DataFrame, features: list, name: str = 'area_code', n: int = 3):
    """ Create an extra feature from the area column. By changing 'n', you can change the 
    feature being created. For example you can choose to make a feature out of the area letter by 
    putting n=1 or by creating a feature out of the letter & digits by setting n=3.
    Args:
        df_all (pd.DataFrame): dataframe with an 'area' column.
        features (list): list of featurs to which the new feature should be added.
        n (int): the number of characters of the string you want to select.
        name (str): the name given to the new feature.
    Returns:
        dataframe with extra column for the area-feature.
    """
    df_all['area_code'] = df_all['area'].str[:3]
    features = features + [name]
    return df_all, features


def encode_data(x: pd.DataFrame, feature: str, transform: bool, ohc):
    """ Encodes a catergorical column in the dataframe.
    Args:
        x (pd.DataFrame): train or test dataframe with a categorical column.
        feature (str): column name to encode.
        transform (bool): whether to fit_transform (True) or just transform (False).
        ohc (OneHotEncoder): sklearn onehotencoder. 
    Returns:
        Dataframe with encoded feature, as well as the encoder. 
    """
    if transform:
        ohe = ohc.fit_transform(x[feature].values.reshape(-1, 1)).toarray()
    else:
        ohe = ohc.transform(x[feature].values.reshape(-1, 1)).toarray()
    df_one_hot = pd.DataFrame(ohe, columns=ohc.categories_[0])
    x = pd.concat([x.reset_index(drop=True), df_one_hot], axis=1)
    x = x.drop(feature, axis=1)
    return x, ohc


def main(args):
    area_feature = 'area_code'
    features = [
        'single', 'married, no kids',
        'not married, no kids', 'married, with kids',
        'not married, with kids', 'single parent',
        'other', 'total'
    ]
    target = 'average woz value'

    df_comp = pd.read_excel(os.path.join('data', 'family_composition_2016_amsterdam.xlsx'),
                            skiprows=2)
    df_price = pd.read_excel(os.path.join('data', 'woz_prices_2015_amsterdam.xlsx'),
                             skiprows=2)

    # Merge data
    df_comp = df_comp.dropna()
    df_price = df_price.dropna()
    df_all = df_comp.merge(df_price, how='outer', left_on='area', right_on='area')

    # Preprocess and feature engineer
    df_all = preprocess(df_all, features, target)
    df_all, features = add_area_feature(df_all, features, area_feature)

    # Drop NaNs for training, shuffle, and split data
    train_test = df_all.dropna()
    x_train, x_test, y_train, y_test = train_test_split(train_test[features],
                                                        train_test[target],
                                                        test_size=args.test_ratio,
                                                        random_state=123)

    # Scale data
    numeric_columns = x_train.columns[x_train.dtypes != object]
    scaler = StandardScaler()
    x_train[numeric_columns] = scaler.fit_transform(x_train[numeric_columns])
    x_test[numeric_columns] = scaler.transform(x_test[numeric_columns])

    # Encode categorical 
    ohc = OneHotEncoder(handle_unknown='ignore')
    x_train, ohc = encode_data(x_train, area_feature, True, ohc)
    x_test, _ = encode_data(x_test, area_feature, False, ohc)

    # Fit model
    # model = linear_model.LinearRegression()
    model = Lasso(alpha=100)
    model.fit(x_train, y_train)

    # Make prediction
    y_pred = model.predict(x_test)
    y_train_pred = model.predict(x_train)

    # Compute metrics
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    r2_train = r2_score(y_train, y_train_pred)
    r2_test = r2_score(y_test, y_pred)
    metrics = {'rmse': rmse, 'r2_train': r2_train, 'r2_test': r2_test}

    # Save results to 'results' dir
    results_path = 'results'
    with open(os.path.join(results_path, args.model_version), 'wb') as files:
        pickle.dump(model, files)
    with open(os.path.join(results_path, f"{args.model_version}_{area_feature}_encoder"), 'wb') \
            as files:
        pickle.dump(ohc, files)
    with open(os.path.join(results_path, f'{args.model_version}_scaler'), 'wb') as fp:
        pickle.dump(scaler, fp)
    with open(os.path.join(results_path, f'{args.model_version}_metrics'), 'w') as fp:
        json.dump(metrics, fp)

    # If this is the model to deploy, save it to the api dir
    if args.deploy:
        with open(os.path.join('api', 'app', 'model'), 'wb') as files:
            pickle.dump(model, files)
        with open(os.path.join('api', 'app', 'encoder'), 'wb') \
                as files:
            pickle.dump(ohc, files)
        with open(os.path.join('api', 'app', 'scaler'), 'wb') \
                as files:
            pickle.dump(scaler, files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_version", type=str, required=True)
    parser.add_argument("--test_ratio", type=float, required=True)
    parser.add_argument("--deploy", type=bool, required=True)
    args = parser.parse_args()
    main(args)
