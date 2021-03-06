#ifndef CorrsAndSysts_h
#define CorrsAndSysts_h

/*
 * CorrsAndSysts class
 *
 * supply functions to apply corrections
 * and systematics needed for the H->bb
 * analysis
 *
 *  G. Facini, N. Morange & D. Buescher
 *  Wed Dec 12 13:07:00 CET 2012
 */

//
// Take all corrections and systematics that affect shapes out of Heather's script
//
// You should apply:
//
// NLO EW Higgs corrections
//
// W, Z, and top backgrounds shape corrections.
//
// pT and Mbb shape systematics. Cut-based values are here, for first estimates/checks.
// Should be replaced with systematics better tailored for MVA.
//
// Most pT systematics are binned in pT, each bin should be varied independently.
// The other are continuous parametrizations.
//


#include <map>
#include <vector>
#include <string>
#include <iostream>
#include <cstdlib>

#include "TH1F.h"
#include "TF1.h"
#include "TString.h"
#include "TFile.h"
#include "TObject.h"

namespace CAS {

  enum EventType { WHlvbb=0, ZHllbb, ZHvvbb, Wb, Wc, Wcc, Wl, Zb, Zc, Zl, ttbar, stop, diboson, NONAME };
  enum SysVar { Do=0, Up=1 };
  enum SysBin {
    None=-2,                            // default
    Any=-1,                             // means no binning -> used for continuous systematics
    Bin0=0, Bin1, Bin2, Bin3, Bin4,     // pT bins for binned systematics
    NOTDEFINED
  };

  enum Systematic // only systematics affecting the shape are relevant to this tool
  {
    Nominal,
    // the following are binned in pT (5 bins, independent systematics)
    PTBINNED,
    SysStopPt,
    SysWbbPtW,
    SysWccPtW,
    SysZbbPtZ,
    SysZccPtZ,
    SysWllPtW,
    SysZllPtZ,
    // the following are continuous (thus correlated in pT)
    CONTINUOUS,
    SysTheoryHPt,
    SysTopPt,
    SysTopMbb,
    SysStopMbb,
    SysZbbMbb,
    SysWbbMbb,
    SysZMbb,
    SysWMbb,
    SysWDPhi,
    SysWccDPhi,
    SysWbDPhi,
    SysZDPhi,
    SysZcDPhi,
    SysZbDPhi,
    LAST
  };
} // end namespace CAS
class DummyCAS{};

class CorrsAndSysts {

  public:

  ~CorrsAndSysts();

  private:

  CorrsAndSysts(){};

  void Initialize();

  int m_debug;

  // string to enums or enums to string
  std::map<std::string, CAS::EventType> m_typeNames;
  std::map<CAS::Systematic, std::string> m_systNames;
  std::map<CAS::SysVar, std::string> m_varNames;
  std::map<CAS::SysBin, std::string> m_binNames;
  std::map<std::string, CAS::Systematic> m_systFromNames;
  std::map<std::string, CAS::SysVar> m_varFromNames;
  std::map<std::string, CAS::SysBin> m_binFromNames;

  Float_t pTbins[6];

  bool m_draw;
  bool m_zero;
  bool m_one;
  bool m_two;
  bool m_seven;
  bool m_eight;

  // use TH* to store weights ; seems easier to maintain if ever we need e.g 2-d corrections
  // corrections
  TH1F* m_h_WHlvbbNLOEWKCorrection;
  TH1F* m_h_ZHllbbNLOEWKCorrection;
  TH1F* m_h_ZHvvbbNLOEWKCorrection;
  TH1F* m_h_WpTCorrection;
  TH1F* m_h_ZpTCorrection;
  TH1F* m_h_WDeltaPhiCorrection2Jet;
  TH1F* m_h_WDeltaPhiCorrection3Jet;
  TH1F* m_h_ZDeltaPhiCorrection;
  TH1F* m_h_topPtCorrection;

  // binned systematics
  TH1F* m_h_SysWbbPtW;
  TH1F* m_h_SysStopPt;
  TH1F* m_h_SysWccPtW;
  TH1F* m_h_SysWllPtW;
  TH1F* m_h_SysZbbPtZ;
  TH1F* m_h_SysZccPtZ;
  TH1F* m_h_SysZllPtZ;

  // continuous systematics
  TH1F* m_h_SysTheoryWHlvbbPt;
  TH1F* m_h_SysTheoryZHllbbPt;
  TH1F* m_h_SysTheoryZHvvbbPt;
  TF1* m_f_WDPhiCorr;
  TF1* m_f_ZDPhiCorr;
  TF1* m_f_SysZbbMbb;
  TF1* m_f_SysWbbMbb;
  TF1* m_f_SysTopMbb;
  TF1* m_f_SysStopMbb;
  TF1* m_f_SysWMbb;
  TF1* m_f_SysZMbb;


  std::map<TString, TObject*> m_allHists;

  public:

  CorrsAndSysts(TString name, bool draw=true); // e.g OneLepton_8TeV
  CorrsAndSysts(int channel, int year, bool draw=true); // channel: 0->0lepton, 1->1lepton, 2->2leptons

  inline void SetDebug(int i) { m_debug = i; }

  CAS::EventType GetEventType(TString name);
  CAS::SysBin GetSysBin(float vpt);

  void WriteHistsToFile(TString fname);

  // all values (VpT, Mbb) in MeV !

  // Higgs pT reweighting (NLO EW corrections)
  float Get_HiggsNLOEWKCorrection(CAS::EventType type, float VpT);
  inline float Get_HiggsNLOEWKCorrection(TString evtType, float VpT)
  { return Get_HiggsNLOEWKCorrection(m_typeNames[evtType.Data()], VpT); }

  // Bkg pT reweighting
  float Get_BkgpTCorrection(CAS::EventType type, float VpT);
  inline float Get_BkgpTCorrection(TString evtType, float VpT)
  { return Get_BkgpTCorrection(m_typeNames[evtType.Data()], VpT); }

  // Top pT reweighting
  float Get_ToppTCorrection(CAS::EventType type, float avgTopPt);
  inline float Get_ToppTCorrection(TString evtType, float avgTopPt)
  { return Get_ToppTCorrection(m_typeNames[evtType.Data()], avgTopPt); }

  // Bkg DeltaPhi correction
  float Get_BkgDeltaPhiCorrection(CAS::EventType type, float DeltaPhi, int njet);
  inline float Get_BkgDeltaPhiCorrection(TString evtType, float DeltaPhi, int njet)
  { return Get_BkgDeltaPhiCorrection(m_typeNames[evtType.Data()], DeltaPhi, njet); }

  // Systematics on distributions
  float Get_SystematicWeight(CAS::EventType type, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, CAS::Systematic sys=CAS::Nominal, CAS::SysVar var=CAS::Up, CAS::SysBin bin=CAS::None);
  float Get_SystematicWeight(CAS::EventType type, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, TString sysName);

  inline float Get_SystematicWeight(TString evtType, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, CAS::Systematic sys, CAS::SysVar var, CAS::SysBin bin)
  { return Get_SystematicWeight(m_typeNames[evtType.Data()], VpT, Mbb, avgTopPt, DeltaPhi, njet, sys, var, bin); }

  inline float Get_SystematicWeight(TString evtType, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, TString sysName)
  { return Get_SystematicWeight(m_typeNames[evtType.Data()], VpT, Mbb, avgTopPt, DeltaPhi, njet, sysName); }


  // forge the normalized syste name from the enums
  inline std::string GetSystName(CAS::Systematic sys, CAS::SysBin bin, CAS::SysVar var)
  { return m_systNames[sys]+m_binNames[bin]+m_varNames[var]; }

  // inverse function
  void GetSystFromName(TString name, CAS::Systematic& sys, CAS::SysBin& bin, CAS::SysVar& var);


  float Get_SystematicWeight0(CAS::EventType type, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet){ return Get_SystematicWeight(type, VpT, Mbb, avgTopPt, DeltaPhi, njet);}
  float Get_SystematicWeight1(CAS::EventType type, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, CAS::Systematic sys){return Get_SystematicWeight(type, VpT, Mbb, avgTopPt, DeltaPhi, njet, sys);}
  float Get_SystematicWeight2(CAS::EventType type, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, CAS::Systematic sys, CAS::SysVar var){return Get_SystematicWeight(type, VpT, Mbb, avgTopPt, DeltaPhi, njet, sys, var);}
  float Get_SystematicWeight3(CAS::EventType type, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, CAS::Systematic sys, CAS::SysVar var, CAS::SysBin bin){return Get_SystematicWeight(type, VpT, Mbb, avgTopPt, DeltaPhi, njet, sys, var, bin);}






};// close CorrsAndSysts class


namespace Utils {

  // utility
  TH1F* BuildTH1F(std::vector<Double_t> contents, TString hname, float min, float max, std::map<TString, TObject*>& hists);
  void  FillTH1F(std::vector<Float_t> contents, TH1F* h, std::map<TString, TObject*>& hists);
  void  FillTH1F(int len, Float_t* contents, TH1F* h, std::map<TString, TObject*>& hists);
  inline float GetScale(float value, TH1F* h);
  void SaveHist(TObject* h, std::map<TString, TObject*>& hists);

  // map<K,V> => map<V,K>
  template <typename T, typename U>
    std::map<U, T> reverseMap(const std::map<T, U>& m_in);

  // Implementation
  //
  template <typename T, typename U>
    std::map<U, T> reverseMap(const std::map<T, U>& m_in) {
      typedef typename std::map<T, U>::const_iterator map_it;
      map_it it=m_in.begin();
      std::map<U, T> m_out;
      while(it!=m_in.end()) {
        m_out[it->second]=it->first;
        it++;
      }
      return m_out;
    }

} // close Utils class

#endif //CorrsAndSysts_HPP_

