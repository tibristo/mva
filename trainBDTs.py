def trainBDTs(bkg_type, sig, bkg):
    #global sig,bkg
    import numpy, sortAndCut, adaBoost
    # sometimes -1 can be returned!
    # nEntries is part of the relative weighting of events, used to be included in the the XS reweighting
    nEntriesSA = 1.0/(float((sig.returnLengthTrain('A')))/float(sig.returnFullLength()))
    nEntriesSB = 1.0/(float((sig.returnLengthTrain('B')))/float(sig.returnFullLength()))
    nEntriesBA = 1.0/(float((bkg.returnTrainingBkgLength('A',bkg_type)))/float(bkg.returnTrainingFullBkgLength(bkg_type)))
    nEntriesBB = 1.0/(float((bkg.returnTrainingBkgLength('B',bkg_type)))/float(bkg.returnTrainingFullBkgLength(bkg_type)))

    # Weights here used as ratio for BDT training weights
    if bkg_type == 'bkg':
        bkg_is_nparray = False
    else:
        bkg_is_nparray = True
    try: 
        x_A, y_A, weights_A = sortAndCut.combineWeights(sig, bkg, 'A', bkg_type, True, bkg_is_nparray)
        x_B, y_B, weights_B = sortAndCut.combineWeights(sig, bkg, 'B', bkg_type, True, bkg_is_nparray)
    except:
        error = 'Caught exception whilst running combineWeights on training data'
        error += ' Bkg_type: ' + str(bkg_type)
        print error
        return error
    try:
        xtA, ytA, weightstA = sortAndCut.combineWeights(sig, bkg, 'A', bkg_type, False, bkg_is_nparray)
        xtB, ytB, weightstB = sortAndCut.combineWeights(sig, bkg, 'B', bkg_type, False, bkg_is_nparray)
    except:
        error = 'Caught exception whilst running combineWeights on testing data'
        error += ' Bkg_type: ' + str(bkg_type)
        print error
        return error
    trainWeights_A = numpy.hstack((sig.returnTrainWeights('A'), bkg.returnTrainWeights('A', bkg_type)))
    weights_A =numpy.multiply(weights_A,trainWeights_A)
    for xi in xrange(0, len(sig.returnTrainingSample('A'))):
        weights_A[xi] = 1.0*nEntriesSA
    for xii in xrange(len(sig.returnTrainingSample('A')), trainWeights_A.shape[0]):
        weights_A[xii] *= nEntriesBA

    trainWeights_B = numpy.hstack((sig.returnTrainWeights('B'), bkg.returnTrainWeights('B', bkg_type)))
    weights_B =numpy.multiply(weights_B,trainWeights_B)
    for xi in xrange(0, len(sig.returnTrainingSample('B'))):
        weights_B[xi] = 1.0*nEntriesSB
    for xii in xrange(len(sig.returnTrainingSample('B')), trainWeights_B.shape[0]):
        weights_B[xii] *= nEntriesBB
    ada1_name = bkg_type+str('_A')
    ada2_name = bkg_type+str('_B')
    ada1 = adaBoost.adaBoost(sig.returnFoundVariables(), x_A, y_A, weights_A, xtA, ytA, ada1_name, bkg_type)
    ada2 = adaBoost.adaBoost(sig.returnFoundVariables(), x_B, y_B, weights_B, xtB, ytB, ada2_name, bkg_type)
    return [ada1,ada2]
    #conn.send([ada1,ada2])
    #conn.close()

