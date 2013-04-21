class Sample():
    from numpy import *
    from root_numpy import *
    import sys
    import createHists
    import sortAndCut as sc

    trainingSet = []
    testingSet = []
    variablesDone = False

    # TODO: creating class that handles a sample: signal/ bkg/ data
    #       - It needs to hold a training and testing array for each, labels, weights
    #       - This makes it easier to do training and testing, and it makes it more readable
    #       - Still need to decide where drawing of histograms gets done
    def __init__ (self, filename, treename, typeOfSample):
        self.sample = root2array(filename,treename)
        self.sample_length = len(self.sample)
        typeUpper = typeOfSample.upper()
        if (typeUpper!='DATA' or typeUpper!='SIG' or typeUpper!='BKG'):
            print 'Type ' + str(typeOfSample) + ' not known, setting to bkg mc'
            self.type = 'bkg'
        self.type = typeOfSample
        
    def returnFullLength(self):
        """Return the length of the full input sample"""
        return self.sample_length
    
    def returnFullSmaple(self):
        return self.sample
    
    def returnSampleType(self):
        """Return data type of input sample."""
        return self.type

    
    # Split for training and testing, remove unwanted variables not for training
    def splitTree(self,training, splitSize, sampleLabel):
        """Return subset of full sample based on training/ testing, length and A or B sample"""
        self.tempSet = sc.cutTree(self.sample,training,splitSize,sampleLabel)
        return self.tempSet

    def returnTemp(self):
        """Return subset of temp sample without recalculating."""
        return self.tempSet

    def returnTempLength(self):
        """Return length of temp sample."""
        return len(self.tempSet)

    def getVariableNames(self, variableNames, foundVariables, varIdx, varWeightsHash):
        """Get all of the indices of the variables in the dataset."""
    # foundVariables, varIdx and varWeightsHash are mutable and changed in the method
        if self.type != 'data':
            sc.getVariableIndices(self.sample, variableNames, foundVariables, varIdx, varWeightsHash, 'mc')
        else:
            # we need to do this for data separately because of different branches
            blah = {}
            sc.getVariableIndices(self.sample, variableNames, foundVariables, varIdx, blah, 'data')
        setVariableNames(variableNames, foundVariables, varIdx, varWeightsHash)

    def setVariableNames(self, variableNames, foundVariables, varIdx, varWeightsHash):
        self.variableNames = copy.deepcopy(variableNames)
        self.varIdx = copy.deepcopy(varIdx)
        self.foundVariables = copy.deepcopy(foundVariables)
        self.varWeightsHash = copy.deepcopy(varWeightsHash)
        self.variablesDone = True


    def returnVariableData(self):
        if not variablesDone:
            return -1
        return self.variableNames, self.varIdx, self.foundVariables, self.varWeightsHash

    # get all of the training data needed
    def getTrainingData(self, nEntriesA, lumi):
        self.train, self.weightsTrain, self.labelsTrain = sc.cutCols(returnTemp(), varIdx, returnTempLength(), len(self.variableNames), self.varWeightsHash, nEntriesA, lumi) # signal set A

    def getTestingDataForData(self, nEntriesA, lumi):
        if not variablesDone:
            return -1
        self.test = sc.cutColsData(self.sample, self.varIdx, len(dataSample),len(variableNames), nEntries, lumi) # data set

# add the training trees together, keeping track of which entries are signal and background
xtA = vstack((sigTrainA, bkgTrainA))
ytA = transpose(hstack(( sc.onesInt(len(sigTrainA)), sc.zerosInt(len(bkgTrainA)) )))
sigWeightA = 1.0 # float(1/float(len(sigTrain)))
bkgWeightA = float(len(sigTrainA))/float(len(bkgTrainA)) # weight background as ratio
weightsBkgA = sc.setWeights(len(bkgTrainA),bkgWeightA)
weightsSigA = sc.setWeights(len(sigTrainA),sigWeightA)
weightstA = transpose(hstack((weightsSigA,weightsBkgA)))

# add the training trees together, keeping track of which entries are signal and background
xtB = vstack((sigTrainB, bkgTrainB))
ytB = transpose(hstack(( sc.onesInt(len(sigTrainB)), sc.zerosInt(len(bkgTrainB)) )))
sigWeightB = 1.0 #float(1/float(len(sigTrain)))
bkgWeightB = float(len(sigTrainB))/float(len(bkgTrainB))
weightsBkgB = sc.setWeights(len(bkgTrainB),bkgWeightB)
weightsSigB = sc.setWeights(len(sigTrainB),sigWeightB)
weightstB = transpose(hstack((weightsSigB,weightsBkgB)))

x = xtA
y = ytA
weights = weightstA

# from sklearn.ensemble import GradientBoostingClassifier

# parameters for boosting:
# GradientBoostingClassifier(loss='deviance', learning_rate=0.10000000000000001, n_estimators=100, subsample=1.0, min_samples_split=2, min_samples_leaf=1, max_depth=3, init=None, random_state=None, max_features=None, verbose=0)

#gb = GradientBoostingClassifier().fit(x,y)

# Test the fit on the other half of the data
sigtemp1A = sc.cutTree(sig,False,len(sig)/2,'A')
bkgtemp1A = sc.cutTree(bkg,False,len(bkg)/2,'A')


labelCodes = sc.readInLabels(sys.argv[1]) # typeOfSample should be signal or bkg
# get all testing arrays, event weights, labels and weight per sample for xs and lumi
sigTestA, weightsSigTestA, labelsSigTestA, weightsPerSigSample = sc.cutCols(sigtemp1A, varIdx, len(sigtemp1A), len(variableNames), varWeightsHash, nEntries, lumi, True, labelCodes)


sortPerm = labelsSigTestA.argsort() # gives the sorting permutation
#t_labelsSigTestA, t_sigTestA, t_weightsSigTestA = zip(*sorted(zip(labelsSigTestA,sigTestA,weightsSigTestA)))
sigTestA = sigTestA[sortPerm] # sort according to the correct permutation
weightsSigTestA = weightsSigTestA[sortPerm]
labelsSigTestA = labelsSigTestA[sortPerm]

bkgTestA, weightsBkgTestA, labelsBkgTestA, weightsPerBkgSample = sc.cutCols(bkgtemp1A, varIdx, len(bkgtemp1A), len(variableNames), varWeightsHash, nEntries, lumi, True, labelCodes)

weightsPerSample = dict(weightsPerSigSample.items() + weightsPerBkgSample.items())
# for python 3 and greater use
# weightsPerSample = dict(list(weightsPerSigSample.items()) + list(weightsPerBkgSample.items()))

sortPermBkg = labelsBkgTestA.argsort() # get the sorting permutation for the background
#t_labelsBkgTestA, t_bkgTestA, t_weightsBkgTestA = zip(*sorted(zip(labelsBkgTestA,bkgTestA,weightsBkgTestA)))
bkgTestA = bkgTestA[sortPermBkg] # sort according to permutation
weightsBkgTestA = weightsBkgTestA[sortPermBkg]
labelsBkgTestA = labelsBkgTestA[sortPermBkg]

sigTestA = transpose(sigTestA)
bkgTestA = transpose(bkgTestA)

x1A = vstack((sigTestA, bkgTestA))
y1A = transpose(hstack((sc.onesInt(len(sigTestA)), sc.zerosInt(len(bkgTestA)))))

from rootpy.interactive import wait
from rootpy.plotting import Canvas, Hist, Hist2D, Hist3D, Legend
from rootpy.io import root_open as ropen, DoesNotExist
from rootpy.plotting import HistStack
import ROOT
ROOT.gROOT.SetBatch(True)
  
# store all histograms in output.root
f = ropen('output.root','recreate')
c1 = Canvas()
c1.cd()

sigtemp1B = sc.cutTree(sig,False,len(sig)/2,'B')
bkgtemp1B = sc.cutTree(bkg,False,len(bkg)/2,'B')

sigTestB, weightsSigTestB, labelsSigTestB = sc.cutCols(sigtemp1B, varIdx, len(sigtemp1B), len(variableNames), varWeightsHash, nEntries, lumi)
# get the reordered, sorted index
sortPermB = labelsSigTestB.argsort()
#t_labelsSigTestB, t_sigTestB, t_weightsSigTestB = zip(*sorted(zip(labelsSigTestB,sigTestB,weightsSigTestB)))
# sort all of the arrays using the sorted index
sigTestB= sigTestB[sortPermB]
weightsSigTestB = weightsSigTestB[sortPermB]
labelsSigTestB= labelsSigTestB[sortPermB]

bkgTestB, weightsBkgTestB, labelsBkgTestB = sc.cutCols(bkgtemp1B, varIdx, len(bkgtemp1B), len(variableNames), varWeightsHash, nEntries, lumi)
# do the ordering for the background
sortPermBkgB = labelsBkgTestB.argsort()
#t_labelsBkgTestB, t_bkgTestB, t_weightsBkgTestB = zip(*sorted(zip(labelsBkgTestB,bkgTestB,weightsBkgTestB)))
bkgTestB= bkgTestB[sortPermBkgB]
weightsBkgTestB = weightsBkgTestB[sortPermBkgB]
labelsBkgTestB= labelsBkgTestB[sortPermB]

x1B = vstack((sigTestB, bkgTestB))
y1B = transpose(hstack((sc.onesInt(len(sigTestB)), sc.zerosInt(len(bkgTestB)))))

sigTestB = transpose(sigTestB)
bkgTestB = transpose(bkgTestB)
dataCut = transpose(dataCut)

count = 0
cols = []
for i in variableNames:
    cols.append(ones(len(sigTestA)))


allStack = []
legendAllStack = []

