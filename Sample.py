class Sample():
    from numpy import *
    from root_numpy import *
    import sys
    import createHists
    import sortAndCut as sc

    variablesDone = False # whether or not the variables have been found
    test = []
    train = []
    testWeights = []
    trainWeights = []
    testLabels = []
    trainLabels = []
    testWeightsXS = []
    trainWeightsXS = []


    def __init__ (self, filename, treename, typeOfSample):
        """Define a Sample object given filename, treename and type of sample - sig/bkg/data."""
        self.sample = root2array(filename,treename)
        self.sample_length = len(self.sample)
        typeUpper = typeOfSample.upper()
        if (typeUpper!='DATA' or typeUpper!='SIG' or typeUpper!='BKG'):
            print 'Type ' + str(typeOfSample) + ' not known, setting to bkg mc'
            self.type = 'bkg'
        self.type = typeOfSample
        
    def returnFullLength(self):
        """Return the length of the full input sample."""
        return self.sample_length
    
    def returnFullSample(self):
        """Return the full input sample as a numpy array."""
        return self.sample
    
    def returnSampleType(self):
        """Return data type of input sample."""
        return self.type

    
    # Split for training and testing, remove unwanted variables not for training
    def splitTree(self,training, splitSize, sampleLabel):
        """Return subset of full sample based on training/ testing, length and A or B sample"""
        self.tempSet = sc.cutTree(self.sample,training,splitSize,sampleLabel)
        self.tempLen = len(self.tempSet)
        return self.tempSet



    def returnTemp(self):
        """Return subset of temp sample without recalculating."""
        return self.tempSet

    def returnTempLength(self):
        """Return length of temp sample."""
        return self.tempLen

    def getVariableNames(self, variableNames, foundVariables, varIdx, varWeightsHash = {}):
        """Get all of the indices of the variables in the dataset."""
    # foundVariables, varIdx and varWeightsHash are mutable and changed in the method
        if self.type != 'data':
            sc.getVariableIndices(self.sample, variableNames, foundVariables, varIdx, varWeightsHash, 'mc')
        else:
            # we need to do this for data separately because of different branches
            blah = {}
            sc.getVariableIndices(self.sample, variableNames, foundVariables, varIdx, varWeightsHash, 'data')
        setVariableNames(variableNames, foundVariables, varIdx, varWeightsHash)

    def setVariableNames(self, variableNames, foundVariables, varIdx, varWeightsHash):
        """Set the variable name values."""
        self.variableNames = copy.deepcopy(variableNames)
        self.varIdx = copy.deepcopy(varIdx)
        self.foundVariables = copy.deepcopy(foundVariables)
        self.varWeightsHash = copy.deepcopy(varWeightsHash)
        self.variablesDone = True


    def returnVariableData(self):
        """Return the variable names, indices, list of found variables and the weights hash table."""
        if not variablesDone:
            return -1
        return self.variableNames, self.varIdx, self.foundVariables, self.varWeightsHash

    # get all of the training data needed
    def getTrainingData(self, splitSize, subset, nEntriesA, lumi, labelCodes):
        """Get the subset of data, the associated weights and labels for training data."""
        splitTree(True, splitSize, subset)
        tr, we, lb, xs = sc.cutCols(returnTemp(), varIdx, returnTempLength(), len(self.variableNames), self.varWeightsHash, nEntriesA, lumi) # signal set A
        append = False
        if subset == 'A':
            trainIdx = 0
            if not self.train:
                append = True
        else:
            trainIdx = 1
            if len(self.train) == 1:
                append = True
        if append:
            self.train.append(tr)
            self.trainweights.append(we)
            self.trainLabels.append(lb)
            self.trainWeightsXS.append(xs)
        else:
            self.train[trainIdx] = tr
            self.trainWeights[trainIdx] = we
            self.trainLabels[trainIdx] = lb
            self.trainWeightsXS[trainIdx] = xs
        if trainIdx == 0:
            self.trainLengthA = len(self.train[0])
        else:
            self.trainLengthB = len(self.train[1])

    def getTestingDataForData(self, nEntriesA, lumi):
        """Get the subset needed for testing if using DATA and NOT MC."""
        if not variablesDone:
            return -1
        if not self.test:
            self.test.append(sc.cutColsData(self.sample, self.varIdx, self.sampleLength,len(self.variableNames), nEntriesA, lumi)) # data set
        else:
            self.test[0]=sc.cutColsData(self.sample, self.varIdx, self.sampleLength,len(self.variableNames), nEntries, lumi) # data set
        return 0
            
    def returnTrainingSamples(self):
        """Return the array of training samples."""
        return self.train, self.trainWeights, self.trainLabels, self.trainWeightsXS

    def returnTrainingSample(self, subset):
        """Return a single training sample indexed by subset A or B."""
        if subset == 'A' and self.train:
            return self.train[0]
        elif len(self.train) > 1:
            return self.train[1]
        return -1

    def returnTestingSample(self, subset):
        """Return a single testing sample indexed by subset A or B."""
        if subset == 'A' and self.test:
            return self.test[0]
        elif len(self.test) > 1:
            return self.test[1]
        return -1

    def getTestingData(self, splitSize, sampleLabel, nEntries, lumi, labelCodes):
        """Set up a test sample."""
        splitTree(False, splitSize, sampleLabel)
        test, weights, labels, weightsXS = sc.cutCols(self.temp, self.varIdx, len(self.temp), len(self.variableNames), self.varWeightsHash, nEntries, lumi, True, labelCodes)
        idx = 0
        append = False
        if sampleLabel == 'A' and not self.test:
            idx = 0
            append = True
        elif sampleLabel == 'A':
            idx = 0
        elif sampleLabel != 'A' and len(self.test) == 1:
            idx = 1
            append = True
        else:
            idx = 1
        # We need to make sure that we append or replace appropriately
        if append:
            self.test.append(copy.deepcopy(test))
            self.testWeights.append(copy.deepcopy(weights))
            self.testLabels.append(copy.deepcopy(labels))
            self.testWeightsXS.append(copy.deepcopy(weightsXS))
        else:
            self.test[idx] = (copy.deepcopy(test))
            self.testWeights[idx] = (copy.deepcopy(weights))
            self.testLabels[idx] = (copy.deepcopy(labels))
            self.testWeightsXS[idx] = (copy.deepcopy(weightsXS))
            
        if idx == 0:
            self.testLengthA = len(self.test[0])
        else:
            self.testLengthB = len(self.test[1])

    def returnTestingSamples(self):
        """Return the array of testing samples."""
        return self.test, self.testWeights, self.testLabels, self.testWeightsXS

    def returnLengthTest(self, subset):
        """Return the length of the testing samples by subset A or B."""
        if subset == 'A' and self.test:
            return self.testLengthA
        elif len(self.test) > 1:
            return self.testLengthB
        else:
            return -1


    def returnLengthTrain(self, subset):
        """Return the length of the training samples by subset A or B."""
        if subset == 'A' and self.train:
            return self.trainLengthA
        elif len(self.train) > 1:
            return self.trainLengthB
        return -1

    def transposeDataTest(self):
        if self.type.upper() == 'DATA':
            self.test[0] = transpose(self.test[0])

    def sortTestSamples(self):
        """Sort the testing samples and weights according to the labels."""
        for x in xrange(0,len(self.test)):
            sortPermutation = self.testLabels[x].argsort()
            self.test[x] = self.test[x][sortPermutation]
            self.testLabels[x] = self.testLabels[x][sortPermutation]
            self.testWeights[x] = self.testWeights[x][sortPermutation]

    def transposeTestSamples(self):
        """Transpose all test matrices."""
        for x in xrange(0,len(self.test)):
            self.test[x] = transpose(self.test[x])
            self.testLabels[x] = transpose(self.testLabels[x])
            self.testWeights[x] = transpose(self.testWeights[x])


    def sortTrainSamples(self):
        """Sort the training samples and weights according to the labels."""
        for x in xrange(0,len(self.train)):
            sortPermutation = self.trainLabels[x].argsort()
            self.train[x] = self.train[x][sortPermutation]
            self.trainLabels[x] = self.trainLabels[x][sortPermutation]
            self.trainWeights[x] = self.trainWeights[x][sortPermutation]

    def transposeTrainSamples(self):
        """Transpose all test matrices."""
        for x in xrange(0,len(self.train)):
            self.train[x] = transpose(self.train[x])
            self.trainLabels[x] = transpose(self.trainLabels[x])
            self.trainWeights[x] = transpose(self.trainWeights[x])

    def returnTrainWeightsXS(self, subset):
        """Return the array of per sample weights (xs)"""
        if subset == 'A' and self.trainWeightsXS:
            return self.trainWeightsXS[0]
        elif len(self.trainWeightsXS) > 1:
            return self.trainWeightsXS[1]
        else:
            return -1

    def returnTestWeightsXS(self, subset):
        """Return the array of per sample weights (xs)"""
        if subset == 'A' and self.testWeightsXS:
            return self.testWeightsXS[0]
        elif len(self.testWeightsXS) > 1:
            return self.testWeightsXS[1]
        return -1

    def returnTestSample(self, subset = 'A'):
        """Return the test array of subset A or B"""
        if self.type.upper == 'DATA':
            return self.test[0]
        if subset == 'A' and self.test:
            return self.test[0]
        elif len(self.test) > 1:
            return self.test[1]
        return -1

    def returnTrainSample(self, subset):
        """Return the array of per sample weights (xs)"""
        if subset == 'A' and self.train:
            return self.train[0]
        elif len(self.train) > 1:
            return self.train[1]
        return -1

    def returnTestSampleLabels(self, subset):
        """Return the array of per sample weights (xs)"""
        if subset == 'A' and self.testLabels:
            return self.testLabels[0]
        elif len(self.testLabels) > 1:
            return self.testLabels[1]
        return -1

    def returnTrainSampleLabels(self, subset):
        """Return the array of per sample weights (xs)"""
        if subset == 'A' and self.trainLabels:
            return self.trainLabels[0]
        elif len(self.trainLabels) > 1:
            return self.trainLabels[1]
        return -1

    def returnFoundVariables(self):
        """Return found variables."""
        if self.doneVariables:
            return self.foundVariables
        else:
            return -1
        

