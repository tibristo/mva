from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from time import clock
import copy
import numpy as np
import sortAndCut as sc

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
        self.twoclass_output_train = self.ada.decision_function(self.trainingData)
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

    def plotScores(self, returnROC = False, rocInput = []):
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        import matplotlib.pyplot as plt
        import pylab as pl
        from sklearn.metrics import roc_curve, auc

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
        mean_fpr = pl.linspace(0, 1, 100)
    
        pl.subplot(132)
        beginIdx = 0
        endIdx = len(self.testingData)#/2

        fpr_arr = []
        tpr_arr = []
        roc_auc_arr = []
        rej_arr = []

        for i in range(1):
            probas_ = self.ada.predict_proba(self.testingData[beginIdx:endIdx])
            #probas_ = self.ada.predict_proba(self.testingData[self.testingClasses == i])
    # Compute ROC curve and area the curve
            fpr, tpr, thresholds, rej = sc.roc_curve_rej(self.testingClasses[beginIdx:endIdx], probas_[:,1])
            #fpr, tpr, thresholds, rej = sc.roc_curve_rej(self.testingClasses[self.testingClasses == i], probas_[:,1],i)
    #mean_tpr += interp(mean_fpr, fpr, tpr)
    #mean_tpr[0] = 0.0
            roc_auc = auc(tpr,rej)#auc(fpr, tpr)
            fpr_arr.append(fpr)
            tpr_arr.append(tpr)
            roc_auc_arr.append(roc_auc)
            rej_arr.append(rej)
            pl.plot(tpr_arr[i], rej_arr[i], lw=1, label='ROC fold %d (area = %0.2f)' % (i, roc_auc_arr[i]), color=plot_colors[i])
            beginIdx = endIdx
            endIdx = len(self.testingData)
        if len(rocInput)>0:
            pl.plot(rocInput[1][0], rocInput[3][0], lw=1, label='ROC fold %d (area = %0.2f)' % (2, rocInput[2][0]), color=plot_colors[1])
        if returnROC:
            return [fpr_arr, tpr_arr, roc_auc_arr, rej_arr]

        pl.show()

    def plotROC(self, returnROC = False, rocInput = []):
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        import matplotlib.pyplot as plt
        import pylab as pl
        from sklearn.metrics import roc_curve, auc
        beginIdx = 0
        endIdx = len(self.testingData)#/2
        plot_colors = "rb"
        plot_step = 1000.0
        class_names = "AB"
        fpr_arr = []
        tpr_arr = []
        roc_auc_arr = []
        rej_arr = []
        names = []

        pl.xlabel("Efficiency")
        pl.ylabel("Rejection") 
        pl.title("ROC curves")

        for i in range(1):
            probas_ = self.ada.predict_proba(self.testingData[beginIdx:endIdx])
            #probas_ = self.ada.predict_proba(self.testingData[self.testingClasses == i])
    # Compute ROC curve and area the curve
            fpr, tpr, thresholds, rej = sc.roc_curve_rej(self.testingClasses[beginIdx:endIdx], probas_[:,1])
            #fpr, tpr, thresholds, rej = sc.roc_curve_rej(self.testingClasses[self.testingClasses == i], probas_[:,1],i)
    #mean_tpr += interp(mean_fpr, fpr, tpr)
    #mean_tpr[0] = 0.0
            roc_auc = auc(tpr,rej)#auc(fpr, tpr)
            fpr_arr.append(fpr)
            tpr_arr.append(tpr)
            roc_auc_arr.append(roc_auc)
            rej_arr.append(rej)
            names.append(self.name)
            if not returnROC:
                pl.plot(tpr_arr[i], rej_arr[i], lw=1, label='ROC %s (area = %0.2f)' % (self.name, roc_auc_arr[i]), color=plot_colors[i])
            beginIdx = endIdx
            endIdx = len(self.testingData)
        if len(rocInput)>0:
            pl.plot(rocInput[1][0], rocInput[3][0], lw=1, label='ROC %s (area = %0.2f)' % (rocInput[4][0], rocInput[2][0]), color=plot_colors[1])
            pl.legend(loc='lower left')
            pl.savefig("roc_combined_"+self.name+".png")
        if returnROC:
            return [fpr_arr, tpr_arr, roc_auc_arr, rej_arr, names]
        pl.show()
        
    def plotDecisionBoundaries(self):
        import numpy as np
        import pylab as pl
        from matplotlib.colors import ListedColormap
        from sklearn.preprocessing import StandardScaler
        #from sklearn.cross_validation import train_test_split
         # just plot the dataset first
        cm = pl.cm.RdBu
        cm_bright = ListedColormap(['#FF0000', '#0000FF'])
        #self.trainingData = StandardScaler().fit_transform(self.trainingData)
        #self.testingData = StandardScaler().fit_transform(self.testingData)
        #X_train = StandardScaler().fit_transform(self.twoclass_output_train)
        h = 0.1
        h2 = 0.01
        #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.4)
        # get most important variable indices
        idx1 = self.foundVariables.index(self.variableNamesSorted[0])
        idx2 = self.foundVariables.index(self.variableNamesSorted[1])
        
        x_min, x_max = self.trainingData[np.argmin(self.trainingData[:, idx1])][idx1] - .1, self.trainingData[np.argmax(self.trainingData[:, idx1])][idx1] + .1
        y_min, y_max = self.trainingData[np.argmin(self.trainingData[:, idx2])][idx2]- .01, self.trainingData[np.argmax(self.trainingData[:,idx2])][idx2] + .01
        x_min2, x_max2 = self.testingData[np.argmin(self.testingData[:, idx1])][idx1] - .1, self.testingData[np.argmax(self.testingData[:, idx1])][idx1] + .1
        y_min2, y_max2 = self.testingData[np.argmin(self.testingData[:, idx2])][idx2] - .01, self.testingData[np.argmax(self.testingData[:, idx2])][idx2] + .01

        xmin = min(x_min,x_min2)
        xmax = max(x_max,x_max2)
        ymin = min(y_min, y_min2)
        ymax = max(y_max,y_max2)
        xx, yy = np.meshgrid(np.arange(xmin, xmax, float((xmax-xmin)/25.0)),
                             np.arange(ymin, ymax, float((ymax-ymin)/25.0)))

        # get mean values for other variables
        means = np.mean(self.testingData, axis=0)
        means = np.tile(means, (xx.shape[1]*xx.shape[0],1))
        for j in xrange(xx.shape[0]):
            for k in xrange(xx.shape[1]):
                means[(j+1)*(k+1)-1][idx1] = xx[0][j]
                means[(j+1)*(k+1)-1][idx2] = yy[k][0]
        #print 'shape X: '
        #print X.shape
        print 'shape xx: '
        print xx.shape
        print 'shape yy: '
        print yy.shape

        #rav = np.c_[xx.ravel(), yy.ravel()]
        print 'shape means: '
        print means.shape
        # Plot the decision boundary. For that, we will assign a color to each
        # point in the mesh [x_min, m_max]x[y_min, y_max].
        #if hasattr(clf, "decision_function"):
        #    Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
        #else:
        Z = self.ada.predict_proba(means)[:, 1]
        print 'Z shape:'
        print Z.shape
        # Put the result into a color plot
        Z = Z.reshape(xx.shape)
        figure = pl.figure()
        ax = pl.axes()
        ax.contourf(xx, yy, Z, cmap=cm, alpha=.8)

        # Plot also the training points
        #for i, n in zip(xrange(2), class_names):
        #    idx = np.where(self.trainingClasses == i)
        ax.scatter(self.trainingData[:, idx1], self.trainingData[:, idx2],
                   c=self.trainingClasses[:], cmap=cm_bright)
        #for i, n in zip(xrange(2), class_names):
        #    idx = np.where(self.testingClasses == i)
        ax.scatter(self.testingData[:, idx1], self.testingData[:, idx2],
                       c=self.testingClasses[:], cmap=cm_bright, alpha=0.6)

        #ax.scatter(X_train[:, 0], X_training[:, 1], c=self.trainingClasses, cmap=cm_bright)
        # and testing points
        #ax.scatter(X[:, 0], X[:, 1], c=self.testingClasses, cmap=cm_bright,
        #           alpha=0.6)

        ax.set_xlim(xx.min(), xx.max())
        ax.set_ylim(yy.min(), yy.max())
        ax.set_xticks(())
        ax.set_yticks(())
        ax.set_title("adaBoost")
        ax.text(xx.max() - .3, yy.min() + .3, ('%.2f' % self.score).lstrip('0'),
                size=15, horizontalalignment='right')
        pl.savefig("adaBoostDecisionBoundaries"+self.name+".png")
        pl.show()
