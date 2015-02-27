import math, collections

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
    nGramsFile = open(corpus, 'r')
    for line in nGramsFile:
      count, first, second, third = line.split()
      count = int(count)
      
      trigram = first + "&" + second + "&" + third
      self.trigramCounts[trigram] += count
      
      bigram = first + "&" + second
      self.bigramCounts[bigram] += count
      bigram = second + "&" + third
      self.bigramCounts[bigram] += count
      
      self.unigramCounts[first] += count
      self.unigramCounts[second] += count
      self.unigramCounts[third] += count
      self.unigramtotal += 3*count     

  def findMostLikely(self, sentences):
    bestScore = float('-inf')
    bestSentence = ""
    for sentence in sentences:
      sentenceScore = self.score(sentence.split())
      if sentenceScore > bestScore:
        bestScore = sentenceScore
        bestSentence = sentence
    return bestSentence

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
        score += 0.1*math.log(bigramcount)
        score -= 0.1*math.log(self.unigramCounts[first])
      else:
        #Laplace Unigram
        score += 0.01*math.log(self.unigramCounts[second] + 1) 
        score -= 0.01*math.log(self.unigramtotal + len(self.unigramCounts))  
    return -score