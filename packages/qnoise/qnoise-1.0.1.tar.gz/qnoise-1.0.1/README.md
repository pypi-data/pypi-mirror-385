# qNoise - Python Package

Non-Gaussian colored noise generator for Python.

[![PyPI version](https://badge.fury.io/py/qnoise.svg)](https://badge.fury.io/py/qnoise)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://img.shields.io/badge/DOI-10.1016%2Fj.softx.2022.101034-blue)](https://doi.org/10.1016/j.softx.2022.101034)

## Installation
```bash
pip install qnoise
```

### Requirements

- Python ≥ 3.8
- NumPy ≥ 1.20
- C++11 compatible compiler

**Platform-specific compiler setup:**

- **macOS:** `xcode-select --install`
- **Linux:** `sudo apt-get install build-essential` (Debian/Ubuntu)
- **Windows:** [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)

## Quick Start
```python
import qnoise
import numpy as np
import matplotlib.pyplot as plt

# Seed for reproducibility
qnoise.seed_manual(42)

# Generate non-Gaussian colored noise
noise = qnoise.generate(tau=1.0, q=1.5, N=10000)

# Generate Gaussian colored noise (Ornstein-Uhlenbeck)
gauss_noise = qnoise.ornstein_uhlenbeck(tau=1.0, N=10000)

# Plot
plt.plot(noise[:1000])
plt.title('Non-Gaussian Colored Noise (q=1.5)')
plt.show()
```

## Parameters

### tau (autocorrelation time)
Controls temporal correlation:
- `tau = 0`: White noise (uncorrelated)
- `tau > 0`: Colored noise with correlation time tau

### q (statistics parameter)
Controls distribution shape:
- `q = 1`: Gaussian (Ornstein-Uhlenbeck)
- `q < 1`: Sub-Gaussian (bounded support)
- `q > 1`: Supra-Gaussian (heavy tails)

### Other parameters
- `N`: Number of samples to generate
- `H`: Integration time step (default: 0.01)
- `temp_N`: Transient samples to discard (default: auto-computed)

## Functions

### High-Level Interface
```python
# Generate qNoise array
qnoise.generate(tau, q, N=1000, H=0.01, temp_N=-1, norm=False)

# Generate Ornstein-Uhlenbeck (Gaussian colored) noise
qnoise.ornstein_uhlenbeck(tau, N=1000, H=0.01, temp_N=-1, 
                          white_noise=False, ini_cond=0.0)
```

### Low-Level Interface (Advanced)

For custom integration loops:
```python
# Single integration steps
qnoise.qnoise_step(x, tau, q, H, sqrt_H)
qnoise.qnoise_norm_step(x, tau, q, H, sqrt_H)
qnoise.ornstein_uhlenbeck_step(x, tau, H)

# White noise
qnoise.gauss_white_noise()

# Random seed control
qnoise.seed_manual(seed)
qnoise.seed_timer()
```

## Applications

- **Algorithm robustness testing:** Test ML models against realistic non-Gaussian noise
- **Monte Carlo simulations:** Financial risk models, reliability analysis
- **Rare event simulation:** Heavy-tailed noise for stress-testing
- **Signal processing:** Benchmark denoising algorithms
- **Stochastic modeling:** Complex systems with non-Gaussian dynamics

## Examples

### Compare Different Statistics
```python
import qnoise
import matplotlib.pyplot as plt

qnoise.seed_manual(42)

fig, axes = plt.subplots(3, 2, figsize=(12, 10))

for i, q in enumerate([0.5, 1.0, 1.5]):
    # Time series
    noise = qnoise.generate(tau=1.0, q=q, N=10000)
    axes[i, 0].plot(noise[:1000])
    axes[i, 0].set_title(f'q={q} Time Series')
    
    # Distribution
    axes[i, 1].hist(noise, bins=50, density=True, alpha=0.7)
    axes[i, 1].set_title(f'q={q} Distribution')

plt.tight_layout()
plt.show()
```

### Autocorrelation Analysis
```python
import qnoise
import numpy as np
import matplotlib.pyplot as plt

qnoise.seed_manual(42)

# Generate noise with different correlation times
for tau in [0.1, 1.0, 10.0]:
    noise = qnoise.generate(tau=tau, q=1.0, N=50000)
    
    # Compute autocorrelation
    autocorr = np.correlate(noise - np.mean(noise), 
                           noise - np.mean(noise), 
                           mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    autocorr /= autocorr[0]
    
    plt.plot(autocorr[:200], label=f'tau={tau}')

plt.xlabel('Lag')
plt.ylabel('Autocorrelation')
plt.legend()
plt.show()
```

## Citation

If you use qNoise in your research, please cite:
```bibtex
@article{deza2022qnoise,
  title={qNoise: A generator of non-Gaussian colored noise},
  author={Deza, J. Ignacio and Ihshaish, Hisham},
  journal={SoftwareX},
  volume={18},
  pages={101034},
  year={2022},
  publisher={Elsevier},
  doi={10.1016/j.softx.2022.101034}
}
```

## Links

- **Paper:** https://doi.org/10.1016/j.softx.2022.101034
- **Demo:** https://ignaciodeza.github.io/qNoise/
- **GitHub:** https://github.com/ignaciodeza/qNoise
- **C++ Version:** [cpp/](https://github.com/ignaciodeza/qNoise/tree/main/cpp)
- **Go Version:** [go/](https://github.com/ignaciodeza/qNoise/tree/main/go)

## License

MIT License - see [LICENSE](../LICENSE) file.

## Author

**J. Ignacio Deza**  
Senior Lecturer in Data Science  
University of the West of England, Bristol  
ignacio.deza@uwe.ac.uk
