import re, math
import os
import textblob.tokenizers  as tt
import pickle
from profanity import profanity

from textblob import TextBlob
from textstat.textstat import textstat as ts

from collections import Counter
from functools import partial

class NLPanalysis:

    # FIELDS

    __nameOfFinalDictionary = ''


    # dictionary in which we keep the data
    __dictionary = {}

    # you keep the result in resultingDictionary
    __resultingDictionary = {}
    __WORD = re.compile(r'\w+')

    ## golden fake is sample of fake news (HOW YOU IDENTIFIED THOSE) that you do not use in fitting the model, but using
    ## as a FEATURE base to which you calculate the (average) cosine (or other) similarities
    ## what I have done is that I extracted 20 percent of all fake to be goldenFake
    __goldenFake = {}

    __goldenFakeVector = []

    ## golden true is sample of true news (HOW YOU IDENTIFIED THOSE) that you do not use in fitting the model, but using
    ## as a FEATURE base to which you calculate the (average) cosine (or other) similarities
    ## what I have done is that I extracted 20 percent of all true to be goldenTrue
    __goldenTrue = {}

    __goldenTrueVector = []

    # CONSTRUCTOR
    ## remember put dictionary == cleaned up dictionary for true and not cleaned for fake
    def __init__(self, goldenFake, goldenTrue, dictionary, nameOfFinalDictionaryOnDisc, fake):
        print('The dictionary you are putting in should be already in form: {text_id: text}.')

        if (type(dictionary) == dict) and (type(fake) == bool) and (type(goldenFake) == dict)\
                and (type(goldenTrue) == dict):

            self.__fake = fake
            self.__goldenFake = self.__cleanTextInFakeDictionary(goldenFake)
            self.__goldenTrue = goldenTrue

            if fake:
                print('NOTE: you are creating the fake = ' + str(fake) + ' class.')
                ## do pre-cleaning here
                self.__dictionary = self.__cleanTextInFakeDictionary(dictionary)
            else:
                print('NOTE: you are creating the fake = ' + str(fake) + ' class.')
                self.__dictionary = dictionary

            # creating the empty dictionary here
            self.__createEmptyDictionary()

            # finally create the name of final dictionary on disc
            self.__nameOfFinalDictionary = nameOfFinalDictionaryOnDisc + str(self.__fake)

            ## pre-compute the golden vectors
            self.__precomputeGoldenVectors()

        else:
            raise ValueError

    # HELPFUL FUNCTIONS

    ## prints name of resulting dictionary as saved on disc
    def get_name_of_resulting_dictionary_on_disc(self):
        return self.__nameOfFinalDictionary + 'pickle'

    ## returns the state saved in resulting dictionary
    def get_resulting_dictionary(self):
        return self.__resultingDictionary

    ## this function pre-computes the vectors for goldenFake and goldenTrue dictionaries

    def __precomputeGoldenVectors(self):
            self.__goldenFakeVector = [self.__text_to_vector(self.__goldenFake[key]) for key in
                                       self.__goldenFake.keys()]
            self.__goldenTrueVector = [self.__text_to_vector(self.__goldenTrue[key]) for key in
                                       self.__goldenTrue.keys()]

            self.__saveToFile(self.__goldenFakeVector, 'goldenFakeVector')
            self.__saveToFile(self.__goldenTrueVector, 'goldenTrueVector')

    ## opening the file from the function
    def __safelyOpen(self, nameOfSavedDictionary):
        try:
            with open(nameOfSavedDictionary + '.pickle', 'rb') as handle:
                return pickle.load(handle)
        except FileNotFoundError:
            print("File was not found ")

    ## saving the structure to file
    def __saveToFile(self, structureToSave, structureNameOnDisc):
        if (structureNameOnDisc + '.pickle') in os.listdir():
            print('NOTICE')
            print('the same named file found on disc, be super that you are not rewriting it in good way')
        with open(structureNameOnDisc + '.pickle', 'wb') as handle:
            pickle.dump(structureToSave, handle)


    ## this function cleans up the fake text
    def __cleanText(self, text):
        if self.__fake:
            text = text.replace('\n', ' ')
            text = text.split('.')
            del (text[-1])
            text.append('')
            text = '.'.join(text)
            return text
        else:
            print('Nothing to do on not fake news, the text seemed clean already.')



    ## create an empty dictionary of structure dic = {article_id: []}
    def __createEmptyDictionary(self):
        self.__resultingDictionary = {key: [] for key in self.__dictionary.keys()}


    ## function calculates the properties of self.__dictionary, saves the result on disc back
    ## and adds the name of user function to funcUsed list and save it on local drive
    def __calculateFunResults(self, fun, key):
        #for key in self.__dictionary.keys():
        self.__resultingDictionary[key].extend(fun(self.__dictionary[key]))

        ### save the resultingDictionary to disc
        self.__saveToFile(self.__resultingDictionary, self.__nameOfFinalDictionary)


    ## FUNCTIONS FOR NLP. CALCULATIONS

    ## function that tokenizes the text
    def __tokenizeText(self, text):
        ### the tt.word_tokenize(text) is just the generator and is not present after you used it once, therefore,
        ### create the list out of it
        self.__tokenizedText = list(tt.word_tokenize(text))

    ## NLP FUNCTIONS:

    ## function calculates the total number of capitalized words in a text
    ## function calculates the density of capitalized words in the text
    def __checkUpperCaseWordsAndDensity(self, text):
        finalNumberOfUpper = 0
        length = float(len(self.__tokenizedText))
        for word in self.__tokenizedText:
            if word.isupper():
                finalNumberOfUpper += 1
        return [finalNumberOfUpper, finalNumberOfUpper/length]


    ## calculating readability of the text (so far only Dale-Chall readability implemented)
    def __readability_of_text(self, text, score="dale_chall"):
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

    ## calculate number of ? and !
    ## calculate number of ? and ! density
    def __calculateQuestAndExAndDensity(self, text):
        length = float(len(self.__tokenizedText))
        qAndEx = len(list(filter(lambda x: re.match('\?|!', x), text)))
        return [qAndEx, qAndEx/length]


    ## total vulgarity of text
    ## vulgar density of the text
    def __vulgarAndDensity(self, text):
        length = float(len(self.__tokenizedText))
        prof = 0
        for word in self.__tokenizedText:
            if profanity.contains_profanity(word):
                prof += 1
        return [prof, prof/length]

    ## calculate polarity and subjectivity
    def __polarityAndSubjectivity(self, text):
        blob = TextBlob(text)
        return [blob.sentiment[0], blob.sentiment[1]]


    ## this calculates the cosine similarities of text to goldenFake and goldenTrue
    def __calculateAvgCosineSim(self, fake, text):

        if (type(fake) == bool) and fake and (type(text) == str):
            vectText = self.__text_to_vector(text)

            return [sum([self.__get_cosine(vectText, vec) for vec in self.__goldenFakeVector])\
                   / float(len(self.__goldenFakeVector))]

        elif (type(fake) == bool) and (not fake) and (type(text) == str):
            vectText = self.__text_to_vector(text)
            return [sum([self.__get_cosine(vectText, vec) for vec in self.__goldenTrueVector])\
                    / float(len(self.__goldenTrueVector))]

        else:
            raise ValueError


    ## this function turns the text into a vector
    def __text_to_vector(self, text):
        text = self.__relevant_words(text)
        words = self.__WORD.findall(text)
        return Counter(words)

    ## this function picks up the relevant words from the text == words of type 'NN' and 'JJ' in nltk language
    def __relevant_words(self, text):
        blob = TextBlob(text)
        tags = blob.tags
        return " ".join([t[0] for t in tags if ((t[1] == "NN") or (t[1] == "JJ"))])

    ## this function calculates cosine similarities between vec1 and vec2
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

    # CLEANING THE FAKE TEXT
    ## function that applies clean text on whole dictionary

    def __cleanTextInFakeDictionary(self, dictionary):
        if self.__fake:
            dicFake = {new_key: self.__cleanText(dictionary[new_key]) for new_key in
                           dictionary.keys()}
            return dicFake
        else:
            print('Nothing to do on not fake news, the text seemed clean already.')
            return dictionary

    # NLP CALCULATIONS

    ## application of the list of functions on our dictionary
    def calculateNLP(self):

        ### putting the list of functions by hand, that you want to apply:
        listOfFunctions = [self.__checkUpperCaseWordsAndDensity,
                           self.__readability_of_text, self.__calculateQuestAndExAndDensity,
                           self.__vulgarAndDensity, partial(self.__calculateAvgCosineSim, True),
                           partial(self.__calculateAvgCosineSim, False)]

        ### loop through the text, for each text ---> tokenize the text ---> apply functions ---> save result to final
        ### dictionary and continue
        for key in self.__dictionary.keys():
            text = self.__dictionary[key]

            # keep the text in self.__tokenized text
            self.__tokenizeText(text)

            for fun in listOfFunctions:
                self.__calculateFunResults(fun, key)

        ### add the used function to 'usedFunctionNames' list and save it on local drive
        # self.__saveToFile([fun.__name__ for fun in listOfFunctions], 'alreadyUsedFunctionsNames' + str(self.__fake))



