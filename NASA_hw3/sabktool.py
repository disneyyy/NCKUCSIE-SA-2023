#!/usr/bin/env python3
import sys
import os
from time import sleep
from datetime import datetime

if __name__ == '__main__':
    if(len(sys.argv) == 2 and sys.argv[1] == "help"):
        print('Usage:\n\tcreate <snapshot-name>\n\tremove <snapshot-name> | all\n\tlist\n\troll <snapshot-name>\n\tlogrotate')
        sys.exit()
    elif(len(sys.argv) == 3 and sys.argv[1] == "create"):
        command="sudo zfs snapshot sa_pool/data@" + sys.argv[2]
        os.system(command)
        sys.exit()
    elif(len(sys.argv) == 3 and sys.argv[1] == "remove"):
        if(sys.argv[2] != "all"):
            command="sudo zfs destroy sa_pool/data@" + sys.argv[2]
        else:
            command="sudo zfs list -H -o name -t snapshot | sudo xargs -n1 zfs destroy >&2"
        os.system(command)
        sys.exit()
    elif(len(sys.argv) == 2 and sys.argv[1] == "list"):
        os.system("sudo zfs list -r -t snapshot -o name /sa_data")
    elif(len(sys.argv) == 3 and sys.argv[1] == "roll"):
        os.system("sudo zfs rollback -r sa_pool/data@" + sys.argv[2])
    elif(len(sys.argv) == 2 and sys.argv[1] == "logrotate"):
        os.system("sudo python3 fakeloggen.py 55 ")
        os.system("sudo logrotate /etc/logrotate.d/fakelog")
        os.system("sudo cp /var/log/fakelog/fakelog.log.* /sa_data/log/.")
        

