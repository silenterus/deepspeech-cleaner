#!/bin/bash


function installer {
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install sqlite3 -y
sudo apt-get install git -y
sudo apt-get install cmake -y
sudo apt-get install make -y
}

function check_progs {



get_config

checker=$(lmplz --help | grep "bash:")
if [ "$checker" != "" ]
then
    echo "lmplz NOT INSTALLED"
    echo "plz install "
    exit
fi


checker=$(build_binary --help | grep "bash:")
if [ "$checker" != "" ]
then
    echo "build_binary NOT INSTALLED"
    echo "plz install "
    exit
fi




checker1=$($root/native_client/generate_trie --help | grep "bash:")
checker2=$($root/generate_trie --help | grep "bash:")
if [ "$checker1" != "" ] && [ "$checker2" != "" ]
then
    echo "didnt found $deepspeech/generate_trie"
    echo "         or $deepspeech/native_client/generate_trie"
    echo "make sure your DeepSpeech path is correct"
    exit
fi


}




function get_config {

    if [ ! -f "audio.db" ] 
    then
        echo "no db"
        echo "run \"python3 deepspeech_cleaner.py --help\"  "
        echo ""
        exit
    fi
    config_data=$(sqlite3 "audio.db" "select earlystop_nsteps,train_batch_size,dev_batch_size,n_hidden,learning_rate,dropout_rate,display_step,validation_step,deepspeech_dir,epoch from configs where name='$config'")

    if [ ! "$config_data" ] || [ "$config_data" = ""] 
    then
        echo "no config data found for [$config]"
        echo "make sure the database is alright"
        exit
    else
        SAVEIFS=$IFS
        IFS=$'|'
        config_data=($config_data)
        IFS=$SAVEIFS


        earlystop_nsteps=${config_data[0]}
        train_batch_size=${config_data[1]}
        dev_batch_size=${config_data[2]}
        test_batch_size=${config_data[2]}

        n_hidden=${config_data[3]}

        learning_rate=${config_data[4]}
        dropout_rate=${config_data[5]}
        display_step=${config_data[6]}
        validation_step=${config_data[7]}
        root=${config_data[8]}
        epochs=${config_data[9]}

        if [ "$root" = "default" ] 
        then
            echo "run \"python3 deepspeech_cleaner.py --help\"  "
            echo ""
            exit
        fi
        echo "earlystop_nsteps : [$earlystop_nsteps]"
        echo "train_batch_size : [$train_batch_size]"
        echo "dev_batch_size   : [$dev_batch_size]"
        echo "test_batch_size  : [$test_batch_size]"
        echo "n_hidden         : [$n_hidden]"
        echo "learning_rate    : [$learning_rate]"
        echo "dropout_rate     : [$dropout_rate]"
        echo "display_step     : [$display_step]"
        echo "validation_step  : [$validation_step]"
        echo "epochs           : [$epochs]"
        
        echo "choosed [$config] config"
    fi


}


function start_training {
    cd "$root"
    python3.6 -u DeepSpeech.py --train_files "$train" --earlystop_nsteps $earlystop_nsteps --dev_files "$dev" --test_files "$test" --alphabet_config_path "$training/alphabet.txt" --lm_trie_path "$tries/trie" --lm_binary_path "$tries/lm.binary"  --train_batch_size $train_batch_size  --dev_batch_size $dev_batch_size --test_batch_size $test_batch_size --n_hidden $n_hidden --learning_rate $learning_rate --dropout_rate $dropout_rate --display_step $display_step --validation_step $validation_step --checkpoint_dir "$training/checkpoints" --export_dir "$training/model_export" 

}


    echo "first argument for training"
    echo "second argument for config name"


    if [ ! "$1" ] || [ "$1" = ""] 
    then

        echo "no training selected"
        exit
    else
        model="$1"
    fi
    if [ ! "$2" ] || [ "$2" = ""] 
    then

        echo "automatically picked [$config]"
        config="default"
    else
        config="$2"
    fi

get_config
root="/home/silenter/DeepSpeech"


training="$PWD/training/$model/"
train="$PWD/training/$model/train.csv"
dev="$PWD/training/$model/dev.csv"
test="$PWD/training/$model/test.csv"

start_training

