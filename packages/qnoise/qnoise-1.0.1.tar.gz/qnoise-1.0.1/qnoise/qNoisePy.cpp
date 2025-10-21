/*
qNoise: A generator of non-Gaussian colored noise
Copyright © 2021-2025, J. Ignacio Deza
email: ignacio.deza@uwe.ac.uk

Description:
qNoise is a non-Gaussian colored random noise generator for complex systems.

License: MIT License
See LICENSE file in the repository root for full license text.
*/

#include <iostream>
#include <cstdlib>
#include <vector>
#include <cmath>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

// Include the core qNoise implementation
#include "qNoise.h"

// Global generator instance
qNoiseGen gen;

// High-level interface: generate array of qNoise values
std::vector<double> generate_qnoise(double tau, double q, int N, double H, 
                                     int temp_N, bool norm) {
    double x;
    std::vector<double> output(N);
    double sqrt_H = std::sqrt(H);
    
    if (tau < 0) tau = -tau;
    if (tau == 0) tau = H;

    if (temp_N < 0)
        temp_N = static_cast<int>(2.0 * tau / H);

    x = gen.gaussWN() / 100.0;
    
    for (int i = -temp_N; i < N; i++) {
        if (norm)
            x = gen.qNoiseNorm(x, tau, q, H, sqrt_H);
        else  
            x = gen.qNoise(x, tau, q, H, sqrt_H);
        
        if (i >= 0)
            output[i] = x;
    }
    return output;
}

// High-level interface: generate array of Ornstein-Uhlenbeck values
std::vector<double> generate_ornstein_uhlenbeck(double tau, int N, double H, 
                                                 int temp_N, bool white_noise, 
                                                 double ini_cond) {
    double x;
    std::vector<double> output(N);
    
    if (tau < 0) tau = -tau;
    if (tau == 0) white_noise = true;

    if (white_noise) {
        for (int i = 0; i < N; i++) 
            output[i] = gen.gaussWN();
        return output;
    }

    if (temp_N < 0) {
        temp_N = static_cast<int>(2.0 * tau / H);
        x = gen.gaussWN() / 100.0;
    } else {
        x = ini_cond;
    }

    for (int i = -temp_N; i < N; i++) {
        x = gen.orsUhl(x, tau, H);
        if (i >= 0)
            output[i] = x;
    }
    return output;
}

// Python interface
namespace py = pybind11;

// Wrap high-level qNoise function
py::array_t<double> py_qnoise(double tau, double q, int N, double H, 
                               int temp_N, bool norm) {
    std::vector<double> result_vec = generate_qnoise(tau, q, N, H, temp_N, norm);

    auto result = py::array_t<double>(N);
    auto result_buffer = result.request();
    double *result_ptr = static_cast<double*>(result_buffer.ptr);

    std::memcpy(result_ptr, result_vec.data(), result_vec.size() * sizeof(double));
    return result;
}

// Wrap high-level Ornstein-Uhlenbeck function
py::array_t<double> py_ornstein_uhlenbeck(double tau, int N, double H, 
                                          int temp_N, bool white_noise, 
                                          double ini_cond) {
    std::vector<double> result_vec = generate_ornstein_uhlenbeck(tau, N, H, 
                                                                  temp_N, 
                                                                  white_noise, 
                                                                  ini_cond);

    auto result = py::array_t<double>(N);
    auto result_buffer = result.request();
    double *result_ptr = static_cast<double*>(result_buffer.ptr);

    std::memcpy(result_ptr, result_vec.data(), result_vec.size() * sizeof(double));
    return result;
}

// Low-level interface wrappers (for advanced users)
double py_qnoise_single(double x, double tau, double q, double H, double sqrt_H) {
    return gen.qNoise(x, tau, q, H, sqrt_H);
}

double py_qnoise_norm_single(double x, double tau, double q, double H, double sqrt_H) {
    return gen.qNoiseNorm(x, tau, q, H, sqrt_H);
}

double py_ors_uhl_single(double x, double tau, double H) {
    return gen.orsUhl(x, tau, H);
}

double py_gauss_wn() {
    return gen.gaussWN();
}

void py_seed_manual(unsigned int seed) {
    gen.seedManual(seed);
}

void py_seed_timer() {
    gen.seedTimer();
}

// Python module definition
PYBIND11_MODULE(_qnoise, m) {
    m.doc() = R"pbdoc(
        qNoise - Non-Gaussian Colored Noise Generator
        
        A generator of self-correlated, non-Gaussian colored random noise.
        
        Based on: Deza, J.I., Ihshaish, H. (2022). qNoise: A generator of 
        non-Gaussian colored noise. SoftwareX, 18, 101034.
        https://doi.org/10.1016/j.softx.2022.101034
    )pbdoc";

    // High-level array generation functions
    m.def("generate", &py_qnoise, 
          R"pbdoc(
          Generate array of qNoise values.
          
          Parameters
          ----------
          tau : float
              Autocorrelation time
          q : float
              Statistics parameter (q=1: Gaussian, q<1: bounded, q>1: heavy-tailed)
          N : int, optional
              Number of samples to generate (default: 1000)
          H : float, optional
              Integration time step (default: 0.01)
          temp_N : int, optional
              Transient samples to discard (default: auto = 2*tau/H)
          norm : bool, optional
              Use normalized version (default: False)
          
          Returns
          -------
          numpy.ndarray
              Array of qNoise values
              
          Examples
          --------
          >>> import qnoise
          >>> qnoise.seed_manual(42)
          >>> noise = qnoise.generate(tau=1.0, q=1.5, N=1000)
          >>> print(noise.shape)
          (1000,)
          )pbdoc",
          py::arg("tau"), 
          py::arg("q"), 
          py::arg("N") = 1000, 
          py::arg("H") = 0.01, 
          py::arg("temp_N") = -1, 
          py::arg("norm") = false);

    m.def("ornstein_uhlenbeck", &py_ornstein_uhlenbeck,
          R"pbdoc(
          Generate array of Ornstein-Uhlenbeck (Gaussian colored) noise.
          
          Parameters
          ----------
          tau : float
              Autocorrelation time (set to 0 for white noise)
          N : int, optional
              Number of samples to generate (default: 1000)
          H : float, optional
              Integration time step (default: 0.01)
          temp_N : int, optional
              Transient samples to discard (default: auto = 2*tau/H)
          white_noise : bool, optional
              Force white noise generation (default: False)
          ini_cond : float, optional
              Initial condition if temp_N >= 0 (default: 0)
          
          Returns
          -------
          numpy.ndarray
              Array of noise values
              
          Examples
          --------
          >>> import qnoise
          >>> qnoise.seed_manual(42)
          >>> noise = qnoise.ornstein_uhlenbeck(tau=1.0, N=1000)
          >>> print(noise.shape)
          (1000,)
          )pbdoc",
          py::arg("tau"), 
          py::arg("N") = 1000, 
          py::arg("H") = 0.01, 
          py::arg("temp_N") = -1, 
          py::arg("white_noise") = false, 
          py::arg("ini_cond") = 0.0);

    // Low-level single-step functions (for custom integrations)
    m.def("qnoise_step", &py_qnoise_single,
          "Single integration step of qNoise (advanced use)",
          py::arg("x"), py::arg("tau"), py::arg("q"), 
          py::arg("H"), py::arg("sqrt_H"));

    m.def("qnoise_norm_step", &py_qnoise_norm_single,
          "Single integration step of normalized qNoise (advanced use)",
          py::arg("x"), py::arg("tau"), py::arg("q"), 
          py::arg("H"), py::arg("sqrt_H"));

    m.def("ornstein_uhlenbeck_step", &py_ors_uhl_single,
          "Single integration step of Ornstein-Uhlenbeck (advanced use)",
          py::arg("x"), py::arg("tau"), py::arg("H"));

    m.def("gauss_white_noise", &py_gauss_wn,
          "Generate single Gaussian white noise value");

    // Random seed control
    m.def("seed_manual", &py_seed_manual,
          R"pbdoc(
          Manually seed the random number generator.
          
          Parameters
          ----------
          seed : int
              Seed value for reproducibility
              
          Examples
          --------
          >>> import qnoise
          >>> qnoise.seed_manual(42)
          )pbdoc",
          py::arg("seed"));

    m.def("seed_timer", &py_seed_timer,
          R"pbdoc(
          Seed random number generator using system time.
          
          Note: This is called automatically on import. Use seed_manual() 
          for reproducible results.
          )pbdoc");

    // Version info
    m.attr("__version__") = "1.0.0";
}