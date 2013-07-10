print 'starting training on DecisionTreeClassifier'
#class sklearn.tree.DecisionTreeClassifier(criterion='gini', max_depth=None, min_samples_split=2, min_samples_leaf=1, min_density=0.10000000000000001, max_features=None, compute_importances=False, random_state=None)

from sklearn.tree import DecisionTreeClassifier
'''
# Build a forest and compute the feature importances
dectree = DecisionTreeClassifier(compute_importances=True)

dectree.fit(x, y)
importancesdectree = dectree.feature_importances_
print importancesdectree
print dectree.score(x1,y1)
'''
'''
std = std([tree.feature_importances_ for tree in dectree.estimators_],
             axis=0)
indicesdectree = argsort(importancesdectree)[::-1]

# Print the feature ranking
print "Feature ranking:"

for f in xrange(12):
    print "%d. feature %d (%f)" % (f + 1, indicesdectree[f], importancesdectree[indicesdectree[f]])


# Plot the feature importances of the forest
import pylab as pl
pl.figure()
pl.title("Feature importances Dectreeom")
pl.bar(xrange(12), importancesdectree[indicesdectree],
       color="r", yerr=std[indicesdectree], align="center")
pl.xticks(xrange(12), indicesdectree)
pl.xlim([-1, 12])
pl.show()
'''

