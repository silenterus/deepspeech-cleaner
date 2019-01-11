#! /usr/bin/env python

import os
import shutil
import time
import random
import hashlib
import subprocess
import tarfile
import zipfile
from subprocess import CalledProcessError


def shell_call(args):
    try:
        shell_output = subprocess.check_output(
            args,
            stderr=subprocess.PIPE
        )
        return str(shell_output.decode("utf-8")).strip('\n')
    except CalledProcessError as cpe:
        return False



def printer(typ,message='',value='',logs=False,logs_path='',new=False,prints=True,maxspace=30):
    suffix = ''
    if typ == 4:
        message = 'space left'
        value = get_space('./')

    if typ > -3:
        if typ > -2:
            for x in range(maxspace-len(message)):
                message += ' '
        if value == '':
            pass
        elif value != '' and typ > -3:
            value = '[' + str(value) + ']'
    if typ == 0:
        suffix = '         '
    if typ == -3:
        suffix = '\n   -------------------------------------------------\n'
    elif typ == 1:
        suffix = '   <---> '
    elif typ == 11:
        suffix = '   ----- '
    elif typ == 2:
        suffix = '   >---> '
    elif typ == 22:
        suffix = '   <---< '
    elif typ == 33:
        suffix = '    ---  '
    if typ == 4:
        suffix = '   +---+ '
    elif typ == 8:
        suffix = '   --!-- '
    elif typ == 88:
        suffix = '   -!!!- '
    elif typ == 9:
        suffix = '   --?-- '
    elif typ == 99:
        suffix = '   -???- '

    if logs == True:
        if new == False:
            append = "a"
        else:
            append = "w"

        with open(logs_path, append) as f:
            f.write('\n' + suffix + str(message) + str(value))
            f.close
    if prints == True:
        print(suffix + str(message) + str(value))



def get_space(path):	
    total, used, free = shutil.disk_usage(path)
    space_left = str(round(free / 1000000000,2)) + ' GB'
    return space_left





def autosave_toggle(lang):
    tools.printer(-3)
    lang[3].execute("select autosave from configs limit 1")
    autosave = lang[3].fetchall()
    if autosave[0][0] == 0:
       printer(22,'Autosave','on')
       lang[3].execute("update configs set autosave=1")
    else:
       printer(22,'Autosave','off')
       lang[3].execute("update configs set autosave=0")
    lang[4].commit()

def check_deepspeech(lang):
    lang[3].execute("select deepspeech_path,configs_id,autosave from configs limit 1")
    deepspeech_data = lang[3].fetchall()
    if deepspeech_data[0][0] == 'default':
        deepspeech_path = get_deepspeech()
        if deepspeech_path == False:
            return False

        lang[3].execute("update configs set deepspeech_path='" + str(deepspeech_path[0]) + "' where configs_id=" + str(deepspeech_data[0][1]) + "")
        lang[4].commit()
        deep_dir = [deepspeech_path,1]
    else:
        deep_dir = [deepspeech_data[0][0],deepspeech_data[0][2]]
    return deep_dir


def get_inputs(allowed,message,forever=True,show=False):

    error = 0

    num_allowd = False
    msg = '   ' + message + ''
    while True:
        if len(allowed) > 0 and show == True:
            print()
            printer(11,'---------------------------','options',)
            print()
            for allow in allowed:
                printer(0,allow[1],allow[0])


         


        if error == 8:
            printer(9,'[q] for quit')

        printer(error,msg,'')

        u_input = input('>->')



        hit = ''
        for allow in allowed:
            if allow[2] == -1:
                hit = u_input
            elif allow[2] == 0 and u_input == allow[0]:
                hit = allow[0]
            elif allow[2] == 1 and os.path.isfile(u_input):
                hit = u_input
            elif allow[2] == 2 and os.path.isdir(u_input):
                hit = u_input
            elif allow[2] > 2:
                if allow[2] == 3:
                    splits = u_input.split('-')
                    if len(splits) == 2:
                        distance = [splits[0],splits[1]]
                    else:
                        distance = [u_input,u_input]

                    splits = allow[0].split('-')

                try:
                    if allow[2] == 3:
                        distance = [int(distance[0]),int(distance[1])]
                        if int(splits[0]) <= distance[0] and int(splits[1]) >= distance[1]:
                            hit = distance
                    if allow[2] == 4:
                        distance = [float(distance[0]),float(distance[1])]
                        if float(splits[0]) <= distance[0] and float(splits[1]) >= distance[1]:
                            hit = distance
                    elif allow[2] == 5:
                        hit = int(u_input)
                    elif allow[2] == 6:
                        hit = float(u_input)
                except:
                    pass

        if hit != '':
            break
        if u_input == 'q' or forever == False:
            if u_input == 'q':
                hit = False
            break

        if allowed[0][2] < 1:
            msg = '[' + str(u_input) + '] not allowed      \n  '
        else:
           if allowed[0][2] == 1: 
            msg = '[' + str(u_input) + '] file not found   \n  '
           elif allowed[0][2] == 2:
            msg = '[' + str(u_input) + '] path not found   \n  '

        error = 8

    printer(-3)
    return hit	


def get_hash(path):	

    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(path, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()
  


def check_dir():
    checkdir = os.getcwd()
    if os.path.isfile(str(checkdir) + "/deepspeech_cleaner.py") == True and os.path.isdir(str(checkdir) + '/toolbox/') == True:
        return checkdir
    else:
        printer(8,'wrong starting path','deepspeech_cleaner.py')
        return False


def create_folder(current_dir,current_model,typ,lang):
    if typ == 'create':
        printer(11,'trainings folder created\n','')
        access_rights = 0o755
        os.makedirs( current_dir + '/languages/' + str(lang) + '/training/' + current_model + '/checkpoints', access_rights )
        os.makedirs( current_dir + '/languages/' + str(lang) + '/training/' + current_model + '/info', access_rights )
        os.mkdir( current_dir + '/languages/' + str(lang) + '/training/' + current_model + '/model_export', access_rights )
        shutil.copy2( current_dir + '/languages/' + str(lang) + '/alphabet.txt' ,  current_dir + '/languages/' + str(lang) + '/training/' + current_model + '/') 



def get_min_max(minmax,types,table='default',cursor=None,model_path=None,autosave=0):

    if minmax == 'default' and types == 0:
        cursor.execute("select " + str(table) + " from languages where selected=1")
        minmax = cursor.fetchall()[0][0]
        printer(22,table,minmax,True,model_path)
    elif cursor != None and types == 0:
        printer(22,table,minmax,True,model_path)
        if autosave == 1:
            cursor.execute("update languages set " + str(table) + "='" + str(minmax) + "' where selected=1")


    if types == 1 and minmax == 'default':
        minmax = '0'
    
    array = []

    if types == 0:
        if minmax == '0':
            min_value = float(0)
            max_value = float(0)
        else:
            minmax = minmax.split('-')
            min_value = float(minmax[0])
            max_value = float(minmax[1])

        array.append(min_value)
        array.append(max_value)

    elif types == 1:
        if minmax == '0' or minmax == 'default':
            array.append(minmax)
        else:
            splits = str(minmax).split('-')
            for arr in splits:
                if arr is not None:
                    array.append(arr)
   

    return array

def get_extension(filename):
    basename = os.path.basename(filename)  
    ext = '.'.join(basename.split('.')[1:])
    return '.' + ext if ext else None



    

def get_size(size,types,logspath):
    value = 0
    for siz in size:
        if siz is not 'None':
            value += siz
    if types == 'size':
        value = value/1000000
        printer(2,'gb', str(round(value,2)),True,logspath)
    elif types == 'duration':
        value = value
        printer(2,'hours', str(round((value/60/60),1)),True,logspath)
    elif types == 'words' or  types == 'letters':
        printer(2,str(types), str(value),True,logspath)
        value = value

    return round(value,1)



def delete_all(path):
    all_pathes = search_path(path,'',3)
    for files in all_pathes[1]:
        if os.path.isfile(files):
            os.remove(files)
    for dirs in sorted(all_pathes[0],reverse=True):
        if os.path.isdir(dirs):
            os.rmdir(dirs)
def get_deepspeech():
    print()
    printer(9,'DeepSpeech path not found','')
    deepspeech_dir = get_inputs([['path/to/DeepSpeech','enter DeepSpeech path',2]],'',True,True)

    
    if deepspeech_dir == 'q' or deepspeech_dir == False:
        return False

    elif os.path.isfile(deepspeech_dir + '/DeepSpeech.py') == False:
        printer(9,'DeepSpeech.py not found','')
        return False
    
    else:
        if os.path.isfile(deepspeech_dir + '/VERSION') == True:
            with open(deepspeech_dir + '/VERSION') as f:
                version = f.read()
            f.close()
        else:
            printer(9,'VERSION not found','')
            version = input("plz enter DeepSpeech VERSION manually : ")



    printer(1,'VERSION',str(version).replace('\n',''))
    return [deepspeech_dir,version]


def get_file(path,array=False,strips=True):
    decoder = 'latin-1'
    try :
        with open(path, 'r') as f:
            if array == True:
                arr = []
                for raw_line in f:
                    if strips == True:
                        line = str(raw_line.strip())
                    else:
                        line = str(raw_line)
                    arr.append(line)
            else:
                arr = f.read()
                if strips == True:
                    line = str(arr.strip())
                else:
                    line = str(arr)
    except:
        with open(path, 'rb') as f:
            if array == True:
                arr = []
                for raw_line in f:
                    if strips == True:
                        line = str(raw_line.decode(decoder)).strip()
                    else:
                        line = str(raw_line.decode(decoder))
                    arr.append(line)
            else:
                arr = f.read()
                if strips == True:
                    arr = str(arr.decode(decoder)).strip()
                else:
                    arr = str(arr.decode(decoder))
    return arr

def create_file(value,path,mode='w',joiner='\n'):
    f = open(path, mode)
    if joiner != '':
        f.write(joiner.join(value))
    else:
        f.write(joiner.join(value))
    f.close()




def search_path(path,search='',starts=1):
    if starts == 3:
        array = [[],[]]
    else:
        array = []
    for root, dirs, files in os.walk(path):
        for file in files:
            current = ''
            if search == '' and starts != 3:
                current=os.path.join(root, file) 
            else:
                if starts == 0 and file == search:
                    current=os.path.join(root, file)
                elif starts == 1 and file.startswith(search):
                    current=os.path.join(root, file)            
                elif starts == 2 and file.endswith(search):
                    current=os.path.join(root, file) 
                elif starts == 3:
                    current=os.path.join(root, file) 

                       
            if current != '' and starts != 3:
                array.append(current)
            elif current != '' and starts == 3:
                array[1].append(current)
        if starts == 3 and search == '':
            array[0].append(root)


    return array




def extract_files(file_path, target_path):
    os.makedirs(target_path, exist_ok=True)

    ext = get_extension(file_path)

    if ext == '.zip':
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(target_path)
    else:
        with tarfile.open(file_path, 'r') as archive:
            archive.extractall(target_path)



    file_name = os.path.splitext(os.path.basename(file_path))[0]
    extracted = os.path.join(target_path, file_name)

    os.remove(file_path) 
    return extracted.replace('.tgz','').replace('.zip','').replace('.tar','').replace('?ddownload=','?download=')






