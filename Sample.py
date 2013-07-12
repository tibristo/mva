import sortAndCut as sc
from numpy import *
import root_numpy
import sys
import createHists
import copy



class Sample:
    __all__= ['getTrainingSample','returnFullLength','returnTestSample']
    __all__.append('returnTestWeightsXS')
    __all__.append('getTestingDataForData')
    __all__.append('transposeDataTest')
    __all__.append('transposeTestSamples')
    __all__.append('returnTrainWeightsXS')
    __all__.append('transposeTrainSamples')
    #variablesDone = False # whether or not the variables have been found

    def __init__ (self, filename, treename, typeOfSample):
        """Define a Sample object given filename, treename and type of sample - sig/bkg/data."""
        self.evNumSearch = False
        self.test = []
        self.train = []
        self.testWeights = []
        self.trainWeights = []
        self.testLabels = []
        self.trainLabels = []
        self.testWeightsXS = []
        self.trainWeightsXS = []
        self.trainCorrectionWeights = []
        self.testCorrectionWeights = []
        self.sample = root_numpy.root2array(filename,treename)
        self.sample_length = len(self.sample)
        self.variablesDone = False
        self.evNumIdx = 0
        typeUpper = typeOfSample.upper()
        if (typeUpper!='DATA' and typeUpper!='SIG' and typeUpper!='BKG'):
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

    def getEventNumberIndex(self):
        """Return the index of the EventNumber index in the sample."""
        idx = 0
        self.evNumSearch = True
        for x in self.sample.dtype.names:
            if x == 'EventNumber':
                return idx
            idx += 1
        return -1
    
    # Split for training and testing, remove unwanted variables not for training
    def splitTree(self,training, splitSize, sampleLabel):
        """Return subset of full sample based on training/ testing, length and A or B sample.
        
        Keyword arguments:
        training -- True or False if it is training or testing
        splitSize -- the maximum output size of the array
        sampleLabel -- A or B, which changes to R if event number index can't be found

        """
        lab = sampleLabel
        if not self.evNumSearch:
            self.evNumIdx = self.getEventNumberIndex()
        if self.evNumIdx == -1:
            print 'EventNumber not found!!!!'
            print 'Using sampleLabel R instead.'
            lab = 'R'
        self.tempSet = sc.cutTree(self.sample, training, splitSize, self.evNumIdx, lab)
        self.tempLen = len(self.tempSet)

        return self.tempSet

    def returnTemp(self):
        """Return subset of temp sample without recalculating."""
        return self.tempSet

    def returnTempLength(self):
        """Return length of temp sample."""
        return self.tempLen

    def setVariableNames(self, variableNames, foundVariables, varIdx, varWeightsHash):
        """Set the variable name values."""
        self.variableNames = copy.deepcopy(variableNames)
        self.varIdx = copy.deepcopy(varIdx)
        self.foundVariables = copy.deepcopy(foundVariables)
        self.varWeightsHash = copy.deepcopy(varWeightsHash)
        self.variablesDone = True

    def getVariableNames(self, variableNames, foundVariables, varIdx, varWeightsHash = {}):
        """Get all of the indices of the variables in the dataset."""
        # foundVariables, varIdx and varWeightsHash are mutable and changed in the method
        if self.type != 'data':
            sc.getVariableIndices(self.sample, variableNames, foundVariables, varIdx, varWeightsHash, 'mc')
        else:
            # we need to do this for data separately because of different branches
            blah = {}
            sc.getVariableIndices(self.sample, variableNames, foundVariables, varIdx, varWeightsHash, 'data')
        self.setVariableNames(variableNames, foundVariables, varIdx, varWeightsHash)
        self.variablesDone = True

    def returnVariableData(self):
        """Return the variable names, indices, list of found variables and the weights hash table."""
        if not self.variablesDone:
            print 'variables not done'
            return self.error()
        return self.variableNames, self.varIdx, self.foundVariables, self.varWeightsHash

    # get all of the training data needed
    def getTrainingData(self, splitSize, subset, nEntriesA, lumi, labelCodes):
        """Get the subset of data, the associated weights and labels for training data."""
        self.splitTree(True, splitSize, subset)
        cw = sc.applyCorrs(self.returnTemp(), labelCodes, self.varWeightsHash, self.returnTempLength())
        tr, we, lb, xs = sc.cutCols(self.returnTemp(), self.varIdx, self.returnTempLength(), len(self.variableNames), self.varWeightsHash, nEntriesA, lumi, True, labelCodes) # signal set A
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
            self.train.append(copy.deepcopy(tr))
            self.trainWeights.append(copy.deepcopy(we))
            self.trainLabels.append(copy.deepcopy(lb))
            self.trainWeightsXS.append(copy.deepcopy(xs))
            self.trainCorrectionWeights.append(copy.deepcopy(cw))
        else:
            self.train[trainIdx] = copy.deepcopy(tr)
            self.trainWeights[trainIdx] = copy.deepcopy(we)
            self.trainLabels[trainIdx] = copy.deepcopy(lb)
            self.trainWeightsXS[trainIdx] = copy.deepcopy(xs)
            self.trainCorrectionWeights[trainIdx] = copy.deepcopy(cw)
        if trainIdx == 0:
            self.trainLengthA = len(self.train[0])
        else:
            self.trainLengthB = len(self.train[1])

    def weightAllTrainSamples(self, subset, weight):
        """Change all weights for the training sample of A or B by a factor weight.
        
        Keyword arguments:
        subset -- A or B
        weight -- the weight to be applied

        """
        if subset == 'A':
            idx = 0
        elif subset == 'B':
            idx = 1
        else:
            print "invalid subset, using A"
            idx = 0
        for key in self.trainWeightsXS[idx]:
            self.trainWeightsXS[idx][key] *= weight

    def weightAllTestSamples(self, subset, weight):
        """Change all weights for the testing sample of A or B by a factor weight.
        
        Keyword arguments:
        subset -- A or B
        weight -- the weight to be applied

        """
        if subset == 'A':
            idx = 0
        elif subset == 'B':
            idx = 1
        else:
            print "invalid subset, using A"
            idx = 0
        for key in self.testWeightsXS[idx]:
            self.testWeightsXS[idx][key] *= weight

    def getTestingDataForData(self, nEntriesA, lumi):
        """Get the subset needed for testing if using DATA and NOT MC."""
        if not self.variablesDone:
            return self.error()
        if not self.test:
            self.test.append(copy.deepcopy(sc.cutColsData(self.sample, self.varIdx, self.sample_length,len(self.variableNames), nEntriesA, lumi))) # data set
        else:
            self.test[0]= copy.deepcopy(sc.cutColsData(self.sample, self.varIdx, self.sample_length,len(self.variableNames), nEntriesA, lumi)) # data set
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
        return self.error()

    def returnTestingSample(self, subset):
        """Return a single testing sample indexed by subset A or B."""
        if subset == 'A' and self.test:
            return self.test[0]
        elif len(self.test) > 1:
            return self.test[1]
        return self.error()

    def getTestingData(self, splitSize, sampleLabel, nEntries, lumi, labelCodes):
        """Set up a test sample."""
        self.splitTree(False, splitSize, sampleLabel)
        cw = sc.applyCorrs(self.tempSet, labelCodes, self.varWeightsHash, len(self.tempSet))
        test, weights, labels, weightsXS = sc.cutCols(self.tempSet, self.varIdx, len(self.tempSet), len(self.variableNames), self.varWeightsHash, nEntries, lumi, True, labelCodes)
        print len(test)
        idx = 0
        append = False
        if (sampleLabel == 'A' or sampleLabel == 'C') and not self.test:
            idx = 0
            append = True
        elif sampleLabel == 'A' or sampleLabel == 'C':
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
            self.testCorrectionWeights.append(copy.deepcopy(cw))
        else:
            self.test[idx] = (copy.deepcopy(test))
            self.testWeights[idx] = (copy.deepcopy(weights))
            self.testLabels[idx] = (copy.deepcopy(labels))
            self.testWeightsXS[idx] = (copy.deepcopy(weightsXS))
            self.testCorrectionWeights[idx] = copy.deepcopy(cw)
            
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
            return self.error()


    def returnLengthTrain(self, subset):
        """Return the length of the training samples by subset A or B."""
        if subset == 'A' and self.train:
            return self.trainLengthA
        elif len(self.train) > 1:
            return self.trainLengthB
        return self.error()

    def transposeDataTest(self):
        """Transpose the data sample"""

        if self.type.upper() == 'DATA':
            self.test[0] = transpose(self.test[0])

    def sortTestSamples(self):
        """Sort the testing samples and weights according to the labels."""
        for x in xrange(0,len(self.test)):
            sortPermutation = self.testLabels[x].argsort()
            self.test[x] = self.test[x][sortPermutation]
            self.testLabels[x] = self.testLabels[x][sortPermutation]
            self.testWeights[x] = self.testWeights[x][sortPermutation]
            self.testCorrectionWeights[x] = self.testCorrectionWeights[x][sortPermutation]
            #self.testWeightsXS[x] = self.testWeightsXS[x][sortPermutation]

    def transposeTestSamples(self):
        """Transpose all test matrices."""

        for x in xrange(0,len(self.test)):
            self.test[x] = transpose(self.test[x])
            self.testLabels[x] = transpose(self.testLabels[x])
            self.testWeights[x] = transpose(self.testWeights[x])
            self.testCorrectionWeights[x] = transpose(self.testCorrectionWeights[x])
            #self.testWeightsXS[x] = transpose(self.testWeightsXS[x])


    def sortTrainSamples(self):
        """Sort the training samples and weights according to the labels."""
        for x in xrange(0,len(self.train)):
            sortPermutation = self.trainLabels[x].argsort()
            self.train[x] = self.train[x][sortPermutation]
            self.trainLabels[x] = self.trainLabels[x][sortPermutation]
            self.trainWeights[x] = self.trainWeights[x][sortPermutation]
            self.trainCorrectionWeights[x] = self.trainCorrectionWeights[x][sortPermutation]
            #self.trainWeightsXS[x] = self.trainWeightsXS[x][sortPermutation]

    def transposeTrainSamples(self):
        """Transpose all test matrices."""
        print len(self.train)
        for x in xrange(0,len(self.train)):
            self.train[x] = transpose(self.train[x])
            self.trainLabels[x] = transpose(self.trainLabels[x])
            self.trainWeights[x] = transpose(self.trainWeights[x])
            self.trainCorrectionWeights[x] = transpose(self.trainCorrectionWeights[x])
            #self.trainWeightsXS[x] = transpose(self.trainWeightsXS[x])

    def returnTrainWeightsXS(self, subset):
        """Return the array of per sample weights (xs)"""

        if subset == 'A' and self.trainWeightsXS:
            return self.trainWeightsXS[0]
        elif len(self.trainWeightsXS) > 1:
            return self.trainWeightsXS[1]
        else:
            return self.error()

    def returnTestWeightsXS(self, subset):
        """Return the array of per sample weights (xs)"""
        if subset == 'A' and self.testWeightsXS:
            return self.testWeightsXS[0]
        elif len(self.testWeightsXS) > 1:
            return self.testWeightsXS[1]
        return self.error()

    def returnTrainCorrectionWeights(self, subset):
        """Return the array of correction weights"""

        if subset == 'A' and self.trainCorrectionWeights:
            return self.trainCorrectionWeights[0]
        elif len(self.trainCorrectionWeights) > 1:
            return self.trainCorrectionWeights[1]
        else:
            return self.error()

    def returnTestCorrectionWeights(self, subset):
        """Return the array of correction weights"""

        if subset == 'A' and self.testCorrectionWeights:
            return self.testCorrectionWeights[0]
        elif len(self.testCorrectionWeights) > 1:
            return self.testCorrectionWeights[1]
        else:
            return self.error()

    def returnTestSample(self, subset = 'A'):
        """Return the test array of subset A or B"""
        if self.type.upper == 'DATA':
            return self.test[0]
        if subset == 'A' and self.test:
            return self.test[0]
        elif len(self.test) > 1:
            return self.test[1]
        return self.error()

    def returnTrainSample(self, subset):
        """Return the array of per sample weights (xs)"""
        if subset == 'A' and self.train:
            return self.train[0]
        elif len(self.train) > 1:
            return self.train[1]
        return self.error()

    def returnTestSampleLabels(self, subset):
        """Return the array of per sample weights (xs)"""
        if subset == 'A' and self.testLabels:
            return self.testLabels[0]
        elif len(self.testLabels) > 1:
            return self.testLabels[1]
        return self.error()

    def returnTrainSampleLabels(self, subset):
        """Return the array of per sample weights (xs)"""
        if subset == 'A' and self.trainLabels:
            return self.trainLabels[0]
        elif len(self.trainLabels) > 1:
            return self.trainLabels[1]
        return self.error()

    def returnFoundVariables(self):
        """Return found variables."""
        if self.variablesDone:
            return self.foundVariables
        else:
            return self.error()

    def error(self):
        print 'some error has occurred, returning -1'
        return -1
