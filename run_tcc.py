# -*- coding: UTF-8 -*-
import TCCapply as TCCapply
import re,sys

TCCapply.GenRules()

def process_TCC(str1):
    text = str1.decode("utf-8")
    notSplit = re.compile(u'([^๐-๙0-9a-zA-Z])',re.UNICODE)
    notSplit2 = re.compile(u'([0-9๐-๙a-zA-Z]+)',re.UNICODE)
    text = notSplit2.sub('\g<0> ',text)
    text = notSplit.sub('\g<0> ',text)[:-1]
    TCCtext = TCCapply.ApplyTCC(text)
    return TCCtext

def load_file(fname=""):
    fp = open(fname,"r").readlines()
    l = ""
    for line in fp:
        l = process_TCC(line.strip().replace(" ",""))
        print l
    #return list(set(l))

if __name__ == "__main__":
    fname = sys.argv[1]
    l = load_file(fname)
    #for i,x in enumerate(l):
    #    print i+1,x
