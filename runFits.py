#@lview.parallel
def runFits(ada):
    import pickle
    with open(ada,'r') as f:
        adax = pickle.load(f)
    #adax = copy.deepcopy(ada)
    try:
        adax.run()
        adaNew = ada[:len(ada)-7]+'_trained.pickle'
        with open(adaNew, 'w') as g:
            pickle.dump(adax, g)
        return adaNew
    except:
        return 'error doing adaBoost training!'
    
