from bs4 import BeautifulSoup as bs

import json
import re
import os
import time
import random
import datetime
import calendar
import logging

import urllib
import urllib.request
from urllib.error import HTTPError

import sklearn
import matplotlib

import numpy as np
import pandas as pd
import sklearn.preprocessing as prep



import requests
import html.parser
from requests.exceptions import HTTPError
from socket import error as SocketError
from http.cookiejar import CookieJar

import feedparser
import pickle

import langdetect

class FakeData:

    # FIELDS
    __fake = []

    # CLASS INITIALIZATION
    def __init__(self, fakeNewsList):
        try:
            ##  NOTE: add conditions to if statement
            if (type(fakeNewsList) == list):
                self.__fake = fakeNewsList
            else:
                raise ValueError
        except ValueError as e:
            print('there has been error values in initialization')

    # HELPFUL METHODS

    ## querying the fake news source
    def __queryFakeNewsUrl(self, reqUrl):

        try:
            ### prepare for opening
            req = urllib.request.Request(reqUrl, None,
                                         {
                                             'User-Agent': 'Mozilla/5.0 (X11; Linux i686; G518Rco3Yp0uLV40Lcc9hAzC1BOROTJADjicLjOmlr4=) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                                             'Accept':
                                                 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                             'Accept-Charset':
                                                 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                                             'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language':
                                                 'en-US,en;q=0.8', 'Connection': 'keep-alive'})
            cj = CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            response = opener.open(reqUrl)
            raw_response = response.read()
            response.close()

            return bs(raw_response, "html.parser")

        except (urllib.request.HTTPError, HTTPError):
            ### add some logging.. LATER FIX
            print('some HTTP/HTML error, check logs')