
import os
import sqlite3
import re
from . import tools
import num2words

error_pattern = re.compile(r'�')

test1 = re.compile(r'[d&#039;]')

test2 = re.compile(r'[d&#039;]')






def num_spacer(abc,sentences,convert):

    if convert == 0:
        sentences = re.sub( r'([' + str(abc) + '])([0-9])', r'\1 \2', sentences )            
        sentences = re.sub( r'([0-9])([' + str(abc) + '])', r'\1 \2', sentences )   
    elif convert == 1:  
        sentences = re.sub( r'([' + str(abc) + ']) ([0-9])', r'\1\2', sentences )            
        sentences = re.sub( r'([0-9]) ([' + str(abc) + '])', r'\1\2', sentences )  


    return sentences



def check_num2words(lang):
    try:
        num2words.num2words('0', lang=lang)
        return True
    except:
        return False



def clean_database(lang):


    lang[1].execute("SELECT audios_id,wav_path from audios")
    data = lang[1].fetchall()
    notfound = 0
    found = 0
    index = 0
    for lines in data:
        data_dir = str(lines[1]) 
        index += 1
        if os.path.isfile(data_dir) == False:
            lang[1].execute("delete from audios where audios_id=" + str(lines[0]) + "")
            notfound += 1
    tools.printer(2,'found',notfound)
    tools.printer(2,'not found',notfound)
    tools.printer(0,'audios left',str(index - notfound))
    lang[1].commit()  




def text_cleaner(changer,sentences,lang,uppercase,turnlower,before_num):
    allow_numbers = changer[3]
    index = 0
    for replace in changer[1]:
        if before_num == True and replace[2] < 0:
             replace_activ = True
        elif before_num == False and replace[2] >= 0:
             replace_activ = True
        else:
             replace_activ = False

        if allow_numbers == True and replace[1] == 'numerical':
             replace_activ = False

        if replace_activ == True:
            if index == turnlower and uppercase == False  and before_num == False:
                sentences = sentences.lower()
            for rep in replace[0]:
                sentences = sentences.replace(str(rep[0]), str(rep[1]))
            index += 1


   
    return sentences

def sentences_cleaner(changer,sentences,lang,uppercase,num_activ,turnlower):
    alphabet_reg = re.compile(r'[' + changer[0][0] + ']')
    upper_reg = re.compile(r'[' + changer[0][1] + ']')
    lower_reg = re.compile(r'[' + changer[0][2] + ']')
    min_reg = changer[0][3]
    allow_numbers = changer[3]
    number_reg = re.compile(r'[0-9]')




    if len(lower_reg.findall(sentences)) == 0 and uppercase == True:
        return False


    sentences =  '> ' + str(sentences).replace('\n',' ') + ' <'


    sentences = text_cleaner(changer,sentences,lang,uppercase,turnlower,True)
    if number_reg.search(sentences) and allow_numbers == False:
        
        # only if num2words supports the selected language
        if num_activ == True:
            

            sentences = num_spacer(changer[0][0],sentences,0)

            for compiles in changer[2]:
                if compiles[1] == -1:
                    if compiles[0].search(sentences):
                        return False
                else:
                    match = compiles[0].search(sentences)
                    while match is not None:
                        if compiles[1] == 0:
                            try:
                                num_word = num2words.num2words(int(match.group().replace(',', '.').replace('.', '').replace(' ', '')), lang=lang)
                            except:
                                return False
                        elif compiles[1] == 1:
                            try:
                                num_word = num2words.num2words(float(match.group().replace(',', '.')), lang=lang)
                            except:
                                return False
                        before = sentences[:match.start()]
                        after = sentences[match.end():]
                        sentences = ' '.join([before, num_word, after])
                        match = compiles[0].search(sentences)


        
        else:

            return False


    sentences = text_cleaner(changer,sentences,lang,uppercase,turnlower,False)



    if error_pattern.search(sentences):
        return False




        
    sentences = sentences.replace('<','').replace('>','').replace('	',' ').replace(',',' ').replace('.',' ').replace('\'',' ').replace('\n','').replace('u\'\xad\'',' ').replace('    ',' ').replace('   ',' ').replace('   ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').strip()

    test_sentences = sentences.replace(' ','')
    test_equal = len(alphabet_reg.findall(test_sentences))
    test_sentences = len(test_sentences)


    if test_equal != test_sentences:
        return False

    if min_reg != '':
        if min_reg.search(str(sentences).lower()):
            return False


    return sentences.strip()





def get_db(lang):
    if os.path.isdir('languages/' + str(lang[0])) == False: 
        folder = os.path.join('languages/', str(lang[0]) + '/' + 'sql_query')
        os.makedirs(folder, exist_ok=True)
        folder = os.path.join('languages/', str(lang[0]) + '/' + 'replacer')
        os.makedirs(folder, exist_ok=True)
        tables = [['age',[]],['dataset',[]],['dialect',[]],['gender',[]],['speaker',[]],['text',['�!','BAD_!','_BAD!','_NOISE_!','_INHALE_!']],['wav_path',['_Kinect-BEAM!','_Samson!','_Realtek!']]]
        for m in tables:
            if len(m[1]) > 0:
                sql_querys = m[1]
            else:
                sql_querys = ''
            tools.create_file(sql_querys,"languages/" + str(lang[0]) + "/sql_query/" + m[0])
            
  
      
    return create_db(lang) 




def get_replacer(lang_short,minletters=0):
    replacer = []
    replacer_file = []
    replacer_path = "languages/" + str(lang_short) + "/replacer"


    if lang_short in ['en']:
        bigint = ['[0-9]+[,][0-9][0-9][0-9][,]',0]
    else:
        bigint = ['[0-9]+[.\ ][0-9][0-9][0-9]',0]

    if lang_short in ['en']:
        floatreg = ['[0-9]+[.][0-9]+',1]
    else:
        floatreg = ['[0-9]+[,][0-9]+',1]


    for root, dirs, files in os.walk(replacer_path):
        for file in files:
            
            numrow = re.sub("[a-zA-Z]+", "", file).replace('_','')
            types = re.sub("[0-9]+", "", file).replace('_','').replace('-','')
            path = os.path.join(root, file)

            try:
                if numrow != '':
                    numrow = int(numrow)
                    replacer_file.append([numrow,types,path])


            except:
                pass

 

    for replace in replacer_file:              
        raw_replace = tools.get_file(replace[2],True,False)
        replacer_temp = []
        for rep in raw_replace:  
            splits = rep.split('>') 
            if len(splits) == 2:
                if splits[0] != '.' and splits[0] != ','  and splits[0] != '<'  and splits[0] != '>' :
                    replacer_temp.append([splits[0],splits[1].replace('\n','')])
           

        if len(replacer_temp) > 1: 
            replacer.append([replacer_temp,replace[1],replace[0]])  


    num_regex = [[' [0][0]+[0-9]+',-1],['[0-9][0-9][0-9][0-9][0-9]+',-1],[' [0-9][0-9][0-9][0-9] ',0],bigint,floatreg,['[0-9]+',0]]
    compiled = []
    for regex in num_regex:
        compiled.append([re.compile(r'' + str(regex[0]) + ''),regex[1]])

       


        
    return [replacer,compiled]









def create_db(lang): 

    db_miss = False
    if os.path.isfile("languages/" + str(lang[0]) + "/audio.db") == True:
        connection = sqlite3.connect("languages/" + str(lang[0]) + "/audio.db")    
        cursor = connection.cursor()
    else:
        db_miss = True




    if db_miss == True:
        connection = sqlite3.connect("languages/" + str(lang[0]) + "/audio.db")    
        cursor = connection.cursor()
        sql_command = """CREATE TABLE "audios" (
    	    `audios_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    	    `size`	INTEGER,
    	    `duration`	INTEGER,
    	    `samples`	INTEGER,
    	    `wordcount`	INTEGER,
    	    `upvotes`	INTEGER,
    	    `downvotes`	INTEGER,
    	    `sectors`	TEXT,
    	    `distance`	TEXT,
    	    `wav_path`	TEXT,
    	    `gender`	TEXT,
    	    `age`	TEXT,
    	    `speaker`	TEXT,
    	    `text`	TEXT,
    	    `samplerate`	TEXT,
    	    `bitrate`	INTEGER,
    	    `channels`	INTEGER,
    	    `codec`	TEXT,
    	    `wordsec`	INTEGER,
    	    `dialect`	TEXT,
    	    `dataset`	TEXT,
    	    `errors`	INTEGER,
    	    `lettercount`	INTEGER,
    	    `lettersec`	INTEGER,
    	    `md5sum`	TEXT UNIQUE
        )"""  
        cursor.execute(sql_command)


        sql_command = """CREATE TABLE "configs" (
    	    `configs_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    	    `name`	TEXT,
    	    `earlystop_nsteps`	INTEGER DEFAULT 5,
    	    `train_batch_size`	INTEGER DEFAULT 24,
    	    `dev_batch_size`	INTEGER DEFAULT 48,
    	    `test_batch_size`	INTEGER DEFAULT 48,
    	    `n_hidden`	INTEGER DEFAULT 2048,
    	    `learning_rate`	INTEGER DEFAULT 0.0001,
    	    `dropout_rate`	INTEGER DEFAULT 0.2,
    	    `display_step`	INTEGER DEFAULT 0,
    	    `epoch`	INTEGER DEFAULT 50,
    	    `validation_step`	INTEGER DEFAULT 1,
    	    `decoder_library_path`	TEXT DEFAULT `native_client/libctc_decoder_with_kenlm.so`,
    	    `batch_size`	INTEGER DEFAULT 32,
    	    `n_steps`	INTEGER DEFAULT 16,
    	    `summary_secs`	INTEGER DEFAULT 600,
    	    `dropout_rate2`	INTEGER DEFAULT -1.0,
    	    `dropout_rate3`	INTEGER DEFAULT -1.0,
    	    `dropout_rate4`	INTEGER DEFAULT 0,
    	    `dropout_rate5`	INTEGER DEFAULT 0,
    	    `dropout_rate6`	INTEGER DEFAULT -1.0,
    	    `relu_clip`	INTEGER DEFAULT 20,
    	    `early_stop`	TEXT DEFAULT `True`,
    	    `estop_mean_thresh`	INTEGER DEFAULT 0.5,
    	    `estop_std_thresh`	INTEGER DEFAULT 0.5,
    	    `beam_width`	INTEGER DEFAULT 1024,
    	    `lm_weight`	INTEGER DEFAULT 1.5,
    	    `beta1`	INTEGER DEFAULT 0.9,
    	    `beta2`	INTEGER DEFAULT 0.999,
    	    `epsilon`	INTEGER DEFAULT 1e-8,
    	    `valid_word_count_weight`	INTEGER DEFAULT 2.25,
    	    `limit_train`	INTEGER DEFAULT 0,
    	    `limit_dev`	INTEGER DEFAULT 0,
    	    `limit_test`	INTEGER DEFAULT 0,
    	    `export_batch_size`	INTEGER DEFAULT 1,
    	    `use_seq_length`	TEXT DEFAULT `True`,
    	    `log_level`	INTEGER DEFAULT 1,
    	    `max_to_keep`	INTEGER DEFAULT 5,
    	    `export_version`	INTEGER DEFAULT 1,
    	    `export_tflite`	TEXT DEFAULT `False`,
    	    `wer_log_pattern`	TEXT DEFAULT ``,
    	    `random_seed`	INTEGER DEFAULT 4567
        )"""  
        cursor.execute(sql_command)
        connection.commit()
        cursor.execute("insert into configs(name,earlystop_nsteps,train_batch_size,dev_batch_size,test_batch_size,n_hidden,learning_rate,dropout_rate,display_step,validation_step) values('default',5,24,48,48,2048,0.0001,0.2,0,1)")
        connection.commit()
        lang[3].execute("select letters_upper,letters_lower from languages where short='" + str(lang[0]) + "'"  )
        data = lang[3].fetchall()
        tools.create_file(data[0],"languages/" + str(lang[0]) + "/alphabet_raw.txt")
        get_letters(lang[0])



        tables = ['correct','abbreviation','day','month','numerical','currency','metrics','error']


        lang[3].execute("select correct,abbreviation,day,month,numerical,currency,metrics,error from languages where short='" + str(lang[0]) + "'"  )

        data = lang[3].fetchall()
        index = 0
        select = 1
        for table in tables:
            dataraw = data[0][index]
            index += 1
            if dataraw == '' or table == 'currency' or table == 'numerical':
                savename = "languages/" + str(lang[0]) + "/replacer/" + str(table)  + ""
            else:
                if table == 'correct':
                    savename = "languages/" + str(lang[0]) + "/replacer/" + "-1_" + str(table)  + ""
                else:
                    savename = "languages/" + str(lang[0]) + "/replacer/" + str(select) + "_"  + str(table)  + ""
                    select += 1

            tools.create_file(dataraw.split('\n'),savename)

  

        lang[3].execute("select space from spaces"  )
        data = lang[3].fetchall()
        index = 0
        arr = []
        for l in data:
            arr.append(str(l[0]) + '> ' + str(' '))   
        index += 1
        tools.create_file(arr,"languages/" + str(lang[0]) + "/replacer/" + str(select) + "_spaces")


        tools.printer(2,'DB created for',lang[0])
        tools.printer(0,'',lang[2])
    return [connection,cursor]




def get_default_lang(lang='',return_db=False):
    connection = sqlite3.connect("config.db")
    cursor = connection.cursor()
    if lang == '' or lang == 'default':
        cursor.execute("select languages_id,short,language from languages where selected=1" )
        data = cursor.fetchall()

        if len(data) == 1:
            lang = data[0][1]
            lang_id = data[0][0]
        else:
            connection.close() 
            tools.printer(9,'no default language')
            exit(1)

    else:
        cursor.execute("select languages_id,short,language from languages where short='" + str(lang) + "'" )
        data = cursor.fetchall()
        if len(data) == 1:
            lang = data[0][1]
            lang_id = data[0][0]
            cursor.execute("update languages set selected=0")
            cursor.execute("update languages set selected=1 where short='" + str(lang) + "'")
            connection.commit() 
        else:
            tools.printer(9,'selected language isn\'t supported',lang)
            connection.close() 
            exit(1)


    if return_db == True:
        return [lang,lang_id,data[0][2],cursor,connection]
    elif return_db == False:
        connection.close() 
        return [lang,lang_id,data[0][2]]



def get_letters(lang_short,upper=False,show=False,minletters=0,allow_numbers=False):



    alphabet = []
    alphabet.append('#start')
    alphabet.append(' ')


    letters = tools.get_file("languages/" + str(lang_short) + "/alphabet_raw.txt",False)
    letters = letters.split('\n')
    letters_upper = letters[0]
    letters_lower = letters[1]


    if upper == False:
        letters = letters_lower
    else:
        letters = letters_lower + letters_upper


    if allow_numbers == True:
        letters += '0123456789'

    for let in letters:
        alphabet.append(let)

    if show == False:
        alphabet.append('#end')
        alphabet.append('\n')
        f = open('languages/' + str(lang_short) + "/alphabet.txt", "w")
        f.write("\n".join(alphabet))
        f.close()
    if show == True:
        tools.printer(1,'used alphabet',tools.get_file("languages/" + str(lang_short) + "/alphabet_raw.txt",False))
 
    upper_regex = ''
    for abc in letters_upper:
        upper_regex += abc + '|'
    upper_regex = str(upper_regex + ']').replace('|]','').replace(']','')


    lower_regex = ''
    for abc in letters_lower:
        lower_regex += abc + '|'
    lower_regex = str(lower_regex + ']').replace('|]','').replace(']','')



    abc_regex = ''
    for abc in letters:
        abc_regex += abc + '|'
    abc_regex = str(abc_regex + ']').replace('|]','').replace(']','')




    max_reg = ''
    for m in range(minletters):
        if m > 0:
            max_reg += '|'
        maxletter_reg = ''
        for s in range(m+1):
           maxletter_reg += '[' + lower_regex + ']'
        max_reg += ' ' + maxletter_reg + ' '

    if max_reg != '':
        if minletters == 1:
            max_reg = re.compile(r'' + max_reg + '')
        else:
            max_reg = re.compile(r'[' + max_reg + ']')


    return [abc_regex,upper_regex,lower_regex,max_reg]


