__all__=['argsortlist','roc_curve_ref','readInLabels','readInNames','sortMultiple','shuffle_in_unison','cutTree','evenArr','oddArr','cutCols','cutColsData','onesInt','zerosInt','setWeights','getVariableIndices','combineWeights']

from numpy import *
from root_numpy import *
import sys
import math
import CorrsAndSysts_ext as cs
corr = cs.CorrsAndSysts(1,2012,True)
labelTranslate = {'ttbar':cs.CAS.EventType.ttbar,'st':cs.CAS.EventType.stop,'WW':cs.CAS.EventType.diboson,'ZZ':cs.CAS.EventType.diboson,'WZ':cs.CAS.EventType.diboson,'Wl':cs.CAS.EventType.Wl,'Wcc':cs.CAS.EventType.Wcc,'Wc':cs.CAS.EventType.Wc,'Wb':cs.CAS.EventType.Wb,'Zb':cs.CAS.EventType.Zb,'Z':cs.CAS.EventType.NONAME,'WH110':cs.CAS.EventType.WHlvbb,'WH115':cs.CAS.EventType.WHlvbb,'WH120':cs.CAS.EventType.WHlvbb,'WH125':cs.CAS.EventType.WHlvbb,'WH130':cs.CAS.EventType.WHlvbb,'WH135':cs.CAS.EventType.WHlvbb,'WH140':cs.CAS.EventType.WHlvbb,'NONAME':cs.CAS.EventType.NONAME}

def argsortlist(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key = seq.__getitem__)

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

def readInLabels():
    f = open('Labels.txt')
    labelcodes = []
    labelcodesNum = []
    for line in f:
        l = line.split(',')
        labelcodes.append(l[0])
        labelcodesNum.append(int(l[1]))
    f.close()
    labelcodesNum,labelcodes = zip(*sorted(zip(labelcodesNum,labelcodes)))
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

def sortMultiple(arr1, arr2):
    print 'sort Multiple'
    if len(arr1) > len(arr2):
        return -1
    for x in xrange(1,len(arr1)-1):
        val = arr1[x]
        val2 = arr2[x]
        hole = x
        while hole > 0 and val < arr1[hole-1]:
            arr1[hole] = arr1[hole-1]
            arr2[hole] = arr2[hole-1]
            hole -= 1
        arr1[hole] = val
        arr2[hole] = val2
    print 'finished sort'
    return arr1,arr2


def shuffle_in_unison(a, b, c):
    """Shuffle three arrays in unison.
    
    Keyword arguments:
    a, b, c --  3 arrays to be shuffled.
    """
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
def cutTree(arr, training, pos, evNum, sampleVersion = 'R' ):
    """Cut the tree into a smaller subset without removing any columns.

    Keyword arguments:
    arr -- the input sample to be divided
    training -- True or False to indicate it is training or testing
    pos -- the split size of the subset
    evNum -- the index of the EventNumber variable in arr
    sampleVersion -- the subset A, B or R for random
    
    """
    lenarr = len(arr)
    # Use first half of array for training, second for testing
    if pos > lenarr:
        pos = lenarr-1
    if training == True:
        if (sampleVersion == 'R'):
            return arr[:pos]
        elif sampleVersion == 'C':
            return arr
        elif (sampleVersion == 'A'):
            return evenArr(arr, evNum, pos)
        elif sampleVersion == 'B':
            return oddArr(arr, evNum, pos)

    else:
        if (sampleVersion == 'R'):
            return arr[lenarr-pos:]
        elif sampleVersion == 'C':
            return arr
        elif (sampleVersion == 'A'):
            return oddArr(arr, evNum, pos, False)#this is odd so that training and testing are done on diff samples
        elif sampleVersion == 'B':
            return evenArr(arr, evNum, pos, False)

def evenArr(arr, evNum, splitSize, training = True):
    """Return an array with only even EventNumber of size splitSize.

    Keyword arguments:
    arr -- the input array
    evNum -- the index of the EventNumber variable in the input array
    splitSize -- the maximum size of the output array
    training -- whether or not this is a training sample

    """
    # arr.shape[1] returns number of columns
    tempnparr = empty([splitSize],dtype=object)
    counter = 0
    if True:#training:
        arrit = arr
    else:
        arrit = arr[::-1]
    for x in arrit:
        if x[evNum]%2 == 0:
            tempnparr[counter] = x
            counter += 1
        if counter >= splitSize:
            break
    tempnparr = resize(tempnparr, [counter])
    return tempnparr

def oddArr(arr, evNum, splitSize, training = True):
    """Return an array with only even EventNumber of size splitSize.

    Keyword arguments:
    arr -- the input array
    evNum -- the index of the EventNumber variable in the input array
    splitSize -- the maximum size of the output array
    training -- whether or not this is a training sample

    """
    tempArr = empty([splitSize],dtype=object)
    counter = 0
    if True:#training:
        arrit = arr
    else:
        arrit = arr[::-1]
    for x in arrit:
        if x[evNum]%2 == 1:
            tempArr[counter] = x
            counter += 1
        if counter >= splitSize:
            break
    tempArr = resize(tempArr, [counter])
    return tempArr




def cutCols(arr, varIdx, rows, cols, varWIdx, nEntries, lumi, calcWeightPerSample = False, labels = []):
    """
    Cut out the columns we need.

    Keyword arguments:
    arr -- Input array
    varIdx -- Indices of all variables
    rows -- Number of rows
    cols -- Number of columns
    varWIdx -- The indices of all of the weights
    nEntries -- Number of entries in the sample
    lumi -- Luminosity
    calcWeightsPerSample -- Whether or not to calculate the weights for each sample
    labels -- The label codes going from a number -> type of sample
    bkgIndices -- Dictionary containing the indices of the different backgrounds in the full sample
    """
    rowcount = 0
    #initialise a basic numpy array that we will return
    outarr = ones((int(rows),int(cols)))
    outweights = []
    outlabels = []
    weightsPerSample = {}
    bkgIndices = {}
    labidx = {}
    for row in arr:
        colcount = 0
        for col in varIdx:
            outarr[rowcount][colcount] = row[col]
            colcount = colcount + 1
        rowcount = rowcount + 1
        weight = float(row[int(varWIdx['final_xs'])]*lumi/row[int(varWIdx['AllEntries'])]) #nEntries)
        key = row[int(varWIdx['label_code'])]
        outweights.append(weight)
        outlabels.append(int(key))
        lab = str(labels[int(key)])
        if lab in bkgIndices:
            bkgIndices[lab][int(labidx[lab])] = int(rowcount-1)
            labidx[lab]+=1
        else:
            #bkgIndices[lab] = [rowcount-1]
            bkgIndices[lab] = empty([rows],dtype=int)
            bkgIndices[lab][0] = int(rowcount-1)
            labidx[lab]=1
        # there is a better way to do this, need to do it once, rather than many times since it'll be the same                      
        if calcWeightPerSample and lab not in weightsPerSample:
            weightsPerSample[labels[int(key)]] = weight            
    for x in bkgIndices.keys():
        bkgIndices[x] = resize(bkgIndices[x],[int(labidx[x])])
        #print 'size of bkgIndices '
        #print bkgIndices[x].shape
    if calcWeightPerSample:
        return outarr, array(outweights), array(outlabels), weightsPerSample, bkgIndices
    else:
        return outarr, array(outweights), array(outlabels), bkgIndices

def cutColsData(arr, varIdx, rows, cols, nEntries, lumi):
    rowcount = 0
    #initialise a basic numpy array that we will return
    outarr = ones((int(rows),int(cols)))
    for row in arr:
        colcount = 0
        for col in varIdx:
            outarr[rowcount][colcount] = row[col]
            colcount = colcount + 1
        rowcount = rowcount + 1
                      
    return outarr


def onesInt(length):
    """Return a list of ones of given length."""
    arr = []
    for i in xrange(0,length):
        arr.append(1)
    return arr

def zerosInt(length):
    """Return a list of zeroes of given length."""
    arr = []
    for i in xrange(0,length):
        arr.append(0)
    return arr

# set the weights for training
def setWeights(length, weight):
    """Return a list of weights of given length."""
    weights = []
    for i in xrange(0,length):
        weights.append(weight)
    return weights

def getVariableIndices(dataset, variableNames, foundVariables, varIdx, varWeightsHash, name):
    """
    
    Keyword arguments:
    dataset -- the input sample
    variableNames -- the list of variableNames we are looking for
    foundVariables -- a list of found variables that gets returned
    varIdx -- the list of all indices of found variables
    varWeightsHash -- a dictionary of all corrections to be applied
    name -- the sample type - MC or data
    bkgIndices -- a dictionary storing indices of different background samples
    """
    xcount = 0
    evNum = 0
#store the variables we find and their indices
    for x in dataset.dtype.names:
        # TODO: read in variableNames from settings xml
        if x in variableNames:
            varIdx.append(xcount)
            foundVariables.append(x)
        if name.upper()=='MC' and x in varWeightsHash.keys():
            varWeightsHash[x]= xcount
        if x == 'EventNumber':
            evNum = xcount
        xcount = xcount + 1

def setCorrWeights(sample, weights, subsample, bkg_name, logfile, trainSample = True):
    try:
        if trainSample:
            corrWeights = sample.returnTrainCorrectionWeights(subsample, bkg_name)
        else:
            corrWeights = sample.returnTestCorrectionWeights(subsample, bkg_name)
    except:
        logfile.write('Failed setCorrWeights on sample.returnTestCorrectionWeights')
        return weights
    xcount = 0
    try:
        for x in corrWeights:
            weights[xcount]*=x
            xcount+=1
    except TypeError:
        logfile.write('corrWeights not iterable')
        return weights
    return weights

def combineWeights(sig, bkg, subsample, bkg_name, trainSample = True, nparrays = False):
    """Add the training trees together, keeping track of which entries are signal and background."""
    log = open(bkg_name+'_' + str(subsample) +'_combineWeights.log','w')
    log.write('obtaining sigTrain and bkgTrain')
    try:
        if nparrays:
            if trainSample:
                sigTrain = sig.returnTrainingSample(subsample)
            else:
                sigTrain = sig.returnTestingSample(subsample)
            bkgTrain = bkg.returnBkg(subsample, trainSample, bkg_name)
        else:
            if trainSample:
                sigTrain = sig.returnTrainingSample(subsample)
                bkgTrain = bkg.returnTrainingSample(subsample)
            else:
                sigTrain = sig.returnTestingSample(subsample)
                bkgTrain = bkg.returnTestingSample(subsample)
        log.write('Obtained sigTrain and bkgTrain')
    except:
        log.write('Problem returning training samples, exiting')
        log.close()
        return self.error()

    #print sigTrain.shape
    #print bkgTrain.shape
    log.write('Begin vstack and hstack')
    try:
        xtA = vstack((sigTrain, bkgTrain))
        ytA = transpose(hstack(( onesInt(len(sigTrain)), zerosInt(len(bkgTrain)) )))
        log.write('completed stacking')
    except:
        log.write('Error running stacking')
        log.close()
        return self.error()
    sigWeightA = 1.0 # float(1/float(len(sigTrain)))
    bkgWeightA = float(len(sigTrain))/float(len(bkgTrain)) # weight background as ratio
    log.write ('Run setCorrWeights for bkg')
    weightsBkgA = setWeights(len(bkgTrain),bkgWeightA)
    try:
        # this won't work for when bkg is numpy array
        setCorrWeights(bkg, weightsBkgA, subsample, bkg_name, log, trainSample)
        log.write('completed setCorrWeights for bkg')
    except:
        log.write('Failed setCorrWeights for bkg')
        log.close()
        return self.error()
    weightsSigA = setWeights(len(sigTrain),sigWeightA)  
    log.write ('Run setCorrWeights for sig')
    try:
        setCorrWeights(sig, weightsSigA, subsample, bkg_name, log, trainSample)
        log.write('Completed setCorrWeights for sig')
    except:
        log.write('Failed setCorrWeights for sig')
        log.close()
        return self.error()
    weightstA = transpose(hstack((weightsSigA,weightsBkgA)))
    log.write('Completed combineWeights for ' + bkg_name + ' ' + str(subsample))
    log.close()
    return xtA, ytA, weightstA

        
def getEventType(labelCodes, labelVal):
    global corr
    global labelTranslate
    key = labelCodes[int(labelVal)]
    if key in labelTranslate.keys():
        evtType = labelTranslate[key]
    else:
        evtType = labelTranslate['NONAME']
    return evtType    

def applyCorrs(arr, labelCodes, varWIdx, nEntries):
    global corr
    correctionWeights = empty([nEntries])
    count = 0
    for row in arr:
        evtType = getEventType(labelCodes,row[varWIdx['label_code']])
        vPt = float(row[varWIdx['VpT_truth']])
        dphi = math.fabs(row[varWIdx['dPhiVBB']])
        njet = 2#row[varWIdx['signal_jets']]#need to add this!!!
        hNLOCorr = corr.Get_HiggsNLOEWKCorrection(evtType, vPt)
        #bkgTopPTCorr = corr.Get_BkgpTCorrection(evtType, vPt)
        topptCorr = 1.0#corr.Get_ToppTCorrection(evtType, avgTopPt)
        dphiCorr = corr.Get_BkgDeltaPhiCorrection(evtType, dphi, njet)
        mcCorr = row[varWIdx['weight_MC']]
        puCorrVec = row[varWIdx['weight_PU']]
        puCorr = puCorrVec[0]
        weight_lepton1_vec = row[varWIdx['weight_lepton1']]
        weight_lepton1 = 1
        for c in weight_lepton1_vec:
            weight_lepton1 *= c
        
        metCorr = row[varWIdx['weight_MET']]
        correctionWeights[count]=math.fabs(1.0*hNLOCorr*topptCorr*dphiCorr*mcCorr*metCorr*weight_lepton1)#*puCorr

        count+=1
    return correctionWeights
