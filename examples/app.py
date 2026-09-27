"""Focused synthetic demonstration of optical response and interference-order ambiguity."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from thinfilm.inference import observable, thickness_scan
from thinfilm.optics import multilayer

st.set_page_config(page_title="Thin-film identifiability", layout="wide")
st.title("Thin-film thickness: what can the spectrum identify?")
st.caption("Synthetic lossless air / n=1.8 coating / n=1.5 substrate. No experimental data.")
thickness = st.slider("True coating thickness (nm)", 20.0, 650.0, 137.0, 1.0)
angle = st.slider("Incidence angle (deg)", 0.0, 70.0, 0.0, 1.0)
window = st.radio("Measurement information", ["Single colour: 600 nm", "Spectrum: 420–780 nm"])
wavelength = np.linspace(400, 800, 201)
result = multilayer(wavelength, [1, 1.8, 1.5], [thickness], angle)
figure = go.Figure()
for values, name in [(result.R_s, "s polarization"), (result.R_p, "p polarization")]:
    figure.add_scatter(x=wavelength, y=values, name=name)
figure.update_layout(xaxis_title="Wavelength (nm)", yaxis_title="Reflectance (fraction)")
st.plotly_chart(figure)
measured_axis = np.full(8, 600.0) if window.startswith("Single") else np.linspace(420, 780, 81)
observed = observable(measured_axis, [1, 1.8, 1.5], [thickness], angle, "reflectance")
grid = np.linspace(20, 700, 801)
scores = thickness_scan(
    measured_axis, [1, 1.8, 1.5], [100], 0, grid, observed, angle_deg=angle, sigma=0.002
)
profile = go.Figure(go.Scatter(x=grid, y=1 + scores, name="Conditional thickness scan"))
profile.add_vline(x=thickness, line_dash="dot", annotation_text="Synthetic truth")
profile.update_layout(
    xaxis_title="Trial thickness (nm)", yaxis_title="1 + weighted mismatch", yaxis_type="log"
)
st.plotly_chart(profile)
st.info(
    "Separated minima represent thickness ambiguity. A local optimizer's precision does not "
    "rule out other interference orders. Here observations are noiseless and 0.002 is only "
    "a plotting weight, not a measured uncertainty."
)
