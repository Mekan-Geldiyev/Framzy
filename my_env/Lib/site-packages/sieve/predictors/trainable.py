from ..predictors import SievePredictor, TemporalPredictor, ObjectPredictor
from ..types.dataset import Dataset

# Create abstract classes for the different types of predictors
class TrainablePredictor(SievePredictor):
    """
    A SievePredictor is a predictor that can be used with the Sieve framework
    """
    ALLOWED_INPUT_TYPES = []
    ALLOWED_OUTPUT_TYPES = []

    def train(self, dataset: Dataset):
        pass

class TrainableTemporalPredictor(TemporalPredictor, TrainablePredictor):
    """
    A trainable temporal processor is a predictor that processes a objects with a temporal component over the last n frames, and can be trained on a dataset
    """
    ALLOWED_INPUT_TYPES = TemporalPredictor.ALLOWED_INPUT_TYPES

    ALLOWED_OUTPUT_TYPES = TemporalPredictor.ALLOWED_OUTPUT_TYPES


class TrainableObjectPredictor(ObjectPredictor, TrainablePredictor):
    """
    A trainable object processor is a predictor that processes an object and can be trained on a dataset
    """

    ALLOWED_INPUT_TYPES = ObjectPredictor.ALLOWED_INPUT_TYPES

    ALLOWED_OUTPUT_TYPES = ObjectPredictor.ALLOWED_OUTPUT_TYPES
