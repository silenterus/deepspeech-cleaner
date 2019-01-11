import os
import sox
from . import tools, parser, inserter
from multiprocessing import Pool


def convert_select(mode,corporas,autoreplace,convert_settings,trimm_settings):
    tools.printer(2,'output settings',str(convert_settings).replace('[','').replace(']','').replace(',','').replace('\'',''))
    if mode == 'convert':
        select = [['s','change output settings',0],['r','autoreplace ' + str(autoreplace) + '',0],['a','convert all',0]]
    elif mode == 'trimm' or mode == 'trimmsilence':
        select = [['s','change output settings',0],['t','change ' + str(mode) + ' settings',0],['r','autoreplace ' + str(autoreplace) + '',0],['a','' + str(mode) + ' all',0]]
        tools.printer(2,'' + str(mode) + ' settings',str(trimm_settings[0]) + ' ' + str(trimm_settings[1]))
    index = 1
    for corp in corporas:
        select.append([str(index),corp[0],0])
        index += 1

    array = [tools.get_inputs(select,'',True,True)]

    if array[0] in ['s','r','t','q',False]:

        return array[0]
    elif array[0] == 'a':
        query = "select wav_path,audios_id from audios"  
    else:
        for corp in select:
            if corp[0] == array[0]:
                query = "select wav_path,audios_id,text from audios where dataset='" + str(corp[1]) + "'"  
    return query


def convert_get(teststring,typus):

    testsplit = str(teststring).split(' ')
    if typus.startswith('trimm'):
        try:
            return [float(testsplit[0]),float(testsplit[1])]
        except:
            return False
    else:
        try:
            return [str(testsplit[0]),int(testsplit[1]),int(testsplit[2]),int(testsplit[3]),str(testsplit[4])]
        except:
            return False





def convert_all(mode,cpus,db,convert_settings,trimm_settings):

    autoreplace = True
    if mode == 'trimmsilence':
        trimm_settings = [0.3, 0.2]
    elif mode == 'trimm':
        trimm_settings = [0.5,0.5]





    db[1].execute("select distinct dataset from audios" )
    corporas = db[1].fetchall()
    index = 1
    settings = ''
    tools.printer(0,'',mode)
    while True:
        array = convert_select(mode,corporas,autoreplace,convert_settings,trimm_settings)
        if array == False or array == 'q':
            return False 
        elif array == 'a':
            query = "select wav_path,audios_id from audios"  
            break
        elif array != 't' and array != 's' and array != 'r':
            query = array
            break
        if array == 't':
            select = [['','',-1,False,False]]
            settings = convert_get(tools.get_inputs(select,' ',True,True),mode)
        elif array == 's':
            select = [['','',-1,False,False]]
            settings = convert_get(tools.get_inputs(select,' ',True,True),'convert')
        elif array == 'r':
            if autoreplace == True:
                autoreplace = False
            elif autoreplace == False:
                autoreplace = True



        if array != 'r' and settings != False and settings != 'q':
            if array == 't':
                trimm_settings = settings
            if array == 's':
                convert_settings = settings
       

    db[1].execute(query)
    audios = db[1].fetchall()


    if len(convert_settings) != 5 and len(convert_settings) != 3:
        convert_settings = convert_get(convert_settings,'')

   
    counter = len(audios)

    steps = round(counter/cpus)
    start = 0
    end = 0
    current = 0
    all_process = []
    for p in range(cpus):

        start = current
        current += steps

        if p+1 == cpus:
            end = counter
        else: 
            end = current
        end = end -start




        process_temp = []
        for aud in audios[start:][:end]:
            if mode == 'convert':
                process_temp.append([aud[1],aud[0],aud[2],convert_settings,[],[],autoreplace])
            elif mode == 'trimm':
                process_temp.append([aud[1],aud[0],aud[2],convert_settings,[],trimm_settings,autoreplace])
            elif mode == 'trimmsilence':
                process_temp.append([aud[1],aud[0],aud[2],convert_settings,trimm_settings,[],autoreplace])

        all_process.append([process_temp,p])





    tools.printer(2,'processing',cpus)

    with Pool(cpus) as p:
        all_wavdata = p.map(convert_prepare, all_process)

    for prep in all_wavdata:
        inserter.update_db(prep,db)






def convert_audios(settings,path,pathto,vadfactor=[],trimmfactor=[]): 
    try:
        if len(path) > 1:
            tools.printer(2,'combining','')
            cbn = sox.Combiner()
            if settings[0] == 'mp3':
                cbn.set_output_format(file_type=settings[0],rate=settings[1],channels=settings[2])
            else:
                cbn.set_output_format(file_type=settings[0],rate=settings[1],channels=settings[2],bits=settings[3],encoding=settings[4])
            cbn.convert()
            cbn.build(
                path, pathto, 'concatenate'
            )
        else:
    
            tfm = sox.Transformer()

            if settings[0] == 'mp3':
                tfm.set_output_format(file_type=settings[0],rate=settings[1],channels=settings[2])          
            else:
                tfm.set_output_format(file_type=settings[0],rate=settings[1],channels=settings[2],bits=settings[3],encoding=settings[4])          
    
    
            if len(trimmfactor) > 1:
                tfm.trim(trimmfactor[0],trimmfactor[1])
            if len(vadfactor) > 1:

                tfm.vad(initial_pad=vadfactor[0])
                tfm.vad(location=-1, initial_pad=vadfactor[1])
    
            tfm.convert()
            tfm.build(path[0], pathto) 
        return True
    except:
            return False




def convert_prepare(inputs):
    proc = inputs[1]
    raw = inputs[0]
    all_results = []
    all_lines = len(raw)
    index = 0
    for r in raw:
        if index % 1000 == 0 and proc == 0:
            tools.printer(0,'[' + str(round((index/all_lines)*100,2)) + '%]',)
        if os.path.isfile(r[1]):
            oldpath = r[1] 
            newpath = '.back.'.join(str(r[1]).split('.')) 
            if len(r[5]) > 1:
                duration = sox.file_info.duration(r[1])
                trimming = [r[5][0],duration-r[5][1]]
            else:
                trimming = []
            check_convert = convert_audios(r[3],[oldpath],newpath,r[4],trimming)
      
            if r[6] == True and check_convert != False:
                os.remove(oldpath)
                os.rename(newpath,oldpath)
            elif r[6] == False and check_convert != False:
                os.rename(oldpath,oldpath + '.temp')
                os.rename(newpath,oldpath)
                os.rename(oldpath + '.temp',newpath)

            if check_convert != False:
                new_data = ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'] 
                new_data[24] = tools.get_hash(oldpath)
                new_data[6] = str(oldpath).replace('\'','\'\'') 
                new_data[10] = str(r[2]).replace('\'','\'\'') 
                new_data.append(r[0])
                all_results.append(scan_file(new_data))
        index += 1 

    if proc == 0:
        tools.printer(0,'[100%]',) 
    return all_results




def wav_prepare(data):
    if os.path.isfile(data[0]) == False:
        return False
    if data[0].endswith('.flac') or data[6] == 'zamia' or data[6] == 'forscher':
        data[0] = replace_wavs(data[0],['wav',16000,1,16,'signed-integer'],True)
        data[8] = tools.get_hash(data[0])
    if data[0] == False:
        return False


    #TEXT  0  6. wav_path
    #TEXT  1  7. gender
    #TEXT  2  8. age
    #TEXT  3  9. speaker
    #TEXT  4  10. text
    #TEXT  5  16. dialect
    #TEXT  6  17. dataset
    #TEXT  7  21. language
    #TEXT  8  24. md5sum
    new_data = ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'] 
    new_data[6] = str(data[0]).replace('\'','\'\'') 
    new_data[7] = str(data[1]).replace('\'','\'\'')
    new_data[8] = str(data[2]).replace('\'','\'\'')
    new_data[9] = str(data[3]).replace('\'','\'\'')
    new_data[10] = str(data[4]).replace('\'','\'\'') 
    new_data[16] = str(data[5]).replace('\'','\'\'') 
    new_data[17] = str(data[6]).replace('\'','\'\'')
    new_data[21] = str(data[7]).replace('\'','\'\'')
    new_data[24] = str(data[8]).replace('\'','\'\'')
    new_data[18] = str(data[9]).replace('\'','\'\'')
    new_data[19] = str(data[10]).replace('\'','\'\'')
    return scan_file(new_data)




def replace_wavs(path,settings=['wav',16000,1,16,'signed-integer'],change_ext=False):
    try:
        path_temp = str(path).replace('.wav','.temp.wav').replace('.ogg','.temp.ogg').replace('.mp3','.temp.mp3').replace('.flac','.temp.flac')
        convert_audios(settings,[path],path_temp)
        os.remove(path)
        if change_ext == True:
            sets = '.' + settings[0]
            path_new = path_temp.replace('.temp.wav',sets).replace('.temp.ogg',sets).replace('.temp.mp3',sets).replace('.temp.flac',sets)
        else:
            path_new = path_temp.replace('.temp.wav','.wav').replace('.temp.ogg','.ogg').replace('.temp.mp3','.mp3').replace('.temp.flac','.flac')
        os.rename(path_temp,path_new)


    except:
        return False

    return path_new
        

def scan_file(data):
    filesize = ''
    duration_sek = ''
    samples = ''
    samplerate = ''
    info = tools.shell_call(['sox', '--i', '-T' ,data[6]])
    if info == False:
        return False
    for i in info.split('\n'):
        splits = i.replace(' ','').split(':')
        if len(splits) > 1:
            if splits[0] == 'Channels':
                channel = splits[1]
            elif splits[0] == 'SampleRate':
                samplerate = splits[1]
            elif splits[0] == 'Precision':
                precision = splits[1].replace('-bit','')
            elif splits[0] == 'Duration':
                temp = ':'.join(splits[1:]).split('=')
                if len(temp) > 1:
                    duration_sek = temp[0].split(':')
                    duration_sek = float(int(duration_sek[0])*60*60+int(duration_sek[1])*60+float(duration_sek[2]))
                    tempus = temp[1].split('samples~')
                    if len(tempus) > 1:
                        samples = temp[1].split('samples~')[0]
                        sectors = temp[1].split('samples~')[1].replace('CDDAsectors','')
                    else:
                         return False
                else:
                    return False
            elif splits[0] == 'FileSize':
                filesize = splits[1].lower()
                if filesize.endswith('k'):
                    filesize = filesize.replace('k','')
                elif filesize.endswith('m'):
                    filesize = float(filesize.replace('m',''))*1000
                elif filesize.endswith('g') or filesize.endswith('gb'):
                    filesize = float(filesize.replace('m',''))*1000*1000
            elif splits[0] == 'SampleEncoding':
                temp = i.split(':')[1].strip()
                encoding = temp


    if filesize == '' or duration_sek == '' or samples == '' or samplerate == '' or len(data[10]) == 0:
        return False
    data[0] = filesize
    data[1] = duration_sek
    data[2] = samples
    data[4] = sectors
    data[11] = samplerate
    data[12] = precision
    data[13] = channel
    data[14] = encoding
    data[3] = len(data[10].split(' '))
    data[15]  = data[1]/data[3]
    data[22] = len(data[10])
    data[23]  = data[1]/data[22]
    return data


