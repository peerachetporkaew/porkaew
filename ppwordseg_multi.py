# -*- coding: utf-8 -*-
from ppfst_decoder import PPState,run_simple_decoder
import kenlm,re,sys
import TCCapply as TCCapply
from multiprocessing import Pool

TCCapply.GenRules()

def process_TCC(str1):
    text = str1.decode("utf-8")
    notSplit = re.compile(u'([^๐-๙0-9a-zA-Z])',re.UNICODE)
    notSplit2 = re.compile(u'([0-9๐-๙a-zA-Z]+)',re.UNICODE)
    text = notSplit2.sub('\g<0> ',text)
    text = notSplit.sub('\g<0> ',text)[:-1]
    TCCtext = TCCapply.ApplyTCC(text)
    return TCCtext

class Scorer:
	def __init__(self,model):
		self.model = kenlm.Model(model)

	def calculate_score(self,token):
		temp = " ".join(token)
		score = self.model.score(temp)
		#print temp,score
		return score

class Thai_WordSegmenter:
	def __init__(self,wordlist,lm):
		#Initializing word list...
		self.TM = PPState("TM")
		
		fp = open(wordlist,"r").readlines()
		for line in fp:
			item = line.split("\t")
			right = item[0] + "|"
			
			item[0] = process_TCC(item[0])
			
			#left = " ".join([x for x in item[0]])

			left = item[0]
			left = left.encode("utf-8")
			if len(item[0]) > 1:
				self.TM.compile_transition(left,right)
			else:
				pass #print item[0]
		
		self.TM.compile_transition("< / s >","</s>|")
		
		#Initializing Tri-gram LM Scorer
		self.scorer = Scorer(lm)
		
	def segment(self,text,beam_size=100):	
		hypo = []
		new_hypo = []
		output = []
		output_sort = {}

		live_k = 0
		
		sentence = process_TCC(text)
		inp = sentence
		inp = inp.encode("utf-8")
		inp = inp.split()
		
		hypo += [["",0]]
		live_k = beam_size

		while live_k > 0 and len(hypo) > 0:
			new_hypo = []
			score = {}
			for h in hypo:
				if h[1] == len(inp):
					live_k -= 1
					score_ = self.scorer.calculate_score(h[0].split("|"))
					output += [h + [score_]]
					output_sort[score_] = h + [score_]
					continue

				nexts = self.TM.try_accept(inp[h[1]:])
				if len(nexts) == 0:
					new_str = h[0] + inp[h[1]] + "|"
					s = self.scorer.calculate_score(new_str.split("|"))
					score[s] = [new_str,h[1] + 1]
				else:
					for next in nexts:
						new_str = h[0] + next[1]
						#new_hypo += [[new_str,h[1] + next[0]]]
						s = self.scorer.calculate_score(new_str.split("|"))
						score[s] = [new_str,h[1] + next[0]]

			#ranking new_hypo
			score_list = score.keys()
			score_list.sort()
			score_list = score_list[::-1] #reverse
			#print score_list
			for sc in score_list:
				new_hypo += [score[sc]]
			#print new_hypo
			hypo = new_hypo[0:live_k]
			#for h in hypo:
			#	print h[0]
			
				#print next
		olist = output_sort.keys()
		olist.sort()
		olist = olist[::-1]

		return output_sort[olist[0]]
   
model = Thai_WordSegmenter("wordlist.sort","best2010.txt.lm")

def process_segment(textStr):
	global model
	return model.segment(textStr.strip())[0].replace("|"," ").strip()


if __name__ == "__main__":
	fp = open(sys.argv[1],"r")
	fo = open(sys.argv[2],"w")
	
	line = fp.readlines()

	p = Pool(20)
	out = p.map(process_segment, line)

	for x in out:
		fo.writelines(x + "\n")

	fo.close()
