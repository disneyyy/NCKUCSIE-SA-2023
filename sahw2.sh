#!/bin/tcsh
hash_num=-1
factor=1
pre="none"
activate=0
strfile="" # string of filenames
strnum="" # string of hash number
max=0
md5hash(){
    for (( i=2; i<=$max; i=i+1))
    do
        substrfile=$(echo $strfile | cut -d" " -f $i)
        substrnum=$(echo $strnum | cut -d" " -f $i)
        substrfile=$(md5sum $substrfile | cut -c 1-32)
        if [ "$substrnum" != "$substrfile" ] ; then
            echo -n -e "Error: Invalid checksum." 1>&2
            exit 1 
        fi
    done
}
sha256hash(){
    for (( i=2; i<=$max; i=i+1))
    do
        substrfile=$(echo $strfile | cut -d" " -f $i)
        substrnum=$(echo $strnum | cut -d" " -f $i)
        substrfile=$(sha256sum $substrfile | cut -c 1-64)
        if [ "$substrnum" != "$substrfile" ] ; then
            echo -n -e "Error: Invalid checksum." 1>&2
            exit 1 
        fi
    done
}
if [ "$#" -eq 1 ] && [ "$1" = "-h" ] ; then
    echo -n -e "\nUsage: sahw2.sh {--sha256 hashes ... | --md5 hashes ...} -i files ...\n\n--sha256: SHA256 hashes to validate input files.\n--md5: MD5 hashes to validate input files.\n-i: Input files.\n"
    exit 0
elif [ "$1" = "--md5" ] || [ "$1" = "--sha256" ] ; then
    for i in "$@" ; do
        if [ "$i" = "--sha256" ] && [ "$1" = "--md5" ] ; then
            echo -n -e "Error: Only one type of hash function is allowed." 1>&2
            exit 1
        elif [ "$i" = "--md5" ] && [ "$1" = "--sha256" ] ; then
            echo -n -e "Error: Only one type of hash function is allowed." 1>&2
            exit 1
        elif [ "$i" != "-i" ] ; then
            hash_num=$(( $hash_num + $factor ))
            if [ "$factor" -eq 1 ] ; then
                strnum="$strnum $i"
            else
                strfile="$strfile $i"
            fi
        else
            max=$(($hash_num+1))
            factor=-1
            strfile="$strfile $i"
        fi
    done
    if [ "$hash_num" -ne 0 ] ; then
        echo -n -e "Error: Invalid values." 1>&2
        exit 1
    elif [ "$1" = "--md5" ] ; then
        md5hash
    elif [ "$1" = "--sha256" ] ; then
        sha256hash
    else
        echo -n -e "Error: Invalid checksum." 1>&2
        exit 1 
    fi
    # while("$i" != "-i")
    #  
    # md5sum $file | cut -c 1-32
elif [ "$1" = "-i" ] ; then
    for i in "$@" ; do
        if [ "$i" = "--sha256" ] && [ "$pre" = "none" ]; then
            pre="--sha256"
            max=$(($hash_num+1))
            factor=-1
            strnum="$strnum $i"
        elif [ "$i" = "--md5" ] && [ "$pre" = "none" ] ; then
            pre="--md5"
            max=$(($hash_num+1))
            factor=-1
            strnum="$strnum $i"
        elif [ "$i" != "--sha256" ] && [ "$i" != "--md5" ] ; then
            hash_num=$(( $hash_num + $factor ))
            if [ "$factor" -eq -1 ] ; then
                strnum="$strnum $i"
            else
                strfile="$strfile $i"
            fi
        elif [ "$i" = "--md5" ] && [ "$pre" != "--md5" ] ; then
            echo -n -e "Error: Only one type of hash function is allowed." 1>&2
            exit 1
        elif [ "$i" = "--sha256" ] && [ "$pre" != "--sha256" ] ; then
            echo -n -e "Error: Only one type of hash function is allowed." 1>&2
            exit 1
        else
            echo -n -e "Error: Only one type of hash function is allowed." 1>&2
            exit 1
        fi
    done
    if [ "$hash_num" -ne 0 ] ; then
        echo -n -e "Error: Invalid values." 1>&2
        exit 1
    elif [ "$pre" = "--md5" ] ; then
        md5hash
    elif [ "$pre" = "--sha256" ] ; then
        sha256hash
    else
        echo -n -e "Error: Invalid checksum." 1>&2
        exit 1 
    fi
else
    echo -n -e "\nUsage: sahw2.sh {--sha256 hashes ... | --md5 hashes ...} -i files ...\n\n--sha256: SHA256 hashes to validate input files.\n--md5: MD5 hashes to validate input files.\n-i: Input files.\n"
    echo -n -e "Error: Invalid arguments." 1>&2
    exit 1
fi

# parsing file
factor=1
type="NONE"
str_usernames=""
str_passwords=""
str_shells=""
str_groups=""
for (( i=2; i<=$max; i=i+1)) ; do
    file_name=$(echo $strfile | cut -d" " -f $i)
    # echo "$file_name"
    cat "$file_name" | jq -r ".[] | .username" > /dev/null 2>&1
    last_result=$?
    if [ $last_result -eq 0 ] ; then
        type="JSON"
        str_usernames="$str_usernames$(cat "$file_name" | jq -r ".[] | .username" | tr '\n' ' ')"
        str_passwords="$str_passwords$(cat "$file_name" | jq -r ".[] | .password" | tr '\n' ' ')"
        str_shells="$str_shells$(cat "$file_name" | jq -r ".[] | .shell" | tr '\n' ' ')"
        str_groups="$str_groups$(cat "$file_name" | jq -r ".[] | .groups" | tr '\"' '\n' | tr -d "[ \n" | tr ']' '.' | tr ',' ' ')"
    fi
    if [ "$type" = "NONE" ] ; then
        if [ "$(head -n 1 $file_name | cut -c 1-30)" = "username,password,shell,groups" ] ; then
            type="CSV"
        else
            echo -n -e "Error: Invalid file format." 1>&2
            exit 1
        fi
        while read line
        do
            # echo $line
            if [ $factor -ne 1 ] ; then
                str_usernames="$str_usernames$(echo $line | cut -d"," -f 1) "
                str_passwords="$str_passwords$(echo $line | cut -d"," -f 2) "
                str_shells="$str_shells$(echo $line | cut -d"," -f 3) "
                if [ "$(echo $line | cut -d"," -f 4 | cut -c 1)" = " " ] ; then
                    str_groups="$str_groups$(echo $line | cut -d"," -f 4 | cut -c 2-)."
                else
                    str_groups="$str_groups$(echo $line | cut -d"," -f 4)."
                fi
            fi
            factor=$(($factor+1))
        done < "$file_name"
        # echo "$str_usernames"
    fi
    # echo "$type"
    type="NONE"
done
echo -n -e "This script will create the following user(s): $str_usernames"
echo -n -e "Do you want to continue? [y/n]:"
# echo "$str_passwords"
# echo "$str_shells"
# echo "$str_groups"

# max = filenum + 1