import math, collections


# usage:
# trainPath = '../data/holbrook-tagged-train.dat'
# trainingCorpus = HolbrookCorpus(trainPath) 
# trigramLanguageModel = TrigramModel(trainingcorpus)
# score = trigramLanguageModel.score(string here)
class TrigramModel:

  def __init__(self, corpus):
    """Initialize your data structures in the constructor."""
    self.trigramCounts = collections.defaultdict(lambda: 0)
    self.bigramCounts = collections.defaultdict(lambda: 0)
    self.unigramCounts = collections.defaultdict(lambda: 0)
    self.unigramtotal = 0
    self.train(corpus)

  def train(self, corpus):
    """ Takes a corpus and trains your language model. 
        Compute any counts or other corpus statistics in this function.
    """  
    for sentence in corpus.corpus:
      for i in xrange(0, len(sentence.data) - 2):
        first = sentence.data[i].word
        second = sentence.data[i+1].word
        third = sentence.data[i+2].word
        trigram = first + "&" + second + "&" + third
        self.trigramCounts[trigram] = self.trigramCounts[trigram] + 1

      for i in xrange(0, len(sentence.data) - 1):
        first = sentence.data[i].word
        second = sentence.data[i+1].word
        bigram = first + "&" + second
        self.bigramCounts[bigram] = self.bigramCounts[bigram] + 1
      
      for datum in sentence.data:  
        first = datum.word
        self.unigramCounts[first] = self.unigramCounts[first] + 1
        self.unigramtotal = self.unigramtotal + 1

  def score(self, sentence):
    """ Takes a list of strings as argument and returns the log-probability of the 
        sentence using your language model. Use whatever data you computed in train() here.
    """
   
    score = 0.0 
    for i in xrange(0,len(sentence) - 2):
      first = sentence[i]
      second = sentence[i+1]
      third = sentence[i+2]
      
      trigram = first + "&" + second + "&" + third
      trigramcount = self.trigramCounts[trigram]

      bigram = first + "&" + second
      bigramcount = self.bigramCounts[bigram]
      
      if trigramcount > 0:
        #tri-gram
        score += math.log(trigramcount) 
        score -= math.log(bigramcount)
      elif bigramcount > 0:  
        #Bi-gram
        score += math.log(bigramcount)
        score -= math.log(self.unigramCounts[first])
      else:
        #Laplace Unigram
        score += math.log(self.unigramCounts[second] + 1) 
        score -= math.log(self.unigramtotal + len(self.unigramCounts))  
    return score