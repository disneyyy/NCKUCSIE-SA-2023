#!/bin/tcsh
hash_num=-1
factor=1
if [ "$#" -eq 1 ] && [ "$1" = "-h" ] ; then
    echo -n -e "\nUsage: sahw2.sh {--sha256 hashes ... | --md5 hashes ...} -i files ...\n\n--sha256: SHA256 hashes to validate input files.\n--md5:MD5 hashes to validate input files.\n-i: Input files.\n"
    exit 0
elif [ "$1" = "--md5" ] || [ "$1" = "--sha256" ]; then
    max=0
    for i in "$@" ; do
        if [ "$i" = "--sha256" ] && [ "$1" = "--md5" ] ; then
            echo "Error: Only one type of hash function is allowed."
            exit 1
        elif [ "$i" = "--md5" ] && [ "$1" = "--sha256" ] ; then
            echo "Error: Only one type of hash function is allowed."
            exit 1
        elif [ "$i" != "-i" ] ; then
            hash_num=$(( $hash_num + $factor ))

        else
            max=${hash_num}
            factor=-1
        fi
    done
    if [ "$hash_num" -ne 0 ] ; then
        echo "Error: Invalid values."
        exit 1
    else
        echo "correct" 
    fi
    # while("$i" != "-i")
    #  
    # md5sum $file | cut -c 1-32
else
    echo "Error: Invalid arguments."
    echo -n -e "\nUsage: sahw2.sh {--sha256 hashes ... | --md5 hashes ...} -i files ...\n\n--sha256: SHA256 hashes to validate input files.\n--md5:MD5 hashes to validate input files.\n-i: Input files.\n"
    exit 1
fi
# sha256sum $file | cut -c 1-64
