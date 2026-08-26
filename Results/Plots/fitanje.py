import numpy as np
import matplotlib.pyplot as plt
import torch

# Parameters

R_true = 500.2      # Ohms
C_true = 202.38e-9        # Farads
R_1_true = 1000.3
C_1_true = 4.9645e-6
#C_1_true = 1.00969709e-7 #s to vrednostjo in vsemi ostalimi parametri enakimi dobim problematično oceno
R_2_true = 200.3
C_2_true = 5.04243635e-7


# Frequency range
f = np.logspace(-3, 5, 300)
w = 2 * np.pi * f

# Complex impedance
Z_true = R_true / (1 + 1j * w * R_true * C_true) + R_1_true / (1 + 1j * w * R_1_true * C_1_true) + R_2_true / (1 + 1j * w * R_2_true * C_2_true)

# Z_4 = Rs + Rg1 / (1 + 1j * w * tauG1) ** 0.5
# Z_5 = Rs + 1j * w * L1
# Z_6 = Rs + sigma1 / (1j * w) ** 0.5
# Z_7 = Rs + 1 / (1 / R1 + Q1 * (1j * w) ** alpha1) + sigma1 / (1j * w) ** 0.5
# Z_8 = Rs + 1 / (1 / R1 + Q1 * (1j * w) ** alpha1) + Rg1 / (1 + 1j * w * tauG1) ** 0.5
# Z_9 = Rs + 1 / (1 / R1 + Q1 * (1j * w) ** alpha1)
#plt.plot(np.real(Z), np.imag(Z))

#plt.show()

# Optional noise
#noise_level = 0.01
#
#Z_noisy = Z_true * (
#    1
#    + noise_level * (
#        np.random.randn(len(Z_true))
#        + 1j * np.random.randn(len(Z_true))
#    )
#)

w_torch = torch.tensor(w, dtype=torch.float64)

Z_real_meas = torch.tensor(
    np.real(Z_true),
    dtype=torch.float64
)

Z_imag_meas = torch.tensor(
    np.imag(Z_true),
    dtype=torch.float64
)


#optimizer

R = torch.tensor(500, dtype=torch.float64, requires_grad=True)
log_C = torch.tensor(np.log(5e-7), dtype=torch.float64, requires_grad=True)

R_1 = torch.tensor(700, dtype=torch.float64, requires_grad=True)
log_C_1 = torch.tensor(np.log(7e-9), dtype=torch.float64, requires_grad=True)

R_2 = torch.tensor(600, dtype=torch.float64, requires_grad=True)
log_C_2 = torch.tensor(np.log(3e-8), dtype=torch.float64, requires_grad=True)


# Adam optimizer
optimizer = torch.optim.Adam([R, log_C, R_1, log_C_1, R_2, log_C_2], lr=1)

# Loss history
losses = []

for epoch in range(3000):

    optimizer.zero_grad()

    # Complex impedance model
    #Z_model = R / (1 + 1j * w_torch * R * torch.exp(log_C))
    Z_model = R / (1 + 1j * w_torch * R * torch.exp(log_C)) + R_1 / (1 + 1j * w_torch * R_1 * torch.exp(log_C_1)) + R_2 / (1 + 1j * w_torch * R_2 * torch.exp(log_C_2))

    # Split into real/imag parts
    Z_real = torch.real(Z_model)
    Z_imag = torch.imag(Z_model)

    # MSE loss
    loss = torch.mean(
        (Z_real - Z_real_meas)**2
        + (Z_imag - Z_imag_meas)**2
    )
    #loss_2 = torch.mean((Z_model - Z_true)**2)

    # Backprop
    loss.backward()

    # Adam step
    optimizer.step()

    losses.append(loss.item())

    if epoch % 200 == 0:
        print(
            f"Epoch {epoch}, "
            f"Loss={loss.item():.6f}, "
            #f"Loss={loss_2.item():.6f}, "
            f"R={R.item():.2f}, "
            f"C={np.exp(log_C.item()):.3e}"
            f"R_1={R_1.item():.2f}, "
            f"C_1={np.exp(log_C_1.item()):.3e}"
            f"R_2={R_2.item():.2f}, "
            f"C_2={np.exp(log_C_2.item()):.3e}"
        )




print("\nTRUE VALUES")
print("R =", R_true)
print("C =", C_true)
print("R_1 =", R_1_true)
print("C_1 =", C_1_true)
print("R_2 =", R_2_true)
print("C_2 =", C_2_true)


print("\nESTIMATED VALUES")
print("R =", R.item())
print("C =", np.exp(log_C.item()))
print("R_1 =", R_1.item())
print("C_1 =", np.exp(log_C_1.item()))
print("R_2 =", R_2.item())
print("C_2 =", np.exp(log_C_2.item()))

# Final fitted impedance
Z_fit = (
    R.item()
    / (1 + 1j * w * R.item() * np.exp(log_C.item()))
    +
    R_1.item()
    / (1 + 1j * w * R_1.item() * np.exp(log_C_1.item()))
    +
    R_2.item()
    / (1 + 1j * w * R_2.item() * np.exp(log_C_2.item())))


plt.figure(figsize=(10, 10))

plt.plot(
    np.real(Z_true),
    np.imag(Z_true),
    'o',
    label='Measured'
)

plt.plot(
    np.real(Z_fit),
    np.imag(Z_fit),
    '-',
    label='Fitted'
)

plt.xlabel('Real(Z)')
plt.ylabel('Imag(Z)')
plt.title('Nyquist Plot')
plt.legend()
plt.grid(True)

plt.show()
plt.close('all')
