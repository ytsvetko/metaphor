#!/usr/bin/env python2.7

from __future__ import division
import cPickle
from itertools import izip_longest
import sys
import codecs
import argparse
import json
import gzip
from sklearn import svm
from sklearn import cross_validation
from sklearn import ensemble
from collections import Counter
import numpy as np

parser = argparse.ArgumentParser()

parser.add_argument("--train_features")
parser.add_argument("--train_labels")

parser.add_argument("--priors", default="{}",
    help="A dictionary of {'Label':prior, ... } or a string 'balanced'. " +
         "Asumes a prior of 1.0 for unspecified labels.")

parser.add_argument("--test_features")
parser.add_argument("--test_predicted_labels_out")
parser.add_argument("--golden_labels")
parser.add_argument("--classifier", default="RandomForest")
parser.add_argument("--num_cross_validation_folds", default=0, type=int)
parser.add_argument("--write_posterior_probabilities", default=False, action='store_true')
parser.add_argument("--write_class_confidence", default=False,  action='store_true')
parser.add_argument("--dump_classifier_filename", help="Saves a trained classifier to a file")
parser.add_argument("--load_classifier_filename")

args = parser.parse_args()

class StrEnumerator(object):
  def __init__(self):
    self.d = {}
    self.labels = []

  def __len__(self):
    return len(self.labels)

  def StrToNum(self, label, create_new=True):
    if label in self.d:
      return self.d[label]
    if not create_new:
      return None
    num = len(self.labels)
    self.d[label] = num
    self.labels.append(label)
    return num

  def NumToStr(self, num):
    return self.labels[num]

class Classifier(object):
  def __init__(self):
    self.classifier = self._NewClassifier()
    self.labels_enum = StrEnumerator()
    self.features_enum = StrEnumerator()

  def _NewClassifier(self):
    if args.classifier == "RandomForest":
      return ensemble.RandomForestClassifier(n_estimators=300, random_state=0)
    elif args.classifier == "SVM":
      return svm.SVC(kernel='rbf', gamma=0.0001, C=1000000.0)
    elif args.classifier == "GBRT":
      return ensemble.GradientBoostingClassifier(
          n_estimators=100, learning_rate=0.2, max_depth=2, random_state=0)
    else: 
      assert False, ("Unknown classifier:", args.classifier)

  def FromSparse(self, Xsparse):
    X = []
    for sparse in Xsparse:
      full = [sparse.get(i, 0.0) for i in xrange(len(self.features_enum))]
      X.append(full)
    return X

  def Train(self, Xsparse, y, priors):
    X = self.FromSparse(Xsparse)
    label_weights = np.array([priors.get(self.labels_enum.NumToStr(l), 1.0) for l in y])
    self.classifier.fit(X, y, label_weights)

  def Predict(self, Xsparse):
    X = self.FromSparse(Xsparse)
    return self.classifier.predict(X), self.classifier.predict_proba(X)

  def LoadCregFeatFile(self, feat_filename, create_new_features=True):
    Xsparse = []
    instances = []
    for features_line in codecs.open(feat_filename, "r", "utf-8"):
      instance, feat_str = features_line.strip().split("\t")
      instances.append(instance)
      features = json.loads(feat_str)
      feat_dict = dict({(self.features_enum.StrToNum(feat, create_new_features), val) for feat, val in features.iteritems()})
      if None in feat_dict:
        del feat_dict[None]
      Xsparse.append(feat_dict)
    return Xsparse, instances

  def LoadCregLabelsFile(self, labels_filename):
    y = []
    instances = []
    for labels_line in codecs.open(labels_filename, "r", "utf-8"):
      instance, label = labels_line.strip().split("\t")
      instances.append(instance)
      y.append(self.labels_enum.StrToNum(label))
    return y, instances

  def SaveCregFeat(self, instances, x_list, feat_filename):
    feat_file = codecs.open(feat_filename, "w", "utf-8")
    for instance, x in izip_longest(instances, x_list):
      features = {}
      for i, val in enumerate(x):
        features[self.features_enum.NumToStr(i)] = val
      features_str = json.dumps(features, sort_keys=True)
      feat_file.write(u"{}\t{}\n".format(instance, features_str))

  def SaveCregLabels(self, instances, y_list, y_probabilities, write_class_confidence, labels_filename):
    labels_file = codecs.open(labels_filename, "w", "utf-8")
    y_prob_iter = [] if y_probabilities is None else y_probabilities
    for instance, y, y_prob in izip_longest(instances, y_list, y_prob_iter):
      label = self.labels_enum.NumToStr(y)
      if y_probabilities is None:
        labels_file.write(u"{}\t{}\n".format(instance, label))
      else:
        prob_dict = {}
        for i, prob in enumerate(y_prob):
          prob_dict[self.labels_enum.NumToStr(i)] = prob
        prob_str = json.dumps(prob_dict, sort_keys=True)
        if not write_class_confidence:
          labels_file.write(u"{}\t{}\t{}\n".format(instance, label, prob_str))
        else:
          first, second = sorted(prob_dict.itervalues(), reverse=True)[:2]
          confidence = first - second
          labels_file.write(u"{}\t{}\t{}\t{}\n".format(instance, label, confidence, prob_str))

  def CalcAccuracy(self, predicted_labels, golden_labels):
    correct = 0
    miss = 0
    for p, g in izip_longest(predicted_labels, golden_labels):
      if p == g:
        correct += 1
      else:
        miss += 1
    return correct / (correct + miss)

  def WriteConfusionMatrix(self, predicted_labels, golden_labels, out_file):
    confusion_matrix = Counter()
    for predicted, golden in izip_longest(predicted_labels, golden_labels):
      confusion_matrix[(self.labels_enum.NumToStr(predicted), self.labels_enum.NumToStr(golden))] += 1

    out_file.write("Confusion Matrix:\nCorrect\\Predicted\n")
    all_labels = sorted(self.labels_enum.labels)
    out_file.write(u"\t{}".format("\t".join(all_labels)))
    for label in all_labels:
      out_file.write(u"\n{}".format(label))
      for predicted_label in all_labels:
        out_file.write(u"\t{:3}".format(confusion_matrix[(predicted_label, label)]))
    out_file.write(u"\n")

  def CrossValidate(self, Xsparse, y, num_folds, priors):
    def GetAccuracy(test_posteriors, test_y):
      def NormalizedHistogram(hist):
        normalized = []
        total = 0
        for index in xrange(len(self.labels_enum.labels)):
          total += hist[index]
          normalized.append(total / len(test_y))
        return normalized

      hist = Counter()
      for posteriors, expected in izip_longest(test_posteriors, test_y):
        sorted_posteriors = sorted(enumerate(posteriors), key=lambda x: x[1], reverse=True)
        sorted_labels = [k for k,v in sorted_posteriors]
        try:
          hist[sorted_labels.index(expected)] += 1
        except ValueError:
          pass  # Did not see this label in training.
      normalized_hist = NormalizedHistogram(hist)
      print normalized_hist
      accuracy = normalized_hist[0]
      return accuracy

    accuracy = []
    X = np.array(self.FromSparse(Xsparse))
    for train, test in cross_validation.StratifiedKFold(y, num_folds):
      X_train, X_test, y_train, y_test = X[train], X[test], y[train], y[test]
      label_weights = np.array([priors.get(self.labels_enum.NumToStr(l), 1.0) for l in y_train])
      classifier = self._NewClassifier()
      classifier.fit(X_train, y_train, label_weights)
      posteriors = classifier.predict_proba(X_test)
      accuracy.append(GetAccuracy(posteriors, y_test))
    return np.array(accuracy)

  def LibraryCrossValidate(self, Xsparse, y, num_folds, priors):
    # TODO: Support priors.
    X = self.FromSparse(Xsparse)
    return cross_validation.cross_val_score(self.classifier, X, y, cv=num_folds)

  def CalculateBalancedPriors(self, y):
    label_counts = Counter()
    for label in y:
      label_counts[label] += 1
    total_count = 0
    priors = {}
    for label, count in label_counts.iteritems():
      weight = len(y) - count
      priors[self.labels_enum.NumToStr(label)] = weight
      total_count += weight
    for label in priors:
      priors[label] /= total_count
    return priors


def main():
  if args.load_classifier_filename:
    with gzip.open(args.load_classifier_filename, "rb") as f:
      classifier = cPickle.load(f)
  else:
    classifier = Classifier()

    # Training
    X, x_instances = classifier.LoadCregFeatFile(args.train_features)
    y, y_instances = classifier.LoadCregLabelsFile(args.train_labels)
    if x_instances != y_instances:
      for i, (x, y) in enumerate(izip_longest(x_instances, y_instances)):
        assert (x==y), (i+1, x, y)

    print "Num of labels:", len(classifier.labels_enum.labels)
    print "Num training samples:", len(y)
    print "Num of features:", len(classifier.features_enum.labels)

    if args.priors == "balanced":
      priors = classifier.CalculateBalancedPriors(y)
      print "Using balanced priors:", priors
    else:
      priors = json.loads(args.priors)

    print("Training")
    if args.num_cross_validation_folds > 0:
      scores = classifier.CrossValidate(X, np.array(y), args.num_cross_validation_folds, priors)
      print("CV Accuracy: {:0.2} (+/- {:0.2}) [{}..{}]".format(
          scores.mean(), scores.std() * 2, scores.min(), scores.max()))

    classifier.Train(X, y, priors)
  if args.dump_classifier_filename:
    with gzip.open(args.dump_classifier_filename, "wb") as f:
      cPickle.dump(classifier, f)

  # Testing
  if args.test_features is None:
    return

  print("Testing")
  X_test, test_instances = classifier.LoadCregFeatFile(args.test_features, create_new_features=False)

  test_predicted_labels, test_predicted_probabilities = classifier.Predict(X_test)
  if args.test_predicted_labels_out:
    out_probabilities = test_predicted_probabilities
    if not args.write_posterior_probabilities:
      out_probabilities = None
    classifier.SaveCregLabels(test_instances, test_predicted_labels,
        out_probabilities, args.write_class_confidence, args.test_predicted_labels_out)
  if args.golden_labels:
    golden_labels, golden_instances = classifier.LoadCregLabelsFile(args.golden_labels)
    assert (golden_instances == test_instances)
    classifier.WriteConfusionMatrix(test_predicted_labels, golden_labels, sys.stdout)
    accuracy = classifier.CalcAccuracy(test_predicted_labels, golden_labels)
    print "Held-out accuracy:", accuracy

if __name__ == '__main__':
  main()

