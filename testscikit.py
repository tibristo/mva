from numpy import *
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
ROOT.gROOT.SetBatch(True)

if len(sys.argv) < 2:
    print 'not enough arguments supplied, need argument for type of sample'
    sys.exit("not enough args supplied")

# read in samples and convert to numpy arrays
sig = Sample('./Ntuplesignal.root','Ntuple','sig')
bkg = Sample('./Ntuplebkg.root','Ntuple','bkg')
dataSample = Sample('./NtupledataAll.root','Ntuple','data')

# keep indices of variables we want
varIdx = []
varIdxData = []
varWIdx = []
variablesNames = createHists.readVarNamesXML()
varWeightsHash = {'xs':-1,'xscorr1':-1,'xscorr2':-1,'final_xs':-1,'label':-1,'label_code':-1,'name':-1,'name_code':-1}
foundVariables = []
foundVariablesData = []

# cut in half for training and testing, remove unwanted variables not for training
# set up testing and training samples for signal and background
sig.getVariableNames(variablesNames, foundVariables, varIdx, varWeightsHash)
dataSample.getVariableNames(variableNames, foundVariablesData, varIdxData)
# create the training trees/ arrays
# TODO: these should be stored in the xml settings file
nEntries = 14443742.0

lumi = 20300.0
#lumi for 2011
#lumi = 4700.00
#lumi for 2012
#lumi = 20300.0
# need to weight nEntries by ratio since sig and bkg samples are split in half! len(A)/len(total)
nEntriesA = nEntries*(float((sig.returnLengthTrain('A')+bkg.returnLengthTrain('A')))/float((sig.returnFullLength() + bkg.returnFullLength())))
nEntriesB = nEntries*(float((sig.returnLengthTrain('B')+bkg.returnLengthTrain('B')))/float((sig.returnFullLength() + bkg.returnFullLength())))
labelCodes = sc.readInLabels(sys.argv[1]) # typeOfSample should be signal or bkg

sig.getTrainingData(sig.returnFullLength/2, 'A', nEntriesA, lumi, labelCodes)
sig.getTrainingData(sig.returnFullLength/2, 'B', nEntriesB, lumi, labelCodes)
bkg.getTrainingData(bkg.returnFullLength/2, 'A', nEntriesA, lumi, labelCodes)
bkg.getTrainingData(bkg.returnFullLength/2, 'B', nEntriesB, lumi, labelCodes)
# might not need to sort and transpose these ones!
sig.sortTrainSamples()
bkg.sortTrainSamples()

# set up some training samples for A
xA, yA, weightsA = sc.combineWeights(sig.getTrainingSample('A'), bkg.getTrainingSample('B'))
xB, yB, weightsB = sc.combineWeights(sig.getTrainingSample('B'), bkg.getTrainingSample('B'))

x = xtA
y = ytA
weights = weightstA

# Set up the testing samples
sig.getTestingData(sig.returnFullLength/2, 'A', nEntriesA, lumi, labelCodes)
sig.getTestingData(sig.returnFullLength/2, 'B', nEntriesB, lumi, labelCodes)
bkg.getTestingData(bkg.returnFullLength/2, 'A', nEntriesA, lumi, labelCodes)
bkg.getTestingData(bkg.returnFullLength/2, 'B', nEntriesB, lumi, labelCodes)
dataSample.getTestingDataforData(nEntries, lumi)

trainweightsXS_A = dict(sig.returnTrainWeightsXS('A').items() + bkg.returnTrainWeightsXS('A').items())
trainweightsXS_B = dict(sig.returnTrainWeightsXS('B').items() + bkg.returnTrainWeightsXS('B').items())
testweightsXS_A = dict(sig.returnTestWeightsXS('A').items() + bkg.returnTestWeightsXS('A').items())
testweightsXS_B = dict(sig.returnTestWeightsXS('B').items() + bkg.returnTestWeightsXS('B').items())
# for python 3 and greater use
# weightsPerSample = dict(list(weightsPerSigSample.items()) + list(weightsPerBkgSample.items()))

sig.transposeTestSamples()
bkg.transposeTestSamples()
dataSample.transposeDataTest()

# draw all training and testing histograms
createHists.drawAllTrainStacks(sig, bkg, dataSample, labelCodes, trainWeightsXS_A, trainWeightsXS_B)
createHists.drawAllTestStacks(sig, bkg, dataSample, labelCodes, testWeightsXS_A, testWeightsXS_B)



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
    fpr, tpr, thresholds, rej = sc.roc_curve_rej(yt[beginIdx:endIdx], probas_[:,1])
    #mean_tpr += interp(mean_fpr, fpr, tpr)
    #mean_tpr[0] = 0.0
    roc_auc = auc(tpr,rej)#auc(fpr, tpr)
    print i
    pl.plot(tpr, rej, lw=1, label='ROC fold %d (area = %0.2f)' % (i, roc_auc), color=plot_colors[i])
    beginIdx = endIdx
    endIdx = len(xt)

pl.show()
'''
