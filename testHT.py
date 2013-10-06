import HistoTransform_ext as ht
b = ht.HistoTransform('bdt_inFile_ttbar_A_0of2.root', 'bdt_outFile_ttbar_A_0of2.root')
subdir = b.addSubDirectory("")
b.addBackground(subdir, 'ttbar')
b.transformBkgBDTs = False
b.addRegion(subdir, "2tag2jet_mva", 0.05, 2)
b.run()
