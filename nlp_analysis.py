import re,math
import os
import textblob.tokenizers as tt
import pickle
import profanity.profanity as pf

from textblob import TextBlob
from textstat.textstat import textstat as ts
from collections import Counter
from functools import partial

class nlp_analysis:

    # FIELDS
    __name_of_final_dictionary = ''
    __dictionary = {}  # dictionary in which we keep the data

    __resulting_dictionary = {}  # you keep the result in resultingDictionary
    __word = re.compile(r'\w+')

    # golden fake is sample of fake news (HOW YOU IDENTIFIED THOSE) that you do not use in fitting the model, but using
    # as a feature base to which you calculate the (average) cosine (or other) similarities
    # what I have done is that I extracted 20 percent of all fake to be goldenFake
    __golden_fake = {}
    __golden_fake_vector = []

    # golden true is sample of true news (HOW YOU IDENTIFIED THOSE) that you do not use in fitting the model, but using
    # as a feature base to which you calculate the (average) cosine (or other) similarities
    # what I have done is that I extracted 20 percent of all true to be goldenTrue
    __golden_true = {}
    __golden_true_vector = []

    __tokenized_text = None  # there I store the tokenized text

    # -----------------------------------------------------------------------------------------------------------------
    # CONSTRUCTOR

    # dictionary == cleaned up dictionary for true and not cleaned for fake
    def __init__(self, golden_fake, golden_true, dictionary, name_of_final_dictionary_on_disc, fake):
        print('The dictionary you are putting in should be already in form: {text_id: text}.')

        if (type(dictionary) == dict) and (type(fake) == bool) and (type(golden_fake) == dict)\
                and (type(golden_true) == dict):

            self.__fake = fake
            self.__golden_fake = self.__clean_text_in_fake_dictionary(golden_fake)
            self.__golden_true = golden_true

            if fake:
                print('NOTE: you are creating the fake = ' + str(fake) + ' class.')
                self.__dictionary = self.__clean_text_in_fake_dictionary(dictionary)  # do pre-cleaning here
            else:
                print('NOTE: you are creating the fake = ' + str(fake) + ' class.')
                self.__dictionary = dictionary

            self.__create_empty_dictionary()  # creating an empty dictionary here

            # finally create the name of final dictionary on disc
            self.__name_of_final_dictionary = name_of_final_dictionary_on_disc + str(self.__fake)

            # pre-compute the golden vectors
            self.__precompute_golden_vectors()

        else:
            raise ValueError

    # -----------------------------------------------------------------------------------------------------------------
    # HELPFUL FUNCTIONS

    # prints name of resulting dictionary as saved on disc
    def get_name_of_resulting_dictionary_on_disc(self):
        return self.__name_of_final_dictionary + 'pickle'

    # returns the state saved in resulting dictionary
    def get_resulting_dictionary(self):
        return self.__resulting_dictionary

    # this function pre-computes the vectors for goldenFake and goldenTrue dictionaries
    def __precompute_golden_vectors(self):
            self.__golden_fake_vector = [self.__text_to_vector(self.__golden_fake[key]) for key in
                                         self.__golden_fake.keys()]
            self.__golden_true_vector = [self.__text_to_vector(self.__golden_true[key]) for key in
                                         self.__golden_true.keys()]

            self.__save_to_file(self.__golden_fake_vector, 'goldenFakeVector')
            self.__save_to_file(self.__golden_true_vector, 'goldenTrueVector')

    # opening the file from the function
    @staticmethod
    def __safely_open(name_of_saved_dictionary):
        try:
            with open(name_of_saved_dictionary + '.pickle', 'rb') as handle:
                return pickle.load(handle)
        except FileNotFoundError:
            print("File was not found ")

    # saving the structure to file
    @staticmethod
    def __save_to_file(structure_to_save, structure_name_on_disc):
        if (structure_name_on_disc + '.pickle') in os.listdir():
            print('NOTICE')
            print('the same named file found on disc, be super that you are not rewriting it in good way')
        with open(structure_name_on_disc + '.pickle', 'wb') as handle:
            pickle.dump(structure_to_save, handle)

    # this function cleans up the fake text
    def __clean_text(self, text):
        if self.__fake:

    # function calculates the properties of self.__dictionary, saves the result on disc back
    # and adds the name of user function to funcUsed list and save it on local drive
            text = text.replace('\n', ' ')
            text = text.split('.')
            del (text[-1])
            text.append('')
            text = '.'.join(text)
            return text
        else:
            print('Nothing to do on not fake news, the text seemed clean already.')

    # create an empty dictionary of structure dic = {article_id: []}
    def __create_empty_dictionary(self):
        self.__resulting_dictionary = {key: [] for key in self.__dictionary.keys()}
    def __calculate_fun_results(self, fun, key):
        # for key in self.__dictionary.keys():
        self.__resulting_dictionary[key].extend(fun(self.__dictionary[key]))


    # function that tokenizes the text
    def __tokenize_text(self, text):
        # the tt.word_tokenize(text) is just the generator and is not present after you used it once, therefore,
        # create the list out of it
        self.__tokenized_text = list(tt.word_tokenize(text))

    # function calculates the total number of capitalized words in a text
    # function calculates the density of capitalized words in the text
    def __check_upper_case_words_and_density(self, text):
        final_number_of_upper = 0
        length = float(len(self.__tokenized_text))

        for word in self.__tokenized_text:
            if word.isupper():
                final_number_of_upper += 1
        return [final_number_of_upper, final_number_of_upper/length]


    # calculating readability of the text (so far only Dale-Chall readability implemented)
    @staticmethod
    def __readability_of_text(text, score="dale_chall"):
        try:
            if type(score) == str:
                if score == "dale_chall":
                    readability = ts.dale_chall_readability_score(text)
                    return [readability]
                else:
                    print('Other scores are not supported yet. You wanted: ' + score + " we have only dale_chall")
            else:
                raise ValueError
        except ValueError:
            print("the score should be of type str. You put " + str(type(score)))
            raise

    # calculate number of ? and !
    # calculate number of ? and ! density
    def __calculate_quest_and_ex_and_density(self, text):
        length = float(len(self.__tokenized_text))
        q_and_ex = len(list(filter(lambda x: re.match('\?|!', x), text)))
        return [q_and_ex, q_and_ex/length]

    # total vulgarity of text
    # vulgar density of the text
    def __vulgar_and_density(self, text):
        length = float(len(self.__tokenized_text))
        prof = 0
        for word in self.__tokenized_text:
            if pf.contains_profanity(word):
                prof += 1
        return [prof, prof/length]

    # calculate polarity and subjectivity
    def __polarity_and_subjectivity(self, text):
        blob = TextBlob(text)
        return [blob.sentiment[0], blob.sentiment[1]]


    # this calculates the cosine similarities of text to goldenFake and goldenTrue
    def __calculate_avg_cosine_sim(self, fake, text):

        if (type(fake) == bool) and fake and (type(text) == str):
            vect_text = self.__text_to_vector(text)

            return [sum([self.__get_cosine(vect_text, vec) for vec in self.__golden_fake_vector]) \
                    / float(len(self.__golden_fake_vector))]

        elif (type(fake) == bool) and (not fake) and (type(text) == str):
            vect_text = self.__text_to_vector(text)
            return [sum([self.__get_cosine(vect_text, vec) for vec in self.__golden_true_vector]) \
                    / float(len(self.__golden_true_vector))]

        else:
            raise ValueError


    # this function turns the text into a vector
    def __text_to_vector(self, text):
        text = self.__relevant_words(text)
        words = self.__word.findall(text)
        return Counter(words)

    # this function picks up the relevant words from the text == words of type 'NN' and 'JJ' in nltk language
    def __relevant_words(self, text):
        blob = TextBlob(text)
        tags = blob.tags
        return " ".join([t[0] for t in tags if ((t[1] == "NN") or (t[1] == "JJ"))])

    # this function calculates cosine similarities between vec1 and vec2
    def __get_cosine(self, vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
        sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

    # function returne yules lexical diversity of the text
    def __get_yules(self, text):
        """
        Returns a tuple with Yule's K and Yule's I.
        (cf. Oakes, M.P. 1998. Statistics for Corpus Linguistics.
        International Journal of Applied Linguistics, Vol 10 Issue 2)
        In production this needs exception handling. (what kind of exceptions??)
        """
        tokens = self.__tokenized_text
        token_counter = Counter(tok.upper() for tok in tokens)

        m1 = sum(token_counter.values())
        m2 = sum([freq ** 2 for freq in token_counter.values()])

        i = (m1 * m1) / (m2 - m1)
        #k = 1 / i * 10000

        return [i]

    # -----------------------------------------------------------------------------------------------------------------
    # CLEANING THE FAKE TEXT

    # function that applies clean text on whole dictionary
    def __clean_text_in_fake_dictionary(self, dictionary):
        if self.__fake:
            dic_fake = {new_key: self.__clean_text(dictionary[new_key]) for new_key in
                       dictionary.keys()}
            return dic_fake
        else:
            print('Nothing to do on not fake news, the text seemed clean already.')
            return dictionary

    # -----------------------------------------------------------------------------------------------------------------
    # NLP CALCULATIONS

    # application of the list of functions on our dictionary
    def calculate_nlp(self):
        # putting the list of functions by hand, that you want to apply:
        list_of_functions = [self.__check_upper_case_words_and_density,
                           self.__readability_of_text, self.__polarity_and_subjectivity,
                        self.__calculate_quest_and_ex_and_density, self.__vulgar_and_density,
                        partial(self.__calculate_avg_cosine_sim, True), partial(self.__calculate_avg_cosine_sim, False),
                             self.__get_yules]

        # loop through the text, for each text ---> tokenize the text ---> apply functions ---> save result to final
        # dictionary and continue
        counter = 0
        for key in self.__dictionary.keys():
            text = self.__dictionary[key]

            # keep the text in self.__tokenized text
            self.__tokenize_text(text)

            for fun in list_of_functions:
                self.__calculate_fun_results(fun, key)

            # save the resultingDictionary to disc
            print('saving, number of dictionary key is: ' + str(counter))
            self.__save_to_file(self.__resulting_dictionary, self.__name_of_final_dictionary)
            counter += 1



