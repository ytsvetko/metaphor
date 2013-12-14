#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import codecs
import collections
import copy
import json
import argparse
import os

parser = argparse.ArgumentParser()

parser.add_argument("--input_file", help="Input file")
parser.add_argument("--predicted_an_label", 
    help="Classify.py output for AdjN relations")
parser.add_argument("--predicted_svo_label", 
    help="Classify.py output for SVO relations")
parser.add_argument("--filter_files_dir", help="Files for filtering words")
parser.add_argument("--default_label", default="L", 
    help="Label if no instances [L|M|?]")
parser.add_argument("--out_file", help="Output file.")

args = parser.parse_args()

def GetPredictions(line_num, line, an_predictions, svo_predictions):
  predictions = copy.deepcopy(an_predictions[line_num])
  predictions.update(svo_predictions[line_num])
  all_labels = set(predictions.values())
  if len(all_labels) == 0:
    label = args.default_label
  else:
    label = "M" if "M" in all_labels else "L"
  return label, predictions

def LoadPredictions(predicted_labels, filter_dict):
  # key - sentence number, value - a dictionary of instance:lavel
  predictions = collections.defaultdict(dict) 
  for line in codecs.open(predicted_labels, "r", "utf-8"):
    # 1_an_-1_0_bald_bald_999_none_none_1_eagle_eagles_U L
    instance, label, posteriors = line.strip().split("\t")
    sentence_num, rel_type, _, _, lemma1, w1, _, lemma2, w2, _, lemma3, w3, _ = instance.split("_")
    out_str = " ".join([ w for w in [w1, w2, w3] if w != "none"])
    if rel_type == "svo":
      if (lemma1 in filter_dict["entity"] or
          lemma2 in filter_dict["action"] or
          lemma3 in filter_dict["entity"]):
        label = "L"
    predictions[int(sentence_num)][out_str] = label
  return predictions

def LoadFilterFile(filter_filename):
  result = set()
  for word in codecs.open(filter_filename, "r", "utf-8"):
    result.add(word.strip().lower())
  return result

def LoadFilters(filter_files_dir):
  if filter_files_dir is None:
    return {"entity":[], "action":[]}
  return {
      "entity":LoadFilterFile(os.path.join(filter_files_dir, "entities")),
      "action":LoadFilterFile(os.path.join(filter_files_dir, "actions")),
      }

def main():
  filter_dict = LoadFilters(args.filter_files_dir)
  an_predictions = LoadPredictions(args.predicted_an_label, filter_dict)
  svo_predictions = LoadPredictions(args.predicted_svo_label, filter_dict)
  out_file = codecs.open(args.out_file, "w", "utf-8")
  for line_num, line in enumerate(codecs.open(args.input_file, "r", "utf-8")):
    label, sentence_predictions = GetPredictions(line_num, 
          line, an_predictions, svo_predictions)
    out_file.write("{}\t{}\t{}\n".format(line.strip(), label, json.dumps(sentence_predictions)))

if __name__ == '__main__':
  main()
