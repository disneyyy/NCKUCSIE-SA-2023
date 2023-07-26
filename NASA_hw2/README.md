# Simple Shell Script for FreeBSD
This is a shell script that can create many users at short time.  
# Environment
FreeBSD 13.1-RELEASE  
# Usages
* help: Terminal will print correct format to activate this shell script.  
```
./sahw2 -h
```  
* Choose either sha256 or md5 as hashing method. Can feed more than one files at a time.
```
./sahw2 {--sha256 | --md5} hash_string -i filename
```
For example:
* Valid Commands:
```
./sahw2 --sha256 77af778b51abd4a3c51c5ddd97204a9c3ae614ebccb75a606c3b6865aed6744e  -i test01.csv
```  
```
./sahw2 --md5 4a4be40c96ac6314e91d93f38043a634 c317ee448fd9d0ad7ab8cb429d691eee -i test01.csv test02.json
```  
```
./sahw2 -i test01.csv test02.json --md5 4a4be40c96ac6314e91d93f38043a634 c317ee448fd9d0ad7ab8cb429d691eee
```  
* Invalid Commands:
```
# ./sahw2 --sha256 77af778b51abd4a3c51c5ddd97204a9c3ae614ebccb75a606c3b6865aed6744e -i test01.csv test02.json
Error: Invalid values.
#
```
```
# ./sahw2 -i test01.json  --md5 4a4be40c96ac6314e91d93f38043a634 c317ee448fd9d0ad7ab8cb429d691eee
Error: Invalid values.
#
```
```
# ./sahw2 --sha256 77af778b51abd4a3c51c5ddd97204a9c3ae614ebccb75a606c3b6865aed6744e --md5 c317ee448fd9d0ad7ab8cb429d691eee -i test01.csv test02.json
Error: Only one type of hash function is allowed.
#
```  
If hash string doesn't match, output error message and terminate.  
```
# ./sahw2.sh --md5 00000000000000000000000000000000 -i test.csv
Error: Invalid checksum.
#
```
After verifying all hash strings respectively, terminal will print a message to check all usernames.
```
# ./sahw2 --md5 4a4be40c96ac6314e91d93f38043a634 -i test01.csv
This script will create the following user(s): user1 user_ejfiwfjoiew Do you want to continue? [y/n]:
```
If the user presses “n” or Enter, the script will exit with zero status code.
This shell script can skip users if they are already created or exist in the OS and print the warning message.
```
# ./sahw2 --md5 4a4be40c96ac6314e91d93f38043a634 -i test01.csv
This script will create the following user(s): user1 user_ejfiwfjoiew root user_haha iiiiiea Do you want to continue? [y/n]: y
Warning: user root already exists.
Warning: user iiiiiea already exists.
```
# Examples of .CSV and .JSON files
* .csv
```
username,password,shell,groups
admin_cat,cat001,/bin/sh, wheel operator
meow_2,cat002,/bin/tcsh,
meow_3,cat003,/bin/csh,
```
* .json
```
[
{
"username": "admin_cat",
"password": "cat001",
"shell": "/bin/sh",
"groups": ["wheel", "operator"]
},
{
"username": "meow_2",
"password": "cat002",
"shell": "/bin/tcsh",
"groups": []
},
{
"username":"meow_3",
"password":"cat003",
"shell":"/bin/csh",
"groups": []
}
]
```

> 作者：成功大學資訊工程學系113級 鄭鈞智  
> 最後編輯： 2023/07/26 15:50
