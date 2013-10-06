from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from time import clock
import copy
import numpy as np

class adaBoost:
    __all__=['run','plotFeatureRanking','plotScores']

    def __init__(self, foundVariables, trainingData, trainingClasses, trainingWeights, testingData, testingClasses, adaName, bkg_name):
        """Build a forest and compute the feature importances.
        
        Keyword args:
        foundVariables -- The list of the names of found variabes, can get using Sample_x.returnFoundVariables()
        trainingData -- The training data
        trainingClasses -- The training data classes
        testingData -- the testing data
        testingClasses -- the testing data classes
        adaName -- the name of the object (eg. sig+bkg_name)
        """
        self.ada = AdaBoostClassifier(DecisionTreeClassifier(compute_importances=True,max_depth=4,min_samples_split=2,min_samples_leaf=100),n_estimators=400, learning_rate=0.5, algorithm="SAMME",compute_importances=True)
        #class sklearn.tree.DecisionTreeClassifier(criterion='gini', max_depth=None, min_samples_split=2, min_samples_leaf=1, min_density=0.10000000000000001, max_features=None, compute_importances=False, random_state=None)
        self.foundVariables = foundVariables
        self.trainingData = trainingData
        self.trainingClasses = trainingClasses
        self.testingData = testingData
        self.testingClasses = testingClasses
        self.trainingWeights = trainingWeights
        self.name = adaName
        self.bkg_name = bkg_name
        self.elapsed = 0.0

    def returnName(self):
        return self.name

    def run(self):
        """Run the fitting and testing."""

    #start the fitting and time it
        start = clock()
        print 'starting training on AdaBoostClassifier'
        self.ada.fit(self.trainingData, self.trainingClasses, self.trainingWeights)
        self.elapsed = clock()-start
        print 'time taken for training: ' + str(self.elapsed)
    #set up the arrays for testing/ eval
        #xtA_C = copy.deepcopy(self.testingData)
        #pred = self.ada.predict(xtA_C)
        #import createHists
        #createHists.drawSigBkgDistrib(xtA_C, pred, self.foundVariables) # draw the signal and background distributions together

    # list the importances of each variable in the bdt, get the score on the test data
        self.importancesada = self.ada.feature_importances_
        print 'importances'
        print self.importancesada
        self.score= self.ada.score(self.testingData,self.testingClasses)
        self.params = self.ada.get_params()
        self.std_mat = np.std([tree.feature_importances_ for tree in self.ada.estimators_],
                           axis=0)
        self.indicesada = np.argsort(self.importancesada)[::-1]
        self.variableNamesSorted = []
        for i in self.indicesada:
            self.variableNamesSorted.append(self.foundVariables[i])

# Print the feature ranking
        print "Feature ranking:"

        for f in xrange(12):
            print "%d. feature %d (%f)" % (f + 1, self.indicesada[f], self.importancesada[self.indicesada[f]]) + " " +self.variableNamesSorted[f]
        self.twoclass_output = self.ada.decision_function(self.testingData)
        self.class_proba = self.ada.predict_proba(self.testingData)[:, -1]



    def plotFeatureRanking(self):
        # We need this to run in batch because it complains about not being able to open display
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        import matplotlib.pyplot as plt
        import pylab as pl

        #plot the feature ranking
        pl.figure()
        pl.title("Feature importances Ada")
        pl.bar(xrange(len(self.variableNamesSorted)), self.importancesada[self.indicesada],
               color="r", yerr=self.std_mat[self.indicesada], align="center")
        pl.xticks(xrange(12), self.variableNamesSorted)#indicesada)
        pl.xlim([-1, 12])
        pl.show()

    def plotScores(self):
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        import matplotlib.pyplot as plt
        import pylab as pl

        plot_colors = "rb"
        plot_step = 1000.0
        class_names = "AB"
    # Plot the training points 
        pl.subplot(131)
        for i, n, c in zip(xrange(2), class_names, plot_colors):
            idx = np.where(self.trainingClasses == i)
            pl.scatter(self.trainingData[idx, 0], self.trainingData[idx, 1],
                       c=c, cmap=pl.cm.Paired,
                       label="Class %s" % n)
        pl.axis("tight")
        pl.legend(loc='upper right')
        pl.xlabel("Decision Boundary")

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
    # Plot the two-class decision scores/ bdt scores
        pl.subplot(133)
        for i, n, c in zip(xrange(2), class_names, plot_colors):
            pl.hist(self.twoclass_output[self.testingClasses == i],
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
    
        pl.subplot(132)
        beginIdx = 0
        endIdx = len(self.testingData)#/2

        for i in range(1):
            probas_ = self.ada.predict_proba(self.testingData[beginIdx:endIdx])
    # Compute ROC curve and area the curve
            fpr, tpr, thresholds, rej = sc.roc_curve_rej(self.testingClasses[beginIdx:endIdx], probas_[:,1])
    #mean_tpr += interp(mean_fpr, fpr, tpr)
    #mean_tpr[0] = 0.0
            roc_auc = auc(tpr,rej)#auc(fpr, tpr)
            pl.plot(tpr, rej, lw=1, label='ROC fold %d (area = %0.2f)' % (i, roc_auc), color=plot_colors[i])
            beginIdx = endIdx
            endIdx = len(self.testingData)

        pl.show()
