metaphor
========

Cross-lingual metaphor detection.


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
  </ul>
  </blockquote>
  The following script demonstrates commands needed for installing the dependencies: ```install_dependencies.sh```


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

##### Prediction: 


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

