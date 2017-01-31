import pandas as pd
import pickle




class Predict:
    # FIELDS
    __numeric_dictionary = {}


    # CONSTRUCTOR
    def __init__(self, numeric_dictionary):
        if type(numeric_dictionary) == dict:
            self.__numeric_dictionary = numeric_dictionary
        else:
            raise ValueError

    # HELPFUL METHODS
    def __createX(self):
        dfX = pd.DataFrame(self.__numeric_dictionary)

        return dfX.transpose()


    ## opening the file from the function
    def __safelyOpen(self, nameOfSavedObject):
        try:
            with open(nameOfSavedObject, 'rb') as handle:
                return pickle.load(handle)
        except FileNotFoundError:
            print("File was not found ")

    def predict(self):

        model = self.__safelyOpen('AdaBoost_ADA_MODEL')
        res = model.predict(self.__createX())

        if res == 1:
            return 'not a fake'
        else:
            return 'fake'