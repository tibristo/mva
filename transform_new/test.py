from ROOT import TString
import HistoTransform_ext as ht
n = TString("bdt0_inFile.root")
ns = "bdt0_inFile.root"
n2 = TString("bdt0_outFile.root")
ns2 = "bdt0_outFile.root"
ht.HistoTransform(ns,ns2)
