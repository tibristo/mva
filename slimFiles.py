import ROOT,sys,copy
selectedFolders = ['SelectedPosMuTrig','SelectedNegMuTrig', 'SelectedPosElTrig', 'SelectedNegElTrig']

log = open('log_slimmedout.txt','w')
inFile = ROOT.TFile(sys.argv[1],'READ')
inFile_curr = ''
outFile = ROOT.TFile(str(sys.argv[1]+'_slimmed.root'),'RECREATE')

def getAllEntries(dirIn, key):
    global log
    hist = dirIn.Get(key.GetName())
    entries = -1
    for lab in hist.GetXaxis().GetLabels():
        labname = lab.GetName()
        if labname.lower().find("all")!=-1:
            bin = hist.GetXaxis().FindBin(labname)
            bincont = hist.GetBinContent(bin)
            if bincont >= 1.0 and bincont%int(bincont) == 0.0:
                entries = int(bincont)
                continue
            else:
                entries = int(bincont)
    log.write(str(key.GetName()) + ' ' + str(entries))
    #return entries

def combineTrees(dirIn, pid, chain):
    for key in dirIn.GetListOfKeys():
        cl_name = dirIn.Get(key.GetName()).ClassName()
        if key.GetName() in selectedFolders:
            new_dir = dirIn.Get(key.GetName())
            print 'adding ntuple'
            print new_dir
            #tree = new_dir.Get(key.GetName()+'Ntuple').Clone()
            #tree.SetName('Ntuple')
            chain.Add(new_dir.Get(key.GetName()+'Ntuple'))#tree)
            #get the ntuple!
        elif cl_name == 'TDirectoryFile':
            combineTrees(dirIn.Get(key.GetName()), pid, chain)
        elif (cl_name == 'TH1F' or cl_name == 'TH1D') and key.GetName().endswith('BaselineOneLepton'):
            getAllEntries(dirIn, key)

def readPIDs(dirIn, pid):
    global inFile,outFile,inFile_curr
    inFile_curr = copy.deepcopy(dirIn.GetName())
    for key in dirIn.GetListOfKeys():
        entries = 0
        cl_name = dirIn.Get(key.GetName()).ClassName()
        if key.GetName().find("pid") != -1:
            #print 'found pid'
            pid = key.GetName()
            print pid
            #chain = ROOT.TChain('Ntuple')
            treelist = ROOT.TList()
            combineTrees(dirIn.Get(key.GetName()), key.GetName(), treelist)
            outFile.cd()
            outFile.mkdir(pid)
            outFile.cd(pid)
            outTree = ROOT.TTree.MergeTrees(treelist)#.Write()
            outTree.Write()
            print inFile_curr
            inFile.cd(inFile_curr)
        elif cl_name == 'TDirectoryFile':
            readPIDs(dirIn.Get(key.GetName()),pid)

if __name__ == '__main__':
    readPIDs(inFile, '')
    inFile.Close()
    outFile.Close()
    log.close()
