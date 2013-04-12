numpy from import *
from root_numpy import *
import sys
# used to shuffle multiple arrays at once
import sortAndCut as sc

if len(sys.argv) < 2:
    print 'not enough arguments supplied, need argument for type of sample'
    sys.exit("not enough args supplied")

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

dataSample = root2array('./NtupledataAll.root','Ntuple')
    #save('./Ntuplebkg.npy',bkg)
#random.shuffle(bkg)
print 'len of sig: ' + str(len(sig))
print 'len of bkg: ' + str(len(bkg))
print 'len of data: ' +str(len(data))

#cut in half for training and testing, remove unwanted variables not for training
sigtempA = sc.cutTree(sig,True,len(sig)/2,'A')
sigtempB = sc.cutTree(sig,True,len(sig)/2,'B')
#print len(sigtemp)
bkgtempA = sc.cutTree(bkg,True,len(bkg)/2,'A')
bkgtempB = sc.cutTree(bkg,True,len(bkg)/2,'B')
#print len(bkgtemp)

# don't want to cut the data... we want it all
#datatempA = sc.cutTree(data,True,len(data/2),'A')
#datatempB = sc.cutTree(data,True,len(data/2),'B')


#keep indices of variables we want
varIdx = []
varIdxData = []
varWIdx = []
#variableNames = ['m_ll','m_Bb','MET','dPhi_VH', 'ptImbalanceSignificance', 'pt_V', 'pt_Bb', 'dR_Bb', 'acop_Bb', 'dEta_Bb', 'mv1_jet0', 'mv1_jet1']
variableNames = ['dRBB','dEtaBB','dPhiVBB','dPhiLMET','dPhiLBMin','pTV','mBB','HT','pTB1','pTB2','pTimbVH','mTW','pTL','MET']#,'mLL']
varWeightsHash = {'xs':-1,'xscorr1':-1,'xscorr2':-1,'final_xs':-1,'label':-1,'label_code':-1,'name':-1,'name_code':-1}
foundVariables = []
foundVariablesData = []

#get all of the indices of the variables in the dataset
#foundVariables, varIdx and varWeightsHash are mutable and changed in the method
sc.getVariableIndices(sig, foundVariables, varIdx, varWeightsHash, 'mc')
# we need to do this for data separately because of different branches
sc.getVariableIndices(data, foundVariablesData, varIdxData, blah={}, 'data')

#create the training trees/ arrays
#TODO: these should be stored in the xml settings file
nEntries = 14443742.0
lumi = 20300.0

sigTrainA,weightsSigTrainA, labelsSigTrainA = sc.cutCols(sigtempA, varIdx, len(sigtempA), len(variableNames), varWeightsHash, nEntries, lumi)
bkgTrainA,weightsBkgTrainA, labelsBkgTrainA = sc.cutCols(bkgtempA, varIdx, len(bkgtempA), len(variableNames), varWeightsHash, nEntries, lumi)
sigTrainB,weightsSigTrainB, labelsSigTrainB = sc.cutCols(sigtempB, varIdx, len(sigtempB), len(variableNames), varWeightsHash, nEntries, lumi)
bkgTrainB,weightsBkgTrainB, labelsBkgTrainB = sc.cutCols(bkgtempB, varIdx, len(bkgtempB), len(variableNames), varWeightsHash, nEntries, lumi)

dataCut = sc.cutColsData(dataSample, varIdxData, len(dataSample),len(variableNames), nEntries, lumi)



#add the training trees together, keeping track of which entries are signal and background
xtA = vstack((sigTrainA, bkgTrainA))
y11A = sc.onesInt(len(sigTrainA))
y21A = sc.zerosInt(len(bkgTrainA))
ytA = hstack((y11A, y21A))
ytA = transpose(ytA)
sigWeightA = 1.0#float(1/float(len(sigTrain)))
#print 'sigWeight ' + str(sigWeightA)
bkgWeightA = float(len(sigTrainA))/float(len(bkgTrainA))
#print 'bkgWeight ' + str(bkgWeightA)
weightsBkgA = sc.setWeights(len(bkgTrainA),bkgWeightA)
weightsSigA = sc.setWeights(len(sigTrainA),sigWeightA)
weightstA = hstack((weightsSigA,weightsBkgA))
weightstA = transpose(weightstA)

#add the training trees together, keeping track of which entries are signal and background
xtB = vstack((sigTrainB, bkgTrainB))
y11B = sc.onesInt(len(sigTrainB))
y21B = sc.zerosInt(len(bkgTrainB))
ytB = hstack((y11B, y21B))
ytB = transpose(ytB)
sigWeightB = 1.0#float(1/float(len(sigTrain)))
#print 'sigWeight ' + str(sigWeightB)
bkgWeightB = float(len(sigTrainB))/float(len(bkgTrainB))
#print 'bkgWeight ' + str(bkgWeightB)
weightsBkgB = sc.setWeights(len(bkgTrainB),bkgWeightB)
weightsSigB = sc.setWeights(len(sigTrainB),sigWeightB)
weightstB = hstack((weightsSigB,weightsBkgB))
weightstB = transpose(weightstB)

x =xtA
y = ytA
weights = weightstA
#x,y,weights = sc.shuffle_in_unison(xt,yt,weightst)

#print 'starting training on GradientBoostingClassifier'

from sklearn.ensemble import GradientBoostingClassifier

# parameters for boosting:
# GradientBoostingClassifier(loss='deviance', learning_rate=0.10000000000000001, n_estimators=100, subsample=1.0, min_samples_split=2, min_samples_leaf=1, max_depth=3, init=None, random_state=None, max_features=None, verbose=0)

#gb = GradientBoostingClassifier().fit(x,y)

#Test the fit on the other half of the data
sigtemp1A = sc.cutTree(sig,False,len(sig)/2,'A')
bkgtemp1A = sc.cutTree(bkg,False,len(bkg)/2,'A')

print sigtemp1A
labelCodes = sc.readInLabels(sys.argv[1])#typeOfSample should be signal or bkg
#find weightsPerSample on first run
sigTestA, weightsSigTestA, labelsSigTestA, weightsPerSigSample = sc.cutCols(sigtemp1A, varIdx, len(sigtemp1A), len(variableNames), varWeightsHash, nEntries, lumi, True, labelCodes)

sortPerm = labelsSigTestA.argsort()
#t_labelsSigTestA, t_sigTestA, t_weightsSigTestA = zip(*sorted(zip(labelsSigTestA,sigTestA,weightsSigTestA)))
sigTestA= sigTestA[sortPerm]#list(t_sigTestA)
weightsSigTestA = weightsSigTestA[sortPerm]#list(t_weightsSigTestA)
labelsSigTestA= labelsSigTestA[sortPerm]#list(t_labelsSigTestA)

#labelsSigTestA, sigTestA, weightsSigTestA = sc.sortMultiple(varWIdx['label_code'],labelsSigtestA,sigTestA,weightsSigTestA)
bkgTestA, weightsBkgTestA, labelsBkgTestA, weightsPerBkgSample = sc.cutCols(bkgtemp1A, varIdx, len(bkgtemp1A), len(variableNames), varWeightsHash, nEntries, lumi, True, labelCodes)
weightsPerSample = dict(weightsPerSigSample.items() + weightsPerBkgSample.items())
#for python 3 and greater use
#weightsPerSample = dict(list(weightsPerSigSample.items()) + list(weightsPerBkgSample.items()))
sortPermBkg = labelsBkgTestA.argsort()
#t_labelsBkgTestA, t_bkgTestA, t_weightsBkgTestA = zip(*sorted(zip(labelsBkgTestA,bkgTestA,weightsBkgTestA)))
bkgTestA= bkgTestA[sortPermBkg]#list(t_bkgTestA)
weightsBkgTestA = weightsBkgTestA[sortPermBkg]#list(t_weightsBkgTestA)
labelsBkgTestA= labelsBkgTestA[sortPermBkg]#list(t_labelsBkgTestA)


print 'weightsPerSample'
print weightsPerSample


x1A = vstack((sigTestA, bkgTestA))
y1A = hstack((sc.onesInt(len(sigTestA)), sc.zerosInt(len(bkgTestA))))
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

lblcount = 0

sigTestA = transpose(sigTestA)
bkgTestA = transpose(bkgTestA)

sigtemp1B = sc.cutTree(sig,False,len(sig)/2,'B')
bkgtemp1B = sc.cutTree(bkg,False,len(bkg)/2,'B')

sigTestB, weightsSigTestB, labelsSigTestB = sc.cutCols(sigtemp1B, varIdx, len(sigtemp1B), len(variableNames), varWeightsHash, nEntries, lumi)
#get the reordered, sorted index
sortPermB = labelsSigTestB.argsort()
#t_labelsSigTestB, t_sigTestB, t_weightsSigTestB = zip(*sorted(zip(labelsSigTestB,sigTestB,weightsSigTestB)))
#sort all of the arrays using the sorted index
sigTestB= sigTestB[sortPermB]
weightsSigTestB = weightsSigTestB[sortPermB]
labelsSigTestB= labelsSigTestB[sortPermB]

bkgTestB, weightsBkgTestB, labelsBkgTestB = sc.cutCols(bkgtemp1B, varIdx, len(bkgtemp1B), len(variableNames), varWeightsHash, nEntries, lumi)
#do the ordering for the background
sortPermBkgB = labelsBkgTestB.argsort()
#t_labelsBkgTestB, t_bkgTestB, t_weightsBkgTestB = zip(*sorted(zip(labelsBkgTestB,bkgTestB,weightsBkgTestB)))
bkgTestB= bkgTestB[sortPermBkgB]
weightsBkgTestB = weightsBkgTestB[sortPermBkgB]
labelsBkgTestB= labelsBkgTestB[sortPermB]



x1B = vstack((sigTestB, bkgTestB))
y1B = hstack((sc.onesInt(len(sigTestB)), sc.zerosInt(len(bkgTestB))))
y1B = transpose(y1B)
print 'starting testing'

sigTestB = transpose(sigTestB)
bkgTestB = transpose(bkgTestB)


count = 0
cols = []
for i in variableNames:
    cols.append(ones(len(sigTestA)))


allStack = []
legendAllStack = []
import CreateHists
# get sigA histograms
hist,histDictSigA,testAStack, legendSigStack = createHists.createHists(sigTestA, labelCodes, 'signal', labelsSigTestA, weightsPerSample, foundVariables, allStack, legendAllStack, True)
# get bkgA histograms
# how to fix legends????
hist2,histDictBkgA,testAStackBkg,legendBkgStack  = createHists.createHists(bkgTestA, labelCodes, 'bkg', labelsBkgTestA, weightsPerSample, foundVariables, allStack, legendAllStack, True)

histData,histDictDataA,testAStackData, legendDataStack = createHists.createHistsData(dataTestA, foundVariables, allStack, legendAllStack, True)


for hist2idx in xrange(0,len(hist)):


    legend = Legend(3)
    legend.AddEntry(hist[hist2idx],'F')
    legend.AddEntry(hist2[hist2idx],'F')
    legend.AddEntry(histData[hist2idx],'F')

    hist[hist2idx].draw('hist')
    hist[hist2idx].Write()
    hist2[hist2idx].draw('histsame')
    hist2[hist2idx].Write()
    histData[hist2idx].draw('same')
    histData[hist2idx].Write()

    legend.Draw('same')
    c1.Write()
    c1.SaveAs(foundVariables[hist2idx]+".png")
    hist2idx+=1

createHists.drawStack(testAStack, legendSigStack, 'Sig')
createHists.drawStack(testAStackBkg, legendBkgStack, 'Bkg')
createHists.drawStack(allStack, legendAllStack, 'Data', histData)
createHists.drawStack(allStack, legendAllStack, 'All')


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
