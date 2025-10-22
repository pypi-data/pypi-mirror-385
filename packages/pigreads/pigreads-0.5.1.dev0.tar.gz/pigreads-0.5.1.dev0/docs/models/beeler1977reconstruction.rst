.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.h``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.

Beeler & Reuter 1977
====================

**Key:** ``beeler1977reconstruction``

The G.W. Beeler and H. Reuter 1977 model was developed to describe the
mammalian ventricular action potential. The total ionic flux is divided into
only four discrete, individual ionic currents. The main additional feature of
the Beeler-Reuter ionic current model is a representation of the intracellular
calcium ion concentration.

References
----------
1. https://doi.org/10.1113/jphysiol.1977.sp011853

Variables
---------
0. ``V = -84.624``
1. ``m = 0.011``
2. ``h = 0.988``
3. ``j = 0.975``
4. ``d = 0.003``
5. ``f = 0.994``
6. ``x1 = 0.0001``
7. ``Cai = 0.0001``

Parameters
----------
- ``diffusivity_V = 1.0``
- ``g_s = 0.0009``
- ``E_Na = 50.0``
- ``g_Na = 0.04``
- ``g_Nac = 3e-05``
- ``C = 0.01``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    // slow inward current
    const Real E_s = -82.3 - 13.0287 * log(Cai * 0.001);
    const Real i_s = g_s * d * f * (V - E_s);
    *_new_Cai = Cai + dt*(-0.01 * i_s + 0.07 * (0.0001 - Cai));

    // d gate
    const Real alpha_d = 0.095 * exp(-(V - 5.0) / 100.0) / (1.0 + exp(-(V - 5.0) / 13.89));
    const Real beta_d = 0.07 * exp(-(V + 44.0) / 59.0) / (1.0 + exp((V + 44.0) / 20.0));
    const Real tau_d = 1.0 / (alpha_d + beta_d);
    const Real d_inf = alpha_d * tau_d;
    *_new_d = d_inf + (d - d_inf) * exp(-dt / tau_d);

    // f gate
    const Real alpha_f = 0.012 * exp(-(V + 28.0) / 125.0) / (1.0 + exp((V + 28.0) / 6.67));
    const Real beta_f = 0.0065 * exp(-(V + 30.0) / 50.0) / (1.0 + exp(-(V + 30.0) / 5.0));
    const Real tau_f = 1.0 / (alpha_f + beta_f);
    const Real f_inf = alpha_f * tau_f;
    *_new_f = f_inf + (f - f_inf) * exp(-dt / tau_f);

    // sodium current
    const Real i_Na = (g_Na * m * m * m * h * j + g_Nac) * (V - E_Na);

    // h gate
    const Real alpha_h = 0.126 * exp(-0.25 * (V + 77.0));
    const Real beta_h = 1.7 / (exp(-0.082 * (V + 22.5)) + 1.0);
    const Real tau_h = 1.0 / (alpha_h + beta_h);
    const Real h_inf = alpha_h * tau_h;
    *_new_h = h_inf + (h - h_inf) * exp(-dt / tau_h);

    // j gate
    const Real alpha_j = 0.055 * exp(-0.25 * (V + 78.0)) / (exp(-0.2 * (V + 78.0)) + 1.0);
    const Real beta_j = 0.3 / (exp(-0.1 * (V + 32.0)) + 1.0);
    const Real tau_j = 1.0 / (alpha_j + beta_j);
    const Real j_inf = alpha_j * tau_j;
    *_new_j = j_inf + (j - j_inf) * exp(-dt / tau_j);

    // m gate
    const Real alpha_m = -safe_divide(V + 47.0, exp(-0.1 * (V + 47.0)) - 1.0);
    const Real beta_m = 40.0 * exp(-0.056 * (V + 72.0));
    const Real tau_m = 1.0 / (alpha_m + beta_m);
    const Real m_inf = alpha_m * tau_m;
    *_new_m = m_inf + (m - m_inf) * exp(-dt / tau_m);

    // time dependent outward current
    const Real i_x1 = x1 * 0.008 * (exp(0.04 * (V + 77.0)) - 1.0) / (exp(0.04 * (V + 35.0)));

    // x1 gate
    const Real alpha_x1 = 0.0005 * exp((V + 50.0) / 12.1) / (1.0 + exp((V + 50.0) / 17.5));
    const Real beta_x1 = 0.0013 * exp(-(V + 20.0) / 16.67) / (1.0 + exp(-(V + 20.0) / 25.0));
    const Real tau_x1 = 1.0 / (alpha_x1 + beta_x1);
    const Real x1_inf = alpha_x1 * tau_x1;
    *_new_x1 = x1_inf + (x1 - x1_inf) * exp(-dt / tau_x1);

    // time independent outward current
    const Real i_K1 = 0.0035 * (4.0 * (exp(0.04 * (V + 85.0)) - 1.0) / (exp(0.08 * (V + 53.0)) + exp(0.04 * (V + 53.0))) + 0.2 * safe_divide(V + 23.0, 1.0 - exp(-0.04 * (V + 23.0))));

    // membrane
    *_new_V = V + dt*(_diffuse_V - (i_Na + i_s + i_x1 + i_K1) / C);


.. raw:: html

    </details>

Additional metadata
-------------------

.. code-block:: yaml

    keywords:
    - excitable media
    - electrophysiology
    - heart
    - phenomenological
    - ventricle

