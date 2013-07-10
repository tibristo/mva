
'''
print 'starting training on ExtraTreesClassifier'
#class sklearn.ensemble.ExtraTreesClassifier(n_estimators=10, criterion='gini', max_depth=None, min_samples_split=2, min_samples_leaf=1, min_density=0.1, max_features='auto', bootstrap=False, compute_importances=False, oob_score=False, n_jobs=1, random_state=None, verbose=0)
from sklearn.ensemble import ExtraTreesClassifier

# Build a forest and compute the feature importances
forest = ExtraTreesClassifier(n_estimators=400,
                              compute_importances=True,
                              random_state=0)

forest.fit(x, y)
importances = forest.feature_importances_
std = std([tree.feature_importances_ for tree in forest.estimators_],
             axis=0)
indices = argsort(importances)[::-1]

# Print the feature ranking
print "Feature ranking:"

for f in xrange(12):
    print "%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]])
'''

'''
# Plot the feature importances of the forest
import pylab as pl
pl.figure()
pl.title("Feature importances")
pl.bar(xrange(12), importances[indices],
       color="r", yerr=std[indices], align="center")
pl.xticks(xrange(12), indices)
pl.xlim([-1, 12])
pl.show()
'''
