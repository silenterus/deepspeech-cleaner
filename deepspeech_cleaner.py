#! /usr/bin/env python


import os
import sys
import sqlite3
import string
import collections
import re
import shutil
sys.path.append(os.path.abspath(os.path.join(__file__, os.path.pardir)))
import argparse
import num2words
import random
import numpy as np
import sox
from cleaner import cleaning
import time




#
#   Regex patterns
#

int_pattern = re.compile(r'[0-9]+')
big_int_pattern = re.compile(r'[0-9]+[.][0-9][0-9][0-9]')
float_pattern = re.compile(r'[0-9]+[,\.][0-9]+')
single_letter = re.compile(r' [a-zA-Z] ')
weird_nums = re.compile(r' [0][0][0]+[0-9]+')
ext_pattern = re.compile(r'\.wav')
question_pattern = re.compile(r'\?')
sign_pattern = re.compile(r"'")
raute_pattern = re.compile(r'#')
at_pattern = re.compile(r'@')
minmax_pattern = re.compile(r'-')
standard_letter = re.compile(r'[a-zA-Z]')















def sentences_prepare(lang):


    changer = []

    replacer = cleaning.get_replacer()

    with open('cleaner/' + str(lang) + '/alphabet.txt' ) as f:
        lines = f.read()
        lines = str(lines).split('\n')
        maxline = len(lines)
        for letter in lines:

            if standard_letter.search(letter):
                pass
            elif raute_pattern.search(letter):
                pass
            elif letter == ' ':
                pass
            elif letter == '\n':
                print('   <>-<> just linebreak')
            elif letter == '':
                pass
            elif sign_pattern.search(letter):
                pass
            elif letter == '\#':
                num_word = num2words.num2words(int(len(changer)), lang='de')
                changer.append([str('@' + str(num_word) + '@'),'#'])
                #print('   <>-<> adding symbol [' + str(letter) + ']')
            else:
                num_word = num2words.num2words(int(len(changer)), lang='de')
                changer.append([str('@' + str(num_word) + '@'),letter])
                #print('   <>-<> adding symbol [' + str(letter) + ']')

    return [changer,replacer]


def query_prepare():
    all_query = []
    for root, dirs, files in os.walk('cleaner/' + str(lang) + '/sql_query/' ):
        for file in files:
            query = []
            if file.endswith('not.txt'):
                query.append(0)
            elif file.endswith('.txt'):
                query.append(1)
            if file.endswith('not.txt') or file.endswith('.txt'):
                query.append(os.path.join(root, file))
                all_query.append(query)


    if len(all_query) == 0:
        print('   ¦¦!¦¦ no sql query files found')
        exit(1)



    sql = []


    for query in all_query:

        row = []
        row.append(query[0]) 
        row.append(str(query[1]).replace('_not.txt','').replace('.txt','').replace('cleaner/de/sql_query/','')) #lazy

        with open(query[1]) as f:
            lines = f.read()
            lines = str(lines).split('\n')


            if lines[0] == '' or lines[0] == '\n' or lines[0] == ' ':
                pass
            else:
                for line in lines: 
                    #just in case
                    if line == '' or line == '\n' or line == ' ':
                        pass
                    else:
                        row.append(str(line))



       
        sql.append(row) 
        f.close()




    return sql


def sentences_covert(changer,sentence,convert):
    for change in changer:
        if convert == 0:
            sentence = str(sentence).replace(change[0],change[1])
        elif convert == 1:
            sentence =  str(sentence).replace(change[1],change[0])

    if convert == 1:

        # spaces at the start and end to ensure we can parse the whole sentence not only one word.
        sentence =  '> ' + str(sentence.encode('ascii',errors='ignore')).replace('b\'','') + ' <'
    elif convert == 0:

        # just making sure all bs is gone        
        sentence = re.sub(" [^a-zA-Z]+ ", "", sentence).replace(u'\xad','').replace(u'\xa0', u' ')
        sentence =  sentence.replace('> ', '').replace(' <', '').replace(',', ' ').replace('‚', ' ').replace('<', ' ').replace('>', ' ').replace('   ', ' ').replace('   ', ' ').replace('  ', ' ').replace('  ', ' ').replace('@', ' ').replace('\'','').strip()

    return sentence

def sentences_cleaner(changer,sentences):






    sentences = str(sentences_covert(changer,sentences,1)).replace('\\n\'','')





    replacer = cleaning.get_replacer()




    # 1. translate any weird char that might be a legit letter
    # 2. translate abbreviations...some need caps
    # 3. translate numerical adverb and lower cap
    # 4. translate special characters
    # 5. replace chars that might indicate a space
    index = 0
    for replace in replacer:

        if replace == 'lower':
            sentences = sentences.lower()
        elif replace == 'upper':
            sentences = sentences.upper()
        else:
            if index == 3:
                sentences = sentences.lower()
            for rep in replace.items():
                sentences = sentences.replace(rep[0], rep[1])
        index += 1



    # translating bigger int's > 999 
    match = big_int_pattern.search(sentences)

    
    while match is not None:
        num_word = num2words.num2words(int(match.group().replace('.', '')), lang=lang)
        before = sentences[:match.start()]
        after = sentences[match.end():]
        sentences = ' '.join([before, num_word, after])
        match = big_int_pattern.search(sentences)




    # translating floats 
    match = float_pattern.search(sentences)

    
    while match is not None:
        num_word = num2words.num2words(float(match.group().replace(',', '.')), lang=lang).lower()
        before = sentences[:match.start()]
        after = sentences[match.end():]
        sentences = ' '.join([before, num_word, after])
        match = float_pattern.search(sentences)



    # translating ints 
    match = int_pattern.search(sentences)

 
    # don't add sentences with weird numbers like 000021 - not worth it
    if weird_nums.search(sentences):
        return False

    # only translate int's without zero 
    while match is not None:
        num_word = num2words.num2words(int(match.group()), lang=lang)
        before = sentences[:match.start()]
        after = sentences[match.end():]
        sentences = ' '.join([before, num_word, after])
        match = int_pattern.search(sentences)







    sentences = str(sentences).replace('?',' ').strip()





    # dont use the sentence 
    # if it is only one char long           > too short
    # if it contain a word with only one char > something went wrong

    if single_letter.search(sentences) or len(sentences) < 2:
        return False
    else:
        sentences = sentences_covert(changer,sentences,0)
        return sentences






def get_extension(filename):
    basename = os.path.basename(filename)  
    ext = '.'.join(basename.split('.')[1:])
    return '.' + ext if ext else None




def get_size(size,types):
    value = 0
    for siz in size:
        if siz is not 'None':
            value += siz
    if types == 'size':
        value = value/1000000000
        print('   <>-<> [' + str(value) + '] GB')
    elif types == 'duration':
        value = value

        print('   <>-<> [' + str(round(value,1)) + '] sek')
        print('   <>-<> [' + str(round((value/60),1)) + '] mins')
        print('   <>-<> [' + str(round((value/60/60),1)) + '] hours')
    return round(value,1)

def check_symbols(sentences):

    match = question_pattern.search(str(sentences))
    if match is not None:

        return False
    match = sign_pattern.search(str(sentences))
    if match is not None:

        return False

    return True





def create_new_db(): 
    if os.path.isfile("audio.db") == True:
        connection = sqlite3.connect("audio.db")    
        cursor = connection.cursor()
        sql_command = """select deepspeech_dir,configs_id from configs limit 1"""

        cursor.execute(sql_command)

        deepspeech_data = cursor.fetchall()
    
        if deepspeech_data[0][0] == 'default':
            deepspeech_path = get_deepspeech()

            sql_command = """update configs set deepspeech_dir='""" + str(deepspeech_path[0]) + """' where configs_id=""" + str(deepspeech_data[0][1]) + """"""  
            print(sql_command)
            cursor.execute(sql_command)
            connection.commit()
            connection.close()
            print('   >---< new DeepSpeech path : [' + str(deepspeech_path) + ']')
        else:
            deepspeech_path = deepspeech_data[0][0]
        #os.remove("audio.db") 
            print('   >---< DeepSpeech path : [' + str(deepspeech_path) + ']')
    else:
        connection = sqlite3.connect("audio.db")    
        cursor = connection.cursor()



        sql_command = """CREATE TABLE "audios" (
    	    `audios_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    	    `size`	INTEGER,
    	    `duration`	INTEGER,
    	    `samples`	INTEGER,
    	    `wordcount`	INTEGER,
    	    `upvotes`	INTEGER,
    	    `downvotes`	INTEGER,
    	    `quality`	TEXT,
    	    `distance`	TEXT,
    	    `wav_path`	TEXT UNIQUE,
    	    `gender`	TEXT,
    	    `age`	TEXT,
    	    `speaker`	TEXT,
    	    `text`	TEXT,
    	    `cleantext`	TEXT,
    	    `samplerate`	TEXT,
    	    `bitrate`	INTEGER,
    	    `channels`	INTEGER,
    	    `codec`	TEXT,
    	    `words_per_sec`	INTEGER,
    	    `dialect`	TEXT,
    	    `dataset`	TEXT,
    	    `errors`	INTEGER,
    	    `lang`	TEXT,
    	    `letters`	INTEGER,
    	    `letters_per_sek`	INTEGER
        )"""  
    

    
        cursor.execute(sql_command)
    
        sql_command = """CREATE TABLE "trainings" (
    	    `trainings_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    	    `configs_id`	INTEGER,
    	    `name`	TEXT,
    	    `current_epoch`	INTEGER DEFAULT 0,
    	    `duration`	INTEGER DEFAULT 0,
    	    `size`	INTEGER DEFAULT 0,
    	    `files_num`	INTEGER DEFAULT 0,
    	    `lang`	TEXT
        )"""  
    

    
        cursor.execute(sql_command)




    
        sql_command = """CREATE TABLE "configs" (
    	    `configs_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    	    `name`	TEXT,
    	    `deepspeech_dir`	TEXT,
    	    `deepspeech_version`	TEXT,
    	    `earlystop_nsteps`	INTEGER DEFAULT 5,
    	    `train_batch_size`	INTEGER DEFAULT 24,
    	    `dev_batch_size`	INTEGER DEFAULT 48,
    	    `test_batch_size`	INTEGER DEFAULT 48,
    	    `n_hidden`	INTEGER DEFAULT 2048,
    	    `learning_rate`	INTEGER DEFAULT 0.0001,
    	    `dropout_rate`	INTEGER DEFAULT 0.2,
    	    `display_step`	INTEGER DEFAULT 0,
    	    `epoch`	INTEGER DEFAULT 50,
    	    `validation_step`	INTEGER DEFAULT 1
        )"""  
    
    
        deepspeech_path = get_deepspeech()
    
        cursor.execute(sql_command)
        sql_command = """insert into configs(name,deepspeech_dir,deepspeech_version,earlystop_nsteps,train_batch_size,dev_batch_size,test_batch_size,n_hidden,learning_rate,dropout_rate,display_step,validation_step) values('default','""" + str(deepspeech_path[0]) + '\',\'' + str(deepspeech_path[1]) + """',5,24,48,48,2048,0.0001,0.2,0,1)"""  
    
        cursor.execute(sql_command)

        sql_command = """insert into trainings(configs_id,name) values(1,'default')"""  
    
        cursor.execute(sql_command)
        connection.commit()
        connection.close()
        print ('   >---< DB CREATED')

    return deepspeech_path


def get_deepspeech():

    deepspeech_dir = input("plz enter DeepSpeech path : ")
    if os.path.isfile(deepspeech_dir + '/DeepSpeech.py') == False:
        print("   ¦¦!¦¦ DeepSpeech.py not found")
        exit(1)
    else:
        if os.path.isfile(deepspeech_dir + '/VERSION') == True:
            print('   >---< VERSION found')

            with open(deepspeech_dir + '/VERSION') as f:
                version = f.read()
            f.close()
        else:
            print('   >---< VERSION not found')
            version = input("plz enter DeepSpeech VERSION manually : ")
    print(str('   >---< [') + str(version).replace('\n','') + str(']'))

    return [deepspeech_dir,version]






def deepspeech_parser(path):
    all_csv = []
    all_wavdata = []
    index = 0
    notfound = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.csv'):
                csvpath=os.path.join(root, file)
                all_csv.append(csvpath)


    if len(all_csv) == 0:
        print('   ¦¦!¦¦ no csv files found in [' + str(csvpath) +']')
        exit(1)
    else:
        print('   >---< found [' + str(len(all_csv)) +'] csv files')

    #get all lines
    maxcsv = len(all_csv) 
    all_lines = 0
    for csv in all_csv:
        with open(csv) as f:
            lines = f.read()
            lines = str(lines).split('\n')
            all_lines += len(lines) 
        f.close()
    index = 0
    print('   >---< analyze audio files')


    starttime = int(time.time()) 
    for csv in all_csv:

        with open(csv) as f:
            lines = f.read()
            lines = str(lines).split('\n')
            maxline = len(lines) 
            row = 0
            for line in lines: 
                index += 1
                row += 1
               
                if row % 100 == 0:
                    show_progress(starttime,index,all_lines, 'analyzing audio files')
                    print('   >---< [' + str(index) + '/' + str(all_lines) + ']')
                    print('   >---< [' + str(row) + '/' + str(maxline) + ']')
                    print('   ¦¦!¦¦ [' + str(notfound) + ']')
                    if len(all_wavdata) > 100:
                        insert_db(all_wavdata)
                        all_wavdata = []

                data = str(line).split(',')

                if len(data) == 8:





                    csv_reg = '/'.join(csv.split('/')[-1:])
                    csv_path = csv.replace(csv_reg,'')

                    if os.path.isfile(str(csv_path) + str(data[0])) == False:
                        notfound += 1

                    else:

                        wavdata = get_data_array()
                        wavdata[6] = str(csv_path) + str(data[0])
                        wavdata[10] = str(data[1]).replace('\'','\'\'')
                        wavdata[18] = data[2]
                        wavdata[19] = data[3]
                        wavdata[8] = data[4]
                        wavdata[7] = data[5]
                        wavdata[16] = data[6]
                        wavdata[17] = 'cv'
     
                        wavdata = scan_file(wavdata)
                        all_wavdata.append(wavdata)



       

        f.close()







def get_data_array():
    wavdata = []
    for x in range(24):
        wavdata.append(0)
    return wavdata
    





def scan_file(data):
    try:
        data[1] = sox.file_info.duration(data[6])
    except:
        data[20] = 8
    try:
        data[13] = sox.file_info.channels(data[6])
    except:
        data[20] = 8
    ext = get_extension(data[6])
    if str(ext) == '.wav':        
        try:
            data[12] = sox.file_info.bitrate(data[6])
        except:
            data[20] = 8


    try:
        data[2] = sox.file_info.num_samples(data[6])
    except:
        data[20] = 8
    try:
        data[11] = sox.file_info.sample_rate(data[6])
    except:
        data[20] = 8
    try:
        data[14] = sox.file_info.encoding(data[6])
    except:
        data[20] = 8
    data[0] = os.path.getsize(data[6])

    data[3] = len(data[10].split(' '))
    data[15]  = data[1]/data[3]


    data[21] = str(lang)
    data[22] = len(data[10])
    data[23]  = data[1]/data[22]
    return data



def show_progress(start,current,maxlen,work):

    elapsed = int(time.time())-int(start) 

    progress = ''
    current_percent = (current/maxlen)*100



    for x in range(50):
        percent = x * 2
        if percent < current_percent:
            progress = progress + '#'
        else:
            progress = progress + '¦'
        
    estimate = (elapsed/100)*percent
    os.system('clear')
    print('') 
    print('                     ' + str(work))
    print('')
    #print('                                            ' + str(elapsed) + ' sek / estimate ' + str(estimate) + ' sek')
    print('   ' + str(progress))
    print('                          [' + str(round(current_percent,2)) + '%]' )
    print('')
    print('   >---< ' + str(current) + '/' + str(maxlen) + '' )




def insert_db(all_wavdata):

 


            #INTEGER 0. size      
            #INTEGER 1. duration  
            #INTEGER 2. samples   
            #INTEGER 3. wordcount
            #TEXT    4. quality
            #TEXT    5. distance
            #TEXT    6. wav_path
            #TEXT    7. gender
            #TEXT    8. age
            #TEXT    9. speaker
            #TEXT    10. text
            #INTEGER 11. samplerate
            #INTEGER 12. bitrate 
            #INTEGER 13. channels
            #TEXT    14. codec 
            #INTEGER 15. words_per_sec
            #TEXT    16. dialect
            #TEXT    17. dataset
            #INTEGER    18. upvotes
            #INTEGER    19. downvotes
            #INTEGER    20. errors
            #INTEGER    21. language
            #INTEGER    22. letters
            #INTEGER    23. letters_per_sec



    connection = sqlite3.connect("audio.db")    
    cursor = connection.cursor()
    
    for wavdata in all_wavdata:

      
    
        sql_command = """insert or ignore into audios(size,duration,samples,wordcount,quality,distance,wav_path,gender,age,speaker,text,samplerate,bitrate,channels,codec,words_per_sec,dialect,dataset,upvotes,downvotes,errors,lang,letters,letters_per_sek) values(""" + str(wavdata[0]) + ',' + str(wavdata[1])  + ',' + str(wavdata[2]) + ',' + str(wavdata[3]) + ',\'' + str(wavdata[4]) + '\',\'' + str(wavdata[5]) + '\',\'' + str(wavdata[6]).replace('/home/silenter/deepspeech-ger/','') + '\',\'' + str(wavdata[7]) + '\',\'' + str(wavdata[8]) + '\',\'' + str(wavdata[9]) + '\',\'' + str(wavdata[10]) + '\',' + str(wavdata[11]) + ',' + str(wavdata[12])  + ',' + str(wavdata[13])  + ',\'' + str(wavdata[14])  + '\',' + str(wavdata[15])  + ',\'' + str(wavdata[16])  + '\',\'' + str(wavdata[17]) + '\',' + str(wavdata[18]) + ',' + str(wavdata[19]) + ',' + str(wavdata[20]) + ',\'' + str(wavdata[21]) + '\',' + str(wavdata[22]) + ',' + str(wavdata[23]) + """)"""  
    
    
        cursor.execute(sql_command)

    connection.commit()
    connection.close()


def create_train_files():


    connection = sqlite3.connect("audio.db")    
    cursor = connection.cursor()




    query = create_query()
 
    sqlquery = """SELECT dataset,wav_path,size,text,duration from audios where errors=0 and lang='""" + str(lang) + """'""" + str(query) + """"""
    cursor.execute(sqlquery)
    data = cursor.fetchall()
    olddata = True
    failer = 0  
    notfound = 0                    
    success = 0           
    newlines = []
    sizes = []  

    durations = []  

    prepare = sentences_prepare('de')
    changer = prepare[0]
    replacer = prepare[1]

    tri_sentences = []   
    index = 0
    starttime = int(time.time()) 
    for lines in data:
        cleaned = sentences_cleaner(changer,str(lines[3]))


       # print(cleaned) 
        #exit(1)

        if str(lines[0]) == 'cv': 
            data_dir = str(lines[1])
        else:           
            data_dir = current_dir  + '/' +  str(lines[1]).replace('.flac','.wav') 



        index += 1
        if cleaned == False: 
            failer += 1
        elif os.path.isfile(data_dir) == False:
            #print(data_dir)
            notfound += 1
        else:
            success += 1  
            tri_sentences.append(cleaned)
            sizes.append(lines[2])  
            durations.append(lines[4])                                  
            newlines.append(data_dir + ',' + str(lines[2]) + ',' + cleaned)
        if index % 10000 == 0:
            show_progress(starttime,index,len(data),'cleaning sentences')
            print('   -----------------------\n   <>-<> cleaned sentences ' + '[' + str(success) + ']' + '\n   ¦¦!¦¦ dropped sentences ' + '[' + str(failer) + ']\n' + '   ¦¦!¦¦ not found         ' + '[' + str(notfound) + ']\n')


    if len(newlines) != 0:
        all_size = get_size(sizes,'size')
        all_duration = get_size(durations,'duration')

        print('   <>-<> training size [' + str(all_size) + '] GB')
        print('   <>-<> training duration [' + str(all_duration) + '] sec')
        print('   <>-<> training files [' + str(len(newlines)) + ']')
    else:
        print('   ¦¦!¦¦ no sentences found or all failed')
        print('   ¦¦!¦¦ try other parameters')
        print('   ¦¦!¦¦ "python3 deepspeech_cleaner.py --help" for help')
        exit(1)
    maxlines = len(newlines)






    test = int(round(maxlines * 0.15 ))
    train = int(float(maxlines - test * 2 ))

    random.shuffle(newlines)

    test_files = []
    train_files = []
    dev_files = []
    test_files.append('wav_filename,wav_filesize,transcript')
    train_files.append('wav_filename,wav_filesize,transcript')
    dev_files.append('wav_filename,wav_filesize,transcript')


    for line in newlines:
        if len(test_files) <= test:
            test_files.append(line)
        elif len(dev_files) <= test:
            dev_files.append(line)
        else:
            train_files.append(line)



        
    print('   >---< train[' + str(len(train_files)) + ']')
    print('   >---< test[' + str(len(test_files)) + ']')
    print('   >---< dev[' + str(len(dev_files)) + ']')

    f = open(current_dir + '/training/'  + current_model + '/' + "dev.csv", "w")
    f.write("\n".join(dev_files))
    f.close()



    f = open(current_dir + '/training/' +  current_model + '/' + "train.csv", "w")
    f.write("\n".join(train_files))
    f.close()



    f = open(current_dir + '/training/' +  current_model + '/' + "test.csv", "w")
    f.write("\n".join(test_files))
    f.close()


    if trie == True:
        create_tri(tri_sentences,changer)


    connection.close()

   


    print('   >---< files created')





def uniq_mix(array,mix):

    array = sorted(array)
    check_array = ''
    unique = []
    print(len(array))
    for arr in array:
        if arr != check_array:
            check_array = arr
            unique.append(arr)
    
    print('removed [' + str(len(array)-len(unique)) + '] duplicates')  
    if mix == True:
        random.shuffle(unique)  
    return unique


def create_tri(sentences,changer):


    counter = 0
    with open(str(current_dir) + '/' + str(args.clean), 'r') as f:
        for text in f:
            counter += 1



    index = 0
    starttime = int(time.time()) 
    with open(str(current_dir) + '/' + str(args.clean), 'r') as f:
        for text in f:
            cleaned = sentences_cleaner(changer,str(text))
                                                
            if index % 10000 == 0:
                show_progress(starttime,index,counter,'cleaning corpora')
                #print('[' + str(index) + ']') 
            index += 1
            if cleaned == False: 
                pass
            else:
                sentences.append(str(cleaned))

    


    f.close()

    sentences = uniq_mix(sentences,True)


    f = open(current_dir + "/training/" + current_model + "/clean", "w")
    f.write("\n".join(sentences))
    f.close()




    cmd =  "lmplz --text " + current_dir + "/training/" + current_model + "/clean --arpa " +  current_dir + "/training/" + current_model + "/words.arpa --o 3" 
    os.system(cmd)


    cmd =  "build_binary trie -q 16 -b 7 -a 64 " + current_dir + "/training/" + current_model + "/words.arpa " + current_dir + "/training/" + current_model + "/lm.binary"
    os.system(cmd)

    if os.path.isfile(deepspeech_dir + "/native_client/generate_trie") == True:
        cmd =  deepspeech_dir + "/native_client/generate_trie " + current_dir + "/training/" + current_model + "/alphabet.txt " + current_dir + "/training/" + current_model + "/lm.binary " + current_dir + "/training/" + current_model + "/clean " + current_dir + "/training/" + current_model + "/trie"
    elif os.path.isfile(deepspeech_dir + "/generate_trie") == True:
        cmd =  deepspeech_dir + "/native_client/generate_trie " + current_dir + "/training/" + current_model + "/alphabet.txt " + current_dir + "/training/" + current_model + "/lm.binary " + current_dir + "/training/" + current_model + "/clean " + current_dir + "/training/" + current_model + "/trie"
    else:
        print('didnt find DeepSpeech/generate_trie or DeepSpeech/native_client/generate_trie')
        exit(1)







    



def create_folder(typ,lang):
    if typ == 'create':
        print('   <>-<> creating training folder + files')

        access_rights = 0o755
        os.makedirs( current_dir + '/training/' + current_model + '/checkpoints', access_rights )
        os.mkdir( current_dir + '/training/' + current_model + '/model_export', access_rights )
        shutil.copy2( current_dir + '/cleaner/' + str(lang) + '/alphabet.txt' ,  current_dir + '/training/' + current_model + '/') 

    elif typ == 'delete_model':
        shutil.rmtree( current_dir + '/training/' + current_model + '/', ignore_errors=True)
        print('   <>-<> DELETED ' + current_model)
    elif typ == 'delete_checkpoints':
        shutil.rmtree( current_dir + '/training/' + current_model + '/checkpoints/', ignore_errors=True)
        print('   <>-<> DELETED CHECKPOINTS OF ' + current_model)


def get_min_max(minmax):
    if minmax == '0':
        min_value = float(0)
        max_value = float(0)
    else:
        minmax = minmax.split('-')
        min_value = float(minmax[0])
        max_value = float(minmax[1])
    return [min_value,max_value]
    

def create_query():


    querys = query_prepare()

    sql = ''
    for query in querys:
        if len(query) > 2:
            if query[0] == 0:
                search = 'not'
            elif query[0] == 1:
                search = ''

            for x in range(len(query)):   
                if x > 2: 
                    sql = sql + ' and ' + str(query[1]) + ' ' + str(search) + ' like \'%' + str(query[x]) + '%\''     




    if size[0] != 0 and size[1] != 0:
        sql = sql + ' and size>=' + str(size[0]) + ' and size<='  + str(size[1])


    if duration[0] != 0 and duration[1] != 0:
        sql = sql + ' and duration>=' + str(duration[0]) + ' and duration<='  + str(duration[1])


    if bitrate[0] != 0 and bitrate[1] != 0:
        sql = sql + ' and bitrate>=' + str(bitrate[0]) + ' and bitrate<='  + str(bitrate[1])


    if samplerate[0] != 0 and samplerate[1] != 0:
        sql = sql + ' and samplerate>=' + str(samplerate[0]) + ' and samplerate<='  + str(samplerate[1])


    if channels[0] != 0 and channels[1] != 0:
        sql = sql + ' and channels>=' + str(channels[0]) + ' and channels<='  + str(channels[1])


    if wordcount[0] != 0 and wordcount[1] != 0:
        sql = sql + ' and wordcount>=' + str(wordcount[0]) + ' and wordcount<='  + str(wordcount[1])


    if wordsek[0] != 0 and wordsek[1] != 0:
        sql = sql + ' and words_per_sec>=' + str(wordsek[0]) + ' and words_per_sec<='  + str(wordsek[1])



    if lettercount[0] != 0 and lettercount[1] != 0:
        sql = sql + ' and letters>=' + str(lettercount[0]) + ' and letters<='  + str(lettercount[1])


    if lettersek[0] != 0 and lettersek[1] != 0:
        sql = sql + ' and letters_per_sec>=' + str(lettersek[0]) + ' and letters_per_sec<='  + str(lettersek[1])



    if upvotes[0] != 0 and upvotes[1] != 0:
        sql = sql + ' and upvotes>=' + str(upvotes[0]) + ' and upvotes<='  + str(upvotes[1])


    if downvotes[0] != 0 and downvotes[1] != 0:
        sql = sql + ' and downvotes>=' + str(downvotes[0]) + ' and downvotes<='  + str(downvotes[1])




    return sql



def check_dir():

    checkdir = os.getcwd()
    if os.path.isfile(str(checkdir) + "/deepspeech_cleaner.py") == True and os.path.isdir(str(checkdir) + '/cleaner/') == True:
        return checkdir
    else:
        print('   ¦¦!¦¦ ' + 'you need to be in the same path as \'deepspeech_cleaner.py\' ')
        exit(1)




if __name__ == '__main__':



    parser = argparse.ArgumentParser(description='DeepSpeech Dataset Cleaner')
    parser.add_argument('mode',help="create_files - [create training files from db],\n\ninsert_cv - [insert Common Voice Corpus in db],\n\ndelete_model - [delete training folder (containing all files and exported graphs)],\n\ndelete_checkpoints - [delete checkpoints  (containing all files and exported graphs)],\n\ncreate_trie - [creating trie file],\n\ncreate_lm - [creating lm.binary file],\n\ncreate_trie_lm - [creating trie and lm.binary file]",type=str)

    parser.add_argument('--training',help=" [%(default)s] path to model files", default='standard', type=str)

    parser.add_argument('--path',help=" [%(default)s] path to corpus", default='', type=str)

    parser.add_argument('--size',help="select min-max file size - 0 = all \'example : 300-100000\'\n\n[%(default)s]", default='300-450000', type=str)

    parser.add_argument('--duration',help="select min-max duration in sec - 0 = all \'example : 0.4-9.5\'\n\n[%(default)s]", default='0.5-11.1', type=str)
    parser.add_argument('--wordcount',help="select min-max words - 0 = all  \'example : 10-22\'\n\n[%(default)s]", default='0', type=str)
    parser.add_argument('--wordsek',help="select min-max words per sec - 0 = all \'example : 0.1-1.2\'\n\n[%(default)s]", default='0.1-1.5', type=str)


    parser.add_argument('--lettercount',help="select min-max letters - 0 = all  \'example : 10-22\'\n\n[%(default)s]", default='0', type=str)
    parser.add_argument('--lettersek',help="select min-max letters per sec - 0 = all \'example : 1.1-10.2\'\n\n[%(default)s]", default='0', type=str)

    parser.add_argument('--bitrate',help="select min-max bitrate - 0 = all  \'example : 8-16\'\n\n[%(default)s]", default='0', type=str)
    parser.add_argument('--samplerate',help="select min-max samplerate - 0 = all  \'example : 16000-22000\'\n\n[%(default)s]", default='0', type=str)
    parser.add_argument('--channels',help="select min-max channels - 0 = all \'example : 1-2\'\n\n[%(default)s]", default='0', type=str)


    parser.add_argument('--upvotes',help="select min-max upvotes - 0 = all \'example : 0-3\'\n\n[%(default)s]", default='0', type=str)
    parser.add_argument('--downvotes',help="select min-max downvotes - 0 = all \'example : 0-3\'\n\n[%(default)s]", default='0', type=str)
    parser.add_argument('--trie',help="automatically create trie and lm.binary after training files\n\n[%(default)s]", default=False, type=bool)

    parser.add_argument('--clean',help="path to clean corpora in case you want to build trie/lm.binary'\n\n[%(default)s]", default='cleaner/all_corpora_filtered_maryfied.txt', type=str)
    parser.add_argument('--cleaning_clean',help="clean corpora for trie/lm.binary first", default=False, type=bool)
    parser.add_argument('--lang',help="only \'de\' right now\n\n[%(default)s]", default='de', type=str)
  
    args = parser.parse_args()
    mode = args.mode

    if mode == '--help' or mode == 'help':
        pass
    else:
        current_dir = check_dir()
        deepspeech_dir = create_new_db()


        trie = args.trie
        lang = args.lang
        current_model = args.training

        print ('   >---< language : [' + str(lang) + ']' )



        if os.path.isdir(current_dir + '/training/' + current_model) == False:
            create_folder('create',lang)
        else:
            if mode == 'delete_model':
                create_folder('delete_model',lang)
            elif mode == 'delete_checkpoints':
                create_folder('delete_checkpoints',lang)
            else:
                print('   >---< training folder for [' + str(current_model) + '] already exists')



    if mode == 'create_files':

        if trie == True:

            print('   >---< trie and lm.binary auto creation')

        wordcount = get_min_max(args.wordcount)
        wordsek = get_min_max(args.wordsek)

        lettercount = get_min_max(args.lettercount)
        lettersek = get_min_max(args.lettersek)


        duration = get_min_max(args.duration)
        bitrate = get_min_max(args.bitrate)

        size = get_min_max(args.size)
        samplerate = get_min_max(args.samplerate)
        channels = get_min_max(args.channels)

        upvotes = get_min_max(args.upvotes)
        downvotes = get_min_max(args.downvotes)




        clean_path = args.clean

    

  

        create_train_files()
    elif mode == 'insert_cv':
        if args.path == '':
            corpus_path = input("enter corpus path : ")
        else:
            corpus_path = args.path


        if os.path.isdir(corpus_path) == True:
            deepspeech_parser(corpus_path)
        else:
            print('   ¦¦!¦¦ [' + str(corpus_path) + '] not found')
            exit(1)
    elif mode == 'create_trie_lm':
            print('   ¦¦!¦¦ [' + str(corpus_path) + '] not found')


    elif mode == 'test':


        show_progress(1521462189,20,200,'testi test')
        exit(1)
  
    elif mode == 'delete_model' or mode == 'delete_checkpoints':
        print('   <>-<> deleted ' + str(mode) + ' - [' + str(current_model) + ']')
    else:
        parser.print_help()

