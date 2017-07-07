#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os, sys,codecs, re

reload(sys)
fileencoding = 'UTF-8'
sys.setdefaultencoding(fileencoding)

con = ('ก','ข','ค','ฅ','ฆ','ง','จ','ฉ','ช','ซ','ฌ','ญ','ฎ','ฏ',
    'ฐ','ฑ','ฒ','ณ','ด','ต','ถ','ท','ธ','น','บ','ป','ผ','พ',
    'ฟ','ภ','ม','ย','ร','ฤ','ล','ฦ','ว','ศ','ษ','ส','ห','ฬ','อ','ฮ')

con_txt=''
for i in con: #set con1 in format ก|ข|...
    con_txt=con_txt+i#+'|'
con_txt=con_txt#[0:-1]

vol1 = ('ะ','า','ำ')
vol1_txt=''
for i in vol1:
    vol1_txt=vol1_txt+i#+'|'
vol1_txt=vol1_txt#[0:-1]

vol2 = ('เ','แ','โ','ไ','ใ')
vol2_txt=''
for i in vol2:
    vol2_txt=vol2_txt+i#+'|'
vol2_txt=vol2_txt#[0:-1]

vol3 = ('ั','ื','ึ')
vol3_txt=''
for i in vol3:
    vol3_txt=vol3_txt+i#+'|'
vol3_txt=vol3_txt#[0:-1]

vol4 = ('ิ','ี','ุ','ู')
vol4_txt=''
for i in vol4:
    vol4_txt=vol4_txt+i#+'|'
vol4_txt=vol4_txt#[0:-1]

ton = ('่','้','๊','๋')
ton_txt=''
for i in ton:
    ton_txt=ton_txt+i#+'|'
ton_txt=ton_txt#[0:-1]
all_rules = []
#outTest = codecs.open('./Test/out','w+',fileencoding)
#inTest = codecs.open('./Test/in','r',fileencoding)

def ApplyTCC(text):
        #text = text.rstrip().replace('',' ')
    #print text
    for i in range(0,len(all_rules)):
        result = ''
        pat = all_rules[i]
        lastEnd = 0
        regex = re.compile(unicode(pat),re.UNICODE)
        for m in regex.finditer(text):
            replaceTxt = m.group(0).replace(u' ',u'')
            result = result+text[lastEnd:m.start()]+replaceTxt
            lastEnd = m.end()
            #print str(i-7)+'....'+replaceTxt+'...'
        text = result+text[lastEnd:]
    #outTest.write(text+'\n')
    return text

def GenRules():
    inRef = codecs.open('TCCprior','r',fileencoding)
    #outRef = codecs.open('./resource/TCCrules.full','w',fileencoding)

    for data in inRef.readlines():
        rule = data.rstrip()
        if(rule[0]!='#'):
            sptRule = rule.split(',')
            FullRule = ''
            for tmp in sptRule:
                if tmp == 'con':
                    FullRule = FullRule+'['+con_txt+']'+' +'
                elif tmp == 'vo1':
                    FullRule = FullRule+'['+vol1_txt+']'+' +'
                elif tmp == 'vo2':
                    FullRule = FullRule+'['+vol2_txt+']'+' +'
                elif tmp == 'vo3':
                    FullRule = FullRule+'['+vol3_txt+']'+' +'
                elif tmp == 'vo4':
                    FullRule = FullRule+'['+vol4_txt+']'+' +'
                elif tmp == 'ton':
                    FullRule = FullRule+'['+ton_txt+']'+' +'
                else:
                    FullRule = FullRule+tmp+' +'
            all_rules.append(FullRule[:-2])
            #outRef.write(FullRule[:-2]+'\n')
    all_rules.reverse()

#GenRules()
#for x in inTest.readlines():
#   print x
#   ApplyTCC(x)
