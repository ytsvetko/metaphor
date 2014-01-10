metaphor
========

Cross-lingual metaphor detection.


This tool is a partial implementation of the ACL'14 submission:

Metaphor Detection with Cross-Lingual Model Transfer


Installation
-------
  
  This tool requires the following dependencies:
  <blockquote>
  <ul>
  <li>
    Python 2.7  <a href="http://www.python.org/download/releases/2.7.3/">www.python.org/download/releases/2.7.3/</a>
  </li> 
  <li>
    Natural Language Toolkit nltk <a href="http://nltk.org">nltk.org</a>
  </li> 
  <li>
    A Python module for machine learning scikit-learn <a href="http://scikit-learn.org">scikit-learn.org</a>
  </li> 
  <li>
    English dependency parser TurboParser <a href="https://www.ark.cs.cmu.edu/TurboParser">www.ark.cs.cmu.edu/TurboParser</a>
  </li> 
    <li>
    Optionally: Russian dependency parser seman <a href="http://seman.sourceforge.net/">seman.sourceforge.net</a>
  </li> 
  <li>
    Important: Uncompress resources/VSM.en-svd-de-64.txt.tar.gz file before running the tool
    
    tar -zxvf en-svd-de-64.txt.tar.gz
  </li> 
  </ul>
  </blockquote>
  The following script demonstrates commands needed for installing the dependencies: ```install_dependencies.sh```


Example
-------
For usage example run the script 
```example.sh```


Usage
-------

##### Training: 


   *Parameters:*

    1. relation type (*svo* or *an*)
    2. format of the training files (*input-text* or *input-rel*)
    3. path to metaphoric training file
    4. path to literal training file

   *Examples:*

```sh
./train.sh \
    svo \
    input-text \
    resources/TroFi/metaphorical.txt \
    resources/TroFi/literal.txt
```

```sh
./train.sh \
    an \
    input-rel \
    resources/AdjN/training_adj_noun_met_en.txt \
    resources/AdjN/training_adj_noun_nonmet_en.txt
```

##### Prediction for subject-verb-object (SVO) or adjective-noun (AN) syntactic relations: 

   *Parameters:*

    1. relation type (*svo* or *an*)
    1. path to relations input file (see examples in ./input/*) 

   *Examples:*

```
./find_metaphors_rel.sh svo input/svo_mets.txt                 
```

   *Output format:*

   Tab-separated text file sentence-aligned to the input file with the following fields:

    1. the original relation
    2. predicted sentence label "M" or "L"
    3. json-formatted metaphor candidates with labels

##### Prediction for raw text files split to sentences: 

   *Parameters:*

    1. path to input file split to sentences

   *Examples:*

```
./find_metaphors.sh path_to_file                       
```

   *Output format:*

   Tab-separated text file sentence-aligned to the input file with the following fields:

    1. the original sentence
    2. predicted sentence label "M" or "L"
    3. json-formatted metaphor candidates with labels

   *Example:*

```
Care to offer some evidence that this bald assertion is true? <tab> M <tab> {"bald assertion": "M", "offer evidence": "M"}
```
##### Released resources:

  <blockquote>
  <ul>
  <li>
    Adjective-Noun and Subject-Verb-Object 
    English and Russian metaphorical and literal test sets along with annotator judgments:

    ./input/Datasets_ACL2014.xlsx
  </li> 
  <li>
    Adjective-Noun 884 metaphorical and 884 literal pairs used for model training:
    
    ./resouces/AdjN/*
  </li> 
  </ul>
  </blockquote>

