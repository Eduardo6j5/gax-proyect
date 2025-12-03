import numpy as np
import panel as pn
import plotly.graph_objects as go
import qrcode
import matplotlib.pyplot as plt

pn.extension('plotly')

# ------- Parámetros iniciales -------
INIT_N = 1000
INIT_BRAZOS = 2
INIT_K = 0.35
INIT_DISP = 0.15
INIT_OMEGA = 0.4
INIT_MASA = 1.0
INIT_DENSIDAD = 1.0        # densidad radial
INIT_DENSIDAD_Z = 1.0      # densidad vertical
R_MAX = 15.0
# -----------------------------------

def generar_estrellas(N, n_brazos, k, disp_z, r_max, densidad, densidad_z, seed=None):
    rng = np.random.default_rng(seed)

    # Densidad afecta la distribución radial
    scale = r_max / (3.0 * densidad)
    r = rng.exponential(scale=scale, size=N)
    r = np.clip(r, 0.01, r_max)

    arm_idx = rng.integers(0, n_brazos, size=N)
    theta_base = rng.uniform(0, 2*np.pi, size=N)
    theta_disp = rng.normal(0.0, 0.6, size=N) * (1.0 / (1.0 + r/2.0))

    # Densidad vertical: disco más delgado o más grueso
    z = rng.normal(0.0, disp_z / densidad_z, size=N)

    return r, theta_base, arm_idx, theta_disp, z

def posiciones_xyz(r, theta_base, arm_idx, theta_disp, z, n_brazos, k, omega, t):
    arm_angle = 2*np.pi * arm_idx / max(1, n_brazos)
    theta = theta_base + arm_angle + k*r + omega*t + theta_disp
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y, z

# Datos base
N = INIT_N
r, theta_base, arm_idx, theta_disp, z = generar_estrellas(
    N, INIT_BRAZOS, INIT_K, INIT_DISP, R_MAX, INIT_DENSIDAD, INIT_DENSIDAD_Z, seed=42
)
t = 0.0

# Sliders interactivos
s_masa = pn.widgets.FloatSlider(name="Masa central", start=0.5, end=5.0, step=0.5, value=INIT_MASA)
s_omega = pn.widgets.FloatSlider(name="Velocidad angular", start=0.0, end=2.0, step=0.1, value=INIT_OMEGA)
s_disp = pn.widgets.FloatSlider(name="Dispersión radial (z)", start=0.05, end=0.5, step=0.05, value=INIT_DISP)

# Densidades agregadas
s_densidad = pn.widgets.FloatSlider(name="Densidad radial", start=0.5, end=3.0, step=0.1, value=INIT_DENSIDAD)
s_densidad_z = pn.widgets.FloatSlider(name="Densidad vertical (grosor disco)", start=0.5, end=3.0, step=0.1, value=INIT_DENSIDAD_Z)

# Función que actualiza la galaxia
def actualizar(masa, omega, disp, densidad, densidad_z):
    r, theta_base, arm_idx, theta_disp, z = generar_estrellas(
        N, INIT_BRAZOS, INIT_K, disp, R_MAX, densidad, densidad_z, seed=42
    )
    x, y, zpos = posiciones_xyz(r, theta_base, arm_idx, theta_disp, z,
                                INIT_BRAZOS, INIT_K, omega, t)

    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=zpos,
        mode='markers',
        marker=dict(size=2, color=r*masa, colorscale='Plasma', opacity=0.8)
    )])

    fig.update_layout(
        title="Galaxia Espiral",
        scene=dict(
            xaxis=dict(backgroundcolor="black", showgrid=False, zeroline=False),
            yaxis=dict(backgroundcolor="black", showgrid=False, zeroline=False),
            zaxis=dict(backgroundcolor="black", showgrid=False, zeroline=False),
            bgcolor="black",
            camera=dict(
                eye=dict(x=0, y=0, z=2),      # Vista desde arriba
                up=dict(x=0, y=1, z=0),
                center=dict(x=0, y=0, z=0)
            )
        ),
        margin=dict(l=0, r=0, b=0, t=40)
    )
    return fig

# Panel interactivo
galaxia_panel = pn.bind(actualizar,
    masa=s_masa,
    omega=s_omega,
    disp=s_disp,
    densidad=s_densidad,
    densidad_z=s_densidad_z
)

app = pn.Column(
    "#  Galaxia Espiral",
    s_masa, s_omega, s_disp,
    s_densidad, s_densidad_z,   # sliders nuevos
    pn.panel(galaxia_panel, sizing_mode="stretch_both")
)

app.servable()

# --------- Generar Código QR ---------
url = "https://eduardo6j5.github.io/galaxi-proyect/"

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=8,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

img_qr = qr.make_image(fill_color="black", back_color="white")
img_qr.save("codigo_qr.png")

plt.figure("Código QR")
plt.imshow(img_qr, cmap="gray")
plt.axis("off")
plt.title("Escanea para abrir la página")
plt.show()

app.save("galaxia.html", embed=True)
