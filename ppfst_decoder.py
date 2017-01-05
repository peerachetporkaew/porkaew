#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Finite State Machine with Multiple Path Decoder
"""

__author__ = "Peerachet Porkaew"
__copyright__ = "Copyright 2010, Text Processing Team, Human Language Technology Laboratory, NECTEC, Thailand"
__credits__ = ["Peerachet Porkaew"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Peerachet Porkaew"
__email__ = "peerachet.porkaew@nectec.or.th"
__status__ = "Production"

class PPState:
    state_count = 0
	
    def __init__(self,name):
        self.next_state = {}
        self.state_name = name
        self.rule = "NULL"
        self.transfer = "NULL"
        self.state_count += 1
		
    def can_transition(self,input_data,condition):
        if input_data == condition:
            return True
        elif condition == "[x]":
            return True
        elif condition == "[x]+":
            return True
        else:
            return False
	
    def transition_rule(self,input_data):
        if self.next_state.has_key(input_data):
            return self.next_state[input_data]
        elif self.next_state.has_key("[x]"):
            return self.next_state["[x]"]
        else:
            return "NULL"
    
    def transition(self,input_data):
        key = self.next_state.keys()
        output = []
        #print key
        for condition in key:
            if self.can_transition(input_data,condition):
                #print "YIELD",input_data
                output += [[input_data,self.next_state[condition]]]
        output += [[input_data,"NULL"]]
        return output
    
    def add_transition(self,input_data, next_state):
        self.next_state[input_data] = next_state
    
    def can_move_next(self,input_data):
        key = self.next_state.keys()
        for i in key:
            if self.can_transition(input_data,i):
                return True
        return False
    
    def try_accept(self,input_data):
        inputL = input_data
        out = []
        current = self
        index = 0
        cur_input = inputL[index]
        found = 1
        while index < len(inputL) and found == 1:
            if current.can_move_next(inputL[index]):
                current = current.next_state[inputL[index]]
                if current.transfer != "NULL":
                    for i in current.transfer:
                        out += [[index+1,i]]
            else:
                found = 0
            index += 1
        return out
    
    def compile_transition(self,rule,transfer):
        rule_list = rule.split(" ")
        current_state = self
        last_state = self
        index = 0
        while(current_state != "NULL") and (index < len(rule_list)):
            last_state = current_state
            current_state = current_state.transition_rule(rule_list[index])
            index += 1
        if current_state != "NULL":
            last_state = current_state
            if last_state.transfer != "NULL":
                last_state.transfer += [transfer]
            else:
                last_state.transfer = [transfer]
            last_state.rule =rule
        else:
            #pass
            index -= 1
            if index < 0:
                index = 0
            if rule_list[index-1] == "[x]+":
                index -= 1
            for i in range(index,len(rule_list)):
                if rule_list[i] != "[x]+":
                    new_state = PPState(rule_list[i])
                    last_state.add_transition(rule_list[i],new_state)
                    last_state = new_state
                else:
                    last_state.add_transition("[x]",last_state)
            last_state.transfer = [transfer]
            last_state.rule = rule

def generate_score_table(token,L):
    table = [[]] * len(token)
    index = 0
    while index < len(token):
        #print token[index]
        out = L.try_accept(token[index:])
        if len(out) > 0:
            table[index] = out
            mini = 1000
            for i in table[index]:
                if i[0] < mini:
                    mini = i[0]
            index += 1
        else:
            table[index] = [[1,token[index]+" "]]
            index += 1
    return table

def generate_node(token,node):
    table = [[]] * len(token)
    index = 0
    while index < len(token):
        #print token[index]
        out = node.try_accept(token[index:])
        if len(out) > 0:
            table[index] = out
            mini = 1000
            for i in table[index]:
                if i[0] < mini:
                    mini = i[0]
            index += 1
        else:
            table[index] = [[1,token[index]+" "]]
            index += 1
    grow = []
    for i in table:
        grow += [max([k[0] for k in i])]
    
    segment = [0] * len(token)
    count = 1
    for i in range(len(table)):
        if segment[i] == 0:
            k = [j[0] for j in table[i]]
            m = max(k)
            #print m
            for j in range(i,i+m):
                segment[j] = count
            count += 1
    #print "Segment : "
    #print segment
    current = segment[0]
    next = segment[0] + grow[0] - 1
    #print "N:",next
    for i in range(len(segment)):
        #print 'nx:',i,next
        if i == next:
            current = segment[i]
            next = i+grow[i]
        else:
            segment[i] = current
            test = i+grow[i]
            if test > next:
                next = test
                #print i
                #print "N:",next
    
    #print "Segment New : "
    #print segment        
            
    sub = {}
    breakpoint = []
    for i in range(len(segment)):
        k = segment[i]
        if sub.has_key(k):
            sub[k] += [i]
        else:
            sub[k] = [i]
    breakpoint = []
    key = sub.keys()
    for i in sub.keys():
        if len(table[sub[i][0]]) == 1:
            breakpoint += [i]
    #print grow
    #print segment
    #print sub
    #print breakpoint
    
    breakpoint.sort()
    key = sub.keys()
    key.sort()
    
    map = {}
    resub = {}
    k = 1
    for i in key:
        resub[k] = sub[i]
        map[i] = k
        k += 1
    #print resub
    
    key = resub.keys()
    key.sort()
    bpIndex = 0
    last = 1
    slist = []
    for i in breakpoint:
        slist += [[min(resub[last]),max(resub[map[i]])]]
        last = map[i]
    slist += [[min(resub[last]),max(resub[key[-1]])]]
    return table,slist

def generate_all_path(table):
    stack = []
    output = []
    MAX = 100
    for i in range(len(table[0])):
        stack += [[i]]
    while len(stack) != 0:
        current = stack.pop()
        pointer = 0
        for i in current:
            pointer += table[pointer][i][0]
            while pointer < len(table) and len(table[pointer]) == 0 :
                pointer += 1
        if pointer >= len(table):
            output += [current]
        elif table[pointer] != []:
            for i in range(len(table[pointer])):
                k = current + [i]
                stack += [k]
        if len(output) > 100:
            return output
    return output

def generate_result(table,path):
    result = []
    for i in path:
        pointer = 0
        output = ""
        for j in i:
            if pointer < len(table) and j < len(table[pointer]):
                output += table[pointer][j][1]
                pointer += table[pointer][j][0]
            else:
                #print pointer,j
                pass
        result += [output.replace(" ","|")]
    return result

def calculate_score(inputStr,LM):
    table = generate_score_table(inputStr.split("|"),LM)
    #print table
    sum = 0.0
    for i in table:
        temp = []
        for j in i:
            if type(j[1]) == type(3.0):
                temp += [j[1]]
        if len(temp) > 0:
            sum += max(temp)
    return sum

def connect_output(str1,str2):
    if str2.strip() != "":        
        a = str2.split("|")
        a = a[0].split(" ")
        if a[0].strip() != "":
            sub = "".join(a[0][::-1])
            str3 = "".join(str1[::-1])
            f = str3.find(sub)
            if f != -1:
                return str1[0:-(f+len(sub))]+str2
            else:
                return str1 + str2
        else:
            return str1 + str2
    else:
        return str1

def connect_output_list(strList):
    output = ""
    for i in strList:
        output = connect_output(output,i)
    return output

def run_simple_decoder(inputStr,TM,LM):
    node = TM
    token = inputStr.split(" ")
    table,slist = generate_node(token,node)
    #print table
    print "SLIST",slist
    output = []
    for i in slist:
        print i
        A = table[i[0]:i[1]+1]
        path = generate_all_path(A)
        result = generate_result(A,path)
        max = -1
        selected = ""
        for i in result:
            score = calculate_score(i,LM)
            print "Score",i,score
            if score > max:
                max = score
                selected = i
        output += [selected]
    return connect_output_list(output)

def clean_output(inStr):
    output = inStr.replace("|"," ")
    output = output.strip()
    output = output.replace(" ","|")
    return output + "|"

if __name__ == "__main__":
    node = PPState("Initial")
    node.compile_transition("โ ค","โค|")
    node.compile_transition("ล ง","ลง|")
    node.compile_transition("โ ค ล ง","โคลง|")
    node.compile_transition("เ ร ื อ","เรือ|")
    
    LM = PPState("Initial Score")
    LM.compile_transition("ลง เรือ",4)
    
    token = "โ ค ล ง เ ร ื อ โ ค ล ง"
    output = run_simple_decoder(token,node,LM)
    print output
