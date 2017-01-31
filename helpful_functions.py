import pickle
import time
import os
import random
# opening the file from the function


def safely_open(name_of_saved_dictionary, pick):
    try:
        if pick:
            with open(name_of_saved_dictionary + '.pickle', 'rb') as handle:
                return pickle.load(handle)
        else:
            with open(name_of_saved_dictionary, 'rb') as handle:
                return pickle.load(handle)
    except (NameError, FileNotFoundError):
        print("File was not found ")


# updating final by temp, if final has the same key as temp, then temp value is gonna prevail


def add_dict(final, temp):
    z = dict(final, **temp)
    final.update(z)

# find unique members in given sequence


def uniqify(seq):

    # Not order preserving
    keys = {}
    for e in seq:
        keys[e] = 1
    return list(keys.keys())

# saves dictionary to file


def save_to_file(object_to_save, name_on_disc, pick):
    if pick:
        with open(name_on_disc + '.pickle', 'wb') as handle:
            pickle.dump(object_to_save, handle)
    else:
        with open(name_on_disc, 'wb') as handle:
            pickle.dump(object_to_save, handle)


# generates local time suffix

def generate_local_time_suffix():
    return '_'.join([str(x) for x in list(time.localtime())[0:6]])


# answers whether some file is in directory
def is_in_directory(name_of_file, pick):
    if pick:
        return (name_of_file + ".pickle") in os.listdir()
    else:
        return name_of_file in os.listdir()

# function that forces system to wait random time, with upper bound on wait equals to maxTime
def wait_random_time(maxTime=7):

    # setting up the seed
    tm = int(round(time.time()))
    random.seed(tm)

    tim = random.randint(0, 8 * 100) / 100.0
    time.sleep(tim)


def intersection(key1, key2):
    return set(key1) & set(key2)

