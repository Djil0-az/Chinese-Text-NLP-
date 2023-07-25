import csv
import time

start_time = time.time()
segmentFile = open("renmin.csv", "r",encoding='utf-8', errors='ignore')
segmentReader = csv.reader(segmentFile)
sendSegments = []
for item in segmentReader:
    sent = []
    for i in item:
        sent.append(i.strip())
    sendSegments.append(sent)

sum_zero = 0
for sent in sendSegments:
    if len(sent) == 0:
        sum_zero += 1
    print(sent)
print(sum_zero)


# unigram
def oneGram(sents: list):
    dic = {}
    dic['#始始#'] = 0
    dic['#末末#'] = 0
    for sent in sents:
        for item in sent:
            if item in dic:
                dic[item] = dic[item] + 1
            else:
                dic[item] = 1
        dic['#始始#'] += 1
        dic['#末末#'] += 1
    return dic


unigram = oneGram(sendSegments)


# print(unigram)


#bigram model
def bgram(sents: list):
    dic = {}
    dic["#始始#"] = dict()
    for sent in sents:
        for i in range(0, len(sent) - 1):
            if sent[i] not in dic:
                dic[sent[i]] = dict()
                dic[sent[i]][sent[i + 1]] = 1
            else:
                if sent[i + 1] in dic[sent[i]]:
                    dic[sent[i]][sent[i + 1]] += 1
                else:
                    dic[sent[i]][sent[i + 1]] = 1

        if sent[0] not in dic["#始始#"]:
            dic["#始始#"][sent[0]] = 1
        else:
            dic["#始始#"][sent[0]] += 1

        if sent[len(sent) - 1] not in dic:
            dic[sent[len(sent) - 1]] = dict()
            dic[sent[len(sent) - 1]]["#末末#"] = 1
        elif "#末末#" not in dic[sent[len(sent) - 1]]:
            dic[sent[len(sent) - 1]]["#末末#"] = 1
        else:
            dic[sent[len(sent) - 1]]["#末末#"] += 1
    return dic
#
#
biGram = bgram(sendSegments)


# print(biGram)


#
def selectUnigram(gram: dict, word):
    return gram[word]
#
#
def selectBigram(gram: dict, word_one, word_two):
    return gram[word_one][word_two]
#
#part of speech tagging
wordTypefile = open("renminPOS.csv", "r", encoding='utf-8', errors='ignore')
wordTypeReader = csv.reader(wordTypefile)
sendWordtype = []
for item in wordTypeReader:
    sent = []
    for i in item:
        sent.append(i.strip())
    sendWordtype.append(sent)
#
# # print(sents)

part = dict()
# count wordTypes
for sent in sendWordtype:
    for word in sent:
        word_part = word.split('/')[-1].split(']')[0].split('!')[0]
        if word_part in part:
            part[word_part] += 1
        else:
            part[word_part] = 1

partLength = len(part)
print(part, "total types：", partLength)
print("total frequency", sum(part.values()))

# transpose matrix
trans = dict()
for sent in sendWordtype:
    for i in range(len(sent) - 1):
        one = sent[i].split('/')[-1].split(']')[0].split('!')[0]
        two = sent[i + 1].split('/')[-1].split(']')[0].split('!')[0]
        if one in trans:
            if two in trans[one]:
                trans[one][two] += 1
            else:
                trans[one][two] = 1
        else:
            trans[one] = dict()
            trans[one][two] = 1
print(trans)

# word probability
percent = dict()
for sent in sendWordtype:
    for word in sent:
        word_word = word.split('/')[0].split('{')[0].strip('[')
        word_part = word.split('/')[-1].split(']')[0].split('!')[0]
        if word_word in percent:
            if word_part in percent[word_word]:
                percent[word_word][word_part] += 1
            else:
                percent[word_word][word_part] = 1
        else:
            percent[word_word] = dict()
            percent[word_word][word_part] = 1


# print(percent)

def segmentWord(text):
    # Generate unary grammar wordnets
    def generateWordnet(gram, text):
        net = [[] for _ in range(len(text) + 2)]
        for i in range(len(text)):
            for j in range(i + 1, len(text) + 1):
                word = text[i:j]
                if word in gram:
                    net[i + 1].append(word)
        i = 1
        while i < len(net) - 1:
            if len(net[i]) == 0:  # empty line
                j = i + 1

                for j in range(i + 1, len(net) - 1):
                    # search for non-empty line
                    if len(net[j]):
                        break
                # append empty line between i and j
                net[i].append(text[i - 1:j - 1])
                i = j
            else:
                i += len(net[i][-1])
        return net

    # test one sentence
    uniNet = generateWordnet(unigram, text)

    # print(uniNet)

    def calculateGramSum(gram: dict):
        num = 0
        for g in gram.keys():
            num += sum(gram[g].values())
        return num

    # wordTwo given wordOne chance，then add to gramsum
    def calculateWeight(gram: dict, wordOne, wordTwo, gramSum):
        if wordOne in gram:
            word_one_all = gram[wordOne].values()
            if wordTwo in gram[wordOne]:
                return (gram[wordOne][wordTwo] + 1) / (sum(word_one_all) + gramSum)
            else:
                return 1 / (sum(word_one_all) + gramSum)
        else:
            return 1 / gramSum

    biGramSum = calculateGramSum(biGram)

    # print(biGramSum)

    def viterbi(wordnet):
        dis = [dict() for _ in range(len(wordnet))]
        node = [dict() for _ in range(len(wordnet))]
        word_line = [dict() for _ in range(len(wordnet))]
        wordnet[len(wordnet) - 1].append("#末末#")
        # new line
        for word in wordnet[1]:
            dis[1][word] = calculateWeight(biGram, "#始始#", word, biGramSum)
            node[1][word] = 0
            word_line[1][word] = "#始始#"
        # each line in wordnet
        for i in range(1, len(wordnet) - 1):

            for word in wordnet[i]:
                #word distance and postion relative to other words
                for to in wordnet[i + len(word)]:
                    if word in dis[i]:
                        if to in dis[i + len(word)]:
                            # largest probability
                            if dis[i + len(word)][to] < dis[i][word] * calculateWeight(biGram, word, to, biGramSum):
                                dis[i + len(word)][to] = dis[i][word] * calculateWeight(biGram, word, to, biGramSum)
                                node[i + len(word)][to] = i
                                word_line[i + len(word)][to] = word
                        else:
                            dis[i + len(word)][to] = dis[i][word] * calculateWeight(biGram, word, to, biGramSum)
                            node[i + len(word)][to] = i
                            word_line[i + len(word)][to] = word

        # BackTrack Algo
        path = []
        f = node[len(node) - 1]["#末末#"]
        fword = word_line[len(word_line) - 1]["#末末#"]
        path.append(fword)
        while f:
            tmpword = fword
            fword = word_line[f][tmpword]
            f = node[f][tmpword]
            path.append(fword)
        path = path[:-1]
        path.reverse()
        return dis, node, word_line, path

    (dis, _, _, path) = viterbi(uniNet)
    # print(dis)
    # print(path)
    return path


def posTag(text):
    textPercent = []

    # words are already in renmin newspaper
    for word in text:
        wordPercent = percent[word]
        textPercent.append(wordPercent)

    # print(textPercent)

    #Use Viterbi find the best set
    dis = [dict() for _ in range(len(text))]
    node = [dict() for _ in range(len(text))]
    for first in textPercent[0].keys():
        dis[0][first] = 1
    for i in range(len(text) - 1):
        wordOne = text[i]
        wordTwo = text[i + 1]
        wordOnePercentDict = textPercent[i]
        wordTwoPercentDict = textPercent[i + 1]

        wordOnePercentKey = list(wordOnePercentDict.keys())
        wordOnePercentVal = list(wordOnePercentDict.values())
        wordTwoPercentKey = list(wordTwoPercentDict.keys())
        wordTwoPercentVal = list(wordTwoPercentDict.values())
        for wordTwoPer in wordTwoPercentKey:
            tempDistance = []
            for wordOnePer in wordOnePercentKey:
                if wordTwoPer in trans[wordOnePer]:
                    tempNum = dis[i][wordOnePer] * (
                            (trans[wordOnePer][wordTwoPer] + 1) / (part[wordOnePer] + partLength)) * (
                                      textPercent[i + 1][wordTwoPer] / part[wordTwoPer])
                    tempDistance.append(tempNum)
                else:
                    tempNum = dis[i][wordOnePer] * (1 / (part[wordOnePer] + partLength)) * (
                            textPercent[i + 1][wordTwoPer] / part[wordTwoPer])
                    tempDistance.append(tempNum)

            maxTempDistance = max(tempDistance)
            maxTempLocation = tempDistance.index(maxTempDistance)
            dis[i + 1][wordTwoPer] = maxTempDistance
            node[i + 1][wordTwoPer] = wordOnePercentKey[maxTempLocation]
    # print(dis, node)

    # find path according to the node
    path = []
    fvalue = list(dis[len(dis) - 1].values())
    fkey = list(dis[len(dis) - 1].keys())
    f = fkey[fvalue.index(max(fvalue))]

    path.append(f)
    for i in range(len(dis) - 1, 0, -1):
        f = node[i][f]
        path.append(f)
    path.reverse()
    return path


# Test All trained sets
test_file = open("renminPOS.csv", "r", encoding='utf-8', errors='ignore')
reader = csv.reader(test_file)
testSent = []
ansSent = []
sendSegments = []
for item in reader:
    test_sent = ""
    ans_sent = []
    sentSegs = []
    for word in item:
        word_word = word.split('/')[0].split('{')[0].strip('[')
        word_part = word.split('/')[-1].split(']')[0].split('!')[0]
        if word_word == '。' and word_word == '！' and word_word == '？':
            test_sent += word_word.strip()
            ans_sent.append(word_word)
            sentSegs.append(word_part)
            break
        else:
            test_sent += word_word.strip()
            ans_sent.append(word_word)
            sentSegs.append(word_part)
    testSent.append(test_sent)
    ansSent.append(ans_sent)
    sendSegments.append(sentSegs)


# put the segmented words into a list
def changeToElem(text: list):
    ans = []
    i = 1
    for word in text:
        ans.append([i, i + len(word) - 1])
        i += len(word)
    return ans


testSentNums = len(testSent)
print(testSentNums)
P = 0
R = 0
A = 0
A_num = 0
for i in range(testSentNums):
    trainingModel = segmentWord(testSent[i])
    trainingList = changeToElem(trainingModel)
    answerList = changeToElem(ansSent[i])

    trainingSet = set()
    for tmp in trainingList:
        trainingSet.add(tuple(tmp))

    ansListSet = set()
    for tmp in answerList:
        ansListSet.add(tuple(tmp))

    TP = ansListSet & trainingSet
    p = len(TP) / len(trainingList)
    r = len(TP) / len(answerList)
    #
    if ansListSet == trainingSet:
        A_num += 1
        # prediction
        wordTypeList = posTag(ansSent[i])
        # accurate
        wordTypeAns = sendSegments[i]
        a = 0
        for j in range(len(wordTypeList)):
            if wordTypeList[j] == wordTypeAns[j]:
                a += 1

        a = a / len(wordTypeList)
        A += a
    P += p
    R += r
    if i % 100 == 0:
        print(i / testSentNums)

# find the average
P = P / testSentNums
R = R / testSentNums
F_1 = 2 * P * R / (P + R)
print("P,R,F1", P, R, F_1)
A = A / A_num
print("A", A)
end_time = time.time()
print(end_time - start_time)