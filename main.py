

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

plt.rcParams['figure.dpi'] = 100


# --- Funciones del modelo LoRa ---
def generar_simbolo_lora(sf, simbolo):
    N = 2 ** sf
    n = np.arange(N)
    fase = 2 * np.pi * ((n**2) / (2*N) + (simbolo/N - 0.5) * n)
    return np.exp(1j * fase)


def frecuencia_instantanea(sf, simbolo):
    N = 2 ** sf
    n = np.arange(N)
    return ((n + simbolo) % N) / N - 0.5


def detectar_simbolo(rx, sf):
    base = generar_simbolo_lora(sf, 0)
    dechirp = rx * np.conj(base)
    espectro = np.abs(np.fft.fft(dechirp))
    return int(np.argmax(espectro)), espectro


def anadir_ruido(tx, snr_db):
    N = len(tx)
    snr_lin = 10 ** (snr_db / 10)
    pot_senal = np.mean(np.abs(tx)**2)
    pot_ruido = pot_senal / snr_lin
    ruido = np.sqrt(pot_ruido/2) * (np.random.randn(N) + 1j*np.random.randn(N))
    return tx + ruido


# --- Ventana principal con 6 graficos ---
fig = plt.figure(figsize=(15, 9))
fig.suptitle("Simulador interactivo de modulacion LoRa (CSS)", fontsize=14, fontweight='bold')
gs = fig.add_gridspec(2, 3, top=0.90, bottom=0.30, hspace=0.4, wspace=0.35)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[0, 2])
ax4 = fig.add_subplot(gs[1, 0])
ax5 = fig.add_subplot(gs[1, 1])
ax6 = fig.add_subplot(gs[1, 2])

# --- Controles (sliders y botones) ---
ax_sf = fig.add_axes([0.12, 0.17, 0.28, 0.02])
ax_simbolo = fig.add_axes([0.12, 0.12, 0.28, 0.02])
ax_snr = fig.add_axes([0.12, 0.07, 0.28, 0.02])

# SF (Spreading Factor): cuantos bits codifica cada simbolo LoRa (7 a 12).
# A mayor SF, el chirp dura mas tiempo (N = 2^SF muestras) y la señal
# llega mas lejos, pero se transmiten menos bits por segundo.
slider_sf = Slider(ax_sf, 'SF', 7, 12, valinit=7, valstep=1)

# Simbolo: el valor entero (0 a 2^SF - 1) que se quiere transmitir.
# Define el punto de inicio del "salto" de frecuencia dentro del chirp,
# es decir, es el dato util que codifica la modulacion.
slider_simbolo = Slider(ax_simbolo, 'Simbolo', 0, 4095, valinit=50, valstep=1)

# SNR (Signal-to-Noise Ratio): relacion señal/ruido en decibeles.
# Indica que tan fuerte es la señal frente al ruido del canal;
# valores mas bajos (o negativos) simulan peores condiciones de recepcion.
slider_snr = Slider(ax_snr, 'SNR (dB)', -20, 10, valinit=-5, valstep=1)

ax_btn_actualizar = fig.add_axes([0.48, 0.11, 0.16, 0.05])
ax_btn_ser = fig.add_axes([0.67, 0.11, 0.18, 0.05])
btn_actualizar = Button(ax_btn_actualizar, 'Actualizar graficos')
btn_ser = Button(ax_btn_ser, 'Calcular curva SER')


def dibujar_principales(event=None):
    sf = int(slider_sf.val)
    N = 2 ** sf
    simbolo = int(slider_simbolo.val) % N
    snr_db = slider_snr.val

    for ax in (ax1, ax2, ax3, ax4):
        ax.clear()

    # 1. Frecuencia instantanea
    for s, color in zip([0, N//3, simbolo], ['#1565C0', '#2E7D32', '#E65100']):
        ax1.plot(frecuencia_instantanea(sf, s), label=f"Sim={s}", linewidth=1.2)
    ax1.set_title(f"Frecuencia instantanea (SF{sf})", fontsize=9)
    ax1.set_xlabel("Muestra (n)"); ax1.set_ylabel("Frec. normalizada")
    ax1.legend(fontsize=7); ax1.grid(alpha=0.3)

    # 2. Forma de onda
    senal = generar_simbolo_lora(sf, simbolo)
    ax2.plot(np.real(senal), color='#1565C0', linewidth=0.7)
    ax2.set_title(f"Forma de onda (simbolo={simbolo})", fontsize=9)
    ax2.set_xlabel("Muestra (n)"); ax2.set_ylabel("Amplitud")
    ax2.grid(alpha=0.3)

    # 3. Espectrograma
    nfft = min(64, N)
    ax3.specgram(senal, NFFT=nfft, Fs=1, noverlap=nfft-16, cmap='viridis')
    ax3.set_title("Espectrograma", fontsize=9)
    ax3.set_xlabel("Muestra (n)"); ax3.set_ylabel("Frec. normalizada")

    # 4. Dechirping y deteccion con ruido
    rx = anadir_ruido(senal, snr_db)
    detectado, espectro = detectar_simbolo(rx, sf)
    ax4.plot(espectro, color='#455A64', linewidth=0.8)
    ax4.axvline(detectado, color='#E65100', linestyle='--', label=f"Detectado={detectado}")
    ax4.axvline(simbolo, color='#2E7D32', linestyle=':', label=f"Real={simbolo}")
    ax4.set_title(f"Deteccion (SNR={snr_db:.0f} dB)", fontsize=9)
    ax4.set_xlabel("Bin FFT"); ax4.legend(fontsize=7); ax4.grid(alpha=0.3)

    fig.canvas.draw_idle()


def calcular_curva_ser(event=None):
    sf = int(slider_sf.val)
    ax5.clear()
    ax5.set_title("Calculando SER...", fontsize=9)
    fig.canvas.draw_idle()
    plt.pause(0.01)

    snr_range = np.arange(-20, 6, 3)
    n_trials = 60
    ser_values = []
    for snr_db in snr_range:
        errores = 0
        for _ in range(n_trials):
            simbolo = np.random.randint(0, 2**sf)
            tx = generar_simbolo_lora(sf, simbolo)
            rx = anadir_ruido(tx, snr_db)
            detectado, _ = detectar_simbolo(rx, sf)
            if detectado != simbolo:
                errores += 1
        ser_values.append(errores / n_trials)

    ax5.clear()
    ax5.semilogy(snr_range, np.array(ser_values) + 1e-3, marker='o', color='#1565C0')
    ax5.set_title(f"SER vs SNR (SF{sf})", fontsize=9)
    ax5.set_xlabel("SNR (dB)"); ax5.set_ylabel("SER")
    ax5.grid(alpha=0.3, which='both')
    fig.canvas.draw_idle()


def dibujar_compromiso():
    sfs = [7, 8, 9, 10, 11, 12]
    bitrate = [5470, 3125, 1760, 980, 540, 290]
    sensibilidad = [-123, -126, -129, -132, -134.5, -137]

    ax6.bar(sfs, bitrate, color='#1565C0', alpha=0.6, width=0.5)
    ax6.set_ylabel("Tasa de bits (bps)", color='#1565C0', fontsize=8)
    ax6.tick_params(axis='y', labelcolor='#1565C0')

    ax6b = ax6.twinx()
    ax6b.plot(sfs, sensibilidad, color='#E65100', marker='o', linewidth=2)
    ax6b.set_ylabel("Sensibilidad (dBm)", color='#E65100', fontsize=8)
    ax6b.tick_params(axis='y', labelcolor='#E65100')

    ax6.set_title("Compromiso SF / bitrate / sensibilidad", fontsize=9)
    ax6.set_xlabel("Spreading Factor")


# --- Conexion de controles con las funciones ---
slider_sf.on_changed(dibujar_principales)
slider_simbolo.on_changed(dibujar_principales)
slider_snr.on_changed(dibujar_principales)
btn_actualizar.on_clicked(dibujar_principales)
btn_ser.on_clicked(calcular_curva_ser)

# --- Dibujo inicial ---
dibujar_principales()
dibujar_compromiso()
calcular_curva_ser()

plt.show()