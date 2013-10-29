
#root -l 'transformLHCP.C+("~/recon/VH/limitHistograms/LimitHistograms.lvbb.LHCP2013.8TeV.Freiburg.v1.4.WlvH125.root", 1, "WlvH125" , "~/recon/VH/limitHistograms/LimitHistograms.lvbb.LHCP2013.8TeV.Freiburg.v1.4.WlvH125.trafo1.root")'
#root -l 'transformLHCP.C+("~/recon/VH/limitHistograms/Freiburg/LimitHistograms.lvbb.LHCP2013.8TeV.Freiburg.v1.5.WlvH125.root", 6, "WlvH125" , "~/recon/VH/limitHistograms/Freiburg/LimitHistograms.lvbb.LHCP2013.8TeV.Freiburg.v1.5.WlvH125.trafo6.root")'
#root -l 'transformLHCP.C+("~/recon/VH/limitHistograms/Freiburg/LimitHistograms.lvbb.LHCP2013.8TeV.Freiburg.v1.6.WlvH125.root", 6, "WlvH125" , "~/recon/VH/limitHistograms/Freiburg/LimitHistograms.lvbb.LHCP2013.8TeV.Freiburg.v1.6.WlvH125.trafo6.root")'
root -l 'transformLHCP.C+("~/recon/VH/limitHistograms/Freiburg/LimitHistograms.lvbb.LHCP2013.8TeV.Freiburg.v1.6.fix.WlvH125.root", 6, "WlvH125" , "~/recon/VH/limitHistograms/Freiburg/LimitHistograms.lvbb.LHCP2013.8TeV.Freiburg.v1.6.fix.WlvH125.trafo6.root")'
#root -l 'transformLHCP.C+("~/recon/VH/limitHistograms/LimitHistograms.lvbb.LHCP2013.8TeV.Freiburg.v1.4.WlvH125.root", 7, "WlvH125" , "~/recon/VH/limitHistograms/LimitHistograms.lvbb.LHCP2013.8TeV.Freiburg.v1.4.WlvH125.trafo7.root")'
#root -l 'transformLHCP.C+("~/recon/VH/limitHistograms/LimitHistograms.lvbb.LHCP2013.8TeV.Freiburg.v1.4.WZ.root", 1, "WZ" , "~/recon/VH/limitHistograms/LimitHistograms.lvbb.LHCP2013.8TeV.Freiburg.v1.4.WZ.trafo1.root")'
#root -l 'transformLHCP.C+("~/recon/VH/limitHistograms/LimitHistograms.lvbb.LHCP2013.8TeV.Freiburg.v1.4.WZ.root", 5, "WZ" , "~/recon/VH/limitHistograms/LimitHistograms.lvbb.LHCP2013.8TeV.Freiburg.v1.4.WZ.trafo5.root")'
#root -l 'transformLHCP.C+("~dbuescher/recon/VH/limitHistograms/LiverpoolBmham/LimitHistograms.llbb.8TeV.MVA.DirectTag_mH125.LiverpoolBmham.v42.root", 6, "ZllH125" , "~dbuescher/recon/VH/limitHistograms/LiverpoolBmham/LimitHistograms.llbb.8TeV.MVA.DirectTag_mH125.LiverpoolBmham.v42.trafo6.root", "Two")'

exit

prefix='/afs/cern.ch/user/d/dbuesche/recon/VH/limitHistograms/FinalInputs/Inputs.LHCP2013.8TeV.MVA.v2.8.1.mH125.TT'

trafos="5 7"

for trafo in $trafos; do
  root -l "transformLHCP.C+(\"${prefix}.root\", ${trafo}, \"ZllH125\", \"${prefix}.2lep.trafo${trafo}.root\", \"TwoLepton\")"
  root -l "transformLHCP.C+(\"${prefix}.root\", ${trafo}, \"WlvH125\", \"${prefix}.1lep.trafo${trafo}.root\", \"OneLepton\")"
  root -l "transformLHCP.C+(\"${prefix}.root\", ${trafo}, \"ZvvH125\", \"${prefix}.0lep.trafo${trafo}.root\", \"ZeroLepton\")"
done
