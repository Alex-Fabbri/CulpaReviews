from flask import Flask, render_template, request
import nltk
import re
import urllib2
from bs4 import BeautifulSoup
import unicodedata
import pickle

'''
Get a dictionary of words from the reviews as well as the name of the professor from that webpage. 
'''
def split(url):
    html = urllib2.urlopen(url)
    raw = BeautifulSoup(html)
    rreviews = raw.find_all(class_="review_content")
    answer = []
    profline = raw.find('title')
    profname = profline.get_text()[8:]
    dict={}
    counter = 1
    for r in rreviews:
        review = r.get_text()
        tokenized_review = nltk.word_tokenize(review)
        for i in range(len(tokenized_review)):
            tokenized_review[i] = unicodedata.normalize('NFKD', tokenized_review[i]).encode('ascii','ignore')
        dict[counter] = tokenized_review
        counter+=1
    answer.append(dict)
    answer.append(profname)
    return answer

'''
Here we get a count of the number of reviews which are voted 'agree', 'disagree' and 'funny'.
'''
def getad(url):
    dt = {}
    furl = urllib2.urlopen(url)
    ct = 1
    a = None
    b = None
    c = None
    def toint(string):
        return(int(string[1:-1]))
    for line in furl:
        matcha=re.search(r'<input class="agree" type="submit" value="Agree ((\S+))" />+',line)
        matchd=re.search(r'<input class="disagree" type="submit" value="Disagree ((\S+))" />+',line)
        matchf=re.search(r'<input class="funny" type="submit" value="Funny ((\S+))" />+',line)
        if matcha != None:
            a = toint(matcha.group(1))
        if matchd != None:
            b = toint(matchd.group(1))
        if matchf != None:
            c = toint(matchf.group(1))
        if a != None and b != None and c != None:
            ls = [a,b,c]
            dt[ct]=ls
            ct = ct+1
            a = None
            b = None
            c = None
    return dt

'''
Based on the above agrees and disagrees as well as the number of positive and negative words we compute and ouput the results of the reviews. 
'''
def maj(getad,dt):
    answer = ""
    dic={}
    for i in getad.keys():
        if getad[i][0]>=getad[i][1]:
            dic[i] = dt[i]
        else:
            answer+="Review " + str(i) + " is discredited based on agree/disagree: " + str(getad[i][0]) + "/" +  str(getad[i][1]) + '<br />'           
    ind = pnident(dic)
    if ind[0]>ind[1]:
        answer+='<br />' + "There is a majority of Positive Reviews with Agreeable Reviews: " + str(ind[0]) + " over " + str(ind[1]) + '<br />'
    elif ind[0]<ind[1]:
        answer+='<br />'+ 'There is a majority of Negative Reviews with Agreeable Reviews: ' + str(ind[0]) + " over " + str(ind[1]) + '<br />'    
    else:
        answer+='<br />' + 'There is tie over Agreeable Reviews: ' +  str(ind[0]) + " vs " + str(ind[1])  + '<br />'
        ind = pnident(dt)
        if ind[0]>ind[1]:
            answer+='<br />' + 'There is a majority of Positive Reviews with All Reviews: ' +  str(ind[0]) + " vs " + str(ind[1])  + '<br />'
        elif ind[0]<ind[1]:
            answer+='<br />' + 'There is a majority of Negative Reviews with All Reviews: ' +  str(ind[0]) + " vs " + str(ind[1])  + '<br />'
        else:
            answer+='<br />' + 'Tie: ' + str(ind[0]) + " over " + str(ind[0]) + '<br />'
    return answer

'''The following help to deal with the dictionaries and lists. 
'''
def lstring(dt):
    ls = []
    for i in dt.keys():
        lines = ""
        for j in dt[i]:
            lines = lines + " " + j
        ls.append(lines)
    return ls
    
def fstring(dt):
    ls = []
    for i in dt.keys():
        for j in dt[i]:
            ls.append(j)
    lines = ""
    for i in ls:
        lines = lines + " " + i
    return lines

def getPB():
    posfile = open('positive.txt','r')
    negfile = open('negative.txt','r')
    posnegdict = {}
    for line in posfile:
        posnegdict[line.rstrip("\r\n")] = "positive"
    for line in negfile:
        posnegdict[line.rstrip("\r\n")] = "negative"
    return posnegdict
def getsum(dt,pb):
    dic = {}
    for i in dt.keys():
        pct = 0
        nct = 0
        wct = 0
        neg = False
        wct = 0
        neg = False
        for j in dt[i]:
            wct = wct + 1
            if j.lower()=="not" or j.lower()=="n't":
                neg = True
            if pb.has_key(j.lower()):
                if neg == False:
                    if pb[j.lower()] == "positive":
                        pct = pct + 1
                    elif pb[j.lower()] == "negative":
                        nct = nct + 1
                else:
                    if pb[j.lower()] == "positive":
                        nct = nct + 1
                    elif pb[j.lower()] == "negative":
                        pct = pct + 1
                neg = False
        dic[i]=[pct,nct,wct]
    return dic
'''
The following deals with the count of positive and negative words as well as the total word count. 
'''
def printsum(dtsum):
    answer = ""
    counter = 1
    for i in dtsum.keys():
        answer +=str(counter) + ' : Pos count: ' + str(dtsum[i][0]) + ". Neg count: " +  str(dtsum[i][1]) + ". total: " + str(dtsum[i][2]) + '<br />'
	counter +=1
    return answer
'''The following deals with the total number of positive and negative reviews. 
'''
def pnident(dic):
    pos = 0
    neg = 0
    tie = 0
    for i in dic.keys():
        if dic[i][0]>dic[i][1]:
            pos = pos + 1
        elif dic[i][0]<dic[i][1]:
            neg = neg + 1
        else:
            tie = tie + 1
    return [pos,neg,tie]
'''
This allows us to capture quotes with essential words. 
'''
def getSnippet(text, profName):
    answer = ""
    ls = []
    ls.append(re.findall(r"([^(.]*?easy[^.]*\.)",text))
    ls.append(re.findall(r"([^(.]*?difficult[^.]*\.)",text))
    ls.append(re.findall(r"([^(.]*?best[^.]*\.)",text))
    ls.append(re.findall(r"([^(.]*?worst[^.]*\.)",text))
    for sent in ls:
        if sent!=[]:
            answer += '"' + sent[0]+ '"' + '<br />'
    if len(answer) > 0:
        answer = profName + "!" + '<br />' + '<br />' + "Let's take a quote or two. " + '<br />' + answer
    else: 
	answer = profName + ":" 
    return answer

'''
What follows is the flask that incorporates the functions into the webpage. 
'''
app = Flask (__name__)
app.config["DEBUG"] = True

@app.route("/")
def home():
	return render_template("page.html")
		

@app.route("/results", methods=["GET","POST"])
def results():
	error = []
	if request.method == "POST":	
		pro = re.compile("(http://culpa.info/professors)")
		url = str(request.form["link"])
		testURL = pro.match(url)
		if (testURL is None):
			return render_template("results.html", final_result = "The horror! The horror! Was that a valid culpa url???")
		else:
			f = open('test.pickle')
			getPB2 = pickle.load(f)
			f.close()
			test = (printsum(getsum(split(url)[0],getPB2())))
			a = getsum(split(url)[0],getPB2())
			b = getad(url)
			test2 = maj(a,b)
				
			
			split1 = split(url)[0]
			fstring1 = fstring(split1)
			quotes = getSnippet(fstring1, split(url)[1])	
			return render_template("results.html", final_result= test, second_result = test2, prof_quotes = quotes)


@app.errorhandler(404)
def page_not_found(error):
	return "Sorry, page not found."

if __name__=="__main__":
	app.run(host="0.0.0.0")
