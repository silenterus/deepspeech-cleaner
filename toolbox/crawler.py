

from . import downloader, wikiextract, tools
import os
import sys
import requests
import wget
import re

def sort_remove_duplicates(path_to):
    #for huge textfiles
    tools.printer(2,'removing duplicates',path_to)
    os.system('cat "' + str(path_to) + '" | sort | uniq > "' + str(path_to) + '.tmp" && rm "' + str(path_to) + '" && mv "' + str(path_to) + '.tmp" "' + str(path_to) + '"')



def check_wiki(lang):
    """ Extract and return urls for all available .tgz files. """
    url = 'https://dumps.wikimedia.org/' + str(lang) +'wiki/'
    req = requests.get(url)

    if req.status_code != 200:
        return

    page_content = req.text
    link_pattern = re.compile(r'<a href="(.*?)">(.*?)</a>')
    array = []
    for match in link_pattern.findall(page_content):
        array.append(match[0])
    sorted(array)

    url = 'https://dumps.wikimedia.org/' + str(lang) +'wiki/' + array[-3]

    req = requests.get(url)

    if req.status_code != 200:
        return


    xml_pattern = re.compile(r'.xml')
    all_articles = []
    all_pages = []
    page_content = req.text
    for match in link_pattern.findall(page_content):
        if match[0].endswith('.bz2') and xml_pattern.search(match[0]):
            all_articles.append('https://dumps.wikimedia.org' + match[0]) 
            all_pages.append('https://dumps.wikimedia.org' + match[0]) 



    return [all_articles,all_pages]





def crawl_corpora(process,lang,lang_dir,minletters=20,append=True):


    if os.path.isfile(lang_dir + "clean_raw") == True and append == False:

        tools.printer(8,'already clean corpora',lang_dir + "clean_raw")
        u_input = tools.get_inputs([['w','overwrite',0],['a','append to existing',0]],'',True,True)
        if u_input == False:
            return False

        if u_input == 'o':
            mode = True
        elif u_input == 'a':
            mode = False

    elif append == True:
        mode = True
    else:
        mode = False



    dumps_dir = lang_dir + 'wiki_dumps/'

    all_url = check_wiki(lang)
 
    start = -1
    end = -1
    index = 0
    if all_url[0] != None:
        for url in all_url[0]:
            tools.printer(22,str(index) + '.',url.split('/')[-1],False,'',False,True,3)

            index += 1

        u_input = tools.get_inputs([['a','download and extract all',0],['0-' + str(len(all_url[0])-1) + '','download and extract specific',3]],'',True,True)
        if u_input == False:
            return False
        if u_input == 'u' or u_input == 'a':
            mode = True
        elif len(u_input) > 1:
            start = u_input[0]
            end = u_input[1]
            mode = True



    index = 0
    if all_url[0] != None:
        for url in all_url[0]:
      
            if start == -1 and end == -1:
                skip = False
 
            elif start <= index and end >= index:
                skip = False
            else:
                skip = True

            if skip == False:
                folder = url.split('/')[-1]
                current_dir = dumps_dir + folder + '/'
                if os.path.isfile(current_dir + 'wiki_articles.xml.bz2') == False:

                    tools.printer(2,'downloading wiki dumps',folder)
                    xmlfile = downloader.download_single(url,current_dir,'wiki_articles.xml.bz2')
                    xmlfile = current_dir + 'wiki_articles.xml.bz2'
                else:
                    xmlfile = current_dir + 'wiki_articles.xml.bz2'

                print('')
                tools.printer(2,'extracting articles - takes quite some time','')
                wikiextract.dump_xml(xmlfile,current_dir,process)
                os.remove(xmlfile)

                extract_sentences(current_dir,lang_dir,minletters,mode)





            index += 1



    tools.delete_all(dumps_dir)
    return True



def extract_sentences(dump_root,language_path,minletters,append=True):


    if append == True:
        mode = 'a'
    else:
        mode = 'w'

    dump_path = dump_root + 'AA/wiki_00'


    tools.printer(2,'spliting text into sentences','')
    # discard all sentences with these
    error = re.compile(r'[[(]|[)]|[\]]|[\[]|[{]|[}]|[=]|[<]|[>]|[/]|[\]|[#]|[*]|[+]|[~]|[|]|[¦]|[−]|[—]|[¦]|[_]|[0-9][-]|[-][0-9]|[-][-]]')


    counter = 0
    index = 0

    new_file = open(language_path + "clean_raw",mode)

    with open(dump_path, 'r') as f:
        for text in f:
            counter += 1

    with open(dump_path, 'r') as f:
        for text in f:
            # splitting the sentences
            text = text.replace('!','!SPLITTSENTENCES').replace('.','.SPLITTSENTENCES').replace('?','?SPLITTSENTENCES').replace('¡','¡SPLITTSENTENCES'.replace('¿','¿SPLITTSENTENCES'))
            sentences = text.split('SPLITTSENTENCES')
            for sentence in sentences:
                if error.search(sentence) or len(sentence) < minletters:
                    pass
                else:
                    new_file.write(sentence.replace('\xa0',' ').strip() + '\n')

            if index % 10000 == 0:
                tools.printer(0,'[' + str(round((index/counter)*100,2)) + '%]',)

            index += 1

        f.close()
    new_file.close()
    tools.delete_all(dump_root)
    sort_remove_duplicates(language_path + "clean_raw")
    return True








