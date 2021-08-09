import numpy as np
import pandas as pd
import csv

fin = "JIR_SPE_RDR_2020048T130003_V01.DAT"
fout = "JIR_SPE_RDR_2020048T130003_V01.csv"

x = np.fromfile(fin, dtype=float)

DF = pd.DataFrame(x)
DF.to_csv(fout)
