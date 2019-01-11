
import os
import re
import requests
import wget
from . import tools , transformer , inserter
from multiprocessing import Pool , cpu_count



def accent_parser(path,db,procs=0):
    trans = tools.search_path(path,'.txt',2)
    wavs = tools.search_path(path,'.wav',2)
    all_wavs = []
    for w in wavs:
        w = str(w).replace('.wav','').replace('.tdf','')
        all_wavs.append([str(w).split('/')[-1],w])

    all_files = []
    for tr in trans:
        files = tools.get_file(tr,True)
        for f in files:
            f = str(f).replace('.wav','').replace('.tdf','')
            splits = str(f).split(' ')[0]
            splittet = str(splits).split('/')[-1]
            all_files.append([splittet,str(f).replace(str(splits) + ' ','')])
    all_wavs = sorted(all_wavs)
    all_files = sorted(all_files)
    checked = []
    while len(all_wavs) > 0 and  len(all_files) > 0:
        count = 0
        for f in all_files:
            if all_wavs[0][0] == f[0]:
                del all_files[count]
                if os.path.isfile(str(all_wavs[0][1]) + '.wav'):
                    checked.append([str(all_wavs[0][1]) + '.wav',f[1]])

                break
            count += 1

        del all_wavs[0]
    all_wavdata = start_multi('accent_multi',checked,procs)
    tools.printer(2,'inserting in db','')
    index = 0
    for prep in all_wavdata:
        inserter.insert_db(prep,db)


def accent_multi(inputs):
    all_files = inputs[0]
    all_lines = len(all_files)
    all_wavdata = []
    index = 0


    if inputs[1] == 0:
        tools.printer(2,'analyzing accent')
    for files in all_files:

        if index % 100 == 0 and inputs[1] == 0:
            tools.printer(0,'[' + str(round((index/all_lines)*100,2)) + '%]',)


        md5check = tools.get_hash(files[0])
        trans = files[1]
        all_wavdata.append(transformer.wav_prepare([str(files[0]).replace('\'','\'\''),'0','0','0',str(trans).replace('\'','\'\''),'0','accent','',md5check,0,0]))

        index += 1
    return all_wavdata

def tatoeba_index(page_content,lang):
    big = 0
    try:
        pagenum = re.compile(r'<a href="/eng/audio/index/' + str(lang) + '/page:(.*?)"(.*?)>')
        if pagenum.search(page_content):
            pagenum = pagenum.findall(page_content)
        else:
            if re.compile(r'"pageNumber"><a href="(.*?)"(.*?)>').search(page_content):
                pagenum = pagenum_safe.findall(page_content)
        for page in pagenum:
            try:
                if int(page[0]) > big:
                    big = int(page[0])
            except:
                pass
    except:
        pass
    return big



def tatoeba_parser(path,url,lang,tato_lang,db):
    req = requests.get(url)
    if req.status_code != 200:
        raise base.FailedDownloadException('Failed to download data (status {}) from {}!'.format(req.status_code,
                                                                                                 url))
    page_content = req.text
    max_index = tatoeba_index(page_content,tato_lang)

    if max_index == 0:
        tools.printer(8,'no wavs found on site','')
        return False
    current_index = 1
    first = re.compile(r'data-sentence-id="(.*?) class="audioButton(.*?) audioAvailable')
    speaker_patter = re.compile(r'title="Play audio recorded by (.*?) class="audioButton(.*?) audioAvailable')
    text_pattern = re.compile(r'class="text correctnessZero">(.*?)<(.*?)/div>')
    mp3_pattern = re.compile(r'<a href="https://audio.tatoeba.org/(.*?)" (.*?)title="')
    raw_data = []
    index = 0
    already = 0
    all_wavdata = []
    mp3_count = 0
    all_lines = max_index * 100

    tools.printer(2,'downloading samples','tatoeba')
    for x in range(max_index+1):
        for match in first.findall(page_content):
            matched = match[0]

            mp3_count += 1
            
            if mp3_pattern.search(matched) and text_pattern.search(matched):
                no_file = False

                if speaker_patter.search(matched):
                    speaker = speaker_patter.findall(matched)[0][0]
                else:
                    speaker = '0'

                mp3_set = 'https://audio.tatoeba.org/' + str(mp3_pattern.findall(matched)[0][0])
                text_set = text_pattern.findall(matched)[0][0]
                raw_data.append([text_set,mp3_set])
                mp3 = path + '/' + mp3_set.split('/')[-1]



                try:
                    if os.path.isfile(mp3) == False and os.path.isfile(mp3.replace('.mp3','.wav')) == False:
                        filename = wget.download(mp3_set, mp3,None) 

                        new_wav = transformer.replace_wavs(mp3,['wav',16000,1,16,'signed-integer'],True)
                       # new_wav = replace_wav(mp3,['mp3',48000,1,16,'signed-integer'],True)
                        mp3 = new_wav
                    else:
                        mp3 = mp3.replace('.mp3','.wav')

                    tools.create_file(text_set,str(new_wav) + '.ttrn','w','')
                except:
                    no_file = True

                if index % 100 == 0:
                    tools.printer(0,'[' + str(round((mp3_count/all_lines)*100,2)) + '%]',)



                if no_file == False:
                    if len(all_wavdata) > 100:
                        inserter.insert_db(all_wavdata,db)
                        all_wavdata = []


                    md5check = tools.get_hash(mp3)
                    prepared = transformer.wav_prepare([mp3,'0','0',speaker,text_set.replace('&quot;','"').replace('#039;','\''),'0','tatoeba','0',md5check,0,0])
                    if prepared != False:
                        all_wavdata.append(prepared)   



                index += 1        
        current_index += 1

        page_html = url + 'page:' + str(current_index)
        req = requests.get(page_html)
        if req.status_code != 200:
            raise base.FailedDownloadException('Failed to download data (status {}) from {}!'.format(req.status_code,
                                                                                                 url))
        page_content = req.text
    if len(all_wavdata) > 0:
        inserter.insert_db(all_wavdata,db)



def vys_parser(path,db,lang,dataset,procs=0):
    all_lines = 0
    all_files = []
    if dataset == 'vystadial':
        fileend = 'wav.trn'
    elif dataset == 'custom':
        fileend = 'wav.ctrn'

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(fileend):
                trans = os.path.join(root, file)
                wav = os.path.join(root, file.replace(fileend,'.wav'))  
                if os.path.isfile(wav) == True:
                    all_files.append([str(wav).replace('\'','\'\''),str(trans).replace('\'','\'\'')])
                    all_lines += 1 


    all_wavdata = start_multi('vys_multi',all_files,procs,[dataset])
    tools.printer(2,'inserting in db','')
    index = 0
    for prep in all_wavdata:
        inserter.insert_db(prep,db)
    




def vys_multi(inputs):
    all_files = inputs[0]
    all_lines = len(all_files)
    all_wavdata = []
    index = 0

    if inputs[1] == 0:
        tools.printer(2,'analyzing vystadial')


    for files in all_files:

        if index % 100 == 0 and inputs[1] == 0:
            tools.printer(0,'[' + str(round((index/all_lines)*100,2)) + '%]',)


        md5check = tools.get_hash(files[0])
        trans = tools.get_file(files[1],False,True)
        all_wavdata.append(transformer.wav_prepare([str(files[0]).replace('\'','\'\''),'0','0','0',str(trans).replace('\'','\'\''),'0','vystadial','',md5check,0,0]))

        index += 1

    return all_wavdata




def tuda_multi(inputs):

    all_files = inputs[0]
    all_wavdata = []
    index = 0
    all_lines = 0
    for data in all_files: 
        for files in data[1]:
            all_lines += 1

    for data in all_files: 
        for files in data[1]:
            index += 1
            if index % 100 == 0 and inputs[1] == 0:
                tools.printer(0,'[' + str(round((index/all_lines)*100,2)) + '%]',)       
            md5check = tools.get_hash(files)
            prepared = transformer.wav_prepare([files,data[0][1],data[0][2],data[0][0],data[0][4],data[0][3],'tuda','',md5check,0,0])
            if prepared != False:
                all_wavdata.append(prepared)   
       

    return all_wavdata



def tuda_parser(rootdir,db,procs=0):
    if os.path.isdir(rootdir + '/train/') == False:
        rootdir += '/german-speechdata-package-v3'
    rootdir = rootdir.replace('//','/')
    if os.path.isdir(rootdir + '/train/') == False:
        return False

    sentences = {}
    cleaned_sentences = {}
    lang = 'de'
    sentences_pattern = re.compile(r"<cleaned_sentence>")
    speaker_pattern = re.compile(r"<speaker_id>")
    age_pattern = re.compile(r"<ageclass>")
    gender_pattern = re.compile(r"<gender>")
    dialect_pattern = re.compile(r"<bundesland>")
    all_lines = 0
    check_files = ['_Yamaha.wav' ,'_Kinect-RAW.wav' ,'_Kinect-Beam.wav' ,'_Realtek.wav' ,'_Samson.wav' ]
    all_files = []
    for folder in [rootdir + '/train/', rootdir + '/test/', rootdir + '/dev/']:
        for f in os.listdir(folder):
            if f.endswith('xml'):
                xmlpath = folder + f
                lines = tools.get_file(xmlpath,False)
                info = []

                if speaker_pattern.search(lines):
                    speaker = str(re.search('%s(.*)%s' % ('<speaker_id>', '</speaker_id>'), lines).group(1))
                else:
                    speaker = '0'

                if age_pattern.search(lines):
                    age = str(re.search('%s(.*)%s' % ('<ageclass>', '</ageclass>'), lines).group(1))
                else:
                    age = '0'

                if gender_pattern.search(lines):
                    gender = str(re.search('%s(.*)%s' % ('<gender>', '</gender>'), lines).group(1))
                else:
                    gender = '0'

                if dialect_pattern.search(lines):
                    dialect = str(re.search('%s(.*)%s' % ('<bundesland>', '</bundesland>'), lines).group(1))
                else:
                    dialect = '0'

                if sentences_pattern.search(lines):
                    sentence = str(re.search('%s(.*)%s' % ('<cleaned_sentence>', '</cleaned_sentence>'), lines).group(1))
                else:
                    sentence = '0'

                if sentence == '0':
                    pass
                else:


                    info = [speaker, age, gender, dialect,sentence]
                    files = []

                    for check in check_files: 

                        checker = xmlpath.replace('.xml',check)


                        if os.path.isfile(checker) == True:
                            files.append(checker)
                            all_lines += 1

                    
                    all_files.append([info,files])



    tools.printer(2,'analyzing','tuda')
    all_wavdata = start_multi('tuda_multi',all_files,procs,[lang])
    tools.printer(2,'inserting','tuda')

    for prep in all_wavdata:
        inserter.insert_db(prep,db)





def cv_parser(path,db,lang,dataset,procs=0):
    all_csv = []
    all_wavdata = []


    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.csv'):
                csvpath=os.path.join(root, file)
                all_csv.append(csvpath)

    if len(all_csv) == 0:
        tools.printer(9,'no csv files found in ',csvpath)
        return
    else:
        tools.printer(2,'csv found ',len(all_csv))

    maxcsv = len(all_csv) 
    all_lines = 0
    for csv in all_csv:
        with open(csv) as f:
            for lines in f:
                all_wavdata.append([str(lines),csv])
                all_lines += 1
        f.close()



    all_wavdata = start_multi('cv_multi',all_wavdata,procs,[lang,dataset])
    tools.printer(2,'inserting in db','')
    index = 0




    for prep in all_wavdata:
        inserter.insert_db(prep,db)




def cv_get_path(rootpath,filepath):
    csv_reg = '/'.join(rootpath.split('/')[-1:])
    csv_path = rootpath.replace(csv_reg,'')
    return str(csv_path) + str(filepath)



def cv_multi(inputs):

    lines = inputs[0]
    if inputs[1] == 0:
        tools.printer(2,'analyzing ' + str(inputs[4]) + '')

    lang = inputs[3]
    dataset = inputs[4]
    all_wavdata = []
    all_lines = len(lines)
    notfound = 0
    index = 0
    for line in lines: 
        index += 1
        
        csv = line[1]
        text = line[0]
        if index % 100 == 0 and inputs[1] == 0:
            tools.printer(0,'[' + str(round((index/all_lines)*100,2)) + '%]',)

        data = str(text).split(',')

        if len(data) == 8 and dataset == 'cv':
            path_set = cv_get_path(csv,data[0])
        elif len(data) > 2 and dataset == 'nicolas':
            path_set = '/'.join(csv.split('/')[:-1]) + '/' + data[0]
            text = ','.join(data[2:]).replace('\n','')



        else:
            path_set = ''

        if path_set == '' or os.path.isfile(path_set) == False:
            notfound += 1
        else:
            md5check = tools.get_hash(path_set)
            if dataset == 'cv':
                prepared = transformer.wav_prepare([path_set,data[5],data[4],'0',data[1],data[5],'cv',lang,md5check,data[2],data[3]])
            elif dataset == 'nicolas':
                prepared = transformer.wav_prepare([path_set,'0','0','0',text,'0','nicolas',lang,md5check,'0','0'])
            if prepared != False:
                all_wavdata.append(prepared)      



    return all_wavdata




def libri_parser(path,db,lang,procs=0):
    
    pathes = []
    filename = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if str(file) == 'metadata.txt' or str(file) == 'metadata.csv':
                filename.append(file)
                pathes.append(os.path.join(root, file))

    sentences = []
    all_lines = 0
    index = 0
    for meta in pathes:
        lines = tools.get_file(meta,True)
        for text in lines:

            splits = text.split('|')
            if len(splits) == 2 or len(splits) == 3:
                newpath = str(str(meta).replace(filename[index],'wavs/')  + str(splits[0]) + '.wav').replace('.wav.wav','.wav').replace('//','/')
              
                if os.path.isfile(newpath) == True:




                    sentences.append([str(newpath).replace('\'','\'\''),str(splits[1]).replace('\'','\'\'')])
                    all_lines += 1     
          
        index += 1




    all_wavdata = start_multi('libri_multi',sentences,procs,[lang])


    tools.printer(2,'inserting in db','')
    index = 0




    for prep in all_wavdata:
        inserter.insert_db(prep,db)
    

    

def libri_multi(inputs):

    all_wavdata = []

    sentences = inputs[0]
    lang = inputs[3]
    all_lines = len(sentences)
    index = 0
    if inputs[1] == 0:
        tools.printer(2,'analyzing librivox')

    for sentence in sentences:

        if index % 100 == 0 and inputs[1] == 0:
            tools.printer(0,'[' + str(round((index/all_lines)*100,2)) + '%]',)




        female_test = str(sentence[0]).split('/female/')
        male_test = str(sentence[0]).split('/male/')

        if len(male_test) == 2:
            gender = 'male'
            speaker = male_test[1].split('/')[1:][0]
        elif len(female_test) == 2:
            gender = 'female'
            speaker = female_test[1].split('/')[1:][0]
        else:
            gender = '0'
            speaker = '0'


        md5check = tools.get_hash(sentence[0])
        prepared = transformer.wav_prepare([sentence[0],gender,'0',speaker,sentence[1],'0','librivox',lang,md5check,0,0])
        if prepared != False:
            all_wavdata.append(prepared)   


        index += 1

    return all_wavdata
    




def swc_aligner(path):


    data = tools.get_file(path)
    sentences_temp = []
    all_sentences = []
    data = data.replace('<sectiontitle>','<s>').replace('</sectiontitle>','</s>').replace('<s text="','<s>').replace('<t text="','<t>').replace('<ignored>','</s>')
    sentence_reg = re.compile(r'<s>(.*?)</s>')
    word_reg = re.compile(r'<t>(.*?)</t>')

    for match in sentence_reg.findall(data):
        start_test = match.split('start="')
        end_test = match.split('end="')


        if len(start_test) > 3 and len(end_test) > 3:
            cleaned = ''
            cleaned_punc = ''
            
            end = end_test[-1].split('"')[0]
            start = start_test[1].split('"')[0]
            for word in word_reg.findall(match):
                split_word = word.split('<n pronunciation="')
                if len(split_word) > 1:
                    splitting = split_word
                    if len(split_word) > 3:
                        clean_word = split_word[0].split('"')[0]

                    else:
                        clean_word = split_word[1].split('"')[0]

                    clean_punc = split_word[0].split('>')[-1]

                else:
                    clean_punc = word
                    clean_word = ''

                cleaned_punc += clean_punc + ' '
                cleaned += clean_word + ' '
            sentences_temp.append([cleaned.replace('  ',' ').strip(),cleaned_punc.strip(),start,end,int(end)-int(start)])
        
    return sentences_temp








def swc_prepare(path,db,lang,procs=0):
    all_path = len(os.listdir(path))
    if all_path == 2:
        for x in os.listdir(path):
            if str(x) != 'download':
                path += '/' + x + '/'
        all_path = len(os.listdir(path))
    else:
        path = path + '/'
    path = path.replace('//','/')


    audios = []
    index = 0


    tools.printer(2,'aligning swc',)

    for x in os.listdir(path):
        newpath = path + x + '/'
        tools.printer(0,'[' + str(round((index/all_path)*100,2)) + '%]',str(x))

        if re.compile(r'[)]').search(x) or re.compile(r'[(]').search(x) or re.compile(r'[&]').search(x):
            clean_x = x.replace('(','').replace(')','').replace('&','und')
            clean_path = path + clean_x + '/'
            os.rename(newpath,clean_path)
            newpath = clean_path
        if os.path.isdir(newpath):

            audios = []
            aligner = ''
            for y in os.listdir(newpath):
                filecheck = newpath + y 
                if os.path.isfile(filecheck):
                    if y.endswith('.ogg') :
                        audios.append(filecheck)
                    if y == 'aligned.swc':
                        aligner = newpath + y
            if aligner != '' and len(audios) > 0:
                os.makedirs(os.path.join(newpath, 'converted'), exist_ok=True)
                if len(audios) > 1 and os.path.isfile(newpath + 'audio.wav') == False: 
                    check_convert = transformer.convert_audios(['wav',16000,1,16,'signed-integer'],audios,newpath + 'audio.wav',[],[])
                    if check_convert == False:
                        for aud in audios:
                            transformer.replace_wavs(aud)
                        check_convert = transformer.convert_audios(['wav',16000,1,16,'signed-integer'],audios,newpath + 'audio.wav',[],[])
                    if check_convert == True:
                        for aud in audios:
                            os.remove(aud)
                    audios = []
                    audios.append(newpath + 'audio.wav')
                elif os.path.isfile(newpath + 'audio.wav'):
                    if len(audios) > 1:
                        for aud in audios:
                            os.remove(aud)
                    audios = [newpath + 'audio.wav']
                align_data = swc_aligner(aligner)
                for align in align_data:
                    filename = newpath + 'converted/' + str(align[2]) + '-' +  str(align[3]) + '-' + str(round(int(align[4])/1000,2)).replace('.','_') + '.wav'
                    if os.path.isfile(filename) == False:
                        check_convert = transformer.convert_audios(['wav',16000,1,16,'signed-integer'],audios,filename ,[],[int(align[2])/1000,int(align[3])/1000])
                        if check_convert == True:
                            tools.create_file(align[0],filename + '.strn','w','')

                os.remove(audios[0])
        
        index += 1






def swc_multi(inputs):
    converted = inputs[0]
    if inputs[1] == 0:
        tools.printer(2,'analyzing swc')

    all_lines = len(converted)

    hits = [[['|user_name ','|user_name=','|user_name	','|sprecher ','|sprecher='],0],[['|gender ','|gender=','|gender	','|geschlecht ','|geschlecht='],1],[['|accent ','|accent=','|accent	','|dialekt ','|dialekt='],2]]
    index = 0   
    metafile = '' 
    tempmeta = ''  
    info_raw = ['0','0','0']  
    index = 0
    all_wavdata = []
    for convert in converted:
        info = ''

        wav_file = str(convert).replace('.wav.strn','.wav')

        if str(convert).endswith('562560-565300-2_74.wav.strn'):  # broken
            pass
        else:
            
            sentences = tools.get_file(convert)
            metafile = str("/".join(convert.split('/')[:-2])) + '/audiometa.txt'
    
            if metafile != tempmeta:
                tempmeta = metafile
                if os.path.isfile(metafile):
                    info = tools.get_file(metafile,True)
                    for i in info:
                        for h in hits:
                            for q in h[0]:
                                if i.startswith(q):
                                    if h[1] == 0 or h[1] == 1 or h[1] == 2:
                                        info_raw[h[1]] = str(i.split('=')[1]).strip() 
                        
                    if info_raw[1].strip().lower() in ['','geschlecht des sprechers']:
                        info_raw[1] = '0'
                    elif info_raw[1].strip().lower() in ['m','male','männlich','male, weiblich','maennlich','mänlich','malee','malee','mann','männ']:
                        info_raw[1] = 'male'
                    elif info_raw[1].strip().lower() in ['f','female','weiblich','weiblich (hochdeutsch), männlich (dialekt)','female, männlich','frau'  ]:
                        info_raw[1] = 'female'
    
    
    
    
    
    
        
            if index % 100 == 0 and inputs[1] == 0:
                tools.printer(0,'[' + str(round((index/all_lines)*100,2)) + '%]',)
    
            md5check = tools.get_hash(wav_file)    
            prepared = transformer.wav_prepare([wav_file,info_raw[1],'0',info_raw[0],sentences,info_raw[2],'swc','',md5check,'0','0'])
            if prepared != False:
                all_wavdata.append(prepared)  

          
        index += 1
    return all_wavdata


def start_multi(name,values,cpus=0,arguments=[]):


    real_cpus = max(1, cpu_count() - 1)
    if cpus == 0 or cpus > real_cpus:
        cpus = real_cpus
    

    all_values = len(values)
    steps = round(all_values/cpus)
    def_process = []
    for p in range(cpus):
        current = steps*p
        if p+1 == cpus:
            next = all_values
            current_range = next - current 
        else:
            next = steps*(p+1)-1
            current_range = next - current + 1

        def_temp = []
        for x in range(current_range):
            cur = x + current
            def_temp.append(values[cur])

        def_tempus = []
        def_tempus.append(def_temp)
        def_tempus.append(p)
        def_tempus.append(cpus)
        if len(arguments) > 0:
            for arg in arguments:
                def_tempus.append(arg)
        def_process.append(def_tempus)

    tools.printer(2,'processing',str(cpus))
    with Pool(cpus) as p:
        return p.map(eval(name), def_process)



def swc_parser(path,db,lang):
    swc_prepare(path,db,lang)
    converted_all = tools.search_path(path,'.wav.strn',2)
    all_wavdata = start_multi('swc_multi',converted_all,0)
    tools.printer(2,'inserting in db','')
    for prep in all_wavdata:
        inserter.insert_db(prep,db)
    tools.printer(2,'complete','')












def get_vox_wavs(path,info,db,dataset,lang):
    wavs = []

    if os.path.isfile(path + '/etc/prompts-original'):
        lines = tools.get_file(path + '/etc/prompts-original',True)
    elif os.path.isfile(path + '/etc/PROMPTS') == True:
        lines = tools.get_file(path + '/etc/PROMPTS',True)
    else:
        return False
    for line in lines:
        if line is not None and line is not '':
            splits = line.replace('	',' ').split(' ')
            wavs.append([splits[0],str(line).replace(str(splits[0]) + ' ','')])


    is_converted = False
    if os.path.isdir(str(path) + '/flac') == True:
        path = str(path) + '/flac/'


    else:
        path = str(path) + '/wav/'


    all_wavdata = []

    for test in wavs:  

        found = True
        if os.path.isfile(str(path + test[0])) == True:
            path_set = path + str(test[0]) 

        elif os.path.isfile(str(path + test[0] + '.wav')) == True:
            path_set = path + str(test[0]) + '.wav'

        elif os.path.isfile(str(path + test[0] + '.flac')) == True:
            path_set = path + str(test[0]) + '.flac'
        else:
            found = False


             

        if found == True:
            md5check = tools.get_hash(path_set)

            new_data = transformer.wav_prepare([path_set,info[1],info[2],info[0],test[1],info[3],dataset,lang,md5check,0,0])

            if new_data != False:
                all_wavdata.append(new_data)




    if len(all_wavdata) > 0:
        inserter.insert_db(all_wavdata,db)






def get_vox_info(readme_path):

    dialect = '0'
    speaker = '0'
    gender = '0'
    age_group = '0'
    native_lang = '0'

   

    male_hit = ['männlich', 'male', 'mnnlich','maschio','[maschio]']
    female_hit = ['weiblich', 'female', '[female]','femmina','[femmina]']
    adult_hit = ['erwachsener', 'adult', '[adult]', '[erwachsener]','adulto','[adulto]']
    senior_hit = ['senior', '[senior']
    youth_hit = ['youth', 'jugendlicher', '[youth]', '[jugendlicher]','giovane','[giovane]']
    child_hit = ['kind', 'child']



    if os.path.isfile(readme_path) == False:
        return [speaker, gender, age_group, native_lang]

    allline = tools.get_file(readme_path,True)
    for line in allline:
        if line is not None and line is not '':
            line = line.rstrip(';.')
            parts = line.split(':', maxsplit=1)

            if len(parts) > 1:
                key = parts[0].strip().lower()
                value = parts[1].strip()

                #tools.printer(2,key,value)

                if key == 'user name':
                    speaker = value

                value = value.lower()

                if key == 'gender':

                    if value in male_hit:
                        gender = 'male'
                    elif value in female_hit:
                        gender = 'female'
                    else:
                        gender = value

                if key == 'age range':

                    if value in adult_hit:
                        age_group = 'adult'
                    elif value in senior_hit:
                        age_group = 'senior'
                    elif value in youth_hit:
                        age_group = 'youth'
                    elif value in child_hit:
                        age_group = 'child'
                    else:
                        age_group = value

                if key == 'pronunciation dialect':
                    dialect = value


                if key == 'language':
                    native_lang = value
    return [speaker, gender, age_group, dialect , native_lang]





