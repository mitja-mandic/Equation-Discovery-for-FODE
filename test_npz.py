from numpy import load

data = load('data/LTE/Z_s.npz', allow_pickle=True)
lst = data.files
print(data['mat_Z'])
