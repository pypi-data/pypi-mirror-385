.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.h``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.

Luo & Rudy 1994
===============

**Key:** ``luo1994dynamic``

This model provides the basis for the study of arrhythmogenic activity of the
single myocyte including afterdepolarizations and triggered activity (by
including descriptions of Ca2+ regulated currents). It can simulate cellular
responses under different degrees of Ca2+ overload.

References
----------
1. https://doi.org/10.1161/01.res.74.6.1071

Variables
---------
0. ``V = -84.624``
1. ``m = 0.0``
2. ``h = 1.0``
3. ``j = 1.0``
4. ``d = 0.0``
5. ``f = 1.0``
6. ``X = 0.0``
7. ``Nai = 10.0``
8. ``Cai = 0.00012``
9. ``Ki = 145.0``
10. ``Ca_JSR = 1.8``
11. ``Ca_NSR = 1.8``

Parameters
----------
- ``diffusivity_V = 1.0``
- ``f_Ca_Km_Ca = 0.0006``
- ``Ca_NSR_max = 15.0``
- ``G_rel_max = 60.0``
- ``I_up = 0.005``
- ``K_mrel = 0.0008``
- ``K_mup = 0.00092``
- ``delta_Ca_i2 = 0.0``
- ``delta_Ca_ith = 0.00018``
- ``t_CICR = 0.0``
- ``tau_off = 2.0``
- ``tau_on = 2.0``
- ``tau_tr = 180.0``
- ``G_rel_peak = 0.0``
- ``K_leak = 0.0003333333333333333``
- ``G_rel = -0.0``
- ``I_pCa = 0.0115``
- ``K_mpCa = 0.0005``
- ``P_Ca = 5.4e-06``
- ``P_K = 1.93e-09``
- ``P_Na = 6.75e-09``
- ``gamma_Cai = 1.0``
- ``gamma_Cao = 0.34``
- ``gamma_Ki = 0.75``
- ``gamma_Ko = 0.75``
- ``gamma_Nai = 0.75``
- ``gamma_Nao = 0.75``
- ``K_NaCa = 20.0``
- ``K_mCa = 1.38``
- ``K_mNa = 87.5``
- ``K_sat = 0.1``
- ``eta = 0.35``
- ``g_Cab = 3.016e-05``
- ``g_Na = 0.16``
- ``Am = 200.0``
- ``Cao = 1.8``
- ``Ko = 5.4``
- ``Nao = 140.0``
- ``V_JSR = 0.0048``
- ``V_NSR = 0.0552``
- ``V_myo = 0.68``
- ``Cm = 0.01``
- ``F = 96845.0``
- ``R = 8314.5``
- ``T = 310.0``
- ``K_m_ns_Ca = 0.0012``
- ``P_ns_Ca = 1.75e-09``
- ``g_Kp = 0.000183``
- ``g_Nab = 1.41e-05``
- ``I_NaK = 0.015``
- ``K_mKo = 1.5``
- ``K_mNai = 10.0``
- ``sigma = 1.0009103049457284``
- ``PR_NaK = 0.01833``
- ``g_K_max = 0.00282``
- ``g_K = 0.00282``
- ``g_K1_max = 0.0075``
- ``g_K1 = 0.0075``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    // L type Ca channel d gate
    const Real d_inf = 1.0 / (1.0 + exp(-((V + 10.0) / 6.24)));
    const Real tau_d = d_inf * safe_divide(1.0 - exp(-((V + 10.0) / 6.24)), 0.035 * (V + 10.0));
    *_new_d = d_inf + (d - d_inf) * exp(-safe_divide(dt, tau_d));

    // L type Ca channel f Ca gate
    const Real f_Ca_f_Ca = 1.0 / (1.0 + pow(Cai / f_Ca_Km_Ca, 2.0));

    // L type Ca channel f gate
    const Real f_inf = 1.0 / (1.0 + exp((V + 35.06) / 8.6)) + 0.6 / (1.0 + exp((50.0 - V) / 20.0));
    const Real tau_f = 1.0 / (0.0197 * exp(-pow(0.0337 * (V + 10.0), 2.0)) + 0.02);
    *_new_f = f_inf + (f - f_inf) * exp(-dt / tau_f);

    // calcium fluxes in the SR
    const Real i_tr = (Ca_NSR - Ca_JSR) / tau_tr;
    const Real i_up = I_up * (Cai / (Cai + K_mup));
    const Real i_leak = K_leak * Ca_NSR;
    const Real i_rel = G_rel * (Ca_JSR - Cai);

    // fast sodium current h gate
    const Real alpha_h = ((V < -40.0) ? 0.135 * exp((80.0 + V) / -6.8) : 0.0);
    const Real beta_h = ((V < -40.0) ? 3.56 * exp(0.079 * V) + 310000.0 * exp(0.35 * V) : 1.0 / (0.13 * (1.0 + exp((V + 10.66) / -11.1))));
    const Real tau_h = 1.0 / (alpha_h + beta_h);
    const Real h_inf = alpha_h * tau_h;
    *_new_h = h_inf + (h - h_inf) * exp(-dt / tau_h);

    // fast sodium current j gate
    const Real alpha_j = ((V < -40.0) ? (-127140.0 * exp(0.2444 * V) - 3.474e-05 * exp(-0.04391 * V)) * ((V + 37.78) / (1.0 + exp(0.311 * (V + 79.23)))) : 0.0);
    const Real beta_j = ((V < -40.0) ? 0.1212 * exp(-0.01052 * V) / (1.0 + exp(-0.1378 * (V + 40.14))) : 0.3 * exp(-2.535e-07 * V) / (1.0 + exp(-0.1 * (V + 32.0))));
    const Real tau_j = 1.0 / (alpha_j + beta_j);
    const Real j_inf = alpha_j * tau_j;
    *_new_j = j_inf + (j - j_inf) * exp(-dt / tau_j);

    // fast sodium current m gate
    const Real alpha_m = 0.32 * safe_divide(V + 47.13, 1.0 - exp(-0.1 * (V + 47.13)));
    const Real beta_m = 0.08 * exp(-V / 11.0);
    const Real tau_m = 1.0 / (alpha_m + beta_m);
    const Real m_inf = alpha_m * tau_m;
    *_new_m = m_inf + (m - m_inf) * exp(-dt / tau_m);

    // sarcolemmal calcium pump
    const Real i_p_Ca = I_pCa * (Cai / (K_mpCa + Cai));

    // time dependent potassium current X gate
    const Real alpha_X = 7.19e-05 * safe_divide(V + 30.0, 1.0 - exp(-0.148 * (V + 30.0)));
    const Real beta_X = 0.000131 * safe_divide(V + 30.0, -1.0 + exp(0.0687 * (V + 30.0)));
    const Real tau_X = safe_divide(1.0, alpha_X + beta_X);
    const Real X_inf = alpha_X * tau_X;
    *_new_X = X_inf + (X - X_inf) * exp(-safe_divide(dt, tau_X));

    // time dependent potassium current Xi gate
    const Real Xi = 1.0 / (1.0 + exp((V - 56.26) / 32.1));

    // ionic concentrations
    *_new_Ca_NSR = Ca_NSR + dt*(-(i_leak + i_tr - i_up));
    *_new_Ca_JSR = Ca_JSR + dt*(-(i_rel - i_tr * (V_NSR / V_JSR)));

    // non specific calcium activated current
    const Real EnsCa = R * T / F * log((Ko + Nao) / (Ki + Nai));
    const Real Vns = V - EnsCa;
    const Real I_ns_K = P_ns_Ca * (Vns * F * F / (R * T)) * safe_divide(gamma_Ki * Ki * exp(Vns * F / (R * T)) - gamma_Ko * Ko, exp(Vns * F / (R * T)) - 1.0);
    const Real I_ns_Na = P_ns_Ca * (Vns * F * F / (R * T)) * safe_divide(gamma_Nai * Nai * exp(Vns * F / (R * T)) - gamma_Nao * Nao, exp(Vns * F / (R * T)) - 1.0);
    const Real i_ns_K = I_ns_K * (1.0 / (1.0 + pow(K_m_ns_Ca / Cai, 3.0)));
    const Real i_ns_Na = I_ns_Na * (1.0 / (1.0 + pow(K_m_ns_Ca / Cai, 3.0)));
    const Real i_ns_Ca = i_ns_Na + i_ns_K;

    // plateau potassium current
    const Real Kp = 1.0 / (1.0 + exp((7.488 - V) / 5.98));

    // sodium potassium pump
    const Real f_NaK = 1.0 / (1.0 + 0.1245 * exp(-0.1 * (V * F / (R * T))) + 0.0365 * sigma * exp(-(V * F / (R * T))));
    const Real i_NaK = I_NaK * f_NaK * (1.0 / (1.0 + pow(K_mNai / Nai, 1.5))) * (Ko / (Ko + K_mKo));

    // time dependent potassium current
    const Real E_K = R * T / F * log((Ko + PR_NaK * Nao) / (Ki + PR_NaK * Nai));
    const Real i_K = g_K * X * X * Xi * (V - E_K);

    // time independent potassium current
    const Real E_K1 = R * T / F * log(Ko / Ki);

    // time independent potassium current K1 gate
    const Real alpha_K1 = 1.02 / (1.0 + exp(0.2385 * (V - E_K1 - 59.215)));
    const Real beta_K1 = (0.49124 * exp(0.08032 * (V + 5.476 - E_K1)) + exp(0.06175 * (V - (E_K1 + 594.31)))) / (1.0 + exp(-0.5143 * (V - E_K1 + 4.753)));
    const Real K1_inf = alpha_K1 / (alpha_K1 + beta_K1);

    // *remaining*
    const Real I_CaCa = P_Ca * 4.0 * (V * F * F / (R * T)) * safe_divide(gamma_Cai * Cai * exp(2.0 * V * F / (R * T)) - gamma_Cao * Cao, exp(2.0 * V * F / (R * T)) - 1.0);
    const Real I_CaK = P_K * (V * F * F / (R * T)) * safe_divide(gamma_Ki * Ki * exp(V * F / (R * T)) - gamma_Ko * Ko, exp(V * F / (R * T)) - 1.0);
    const Real I_CaNa = P_Na * (V * F * F / (R * T)) * safe_divide(gamma_Nai * Nai * exp(V * F / (R * T)) - gamma_Nao * Nao, exp(V * F / (R * T)) - 1.0);
    const Real i_NaCa = K_NaCa * (1.0 / (K_mNa * K_mNa * K_mNa + Nao * Nao * Nao)) * (1.0 / (K_mCa + Cao)) * (1.0 / (1.0 + K_sat * exp((eta - 1.0) * V * (F / (R * T))))) * (exp(eta * V * (F / (R * T))) * Nai * Nai * Nai * Cao - exp((eta - 1.0) * V * (F / (R * T))) * Nao * Nao * Nao * Cai);
    const Real E_CaN = R * T / (2.0 * F) * log(Cao / Cai);
    const Real E_Na = R * T / F * log(Nao / Nai);
    const Real E_Kp = E_K1;
    const Real i_K1 = g_K1 * K1_inf * (V - E_K1);
    const Real i_CaCa = d * f * f_Ca_f_Ca * I_CaCa;
    const Real i_CaK = d * f * f_Ca_f_Ca * I_CaK;
    const Real i_CaNa = d * f * f_Ca_f_Ca * I_CaNa;
    const Real i_Ca_b = g_Cab * (V - E_CaN);
    const Real i_Na = g_Na * m * m * m * h * j * (V - E_Na);
    const Real i_Kp = g_Kp * Kp * (V - E_Kp);
    const Real E_NaN = E_Na;
    const Real i_Ca_L = i_CaCa + i_CaK + i_CaNa;
    *_new_Cai = Cai + dt*(-(i_CaCa + i_p_Ca + i_Ca_b - i_NaCa) * (Am / (2.0 * V_myo * F)) + i_rel * (V_JSR / V_myo) + (i_leak - i_up) * (V_NSR / V_myo));
    *_new_Ki = Ki + dt*(-(i_CaK + i_K + i_K1 + i_Kp + i_ns_K + -(i_NaK * 2.0)) * (Am / (V_myo * F)));
    const Real i_Na_b = g_Nab * (V - E_NaN);
    *_new_Nai = Nai + dt*(-(i_Na + i_CaNa + i_Na_b + i_ns_Na + i_NaCa * 3.0 + i_NaK * 3.0) * (Am / (V_myo * F)));
    const Real dV_dt = -(i_Na + i_Ca_L + i_K + i_K1 + i_Kp + i_NaCa + i_p_Ca + i_Na_b + i_Ca_b + i_NaK + i_ns_Ca) / Cm;
    *_new_V = V + dt*(dV_dt + _diffuse_V);

    // check for unphysical values
    if(*_new_Nai <= 0.0) { *_new_Nai = VERY_SMALL_NUMBER; }
    if(*_new_Cai <= 0.0) { *_new_Cai = VERY_SMALL_NUMBER; }
    if(*_new_Ki <= 0.0) { *_new_Ki = VERY_SMALL_NUMBER; }
    if(*_new_Ca_JSR <= 0.0) { *_new_Ca_JSR = VERY_SMALL_NUMBER; }
    if(*_new_Ca_NSR <= 0.0) { *_new_Ca_NSR = VERY_SMALL_NUMBER; }


.. raw:: html

    </details>

Additional metadata
-------------------

.. code-block:: yaml

    keywords:
    - excitable media
    - electrophysiology
    - heart
    - human
    - ventricle

