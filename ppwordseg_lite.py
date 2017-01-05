# -*- coding: utf-8 -*-
from ppfst_decoder import PPState,run_simple_decoder
import kenlm,sys

class Scorer:
	def __init__(self,model):
		self.model = kenlm.Model(model)

	def calculate_score(self,token):
		temp = " ".join(token[0:3])
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
			item[0] = item[0].decode("utf-8")
			left = " ".join([x for x in item[0]])
			left = left.encode("utf-8")
			if len(item[0]) > 1:
				self.TM.compile_transition(left,right)
			else:
				pass #print item[0]
		self.TM.compile_transition("_","_|")
		self.TM.compile_transition("บ ร ม","บรม|")
		self.TM.compile_transition("ไ ด ้","ได้|")
		self.TM.compile_transition("< / s >","</s>|")
		
		#Initializing Tri-gram LM Scorer
		self.scorer = Scorer(lm)
		
	def segment(self,text,beam_size=20):
		
		def look_ahead(depth,token,TM):
			if depth >= 0:
				if len(token) > 0:
					out = TM.try_accept(token)
					if len(out) == 0:
						out += [[1,token[0]+"|"]]
					for o in out:
						for y in look_ahead(depth-1,token[o[0]:],TM):
							if len(y) > 0:
								yield o[1] + y
							else:
								yield o[1]
			else:
				yield ""
		
		
		sentence = text.decode("utf-8")
		inp = " ".join([x for x in sentence]) + " ที่ _ _ _".decode("utf-8")
		inp = inp.encode("utf-8")
		inp = inp.split()
		
		start = 0
		output_token = []
		output = ""
		iteration = 0
		while start < len(inp)-4:
			#print "Iter",iteration,start,inp[start]
			iteration += 1
			stack = []
			for i,x in enumerate(look_ahead(3,inp[start:],self.TM)):
				if i > beam_size:
					break;
				if len(x) > 0:
					score = self.scorer.calculate_score(output_token[-2:] + x.split("|"))
					stack += [[x,score]]
			
			#Calculate Score
			max_score = -100000.0
			selected = ""
			#print "STACK"
			for s in stack:
				#print s[0],s[1]
				if s[1] > max_score:
					max_score = s[1]
					selected = s[0]
			selected = selected.split("|")[0]
			
			#print selected
			output += selected + " "
			output_token += [selected]
			
			#print "OUT",selected
			temp = selected.replace("|","").decode("utf-8")
			if len(temp) == 0:
				output += inp[start] + "@ "
				start += 1
				#self.TM.compile_transition(inp[start],inp[start]+"|")
				#raw_input()
			else:
				start += len(temp)
		return output

if __name__ == "__main__":
	model = Thai_WordSegmenter("wordlist.sort","best2010.txt.lm")
	#out = model.segment("ตกลง ลาก่อน")
	#print out
	#exit()
	
	fp = open(sys.argv[1],"r")
	fo = open(sys.argv[2],"w")
	
	line = fp.readline()
	i = 0
	while line:
		print i
		i += 1
		line = line.strip().replace(" ","")
		out = model.segment(line)
		fo.writelines(out+"\n")
		line = fp.readline()
	fo.close()
