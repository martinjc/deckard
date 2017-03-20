#!/usr/bin/env python

import random
import string
import argparse

from twython import Twython

from _credentials import *

class Markov(object):

    def __init__(self, open_file):
        self.cache = {}
        self.open_file = open_file
        self.words = self.file_to_words()
        self.word_size = len(self.words)
        self.database()


    def file_to_words(self):
        self.open_file.seek(0)
        data = self.open_file.read()
        words = data.split()
        words = [word for word in words if word.find('http') < 0 and word.find('@') < 0]
        return words


    def triples(self):

        if len(self.words) < 3:
                return

        for i in range(len(self.words) - 2):
                yield (self.words[i], self.words[i+1], self.words[i+2])

    def database(self):
        for w1, w2, w3 in self.triples():
                key = (w1, w2)
                if key in self.cache:
                        self.cache[key].append(w3)
                else:
                        self.cache[key] = [w3]

    def generate_markov_text(self, size=25, word=None):
        seed = random.randint(0, self.word_size-3)
        if word:
            seed_word = word
            seed_word_indexes = [i for i,x in enumerate(self.words) if x.lower() == seed_word.lower()]
            seed_word_index = random.choice(seed_word_indexes)
            if seed_word_index != -1 and seed_word_index < len(self.words):
                seed_word, next_word = self.words[seed_word_index], self.words[seed_word_index+1]
            else:
                seed_word, next_word = self.words[seed], self.words[seed+1]
        else:
            seed_word, next_word = self.words[seed], self.words[seed+1]
        w1, w2 = seed_word, next_word
        gen_words = []
        for i in range(size):
                gen_words.append(w1)
                w1, w2 = w2, random.choice(self.cache[(w1, w2)])
        gen_words.append(w2)
        return ' '.join(gen_words)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Markov tweeting')
    parser.add_argument('screen_name', help='Screen name to impersonate tweets of')
    parser.add_argument('--word', help='Starting word')
    args = parser.parse_args()

    screen_name = args.screen_name
    word = args.word

    punc = '.)!?'

    with open("cache/%s_tweets.txt" % screen_name, "r") as input_file:

        markov = Markov(input_file)
        text = markov.generate_markov_text(35, word)
        last_break = 0
        if len(text) > 140:
            text = text[:140]
            print(text)
            for char in punc:
                if text.rfind(char) > last_break:
                    last_break = text.rfind(char)
                    print(last_break)
            text = text[:last_break+1]

        print(text)

        api = Twython(client_id, client_secret, access_token, access_secret)

        api.update_status(status=text)
