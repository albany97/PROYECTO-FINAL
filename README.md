# PROYECTO-FINAL
# Calculadora Web de Corriente Eléctrica y Resistencia (DC) en Serie
**Proyecto Académico de Programación I en Python**  
Simulación física modular de circuitos resistivos de corriente continua (DC) a 20 °C con interfaz gráfica en Streamlit.



## 1. Propósito y Alcance del Proyecto

Este proyecto implementa una herramienta web didáctica para calcular y analizar el comportamiento eléctrico de un **circuito DC resistivo en serie** compuesto por:
1. Una fuente de tensión continua (V).
2. Un conductor de ida con resistencia propia (Rc).
3. Una carga resistiva receptora (Rcarga).
4. Un conductor de retorno idéntico en material, longitud y sección.


### Alcance Didáctico y Limitaciones Físicas
- **Simulación ideal a 20 °C:** Utiliza los valores de resistividad ($\rho$) estándar a temperatura ambiente de referencia constante.
- **No es un dimensionador comercial:** No calcula ampacidad, no evalúa sobrecalentamiento por efecto Joule prolongado, no contempla resistencia de bornes o contactos, ni sustituye los cálculos normativos (NEC/IEC) de instalaciones eléctricas reales.

## 2. Modelo Matemático y Orden de Cálculo

Los cálculos se ejecutan respetando rigurosamente el orden establecido y **sin redondear variables intermedias**, conservando la máxima precisión de coma flotante:

1. **Conversión de la sección transversal a metros cuadrados:**
   $$A(\text{m}^2) = A(\text{mm}^2) \times 10^{-6}$$

2. **Cálculo de la longitud total del conductor (ida y vuelta):**
   $$L_{\text{total}} = 2 \times L$$

3. **Cálculo de la resistencia óhmica del cable:**
   $$R_c = \rho \times \frac{L_{\text{total}}}{A(\text{m}^2)}$$

4. **Cálculo de la resistencia total del circuito en serie:**
   $$R_t = R_{\text{carga}} + R_c$$

5. **Cálculo de la corriente eléctrica por Ley de Ohm:**
   $$I = \frac{V}{R_t}$$

6. **Cálculo de la caída de tensión en el conductor:**
   $$V_c = I \times R_c$$

7. **Cálculo de la potencia disipada por efecto Joule en el cable:**
   $$P_c = I^2 \times R_c$$

### Catálogo de Resistividades a 20 °C ($\Omega\cdot\text{m}$)
*Cobre | $1,68 \times 10^{-8}$ | Conductor estándar en instalaciones eléctricas |
*Aluminio | $2,65 \times 10^{-8}$ | Conductor ligero para líneas de distribución |
*Plata | $1,59 \times 10^{-8}$ | Mayor conductividad eléctrica conocida |
*Oro | $2,44 \times 10^{-8}$ | Máxima resistencia a la oxidación y corrosión |
*Hierro | $9,71 \times 10^{-8}$ | Conductor ferromagnético de moderada resistividad |


## 4. Caso de Comprobación y Calibración Obligatorio

Para validar el simulador, se utiliza el caso de prueba estándar:

- **Tensión ($V$):** $12\,\text{V}$
- **Resistencia de Carga ($R_{\text{carga}}$):** $10\,\Omega$
- **Material:** Cobre ($\rho = 1,68 \times 10^{-8}\,\Omega\cdot\text{m}$)
- **Longitud de ida ($L$):** $5\,\text{m}$
- **Sección transversal ($A$):** $2,5\,\text{mm}^2$

### Resultados Obtenidos y Verificados:
- $L_{\text{total}} = 2 \times 5 = 10\,\text{m}$
- $A = 2,5 \times 10^{-6}\,\text{m}^2$
- $R_c = 1,68 \times 10^{-8} \times \frac{10}{2,5 \times 10^{-6}} = \mathbf{0,0672\,\Omega}$
- $R_t = 10 + 0,0672 = \mathbf{10,0672\,\Omega}$
- $I = \frac{12}{10,0672} \approx \mathbf{1,1920\,\text{A}}$
- $V_c = 1,1920 \times 0,0672 \approx \mathbf{0,0801\,\text{V}}$
- $P_c = (1,1920)^2 \times 0,0672 \approx \mathbf{0,0955\,\text{W}}$

---

## 5. Instalación y Ejecución Paso a Paso

### Prerrequisitos
- Tener instalado **Python 3.9 o superior** (verificar con `python --version`).

### Paso 1: Clonar o situarse en la raíz del proyecto
```bash
cd "c:\Users\PEDRO\Documents\PAULA MARIA"
```

### Paso 2: Crear el entorno virtual de Python
En Windows (PowerShell o CMD):
```bash
python -m venv .venv
```

En Linux / macOS:
```bash
python3 -m venv .venv
```

### Paso 3: Activar el entorno virtual
En Windows (PowerShell):
```powershell
.venv\Scripts\Activate.ps1
```
(Si PowerShell bloquea scripts, ejecuta antes: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)

En Windows (CMD):
```cmd
.venv\Scripts\activate.bat
```

En Linux / macOS:
```bash
source .venv/bin/activate
```

### Paso 4: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 5: Ejecutar la batería de pruebas unitarias
```bash
python test_calculadora.py

### Paso 6: Lanzar la aplicación web
```bash
streamlit run app.py
```
La aplicación abrirá automáticamente tu navegador en `http://localhost:8501`.



