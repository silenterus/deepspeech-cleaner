import os
import re
import gzip
import io
import wget
import requests
from . import tools, parser



def download(working_path,target_path,db,lang,dataset):
    if len(dataset) == 0:
        tools.printer(9,'no corpus found',str(dataset))
        return
    tools.printer(2,'selected corpora',)
    for sets in dataset:
        tools.printer(0,'',str(sets[1]))

    all_urls = []
    all_path = []
    vox_num = 0
    current_vox = 0
    for sets in dataset:
        if sets[1] == 'vox16' or sets[1] == 'zamia' or sets[1] == 'vox8' or sets[1] == 'forscher' :
            all_temp_urls = check_vox_files(sets[0],all_urls,sets[1],vox_num)
            vox_num = all_temp_urls[1]
            all_urls = all_temp_urls[0]
 
        else:
            all_urls.append([sets[0],sets[1]])

    index = 0
    for urls in all_urls:
        index += 1
        if urls[1] == 'tatoeba':
            tools.printer(-4)
            tools.printer(2,'current dataset',urls[1])
            langs_id = str(urls[0]).split('/')[-2]
            temp_folder = os.path.join(target_path, str(urls[1]))
            os.makedirs(temp_folder, exist_ok=True)
            parser.tatoeba_parser(temp_folder,urls[0],lang,langs_id,db)
        else:          
            temp_folder = os.path.join(target_path, str(urls[1]) + '/download')
   
            os.makedirs(temp_folder, exist_ok=True)

            downloaded = download_files(urls[0], temp_folder,urls[1],db)


            if downloaded != '' and downloaded != True:
                print('')
                tools.printer(2,'extracting')
                extracted = tools.extract_files(downloaded, target_path + urls[1])
                tools.printer(2,'reading info')
                if urls[1] == 'vox16' or urls[1] == 'zamia' or urls[1] == 'vox8' or urls[1] == 'forscher' :
                    info = parser.get_vox_info(str(extracted) + '/etc/README')
                    tools.printer(2,'inserting wavs','')
                    parser.get_vox_wavs(str(extracted),info,db,urls[1],lang)
                elif urls[1] == 'swc':
                    parser.swc_parser("/".join(str(extracted).split('/')[0:-1]),db,lang)
                elif urls[1] == 'librivox':
                    parser.libri_parser("/".join(str(extracted).split('/')[0:-1]),db,lang)
                elif urls[1] == 'cv':
                    parser.cv_parser(str(extracted),db,lang)            
                elif urls[1] == 'tuda':
                    parser.tuda_parser(str(extracted),db)
                elif urls[1] == 'vystadial':
                    parser.vys_parser(str(extracted),db,lang)
                elif urls[1] == 'accent':
                    parser.accent_parser(str(extracted),db)
            if urls[1] == 'vox16' or urls[1] == 'zamia' or urls[1] == 'vox8' or urls[1] == 'forscher' :
                current_vox += 1
                if downloaded == '':
                    tools.printer(22,'already downloaded',str(index) + '/' + str(len(all_urls)))
                else:
                    tools.printer(0,'[' + str(round((current_vox/vox_num)*100,2)) + '%]\n',)
                    tools.printer(2,'current dataset',urls[1])
                    tools.printer(2,'checking ',str(current_vox) + '/' + str(vox_num))



def download_files(file_url, target_path,corpus,db):
    start_download = True
    path_check = str(target_path).replace('download','')
    check_dataset = insert_corpora(path_check)
    if check_dataset == '':
        if corpus != 'vox16' and  corpus != 'vox8'  and corpus != 'forscher'  and corpus != 'zamia' :
            tools.printer(-4)
            tools.printer(2,'current dataset',corpus)
    elif corpus != 'vox16' and  corpus != 'vox8'  and corpus != 'forscher'  and corpus != 'zamia' :
        cmd = already_downloaded(path_check,corpus,db)
        if cmd == 'd':
            tools.delete_all(path_check)
        elif cmd == 'i':
            insert_corpora(path_check,True,db,'')
            return True
        elif cmd == 'q':
            return False
        else:
            return ''

    os.makedirs(target_path, exist_ok=True)
    file_name = os.path.basename(file_url)

    if corpus == 'vox16' or corpus == 'vox8' or corpus == 'forscher' or corpus == 'zamia':
        check_path = str(target_path).replace('download','')  + str(file_name).replace('.tgz','').replace('.zip','').replace('.tar','') + '/etc'


        if os.path.isdir(check_path) == False:
            start_download = True
        else:
            start_download = False


    if start_download == True:
        target_file_path = os.path.join(target_path, file_name)
        tools.printer(2,'downloading',str(file_url).split('/')[-1])
        filename = wget.download(file_url, target_file_path)  



        return filename
    else:
        return ''





def download_clean(file_url, target_path,file_name='clean_raw.gz'):
    target_file_path = os.path.join(target_path, file_name)
    tools.printer(2,'downloading',str(file_url))
    filename = wget.download(file_url, target_file_path) 
    with open(target_path + 'clean_raw', 'a', encoding='utf-8') as clean:
        with io.TextIOWrapper(io.BufferedReader(gzip.open(filename)), encoding='utf8') as text:
            for line in text:
                clean.write(line)
    os.remove(target_file_path) 




def download_single(file_url, target_path,file_name):
    os.makedirs(target_path, exist_ok=True)
    filename = wget.download(file_url, target_path + '/' + file_name)  
    return target_path + '/' + file_name



def already_downloaded(path_check,corpus,db):
        tools.printer(0,'')
        tools.printer(22,'already downloaded',corpus)
        return tools.get_inputs([['d','delete and redownload',0],['i','insert again',0],['s','skip',0]],'',True,True)





def check_corpora(lang,selected,types=0):
    sql = ''
    datasets = []
    if len(selected) > 0:
        
        if selected[0] == '0' or selected == '[\'0\']':
            lang[3].execute("select url,corpora,size from urls where corpora!='tedv1' and corpora!='tedv2' and corpora!='vox8' and type="+ str(types) + " and languages_id=" + str(lang[1])  + " order by corpora asc")
            raw_urls = lang[3].fetchall()
            if len(raw_urls) > 0:
                for url in raw_urls:
                    if url[1] != 'tedv1' and url[1] != 'tedv2' and url[1] != 'tedv3': #no parser yet
                        datasets.append([url[0],url[1],url[2]])
                    elif types == 1:
                        datasets.append([url[0],url[1],url[2]])
        else:

            for select in selected:
                if select == 'vox':
                    select = 'vox16'
                lang[3].execute("select url,corpora,size from urls where type="+ str(types) + " and languages_id=" + str(lang[1]) + " and corpora='" + str(select)  + "' order by corpora asc")
                url = lang[3].fetchall()
                if len(url) > 0:
                    for u in url:
                        if u[1] != 'tedv1' and u[1] != 'tedv2' and u[1] != 'tedv3':  #no parser yet
                            datasets.append([u[0],u[1],u[2]])


    return datasets




def insert_corpora(target_path,insert=False,db=None,lang=''):
    files = tools.search_path(target_path)
    testing = [['aligned.swc','swc'],['/male/','librivox'],['etc/PROMPT','vox'],['etc/prompts-','vox'],['Kinect-Beam.','tuda'],['conditioned.txt','accent'],['.trn','vystadial','swc'],['.strn','swc'],['invalidated.tsv','cv'],['/cv-other-train.csv','cv'],['/data.csv','nicolas'],['.ttrn','tatoeba'],['.ctrn','custom']]
    dataset = ''
    for f in files:
        for test in testing:
            testsplit = f.split(test[0])
            if len(testsplit) > 1:
                dataset = test[1]
                break

        if dataset != '':
            break

    if insert == True:
        tools.printer(22,'recognize dataset',dataset)
        if dataset == 'vox':
            pass
        elif dataset == 'librivox':
            parser.libri_parser(target_path,db,lang)
        elif dataset == 'swc':
            parser.swc_parser(target_path,db,lang)
        elif dataset == 'cv' or dataset == 'nicolas':
            parser.cv_parser(target_path,db,lang,dataset)
        elif dataset == 'tuda':
            parser.tuda_parser(target_path,db)
        elif dataset == 'vystadial' or dataset == 'custom':
            parser.vys_parser(target_path,db,lang,dataset)
        elif dataset == 'accent':
            parser.accent_parser(target_path,db)




    return dataset









def check_vox_files(url,available_files,dataset,voxnum):
    """ Extract and return urls for all available .tgz files. """
    req = requests.get(url)

    if req.status_code != 200:
        raise base.FailedDownloadException('Failed to download data (status {}) from {}!'.format(req.status_code,
                                                                                                 url))

    page_content = req.text
    link_pattern = re.compile(r'<a href="(.*?)">(.*?)</a>')

    
    for match in link_pattern.findall(page_content):
        if match[0].endswith('.tgz'):
            voxnum += 1
            available_files.append([os.path.join(url, match[0]),dataset])




    return [available_files,voxnum]


