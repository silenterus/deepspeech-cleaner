



#INTEGER 0. size      
#INTEGER 1. duration  
#INTEGER 2. samples   
#INTEGER 3. wordcount
#TEXT    4. sectors
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
#INTEGER 15. wordsec
#TEXT    16. dialect
#TEXT    17. dataset
#INTEGER    18. upvotes
#INTEGER    19. downvotes
#INTEGER    20. errors
#INTEGER    21. language
#INTEGER    22. letters
#INTEGER    23. lettersec
#INTEGER    24. md5sum



def update_db(all_wavdata,db):

    for wavdata in all_wavdata:
        db[1].execute("update audios set size=" + str(wavdata[0]) +", duration=" + str(wavdata[1]) +", samples=" + str(wavdata[2]) +", wordcount=" + str(wavdata[3]) +", sectors=" + str(wavdata[4]) +", wav_path='" + str(wavdata[6]) +"', samplerate=" + str(wavdata[11]) +", bitrate=" + str(wavdata[12]) +", channels=" + str(wavdata[13]) +", codec='" + str(wavdata[14]) +"', wordsec=" + str(wavdata[15]) +", lettersec=" + str(wavdata[23]) +", md5sum='" + str(wavdata[24]) +"' where audios_id=" + str(wavdata[-1])  + "")

    db[0] .commit()


def insert_db(all_wavdata,db):

    for wavdata in all_wavdata:


        db[1].execute("delete from audios WHERE md5sum='"  + str(wavdata[24]) +  "'")
        db[1].execute("insert or ignore into audios(size,duration,samples,wordcount,sectors,distance,wav_path,gender,age,speaker,text,samplerate,bitrate,channels,codec,wordsec,dialect,dataset,upvotes,downvotes,errors,lettercount,lettersec,md5sum) values(""" + str(wavdata[0]) + ',' + str(wavdata[1])  + ',' + str(wavdata[2]) + ',' + str(wavdata[3]) + ',\'' + str(wavdata[4]) + '\',\'' + str(wavdata[5]) + '\',\'' + str(wavdata[6]) + '\',\'' + str(wavdata[7]) + '\',\'' + str(wavdata[8]) + '\',\'' + str(wavdata[9]) + '\',\'' + str(wavdata[10]) + '\',' + str(wavdata[11]) + ',' + str(wavdata[12])  + ',' + str(wavdata[13])  + ',\'' + str(wavdata[14])  + '\',' + str(wavdata[15])  + ',\'' + str(wavdata[16])  + '\',\'' + str(wavdata[17]) + '\',' + str(wavdata[18]) + ',' + str(wavdata[19]) + ',' + str(wavdata[20]) + ',' + str(wavdata[22]) + ',' + str(wavdata[23]) + ',\'' + str(wavdata[24]) + "')")


    db[0] .commit()


