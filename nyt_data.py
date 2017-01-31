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

### RESOLVE THIS
from urllib.error import HTTPError

import requests
import html.parser
from requests.exceptions import HTTPError
from socket import error as SocketError
from http.cookiejar import CookieJar

import feedparser
import pickle


class nyt_data:
    # FIELDS
    __offset = 'offset=0'
    # you use just 9000 out of 10000 to have some buffer
    __totalNumberOfAllowedQueries = 9000
    __numberOfUsedQueries = 0
    __nytApiKey = ''
    __queryList = []
    __paperName = ''

    # CLASS INITIALIZATION
    def __init__(self, apiKey, paperName, totalNumberOfAllowedQueries=9000):
        try:
            ##  NOTE: add conditions to if statement
            if ((type(apiKey) and type(paperName)) == str):
                self.__nytApiKey = 'api-key=' + apiKey
                self.__paperName = paperName

                # add the required query list by hand
                self.__queryList = ["Politics", "Economics", "Business", "Financial", "World",
                                    "Washington", "Wealth", "Jobs", "Society"]
                # self.__queryList = queryList
                self.__totalNumberOfAllowedQueries = totalNumberOfAllowedQueries
            else:
                raise ValueError
        except ValueError as e:
            print('there has been error values in initialization')

    # HELPFUL FUNCTIONS (mostly private)

    ## this function constructs the Nytimes query, starting from some start date and end date and for some requested page
    def __constructUrlNytimes(self, queryList, startDate='20160901', endDate='20160930', page=0):

        apiUrl = 'http://api.nytimes.com/svc/search/v2/articlesearch.json?'

        query = 'fq=news_desk:('
        for iquery in queryList:
            query = query + '"' + iquery + '"'
        query += ')'
        apiUrl += query

        apiDate = 'begin_date=' + startDate + '&end_date=' + endDate + '&sort=newest' + "&page=" + str(page)

        link = [apiUrl, apiDate, self.__offset, self.__nytApiKey]
        reqUrl = '&'.join(link)
        return reqUrl

    ## function that constructs a feed
    def __constructFeed(self, reqUrl):
        try:
            ### prepare for opening
            req = urllib.request.Request(reqUrl, None)
            cj = CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            response = opener.open(req)
            raw_response = response.read()
            response.close()

            ### increase the number of used queries
            self.__numberOfUsedQueries += 1

            ### return the feed
            return json.loads(raw_response)
        except (urllib.request.HTTPError, HTTPError):
            print('some HTTPError')
            raise

    ## function that parse the feed and add it up to existing dictionary
    def __feedToDicParser(self, dictionary, feed):
        fake = False
        feed = feed['response']['docs']

        # this is the range the NYTimes gives you in one query
        for i in range(0, len(feed)):
            tempFeed = feed[i]
            idf = tempFeed['_id']
            dictionary[idf] = []

            # for security remember the id also in the body
            dictionary[idf].append(idf)
            # add whether source is fake or not a fake
            dictionary[idf].append(fake)
            # add publication date
            dictionary[idf].append(tempFeed['pub_date'])
            # add web-url
            dictionary[idf].append(tempFeed['web_url'])
            # add in a snippet
            dictionary[idf].append(tempFeed['snippet'])
            # add in an abstract
            dictionary[idf].append(tempFeed['abstract'])
        return dictionary

    ## function returns nyt snippets as a dictionary
    def __getNYTsnippets(self, queryList, startDate='20160901', endDate='20160931', upperBoundOnPages=10):
        dic = {}
        totalNumberOfErrors = 10
        numOfErrors = 0
        if ((upperBoundOnPages > self.__totalNumberOfAllowedQueries)
            or (self.__numberOfUsedQueries > self.__totalNumberOfAllowedQueries)):
            print('NYT upper bound exceeded returning empty dictionary ')
            return dic
        else:
            i = 0
            while i in range(0, upperBoundOnPages):
                try:
                    ### get the url
                    url = self.__constructUrlNytimes(queryList, startDate, endDate, page=i)
                    print(url)
                    ### get feed
                    feed = self.__constructFeed(url)
                    ### parse the feed and add it to dic
                    dic = self.__feedToDicParser(dic, feed)
                    print('DOING PAGE NR. :' + str(i))
                    i += 1
                    time.sleep(3)
                except (urllib.request.HTTPError, HTTPError):
                    if numOfErrors <= totalNumberOfErrors:
                        print('TOTAL NR. of ERRORS: ' + str(numOfErrors))
                        numOfErrors += 1
                        continue
                    else:
                        break
            return dic

    ## function that finds the url links in saved snippet dictionary
    ### if time allows add checker whether you are reading the NYT snippet dictionary
    def __findUrlLinks(self, nameOfDic):
        urlList = []
        dic = self.__safelyOpenDict(nameOfDic)
        for k in dic.keys():
            for idd in dic[k].keys():
                urlList.append(dic[k][idd][3])
        return urlList

    ## in this prune away 'video' section and 'slideshow' section in saved snippet dic.
    ## reason is too little text in there
    ### if time allows add checker whether you are reading the NYT snippet dictionary
    def __findUrlLinksPruned(self, nameOfDic):
        urlList = []
        dic = self.__safelyOpenDict(nameOfDic)
        for k in dic.keys():
            for idd in dic[k].keys():
                tempLink = dic[k][idd][3]
                if not (('video' in tempLink) or ('slideshow' in tempLink)):
                    urlList.append(dic[k][idd][3])
        return urlList

    ## in this prune away 'video' section and 'slideshow' section in saved snippet dic.
    ## reason is too little text in there
    ### if time allows add checker whether you are reading the NYT snippet dictionary
    def __findUrlLinksPrunedDictionary(self, nameOfDic):
        urlListDict = {}
        dic = self.__safelyOpenDict(nameOfDic)
        for k in dic.keys():
            for idd in dic[k].keys():
                tempLink = dic[k][idd][3]
                if not (('video' in tempLink) or ('slideshow' in tempLink)):
                    urlListDict[idd] = dic[k][idd][3]
        return urlListDict

    ## function that forces system to wait random time, with upper bound on wait equals to maxTime
    def __waitRandomTime(self, maxTime=7):
        ## setting up the seed
        tm = int(round(time.time()))
        random.seed(tm)

        tim = random.randint(0, 8 * 100) / 100.0
        time.sleep(tim)

    ## SAVING and ADD/DEL FUNCTIONS

    ### adds up two dictionaries and updates the first one to conglomerate
    def __addDict(self, final, temp):
        z = dict(final, **temp)
        final.update(z)

    ### creates an empty dictionary
    def __createEmptyDict(self, name_of_dictionary):
        with open(name_of_dictionary + '.pickle', 'wb') as handle:
            pickle.dump({}, handle)

    ###  opens the dictionary from file, if file is not present it creates is
    def __openDict(self, name_of_saved_dictionary):
        try:
            with open(name_of_saved_dictionary + '.pickle', 'rb') as handle:
                return pickle.load(handle)
        except FileNotFoundError:
            print("File was not found, I will create empty dictionary with name " + name_of_saved_dictionary)
            self.__createEmptyDict(name_of_saved_dictionary)
            return self.__openDict(name_of_saved_dictionary)

    ### save list to file
    def __saveList(self, listToSave, nameOfList):
        if (nameOfList + '.pickle') not in os.listdir():
            with open(nameOfList + '.pickle', 'wb') as handle:
                pickle.dump(listToSave, handle)
            print('List was saved under name ' + nameOfList + '.pickle')
        else:
            print('ERROR: the name ' + nameOfList + '.pickle has been used, use different one!')

    ### saves dictionary to file
    def __saveDictToFile(self, dictionary, name):
        with open(name + '.pickle', 'wb') as handle:
            pickle.dump(dictionary, handle)

    ### saving function that saves the dictionary and if not such a dictionary is present on disc will create it
    def __saveDict(self, dictionary, name_of_dictionary, start_of_the_month):

        # I will try to open a dictionary
        tempDic = self.__openDict(name_of_dictionary)

        # add a dictionary to current dictionary if it was not there
        if start_of_the_month not in tempDic.keys():
            addThisDic = {}
            addThisDic[start_of_the_month] = dictionary
            self.__addDict(tempDic, addThisDic)

            # saving dictionary into the file
            self.__saveDictToFile(tempDic, name_of_dictionary)
        else:
            print('the month ' + start_of_the_month + ' has been found in dictionary ' + name_of_dictionary)

    ### safely open the dictionary from file
    def __safelyOpenDict(self, nameOfSavedDictionary):
        try:
            with open(nameOfSavedDictionary + '.pickle', 'rb') as handle:
                return pickle.load(handle)
        except FileNotFoundError:
            print("File was not found ")

    ### deleting a key from a dictionary
    def __delPartKey(self, key, nameOfDic):
        dic = self.__safelyOpenDict(nameOfDic)

        if key in dic.keys():
            del (dic[key])

        self.__saveDictToFile(dic, nameOfDic)

    ## SCRAPING functions

    ## function that scrapes another link
    ### add checkers whether types are matching
    def __findAllInBs(self, beautifulSoup, textClass, itemprop=False, p='p'):
        text = ''
        if itemprop:
            for txt in beautifulSoup.find_all(p, class_=textClass, itemprop="articleBody"):
                text = text + ' ' + txt.text
            return text
        else:
            for txt in beautifulSoup.find_all(p, class_=textClass):
                text = text + ' ' + txt.text
            return text

    ## function that extract text, for Nytimes we have several classes of the text
    def __extractText(self, beautifulSoup, textClass=1):
        text = ''
        if textClass == 1:
            cls = "story-body-text"
            return self.__findAllInBs(beautifulSoup, cls, itemprop=True)
        elif textClass == 2:
            cls = "story-body-text story-content"
            return self.__findAllInBs(beautifulSoup, cls)
        elif textClass == 3:
            ### seems to be valid for video section, that I pruned away
            cls = "content-description"
            return self.__findAllInBs(beautifulSoup, cls)

    ## function that removes some garbage from the text
    def __removeTextGarbage(self, text, textClass=1):
        if textClass == 1:
            text = re.sub('\n', ' ', text)
            text = text.split('.')
            # get rid of two last sentences for text from textClass=1
            del (text[-1])
            del (text[-1])
            # join the text back to pre-cleaned text
            text = '. '.join(text)
            text += '.'
            return text

    ## function that finds a missing part of dictionary B in dictionary A
    def __findMissingDic(self, dicA, dicB):
        tempDic = {}
        for key in dicB.keys():
            if key not in dicA.keys():
                self.__addDict(tempDic, {key: dicB[key]})
        return tempDic

    ## this function adds and saves dictionaryToAdd to the saved dictionary called nameOfDictionary
    def __saveDictNytFullText(self, dictionaryToAdd, nameOfDictionary):

        # I will try to open a dictionary
        tempDic = self.__openDict(nameOfDictionary)

        # add a dictionary to current dictionary if it was not there
        # find Missing compares the two dictionaries and returns ids of all members of dictionary that
        # are not in tempDic
        missingIntempDic = self.__findMissingDic(tempDic, dictionaryToAdd)
        if len(missingIntempDic):
            print('adding some missing stuff to dictionary')
            self.__addDict(tempDic, missingIntempDic)

            # saving dictionary into the file
            self.__saveDictToFile(tempDic, nameOfDictionary)
        else:
            print('Everything seems to be already in the saved dictionary ' + nameOfDictionary + '.pickle')

    ## function retrieves the text and if necessary adds to a badLinkList, NOTICE NOTICE NOTICE this function depends
    ## on number of text classes you have
    def __getText(self, link, badLinkList, numberOfTextClasses):

        try:
            req = urllib.request.Request(link, None)
            cj = CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            response = opener.open(req)
            raw_response = response.read()
            response.close()

            bss = bs(raw_response, "html.parser")

            # this part is responsible for getting the nonzero text
            textClass = 1
            text = ''
            while textClass <= numberOfTextClasses:
                print(textClass)
                tempText = self.__extractText(bss, textClass=textClass)
                if len(tempText) > len(text):
                    text = tempText
                textClass += 1
            # if number of characters is smaller than 55 chars something is wrong, put link into the badLinkList
            if len(text) < 55:
                badLinkList.append(text)
                print('Check the bad link list, because there are ' + str(len(badLinkList)) + ' already ' +
                      'and one was just added! It is possible that there is another textClass among them or something else'
                      ' is not working properly.')
            return text

        except urllib.request.HTTPError as inst:
            output = format(inst)
            print(output)
            raise

    ## this function queries the NYT server, scrape the page and retrieve text, save it to: nameOfFile
    ## remember use the pruned dictionary
    def __downloadNytText(self, urlDic, nameOfFile):
        if (nameOfFile + '.pickle') in os.listdir():
            print(
                'ERROR: ALREADY USED name for requested file: ' + nameOfFile + '.pickle' + ',   USE different filename!')
        else:
            totalNumberOfErrors = 1000
            numberOfErrors = 0
            finalDic = {}
            badLinkList = []
            counter = 1

            ### we have to catch the HTTP errors
            for articleKey in urlDic.keys():
                try:
                    print('work in progress, step: ' + str(counter))
                    print('working on article with id: ' + articleKey)

                    # print(urlDic[articleKey])
                    text = self.__getText(urlDic[articleKey], badLinkList, 2)
                    # print(text)
                    counter += 1

                    if text != None and len(text) < 55:
                        print('continue')
                        continue
                    else:
                        finalDic[articleKey] = text

                    ## for sureness save it to disc immediately every 20 articles:
                    if (counter % 20) == 0:
                        self.__saveDictNytFullText(finalDic, nameOfFile)

                    ## waiting some random time to not be blocked (at least fast)
                    self.__waitRandomTime()

                except (urllib.request.HTTPError, HTTPError):
                    numberOfErrors += 1
                    print('ERROR nr. ' + str(numberOfErrors))
                    print('there was some HTTP error, it might be they have blocked you, '
                          'I will wait for some longer time and will query again')
                    print('I will do that until total number errors is smaller than ' + str(totalNumberOfErrors))

                    if numberOfErrors <= totalNumberOfErrors:
                        self.__waitRandomTime(15)
                        continue
                    else:
                        print('-----------END------BECAUSE---HTTP----ERROR---DID---NOT--STOP')
                        print('last article id was: ' + str(articleKey))
                except urllib.error.URLError as e:
                    print('URLError---URLError---URLError--URLError--URLError')
                    numberOfErrors += 1
                    print('ERROR nr. ' + str(numberOfErrors))
                    print('there was some HTTP error, it might be they have blocked you, '
                          'I will wait for some longer time and will query again')
                    print('I will do that until total number errors is smaller than ' + str(totalNumberOfErrors))

                    if numberOfErrors <= totalNumberOfErrors:
                        self.__waitRandomTime(15)
                        continue
                    else:
                        print('-----------END------BECAUSE---HTTP----ERROR---DID---NOT--STOP')
                        print('last article id was: ' + str(articleKey))

            ## saving what I have in final dic
            print('saving what I have in final dic ')
            self.__saveDictNytFullText(finalDic, nameOfFile)

            return badLinkList

    ## by this function you are getting the text from Nytimes, the year you are getting is dependent ONLY on
    ## the name of the dictionary nameOfUrlLinksDictionary
    def __getNytText(self, nameOfTextDictOnDisk, nameOfUrlLinksDictionary, year):

        ### creating the customary names
        nameOfTextDictOnDisk = nameOfTextDictOnDisk + str(year)
        nameOfUrlLinksDictionary = nameOfUrlLinksDictionary + str(year)

        urlDic = self.__findUrlLinksPrunedDictionary(nameOfUrlLinksDictionary)
        print('creating the url dictionary that is pruned')

        if len(urlDic) > 0:
            print('downloading the Nyt for the Url dictionary ' + nameOfUrlLinksDictionary)
            badLinkList = self.__downloadNytText(urlDic, nameOfTextDictOnDisk)
            if len(badLinkList) > 0:
                print('there are some links that have not been turned into text see saved badLinkList for current year')
                self.__saveList(badLinkList, ('badLinkList' + str(year)))
            else:
                print('everything seems to be turned into text check results saved in: ' + nameOfTextDictOnDisk)
        else:
            print('CHECK: for some reason the created urlDic is empty')

    ## querying through months
    def __queryThroughMonths(self, queryList, year=2016):
        for month in range(1, 13):
            try:
                print('dealing with month nr.: ' + str(month))
                rang = calendar.monthrange(year, month)
                start = datetime.date(year=year, month=month, day=1).strftime("%Y%m%d")
                end = datetime.date(year=year, month=month, day=rang[1]).strftime("%Y%m%d")

                docName = 'nytSnippets' + str(year)
                if (docName + '.pickle') in os.listdir():
                    temp = self.__safelyOpenDict(docName)

                    if start not in temp.keys():
                        dic = self.__getNYTsnippets(queryList, startDate=start, endDate=end)
                        self.__saveDict(dic, docName, start)
                    else:
                        print('skipping month ' + start + ' because already in database')
                else:
                    dic = self.__getNYTsnippets(queryList, startDate=start, endDate=end)
                    self.__saveDict(dic, docName, start)

                print('finished and saved month nr.: ' + str(month) + 'for year :' + str(year))

            except (urllib.request.HTTPError, HTTPError):
                #logging.error("HTTPError: with code: %s and with reason: %s", e.code, e.reason)
                print('there was some error in month ' + str(month) + ' see the logs')
                continue

    ### !!!!!!!!!!------->>>>>> NOTE NOTE NOTE not tested function

    ## final function that allows you to get data between years startYear and endYear
    def getDataNytimes(self, startYear, endYear):
        ### looping through the years
        for year in range(startYear, endYear + 1):

            ### if number of queries is bigger than total number of queries allowed bail
            if self.__numberOfUsedQueries > self.__totalNumberOfAllowedQueries:
                break
            else:
                try:
                    print('START querying the year: ' + str(year))
                    print('TOTAL number of queries used: ' + str(self.__numberOfUsedQueries))

                    ### this queries through months and saves result
                    self.__queryThroughMonths(self.__queryList, year)

                    nameOfSnippetDictionary = 'nytSnippets' + str(year)
                    print('FINISHED querying for the year: ' + str(year) + 'checking whether you have file: '
                          + nameOfSnippetDictionary + '.pickle saved in directory')

                    if (nameOfSnippetDictionary + '.pickle') in os.listdir():
                        print(nameOfSnippetDictionary + '.pickle is in directory')
                        print('everything seems to be OK')
                    else:
                        print('ERROR:' + nameOfSnippetDictionary + '.pickle was NOT found directory')
                        break

                    ### in this part you creates the pruned dictionary to be used in actual downloading of the data
                    ### this is for current year
                    dicToDownload = self.__findUrlLinksPrunedDictionary(nameOfSnippetDictionary)

                    ### downloading the dicToDownload
                    print('starting to download the text for year: ' + str(year))

                    print('first check whether you already do not have the file on disc if yes skip and report')
                    nameOfRawTextDictionary = 'nytRawText' + str(year) + '.pickle'

                    if nameOfRawTextDictionary not in os.listdir():
                        print('the raw text dictionary with name: ' + nameOfRawTextDictionary + '.pickle' +
                              ' has not been found on local drive. I will proceed to download it.')
                        badLinkList = self.__getNytText('nytRawText', 'nytSnippets', year)
                        print('stopped the text download for year ' + str(year))
                    else:
                        print('the raw text dictionary with name: ' + nameOfRawTextDictionary + '.pickle' +
                              ' HAS BEEN found on local drive. I will NOT download it.')
                        print('please check whether you have everything you wanted in ' +
                              nameOfRawTextDictionary + '.pickle')

                    ### checking whether you have saved at least something on disc
                    if nameOfRawTextDictionary not in os.listdir():
                        print('the raw text dictionary with name: ' + nameOfRawTextDictionary + '.pickle' +
                              ' has not been found on local drive. I will proceed to download it.')

                    else:
                        print('the raw text dictionary with name: ' + nameOfRawTextDictionary + '.pickle' +
                              ' HAS BEEN found on local drive. SOMETHING is wrong!!!!')
                        break


                        ### waiting some random time in order not to be blocked or at least not that fast
                except (urllib.request.HTTPError, HTTPError):
                    #logging.error("HTTPError: with code: %s and with reason: %s", e.code, e.reason)
                    print('there was HTTP error ' + ' see the logs')
                    continue
        return badLinkList














