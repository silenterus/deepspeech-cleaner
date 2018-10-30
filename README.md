# deepspeech-cleaner

### Multi-Language Dataset Cleaner/Creator for [Mozilla's DeepSpeech Framework ](https://github.com/mozilla/DeepSpeech/) 
alpha-version
only supports german right now

#### 

## Installation :
```
sudo apt-get update 
sudo apt-get upgrade
sudo apt-get install make cmake sqlite3 git python3 python3-pip 
```

#### install Tensorflow using Mozilla's fork 
follow the instruction https://github.com/mozilla/tensorflow/tree/r1.11


#### install DeepSpeech 
follow the instruction https://github.com/mozilla/DeepSpeech


 
#### if you want to build tri and binary (you need to install them otherwise the script wont find them)
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


#### possible parameters
```
python3 deepspeech-cleaner.py --help

```
#### default text querys
> deepspeech-cleaner/de/sql_query 

###### strings for query 
>> *.txt

###### strings for NOT query 
>> *_not.txt



### Downloader

#### work in progress




### Inserter

##### analyze and insert Common Voice Corpus 

```
python3 deepspeech-cleaner.py insert_cs --path /path/to/common_voice_corpus/

```




### Creator



##### creating training files in "training/standard" with default values 
```
python3 deepspeech-cleaner.py create_files

```
##### creating training files in "training/german300k" with default values 
```
python3 deepspeech-cleaner.py create_files --training german300k
```

##### creating training files in "training/german200k" with default values and create lm.binary + trie + words.arpa
###### put [all_corpora_filtered_maryfied.txt](http://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/German_sentences_8mil_filtered_maryfied.txt.gz) in 
> deepspeech-cleaner/cleaner 
###### i used Version 0.3.0 to generate the trie
```
python3 deepspeech-cleaner.py create_files --training german200k --trie True
```

### Trainer


##### start training for standard
```
bash start_train.sh standard
```

##### start training for german300k
```
bash start_train.sh german300k
```




## Worth checking out


  * [Mozilla's DeepSpeech](https://github.com/mozilla/DeepSpeech/)
    incredibly work - the potential to gain some autonomy back.


  * [TU-Darmstadt Kaldi](https://github.com/uhh-lt/kaldi-tuda-de)
    great dataset for trainingsets with lower qualitys 


  * [deepspeech-ger](https://github.com/ynop/deepspeech-german)
    i got many ideas from this git


  * [Audiomate](https://github.com/ynop/audiomate)
    also worth checking out



