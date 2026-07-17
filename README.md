# Simulador de Modulación LoRa (Chirp Spread Spectrum)

Simulación interactiva en Python de la modulación **LoRa (CSS - Chirp Spread Spectrum)**, desarrollada como trabajo encargado del curso de Administración de Sistemas de Comunicación de Datos — Universidad Nacional del Altiplano.

El script genera una sola ventana con **6 gráficos** y controles deslizantes para modificar los parámetros de la modulación en tiempo real, sin necesidad de guardar ni recargar imágenes.

## Vista general

El simulador permite observar cómo se genera un símbolo LoRa (chirp), cómo se transmite bajo ruido, y cómo el receptor lo detecta mediante la técnica de *dechirping*, todo con controles interactivos.

## Requisitos

- Python 3.8 o superior
- numpy
- matplotlib (con backend interactivo, por ejemplo `TkAgg` o `Qt5Agg`)

Instalación de dependencias:

```bash
pip install numpy matplotlib
```

## Uso

```bash
python lora_simulacion.py
```

Se abrirá una ventana con los 6 gráficos y tres controles deslizantes en la parte inferior. Mueve los sliders o usa los botones para actualizar la simulación.

## Parámetros interactivos

| Parámetro | Rango | Descripción |
|---|---|---|
| **SF** (Spreading Factor) | 7 a 12 | Determina cuántos bits codifica cada símbolo. A mayor SF, el chirp dura más tiempo (N = 2^SF muestras), la señal alcanza mayor distancia, pero la tasa de bits disminuye. |
| **Símbolo** | 0 a 2^SF - 1 | El valor entero que se transmite; define el punto de inicio del salto de frecuencia dentro del chirp. |
| **SNR** (Signal-to-Noise Ratio) | -20 a 10 dB | Relación señal/ruido del canal. Valores más bajos simulan peores condiciones de recepción. |

Además hay dos botones:

- **Actualizar gráficos**: redibuja los 4 gráficos principales con los valores actuales de los sliders.
- **Calcular curva SER**: recalcula la curva de tasa de error de símbolo (más lenta, por eso está separada).

## Descripción de los 6 gráficos

1. **Frecuencia instantánea**: muestra cómo varía la frecuencia del chirp a lo largo del tiempo para distintos símbolos, evidenciando el salto característico de la modulación CSS.
2. **Forma de onda**: parte real de la señal chirp generada para el símbolo seleccionado.
3. **Espectrograma**: representación tiempo-frecuencia del símbolo, útil para visualizar el barrido de frecuencia.
4. **Dechirping y detección**: simula la recepción con ruido AWGN y el proceso de demodulación (multiplicación por el chirp base + FFT) para detectar el símbolo transmitido.
5. **Curva SER vs SNR**: tasa de error de símbolo simulada en función del SNR, mostrando el desempeño del sistema ante distintas condiciones de canal.
6. **Compromiso SF / tasa de bits / sensibilidad**: gráfico de barras y líneas que compara, para cada SF, la tasa de bits alcanzable y la sensibilidad del receptor.

## Fundamento teórico

La modulación LoRa se basa en la técnica *Chirp Spread Spectrum*, donde cada símbolo se representa como un chirp cíclico cuya frecuencia inicial codifica la información. El receptor realiza *dechirping* (multiplicación por el conjugado del chirp base) seguido de una FFT para recuperar el símbolo transmitido.

**Referencia:**
Vangelista, L. (2017). Frequency shift chirp modulation: The LoRa modulation. *IEEE Signal Processing Letters*, 24(12), 1818-1821.

## Autor

Trabajo encargado — Universidad Nacional del Altiplano.

## Licencia

Uso libre con fines académicos.
