import pickle
import numpy as np
import pandas as pd
from math import log
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')


def process_text(text, lower_case=True, stem=True, stop_words=True, gram=2):
    if lower_case:
        text = text.lower()
    words = word_tokenize(text)  # sentence is converted into a group of words
    # only those words whose length >2 are included in word list
    words = [w for w in words if len(w) > 2]
    if gram > 1:
        w = []
        for i in range(len(words) - gram + 1):
            # joining the words back to sentences
            w += [' '.join(words[i:i + gram])]
        return w
    if stop_words:
        # removing meaningless words like of,is,are,the etc
        sw = stopwords.words('english')
        words = [word for word in words if word not in sw]
    if stem:
        stemmer = PorterStemmer()
        # similar meaning words are converted are replaced by one single word eg:go,going,gone-->go
        words = [stemmer.stem(word) for word in words]
    return words


class Classifier(object):
    def __init__(self, trainData):
        # text data and its labels from dataset are stored in 2 diff variables
        self.text, self.labels = trainData['text'], trainData['label']

    def train(self):
        # converting words to vectors for caluculation because computer cannot understand words
        self.calc_TF_and_IDF()
        self.calc_TF_IDF()  # TF-Idf technique is used

    def calc_TF_and_IDF(self):
        # no. of rows in text i.e total no. of sentences
        noOftext = self.text.shape[0]
        self.depressive_text, self.positive_text = self.labels.value_counts()[
            1], self.labels.value_counts()[0]  # no. of depressive and positive words are counted based on labels given
        self.total_text = self.depressive_text + self.positive_text
        self.depressive_words = 0
        self.positive_words = 0
        self.tf_depressive = dict()
        self.tf_positive = dict()
        self.idf_depressive = dict()
        self.idf_positive = dict()
        for i in range(noOftext):
            # each sentence is sent for data cleaning
            text_processed = process_text(self.text.iloc[i])
            count = list()
            for word in text_processed:  # after cleaning for remaining words checking labels and counting
                if self.labels.iloc[i]:  # label for depressive sentences is 1
                    self.tf_depressive[word] = self.tf_depressive.get(
                        word, 0) + 1  # counting the number of times the depressing word appears in the sentence
                    self.depressive_words += 1  # counting the total number of depressive words
                else:
                    # counting the number of times the poitive word appears in the sentence
                    self.tf_positive[word] = self.tf_positive.get(word, 0) + 1
                    self.positive_words += 1  # counting the total number of positive words
                if word not in count:
                    # creating a list of unique words for each sentence
                    count += [word]
            for word in count:
                if self.labels.iloc[i]:
                    self.idf_depressive[word] = self.idf_depressive.get(
                        word, 0) + 1  # number of times the unique depressive word appears in the sentence
                else:
                    self.idf_positive[word] = self.idf_positive.get(
                        word, 0) + 1  # number of times the unique positive word appears in the sentence

    def calc_TF_IDF(self):
        # Tf-Idf is used to weight words according to how important they are. Words that are used frequently in many documents will have a lower weighting while infrequent ones will have a higher weighting. Below is the formula: w(i,j) = TF(i,j) * log(N / IDF(i)) Here, N = total sentences
        # For training it calculates the tf_idf score by summing tf-idf values and the total is then divided by the summation of all the document tf-idf values.
        # This tf-idf weighting scheme is used to score sentence’s relevance given a user query.
        self.prob_depressive = dict()
        self.prob_positive = dict()
        self.sum_tf_idf_depressive = 0
        self.sum_tf_idf_positive = 0
        for word in self.tf_depressive:
            self.prob_depressive[word] = (self.tf_depressive[word]) * log((self.depressive_text + self.positive_text)
                                                                          / (self.idf_depressive[word] + self.idf_positive.get(word, 0)))
            # sum of tf-idf values is caluculated by adding each word's value
            self.sum_tf_idf_depressive += self.prob_depressive[word]

        for word in self.tf_depressive:  # caluculates tf-idf score
            self.prob_depressive[word] = (self.prob_depressive[word] + 1) / (
                self.sum_tf_idf_depressive + len(list(self.prob_depressive.keys())))

        for word in self.tf_positive:
            self.prob_positive[word] = (self.tf_positive[word]) * log((self.depressive_text + self.positive_text)
                                                                      / (self.idf_depressive.get(word, 0) + self.idf_positive[word]))
            # sum of all tf-idf values for each word
            self.sum_tf_idf_positive += self.prob_positive[word]

        for word in self.tf_positive:
            self.prob_positive[word] = (self.prob_positive[word] + 1) / (
                self.sum_tf_idf_positive + len(list(self.prob_positive.keys())))  # total tf-idf score

        self.prob_depressive_text, self.prob_positive_text = self.depressive_text / \
            self.total_text, self.positive_text / self.total_text

    def classify(self, processed_text):
        pDepressive, pPositive = 0, 0
        for word in processed_text:
            if word in self.prob_depressive:
                pDepressive += log(self.prob_depressive[word])
            else:
                pDepressive -= log(self.sum_tf_idf_depressive +
                                   len(list(self.prob_depressive.keys())))
            if word in self.prob_positive:
                pPositive += log(self.prob_positive[word])
            else:
                pPositive -= log(self.sum_tf_idf_positive +
                                 len(list(self.prob_positive.keys())))
            pDepressive += log(self.prob_depressive_text)
            pPositive += log(self.prob_positive_text)
        return pDepressive >= pPositive

    def predict(self, testData):
        result = dict()
        for (i, text) in enumerate(testData):
            processed_text = process_text(text)
            result[i] = int(self.classify(processed_text))
        return result


Data = pd.read_csv("data.csv")  # reading dataset
# gives count of number of depressive and positive sentences
Data['label'].value_counts()

Model = Classifier(Data)  # creatng object of classifier class
Model.train()  # training the model object

filename = "finalized_model.sav"
pickle.dump(Model, open(filename, 'wb'))
