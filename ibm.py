import itertools as it
import collections
import re
import string
import sys

from collections import defaultdict
from itertools import izip

class IBM:

    def __init__(self, sentences):
        # For holding the data - initialized in read_data()
        self.words = {} #2d array of [e][f] word mapping probabilities
        self.dictionary = defaultdict(lambda: "")
        self.sentences = sentences[:];
        self.english_words = set()
        self.spanish_words = set()
        self.NUM_ROUND = 1
        self.progress = 0
        self.maxIter = 10

    def parse_words(self):

        for (en_sent, es_sent) in self.sentences:
            for en_word in en_sent:
                self.english_words.add(en_word)
            for es_word in es_sent:
                self.spanish_words.add(es_word)

        uniform_val = 1.0 / len(self.english_words)
        self.words = defaultdict(lambda: defaultdict(lambda: uniform_val))

    def EM(self):

        self.progress += 1
        count = defaultdict(lambda: defaultdict(lambda: 0.0))
        total = defaultdict(lambda: 0.0)

        for (en_sent, es_sent) in self.sentences:
            for en_word in en_sent:
                total_s = 0
                for es_word in es_sent:
                    total_s += self.words[es_word][en_word]

                total_s = float(total_s)
                for es_word in es_sent:
                    count[es_word][en_word] += self.words[es_word][en_word] / total_s
                    total[es_word] += self.words[es_word][en_word] / total_s

        for es_word in self.words:
            for en_word in self.words[es_word]:
                count[es_word][en_word] = count[es_word][en_word] / total[es_word]

        return count

    def mapEquals(self, map1, map2):
        for key1 in map1:
            for key2 in map1[key1]:
                if round(map1[key1][key2], self.NUM_ROUND) != round(map2[key1][key2], self.NUM_ROUND): return False
        return True

    def makeDict(self):
        for es_word in self.spanish_words:
            max_prob = -1
            for en_word in self.words[es_word]:
                if self.words[es_word][en_word] > max_prob:
                    max_prob = self.words[es_word][en_word]
                    self.dictionary[es_word] = en_word

    def preprocess(self):
        self.parse_words()
        newMap = self.EM()               # called over and over again
        while (not self.mapEquals(self.words, newMap)):
            if self.progress % 1 is 0:
                sys.stdout.write(str(self.progress) + ".."),
                sys.stdout.flush()
            if self.progress is self.maxIter: break
            self.words = newMap
            newMap = self.EM()

        self.words = newMap
        self.makeDict()

        return self.words

    def translate(self, sentence):
        trans_sent = ""
        for word in sentence.split():
            trans_sent += " " + self.dictionary[word]

        return trans_sent

def loadSentences(englishFileName, foreignFileName) :
    sentences = []
    with open(englishFileName, 'r') as englishFile, open(foreignFileName, 'r') as foreignFile:
        for englishSentence, foreignSentence in izip(englishFile, foreignFile):
            englishSentence = sanitize(englishSentence)
            foreignSentence = sanitize(foreignSentence)
            tupl = (englishSentence.split(), foreignSentence.split())
            sentences.append(tupl)
    return sentences

def sanitize(sentence) :
    sentence = sentence.lower()
    puncRegex = re.compile("[" + string.punctuation + "]", re.IGNORECASE)
    sentence = puncRegex.sub(' ', sentence)
    sentence = sentence.strip()
    return sentence

def main():

    ibm = IBM(loadSentences("europarl-v7.es-en.en", "europarl-v7.es-en.es"))
#    ibm = IBM(loadSentences("test.en", "test.es"))
    result = ibm.preprocess()
    print '\n\n'

    with open("testsentences", 'r') as testFile:
        for testSentence in testFile:
            result = ibm.translate(sanitize(testSentence))

    while (True):
        sentence = raw_input('==> ')
        result = ibm.translate(sanitize(sentence))
        print result

if __name__ == '__main__':
    main()
