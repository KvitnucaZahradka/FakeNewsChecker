import pythonwhois  # it's using this http://cryto.net/pythonwhois
from urllib.error import HTTPError
from requests.exceptions import HTTPError
import urllib
import helpful_functions
import urllib.request
import socket



class url_analysis():

    __data = None
    __urls = None
    __meta = None
    __meta_data_name = None

    # data = numerical data you already have
    # urls = urls for the numerical data
    # false = are data to be considered false or not false
    def __init__(self, data, urls, false):
        self.__data = data
        self.__urls = urls

        if false:
            self.__meta_data_name = 'fake_urls_metadata'
        else:
            self.__meta_data_name = 'true_urls_metadata'


    # strategy: loop through the urls that belong to data, for given url look into my precomputed metadata
    # if you find url ok calculate url_analysis, if not query pythonwhois and calculate it after that and add to
    # meta_data I am keeping offline

    # MAIN FUNCTIONS
    def __open_and_produce_url_meta(self):
        self.__meta = helpful_functions.safely_open(self.__meta_data_name, pick=True)

        # NOTE: fix this function tomorrow
        if self.__meta is not None:
            uniq = helpful_functions.uniqify(self.__urls.values())
            difference = helpful_functions.set_difference(uniq, self.__meta)

            if difference is not None:
                print('difference is not empty, is of size: ' + str(len(difference)))
                print('we add it to self.__meta, that is of size: ' + str(len(self.__meta)))

                add_to_meta = {}
                self.__find_url_meta(difference, add_to_meta)
                helpful_functions.add_dict(self.__meta, add_to_meta)

                print('we added missing urls metadata to self.__meta, now it is of size: ' + str(len(self.__meta)))
                print('saving the meta on disc')
                helpful_functions.save_to_file(self.__meta, self.__meta_data_name, pick=True)

        else:
            self.__meta = {}
            self.__find_url_meta(self.__urls.values(), self.__meta)
            helpful_functions.save_to_file(self.__meta, self.__meta_data_name, pick=True)

    # looping through the article ids and adding the outside url features, as calculated from appropriate meta
    def url_analysis(self):
        self.__open_and_produce_url_meta()

        # looking for creation date
        for key in self.__data.keys():
            url = self.__urls[key]
            try:
                year = int(self.__meta[url]['creation_date'][0].year)
            except (TypeError, KeyError):
                year = 2000

            # DEPRECATE the original year_bias function
            # year_bias = self.__year_bias(year)

            # better year_bias calculated by sigmoid_year() function
            year_bias = self.__sigmoid_year(year)
            self.__data[key].extend(year_bias)

    # sigmoid year is probably better feature than year bias
    def __sigmoid_year(self, year):
        return [helpful_functions.sigmoid(year)]

    # this is proxy 0 function, you better should do some clustering will be proxy 1
    # maybe you should implement this as sigmoid function from 1900 ---> 1 and 2017 --> -1, centered at 2000 ???
    def __year_bias(self, year):
        if year < 2000:
            return [1]
        elif year > 2000:
            return [-1]
        else:
            return [0]

    def __find_url_meta(self, domains, meta_fake):
        if type(meta_fake) == dict:
            for dom in domains:
                try:
                    print(dom)
                    meta_fake[dom] = pythonwhois.get_whois(dom)
                except (urllib.request.HTTPError, HTTPError, ConnectionResetError, UnicodeDecodeError):
                    helpful_functions.wait_random_time(45)
                except (KeyError, socket.gaierror):
                    meta_fake[dom] = None
                except pythonwhois.shared.WhoisException:
                    meta_fake[dom] = None
        else:
            raise ValueError

    # HELPFUL FUNCTIONS


    # getting data from outside
    def get_data(self):
        return self.__data

