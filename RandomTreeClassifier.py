print 'starting training on randomforestclassifier'

#class sklearn.ensemble.RandomForestClassifier(n_estimators=12, criterion='gini', max_depth=None, min_samples_split=2, min_samples_leaf=1, min_density=0.1, max_features='auto', bootstrap=True, compute_importances=False, oob_score=False, n_jobs=1, random_state=None, verbose=0)
'''
from sklearn.ensemble import RandomForestClassifier

# Build a forest and compute the feature importances
forestrand = RandomForestClassifier(n_estimators=400,
                              compute_importances=True,
                              random_state=0)

forestrand.fit(x, y)
importancesrand = forestrand.feature_importances_
std = std([tree.feature_importances_ for tree in forestrand.estimators_],
             axis=0)
indicesrand = argsort(importancesrand)[::-1]

# Print the feature ranking
print "Feature ranking:"

for f in xrange(12):
    print "%d. feature %d (%f)" % (f + 1, indicesrand[f], importancesrand[indicesrand[f]])

# Plot the feature importances of the forest
import pylab as pl
pl.figure()
pl.title("Feature importances Random")
pl.bar(xrange(12), importancesrand[indicesrand],
       color="r", yerr=std[indicesrand], align="center")
pl.xticks(xrange(12), indicesrand)
pl.xlim([-1, 12])
pl.show()
'''






