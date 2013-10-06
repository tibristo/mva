from numpy import *
import adaBoost as ab
from root_numpy import *
import sys
import createHists
import sortAndCut as sc
import Sample
from rootpy.interactive import wait
from rootpy.plotting import Canvas, Hist, Hist2D, Hist3D, Legend
from rootpy.io import root_open as ropen, DoesNotExist
from rootpy.plotting import HistStack
import ROOT
import copy
from sklearn.metrics import roc_curve, auc
import ada_threading as a_t
import threading
ROOT.gROOT.SetBatch(True)

if len(sys.argv) < 1:
    print 'not enough arguments supplied, need argument for type of sample'
    sys.exit("not enough args supplied")

# read in samples and convert to numpy arrays
#sig = Sample.Sample('/Disk/speyside8/lhcb/atlas/tibristo/Ntuple120_sumet_sig12_FullCutflow.root','Ntuple','sig')
if len(sys.argv) > 1:
    if sys.argv[1] == 'el':
        sig = Sample.Sample('/media/Acer/mvaFiles/datatrig/Ntuple_jvf_sig_el12_FullCutflow.root','Ntuple','sig')
        bkg = Sample.Sample('/media/Acer/mvaFiles/datatrig/Ntuple_jvf_bkg_el12.root','Ntuple','bkg')
        dataSample = Sample.Sample('/media/Acer/mvaFiles/datatrig/Ntuple_jvf_dataEl12.root','Ntuple','data')
        print 'el channel'
    elif sys.argv[1] == 'mu':
        sig = Sample.Sample('/media/Acer/mvaFiles/datatrig/Ntuple_jvf_sig_mu12_FullCutflow.root','Ntuple','sig')
        bkg = Sample.Sample('/media/Acer/mvaFiles/datatrig/Ntuple_jvf_bkg_mu12.root','Ntuple','bkg')
        dataSample = Sample.Sample('/media/Acer/mvaFiles/datatrig/Ntuple_jvf_dataMu12.root','Ntuple','data')
        print 'mu channel'
    else:
        sig = Sample.Sample('/media/Acer/mvaFiles/trigger/Ntuple120_trigger_sig12_FullCutflow.root','Ntuple','sig')
        bkg = Sample.Sample('/media/Acer/mvaFiles/trigger/Ntuple120_trigger_bkg12.root','Ntuple','bkg')
        dataSample = Sample.Sample('/media/Acer/mvaFiles/trigger/Ntuple120_trigger_data12.root','Ntuple','data')
        print 'both channels'
else:
    sig = Sample.Sample('/media/Acer/mvaFiles/trigger/Ntuple120_trigger_sig12_FullCutflow.root','Ntuple','sig')
    bkg = Sample.Sample('/media/Acer/mvaFiles/trigger/Ntuple120_trigger_bkg12.root','Ntuple','bkg')
    dataSample = Sample.Sample('/media/Acer/mvaFiles/trigger/Ntuple120_trigger_data12.root','Ntuple','data')
    print 'both channels'
print 'Finished reading in all samples'

# keep indices of variables we want
varIdx = []
varIdxBkg = []
varIdxData = []
varWIdx = []
variablesNames = createHists.readVarNamesXML()
varWeightsHash = {'xs':-1,'xscorr1':-1,'xscorr2':-1,'final_xs':-1,'label':-1,'label_code':-1,'name':-1,'name_code':-1,'AllEntries':-1, 'VpT_truth':-1, 'dPhiVBB': -1, 'weight_MC' : -1, 'weight_PU' : -1, 'weight_lepton1' : -1, 'weight_MET' : -1}
varWeightsHashBkg = {'xs':-1,'xscorr1':-1,'xscorr2':-1,'final_xs':-1,'label':-1,'label_code':-1,'name':-1,'name_code':-1, 'AllEntries':-1, 'VpT_truth':-1, 'dPhiVBB': -1, 'weight_MC' : -1, 'weight_PU' : -1, 'weight_lepton1' : -1, 'weight_MET' : -1}
foundVariables = []
foundVariablesBkg = []
foundVariablesData = []

# cut in half for training and testing, remove unwanted variables not for training
# set up testing and training samples for signal and background

sig.getVariableNames(variablesNames, foundVariables, varIdx, varWeightsHash)
bkg.getVariableNames(variablesNames, foundVariablesBkg, varIdxBkg, varWeightsHashBkg)
dataSample.getVariableNames(variablesNames, foundVariablesData, varIdxData)

# create the training trees/ arrays
# TODO: these should be stored in the xml settings file
nEntries = 14443742.0
nEntries = 13600000.0 + 82900.0

lumi = 13000.00#20300.0
#lumi for 2011
#lumi = 4700.00
#lumi for 2012
#lumi = 20300.0
labelCodes = sc.readInLabels()

sig.getTrainingData(sig.returnFullLength()/2, 'A', nEntries, lumi, labelCodes)
sig.getTrainingData(sig.returnFullLength()/2, 'B', nEntries, lumi, labelCodes)
bkg.getTrainingData(bkg.returnFullLength()/2, 'A', nEntries, lumi, labelCodes)
bkg.getTrainingData(bkg.returnFullLength()/2, 'B', nEntries, lumi, labelCodes)

#nEntriesA = 1.0/(float((sig.returnLengthTrain('A')+bkg.returnLengthTrain('A')))/float((sig.returnFullLength() + bkg.returnFullLength())))
#nEntriesB = 1.0/(float((sig.returnLengthTrain('B')+bkg.returnLengthTrain('B')))/float((sig.returnFullLength() + bkg.returnFullLength())))

nEntriesSA = 1.0/(float((sig.returnLengthTrain('A')))/float(sig.returnFullLength()))
nEntriesSB = 1.0/(float((sig.returnLengthTrain('B')))/float(sig.returnFullLength()))
nEntriesBA = 1.0/(float((bkg.returnLengthTrain('A')))/float(bkg.returnFullLength()))
nEntriesBB = 1.0/(float((bkg.returnLengthTrain('B')))/float(bkg.returnFullLength()))

sig.weightAllTrainSamples('A', nEntriesSA)
bkg.weightAllTrainSamples('A', nEntriesBA)
sig.weightAllTrainSamples('B', nEntriesSB)
bkg.weightAllTrainSamples('B', nEntriesBB)

print 'Finished getting training data'

sig.sortTrainSamples()
bkg.sortTrainSamples()
print 'Finished sorting training samples'

# set up some training samples for A
xA, yA, weightsA = sc.combineWeights(sig, bkg, 'A', True)
xB, yB, weightsB = sc.combineWeights(sig, bkg, 'B', True)

x = xA
y = yA
weights = weightsA

# Set up the testing samples
sig.getTestingData(sig.returnFullLength(), 'A', nEntries, lumi, labelCodes)
sig.getTestingData(sig.returnFullLength(), 'B', nEntries, lumi, labelCodes)
bkg.getTestingData(bkg.returnFullLength(), 'A', nEntries, lumi, labelCodes)
bkg.getTestingData(bkg.returnFullLength(), 'B', nEntries, lumi, labelCodes)
dataSample.getTestingDataForData(nEntries, lumi)

############################################################# WORK IN PROGRESS #############################################



nEntriesSA = 1.0/(float((sig.returnLengthTest('A')))/float(sig.returnFullLength()))
nEntriesSB = 1.0/(float((sig.returnLengthTest('B')))/float(sig.returnFullLength()))
nEntriesBA = 1.0/(float((bkg.returnTestingBkgLength('A',bkg_type)))/float(bkg.returnTestingFullBkgLength(bkg_type)))
nEntriesBB = 1.0/(float((bkg.returnTestingBkgLength('B',bkg_type)))/float(bkg.returnTestingFullBkgLength(bkg_type)))

x_A, y_A, weights_A = sc.combineWeights(sig, bkg.returnBkg('A', bkg_type), 'A', True)
x_B, y_B, weights_B = sc.combineWeights(sig, bkg.returnBkg('B', bkg_type), 'B', True)

xtA, ytA, weightstA = sc.combineWeights(sig, bkg.returnBkg('A', bkg_type), 'A', False)
xtB, ytB, weightstB = sc.combineWeights(sig, bkg.returnBkg('B', bkg_type), 'B', False)

trainWeights_A = hstack((sig.returnTrainWeights('A'), bkg.returnTrainBkgWeights('A', bkg_type)))
weights_A =multiply(weights_A,trainWeights_A)
for xi in xrange(0, len(sig.returnTrainingSample('A'))):
    weights_A[xi] = 1.0*nEntriesSA
for xii in xrange(len(sig.returnTrainingSample('A')), trainWeights_A.shape[0]):
    weights_A[xii] *= nEntriesBA

trainWeights_B = hstack((sig.returnTrainWeights('B'), bkg.returnTrainBkgWeights('B', bkg_type)))
weights_B =multiply(weights_B,trainWeights_B)
for xi in xrange(0, len(sig.returnTrainingSample('B'))):
    weights_B[xi] = 1.0*nEntriesSB
for xii in xrange(len(sig.returnTrainingSample('B')), trainWeights_B.shape[0]):
    weights_B[xii] *= nEntriesBB

ada1 = ab.adaBoost(sig.returnFoundVariables(), x_A, y_A, weights_A, xtA, ytA)
ada2 = ab.adaBoost(sig.returnFoundVariables(), x_B, y_B, weights_B, xtB, ytB)
#need to multithread this

threadLock = threading.Lock()
threads = []
transformBDTs = True
try:
    # Create new threads
    threadA = a_t.adaThread(1, "Thread-A", 1, ada1)
    threadB = a_t.adaThread(2, "Thread-B", 2, ada2)
    
    # Start new Threads
    threadA.start()
    threadB.start()

    # Add threads to thread list
    threads.append(threadA)
    threads.append(threadB)

    # Wait for all threads to complete
    for t in threads:
        t.join()
    print "Exiting Main Thread"

except:
    print "Unable to start thread"
    transformBDTs = False

if transformBDTs: #can't run if threads failed
    createHists.createTransformedBDT(ada1.twoclass_output, ytA, ada2.twoclass_output, ytB)



#############################################################################################################################

nEntriesSA = 1.0/(float((sig.returnLengthTest('A')))/float(sig.returnFullLength()))
nEntriesSB = 1.0/(float((sig.returnLengthTest('B')))/float(sig.returnFullLength()))
nEntriesBA = 1.0/(float((bkg.returnLengthTest('A')))/float(bkg.returnFullLength()))
nEntriesBB = 1.0/(float((bkg.returnLengthTest('B')))/float(bkg.returnFullLength()))

sig.weightAllTestSamples('A', nEntriesSA)
bkg.weightAllTestSamples('A', nEntriesBA)
sig.weightAllTestSamples('B', nEntriesSB)
bkg.weightAllTestSamples('B', nEntriesBB)

xtA, ytA, weightstA = sc.combineWeights(sig, bkg, 'A', False)
xtB, ytB, weightstB = sc.combineWeights(sig, bkg, 'B', False)

sig.transposeTestSamples()
sig.transposeTrainSamples()
bkg.transposeTestSamples()
bkg.transposeTrainSamples()
dataSample.transposeDataTest()

trainWeightsXS_A = [dict(sig.returnTrainWeightsXS('A').items()), dict(bkg.returnTrainWeightsXS('A').items())]
#print trainWeightsXS_A
trainWeights_A = hstack((sig.returnTrainWeights('A'), bkg.returnTrainWeights('A')))
weights =multiply(weights,trainWeights_A)
for xi in xrange(0, len(sig.returnTrainingSample('A'))):
    weights[xi] = 1.0
trainWeightsXS_B = [dict(sig.returnTrainWeightsXS('B').items()), dict(bkg.returnTrainWeightsXS('B').items())]
trainWeights_B = hstack((sig.returnTrainWeights('B'), bkg.returnTrainWeights('B')))
weightsB =multiply(weightsB,trainWeights_B)
for xi in xrange(0, len(sig.returnTrainingSample('B'))):
    weightsB[xi] = 1.0
testWeightsXS_A = [dict(sig.returnTestWeightsXS('A').items()), dict(bkg.returnTestWeightsXS('A').items())]
#print testWeightsXS_A
testWeightsXS_B = [dict(sig.returnTestWeightsXS('B').items()), dict(bkg.returnTestWeightsXS('B').items())]

trainCorrWeights_A = hstack((sig.returnTrainCorrectionWeights('A'), bkg.returnTrainCorrectionWeights('A')))
trainCorrWeights_B = hstack((sig.returnTrainCorrectionWeights('B'), bkg.returnTrainCorrectionWeights('B')))
testCorrWeights_A = hstack((sig.returnTestCorrectionWeights('A'), bkg.returnTestCorrectionWeights('A')))
testCorrWeights_B = hstack((sig.returnTestCorrectionWeights('B'), bkg.returnTestCorrectionWeights('B')))
# for python 3 and greater use
# weightsPerSample = dict(list(weightsPerSigSample.items()) + list(weightsPerBkgSample.items()))

# draw all training and testing histograms
#createHists.drawAllTrainStacks(sig, bkg, dataSample, labelCodes, trainWeightsXS_A, trainWeightsXS_B, trainCorrWeights_A, trainCorrWeights_B)
#createHists.drawAllTestStacks(sig, bkg, dataSample, labelCodes, testWeightsXS_A, testWeightsXS_B, 'C', testCorrWeights_A, testCorrWeights_B)

import adaBoost as ab
ada1 = ab.adaBoost(sig.returnFoundVariables(), x, y, weights, xtA, ytA)
ada2 = ab.adaBoost(sig.returnFoundVariables(), xB, yB, weightsB, xtB, ytB)
#need to multithread this
import ada_threading as a_t
import threading
threadLock = threading.Lock()
threads = []
transformBDTs = True
try:
    # Create new threads
    threadA = a_t.adaThread(1, "Thread-A", 1, ada1)
    threadB = a_t.adaThread(2, "Thread-B", 2, ada2)
    
    # Start new Threads
    threadA.start()
    threadB.start()

    # Add threads to thread list
    threads.append(threadA)
    threads.append(threadB)

    # Wait for all threads to complete
    for t in threads:
        t.join()
    print "Exiting Main Thread"

except:
    print "Unable to start thread"
    transformBDTs = False
ada1.plotScores()
ada2.plotScores()
if transformBDTs: #can't run if threads failed
    createHists.createTransformedBDT(ada1.twoclass_output, ytA, ada2.twoclass_output, ytB)

print 'type Enter to quit'
raw_input()

################################################################################
################### Train SVM
################################################################################
