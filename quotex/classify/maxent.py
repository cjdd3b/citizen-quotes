'''
maxent.py

Tools and wrappers to facilitate quote classification using a Maximum Entropy Model
classifier from NLTK. 

More information about the math can be found here:
http://en.wikipedia.org/wiki/Principle_of_maximum_entropy

Great description of the algorithm here:
http://www.cs.cmu.edu/afs/cs/user/aberger/www/html/tutorial/tutorial.html

And here's some reference info for maxent in NLTK:
http://nltk.googlecode.com/svn/trunk/doc/book/ch06.html
'''
import nltk
from nltk.classify import MaxentClassifier
from apps.content.models import Paragraph
from classify.features import *

########## FEATURE AGGREGATOR ##########

def get_features(words):
    '''
    Function that aggregates active features for the maxent classifier and returns
    a feature dict in the format expected by NLTK.
    '''
    features = {} # Start with empty feature dict

    # Put features here (found in classify.features)
    features['contains_quotes'] = contains_quotes(words)
    features['first_quote_index'] = first_quote_index(words)
    features['last_word_%s' % last_word(clean_text(words))] = True
    features['said_near_source'] = said_near_source(words)
    features['num_words_between_quotes'] = num_words_between_quotes(words)
    for word in words_near_quotes(words):
        features['%s_near_quote' % word] = True

    return features

########## MAXENT WRAPPER CLASS ##########

class MaxentWrapper(object):
    '''
    Simple wrapper around NLTK's maxent classifier to facilitate training
    and evaluation.
    '''
    def __init__(self, train):
        self.train = train # Init requires training data

    def _train(self, algo='iis', trace=0, max_iter=10):
        '''
        Internal method to train and return a NLTK maxent classifier.
        ''' 
        data = [(p.text, p.quote) for p in train_query]
        train_set = [(get_features(n), g) for (n, g) in data]
        return MaxentClassifier.train(train_set, algorithm=algo, trace=trace, max_iter=max_iter)

    def evaluate(self, test):
        '''
        Evaluate the performance of a test set. The test set should contain labeled data,
        just like a training set. The purpose of this method is to see how well your trained
        classifier performs on quotes you have already vetted and classified. Takes a list or
        queryset of Paragraph objects as input.
        '''
        classifier = self._train() # Get the classifier

        true_pos, false_pos, true_neg, false_neg = 0, 0, 0, 0
        for item in test:
            # Ground truth data. The quote status should already be flagged manually in the test
            # set before you run this.
            truth = item.quote

            # Create a classifier with features extracted from the item text
            features = get_features(item.text)
            classify = classifier.prob_classify(features)
            guess = classify.max() # Return guess with the highest probability.

            # Add up true positives, false positives, true negatives and false negatives. Also
            # print the text and feature sets for false positives and false negatives so problems
            # are easier to diagnose.
            if truth == True and guess == True:
                true_pos += 1
            elif truth == True and guess == False:
                print item.text
                print features
                false_neg += 1
            elif truth == False and guess == False:
                true_neg += 1
            elif truth == False and guess == True:
                false_pos += 1
                print item.text
                print features

        # Print stats
        print 'True positives: %s' % true_pos
        print 'False positives: %s' % false_pos
        print 'True negatives: %s' % true_neg
        print 'False negatives: %s' % false_neg

        # Return the 10 most useful features learned by the classifier
        print classifier.show_most_informative_features(10)
        return

    def classify(self, to_classify):
        '''
        Classify a set of unlabeled data, given a training set. Takes a list or queryset of
        Paragraph objects as input.
        '''
        classifier = self._train() # Get the classifier
        for item in to_classify:

            # Create a classifier with features extracted from item text
            features = get_features(item.text)
            classify = classifier.prob_classify(features)
            guess = classify.max()

            # Because this is a proabilistic classifier, we can get the probability
            # score of a given guess, which can be seen as an indicator of certainty.
            certainty = float(classify.prob(guess))

            # Save the Paragraph object to the database
            item.quote = guess
            item.score = certainty
            item.save()
        return

########## MAIN ##########

if __name__ == '__main__':
    # Train and test querysets for evaluate method
    training_set = Paragraph.training.all()
    train_query = training_set[:len(training_set)/2]
    test_query = training_set[len(training_set)/2:]

    # Unlabeled data for the classify method
    unlabeled = Paragraph.unclassified.all()

    # Evaluate and classify
    me_classifier = MaxentWrapper(train_query)
    me_classifier.evaluate(test_query)
    #me_classifier.classify(unlabeled)
