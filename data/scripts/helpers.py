import pandas as pd
import glob
import os
import xgboost as xgb
import lightgbm as lgbm
import catboost
from sklearn.model_selection import train_test_split, cross_validate, \
    cross_val_score, RepeatedKFold
from sklearn.preprocessing import RobustScaler, StandardScaler, OrdinalEncoder
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import cross_validate
import numpy as np
from tqdm import tqdm

def grab_col_names(dataframe, cat_th=10, car_th=20):
    # cat_cols, cat_but_car
    cat_cols = [col for col in dataframe.columns if
                dataframe[col].dtypes == "O"]

    num_but_cat = [col for col in dataframe.columns if
                   dataframe[col].nunique() < cat_th and
                   dataframe[col].dtypes != "O"]

    cat_but_car = [col for col in dataframe.columns if
                   dataframe[col].nunique() > car_th and
                   dataframe[col].dtypes == "O"]

    cat_cols = cat_cols + num_but_cat

    cat_cols = [col for col in cat_cols if col not in cat_but_car]

    # num_cols
    num_cols = [col for col in dataframe.columns if
                dataframe[col].dtypes != "O"]

    num_cols = [col for col in num_cols if col not in num_but_cat]

    return cat_cols, num_cols, cat_but_car, num_but_cat

def validate(model, X, y):
    results = pd.DataFrame(cross_validate(model, X, y, cv=5,
                                          scoring=[
                                              "neg_mean_squared_error",
                                              "r2"]))
    results["test_neg_mean_squared_error"] = results[
        "test_neg_mean_squared_error"].apply(lambda x: -x)
    results["rmse"] = results["test_neg_mean_squared_error"].apply(
        lambda x: np.sqrt(x))
    return results.mean().to_frame().T

def results(dataframe, target, scale=False, ordinal=False):
    X = dataframe.drop(target, axis=1)
    y = dataframe[target]

    if scale:
        cat_cols, num_cols, cat_but_car, num_but_cat = grab_col_names(X)
        ss = StandardScaler()
        for col in num_cols:
            X[col] = ss.fit_transform(X[[col]])

    if ordinal:
        cat_cols, num_cols, cat_but_car, num_but_cat = grab_col_names(X)
        for col in cat_cols:
            if X[col].dtype.name == 'category':
                oe = OrdinalEncoder(
                    categories=[X[col].dtype.categories.to_list()])
                X[col] = oe.fit_transform(X[[col]])

    X = pd.get_dummies(X, drop_first=True)

    models = [catboost.CatBoostRegressor(random_state=42, silent=True),
              RandomForestRegressor(random_state=42),
              ExtraTreesRegressor(random_state=42),
              xgb.XGBRegressor(random_state=42),
              lgbm.LGBMRegressor(random_state=42)]

    result = pd.DataFrame()
    for model in tqdm(models, desc='Fitting '):
        mdl = model
        res = validate(mdl, X, y)
        result = pd.concat([result, res])

    result.index = ['CatB', 'RF', 'ET', 'XGB', 'LGBM']
    result = result[['test_neg_mean_squared_error', 'test_r2', 'rmse']]
    result = result.rename(columns={'test_neg_mean_squared_error': 'MSE',
                                    'test_r2': 'R2',
                                    'rmse': 'RMSE'})
    return result.T