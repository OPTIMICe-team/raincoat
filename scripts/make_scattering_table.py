# -*- coding: utf-8 -*-

import numpy as np
from raincoat.scatTable import water
from raincoat.scatTable.TMMrain import scatTable
from pytmatrix import tmatrix_aux

frequencies = [9.6]
temperatures = [273.15]
sizes = np.arange(0.01, 0.1, 0.01)

for T in temperatures:
	for f in frequencies:
		table = scatTable(frequency=f,
						  n=water.n(T, f*1.e9),
						  sizes=sizes,
						  canting=10.0,
						  elevation=90.0,
						  aspect_ratio_func=1.0)#tmatrix_aux.dsr_thurai_2007)

		table.compute(verbose=True)
		table.save_text_scat_table(str(T) + '_' + str(f) + 'GHz.csv')
