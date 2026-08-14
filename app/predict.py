import numpy as np


def make_prediction(model, features):
    data = np.array(features).reshape(1, -1)

    prediction = model.predict(data)[0]

    probabilities = model.predict_proba(data)[0]

    confidence = float(max(probabilities))

    return int(prediction), confidence