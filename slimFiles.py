import ROOT,sys,copy,argparse
selectedFolders = ['SelectedPosMuTrig','SelectedNegMuTrig', 'SelectedPosElTrig', 'SelectedNegElTrig']

# not very elegant, need to think of a better way to specify these options....
parser = argparse.ArgumentParser(description='Combine TTrees from different TFiles.')
parser.add_argument('--file', help='Single file to process')
parser.add_argument('--sample-type', choices=['Signal','AllBkg','Data'], help='Choose from type of sample to create')
parser.add_argument('--output-partial',action='store_true', help='If creating full sample type, specify whether or not to create partial outputs')
args = parser.parse_args()

if not vars(args)['sample_type'] and not vars(args)['file']:
    print 'Incorrect usage!  Need to specify an input file or at least a sample type. Press any key to exit.'
    raw_input()
    sys.exit(0)

all_xsec = {}
# ProcessLine for adding xsec and pid
ROOT.gROOT.ProcessLine(\
    "struct Vars{\
    Float_t xsec;\
    Int_t pid;\
    Long_t entries;\
    };")
allTrees_list = ROOT.TList()
allTrees_arr = []
entries = -1 #cheap and dirty hack because I'm lazy
createFullSample = False
data = False

def readXml(dataType):
    '''
    Get the settings for which PIDs to combine in the combined root file and which root files to run over.  The one to run is specified at run time and given as an arg.
    Keyword arguments:
    dataType --- The type of sample to run, AllBkg or Signal, for eg. Set PIDs for each in settings_slimming.xml

    returns a list of pids and files to run over
    '''
    import xml.etree.ElementTree as ET
    xmlTree = ET.parse('settings_slimming.xml')
    root = xmlTree.getroot()

    pids = []
    files = []
    for child in root.findall('sampleType'):
        if child.get('name') == dataType:
            for grandchild in list(child):
                if grandchild.tag == 'pid':
                    pids.append(grandchild.get('name'))
                elif grandchild.tag == 'file':
                    files.append(grandchild.get('name'))
    return pids,files

def stripPID(pid):
    '''
    Strip the PID identifier of any non-integer characters.
    Keyword arguments:
    pid --- The pid identifier
    
    returns stripped pid
    '''
    if pid.isdigit():
        return pid
    new_pid = ''
    for x in pid:
        if x.isdigit():
            new_pid+=x
    return new_pid

def getXSec(pid):
    '''
    Get the cross section for the sample based on the pid identifier.  The cross sections are based on the PID and come from 2012_hcp_cross_sections.txt.
    Keyword arguments:
    pid -- the PID, not necessarily only integers at this point.

    returns dictionary with stripped pid as key, list containing [Process, Generator, cross-section*BR, k-factor, name]
    '''
    #strip non-integer parts off pid
    new_pid = stripPID(pid)
    global all_xsec, data
    if data:
        return ['DATA','DATA',1,1,1,'DATA']
    if all_xsec: #don't do it again if it's already been done!
        if new_pid in all_xsec.keys():
            return all_xsec[new_pid]
        else:
            log.write("No xsec available for "+ new_pid)
            return ['NONE','NONE',1,1,1,'NONE']
    f = open('2012_cross_sections.txt','r')
    for line in f:
        line_arr = line.split('|')
        if len(line_arr) == 7:
            for i in xrange(len(line_arr)):
                line_arr[i] = line_arr[i].strip()
            all_xsec[str(line_arr[0]).strip()] = line_arr[1:]
    f.close()
    if new_pid in all_xsec.keys():
        return all_xsec[new_pid]
    else:
        log.write("No xsec available for "+ new_pid)
        return ['NONE','NONE',1,1,1,'NONE']

def getAllEntries(dirIn, key, log):
    '''
    Gets the full number of entries for the original sample by reading this from the cutflow Ntuple in the .root file.
    Keyword arguments:
    dirIn --- The current TDirectory.
    key --- The key or object we are looking at in the current TDirectory.
    log --- The log file.
    '''
    global full_log, entries
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

def combineTrees(dirIn, pid, chain, log):
    '''
    Combine the TTrees together -> add them to the chain which is a TList.
    Keyword arguments:
    dirIn --- The current directory in the current input TFile.
    pid --- The pid we are working on.
    chain --- TList with all TTrees in it.
    log --- The log file.
    '''
    for key in dirIn.GetListOfKeys():
        cl_name = dirIn.Get(key.GetName()).ClassName()
        if key.GetName() in selectedFolders:
            new_dir = dirIn.Get(key.GetName())
            print 'adding ntuple'
            chain.Add(new_dir.Get(key.GetName()+'Ntuple'))#tree)
        elif cl_name == 'TDirectoryFile':
            combineTrees(dirIn.Get(key.GetName()), pid, chain, log)
        elif (cl_name == 'TH1F' or cl_name == 'TH1D') and key.GetName().endswith('BaselineOneLepton'):
            getAllEntries(dirIn, key, log)

def readPIDs(dirIn, pids, inFile, inFile_curr, outFile, log, createFullSample, allTrees_list, fullTree = None):
    '''
    Read all the TTrees for different PIDs, traversing through all subfolders.  Recursive method, calls on itself if the current item being viewed in the pwd is a TDirectory.
    Keyword arguments:
    dirIn --- The current TDirectory.
    pid --- A list of PIDs to read in.
    inFile --- The input TFile.
    inFile_curr --- The current directory in the input TFile.
    outFile --- The output TFile.
    log --- The log file.
    allTrees_list --- list containing all merged TTrees
    '''
    global entries, data
    entries = -1
    inFile_curr = copy.deepcopy(dirIn.GetName())
    for key in dirIn.GetListOfKeys():
        cl_name = dirIn.Get(key.GetName()).ClassName()
        if key.GetName().find("pid") != -1 or data:
            pid = key.GetName()
            new_pid = stripPID(pid)
            if data:
                new_pid = '-999'
            print pid
            if pids and (not new_pid in pids):
                # Add 'continue' here since we don't want to add this!
                continue
            treelist = ROOT.TList()
            combineTrees(dirIn.Get(key.GetName()), key.GetName(), treelist, log)
            print 'outfile.cd'
            outFile.cd()
            mergeTree = ROOT.TTree.MergeTrees(treelist)#.Write()
            # add new branch with xsec and pid
            xsec = getXSec(pid)
            varStruct = ROOT.Vars()
            outTree = mergeTree.CloneTree(0)
            outTree.Branch('xsec', ROOT.AddressOf(varStruct, 'xsec'), 'xsec/F')
            outTree.Branch('pid', ROOT.AddressOf(varStruct, 'pid'), 'pid/I') #/I is very important!!!!
            outTree.Branch('entries', ROOT.AddressOf(varStruct, 'entries'), 'entries/L')
            # Loop through all entries and add values
            varStruct.xsec = float(xsec[2])*float(xsec[3])
            varStruct.pid = int(copy.deepcopy(new_pid))
            if entries == -1:
                entries = mergeTree.GetEntries()
                log.write('Number of entries is probably incorrect, not set by CutFlow Histogram!!!  Set by mergeTree.GetEntries()')
                full_log.write('Number of entries is probably incorrect, not set by CutFlow Histogram!!!  Set by mergeTree.GetEntries()')
            varStruct.entries = entries # oh noes?!
            for i in xrange(mergeTree.GetEntries()):
                mergeTree.GetEntry(i)
                outTree.Fill()
            outTree.SetName('Ntuple_'+str(pid))
            outTree.Write()
            if createFullSample:
                print 'fulltree.cd'
                fullTree.cd()
                treeClone = outTree.CloneTree()
                allTrees_list.Add(treeClone)
            print 'infile.cd'
            print inFile_curr
            inFile.cd(inFile_curr)
            print 'blah'
        elif cl_name == 'TDirectoryFile':
            readPIDs(dirIn.Get(key.GetName()),pids, inFile, inFile_curr, outFile, log, createFullSample, allTrees_list, fullTree)

full_log = open('FullLog','w')

if __name__ == '__main__':

    pids = []
    files = []
    if vars(args)['sample_type']:
        pids,files = readXml(vars(args)['sample_type'])
        print vars(args)['sample_type']
        if vars(args)['sample_type']=='Data':
            data = True
        full_log.write('sample_type: ' + vars(args)['sample_type'])
        if vars(args)['file']:
            files = [vars(args)['file']]
        createFullSample = True
        fullSampleFile = ROOT.TFile(str('/Disk/speyside8/lhcb/atlas/tibristo/Fullsample_'+vars(args)['sample_type']+'.root'),'RECREATE')
    elif vars(args)['file']:
        files = [vars(args)['file']]
    full_log.write('files: ')
    
    files_tlist = ROOT.TList()
    for f in files:
        full_log.write(f)
    full_log.write('output_partial: ' + str(vars(args)['output_partial']))
    
    for f in files:
        inFile = ROOT.TFile(f, "READ")
        log = open(str(f)+'_slimmed_log.txt','w')
        full_log.write('Starting file: ' + str(f))
        print 'starting file: ' + str(f)
#        try:
        inFile_curr = ''
        outFile = ROOT.TFile(str(f+'_slimmed.root'),'RECREATE')
        if createFullSample:
            readPIDs(inFile, pids, inFile, inFile_curr, outFile, log, createFullSample, allTrees_list, fullSampleFile)
        else:
            readPIDs(inFile, pids, inFile, inFile_curr, outFile, log, createFullSample, allTrees_list)
        outFile.Close()
        inFile.Close()
        
 #           log.write('Error trying to run through file ' + str(f))
  #          full_log.write('Error trying to run through file ' + str(f))
   #         print 'Error trying to run through file ' + str(f)
        log.close()
        full_log.write('Finished file: ' + str(f))
        full_log.write('*******************************************')

    if createFullSample:# and allTrees_arr:#'size=0' not in allTreesSize_in:
        #loop through allTrees and add to TList
        print 'all added to TList'
        fullSampleFile.cd()
        finalTree = ROOT.TTree.MergeTrees(allTrees_list)
        finalTree.SetName("Ntuple")
        print 'merged trees'
        finalTree.Write()
        fullSampleFile.Close()
    log.close()
    full_log.close()
#sys.exit()
