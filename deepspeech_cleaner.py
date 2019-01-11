#! /usr/bin/env python

"""
Version: 1.0.0 (Jan 10, 2019)
Author: Harold Andreas Zellner - hoopiger@googlemail.com

"""

import os
import sqlite3
import argparse
import random
import numpy as np
import re
from multiprocessing import Pool , cpu_count
from toolbox import tools, downloader, crawler , alphabet, transformer




def create_query():
    # search for query files
    files = tools.search_path(str(language_path) + 'sql_query')
    all_query = []
    query_not = []
    for found in files:
        table = str(str(found).split('/')[-1]).replace('.txt','')
        # read file only if tablename exist
        if table in sql_tables:
            querys = tools.get_file(found,True)
            if len(querys) > 0:
                # discard all unusefull stuff
                for query in querys:
                    if query != '' and query != ' ':
                        ind = 0
                        q_set = ''
                        # find and discard ! 
                        for q in query:
                            ind += 1
                            if len(query) == ind and q == '!':
                                query_not.append([q_set,table])
                                break
                            else:
                                q_set += q
                            if len(query) == ind:   
                                all_query.append([q_set,table])

    sql = ''
    # get min max values from arguments or defaults
    for m in sql_minmax:
        minvalue = m[1][0]
        maxvalue = m[1][1]
        if minvalue == 0.0 and maxvalue == 0.0:
            pass
        else:
            if str(m[0]) == 'samplerate':
                minus = '-1'
            else:
                minus = ''
            if sql == '':
                sql += '(' + str(m[0]) + '>=' + str(minvalue) + str(minus) + ' and ' + str(m[0]) + '<='  + str(maxvalue)
            else:
                sql += ' and ' + str(m[0]) + '>=' + str(minvalue)  + str(minus) + ' and ' + str(m[0]) + '<='  + str(maxvalue)
    if sql == '':
        sql += '(errors=0'
    else:
        sql += ' and errors=0'
    for x in range(2):
        if x == 0:
            like = 'not like'
            operator = 'and'
            query_temp = query_not
        elif x == 1:
            like = 'like'
            operator = 'or'
            query_temp = all_query

        sql_temp = ''


        if len(query_temp) > 0 :
            for query in query_temp:
                if sql_temp == '' and sql != '' and x == 0:
                    sql_temp += ' and ' + str(query[1]) + ' ' + str(like) + ' \'%' + str(query[0]) + '%\''
                elif sql_temp == '' and sql != '' and x == 1:
                    sql_temp += ' and (' + str(query[1]) + ' ' + str(like) + ' \'%' + str(query[0]) + '%\''
                else:
                    sql_temp += ' ' + str(operator) + ' ' + str(query[1]) + ' ' + str(like) + ' \'%' + str(query[0]) + '%\''
          
        if x == 1 and sql_temp == '':
            pass
        else:
            sql += sql_temp + ')'
       

    return sql


        




def create_train_files():
    tools.printer(22,'wordlength',args.wordlength,True,model_path + 'info/training.txt')
    tools.printer(22,'numbers',args.numbers,True,model_path + 'info/training.txt')
    tools.printer(22,'upper',args.upper,True,model_path + 'info/training.txt')
    tools.printer(22,'lower',args.lower,True,model_path + 'info/training.txt')
    tools.printer(-3)
    # get sentences from db and clean them
    newlines = clean_sentences([1],True,True)
    tri_sentences = newlines[1]
    dropped = newlines[2]
    newlines = newlines[0]
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


    tools.printer(2,'all files', str(len(newlines)),True,model_path + 'info/training.txt')
    tools.printer(2,'train files', str(len(train_files)),True,model_path + 'info/training.txt')
    tools.printer(2,'test files', str(len(test_files)),True,model_path + 'info/training.txt')
    tools.printer(2,'dev files', str(len(dev_files)),True,model_path + 'info/training.txt')
    # add all sentences 
    tools.create_file(tri_sentences,model_path + "clean")
    tools.create_file(tri_sentences,model_path + "info/cleaned_sentences")
    tools.create_file(dropped,model_path + "info/dropped_sentences")
    tools.create_file(newlines,model_path + "all.csv")
    tools.create_file(dev_files,model_path + "dev.csv")
    tools.create_file(train_files,model_path + "train.csv")
    tools.create_file(test_files,model_path + "test.csv")




    if args.notrie == False:
        if create_trie() == False:
            tools.printer(9,'couldn\'t create lm.binary and trie', language_data[0])
            tools.printer(8,'use -nt to skip lm.binary /trie creation', language_data[0])
            return False




    # array with arguments for start_train.sh
    raw_conf = "earlystop_nsteps,train_batch_size,dev_batch_size,test_batch_size,n_hidden,learning_rate,dropout_rate,display_step,epoch,validation_step,decoder_library_path,batch_size,n_steps,summary_secs,dropout_rate2,dropout_rate3,dropout_rate4,dropout_rate5,dropout_rate6,relu_clip,early_stop,estop_mean_thresh,estop_std_thresh,beam_width,lm_weight,beta1,beta2,epsilon,valid_word_count_weight,limit_train,limit_dev,limit_test,export_batch_size,use_seq_length,log_level,max_to_keep "
    splits = raw_conf.split(',')

    # get argument values from db
    main_db[1].execute("select " + str(raw_conf) + " from configs where name='" + str('default') + "'")
    index = 0
    raw_conf = main_db[1].fetchall()
    config = []

    
    # set right pathes
    varis = '\n\n\nlm_trie_path="' + model_path + 'trie" \nlm_binary_path="' + model_path + 'lm.binary" \ncheckpoint_dir="' + model_path + 'checkpoints" \nexport_dir="' + model_path + 'model_export"\nalphabet="' + model_path + 'alphabet.txt' + '"\ntest="' + model_path + 'test.csv' + '"\ndev="' + model_path + 'dev.csv' + '"\ntrain="' + model_path + 'train.csv' + '"'


    cmd = '\n\n\ncd "' + str(deepspeech_dir[0]) + '"\n\npython3 DeepSpeech.py --lm_trie_path "$lm_trie_path" --lm_binary_path "$lm_binary_path" --checkpoint_dir "$checkpoint_dir" --export_dir "$export_dir" --alphabet_config_path "$alphabet" --train_files "$train" --dev_files "$dev" --test_files "$test"'

    # determine value types and add them
    for conf in raw_conf[0]:
        value = str(conf).strip()

        conf = str(splits[index]).strip()
        config.append([conf,value])
        if re.compile(r'[a-zA-Z]+').search(value):
          
            if value == 'True' or value == 'False' or re.compile(r'1e-').search(value):
                varis += '\n' + conf + '=' + value + ''
                cmd += ' --' + conf + ' $' + conf + ''
            else:
                varis += '\n' + conf + '="' + value + '"'
                cmd += ' --' + conf + ' "$' + conf + '"'
        else:
            varis += '\n' + conf + '=' + value + ''
            cmd += ' --' + conf + ' $' + conf + ''
        index += 1

    varis += cmd
    tools.printer(-4,varis,'',True,model_path + 'start_train.sh',True,False)


    tools.printer(-3)
    if args.notrie == True:
        tools.printer(8,'path for your own trie/lm.binary',model_path)
        tools.printer(0,'otherwise trainings script wont work\n')
    tools.printer(2,'start training with')
    tools.printer(-1,'          ↓        ')
    tools.printer(-1,'bash "' + model_path + 'start_train.sh"')


    return True



def create_trie():
    clean = checking_clean_corpora()
    if clean == False:
        return False



    raw_sentences = []
    clean_path = language_path + 'clean_raw'
    clean_model = model_path + "clean"
    file_cleaner(clean_path,clean_model)
    crawler.sort_remove_duplicates(clean_model)
    tools.printer(0,'\n   -----------------------------------------\n   creating trie and lm.binary\n\n\n','')
    os.system('bash toolbox/make_trie.sh "' + str(deepspeech_dir[0]) + '" "' + str(model_path) + '" ' + str('3'))
    if os.path.isfile(model_path + 'trie') == False:
        return False
    else:
        return True



def clean_sentences(all_sentences,deep_create=False,analyze=False):

    # get overall statistics
    if analyze == True:
        sizes = []  
        durations = []  
        wordcounts = []  
        words_sec = []  
        letters = []  
        letters_sec = []  

    if all_sentences[0] == 0: # 0 - array of sentences
        set_sentences = all_sentences[1]
    elif all_sentences[0] == 1: # 1 - sql query 
        query = create_query()
        main_db[1].execute("SELECT dataset,wav_path,size,text,duration,wordcount,lettercount,lettersec,wordsec from audios where " + str(query) + "")
        data = main_db[1].fetchall()
        set_sentences = data

    counter = len(set_sentences)
  

    index = 0
    failer = 0
    success = 0
    cleaned = ''
    cleaned_sentences = []
    cleaned_raw = []
    dropped = []
    datasets = []
    show_index = round(counter/20)
    for set_s in set_sentences:  

        if index % show_index == 0:
            tools.printer(0,'[' + str(round((index/counter)*100,2)) + '%]',str(index) + '/' + str(counter))
        if deep_create == True:
            text = set_s[3] 
            data_dir = str(set_s[1])
            if os.path.isfile(data_dir) == False:
                cleaned = False

        else:
            text = set_s  



        if args.noclean == False:
            cleaned = alphabet.sentences_cleaner(prepare,str(text),language_data[0],args.upper,num_activ,args.lower)
        else:
            cleaned = str(text).replace('\n',' ')
            if args.upper == False:
                cleaned = cleaned.lower()

        if cleaned == False: 
            failer += 1
            dropped.append(str(text))
        else:
            success += 1  
            if analyze == True:
                if set_s[0] in datasets:
                    pass
                else:
                    datasets.append(set_s[0])
                sizes.append(set_s[2])  
                durations.append(set_s[4])  
                wordcounts.append(set_s[5])   
                letters.append(set_s[6])   
                letters_sec.append(set_s[7])                                                                                                                                 
                words_sec.append(set_s[8])                                                                                                                                 

            if deep_create == True:
                cleaned_sentences.append(data_dir + ',' + str(set_s[2]) + ',' + cleaned)
                cleaned_raw.append(str(cleaned))
            else:
                cleaned_sentences.append(str(cleaned)) 




        index += 1

    print()

    # exit if no sentences
    if deep_create == True and len(cleaned_sentences) == 0:
        tools.printer(9,'no sentences found or all failed','')
        tools.printer(88,'try other parameters','')
        tools.printer(99,'python3 deepspeech_cleaner.py --help" for help','')
        close_db(2,True)


    if analyze == True:
        tools.printer(11,'info:','',True,model_path + 'info/training.txt')
        tools.printer(2,'corpora','-'.join(datasets),True,model_path + 'info/training.txt')      
        tools.get_size(sizes,'size',model_path + "info/training.txt")
        all_duration = tools.get_size(durations,'duration',model_path + "info/training.txt")
        all_words = tools.get_size(wordcounts,'words',model_path + "info/training.txt")
        all_letters = tools.get_size(letters,'letters',model_path + "info/training.txt")
        tools.printer(2,'words per sec',round(all_words/all_duration,2),True,model_path + 'info/training.txt')
        tools.printer(2,'letters per sec',round(all_letters/all_duration,2),True,model_path + 'info/training.txt')

    return [cleaned_sentences,cleaned_raw,dropped]








def multi_cleaner(inputs):
    if args.max < 1:
        args.max = 1

    index = 0
    startrange = inputs[0]
    endrange = inputs[1]

    failer = 0
    success = 0
    counter = endrange-startrange
    all_sentences = []
    show_index = 100000
    if inputs[4] == 0:
        show_index = round(counter/200)


    with open(inputs[2], 'r') as f:
        for text in f:
            if index >= startrange and index <= endrange:

                if args.noclean == False:
                    cleaned = alphabet.sentences_cleaner(prepare,str(text),language_data[0],args.upper,num_activ,args.lower)
                else:
                    cleaned = str(text)
                    if args.upper == False:
                        cleaned = cleaned.lower()




                if cleaned == False: 
                    failer += 1

                else:
                    success += 1  
                    all_sentences.append(str(cleaned))
                if index % show_index == 0 and inputs[4] == 0:

                    tools.printer(0,'[' + str(round((index/counter)*100,2)) + '%]',)




                if len(all_sentences) > args.max:
                    tools.create_file(all_sentences,inputs[3],'a')
                    all_sentences = []



    
            index += 1
    
    f.close

    if len(all_sentences) > 0:
        tools.create_file(all_sentences,inputs[3],'a')

    

    





def file_cleaner(path,targetpath):
    counter = 0
    all_process = []

    with open(path, 'r') as f:
        for text in f:
            counter += 1

    cpus = get_process_count()

   
    steps = round(counter/cpus)
    start = 0
    end = 0
    current = 0
    for p in range(cpus):

        start = current
        current += steps

        if p+1 == cpus:
            end = counter
        else: 
            end = current
        

 
        all_process.append([start,end,path,targetpath,p])


    tools.printer(2,'cleaning',path)
    tools.printer(2,'        ',targetpath)
    tools.printer(2,'processing',cpus)
    with Pool(cpus) as p:
        return p.map(multi_cleaner, all_process)








        


def model_check():
    new_path = model_path
    new_model = current_model
    tools.printer(11,'training',new_model)
    if os.path.isdir(new_path) == True:
        tools.printer(8,'already trainings file for',new_model)
        u_input = tools.get_inputs([['d','delete and recreate',0],['c','choose another trainings name',0]],'',True,True)
        if u_input == 'd':
            tools.delete_all(new_path)
        elif u_input == 'c':
            while True:
                new_model = input("         new name for training\n\n--:")
                new_path = current_dir + '/languages/' + str(language_data[0]) + '/training/' + new_model + '/'
                if os.path.isdir(new_path) == False:
                    break
                elif new_model in ['q','Q']:
                    return [False]
                print()
                tools.printer(8,'already trainings file for',new_model)
        elif new_model in ['q','Q']:
            return [False]
        else:
            return [False]


    tools.create_folder(current_dir,new_model,'create',language_data[0])

    tools.printer(-3,'','',True,new_path + 'info/training.txt',True,False)
    return [True,new_model,new_path]



    


def create_clean_corpora(append=False):

    tools.printer(99,'need to download clean corpora')
    corporas = downloader.check_corpora(language_data,'[\'0\']',1)
    if len(corporas) == 0:
        tools.printer(8,'no clean corpora',str(language_data[0]))
        tools.printer(0,'trying to crawl one')
        tools.printer(-3)
        crawler.crawl_corpora(args.process,language_data[0],language_path,10,append)
       

    else:
        tools.printer(2,'downloading clean corpora','')
        downloader.download_clean(corporas[0][0],language_path)
    return True


def checking_clean_corpora():

    if os.path.isfile(language_path + 'clean_raw') == False:
        create_clean_corpora()
    else:

        clean_size = round(os.path.getsize(language_path + 'clean_raw')/1000000000,3)
        tools.printer(2,'found clean corpora')
        tools.printer(0,'size',str(clean_size) + 'GB')
        return True




def get_prepare():
    # array of replacer
    replacer = alphabet.get_replacer(language_data[0])
    # selected alphabet - upper/lower for regex
    if args.wordlength < 0:
        args.wordlength = 0

    alpha = alphabet.get_letters(language_data[0],args.upper,False,args.wordlength,args.numbers)
    return [alpha,replacer[0],replacer[1],args.numbers]



def get_process_count():
    cpus = args.process
    real_cpus = max(1, cpu_count() - 1)
    if cpus == 0 or cpus > real_cpus:
        cpus = real_cpus
    return cpus

def close_db(which=0,leave=False):
    if which == 0 or which == 1:
        language_data[4].close()
    if which == 0 or which == 2:
        main_db[0].close()

    if leave == True:
        tools.printer(-3)
        exit(1)



def error_flag():
    if sec_input == '':
        tools.printer(8,'no audio path')
        array = [tools.get_inputs([['wav_path','audio path from db',1],['audios_id','audio id from db',5]],'',True,True)]
    else:
        array = [sec_input]
    try:
        sql_test = "select audios_id from audios where audios_id=" + str(int(array[0])) + ""
        sql = "update audios set errors=9 where wav_path=" + str(int(array[0])) + ""
    except:


        sql_test = "select audios_id from audios where wav_path='" + str(array[0]) + "'"
        sql = "update audios set errors=9 where wav_path='" + str(array[0]) + "'"

    if str(array[0]) == 'unflag':
        tools.printer(22,'all errors are unflagged',array[0])
        main_db[1].execute('update audios set errors=0')
        main_db[0].commit()
    else:
        main_db[1].execute(sql_test)
        test = main_db[1].fetchall()
        if len(test) > 0:
            tools.printer(22,'error flagged',array[0])
            main_db[1].execute(sql)
            main_db[0].commit()
        else:
            tools.printer(9,'not found',array[0])

def test_sentences():
    if sec_input == '':
        tools.printer(8,'no test input')
        array = [tools.get_inputs([['','sentences or path',-1]],'',True,True)]

    if os.path.isfile(sec_input) == True:
        array = tools.get_file(sec_input,True)
    elif sec_input != '':
        array = [sec_input] 

    print()
    for arr in array:
        cleaned = alphabet.sentences_cleaner(prepare,str(arr),language_data[0],args.upper,num_activ,args.lower)
        if cleaned == False: 
            tools.printer(8,arr + '\n')
        else:
            tools.printer(2, arr)
            tools.printer(22,cleaned + '\n')


def start_download():
        corporas = tools.get_min_max(str(args.corpora),1)
        tools.printer(-3)
        tools.printer(1,'Downloader\n')
        corporas = downloader.check_corpora(language_data,corporas,0)
        downloader.download(current_dir,language_path + 'datasets/' ,main_db,language_data[0],corporas)





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DeepSpeech Dataset Downloader/Combiner/Cleaner')
    parser.add_argument('mode',help="""
    download     - [download corpora if available]------------
    crawl        - [download/clean wiki dumps for lm.binary/trie]
    create       - [create training files]----------------------
    insert       - [insert corpus in db]------------------------
    convert      - [convert audio files from database]---------
    trimm        - [trimm all audio files start/end]-------------
    trimmsilence - [vad only start/end]-------------------
    clean_db     - [delete all missing files in db]-----------
    save         - [autosave arguments for each language on/off]--
    test         - [test single sentence or file]-----------------
    error        - [error flag audio files with path/id]---------""",nargs='+',type=str)

    parser.add_argument('-t','--training',help=" path to model files [%(default)s]", default='standard', type=str)
    parser.add_argument('-c','--corpora',help="which corpora - 0=all [0]", default='default', type=str)
    parser.add_argument('-u','--upper',help="use upper and lowercase [False]", default=False, type=bool)
    parser.add_argument('-n','--numbers',help="allow numbers [False]", default=False, type=bool)
    parser.add_argument('-lo','--lower',help="replacer round to turn sentence to lowercase - only if -u/--upper=False [0]", default=0, type=int)
    parser.add_argument('-l','--lang',help="available [it|hu|hr|pt|sv|fi|el|da|nn|lv|lt|bg|bs|sl|sk|is|en|uk|de|tr|ru|ro|es|fr|nl|pl|sq|cs|sr|et]", default='default', type=str)
    parser.add_argument('-nc','--noclean',help="don't clean sentences", default=False, type=bool)
    parser.add_argument('-nt','--notrie',help="no trie/lm.binary creation [False]", default=False, type=bool)
    parser.add_argument('-s','--size',help="select min-max file size - 0=off [500-100000]", default='default', type=str)
    parser.add_argument('-d','--duration',help="select min-max duration in sec - 0=off [1.5-9.9]", default='default', type=str)
    parser.add_argument('-wc','--wordcount',help="select min-max words - 0=off [10-22]", default='default', type=str)
    parser.add_argument('-ws','--wordsec',help="select min-max words per sec - 0=off [0.5-1.7]", default='default', type=str)
    parser.add_argument('-wl','--wordlength',help="select minimum letters for a word - 0=off [0]", default=0, type=int)
    parser.add_argument('-lc','--lettercount',help="select min-max letters - 0=off [10-22]", default='default', type=str)
    parser.add_argument('-ls','--lettersec',help="select min-max letters per sec - 0=off [1.1-10.2]", default='default', type=str)
    parser.add_argument('-b','--bitrate',help="select min-max bitrate - 0=off [8-16]", default='default', type=str)
    parser.add_argument('-sa','--samplerate',help="select min-max samplerate - 0=off [16000-22000]", default='default', type=str)
    parser.add_argument('-se','--sectors',help="select min-max sectors - 0=off [221-505]", default='default', type=str)
    parser.add_argument('-ch','--channels',help="select min-max channels - 0=off [1-2]", default='default', type=str)
    parser.add_argument('-uv','--upvotes',help="select min-max upvotes - 0=off [0-3]", default='default', type=str)
    parser.add_argument('-dv','--downvotes',help="select min-max downvotes - 0=off [0-3]", default='default', type=str)
    parser.add_argument('-cs','--convert_settings',help="change audio output settings [\"wav 16000 1 16 signed-integer\"]", default='wav 16000 1 16 signed-integer', type=str)
    parser.add_argument('-ts','--trimm_settings',help="change audio trimm settings [\"0.5 0.5\"]", default='default', type=str)
    parser.add_argument('-ps','--process',help="how many processes should be used - 0=one per cpu [0]", default=0, type=int)
    parser.add_argument('-m','--max',help="max sentences in ram before writing to file [1000]", default=1000, type=int)


    args = parser.parse_args()

    if len(args.mode) == 0:
        mode = 'help'
    else:
        mode = args.mode[0]

    if len(args.mode) == 1:
        sec_input = ''
    elif len(args.mode) > 1:
        sec_input = ' '.join(args.mode[1:])



    print(sec_input)


    if mode == 'help':
        pass
    else:
        current_dir = tools.check_dir()
        language_data = alphabet.get_default_lang(args.lang,True)
        main_db = alphabet.get_db(language_data)
        deepspeech_dir = tools.check_deepspeech(language_data)
        if deepspeech_dir[0] == False:
            mode = '_'
        else:
        
            tools.printer(-3,'','')
            tools.printer(1,'Language',language_data[2])
            tools.printer(0,'',language_data[0])
            language_path = current_dir + '/languages/' + str(language_data[0]) + '/'
            # check if num2words got language support
            num_activ = alphabet.check_num2words(language_data[0])
            prepare = get_prepare()


    if mode == 'create':

        tools.printer(-3)
        tools.printer(1,'Creator\n')
        sql_minmax  = [['size',[]],['duration',[]],['bitrate',[]],['samplerate',[]],['channels',[]],['wordcount',[]],['wordsec',[]],['lettercount',[]],['lettersec',[]],['upvotes',[]],['downvotes',[]],['sectors',[]]]
        sql_tables = ['age','dataset','dialect','gender','speaker','text','wav_path']

        current_model = args.training
        model_path = current_dir + '/languages/' + str(language_data[0]) + '/training/' + current_model + '/'

        current_model = model_check()
        if current_model[0] == False:
            close_db(0,True)
        else:
            model_path = current_model[2]
            current_model = current_model[1]

        tools.printer(11,'options:','',True,model_path + 'info/training.txt')
        for x in range(len(sql_minmax)):
            sql_minmax[x][1] = tools.get_min_max(eval('args.' + str(sql_minmax[x][0]) + ''),0,sql_minmax[x][0],language_data[3],model_path + 'info/training.txt',deepspeech_dir[1])


        language_data[4].commit()

        


        create_train_files()


    elif mode == 'error':
        error_flag()


    elif mode == 'insert':
        tools.printer(-3)
        tools.printer(1,'Inserter\n')

        if sec_input == '':
            tools.printer(8,'no path selected','')
            corpus_path = tools.get_inputs([['','',2]],'enter corpus path',True,True)
        else:
            corpus_path = sec_input

        if corpus_path != False:
            tools.printer(2,'found path',str(corpus_path))
            downloader.insert_corpora(corpus_path,True,main_db,language_data[0])
        else:
            tools.printer(9,'path not found',str(corpus_path))





    elif mode == 'test' or mode == 'testing' :

  
        tools.printer(-3)
        tools.printer(1,'Replacement Tester\n')
        test_sentences()

       
    elif mode == 'crawl':
        tools.printer(-3)
        tools.printer(1,'Crawler\n')
        crawler.crawl_corpora(get_process_count(),language_data[0],language_path,20,False)
        tools.printer(1,'crawling complete')

    elif mode == 'convert' or mode == 'trimm' or mode == 'trimmsilence':
        tools.printer(-3)
        tools.printer(1,'Audio Transformer\n')

        transformer.convert_all(mode,get_process_count(),main_db,args.convert_settings,args.trimm_settings)

        tools.printer(2,mode,'done')

    elif mode == 'download':
        start_download()
    elif mode == 'clean_db':
        alphabet.clean_database(main_db)


    elif mode == 'save':
        tools.autosave_toggle(language_data)


    elif mode == '_':
        tools.printer(11,'quit')
        pass
    else:


        parser.print_help()
        exit(1)



    close_db(0,True)


