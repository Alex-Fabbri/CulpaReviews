'''
This file contains positive/negative classifiers that we were considering using, 
but which ultimately were too finicky and were giving too many innacurate results to 
be ultimately helpful for the user. You can test your own text file by calling the 
functions below on that file. 
'''


import pickle
import nltk.classify.util
from nltk.corpus import movie_reviews
 
'''
This is a very basic feature extraction that just puts the individual words
into a dictionary
''' 
def word_feats(words):
    return dict([(word, False) for word in words])
 
negativeids = movie_reviews.fileids('neg')
positiveids = movie_reviews.fileids('pos')
 
negativefeatures = [(word_feats(movie_reviews.words(fileids=[f])), 'negative') for f in negativeids]
positivefeatures = [(word_feats(movie_reviews.words(fileids=[f])), 'positive') for f in positiveids]

negcutoff = len(negativefeatures)*3/4
poscutoff = len(positivefeatures)*3/4 
 
trainfeatures = negativefeatures[:negcutoff] + positivefeatures[:poscutoff]
testfeatures = negativefeatures[negcutoff:] + positivefeatures[poscutoff:]
'''
test uses a classifier made from the list of positive and negative words. 
'''


def testPosNegWords(fileName = "testCULPA.txt"):
    f = open('my_classifierPosNegWords.pickle')
    classifier = pickle.load(f)
    f.close()
    print ('The accuracy of classifier based only on positive and negative words being tested on movie reviews: ' + str(nltk.classify.util.accuracy(classifier, testfeatures)))
    testfile = open(fileName,  'r')
    lines = testfile.readlines()
    print("The Pos/NegWord ckassifier classifies this document as: " + classifier.classify(word_feats(lines)))

def testMovieClassifier(fileName = "testCULPA.txt"):
    f = open('my_Movieclassifier.pickle')
    classifier = pickle.load(f)
    f.close()
    testfile = open('testCULPA.txt', 'r')
    lines = testfile.readlines()
    print("The accuracy of the classifier based on the movie review corpus of data: " + str(nltk.classify.util.accuracy(classifier, testfeatures)))
    print("The MovieReview classifier classifies this document as: " +  classifier.classify(word_feats(lines)))



testPosNegWords()
testMovieClassifier()
