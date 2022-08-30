import os

logfile = '/log.txt'
print("log size is {size}kB".format(size=os.stat(logfile)[6]/1024))
with open(logfile, 'r', encoding='utf-8') as f:
    for line in f:
        print(line.rstrip())
