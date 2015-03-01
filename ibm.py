import itertools as it
import collections
import re
import string
import sys
import heapq
from TrigramModel import TrigramModel
import nltk
import chardet
from collections import defaultdict
from itertools import izip

class IBM:

    def __init__(self, sentences):
        # for holding the data - initialized in read_data()
        self.words = {} # 2d array of [e][f] word mapping probabilities
        self.dictionary = defaultdict(lambda: "")
        self.sentences = sentences[:];
        self.grams_n = 3
        self.english_words = set()
        self.spanish_words = set()
        self.progress = 0
        self.maxIter = 10
        self.threshold = .35

    def set_threshold(self, thres):
        self.threshold = thres

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
                total_s = 0.0
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
        print "Transforming to map..."
        for es_word in self.spanish_words:
            words = []

            for en_word in self.words[es_word]:
                prob = self.words[es_word][en_word]
                heapq.heappush(words, (prob, en_word))
                if len(words) > self.grams_n: heapq.heappop(words)

            self.dictionary[es_word] = heapq.nlargest(self.grams_n, words)

    def preprocess(self):
        self.parse_words()
        newMap = self.EM()               # called over and over again
        while (True):
            if self.progress % 1 is 0:
                sys.stdout.write(str(self.progress) + ".."),
                sys.stdout.flush()
            if self.progress is self.maxIter: break
            self.words = newMap
            newMap = self.EM()

        print "done!"
        self.words = newMap
        self.makeDict()

        return self.words

    def addCandidatesToSentence(self, partial, sentence, sentences):
        if len(sentence) is 0:
            sentences.append(partial[1:])
            return

        word = sentence[0]
        candidates = self.dictionary[word]

        if len(candidates) is 0:
            self.addCandidatesToSentence(partial + " " + word, sentence[1:], sentences)
            return

        if candidates[0][0] < self.threshold:
            self.addCandidatesToSentence(partial + " " + candidates[0][1], sentence[1:], sentences)
            return

        for i in range(len(candidates)):
            if i < self.grams_n and candidates[i][0] > self.threshold:
                self.addCandidatesToSentence(partial + " " + candidates[i][1], sentence[1:], sentences)

    def translate(self, sentence):
        sentences = []
        self.addCandidatesToSentence("", sentence.split(), sentences)
        return sentences

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
    # puncRegex = re.compile("[" + string.punctuation + "]", re.IGNORECASE)
    # puncRegex = re.compile("[,.?]", re.IGNORECASE)
    # sentence = puncRegex.sub(' ', sentence)
    # sentence = sentence.strip()
    return sentence

def postProcess(result):
    newResult = []
    for sentence in result:
        newResult.append(processSentence(sentence))

    return newResult

def takeOutUnicode(sentence):
    newSentence = []
    for word in sentence.split():
        encoding = chardet.detect(word)
        if encoding['encoding'] == 'ascii' and word.isalpha():
            newSentence.append(word)
    result = ""
    for word in newSentence:
        result += word + " "
    return result

def makeSwitch(sentence, noun, adj):
    allWords = sentence.split()
    index = 0
    prevWord = "NOT"
    for word in allWords:
        if prevWord == noun and word == adj:
            allWords[index - 1] = adj
            allWords[index] = noun
            break
        index += 1
        prevWord = word
    result = ""
    for word in allWords:
        result += word + " "
    return result

def processSentence(sentence):
    processSentence = takeOutUnicode(sentence)
    tokens = nltk.word_tokenize(processSentence)
    tags = nltk.pos_tag(tokens)
    # newSentence = []
    oldWord = ""
    preLabel = "PLACEHOLDER"
    for (word, label) in tags:
        if preLabel == "NN" and (label == "JJ" or label == "RB"):
            # oldWord = newSentence[len(newSentence) - 1]
            sentence = makeSwitch(sentence, oldWord, word)
            # newSentence[len(newSentence) - 1] = word
            # newSentence.append(oldWord)
        # else:
        #    newSentence.append(word)
        preLabel = label
        oldWord = word
    # result = ""
    # for word in newSentence:
    #     result += word + " "
    return sentence

def main():
    # initialize trigram model
    trigramLanguageModel = TrigramModel("data/es-en/train/europarl-v7.es-en.en")
    print 'Trigram Model Loaded! \n'

    ibm = IBM(loadSentences("data/es-en/train/europarl-v7.es-en.en", "data/es-en/train/europarl-v7.es-en.es"))
    result = ibm.preprocess()
    print 'Preproccess done! \n'

    
    while (True):
        kind = raw_input('Type (f, s, t): ')
        if kind is not "f" and kind is not "s" and kind is not "t": continue
        input_data = raw_input('==> ')
        if kind is "f":
            try:
                with open(input_data, 'r') as testFile:
                    bleuFile = open("output-" + input_data, "w+")
                    for testSentence in testFile:
                        result = ibm.translate(sanitize(testSentence)) # returns array of translations
                        result = postProcess(result)
                        # result = trigramLanguageModel.findMostLikely(result) # returns best scoring result
                        bleuFile.write(result[0] + "\n")
                    bleuFile.close()
            except:
                print "Filename invalid"
                continue
        elif kind is "s":
            result = ibm.translate(sanitize(input_data)) # returns array of translations
            result = postProcess(result)
            # result = trigramLanguageModel.findMostLikely(result) # returns best scoring result
            print result[0]
        elif kind is "t":
            ibm.set_threshold(float(input_data))
            print "Set threshold to: " + input_data

if __name__ == '__main__':
    main()
