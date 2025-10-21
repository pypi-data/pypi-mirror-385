"""
qNoise - Non-Gaussian Colored Noise Generator

A generator of self-correlated, non-Gaussian colored random noise for
complex systems analysis.

Based on: Deza, J.I., Ihshaish, H. (2022). qNoise: A generator of 
non-Gaussian colored noise. SoftwareX, 18, 101034.
https://doi.org/10.1016/j.softx.2022.101034

Examples
--------
>>> import qnoise
>>> qnoise.seed_manual(42)  # For reproducibility
>>> 
>>> # Generate non-Gaussian colored noise
>>> noise = qnoise.generate(tau=1.0, q=1.5, N=10000)
>>> 
>>> # Generate Gaussian colored noise (Ornstein-Uhlenbeck)
>>> gauss_noise = qnoise.ornstein_uhlenbeck(tau=1.0, N=10000)
"""

from ._qnoise import (
    generate,
    ornstein_uhlenbeck,
    qnoise_step,
    qnoise_norm_step,
    ornstein_uhlenbeck_step,
    gauss_white_noise,
    seed_manual,
    seed_timer,
    __version__
)

__author__ = "J. Ignacio Deza"
__email__ = "ignacio.deza@uwe.ac.uk"

__all__ = [
    "generate",
    "ornstein_uhlenbeck",
    "qnoise_step",
    "qnoise_norm_step", 
    "ornstein_uhlenbeck_step",
    "gauss_white_noise",
    "seed_manual",
    "seed_timer",
    "__version__",
]

# Auto-seed on import
seed_timer()