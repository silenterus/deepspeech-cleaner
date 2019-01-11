# deepspeech-cleaner

## Multi-Language Dataset Cleaner/Combiner for [Mozilla's DeepSpeech Framework ](https://github.com/mozilla/DeepSpeech/) 

#### makes the whole process of collecting,cleaning and sorting datasets alot easier


### Supported Languages 
  *  [pl - Polish = 13.7%](https://drive.google.com/open?id=14oDu1Kes2I16ReBhCJpAFETHVRETlT0N)
  *  [es - Spanish = 13.9%](https://drive.google.com/open?id=1Yw5SUbIzKUqsEQCwP-eoaTW492QYc1Ol)
  *  [it - Italian = 18.4%](https://drive.google.com/open?id=14l-jx56zM84EWpfhkYT0gHc9cZZ-Ti9D)
  *  [de - German = 18.9%](https://drive.google.com/open?id=19eV4yvXrM89YayfF6OAGNnWo0a6vXmoH)
  *  [fr - French = 22.7%](https://drive.google.com/open?id=1tHNM-7HnPQBdooVgTxNl6F-pgVbRMk3h)
  *  [uk - Ukrainian = 29.9%](https://drive.google.com/open?id=1dQ5MzlkhjdiQpLCJDNqV1-Z2GsquXIx1)
  *  [ru - Russian = 36.9%](https://drive.google.com/open?id=1eBm2aD0QGh8y5LgZP0MYqZresdcVIvgz)
  *  [nl - Dutch = 39.6%](https://drive.google.com/open?id=1eP8ug3qTUwodI3uEaofJ5xqjhMfjWUs6)
  *  [pt - Portuguese = 50.7%](https://drive.google.com/open?id=1QE7PIUnQXS6X_t90O8bTiupJu5a0kPf-)
  *  en - English 



### Supported but not enough Datasets 
###### hu - Hungarian
###### nn - Norwegian
###### ro - Romanian
###### sv - Swedish
###### tr - Turkish
###### cs - Czech
###### da - Danish
###### fi - Finnish
###### et - Estonian
###### el - Greek
###### is - Icelandic
###### lv - Latvian 
###### lt - Lithuanian
###### sr - Serbian
###### sk - Slovak 
###### sl - Slovenian 
###### sq - Albanian 
###### bs - Bosnian
###### bg - Bulgarian 
###### hr - Croatian 


 

## Installation :

##### install [kenlm](https://github.com/kpu/kenlm)
##### install [DeepSpeech](https://github.com/mozilla/DeepSpeech)

```
git clone https://github.com/silenterus/deepspeech-cleaner
cd deepspeech-cleaner
pip install -r requirements.txt
```





## Quick Start


### Downloader
##### download/analyze/insert all available corpora for french
```
python3 deepspeech-cleaner.py download --lang fr

```


### Inserter
##### insert corpora - in case you download the files by yourself
```
python3 deepspeech-cleaner.py insert /path/to/corpora/ 

```


### Creator
##### clean/sort/create all necessary files for training - includes lm.binary/trie if kenlm is installed
```
python3 deepspeech-cleaner.py create 

```
##### clean/sort/create all necessary files for training - no cleaning and no lm.binary/trie creation
```
python3 deepspeech-cleaner.py create --noclean --notrie

```


##### start deepspeech training 
```
bash languages/fr/training/standard/start_train.sh
```


## Other Options


### Wiki Crawler
##### download/extract/clean articles from [Wiki Dumps](https://dumps.wikimedia.org/) 

```
python3 deepspeech-cleaner.py crawl 

```


### Replacement Tester
##### Test num2words and your replacement rules 

```
python3 deepspeech-cleaner.py test 1 2 3 is not for me 
python3 deepspeech-cleaner.py test /path/to/textfile.txt

```

### Audio Transformer
##### convert/trimm/trimmsilence all audio files in your Database
```
python3 deepspeech-cleaner.py convert 

```


### Autosave
##### all arguments are saved for each language seperately 
##### autosave off/on
```
python3 deepspeech-cleaner.py autosave

```



### Hints
#### change replacer rules in

```
languages/fr/replacer/..
```

##### files contain rules like 
```
'@> '
' Sat > Saturday '
```
  *  only files with a number attached will be used 
  *  <0 used before number translation 
  *  =>0 used after number translation 
  *  replace a word/symbol with '�' and the whole sentence get rejected
  *  spaces at the start/end are important for whole words


#### change the string based sql querys in
```
languages/fr/sql_query/..
```
  *  files are named like the tables in your "audio.db"
  *  '!' at the end of a line functions as NOT



### Help
```
python3 deepspeech-cleaner.py help
```



#### Datasets  
  * [CommonVoice](https://voice.mozilla.org/en/datasets)

  * [Voxforge](http://www.repository.voxforge1.org/downloads/)

  * [Librivox](http://www.caito.de/2019/01/the-m-ailabs-speech-dataset/)

  * [SpokenWiki](https://www2.informatik.uni-hamburg.de/nats/pub/SWC/)

  * [Vystadial](https://ufal.mff.cuni.cz/grants/vystadial)

  * [TuDa](https://www.inf.uni-hamburg.de/en/inst/ab/lt/resources/data/acoustic-models.html)

  * [Zamia](https://github.com/gooofy/zamia-speech)

  * [Tatoeba](https://tatoeba.org/)

  * [African Accent French](http://www.openslr.org/57/)

  * [Nicolas French Trainings Data](https://gitlab.com/nicolaspanel/TrainingSpeech)


##### coming soon
 
  * [TED](https://voice.mozilla.org/en/datasets)



 




## Worth checking out


  * [Mozilla's DeepSpeech](https://github.com/mozilla/DeepSpeech/)
    incredibly work - the potential to gain some autonomy back.

  * [Mozilla's Common Voice](https://github.com/mozilla/DeepSpeech/)
    help with your voice

  * [TU-Darmstadt Kaldi](https://github.com/uhh-lt/kaldi-tuda-de)
    great dataset for trainingsets with lower qualitys 

  * [deepspeech-ger](https://github.com/ynop/deepspeech-german)
    i got many ideas from this git

  * [WikiExtractor](https://github.com/attardi/wikiextractor)
    used part of it to extract the wiki articles

  * [M-AILABS](http://www.caito.de/2019/01/the-m-ailabs-speech-dataset/)

  * [Open Speech and Language Resources](http://www.openslr.org/)
    all sorts of datasets



## Results  





###   Polnish Results:                    [pl]

   

####   ----- options:                      
#####    <---> size                          [5-10000]
#####    <---> duration                      [0.5-15]
#####    <---> bitrate                       [0]
#####    <---> samplerate                    [16000-48000]
#####    <---> channels                      [0]
#####    <---> wordcount                     [2-1500]
#####    <---> wordsec                       [0.2-1.8]
#####    <---> lettercount                   [0]
#####    <---> lettersec                     [0]
#####    <---> upvotes                       [0]
#####    <---> downvotes                     [0]
#####    <---> sectors                       [0]
####   ----- info:                         
#####    <---> corpora                       [librivox-tatoeba]
#####    <---> gb                            [5.97]
#####    <---> hours                         [51.8]
#####    <---> words                         [420039]
#####    <---> letters                       [2708869]
#####    <---> words per sec                 [2.25]
#####    <---> letters per sec               [14.53]
#####    <---> all files                     [25903]
#####    <---> train files                   [18134]
#####    <---> test files                    [3886]
#####    <---> dev files                     [3886]


######   I Test of Epoch 12 - WER: 0.137465, loss: 29.99004187996005, mean edit distance: 0.058884            
######   I WER: 0.142857, loss: 4.163468, mean edit distance: 0.065217
######   I  - src: "jak w ogóle we wszystkich naszych obliczeniach"
######   I  - res: "a w ogóle we wszystkich naszych obliczeniach "
######   I WER: 0.142857, loss: 4.163468, mean edit distance: 0.065217
######   I  - src: "jak w ogóle we wszystkich naszych obliczeniach"
######   I  - res: "a w ogóle we wszystkich naszych obliczeniach "
######   I WER: 0.181818, loss: 6.447145, mean edit distance: 0.025641
######   I  - src: "pomimoto w stosunku wokulskiego do panny izabeli pierwsze lody były przełamane"
######   I  - res: "pomimo to w stosunku wokulskiego do panny izabeli pierwsze lody były przełamane "
######   I WER: 0.400000, loss: 6.677766, mean edit distance: 0.107143
######   I  - src: "otarła oczy i ciągnęła dalej"
######   I  - res: "otarołaoczy i ciągnęła dalej "
######   I WER: 0.400000, loss: 6.677766, mean edit distance: 0.107143
######   I  - src: "otarła oczy i ciągnęła dalej"
######   I  - res: "otarołaoczy i ciągnęła dalej "
######   I WER: 0.500000, loss: 1.875308, mean edit distance: 0.105263
######   I  - src: "niedziela sprowadzą"
######   I  - res: "niedziela prowadzą "
######   I WER: 0.500000, loss: 1.875308, mean edit distance: 0.105263
######   I  - src: "niedziela sprowadzą"
######   I  - res: "niedziela prowadzą "
######   I WER: 1.000000, loss: 3.942765, mean edit distance: 0.105263
######   I  - src: "tu będzie licytacya"
######   I  - res: "tubędzielicytacya"
######   I WER: 1.000000, loss: 3.942765, mean edit distance: 0.105263
######   I  - src: "tu będzie licytacya"
######   I  - res: "tubędzielicytacya"
######   I WER: 1.000000, loss: 6.762781, mean edit distance: 0.176471
######   I  - src: "jakto z kucharzem"
######   I  - res: "jak to skucharzem"




   -------------------------------------------------

###    Spanish Results:                    [es]

   

####     ----- options:
#####    <---> corpora                       [librivox-vox-tatoeba]
#####    <---> size                          [5-10000]
#####    <---> duration                      [0.5-15]
#####    <---> bitrate                       [0]
#####    <---> samplerate                    [16000-48000]
#####    <---> channels                      [0]
#####    <---> wordcount                     [2-1500]
#####    <---> wordsec                       [0.25-1.9]
#####    <---> lettercount                   [0]
#####    <---> lettersec                     [0]
#####    <---> upvotes                       [0]
#####    <---> downvotes                     [0]
#####    <---> sectors                       [0]

####     ----- info:                       
#####    <---> gb                            [20.02]
#####    <---> hours                         [190.1]
#####    <---> words                         [1545009]
#####    <---> letters                       [8793419]
#####    <---> words per sec                 [2.26]
#####    <---> letters per sec               [12.85]
#####    <---> all files                     [139265]
#####    <---> train files                   [97486]
#####    <---> test files                    [20891]
#####    <---> dev files                     [20891]


######   I Test of Epoch 12 - WER: 0.139222, loss: 16.857607432188242, mean edit distance: 0.060826
######   I WER: 0.250000, loss: 0.047055, mean edit distance: 0.047619
######   I  - src: "tengo que comprar uno"
######   I  - res: "tengo que comprar un "
######   I WER: 0.500000, loss: 0.039710, mean edit distance: 0.083333
######   I  - src: "sé cuidadoso"
######   I  - res: "se cuidadoso"
######   I WER: 0.500000, loss: 0.072996, mean edit distance: 0.111111
######   I  - src: "me amabas"
######   I  - res: "me amaba "
######   I WER: 0.500000, loss: 0.072996, mean edit distance: 0.111111
######   I  - src: "me amabas"
######   I  - res: "me amaba "
######   I WER: 0.500000, loss: 0.098463, mean edit distance: 0.071429
######   I  - src: "cuándo termina"
######   I  - res: "cuando termina"
######   I WER: 1.000000, loss: 0.027957, mean edit distance: 0.100000
######   I  - src: "sabías eso"
######   I  - res: "sabíaseso"
######   I WER: 1.000000, loss: 0.089742, mean edit distance: 0.125000
######   I  - src: "ven solo"
######   I  - res: "vensolo"
######   I WER: 1.000000, loss: 0.092845, mean edit distance: 0.100000
######   I  - src: "te matarán"
######   I  - res: "tematarán"
######   I WER: 1.000000, loss: 0.092845, mean edit distance: 0.100000
######   I  - src: "te matarán"
######   I  - res: "tematarán"
######   I WER: 1.000000, loss: 0.099211, mean edit distance: 0.076923
######   I  - src: "has entendido"
######   I  - res: "hasentendido"




   -------------------------------------------------



###    German Uppercase Results:                    [de]




######   I Test of Epoch 15 - WER: 0.189181, loss: 32.588361254231685, mean edit distance: 0.075573
######   I WER: 0.125000, loss: 0.548302, mean edit distance: 0.023810
######   I - src: “Fr dieses Geld kann man sich nichts kaufen”
######   I - res: “Für dieses Geld kann man sich nichts kaufen”
######   I WER: 0.142857, loss: 0.420042, mean edit distance: 0.025641
######   I - src: “Sie ist nicht abhngig von der Forderung”
######   I - res: “Sie ist nicht abhängig von der Forderung”
######   I WER: 0.142857, loss: 0.467154, mean edit distance: 0.022222
######   I - src: “um die Sicherheit des Systems zu gewhrleisten”
######   I - res: “Um die Sicherheit des Systems zu gewhrleisten”
######   I WER: 0.142857, loss: 0.512185, mean edit distance: 0.027778
######   I - src: “Es gibt immer nur noch hhere Steuern”
######   I - res: “Es gibt immer nur noch höhere Steuern”
######   I WER: 0.142857, loss: 0.615085, mean edit distance: 0.016393
######   I - src: “die achtzehn Hundert achtundsiebzig zwischen dem Hauptbahnhof”
######   I - res: “Die achtzehn Hundert achtundsiebzig zwischen dem Hauptbahnhof”
######   I WER: 0.200000, loss: 0.396312, mean edit distance: 0.030303
######   I - src: “Viele Menschen fhlen sich belogen”
######   I - res: “Viele Menschen fühlen sich belogen”
######   I WER: 0.200000, loss: 0.480538, mean edit distance: 0.048780
######   I - src: “im Sommer achtzehn Hundert achtunddreißig”
######   I - res: "Im Sommer achtzehn Hundert achtunddreißig "
######   I WER: 0.250000, loss: 0.135146, mean edit distance: 0.041667
######   I - src: “Die Kapazitt wurde erhht”
######   I - res: “Die Kapazität wurde erhht”
######   I WER: 0.250000, loss: 0.493074, mean edit distance: 0.062500
######   I - src: “Ich mache sie zu”
######   I - res: “Ich mache Sie zu”
######   I WER: 0.250000, loss: 0.601982, mean edit distance: 0.058824
######   I - src: “Das Ende ist nahe”
######   I - res: "Das Ende ist nah "


   -------------------------------------------------



###    French Results:                    [fr]

   

####     ----- options:                      
#####    <--->size                          [5-10000]
#####    <--->duration                      [0.5-15]
#####    <--->bitrate                       [0]
#####    <--->samplerate                    [16000-48000]
#####    <--->channels                      [0]
#####    <--->wordcount                     [2-1500]
#####    <--->wordsec                       [0.2-1.8]
#####    <--->lettercount                   [0]
#####    <--->lettersec                     [0]
#####    <--->upvotes                       [0]
#####    <--->downvotes                     [0]
#####    <--->sectors                       [0]
####     ----- info: 
#####    <---> corpora                       [librivox-tatoeba-vox16-accent]                        
#####    <---> gb                            [26.14]
#####    <---> hours                         [226.8]
#####    <---> words                         [1932291]
#####    <---> letters                       [11767617]
#####    <---> words per sec                 [2.37]
#####    <---> letters per sec               [14.41]
#####    <---> all files                     [125625]
#####    <---> train files                   [87938]
#####    <---> test files                    [18845]
#####    <---> dev files                     [18845]


######   I Test of Epoch 11 - WER: 0.227659, loss: 38.279466658148145, mean edit distance: 0.123504
######   I WER: 0.333333, loss: 0.538573, mean edit distance: 0.166667
######   I  - src: "ceci est bon"
######   I  - res: "ceci est mon "
######   I WER: 0.333333, loss: 0.656955, mean edit distance: 0.166667
######   I  - src: "pour le tout"
######   I  - res: "pour le tour "
######   I WER: 0.333333, loss: 0.885854, mean edit distance: 0.062500
######   I  - src: "nous avons gagné"
######   I  - res: "nous avons gagne"
######   I WER: 0.333333, loss: 0.885854, mean edit distance: 0.062500
######   I  - src: "nous avons gagné"
######   I  - res: "nous avons gagne"
######   I WER: 0.500000, loss: 0.314220, mean edit distance: 0.333333
######   I  - src: "de qui"
######   I  - res: "ce qui "
######   I WER: 1.000000, loss: 0.245572, mean edit distance: 1.000000
######   I  - src: "ah"
######   I  - res: ""
######   I WER: 1.000000, loss: 0.448257, mean edit distance: 1.000000
######   I  - src: "ah"
######   I  - res: ""
######   I WER: 1.000000, loss: 0.448257, mean edit distance: 1.000000
######   I  - src: "ah"
######   I  - res: ""
######   I WER: 1.000000, loss: 0.628055, mean edit distance: 0.333333
######   I  - src: "oui"
######   I  - res: "ou "
######   I WER: 1.000000, loss: 0.628055, mean edit distance: 0.333333
######   I  - src: "oui"
######   I  - res: "ou "





   -------------------------------------------------

###    Italian Results:                    [it]

   

####     ----- options:                       
#####    <---> corpora                       [librivox-vox-tatoeba]
#####    <---> size                          [5-10000]
#####    <---> duration                      [0.2-15]
#####    <---> bitrate                       [0]
#####    <---> samplerate                    [16000-48000]
#####    <---> channels                      [0]
#####    <---> wordcount                     [2-1500]
#####    <---> wordsec                       [0.2-1.9]
#####    <---> lettercount                   [0]
#####    <---> lettersec                     [0]
#####    <---> upvotes                       [0]
#####    <---> downvotes                     [0]
#####    <---> sectors                       [0]

####     ----- info:                       
#####    <---> gb                            [20.01]
#####    <---> hours                         [146.5]
#####    <---> words                         [1144530]
#####    <---> letters                       [6766871]
#####    <---> words per sec                 [2.17]
#####    <---> letters per sec               [12.83]
#####    <---> all files                     [83291]
#####    <---> train files                   [58304]
#####    <---> test files                    [12495]
#####    <---> dev files                     [12495]


######   I Test of Epoch 10 - WER: 0.184894, loss: 28.62499210021505, mean edit distance: 0.075463           
######   I WER: 0.083333, loss: 1.599633, mean edit distance: 0.029851
######   I  - src: "cosí riflettendo su le sue sciagure bruno celèsia si ridusse a casa"
######   I  - res: "così riflettendo su le sue sciagure bruno celèsia si ridusse a casa "
######   I WER: 0.090909, loss: 1.664164, mean edit distance: 0.033333
######   I  - src: "abbiamo forse fatto male no niente di male rispose il medico"
######   I  - res: "abbiamo forse fatto male no niente di male rispose il medio "
######   I WER: 0.100000, loss: 1.168548, mean edit distance: 0.033898
######   I  - src: "perchè vedete signora voi siete stata la pietra di paragone"
######   I  - res: "perché vedete signora voi siete stata la pietra di paragone "
######   I WER: 0.100000, loss: 1.493682, mean edit distance: 0.016129
######   I  - src: "state zitto avaraccio gridò carmaux che slegava il povero uomo"
######   I  - res: "state zitto avaraccio gridò carmaux che slegava il povero uuomo"
######   I WER: 0.100000, loss: 1.706887, mean edit distance: 0.040816
######   I  - src: "oh esclamò in quel momento toby che si era levato"
######   I  - res: "o esclamò in quel momento toby che si era levato "
######   I WER: 0.142857, loss: 0.449785, mean edit distance: 0.046512
######   I  - src: "giunsi al paese senza averne fissato alcuno"
######   I  - res: "giunse al paese senza averne fissato alcuno "
######   I WER: 0.142857, loss: 1.841321, mean edit distance: 0.058824
######   I  - src: "le ricerche durarono più d un mese"
######   I  - res: "le ricerche durarono più di un mese "
######   I WER: 0.200000, loss: 0.612865, mean edit distance: 0.083333
######   I  - src: "ah e quale filippo ferri"
######   I  - res: "a e quale filippo ferri "
######   I WER: 0.200000, loss: 0.969935, mean edit distance: 0.086957
######   I  - src: "entrai in un altra sala"
######   I  - res: "entra in un altra sala "
######   I WER: 0.200000, loss: 0.969935, mean edit distance: 0.086957
######   I  - src: "entrai in un altra sala"
######   I  - res: "entra in un altra sala "



   -------------------------------------------------

###    Ukranian Results:                   [uk]

   

####     ----- options:                       
#####    <---> corpora                       [librivox-vox-tatoeba]
#####    <---> size                          [5-100000]
#####    <---> duration                      [0.5-15]
#####    <---> bitrate                       [0]
#####    <---> samplerate                    [16000-48000]
#####    <---> channels                      [0]
#####    <---> wordcount                     [2-1500]
#####    <---> wordsec                       [0.2-1.8]
#####    <---> lettercount                   [0]
#####    <---> lettersec                     [0]
#####    <---> upvotes                       [0]
#####    <---> downvotes                     [0]
#####    <---> sectors                       [0]

####     ----- info:                       
#####    <---> gb                            [10.03]
#####    <---> hours                         [71.8]
#####    <---> words                         [500062]
#####    <---> letters                       [3013061]
#####    <---> words per sec                 [1.94]
#####    <---> letters per sec               [11.66]
#####    <---> all files                     [31930]
#####    <---> train files                   [22351]
#####    <---> test files                    [4791]
#####    <---> dev files                     [4791]


######   I Test of Epoch 10 - WER: 0.299552, loss: 41.175528268814084, mean edit distance: 0.117625
######   I WER: 0.250000, loss: 1.425027, mean edit distance: 0.117647
######   I  - src: "але як се зробити"
######   I  - res: "але як це зробити "
######   I WER: 0.250000, loss: 1.425027, mean edit distance: 0.117647
######   I  - src: "але як се зробити"
######   I  - res: "але як це зробити "
######   I WER: 0.285714, loss: 2.314395, mean edit distance: 0.066667
######   I  - src: "тож до тебе я зверну свою мову"
######   I  - res: "то ж до тебе я зверну свою мову "
######   I WER: 0.285714, loss: 2.314395, mean edit distance: 0.066667
######   I  - src: "тож до тебе я зверну свою мову"
######   I  - res: "то ж до тебе я зверну свою мову "
######   I WER: 0.333333, loss: 2.467164, mean edit distance: 0.250000
######   I  - src: "а чия ти"
######   I  - res: "а чи ти "
######   I WER: 0.333333, loss: 2.467164, mean edit distance: 0.250000
######   I  - src: "а чия ти"
######   I  - res: "а чи ти "
######   I WER: 0.500000, loss: 2.119555, mean edit distance: 0.142857
######   I  - src: "ні сину"
######   I  - res: "ні син "
######   I WER: 0.500000, loss: 2.119555, mean edit distance: 0.142857
######   I  - src: "ні сину"
######   I  - res: "ні син "
######   I WER: 1.000000, loss: 0.684362, mean edit distance: 0.333333
######   I  - src: "яку"
######   I  - res: "як "
######   I WER: 1.000000, loss: 0.684362, mean edit distance: 0.333333
######   I  - src: "яку"
######   I  - res: "як "







   -------------------------------------------------

###    Russian Results:                    [ru]

   

####     ----- options:                      
#####    <---> size                          [5-10000]
#####    <---> duration                      [0.5-15]
#####    <---> bitrate                       [0]
#####    <---> samplerate                    [16000-48000]
#####    <---> channels                      [0]
#####    <---> wordcount                     [2-1500]
#####    <---> wordsec                       [0.2-1.8]
#####    <---> lettercount                   [0]
#####    <---> lettersec                     [0]
#####    <---> upvotes                       [0]
#####    <---> downvotes                     [0]
#####    <---> sectors                       [0]
####     ----- info:                         
#####    <---> gb                            [6.8]
#####    <---> hours                         [59.1]
#####    <---> words                         [406385]
#####    <---> letters                       [2507215]
#####    <---> words per sec                 [1.91]
#####    <---> letters per sec               [11.79]
#####    <---> all files                     [29083]
#####    <---> train files                   [20360]
#####    <---> test files                    [4363]
#####    <---> dev files                     [4363]


######   I Test of Epoch 12 - WER: 0.369255, loss: 49.01442650910262, mean edit distance: 0.155081                                                  
######   I WER: 0.500000, loss: 0.076582, mean edit distance: 0.200000
######   I  - src: "я том"
######   I  - res: "я то "
######   I WER: 0.500000, loss: 0.076582, mean edit distance: 0.200000
######   I  - src: "я том"
######   I  - res: "я то "
######   I WER: 0.500000, loss: 0.199971, mean edit distance: 0.166667
######   I  - src: "я села"
######   I  - res: "я сел "
######   I WER: 0.500000, loss: 0.199971, mean edit distance: 0.166667
######   I  - src: "я села"
######   I  - res: "я сел "
######   I WER: 0.500000, loss: 0.276903, mean edit distance: 0.200000
######   I  - src: "это я"
######   I  - res: "это "
######   I WER: 0.500000, loss: 0.276903, mean edit distance: 0.200000
######   I  - src: "это я"
######   I  - res: "это "
######   I WER: 0.500000, loss: 0.312152, mean edit distance: 0.142857
######   I  - src: "кто она"
######   I  - res: "кто он "
######   I WER: 0.500000, loss: 0.312152, mean edit distance: 0.142857
######   I  - src: "кто она"
######   I  - res: "кто он "
######   I WER: 0.500000, loss: 0.868555, mean edit distance: 0.285714
######   I  - src: "вы одна"
######   I  - res: "в одна "
######   I WER: 0.500000, loss: 0.868555, mean edit distance: 0.285714
######   I  - src: "вы одна"
######   I  - res: "в одна "





   -------------------------------------------------

###    Dutch Results:                      [nl]

   

###### ----- options:                       
#####    <---> corpora                       [swc-vox-tatoeba]
#####    <---> size                          [5-10000]
#####    <---> duration                      [0.5-15]
#####    <---> bitrate                       [0]
#####    <---> samplerate                    [16000-48000]
#####    <---> channels                      [0]
#####    <---> wordcount                     [2-1500]
#####    <---> wordsec                       [0.25-1.9]
#####    <---> lettercount                   [0]
#####    <---> lettersec                     [0]
#####    <---> upvotes                       [0]
#####    <---> downvotes                     [0]
#####    <---> sectors                       [0]

####     ----- info:                       
#####    <---> gb                            [10.10]
#####    <---> hours                         [75.0]
#####    <---> words                         [598945]
#####    <---> letters                       [3752358]
#####    <---> words per sec                 [2.22]
#####    <---> letters per sec               [13.9]
#####    <---> all files                     [43711]
#####    <---> train files                   [30598]
#####    <---> test files                    [6558]
#####    <---> dev files                     [6558]


######   I Test of Epoch 9 - WER: 0.396161, loss: 92.96824162893921, mean edit distance: 0.193605                            
######   I WER: 0.083333, loss: 3.263168, mean edit distance: 0.014706
######   I  - src: "de buurtschap ligt ten zuiden van dasselaar en ten westen van norden"
######   I  - res: "de buurtschap ligt ten zuiden van dasselaar en ten westen van noorden"
######   I WER: 0.125000, loss: 3.376268, mean edit distance: 0.026316
######   I  - src: "het is een restant van de oude zeedijk"
######   I  - res: "het is een restant van de oude zeedik"
######   I WER: 0.142857, loss: 2.820412, mean edit distance: 0.025000
######   I  - src: "de herkomst van dit wapen is onduidelijk"
######   I  - res: "de herkomst van dit wapen is onduidenlijk"
######   I WER: 0.142857, loss: 3.029150, mean edit distance: 0.028571
######   I  - src: "het ligt iets ten noorden van gendt"
######   I  - res: "het ligt iets ten noorden van gent"
######   I WER: 0.142857, loss: 3.029150, mean edit distance: 0.028571
######   I  - src: "het ligt iets ten noorden van gendt"
######   I  - res: "het ligt iets ten noorden van gent"
######   I WER: 0.142857, loss: 3.058265, mean edit distance: 0.025641
######   I  - src: "bij het buurtje lag een wierde die in de negentiende eeuw geheel is afgegraven"
######   I  - res: "bij het buurtje lag een wierde die in de negentien e eeuw geheel is afgegraven "
######   I WER: 0.222222, loss: 2.067109, mean edit distance: 0.023256
######   I  - src: "het dorp ligt op de rechteroever van de lek"
######   I  - res: "het dorp ligt op de rechter oever van de lek"
######   I WER: 0.285714, loss: 1.334180, mean edit distance: 0.025000
######   I  - src: "het dorp ontstond in de negentiende eeuw"
######   I  - res: "het dorp ontstond in de negentien e eeuw"
######   I WER: 0.333333, loss: 2.122649, mean edit distance: 0.017857
######   I  - src: "in duizendzeshonderdeenenvijftig wordt een sluis gebouwd"
######   I  - res: "in duizendzeshonderdeenenvijftig wordt een sluisgebouwd"
######   I WER: 0.333333, loss: 2.648912, mean edit distance: 0.026316
######   I  - src: "hier wordt lesgegeven aan de onderbouw"
######   I  - res: "hier wordt les gegeven aan de onderbouw"




   -------------------------------------------------

###   Portuguese Results:                      [pt]

   

####   ----- options:                      
#####    <---> size                          [5-10000]
#####    <---> duration                      [0.5-15]
#####    <---> bitrate                       [0]
#####    <---> samplerate                    [16000-48000]
#####    <---> channels                      [0]
#####    <---> wordcount                     [2-1500]
#####    <---> wordsec                       [0.2-1.8]
#####    <---> lettercount                   [0]
#####    <---> lettersec                     [0]
#####    <---> upvotes                       [0]
#####    <---> downvotes                     [0]
#####    <---> sectors                       [0]
####   ----- info:                         
#####    <---> corpora                       [tatoeba-vox16]
#####    <---> gb                            [1.13]
#####    <---> hours                         [9.8]
#####    <---> words                         [66346]
#####    <---> letters                       [352192]
#####    <---> words per sec                 [1.88]
#####    <---> letters per sec               [9.98]
#####    <---> all files                     [13684]
#####    <---> train files                   [9579]
#####    <---> test files                    [2054]
#####    <---> dev files                     [2054]



######   I Test of Epoch 10 - WER: 0.507568, loss: 21.292116564373636, mean edit distance: 0.244271                                                 
######   I WER: 0.200000, loss: 1.065989, mean edit distance: 0.058824
######   I  - src: "não foi tom não é"
######   I  - res: "não foi tom não "
######   I WER: 0.250000, loss: 1.081908, mean edit distance: 0.200000
######   I  - src: "tom não tem pai"
######   I  - res: "tom não tem "
######   I WER: 0.250000, loss: 1.081908, mean edit distance: 0.200000
######   I  - src: "tom não tem pai"
######   I  - res: "tom não tem "
######   I WER: 0.333333, loss: 1.577532, mean edit distance: 0.083333
######   I  - src: "tom é cantor"
######   I  - res: "tom é cantour"
######   I WER: 0.333333, loss: 1.577532, mean edit distance: 0.083333
######   I  - src: "tom é cantor"
######   I  - res: "tom é cantour"
######   I WER: 0.500000, loss: 1.114254, mean edit distance: 0.083333
######   I  - src: "estou seguro"
######   I  - res: "estou segura"
######   I WER: 0.500000, loss: 1.114254, mean edit distance: 0.083333
######   I  - src: "estou seguro"
######   I  - res: "estou segura"
######   I WER: 0.500000, loss: 1.841137, mean edit distance: 0.333333
######   I  - src: "oi tom"
######   I  - res: "o tom "
######   I WER: 0.500000, loss: 1.879081, mean edit distance: 0.100000
######   I  - src: "não corras"
######   I  - res: "não coras"
######   I WER: 0.500000, loss: 1.879081, mean edit distance: 0.100000
######   I  - src: "não corras"
######   I  - res: "não coras"











