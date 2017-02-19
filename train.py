import numpy as np
import pandas as pd
import helpful_functions

from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import f1_score
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import train_test_split
import six.moves.cPickle as cPickle

class train:

    # FIELDS
    # models I have already implemented
    __build_in_models = ['AdaBoost']
    # numeric fake keeps the numeric data for fake news
    __numericFake = None

    # numeric true keeps the numeric data for true news
    __numericTrue = None

    __modelName = ''
    __model = None

    # CONSTRUCTOR
    # at this stage you are picking up the Ada Boost
    def __init__(self, numericFake, numericTrue, modelName='AdaBoost'):
        if (type(numericFake) == dict) and (type(numericTrue) == dict):
            self.__numericFake = {}
            self.__numericTrue = {}

            ## you add a class true/fake as 1/0
            self.__addClassOfNewsToData(numericFake, fake=True)
            self.__addClassOfNewsToData(numericTrue, fake=False)

            self.__numericFake = numericFake
            self.__numericTrue = numericTrue

            self.__modelName = modelName + helpful_functions.generate_local_time_suffix()
        else:
            raise ValueError

    # HELPFUL METHODS

    ## this function adds a class (fakeNews = 0 or trueNews = 1)
    def __addClassOfNewsToData(self, dictionary, fake):
        if fake:
            for key in dictionary.keys():
                dictionary[key].append(0)
        else:
            for key in dictionary.keys():
                dictionary[key].append(1)

    ## create the data frames to use in predictions
    def __createDataFrames(self):
        trueDf = pd.DataFrame(self.__numericTrue)
        fakeDf = pd.DataFrame(self.__numericFake)

        return trueDf.join(fakeDf).transpose()

    ## this function splits data into training and testing set
    def __split_training_testing_and_validation(self, joinedDataFrame):
        ## shuffles and splits to train validation and test
        ## note: [int(.7*len(df)), int(.8*len(df))] are: indices_or_sections array for numpy.split()

        train, validate, test = np.split(joinedDataFrame.sample(frac=1),
                                         [int(.7 * len(joinedDataFrame)), int(.8 * len(joinedDataFrame))])

        print('returning: @ 0 = training set, @ 1 = testing set, @ 2 = validation set')
        return [train, test, validate]

    # ADA-BOOSTed classifier WITH grid search
    def __ada_function_specific(self, data_train, y_train, data_test, y_test, data_valid, y_valid):
        name = self.__modelName
        # Ada-Boost grid search
        param_grid = {"base_estimator__criterion": ["gini", "entropy"],
                          "base_estimator__splitter": ["best", "random"],
                          "n_estimators": [150]}

        # DTC = DecisionTreeClassifier(random_state=11, max_features="auto", class_weight="auto", max_depth=None)

        # grid_search_ABC = GridSearchCV(ABC, param_grid=param_grid, scoring='f1', n_jobs=-1)
        # griddi = grid_search_ABC.fit(data_train, y_train)

        # try withou base classifier
        ABC = AdaBoostClassifier(n_estimators=150, learning_rate=1.5, algorithm="SAMME")

        ABC.fit(data_train, y_train)
        griddi = ABC

        # Save the grid searched model as the "name".pkl
        print('saving the model as: ' + name + '.pkl')
        with open(name, 'wb') as fid:
            cPickle.dump(griddi, fid)

        # Print accuracy scores and return the model
        print("Test set accuracy score for the model " + name + " is " + \
                str(accuracy_score(y_test, griddi.predict(data_test))))
        print("Validation set accuracy score for the model " + name + " is " + \
                  str(accuracy_score(y_valid, griddi.predict(data_valid))))

        print("Validation set F1 score for the model " + name + " is " + \
                  str(f1_score(y_valid, griddi.predict(data_valid))))

        return griddi

    def trainModel(self, modelName):
        if type(modelName) == str:
            if modelName == 'AdaBoost':

                fullDataFrame = self.__createDataFrames()
                splitData = self.__split_training_testing_and_validation(fullDataFrame)

                y_dimensions = splitData[0].shape[1]

                # picking up training, testing and validation

                # before: trainX = splitData[0].ix[:, 0:8]
                # before: trainY = splitData[0].ix[:, 9]
                trainX = splitData[0].ix[:, 0:(y_dimensions-2)]
                trainY = splitData[0].ix[:, y_dimensions-1]

                print('number of trainX features is: ' + str(trainX.shape))
                print('print first row in trainX ')
                print(trainX.ix[0, 0:(y_dimensions-2)])

                print('shape of trainY is: ' + str(trainY.shape))

                # before: testX = splitData[1].ix[:, 0:8]
                # before: testY = splitData[1].ix[:, 9]
                testX = splitData[1].ix[:, 0:(y_dimensions-2)]
                testY = splitData[1].ix[:, y_dimensions-1]

                # before: validationX = splitData[2].ix[:, 0:8]
                # before: validationY = splitData[2].ix[:, 9]
                validationX = splitData[2].ix[:, 0:(y_dimensions-2)]
                validationY = splitData[2].ix[:, y_dimensions-1]

                print('start grid-search for ada - boost')

                self.__model = self.__ada_function_specific(trainX, trainY, testX, testY, validationX, validationY)

                print('ada - boost grid search finished it is saved on local drive as (note without .pickle): '
                      + self.__modelName)

                print('model is also stored in local instance of Train class, use method get_model() to retrieve it')

            else:
                print('the requested model ' + modelName + ' is not supported')
        else:
            raise ValueError

    # get model from instance
    def get_model(self):
        return self.__model

    ## this function predicts
    def predict(self, text):
        pass