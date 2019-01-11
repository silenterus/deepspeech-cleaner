
deepspeech_path=$1
trainings_path=$2

if [ "$deepspeech_path" = "" ] || [ "$trainings_path" = "" ] || [ ! -d "$deepspeech_path" ] || [ ! -d "$trainings_path" ] 
then
    exit
fi
deepdir=$(echo "$deepspeech_path/" | sed "s/\/\/\//\//g" | sed "s/\/\///g")
words=$(echo "$trainings_path/words.arpa" | sed "s/\/\/\//\//g" | sed "s/\/\//\//g")
lm=$(echo "$trainings_path/lm.binary" | sed "s/\/\/\//\//g" | sed "s/\/\//\//g")
trie=$(echo "$trainings_path/trie"  | sed "s/\/\/\//\//g" | sed "s/\/\//\//g")
alphabet=$(echo "$trainings_path/alphabet.txt" | sed "s/\/\/\//\//g"  | sed "s/\/\//\//g")
start=$(echo "$trainings_path/start_train.sh" | sed "s/\/\/\//\//g"  | sed "s/\/\//\//g")
cleaner=$(echo "$trainings_path/clean" | sed "s/\/\/\//\//g"  | sed "s/\/\//\//g")
type=$3

if [ -f "../kenlm/build/bin/build_binary" ]
then
    lmplz="../kenlm/build/bin/lmplz"
    build_binary="../kenlm/build/bin/build_binary"
else 
    if ! [ -x "$(command -v lmplz)" ]; then
        echo 'lmplz is not installed.' >&2
        exit 1
    fi

    if ! [ -x "$(command -v build_binary)" ]; then
        echo 'Error: build_binary is not installed.' >&2
        exit 1
    fi
    lmplz=lmplz
    build_binary=build_binary
fi


if  [ -f  "$deepdir/native_client/generate_trie" ]
then
    generate="$deepdir/native_client/generate_trie"
elif [ -f  "$deepdir/generate_trie" ]
then
    generate="$deepdir/generate_trie"
else
    if ! [ -x "$(command -v genereate_trie)" ]; then
        echo 'genereate_trie not found' >&2
        exit 1
    fi    
fi


if [ "$type" = "1" ]
then
    $lmplz --o 3 --text "$cleaner" --arpa "$words"
    $build_binary trie  -T -s  "$words" "$lm"
    $generate
elif [ "$type" = "2" ]
then
    $lmplz  --o 3 --text "$cleaner" --arpa "$words"
    $build_binary trie -q 16 -b 7 -a 64  "$words" "$lm"
    $generate
elif [ "$type" = "3" ]
then
    $lmplz --order 5 --memory 50% --prune 0 0 0 1 --text "$cleaner" --arpa "$words"
    $build_binary trie -q 8 -a 255 "$words" "$lm"
    $generate "$alphabet" "$lm" "$trie"
        
fi


rm "$cleaner"
rm "$words"

