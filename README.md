# deepspeech-cleaner

### Multi-Language Dataset Cleaner/Creator for [Mozilla's DeepSpeech Framework ](https://github.com/mozilla/DeepSpeech/) 

#### 

## Installation :
```
sudo apt-get update 
sudo apt-get upgrade
sudo apt-get install make cmake sqlite3 git python3 python3-pip 
```



 
#### if you want to buld tri and binary (you need to install them otherwise the script wont find them)
```
git clone https://github.com/kpu/kenlm
cd kenlm
mkdir -p build
cd build
cmake ..
make -j 4
make install      # important !!!
cd ..
cd ..

```

#### then
```
git clone https://github.com/silenterus/deepspeech-cleaner
cd deepspeech-cleaner
pip3 install -r requirements.txt
```


## Quick Start


### --help for all possible parameters
```
python3 deepspeech-cleaner.py --help

```


### Downloader

#### work in progress



### Creator



#### creating training files in "training/defaulter" with default values without lm.binary + trie
```
python3 deepspeech-cleaner.py create_files

```
#### creating training files in "training/german300k" with default values without lm.binary + trie
```
python3 deepspeech-cleaner.py create_files --training german300k
```


#### creating training files in "training/german200k" with default values and lm.binary + trie
#### put all_corpora_filtered_maryfied.txt in 
>>> deepspeech-cleaner/cleaner 

#### the paramater doesnt work yet

#### i used DeepSpeech Version 0.2.1-alpha.2 to generate the trie. I hope they didnt change the language model since then
```
python3 deepspeech-cleaner.py create_files --training german200k --trie True

```

### Trainer


#### start training in defaulter
```
bash start_train.sh defaulter
```

#### start training in german300k
```
bash start_train.sh german300k
```




## Notes and Common Issues


  * [Mozilla's DeepSpeech](https://github.com/mozilla/DeepSpeech/)
    incredibly work - the potential to gain some autonomy back.


  * [TU-Darmstadt Kaldi](https://github.com/uhh-lt/kaldi-tuda-de)
    great dataset for trainingsets with lower qualitys 


  * [deepspeech-ger](https://github.com/ynop/deepspeech-german)
    i got many ideas from this git


  * [Audiomate](https://github.com/ynop/audiomate)
    also worth checking out



## Background
