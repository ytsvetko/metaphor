metaphor
========

Cross-lingual metaphor detection.


Installation
-------

  <p><code>./install_dependencies.sh</code>


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
   ./train.sh svo input-text  resources/TroFi/metaphorical.txt resources/TroFi/literal.txt
   </code>

   <p><code>
   ./train.sh an input-rel resources/AdjN/training_adj_noun_met_en.txt resources/AdjN/training_adj_noun_nonmet_en.txt
  </code>

##### Prediction: 
   *Parameters:*

      1. path to input file split to sentences

   *Examples:*

   <p><code>
   ./find_metaphors.sh path_to_file                       
   </code>

 

0. Split the text to sentences. This is important for aligning lines in the final output.

--- Internal process ---

1. Run Turbo Parser on a text file split to sentences.

~/tools/TurboParser-2.1.0/scripts/parse.sh tmp

2. Convert Turbo Parser output into internal format of instances.
   Separate files for SVO and AN.

src/parse_turbo_output.py --turbo_filename resources/TroFi/literal.txt_turbo_parsed --out_file /tmp/parsed_instances --filter_verbs_filename resources/TroFi/trofi_verbs.txt --rel_type svo

./parse_turbo_output.py --turbo_filename tmp.parsed --out_file parsed_instances --rel_type an


3. Run each through feature extraction:
   Different parameters for each mode (SVO or AN).

src/extract_instances.py --input_file /tmp/parsed_instances --features_filename /tmp/feat --labels_filename /dev/null --blacklisted_instances resources/en/TroFi/to_filter --append_wn_supersenses --append_VSM_features --VSM_filename ../clab_metaphor/system/resources/manaal/en-svd-de-64.txt --append_abstractness_features --abstractness_predictions_filename ../clab_metaphor/system/resources/abstract/to_predict.predictions --append_imageability_features --imageability_predictions_filename ../clab_metaphor/system/resources/imageable/to_predict.predictions

4. Run classifier trained for each mode separately.

src/classify.py

5. Merge classification results of both modes with the original file and produce output in desired format (?).

Step 1:
* Prepare the resources for the release:  ***DONE
   - VSM files.
   - Abstracteness/Imageability outputs.
   - Adj/Noun/Verb supersenses.
* Fix the TODOs in the code for Adj extraction.  ***DONE
* Implement the testing script for users to use. (up until output parser)  ***DONE
* Implement the training script and ability to save/load trained model to disk.  ***DONE

TODOs:
===========
* Implement the script for merging results from SVO and AN and creating output in the right format (?)
  (after classify.py) - based on check_accuracy.py
* Implement the evaluation scripts (accuracy, etc.).
* Change the header of each python script to use python2.7
* Push changes to github.

Step 2:
* Implement installation script that automatically installs and configures all dependencies.


===========

For multi-lingual:
* Add the dictionary.
* Instance extractor from the TurboParser alternative in that language.
* Change the abstractness/imageability to use dictionary instead of translating outside.  ***DONE

Nice to haves:
* Change the format of the "to_filter" file.
* Combine the two modes into a single file.
* Merge the feat and labels file in the classifier format.
