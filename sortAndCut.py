__all__=['argsortlist','roc_curve_ref','readInLabels','readInNames','sortMultiple','shuffle_in_unison','cutTree','evenArr','oddArr','cutCols','cutColsData','onesInt','zerosInt','setWeights','getVariableIndices']

from numpy import *
from root_numpy import *
import sys


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
    #print labelcodes
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
        if (sampleVersion == 'Any'):
            return arr[:pos]
        elif (sampleVersion == 'A'):
            return evenArr(arr, evNum)
        elif sampleVersion == 'B':
            return oddArr(arr, evNum)

    else:
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
    if calcWeightPerSample:
        return outarr, array(outweights), array(outlabels), weightsPerSample
    else:
        return outarr, array(outweights), array(outlabels)



# take out only the variables we want to train on
# if sampleVersion = A, only use even EventNumbers, B odd
'''
def cutCols(arr, varIdx, rows, cols, varWIdx, nEntries, lumi):
    rowcount = 0
    #initialise a basic numpy array that we will return
    outarr = ones((int(rows),int(cols)))
    outweights = []
    outlabels = []
    for row in arr:
        colcount = 0
        for col in varIdx:
            outarr[rowcount][colcount] = row[col]
            colcount = colcount + 1
        rowcount = rowcount + 1
        outweights.append(row[int(varWIdx['final_xs'])]*lumi/nEntries)
        outlabels.append(int(row[int(varWIdx['label_code'])]))
        
    return outarr, array(outweights), array(outlabels)
'''
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

def getVariableIndices(dataset, variableNames, foundVariables, varIdx, varWeightsHash, name):
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
