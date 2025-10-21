/*
qNoise: A generator of non-Gaussian colored noise
Copyright (c) 2021-2025 J. Ignacio Deza

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

Description:
qNoise is a non-Gaussian colored random noise generator. It is a handy source 
of self-correlated noise for a great variety of applications. It depends on 
two parameters only: tau for controlling the autocorrelation, and q for 
controlling the statistics.

- q = 1: Ornstein-Uhlenbeck (colored Gaussian) noise
- q < 1: Bounded noise (sub-Gaussian)
- q > 1: Heavy-tailed noise (supra-Gaussian)

The noise is generated via a stochastic differential equation using the Heun 
method (a second-order Runge-Kutta integration scheme).

Requirements:
- C++11 or higher (uses <random> library)
- No external dependencies

Contact: ignacio.deza@uwe.ac.uk

Citation:
Deza, J.I., Ihshaish, H. (2022). qNoise: A generator of non-Gaussian colored 
noise. SoftwareX, 18, 101034. https://doi.org/10.1016/j.softx.2022.101034
*/

#ifndef QNOISEGEN_H
#define QNOISEGEN_H

#include <iostream>
#include <climits>
#include <cstdio>
#include <ctime>
#include <cmath>
#include <random>
#include <chrono>
#include <ctime>
#include <ratio>

class qNoiseGen {
    double potQNoisePrime(double eta, double tau, double q);
    typedef std::chrono::high_resolution_clock myclock;
    myclock::time_point beginning;
    unsigned seed;
    std::mt19937 generator;
    std::normal_distribution<double> randNorm;
    std::uniform_real_distribution<double> uniform;

public:
    void seedManual(unsigned UserSeed);
    void seedTimer();
    double gaussWN();
    double orsUhl(double x, double tau, double H);
    double qNoise(double x, double tau, double q, double H, double sqrt_H);
    double qNoiseNorm(double x, double tau, double q, double H, double sqrt_H);

    qNoiseGen() {
        std::normal_distribution<double> randNorm(0.0, 1.0);
        std::uniform_real_distribution<double> uniform(0.0,0.99);
        beginning = myclock::now();
        seedTimer();
    }
};

#endif  // QNOISEGEN_H
