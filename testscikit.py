from numpy import *
from root_numpy import *
import sys
# used to shuffle multiple arrays at once

def argsortlist(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key = seq.__getitem__)

if len(sys.argv) < 2:
    print 'not enough arguments supplied, need argument for type of sample'
    sys.exit("not enough args supplied")

def roc_curve_rej(y_true, y_score, pos_label=None):
    """Compute Receiver operating characteristic (ROC)

    Note: this implementation is restricted to the binary classification task.

    Parameters
    ----------

    y_true : array, shape = [n_samples]
        True binary labels in range {0, 1} or {-1, 1}.  If labels are not
        binary, pos_label should be explictly given.

    y_score : array, shape = [n_samples]
        Target scores, can either be probability estimates of the positive
        class, confidence values, or binary decisions.

    pos_label : int
        Label considered as positive and others are considered negative.

    Returns
    -------
    fpr : array, shape = [>2]
        False Positive Rates.

    tpr : array, shape = [>2]
        True Positive Rates.

    thresholds : array, shape = [>2]
        Thresholds on ``y_score`` used to compute ``fpr`` and ``fpr``.

    Notes
    -----
    Since the thresholds are sorted from low to high values, they
    are reversed upon returning them to ensure they correspond to both ``fpr``
    and ``tpr``, which are sorted in reversed order during their calculation.

    References
    ----------
    http://en.wikipedia.org/wiki/Receiver_operating_characteristic

    Examples
    --------
    >>> import numpy as np
    >>> from sklearn import metrics
    >>> y = np.array([1, 1, 2, 2])
    >>> scores = np.array([0.1, 0.4, 0.35, 0.8])
    >>> fpr, tpr, thresholds = metrics.roc_curve(y, scores, pos_label=2)
    >>> fpr
    array([ 0. ,  0.5,  0.5,  1. ])

    """
    y_true = ravel(y_true)
    y_score = ravel(y_score)
    classes = unique(y_true)

    # ROC only for binary classification if pos_label not given
    if (pos_label is None and
        not (all(classes == [0, 1]) or
             all(classes == [-1, 1]) or
             all(classes == [0]) or
             all(classes == [-1]) or
             all(classes == [1]))):
        raise ValueError("ROC is defined for binary classification only or "
                         "pos_label should be explicitly given")
    elif pos_label is None:
        pos_label = 1.

    # y_true will be transformed into a boolean vector
    y_true = (y_true == pos_label)
    n_pos = float(y_true.sum())
    n_neg = y_true.shape[0] - n_pos
    '''
    if n_pos == 0:
        warnings.warn("No positive samples in y_true, "
                      "true positve value should be meaningless")
        n_pos = nan
    if n_neg == 0:
        warnings.warn("No negative samples in y_true, "
                      "false positve value should be meaningless")
        n_neg = nan
    '''
    thresholds = unique(y_score)
    neg_value, pos_value = False, True

    tpr = empty(thresholds.size, dtype=float)  # True positive rate
    tnr = empty(thresholds.size, dtype=float)  # True negative rate
    fpr = empty(thresholds.size, dtype=float)  # False positive rate
    fnr = empty(thresholds.size, dtype=float)  # False negative rate
    rej = empty(thresholds.size, dtype=float)  # Bkg rejection rate
    # Build tpr/fpr vector
    current_pos_count = current_neg_count = sum_pos = sum_neg = idx = 0

    signal = c_[y_score, y_true]
    sorted_signal = signal[signal[:, 0].argsort(), :][::-1]
    last_score = sorted_signal[0][0]
    for score, value in sorted_signal:
        if score == last_score:
            if value == pos_value:
                current_pos_count += 1
            else:
                current_neg_count += 1
        else:
            tpr[idx] = (sum_pos + current_pos_count) / n_pos
            #tnr[idx] = (sum_neg + current_pos_count) / n_neg
            fpr[idx] = (sum_neg + current_neg_count) / n_neg
            #fnr[idx] = (sum_neg + current_neg_count) / n_pos
            rej[idx] = 1 - fpr[idx]
            sum_pos += current_pos_count
            sum_neg += current_neg_count
            current_pos_count = 1 if value == pos_value else 0
            current_neg_count = 1 if value == neg_value else 0
            idx += 1
            last_score = score
    else:
        tpr[-1] = (sum_pos + current_pos_count) / n_pos
        fpr[-1] = (sum_neg + current_neg_count) / n_neg
        rej[-1] = 1 - ((sum_neg + current_neg_count) / n_neg)

    # hard decisions, add (0,0)
    if fpr.shape[0] == 2:
        fpr = array([0.0, fpr[0], fpr[1]])
        tpr = array([0.0, tpr[0], tpr[1]])
        rej = array([0.0, rej[0], rej[1]])
    # trivial decisions, add (0,0) and (1,1)
    elif fpr.shape[0] == 1:
        fpr = array([0.0, fpr[0], 1.0])
        tpr = array([0.0, tpr[0], 1.0])
        rej = array([0.0, rej[0], 1.0])

    if n_pos is nan:
        tpr[0] = nan

    if n_neg is nan:
        fpr[0] = nan
        rej[0] = nan

    return fpr, tpr, thresholds[::-1], rej

def readInLabels(fname):
    f = open('Labels.txt')#+fname+'.txt')
    labelcodes = []
    labelcodesNum = []
    for line in f:
        l = line.split(',')
        labelcodes.append(l[0])
        labelcodesNum.append(int(l[1]))
    f.close()
    labelcodesNum,labelcodes = zip(*sorted(zip(labelcodesNum,labelcodes)))
    print labelcodes
    return labelcodes

def readInNames(fname):
    f = open('Names.txt')
    namecodes = []
    namecodesNum = []
    for line in f:
        l = line.split(',')
        namecodes.append(l[0])
        namecodesNum.append(int(l[1]))
    f.close()
    namecodesNum,namecodes = zip(*sorted(zip(namecodesNum,namecodes)))
    return namecodes

def sortMultiple(ind, arr1, arr2, arr3 = []):
    if len(arr1) > len(arr2):
        return -1
    for x in xrange(1,len(arr1)-1):
        val = arr1[ind][x]
        val2 = arr2[ind][x]
        if not arr3 == []:
            val3 = arr3[ind][x]
        hole = x
        while hole > 0 and val < arr[ind][hole-1]:
            arr1[ind][hole] = arr1[ind][hole-1]
            arr2[ind][hole] = arr2[ind][hole-1]
            if not arr3 == []:
                arr3[ind][hole] = arr3[ind][hole-1]
            hole -= 1
        arr1[hole] = val
        arr2[hole] = val2
        arr3[hole] = val3
        
    return arr1,arr2,arr3


def shuffle_in_unison(a, b, c):
    assert len(a) == len(b)
    shuffled_a = empty(a.shape, dtype=a.dtype)
    shuffled_b = empty(b.shape, dtype=b.dtype)
    shuffled_c = empty(c.shape, dtype=c.dtype)
    permutation = random.permutation(len(a))
    for old_index, new_index in enumerate(permutation):
        shuffled_a[new_index] = a[old_index]
        shuffled_b[new_index] = b[old_index]
        shuffled_c[new_index] = c[old_index]
    return shuffled_a, shuffled_b, shuffled_c

# return a part of the array
def cutTree(arr, training, pos, evNum, sampleVersion = 'Any' ):
    lenarr = len(arr)


    if pos > lenarr:
        pos = lenarr-1
    if training == True:
        print 'true'
        if (sampleVersion == 'Any'):
            return arr[:pos]
        elif (sampleVersion == 'A'):
            return evenArr(arr, evNum)
        elif sampleVersion == 'B':
            return oddArr(arr, evNum)

    else:
        print 'false'
        if (sampleVersion == 'Any'):
            return arr[lenarr-pos:]
        elif (sampleVersion == 'A'):
            return evenArr(arr, evNum)
        elif sampleVersion == 'B':
            return oddArr(arr, evNum)

def evenArr(arr, evNum):
    tempArr = []
    counter = 0
    for x in arr:
        if x %2 == 0:
            tempArr.append(x)
        counter += 1
    return array(tempArr)
def oddArr(arr, evNum):
    tempArr = []
    counter = 0
    for x in arr:
        if x[evNum] %2 == 1:
            tempArr.append(x)
        counter += 1
    return array(tempArr)


# take out only the variables we want to train on
# if sampleVersion = A, only use even EventNumbers, B odd
def cutCols(arr, varIdx, rows, cols, varWIdx, nEntries, lumi, calcWeightPerSample = False, labels = []):
    rowcount = 0
    #initialise a basic numpy array that we will return
    outarr = ones((int(rows),int(cols)))
    outweights = []
    outlabels = []
    weightsPerSample = {}
    for row in arr:
        colcount = 0
        for col in varIdx:
            outarr[rowcount][colcount] = row[col]
            colcount = colcount + 1
        rowcount = rowcount + 1
        weight = float(row[int(varWIdx['final_xs'])]*lumi/nEntries)
        outweights.append(weight)
        key = row[int(varWIdx['label_code'])]
        outlabels.append(int(key))
        # there is a better way to do this, need to do it once, rather than many times since it'll be the same
        
        if calcWeightPerSample and (str(key) not in weightsPerSample):
            weightsPerSample[labels[int(row[int(varWIdx['label_code'])])]] = weight
        if (int(row[int(varWIdx['label_code'])]) > 0):
            print 'not 0!!!!!!'
            print row[int(varWIdx['label_code'])]
    if calcWeightsPerSample:
        return outarr, array(outweights), array(outlabels), weightsPerSample
    else:
        return outarr, array(outweights), array(outlabels)

def onesInt(length):
    arr = []
    for i in xrange(0,length):
        arr.append(1)
    return arr

def zerosInt(length):
    arr = []
    for i in xrange(0,length):
        arr.append(0)
    return arr

# set the weights for training
def setWeights(length, weight):
    weights = []
    for i in xrange(0,length):
        weights.append(weight)
    return weights

# convert to numpy arrays, then randomise
#sig = root2array('BonnTMVATrainingSample_ZH125.root','TrainTree')
from tempfile import TemporaryFile

npyFileExists = False
try:
   with open('./Ntuplesignal.npy'): pass
   #close('./Ntuplesignal.npy')
   npyFileExists = True
except IOError:
   print 'Oh dear.'

if npyFileExists:
    sig = load('./Ntuplesignal.npy')
else:
    sig = root2array('./Ntuplesignal.root','Ntuple')
    #save('./Ntuplesignal.npy',sig)
print 'len of sig: ' + str(len(sig))
#random.shuffle(sig)
#bkg = root2array('BonnTMVATrainingSample_ttbar.root','TrainTree')
npyBkgFileExists = False
try:
   with open('./Ntuplebkg.npy'): pass
   #close('./Ntuplebkg.npy')
   npyBkgFileExists = True
except IOError:
   print 'Oh dear.'

if npyBkgFileExists:
    bkg = load('./Ntuplebkg.npy')
else:
    bkg = root2array('./Ntuplebkg.root','Ntuple')
    #save('./Ntuplebkg.npy',bkg)
#random.shuffle(bkg)
print 'len of bkg: ' + str(len(bkg))

#cut in half for training and testing, remove unwanted variables not for training
#sigtemp = cutTree(sig,True,len(sig)/2)
sigtempA = cutTree(sig,True,len(sig)/2,'A')
sigtempB = cutTree(sig,True,len(sig)/2,'B')
#print len(sigtemp)
#bkgtemp = cutTree(bkg,True,len(bkg)/2)
bkgtempA = cutTree(bkg,True,len(bkg)/2,'A')
bkgtempB = cutTree(bkg,True,len(bkg)/2,'B')
#print len(bkgtemp)
#keep indices of variables we want
varIdx = []
varWIdx = []
#variableNames = ['m_ll','m_Bb','MET','dPhi_VH', 'ptImbalanceSignificance', 'pt_V', 'pt_Bb', 'dR_Bb', 'acop_Bb', 'dEta_Bb', 'mv1_jet0', 'mv1_jet1']
variableNames = ['dRBB','dEtaBB','dPhiVBB','dPhiLMET','dPhiLBMin','pTV','mBB','HT','pTB1','pTB2','pTimbVH','mTW','pTL','MET']#,'mLL']
varWeightsHash = {'xs':-1,'xscorr1':-1,'xscorr2':-1,'final_xs':-1,'label':-1,'label_code':-1,'name':-1,'name_code':-1}
foundVariables = []


xcount = 0
evNum = 0
#store the variables we find and their indices
for x in sig.dtype.names:
    if x in variableNames:
        varIdx.append(xcount)
        foundVariables.append(x)
    if x in varWeightsHash.keys():
        varWeightsHash[x]= xcount
    if x == 'EventNumber':
        evNum = xcount
    xcount = xcount + 1


#print sig.dtype.names
#print varIdx
#print foundVariables
#create the training trees/ arrays
nEntries = 14443742.0
lumi = 20300.0

sigTrainA,weightsSigTrainA, labelsSigTrainA = cutCols(sigtempA, varIdx, len(sigtempA), len(variableNames), varWeightsHash, nEntries, lumi)
bkgTrainA,weightsBkgTrainA, labelsBkgTrainA = cutCols(bkgtempA, varIdx, len(bkgtempA), len(variableNames), varWeightsHash, nEntries, lumi)
sigTrainB,weightsSigTrainB, labelsSigTrainB = cutCols(sigtempB, varIdx, len(sigtempB), len(variableNames), varWeightsHash, nEntries, lumi)
bkgTrainB,weightsBkgTrainB, labelsBkgTrainB = cutCols(bkgtempB, varIdx, len(bkgtempB), len(variableNames), varWeightsHash, nEntries, lumi)

#add the training trees together, keeping track of which entries are signal and background
xtA = vstack((sigTrainA, bkgTrainA))
y11A = onesInt(len(sigTrainA))
y21A = zerosInt(len(bkgTrainA))
ytA = hstack((y11A, y21A))
ytA = transpose(ytA)
sigWeightA = 1.0#float(1/float(len(sigTrain)))
print 'sigWeight ' + str(sigWeightA)
bkgWeightA = float(len(sigTrainA))/float(len(bkgTrainA))
print 'bkgWeight ' + str(bkgWeightA)
weightsBkgA = setWeights(len(bkgTrainA),bkgWeightA)
weightsSigA = setWeights(len(sigTrainA),sigWeightA)
weightstA = hstack((weightsSigA,weightsBkgA))
weightstA = transpose(weightstA)

#add the training trees together, keeping track of which entries are signal and background
xtB = vstack((sigTrainB, bkgTrainB))
y11B = onesInt(len(sigTrainB))
y21B = zerosInt(len(bkgTrainB))
ytB = hstack((y11B, y21B))
ytB = transpose(ytB)
sigWeightB = 1.0#float(1/float(len(sigTrain)))
print 'sigWeight ' + str(sigWeightB)
bkgWeightB = float(len(sigTrainB))/float(len(bkgTrainB))
print 'bkgWeight ' + str(bkgWeightB)
weightsBkgB = setWeights(len(bkgTrainB),bkgWeightB)
weightsSigB = setWeights(len(sigTrainB),sigWeightB)
weightstB = hstack((weightsSigB,weightsBkgB))
weightstB = transpose(weightstB)

x =xtA
y = ytA
weights = weightstA
#x,y,weights = shuffle_in_unison(xt,yt,weightst)

#print 'starting training on GradientBoostingClassifier'

from sklearn.ensemble import GradientBoostingClassifier

# parameters for boosting:
# GradientBoostingClassifier(loss='deviance', learning_rate=0.10000000000000001, n_estimators=100, subsample=1.0, min_samples_split=2, min_samples_leaf=1, max_depth=3, init=None, random_state=None, max_features=None, verbose=0)

#gb = GradientBoostingClassifier().fit(x,y)

#Test the fit on the other half of the data
sigtemp1A = cutTree(sig,False,len(sig)/2,'A')
bkgtemp1A = cutTree(bkg,False,len(bkg)/2,'A')

print sigtemp1A
labelCodes = readInLabels(sys.argv[1])#typeOfSample should be signal or bkg
#find weightsPerSample on first run
sigTestA, weightsSigTestA, labelsSigTestA, weightsPerSample = cutCols(sigtemp1A, varIdx, len(sigtemp1A), len(variableNames), varWeightsHash, nEntries, lumi, True, labelCodes)
sortPerm = labelsSigTestA.argsort()
#t_labelsSigTestA, t_sigTestA, t_weightsSigTestA = zip(*sorted(zip(labelsSigTestA,sigTestA,weightsSigTestA)))
sigTestA= sigTestA[sortPerm]#list(t_sigTestA)
weightsSigTestA = weightsSigTestA[sortPerm]#list(t_weightsSigTestA)
labelsSigTestA= labelsSigTestA[sortPerm]#list(t_labelsSigTestA)

#labelsSigTestA, sigTestA, weightsSigTestA = sortMultiple(varWIdx['label_code'],labelsSigtestA,sigTestA,weightsSigTestA)
bkgTestA, weightsBkgTestA, labelsBkgTestA = cutCols(bkgtemp1A, varIdx, len(bkgtemp1A), len(variableNames), varWeightsHash, nEntries, lumi)
sortPermBkg = labelsBkgTestA.argsort()
#t_labelsBkgTestA, t_bkgTestA, t_weightsBkgTestA = zip(*sorted(zip(labelsBkgTestA,bkgTestA,weightsBkgTestA)))
bkgTestA= bkgTestA[sortPermBkg]#list(t_bkgTestA)
weightsBkgTestA = weightsBkgTestA[sortPermBkg]#list(t_weightsBkgTestA)
labelsBkgTestA= labelsBkgTestA[sortPermBkg]#list(t_labelsBkgTestA)



x1A = vstack((sigTestA, bkgTestA))
y1A = hstack((onesInt(len(sigTestA)), zerosInt(len(bkgTestA))))
y1A = transpose(y1A)


from rootpy.interactive import wait
from rootpy.plotting import Canvas, Hist, Hist2D, Hist3D, Legend
from rootpy.io import root_open as ropen, DoesNotExist
from rootpy.plotting import HistStack
import ROOT
ROOT.gROOT.SetBatch(True)
  
f = ropen('output.root','recreate')
c1 = Canvas()
c1.cd()

histDictSigA = {'W':[],'Z':[],'WW':[],'ZZ':[],'st':[],'ttbar':[],'WZ':[],'WH125':[]}
histDictBkgA = {'W':[],'Z':[],'WW':[],'ZZ':[],'st':[],'ttbar':[],'WZ':[],'WH125':[]}


coloursForStack = ['blue', 'green', 'red', 'yellow', 'black', 'pink', 'magenta', 'cyan']
colourDict = {'W':0,'Z':1,'WW':2,'ZZ':3,'st':4,'ttbar':5,'WZ':6,'WH125':7}

lblcount = 0

sigTestA = transpose(sigTestA)
bkgTestA = transpose(bkgTestA)

sigtemp1B = cutTree(sig,False,len(sig)/2,'B')
bkgtemp1B = cutTree(bkg,False,len(bkg)/2,'B')

sigTestB, weightsSigTestB, labelsSigTestB = cutCols(sigtemp1B, varIdx, len(sigtemp1B), len(variableNames), varWeightsHash, nEntries, lumi)
sortPermB = labelsSigTestB.argsort()
#t_labelsSigTestB, t_sigTestB, t_weightsSigTestB = zip(*sorted(zip(labelsSigTestB,sigTestB,weightsSigTestB)))
sigTestB= sigTestB[sortPermB]#list(t_sigTestB)
weightsSigTestB = weightsSigTestB[sortPermB]#list(t_weightsSigTestB)
labelsSigTestB= labelsSigTestB[sortPermB]#list(t_labelsSigTestB)

bkgTestB, weightsBkgTestB, labelsBkgTestB = cutCols(bkgtemp1B, varIdx, len(bkgtemp1B), len(variableNames), varWeightsHash, nEntries, lumi)
sortPermBkgB = labelsBkgTestB.argsort()
#t_labelsBkgTestB, t_bkgTestB, t_weightsBkgTestB = zip(*sorted(zip(labelsBkgTestB,bkgTestB,weightsBkgTestB)))
bkgTestB= bkgTestB[sortPermBkgB]#list(t_bkgTestB)
weightsBkgTestB = weightsBkgTestB[sortPermBkgB]#list(t_weightsBkgTestB)
labelsBkgTestB= labelsBkgTestB[sortPermB]#list(t_labelsBkgTestB)



x1B = vstack((sigTestB, bkgTestB))
y1B = hstack((onesInt(len(sigTestB)), zerosInt(len(bkgTestB))))
y1B = transpose(y1B)
print 'starting testing'

sigTestB = transpose(sigTestB)
bkgTestB = transpose(bkgTestB)


count = 0
cols = []
for i in variableNames:
    cols.append(ones(len(sigTestA)))

hist = []
histidx = 0
hist2 = []
hist2idx = 0
histstack = []
histstack2 = []
maxi = []
mini = []




#nameCodes = readInCodes(typeOfSample)
#print 'labelsSigTestA'
#print labelsSigTestA
log = open('log.txt','w')
log.write('############################# Signal #############################\n')

#TODO: need to write generic method to do the loop of sigTestA and bkgTestA, will need to do it over B sets too
legendsForSigStack = {}

for c in sigTestA:
    maxi.append(c[argmax(c)])
    mini.append(c[argmin(c)])
    hist.append(Hist(20,mini[histidx],maxi[histidx]))
    hist[histidx].fill_array(c)


    hist[histidx].scale(1.0/hist[histidx].integral())

    hist[histidx].fillcolor='blue'
    hist[histidx].linecolor='blue'

    hist[histidx].GetXaxis().SetTitle(foundVariables[histidx])
    hist[histidx].GetYaxis().SetTitle('# Events Normalised to 1')
    hist[histidx].SetTitle("signal")
    hist[histidx].fillstyle='solid'
    lblcount = 0
    for k in histDictSigA.keys():
        histDictSigA[k].append(Hist(20,mini[histidx],maxi[histidx]))
        histDictSigA[k][histidx].fillcolor = coloursForStack[int(colourDict[k])]
        histDictSigA[k][histidx].fillstyle = 'solid'
        histDictSigA[k][histidx].SetOption('hist')
        histDictSigA[k][histidx].SetTitle(k)
    for i in c:
        lbl = labelCodes[int(labelsSigTestA[lblcount])]
        #if len(histDictSigA[lbl]) >= histidx and histDictSigA[lbl][histidx] == []:
        # weight i
        weighted_i = i#*weightsSigTestA[lblcount]
        histDictSigA[lbl][histidx].fill(weighted_i)
        lblcount += 1
        #log.write(lbl + '['+str(histidx)+']: '+str(weighted_i)+'\n')
    
    histidx+=1

#testAStack = {'W':HistStack('Wtest','Wstack'),'Z':HistStack('Ztest','Zstack'),'WW':HistStack('WWtest','WWstack'),'ZZ':HistStack('ZZtest','ZZstack'),'st':HistStack('sttest','ststack'),'ttbar':HistStack('ttbartest','ttbarstack'),'WZ':HistStack('WZtest','WZstack'),'WH125':HistStack('WH125test','WH125stack')}
testAStack = []#HistStack('dRBB','dRBB'),HistStack('dEtaBB','dEtaBB'),HistStack('dPhiVBB','dPhiVBB'),HistStack('dPhiLMET','dPhiLMET'),HistStack('dPhiLBMin','dPhiLBMin'),HistStack('pTV','pTV'),HistStack('mBB','mBB'),HistStack('HT','HT'),HistStack('pTB1','pTB1'),HistSTack('pTB2','pTB2'),HistStack('pTimbVH','pTimbVH'),HistStack('mTW','mTW'),HistStack('pTL','pTL'),HistStack('MET','MET')]#,'mLL']
allStack = []
legendSigStack = []
legendAllStack = []
for st in foundVariables:
    testAStack.append(HistStack(st,st))
    allStack.append(HistStack(st,st))
    legendSigStack.append(Legend(7))
    legendAllStack.append(Legend(7))

for rw in histDictSigA.keys():
    log.write(rw + ' length: '+str(len(histDictSigA[rw]))+'\n')
    for rwcount in xrange(0,len(histDictSigA[rw])):
        if histDictSigA[rw][rwcount].GetEntries() > 0:
            histDictSigA[rw][rwcount].scale(weightsPerSample[rw])
            testAStack[rwcount].Add(histDictSigA[rw][rwcount])
            allStack[rwcount].Add(histDictSigA[rw][rwcount])
            histDictSigA[rw][rwcount].draw('hist')
            legendSigStack[rwcount].AddEntry( histDictSigA[rw][rwcount], 'F')
            legendAllStack[rwcount].AddEntry( histDictSigA[rw][rwcount], 'F')
            c1.SaveAs("histDictSigA"+str(rwcount)+".png")
            log.write(rw + '['+str(rwcount)+'] entries: ' + str(histDictSigA[rw][rwcount].GetEntries())+'\n')
#testABkgStack = HistStack('bkgtest','bkgstack')
log.write('########################### Background ###########################\n')
for d in bkgTestA:
    maxi2 = argmax(d)
    mini2 = argmin(d)

    hist2.append(Hist(20,mini[hist2idx],maxi[hist2idx]))
    hist2[hist2idx].fill_array(d)
    hist2[hist2idx].scale(1.0/hist2[hist2idx].integral())
    hist2[hist2idx].GetXaxis().SetTitle(foundVariables[hist2idx])
    hist2[hist2idx].GetYaxis().SetTitle('# Events Normalised to 1')
    hist2[hist2idx].fillcolor='red'
    hist2[hist2idx].fillstyle='/'
    hist2[hist2idx].linecolor='red'
    hist2[hist2idx].SetTitle("bkg")


    #hist[histidx].GetYaxis().SetRangeUser(0.0,1.2*max(hist[hist2idx].GetBinContent(hist[hist2idx].GetMaximumBin()),hist2[hist2idx].GetBinContent(hist2[hist2idx].GetMaximumBin())   ))
    hist[hist2idx].draw('hist')
    hist[hist2idx].Write()
    legend = Legend(2)
    legend.AddEntry(hist[hist2idx],'F')
    legend.AddEntry(hist2[hist2idx],'F')
#    hist[histidx].
    hist2[hist2idx].draw('histsame')
    hist2[hist2idx].Write()
    legend.Draw('same')
    c1.Write()
    c1.SaveAs(foundVariables[hist2idx]+".png")

    for k in histDictBkgA.keys():
        histDictBkgA[k].append(Hist(20,mini[hist2idx],maxi[hist2idx]))
        histDictBkgA[k][hist2idx].fillcolor = coloursForStack[int(colourDict[k])]
        histDictBkgA[k][hist2idx].fillstyle = 'solid'
        histDictBkgA[k][hist2idx].SetOption('hist')
        histDictBkgA[k][hist2idx].SetTitle(k)
    lblcount = 0
    for i in d:
        lbl = labelCodes[int(labelsBkgTestA[lblcount])]
        #if len(histDictBkgA[lbl]) >= hist2idx and histDictBkgA[lbl][hist2idx] == []:
        #weight 
        weighted_i = i*weightsBkgTestA[lblcount]
        histDictBkgA[lbl][hist2idx].fill(weighted_i)
        lblcount += 1
        #log.write(lbl + '['+str(histidx)+']: '+str(weighted_i)+'\n')


    hist2idx += 1

testAStackBkg = []#HistStack('dRBB','dRBB'),HistStack('dEtaBB','dEtaBB'),HistStack('dPhiVBB','dPhiVBB'),HistStack('dPhiLMET','dPhiLMET'),HistStack('dPhiLBMin','dPhiLBMin'),HistStack('pTV','pTV'),HistStack('mBB','mBB'),HistStack('HT','HT'),HistStack('pTB1','pTB1'),HistSTack('pTB2','pTB2'),HistStack('pTimbVH','pTimbVH'),HistStack('mTW','mTW'),HistStack('pTL','pTL'),HistStack('MET','MET')]#,'mLL']
legendBkgStack = []
for st in foundVariables:
    testAStackBkg.append(HistStack(st,st))
    legendBkgStack.append(Legend(7))


for rw in histDictBkgA.keys():
    log.write(rw + ' length: '+str(len(histDictBkgA[rw]))+'\n')
    for rwcount in xrange(0,len(histDictBkgA[rw])):
        if histDictBkgA[rw][rwcount].GetEntries() > 0:
            histDictBkgA[rw][rwcount].scale(weightsPerSample[rw])
            testAStackBkg[rwcount].Add(histDictBkgA[rw][rwcount])
            allStack[rwcount].Add(histDictBkgA[rw][rwcount])
            legendBkgStack[rwcount].AddEntry(histDictBkgA[rw][rwcount], 'F')
            histDictBkgA[rw][rwcount].draw('hist')
            c1.SaveAs("histDictBkgA"+str(rwcount)+".png")
            log.write(rw + '['+str(rwcount)+'] entries: ' + str(histDictBkgA[rw][rwcount].GetEntries())+'\n')
log.close()
c2 = Canvas()
c2.cd()
xcount = 0
for x in testAStack:
    x.Draw('hist')
    legendSigStack[xcount].Draw('same')
    x.Write()
    c2.SaveAs(foundVariables[xcount]+'SigStack.png')
    c2.Write()
    xcount +=1 
xcount = 0
for x in testAStackBkg:
    x.Draw('hist')
    legendBkgStack[xcount].Draw('same')
    x.Write()
    c2.SaveAs(foundVariables[xcount]+'BkgStack.png')
    c2.Write()
    xcount+=1

xcount = 0
for x in allStack:
    x.Draw('hist')
    legendAllStack[xcount].Draw('same')
    x.Write()
    c2.SaveAs(foundVariables[xcount]+'AllStack.png')
    c2.Write()
    xcount+=1


f.close()
#testABkgStack.draw()

hist = []
hist2 = []
#score = gb.score(x1,y1)

#print score

from sklearn.tree import DecisionTreeClassifier



print 'starting training on AdaBoostClassifier'
#class sklearn.tree.DecisionTreeClassifier(criterion='gini', max_depth=None, min_samples_split=2, min_samples_leaf=1, min_density=0.10000000000000001, max_features=None, compute_importances=False, random_state=None)
'''

from sklearn.ensemble import AdaBoostClassifier
from time import clock
# Build a forest and compute the feature importances
ada = AdaBoostClassifier(DecisionTreeClassifier(compute_importances=True,max_depth=4,min_samples_split=2,min_samples_leaf=100),n_estimators=400, learning_rate=0.5, algorithm="SAMME",compute_importances=True)
start = clock()
ada.fit(xtA, ytA)
elapsed = clock()-start
print 'time taken for training: ' + str(elapsed)
importancesada = ada.feature_importances_
print importancesada
#print ada.score(x1,y1)
print ada.get_params()
std = std([tree.feature_importances_ for tree in ada.estimators_],
             axis=0)
indicesada = argsort(importancesada)[::-1]
variableNamesSorted = []
for i in indicesada:
    variableNamesSorted.append(foundVariables[i])

# Print the feature ranking
print "Feature ranking:"

for f in xrange(12):
    print "%d. feature %d (%f)" % (f + 1, indicesada[f], importancesada[indicesada[f]]) + " " +variableNamesSorted[f]


# Plot the feature importances of the forest
# We need this to run in batch because it complains about not being able to open display
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import matplotlib.pyplot as plt
from pylab import * 

import pylab as pl

pl.figure()
pl.title("Feature importances Ada")
pl.bar(xrange(len(variableNames)), importancesada[indicesada],
       color="r", yerr=std[indicesada], align="center")
pl.xticks(xrange(12), variableNamesSorted)#indicesada)
pl.xlim([-1, 12])
pl.show()

plot_colors = "rb"
plot_step = 1000.0
class_names = "AB"


pl.figure(figsize=(15, 5))
'''
'''
# Plot the decision boundaries
pl.subplot(131)
x_min, x_max = x[:, 0].min() - 1, x[:, 0].max() + 1
y_min, y_max = x[:, 1].min() - 1, x[:, 1].max() + 1
print 'xmin ' + str(x_min)
print 'xmax ' + str(x_max)
print 'ymin ' + str(y_min)
print 'ymax ' + str(y_max)
xx, yy = meshgrid(arange(x_min, x_max, plot_step),
                     arange(y_min, y_max, plot_step))

Z = ada.predict(c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
cs = pl.contourf(xx, yy, Z, cmap=pl.cm.Paired)
pl.axis("tight")
'''
'''




# Plot the training points
pl.subplot(131)
for i, n, c in zip(xrange(2), class_names, plot_colors):
    idx = where(y == i)
    pl.scatter(x[idx, 0], x[idx, 1],
               c=c, cmap=pl.cm.Paired,
               label="Class %s" % n)
pl.axis("tight")
pl.legend(loc='upper right')
pl.xlabel("Decision Boundary")





# Plot the class probabilities
class_proba = ada.predict_proba(x)[:, -1]
#pl.subplot(132)
for i, n, c in zip(xrange(2), class_names, plot_colors):
    pl.hist(class_proba[y == i],
            bins=50,
            range=(0, 1),
            facecolor=c,
            label='Class %s' % n)
pl.legend(loc='upper center')
pl.ylabel('Samples')
pl.xlabel('Class Probability')

# Plot the two-class decision scores
twoclass_output = ada.decision_function(x)

#reweight twoclass_output
print twoclass_output

#for x in xrange(0,len(twoclass_output)):
#    weight = 
#    twoclass_output[x][0] = twoclass_output[x][0]*weight

pl.subplot(133)
for i, n, c in zip(xrange(2), class_names, plot_colors):
    pl.hist(twoclass_output[y == i],
            bins=50,
            range=(-1, 1),
            facecolor=c,
            label='Class %s' % n, normed=True)
pl.legend(loc='upper right')
pl.ylabel('Samples')
pl.xlabel('Two-class Decision Scores')

pl.subplots_adjust(wspace=0.25)
mean_tpr = 0.0
mean_fpr = linspace(0, 1, 100)
from sklearn.metrics import roc_curve, auc
pl.subplot(132)
beginIdx = 0
endIdx = len(xt)#/2
#need method to calculate rej: 1-num(b)/total(b)
#tpr is signal efficiency: num(s)/total(s)
for i in range(1):
    probas_ = ada.predict_proba(xt[beginIdx:endIdx])
    # Compute ROC curve and area the curve
    fpr, tpr, thresholds, rej = roc_curve_rej(yt[beginIdx:endIdx], probas_[:,1])
    #mean_tpr += interp(mean_fpr, fpr, tpr)
    #mean_tpr[0] = 0.0
    roc_auc = auc(tpr,rej)#auc(fpr, tpr)
    print i
    pl.plot(tpr, rej, lw=1, label='ROC fold %d (area = %0.2f)' % (i, roc_auc), color=plot_colors[i])
    beginIdx = endIdx
    endIdx = len(xt)

pl.show()
'''
