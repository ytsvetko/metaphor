metaphor
========

Cross-lingual metaphor detection.



src/parse_turbo_output.py --turbo_filename resources/en/TroFi/literal.txt_turbo_parsed --out_file /tmp/parsed_instances --filter_verbs_filename resources/en/TroFi/trofi_verbs.txt --rel_type svo

src/extract_instances.py --input_file /tmp/parsed_instances --features_filename /tmp/feat --labels_filename /tmp/label --blacklisted_instances resources/en/TroFi/to_filter --append_wn_supersenses --append_VSM_features --VSM_filename ../clab_metaphor/system/resources/manaal/en-svd-de-64.txt --append_abstractness_features --abstractness_predictions_filename ../clab_metaphor/system/resources/abstract/to_predict.predictions --append_imageability_features --imageability_predictions_filename ../clab_metaphor/system/resources/imageable/to_predict.predictions
