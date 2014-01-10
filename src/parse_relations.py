#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

import sys
import collections
import codecs
import glob
import os
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--input_dir", help="Directory with relation files")
parser.add_argument("--out_dir", help="Directory with results.")

parser.add_argument("--input_file", help="A file with relations")
parser.add_argument("--out_file", help="Output file.")

parser.add_argument("--rel_type", help="Relation types (SVO or NN).")

args = parser.parse_args()

def FormatWord(word, pos, index):
  return u"{} {} {} {}".format(word, word, pos, index)

def FormatAN(line, index):
  tokens = line.split()
  w1 = FormatWord(tokens[0], 'JJ', 1)
  w2 = FormatWord(tokens[1], 'NN', 2)
  return u"{}\tan\t-1\t{}\tNone\t{}\n".format(index, w1, w2)

def FormatSVO(line, index):
  tokens = line.split()
  w1 = FormatWord(tokens[0], 'NN', 1)
  w2 = FormatWord(tokens[1], 'VB', 2)
  if len(tokens) == 3:
    w3 = FormatWord(tokens[2], 'NN', 3)
  else: 
    w3 = None
  return u"{}\tsvo\t-1\t{}\t{}\t{}\n".format(index, w1, w2, w3)

def ProcessFile(in_filename, out_filename, rel_type):
  out_file = codecs.open(out_filename, "w", "utf-8")
  for index, line in enumerate(codecs.open(in_filename, "r", "utf-8")):
    if rel_type == "an": 
      out_file.write(FormatAN(line, index))
    else:
      assert rel_type == 'svo', args.rel_type
      out_file.write(FormatSVO(line, index))

def main():
  assert args.rel_type.lower() in ['svo', 'an']
  if args.input_dir:
    for filename in glob.iglob(os.path.join(args.input_dir, "*")):
      basename = os.path.basename(filename)
      out_filename = os.path.join(args.out_dir, basename)
      ProcessFile(basename, out_filename, args.rel_type.lower())
  elif args.input_file:
    ProcessFile(args.input_file, args.out_file, args.rel_type.lower())

if __name__ == '__main__':
  main()

