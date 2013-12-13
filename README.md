metaphor
========

Cross-lingual metaphor detection.


Installation
-------
  
  This tool requires:
  <blockquote>
  <ul>
  <li>
    Python 2.7  <a href="http://www.python.org/download/releases/2.7.3/">www.python.org/download/releases/2.7.3/</a>
  </li> 
  <li>
    Natural Language Toolkit nltk <a href="nltk.org">nltk.org</a>
  </li> 
  <li>
    A Python module for machine learning scikit-learn <a href="scikit-learn.org">scikit-learn.org</a>
  </li> 
  <li>
    English dependency parser TurboParser <a href="https://www.ark.cs.cmu.edu/TurboParser">www.ark.cs.cmu.edu/TurboParser</a>
  </li> 
    <li>
    Optionally: Russian dependency parser seman <a href="http://seman.sourceforge.net/">seman.sourceforge.net</a>
  </li> 
  </ul>
  </blockquote>
  See installing the dependencies example in <p><code>install_dependencies.sh</code></p>


Usage
-------

##### Training: 
   *Parameters:*

      1. relation type (*svo* or *an*)
      2. format of the training files (*input-text* or *input-rel*)
      3. path to metaphoric training file
      4. path to literal training file


   *Examples:*

   <p><code>
   ./train.sh svo input-text \

       resources/TroFi/metaphorical.txt \

       resources/TroFi/literal.txt
   </code>

   <p><code>
   ./train.sh an input-rel \

       resources/AdjN/training_adj_noun_met_en.txt \

       resources/AdjN/training_adj_noun_nonmet_en.txt
  </code>

##### Prediction: 
   *Parameters:*

      1. path to input file split to sentences

   *Examples:*

   <p><code>
   ./find_metaphors.sh path_to_file                       
   </code>

