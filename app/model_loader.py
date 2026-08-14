import joblib

import config


model = joblib.load(config.MODEL_PATH)
