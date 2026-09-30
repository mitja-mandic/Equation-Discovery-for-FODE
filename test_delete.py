import numpy as np
#
##data = load(r'C:\Users\Mitja\Work\ijs\baterije\FODE for SOFC\Equation-Discovery-for-FODE\data\battery\bank2_20260207-224617_0.01.npz')
#data = load(r"data\battery\bank2_20260207-224617_0.01.npz", allow_pickle=True)
#
#lst = data.files
#for item in lst:
#    print(item)
#
#    print(data[item])
   
x =  {'Rs': np.float64(0.017161530254175966), 'Q1': np.float64(38.05237609752811), 'alpha1': np.float64(0.8440783232423466), 'sigma2': np.float64(0.0017909991422941397), 'R3': np.float64(0.005606625157797635), 'Q4': np.float64(3.5686721833944475), 'alpha4': np.float64(0.7972900507433649)}
parameter_names = [y for y in x.keys()]
print(parameter_names)