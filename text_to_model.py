import NLPanalysis
import os
import helpful_functions
import pandas
import random
import Train
import url_analysis

class text_to_model():

    #GLOBALS, by the way standard is conservative
    __good_urls = ['nytimes.com', 'wsj.com', 'abcnews.go.com', 'cnn.com', 'cbsnews.com', 'foxnews.com', 'msnbc.com',
                  'nbcnews.com','oann.com', 'latimes.com', 'usatoday.com', 'washingtonpost.com', 'newsweek.com',
                  'time.com', 'usnews.com', 'theguardian.com', 'telegraph.co.uk', 'thetimes.co.uk', 'ft.com',
                  'independent.co.uk', 'bbc.com', 'standard.co.uk', 'dailymail.co.uk', 'express.co.uk',
                  'dailytelegraph.com.au', 'thestar.com','theglobeandmail.com', 'nationalpost.com',
                   'calgaryherald.com', 'herald.ie', 'irishtimes.com', 'independent.ie', 'afr.com.au',
                   'theaustralian.com.au', 'thesaturdaypaper.com.au', 'reddit.com', 'Cnn.com', 'Bbc.co.uk', 'Weather.com',
                   'News.yahoo.com', 'Huffingtonpost.com','Forbes.com', 'Foxnews.com', 'news.google.com' ,
                   'Shutterstock.com', 'Timesofindia.indiatimes.com', 'Bloomberg.com', 'Reuters.com', 'Wunderground.com',
                   'Money.cnn.com', 'Indianexpress.com', 'Nbcnews.com', 'Latimes.com', 'cnbc.com', 'cbsnews.com',
                   'vox.com', 'Abcnews.go.com', 'Nypost.com', 'Theatlantic.com', 'Chicagotribune.com', 'Chinadaily.com.cn'
                   ,'Hollywoodreporter.com', 'Sfgate.com', 'Usnews.com', 'Economist.com', 'Aljazeera.com', 'Fortune.com',
                   'Newsnow.co.uk', 'Variety.com', 'Euronews.com', 'Washingtontimes.com', 'Bostonglobe.com', 'Newsweek.com'
                   ]

    # FIELDS
    __dataFake = {}
    __dataTrue = {}

    __goldenFake = {}
    __goldenTrue = {}

    __urlFake = {}
    __urlTrue = {}

    # CONSTRUCTOR
    def __init__(self, name_of_true_text_dictionaries, name_of_fake_text_dictionaries):
        # NOTE: seed = 77, change this @ the end to some time dependent seed
        random.seed(77)
        if type(name_of_fake_text_dictionaries) == list and type(name_of_true_text_dictionaries) == list:
            length_original_fake = len(name_of_fake_text_dictionaries)
            length_original_true = len(name_of_true_text_dictionaries)

            print(length_original_true)
            print(length_original_fake)

            name_of_fake_text_dictionaries = self.__data_on_disc(name_of_fake_text_dictionaries)
            name_of_true_text_dictionaries = self.__data_on_disc(name_of_true_text_dictionaries)

            if len(name_of_fake_text_dictionaries) != length_original_fake \
                    or len(name_of_true_text_dictionaries)!=length_original_true:
                print('NOTICE, there is mismatch between what is in your lists and what is on disc')

            if name_of_fake_text_dictionaries is not None and name_of_true_text_dictionaries is not None:
                self.__join_raw_data(name_of_true_text_dictionaries, fake=False)
                self.__join_raw_data(name_of_fake_text_dictionaries, fake=True)

            # create the url dictionaries for fake and for true news
            self.__create_url_fake_and_true()

            # for fake news rewrite data to dictionary and leave just text
            self.__dataFake = self.__create_dictionary(self.__dataFake, 'text')

        else:
            raise ValueError


    # MAIN MODEL CREATION FUNCTIONS
    def __create_url_fake_and_true(self):
        self.__urlFake = self.__create_dictionary(self.__dataFake, 'site_url')

        # NOTE, the following has to be fixed in better way
        self.__urlTrue = self.__create_true_urls()

    def create_model(self, name_of_model='AdaBoost'):

        # shuffle before split
        data_fake_keys = random.shuffle(self.__dataFake.keys())
        data_true_keys = random.shuffle(self.__dataTrue.keys())

        self.__dataFake = {key: self.__dataFake[key] for key in data_fake_keys}
        self.__dataTrue = {key: self.__dataTrue[key] for key in data_true_keys}

        # find golden true and golden fake vectors
        # golden vectors are defined to be 20 percent of each dataFake and dataTrue
        len_golden_fake = int(0.2 * len(self.__dataFake))
        len_golden_true = int(0.2 * len(self.__dataTrue))

        # fake data split
        data_fake_gold_vector_keys = list(self.__dataFake.keys())[0:len_golden_fake]
        data_fake_calculation_keys = list(self.__dataFake.keys())[len_golden_fake:len(self.__dataFake)]

        # true data split
        data_true_gold_vector_keys = list(self.__dataTrue.keys())[0:len_golden_true]
        data_true_calculation_keys = list(self.__dataTrue.keys())[len_golden_true:len(self.__dataTrue)]

        # shuffle dataFake, dataTrue, goldenFake, goldenTrue
        random.shuffle(data_fake_gold_vector_keys)
        random.shuffle(data_fake_calculation_keys)

        random.shuffle(data_true_gold_vector_keys)
        random.shuffle(data_true_calculation_keys)

        # splitting the data to goldenTrue, goldenFake, dataTrue, dataFake and cutting related urlFake, urlTrue
        self.__goldenFake = {key: self.__dataFake[key] for key in data_fake_gold_vector_keys}
        self.__goldenTrue = {key: self.__dataTrue[key] for key in data_true_gold_vector_keys}

        self.__dataFake = {key: self.__dataFake[key] for key in data_fake_calculation_keys}
        self.__dataTrue = {key: self.__dataTrue[key] for key in data_true_calculation_keys}

        self.__urlFake = {key: self.__urlFake[key] for key in data_fake_calculation_keys}
        self.__urlTrue = {key: self.__urlTrue[key] for key in data_true_calculation_keys}

        # save goldenFake, goldenTrue
        print('saving data: goldenTrue, goldenFake, dataTrue, dataFake')
        helpful_functions.save_to_file(self.__goldenFake,
                                       'goldenFake' + helpful_functions.generate_local_time_suffix(), pick=True)

        helpful_functions.save_to_file(self.__goldenTrue,
                                       'goldenTrue' + helpful_functions.generate_local_time_suffix(), pick=True)

        # save the dataTrue and dataFake on disc
        helpful_functions.save_to_file(self.__dataTrue,
                                       'dataTrue' + helpful_functions.generate_local_time_suffix(), pick=True)
        helpful_functions.save_to_file(self.__dataFake,
                                       'dataFake' + helpful_functions.generate_local_time_suffix(), pick=True)

        # nlp part:
        print('starting the NLP calculations')

        # NLPanalysis instances
        nlpTrue = NLPanalysis.NLPanalysis(self.__goldenFake, self.__goldenTrue, self.__dataTrue,
                                           'nlp_true_data_' + helpful_functions.generate_local_time_suffix())
        nlpFake = NLPanalysis.NLPanalysis(self.__goldenFake, self.__goldenTrue, self.__dataFake,
                                           'nlp_fake_data_' + helpful_functions.generate_local_time_suffix())

        print('starting the nlp of true set')
        nlpTrue.calculateNLP()
        self.__dataTrue = nlpTrue.get_resulting_dictionary()
        print('the NLPanalysis class saves resulting dictionary as ' +
              nlpTrue.get_name_of_resulting_dictionary_on_disc())

        print('nlp of true set finished')

        print('starting nlp of false set')
        nlpFake.calculateNLP()
        self.__dataFake = nlpFake.get_resulting_dictionary()
        print('the NLPanalysis class saves resulting dictionary as ' +
              nlpTrue.get_name_of_resulting_dictionary_on_disc())

        # add the outside nlp features, i.e. calculated by url_analysis
        urlTrue = url_analysis.url_analysis(self.__dataTrue, self.__urlTrue)


        if type(name_of_model) == str and name_of_model == 'AdaBoost':
            print('MODEL NOT ADDED ADD ADD ADD')
            pass
        else:
            print('required model ' + str(name_of_model) + ' is not implemented')
            print('or wrong type of model name')




    # HELPFUL FUNCTIONS

    # function that adds some good urls to my text data, redo this approach, since so far I have all data just from
    # nytimes
    def __create_true_urls(self):
        return {key: self.__good_urls[self.__random_choice()] for key in self.__dataTrue.keys()}

    def __random_choice(self):
        return random.randint(0, len(self.__good_urls) - 1)

    def __join_raw_data(self, names_to_join, fake):
        if fake:
            for name in names_to_join:
                temp_dict = helpful_functions.safely_open(name, pick=True)
                helpful_functions.add_dict(self.__dataFake, temp_dict)
            # creates the fake data dictionary
            self.__dataFake = self.__create_dictionary(self.__dataFake, 'text')
        else:
            for name in names_to_join:
                temp_dict = helpful_functions.safely_open(name, pick=True)
                helpful_functions.add_dict(self.__dataTrue, temp_dict)

    def __data_on_disc(self, list_of_names):
        directory_files = os.listdir()
        return list(filter(lambda x: (x + '.pickle') in directory_files, list_of_names))


    # function that converts the particular panda data frame to dictionary
    # this function is Fake News from Kaggle-source specific
    def __create_dictionary(self, pandaData, columnName):
        # sub-setting the pandaData
        ddt = pandaData.ix[:, str(columnName)]
        # creating the dictionary
        return ddt.to_dict()
