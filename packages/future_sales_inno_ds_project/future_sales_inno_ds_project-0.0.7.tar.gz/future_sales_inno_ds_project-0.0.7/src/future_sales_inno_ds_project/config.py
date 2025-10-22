# config.py

from hyperopt import hp
import os

# Set base dir
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# Main paths
TRAIN_PATH = os.path.join(BASE_DIR, "data/raw/sales_train.csv")
TEST_PATH = os.path.join(BASE_DIR, "data/raw/test.csv")
ITEMS_PATH = os.path.join(BASE_DIR, "data/raw/items.csv")
CATS_PATH = os.path.join(BASE_DIR, "data/raw/item_categories.csv")
SHOPS_PATH = os.path.join(BASE_DIR, "data/raw/shops.csv")
SUB_PATH = os.path.join(BASE_DIR, "data/raw/sample_submission.csv")
PRED_PATH = os.path.join(BASE_DIR, "data/processed/sample_submission.csv")
MODEL_SAVE_PATH = os.path.join(BASE_DIR, "models/sales_model.pkl")

# Processed data files
X_PATH = os.path.join(BASE_DIR, "data/processed/x.csv")
X_TEST_PATH = os.path.join(BASE_DIR, "data/processed/x_test.csv")
Y_PATH = os.path.join(BASE_DIR, "data/processed/y.csv")

# Labels-value pairs
LE_CITY_PATH = os.path.join(BASE_DIR, "data/labels/shop_city_labels.csv")
LE_GROUPS_PATH = os.path.join(BASE_DIR, "data/labels/group_name_labels.csv")
LE_ITEMF4_PATH = os.path.join(BASE_DIR, "data/labels/item_first4_labels.csv")
LE_ITEMF6_PATH = os.path.join(BASE_DIR, "data/labels/item_first6_labels.csv")
LE_ITEMF11_PATH = os.path.join(BASE_DIR, "data/labels/item_first11_labels.csv")

HISTOGRAM_PATH = os.path.join(BASE_DIR, "shap_graphs/error_histogram.png")
DYNAMIC_VS_ERROR_PATH = os.path.join(BASE_DIR, "shap_graphs/dynamic_vs_error.png")
BEESWARM_PATH = os.path.join(BASE_DIR, "shap_graphs/shap_beeswarm.png")
SHAP_LSTM_PATH = os.path.join(BASE_DIR, "shap_graphs/shap_lstm_summary.png")


# To retrain base rfr model for feature selection
RF_BASE_PATH = os.path.join(BASE_DIR, "models/rfr.pkl")

# Remaining features for result model
FEATURE_COLS = [
    'lag_1_month', 'lag_2_month', 'lag_3_month',
    'avg_item_cnt_prev_month', 'avg_shop_cnt_prev_month', 'month',
    'item_age', 'shop_age', 'category_age',
    'item_category_id', 'shop_city',
    'category_cnt_lag1', 'category_cnt_all_shops_lag1',
    'group_cnt_lag1', 'group_cnt_all_shops_lag1',
    'city_cnt_lag1', 'year'
]

# Metadata
MODEL_METADATA = {
    "name": "Sales prediction model",
    "author": "Katsiaryna Shymchonak",
    "version": 1
}

USE_FEATURE_SELECTION = 0
LOG_TARGET = 0
# XGBRegressor, LGBMRegressor, RandomForestRegressor, RidgeRegression, LSTM
MODEL_TYPE = "XGBRegressor"
FEATURE_SET = "basic"  # "basic", "extended", "lags_only"
USE_OPTUNA = 1,
USE_PARALLEL_TUNING = 0,
LSTM_INPUT_SHAPE = (1, len(FEATURE_COLS))  # timesteps, features

FORM_PREP_DATA = 0
TRAIN_RFR_MODEL = 0
SAMPLE_BEFORE_TUNING = 1

HYPEROPT_SPACES = {
    "XGBRegressor": {
        "n_estimators": hp.quniform("xgb_n_estimators", 300, 1200, 100),
        "max_depth": hp.quniform("xgb_max_depth", 4, 10, 1),
        "learning_rate": hp.loguniform("xgb_learning_rate", -4.6, -1.6),  # log(0.01) to log(0.2)
        "subsample": hp.uniform("xgb_subsample", 0.6, 1.0),
        "colsample_bytree": hp.uniform("xgb_colsample_bytree", 0.6, 1.0),
        "reg_alpha": hp.loguniform("xgb_reg_alpha", -18.4, 2.3),  # log(1e-8) to log(10)
        "reg_lambda": hp.loguniform("xgb_reg_lambda", -18.4, 2.3),
        "min_child_weight": hp.quniform("xgb_min_child_weight", 1, 300, 1),
        "gamma": hp.uniform("xgb_gamma", 0.0, 5.0),
        "tree_method": "hist",
        "objective": "reg:squarederror",
        "verbosity": 0
    },

    "LGBMRegressor": {
        "n_estimators": hp.quniform("lgb_n_estimators", 300, 1200, 100),
        "learning_rate": hp.loguniform("lgb_learning_rate", -4.6, -1.6),
        "max_depth": hp.quniform("lgb_max_depth", 4, 12, 1),
        "num_leaves": hp.quniform("lgb_num_leaves", 31, 256, 1),
        "min_data_in_leaf": hp.quniform("lgb_min_data_in_leaf", 20, 100, 1),
        "min_gain_to_split": hp.uniform("lgb_min_gain_to_split", 0.0, 0.5),
        "feature_fraction": hp.uniform("lgb_feature_fraction", 0.6, 1.0),
        "bagging_fraction": hp.uniform("lgb_bagging_fraction", 0.6, 1.0),
        "bagging_freq": hp.quniform("lgb_bagging_freq", 1, 10, 1),
        "lambda_l1": hp.loguniform("lgb_lambda_l1", -18.4, 2.3),
        "lambda_l2": hp.loguniform("lgb_lambda_l2", -18.4, 2.3),
        "force_col_wise": True,
        "verbosity": -1,
        "objective": "regression"
    },

    "RandomForestRegressor": {
        "n_estimators": hp.quniform("rf_n_estimators", 100, 500, 100),
        "max_depth": hp.quniform("rf_max_depth", 4, 10, 1),
        "min_samples_split": hp.quniform("rf_min_samples_split", 2, 20, 1),
        "min_samples_leaf": hp.quniform("rf_min_samples_leaf", 1, 10, 1),
        "max_features": hp.choice("rf_max_features", ["sqrt", "log2"])
    },

    "Ridge": {
        "alpha": hp.loguniform("ridge_alpha", -4.6, 4.6),  # log(0.01) to log(100)
        "fit_intercept": hp.choice("ridge_fit_intercept", [True, False]),
        "solver": hp.choice("ridge_solver", ["auto", "svd", "cholesky", "lsqr", "sparse_cg", "sag"])
    },
}


def xgb_param_space(trial):
    return {
        "n_estimators": trial.suggest_int("xgb_n_estimators", 300, 1200, step=100),
        "max_depth": trial.suggest_int("xgb_max_depth", 4, 10),
        "learning_rate": trial.suggest_float("xgb_learning_rate", 0.01, 0.2, log=True),
        "subsample": trial.suggest_float("xgb_subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("xgb_colsample_bytree", 0.6, 1.0),
        "reg_alpha": trial.suggest_float("xgb_reg_alpha", 1e-8, 10.0, log=True),
        "reg_lambda": trial.suggest_float("xgb_reg_lambda", 1e-8, 10.0, log=True),
        "min_child_weight": trial.suggest_int("xgb_min_child_weight", 1, 300),
        "gamma": trial.suggest_float("xgb_gamma", 0.0, 5.0),
        "tree_method": "hist",  # ускоряет обучение на больших данных
        "objective": "reg:squarederror",
        "verbosity": 0
    }


def lgb_param_space(trial):
    return {
        "n_estimators": trial.suggest_int("lgb_n_estimators", 300, 1200, step=100),
        "learning_rate": trial.suggest_float("lgb_learning_rate", 0.01, 0.2, log=True),
        "max_depth": trial.suggest_int("lgb_max_depth", 4, 12),
        "num_leaves": trial.suggest_int("lgb_num_leaves", 31, 256),
        "min_data_in_leaf": trial.suggest_int("lgb_min_data_in_leaf", 20, 100),
        "min_gain_to_split": trial.suggest_float("lgb_min_gain_to_split", 0.0, 0.5),
        "feature_fraction": trial.suggest_float("lgb_feature_fraction", 0.6, 1.0),
        "bagging_fraction": trial.suggest_float("lgb_bagging_fraction", 0.6, 1.0),
        "bagging_freq": trial.suggest_int("lgb_bagging_freq", 1, 10),
        "lambda_l1": trial.suggest_float("lgb_lambda_l1", 1e-8, 10.0, log=True),
        "lambda_l2": trial.suggest_float("lgb_lambda_l2", 1e-8, 10.0, log=True),
        "force_col_wise": True,
        "verbosity": -1,
        "objective": "regression"
    }


def rf_param_space(trial):
    return {
        "n_estimators": trial.suggest_int("rf_n_estimators", 100, 500, step=100),
        "max_depth": trial.suggest_int("rf_max_depth", 4, 10),
        "min_samples_split": trial.suggest_int("rf_min_samples_split", 2, 20),
        "min_samples_leaf": trial.suggest_int("rf_min_samples_leaf", 1, 10),
        "max_features": trial.suggest_categorical("rf_max_features", ["sqrt", "log2"]),
    }


def ridge_param_space(trial):
    return {
        "alpha": trial.suggest_float("ridge_alpha", 0.01, 100.0, log=True),
        "fit_intercept": trial.suggest_categorical("ridge_fit_intercept", [True, False]),
        "solver": trial.suggest_categorical("ridge_solver", ["auto", "svd", "cholesky", "lsqr", "sparse_cg", "sag"])
    }


OPTUNA_SPACES = {
    "XGBRegressor": xgb_param_space,
    "LGBMRegressor": lgb_param_space,
    "RandomForestRegressor": rf_param_space,
    "Ridge": ridge_param_space,
}
