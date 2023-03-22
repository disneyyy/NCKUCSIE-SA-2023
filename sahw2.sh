#!/bin/tcsh

if [ "$#" -eq 1 ] && [ "$1" = "-h" ] ; then
    echo -n -e "\nUsage: sahw2.sh {--sha256 hashes ... | --md5 hashes ...} -i files ...\n\n--sha256: SHA256 hashes to validate input files.\n--md5:MD5 hashes to validate input files.\n-i: Input files.\n"

else
    echo "Hello World.\n"
fi
