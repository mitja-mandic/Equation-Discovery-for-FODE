from numpy import load

#data = load(r'C:\Users\Mitja\Work\ijs\baterije\FODE for SOFC\Equation-Discovery-for-FODE\data\battery\bank2_20260207-224617_0.01.npz')
data = load(r"data\battery\bank2_20260207-224617_0.01.npz", allow_pickle=True)

lst = data.files
for item in lst:
    print(item)

    print(data[item])
   

