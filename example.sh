#!/bin/bash

echo "Training subject-verb-object (SVO) metaphor classifier using Random Forest"
echo "./train.sh svo input-text resources/TroFi/metaphorical.txt resources/TroFi/literal.txt"
./train.sh svo input-text resources/TroFi/metaphorical.txt resources/TroFi/literal.txt


echo "Training adjective-noun (AN) metaphor classifier using Random Forest"
echo "./train.sh an input-rel resources/AdjN/training_adj_noun_met_en.txt resources/AdjN/training_adj_noun_nonmet_en.txt"

./train.sh \
    an \
    input-rel \
    resources/AdjN/training_adj_noun_met_en.txt \
    resources/AdjN/training_adj_noun_nonmet_en.txt



echo "Testing SVO metaphor classifier"
echo "./find_metaphors_rel.sh svo input/svo_mets.txt"
./find_metaphors_rel.sh svo input/svo_mets.txt

echo "Testing AN metaphor classifier"
./find_metaphors_rel.sh an input/an_mets.txt


echo "Done. Have a nice day :)"
