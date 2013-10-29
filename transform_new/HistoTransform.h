#ifndef HistoTransform_h
#define HistoTransform_h
#include <iostream>
#include <TROOT.h>
#include <TSystem.h>
#include <TIterator.h>
#include <TKey.h>
#include <TString.h>
#include <TObjArray.h>
#include <TObjString.h>
#include <TFile.h>
#include <TH1.h>
#include <TDirectory.h>
#include <TClass.h>
#include <TObject.h>
#include <vector>

using namespace std;

class HistoTransform {
public:
  HistoTransform();
  HistoTransform(const std::string inFileName, const std::string outFileName = "");// {
  TString m_inFileName;
  TString m_outFileName;
  TFile* m_inFile;
  TFile* m_outFile;

  typedef struct {
    string name;
    float maxUnc;
    TH1* bkg;
    TH1* sig;
    vector<int> bins;
  } Region;

  typedef struct {
    string name;
    int nFold;
    vector<Region*> regions;
  } KFold;

  typedef struct {
    TDirectory* dir;
    vector<string> backgrounds;
    string signal;
    //vector<Region*> regions;
    vector<KFold*> kFolds;
  } SubDirectory;

  vector<SubDirectory*> m_subDirs;

  vector<int> getRebinBins(TH1* histoBkg, TH1* histoSig, int method, double maxUnc = 0.05);
  KFold* getKFold(SubDirectory* subDir, string histName);
  Region* getRegion(SubDirectory* subDir, string histName);
  bool isFirstOfKFold(KFold* kFold, string histName);
  void rebinHisto(TH1* histo, vector<int>* bins);
  void readRebinBins(SubDirectory* subDir);
  void rebinAllHistos(TDirectory* source, SubDirectory* subDir);
  void mergeKFolds(TDirectory* source, SubDirectory* subDir);
  void readTotalBkg(SubDirectory* source);
  void readSignal(SubDirectory* source);
  void findRegions(SubDirectory* subDir, string anyHistoName, float maxUnc = 0.05, string containRegion = "", int nFold = 1);
  SubDirectory* findSubDirs(string subDirName, bool identical = false);
  void skimKFoldTrafos(SubDirectory * subDir);
  void addRegion1(SubDirectory* subDir, string regionName, float maxUnc = 0.05, int nFold = 1);
  string getNameField(string histoName, int field);
  string getSampleName(string histoName);
  string getRegionName(string histoName);
  string getMVATag(string histoName);
  string getSysName(string histoName);

  bool doMergeKFolds;
  bool doTransformBeforeMerging;
  bool transformBkgBDTs;
  int transformAlgorithm;
  float trafoFiveY;
  float trafoSixY;
  float trafoSixZ;
  unsigned int trafoSevenNBins;
  int trafoEightRebin;

  SubDirectory* addSubDirectory(string subDirName);
  void addBackground(SubDirectory* subDir, string bkgName);
  void setSignal(SubDirectory* subDir, string bkgName);
  void addRegion(SubDirectory* subDir, string regionName, float maxUnc = 0.05, int nFold = 1);
  void run();

  /*  HistoTransform(TString inFileName, TString outFileName = "") {

    m_inFileName = inFileName;
    m_outFileName = outFileName;

    cout << "INFO: reading from file '" << m_inFileName.Data() << "'" << endl;
    m_inFile = new TFile(m_inFileName, "read");
    if (!m_inFile -> IsOpen()) {
      gSystem -> Exit(1);
    }

    if (m_outFileName == "") {
      m_outFileName = m_inFileName;
      m_outFileName.ReplaceAll(".root", ".transformed.root");
    }
    cout << "INFO: writing to file '" << m_outFileName.Data() << "'" << endl;
    m_outFile = new TFile(m_outFileName, "recreate");

    doMergeKFolds = true;
    doTransformBeforeMerging = false;
    transformAlgorithm = 1;
    trafoFiveY = 5.;
    trafoSixY = 10.;
    trafoSixZ = 10.;
    trafoSevenNBins = 20;
    trafoEightRebin = 20;
    transformBkgBDTs = true;

    }*/

};


#endif
