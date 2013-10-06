from sklearn import svm
from time import clock
import copy
import numpy as np
import createHists

class SVMTrain:
    __all__= ['run','plot']
# Build a forest and compute the feature importances
    def __init__(self, foundVariables, trainingData, trainingClasses, trainingWeights, testingData, testingClasses):
        """Build a forest and compute the feature importances.
        
        Keyword args:
        foundVariables -- The list of the names of found variabes, can get using Sample_x.returnFoundVariables()
        trainingData -- The training data
        trainingClasses -- The training data classes
        testingData -- the testing data
        testingClasses -- the testing data classes
        """
        self.clf = svm.SVC(probability=True)
        self.foundVariables = foundVariables
        self.trainingData = trainingData
        self.trainingClasses = trainingClasses
        self.testingData = testingData
        self.testingClasses = testingClasses
        self.trainingWeights = trainingWeights



    def run(self):
        start = clock()
        self.clf.fit(self.trainingData, self.trainingClasses, self.trainingWeights)
        self.elapsed = clock()-start
        print 'time taken for training: ' + str(self.elapsed)
        xtA_D = copy.deepcopy(self.testingData)
        self.pred = self.clf.predict(xtA_D)
        
        createHists.drawSigBkgDistrib(xtA_D, self.pred, self.foundVariables)

        #importancessvm = clf.coef_
        self.score = self.clf.score(self.testingData, self.testingClasses)
        print self.score
        self.class_proba = self.clf.predict_proba(self.testingData)[:, -1]
        self.twoclass_output = self.clf.decision_function(self.testingData)


    def plot(self):
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        import matplotlib.pyplot as plt
        import pylab as pl

        plot_colors = "rb"
        plot_step = 1000.0
        class_names = "AB"
        pl.figure(figsize=(15, 5))
        # Plot the class probabilities
        for i, n, c in zip(xrange(2), class_names, plot_colors):
            pl.hist(self.class_proba[self.testingClasses == i],
                    bins=50,
                    range=(0, 1),
                    facecolor=c,
                    label='Class %s' % n)
        pl.legend(loc='upper center')
        pl.ylabel('Samples')
        pl.xlabel('Class Probability')

        # Plot the two-class decision scores


        pl.subplot(133)
        for i, n, c in zip(xrange(2), class_names, plot_colors):
            pl.hist(self.twoclass_output[self.testingClasses == i],
                    bins=50,
                    range=(0, 1),
                    facecolor=c,
                    label='Class %s' % n, normed=True)
        pl.legend(loc='upper right')
        pl.ylabel('Samples')
        pl.xlabel('Two-class Decision Scores')

        pl.subplots_adjust(wspace=0.25)
        mean_tpr = 0.0
        mean_fpr = linspace(0, 1, 100)
        pl.subplot(132)
        beginIdx = 0
        endIdx = len(self.testingData)#/2

        #tpr is signal efficiency: num(s)/total(s)
        for i in range(1):
            probas_ = self.clf.predict_proba(self.testingData[beginIdx:endIdx])
            # Compute ROC curve and area the curve
            fpr, tpr, thresholds, rej = sc.roc_curve_rej(self.testingClasses[beginIdx:endIdx], probas_[:,1])
            roc_auc = auc(tpr,rej)#auc(fpr, tpr)
            pl.plot(tpr, rej, lw=1, label='ROC fold %d (area = %0.2f)' % (i, roc_auc), color=plot_colors[i])
            beginIdx = endIdx
            endIdx = len(self.testingData)

        pl.show()



'''
indicessvm = argsort(importancessvm)[::-1]
variableNamesSorted = []
for i in indicessvm:
    variableNamesSorted.append(foundVariables[i])

# Print the feature ranking
print "Feature ranking:"

for f in xrange(12):
    print "%d. feature %d (%f)" % (f + 1, indicessvm[f], importancessvm[indicessvm[f]]) + " " +variableNamesSorted[f]


# Plot the feature importances of the forest
# We need this to run in batch because it complains about not being able to open display

pl.figure()
pl.title("Feature importances SVM")
pl.bar(xrange(len(variableNamesSorted)), importancessvm[indicessvm],
       color="r", align="center")
pl.xticks(xrange(12), variableNamesSorted)#indicesada)
pl.xlim([-1, 12])
pl.show()
'''
