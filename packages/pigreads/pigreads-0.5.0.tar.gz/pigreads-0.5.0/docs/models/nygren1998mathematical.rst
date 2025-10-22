.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.h``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.

Nygren et al. 1998
==================

**Key:** ``nygren1998mathematical``

A mathematical model of the human atrial myocyte based on averaged
voltage-clamp data recorded from isolated single myocytes. This model
consists of a Hodgkin-Huxley–type equivalent circuit for the sarcolemma,
coupled with a fluid compartment model, which accounts for changes in ionic
concentrations in the cytoplasm as well as in the sarcoplasmic reticulum.
This formulation can reconstruct action potential data that are
representative of recordings from a majority of human atrial cells and
therefore provides a biophysically based account of the underlying ionic
currents.

References
----------
1. https://doi.org/10.1161/01.RES.82.1.63

Variables
---------
0. ``V = -74.2525``
1. ``Ca_c = 1.8147``
2. ``Ca_d = 7.2495e-05``
3. ``Ca_i = 6.729e-05``
4. ``Ca_rel = 0.6465``
5. ``Ca_up = 0.6646``
6. ``K_c = 5.3581``
7. ``K_i = 129.435``
8. ``Na_c = 130.011``
9. ``Na_i = 8.5547``
10. ``F1 = 0.4284``
11. ``F2 = 0.0028``
12. ``O_C = 0.0275``
13. ``O_Calse = 0.4369``
14. ``O_TC = 0.0133``
15. ``O_TMgC = 0.1961``
16. ``O_TMgMg = 0.7094``
17. ``d_L = 1.3005e-05``
18. ``f_L1 = 0.9986``
19. ``f_L2 = 0.9986``
20. ``h1 = 0.8814``
21. ``h2 = 0.8742``
22. ``m = 0.0032017``
23. ``n = 0.0048357``
24. ``p_a = 0.0001``
25. ``r = 0.0010678``
26. ``r_sus = 0.00015949``
27. ``s = 0.949``
28. ``s_sus = 0.9912``

Parameters
----------
- ``diffusivity_V = 1.0``
- ``Cm = 0.05``
- ``Ca_b = 1.8``
- ``K_b = 5.4``
- ``Mg_i = 2.5``
- ``Na_b = 130.0``
- ``E_Ca_app = 60.0``
- ``F = 96487.0``
- ``I_up_max = 2800.0``
- ``P_Na = 0.0016``
- ``R = 8314.0``
- ``T = 306.15``
- ``Vol_c = 0.000800224``
- ``Vol_d = 0.00011768``
- ``Vol_i = 0.005884``
- ``Vol_rel = 4.41e-05``
- ``Vol_up = 0.0003969``
- ``alpha_rel = 200000.0``
- ``d_NaCa = 0.0003``
- ``g_B_Ca = 0.078681``
- ``g_B_Na = 0.060599``
- ``g_Ca_L = 6.75``
- ``g_K1 = 3.0``
- ``g_Kr = 0.5``
- ``g_Ks = 1.0``
- ``g_sus = 2.75``
- ``g_t = 7.5``
- ``gamma = 0.45``
- ``i_CaP_max = 4.0``
- ``i_NaK_max = 70.8253``
- ``k_Ca = 0.025``
- ``k_CaP = 0.0002``
- ``k_NaCa = 0.0374842``
- ``k_NaK_K = 1.0``
- ``k_NaK_Na = 11.0``
- ``k_cyca = 0.0003``
- ``k_rel_d = 0.003``
- ``k_rel_i = 0.0003``
- ``k_srca = 0.5``
- ``k_xcs = 0.4``
- ``phi_Na_en = -1.68``
- ``r_recov = 0.815``
- ``tau_Ca = 24.7``
- ``tau_K = 10.0``
- ``tau_Na = 14.3``
- ``tau_di = 0.01``
- ``tau_tr = 0.01``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    // r gate
    const Real r_inf = 1.0 / (1.0 + exp((V - 1.0) / -11.0));
    const Real tau_r = 0.0035 * exp(-pow(V / 30.0, 2.0)) + 0.0015;
    *_new_r = r_inf + (r - r_inf) * exp(-(dt / tau_r));

    // s gate
    const Real s_inf = 1.0 / (1.0 + exp((V + 40.5) / 11.5));
    const Real tau_s = 0.4812 * exp(-pow((V + 52.45) / 14.97, 2.0)) + 0.01414;
    *_new_s = s_inf + (s - s_inf) * exp(-(dt / tau_s));

    // L type Ca channel
    const Real f_Ca = Ca_d / (Ca_d + k_Ca);
    const Real i_Ca_L = g_Ca_L * d_L * (f_Ca * f_L1 + (1.0 - f_Ca) * f_L2) * (V - E_Ca_app);

    // d_L gate
    const Real d_L_inf = 1.0 / (1.0 + exp((V + 9.0) / -5.8));
    const Real tau_d_L = 0.0027 * exp(-pow((V + 35.0) / 30.0, 2.0)) + 0.002;
    *_new_d_L = d_L_inf + (d_L - d_L_inf) * exp(-(dt / tau_d_L));

    // f_L1 gate
    const Real f_L_inf = 1.0 / (1.0 + exp((V + 27.4) / 7.1));
    const Real tau_f_L1 = 0.161 * exp(-pow((V + 40.0) / 14.4, 2.0)) + 0.01;
    *_new_f_L1 = f_L_inf + (f_L1 - f_L_inf) * exp(-(dt / tau_f_L1));

    // n gate
    const Real n_inf = 1.0 / (1.0 + exp((V - 19.9) / -12.7));
    const Real tau_n = 0.7 + 0.4 * exp(-pow((V - 20.0) / 20.0, 2.0));
    *_new_n = n_inf + (n - n_inf) * exp(-(dt / tau_n));

    // pa gate
    const Real p_a_inf = 1.0 / (1.0 + exp((V + 15.0) / -6.0));
    const Real tau_p_a = 0.03118 + 0.21718 * exp(-pow((V + 20.1376) / 22.1996, 2.0));
    *_new_p_a = p_a_inf + (p_a - p_a_inf) * exp(-(dt / tau_p_a));

    // pi gate
    const Real p_i = 1.0 / (1.0 + exp((V + 55.0) / 24.0));

    // intracellular Ca buffering
    const Real dot_O_C = 200000.0 * Ca_i * (1.0 - O_C) - 476.0 * O_C;
    const Real dot_O_TC = 78400.0 * Ca_i * (1.0 - O_TC) - 392.0 * O_TC;
    const Real dot_O_TMgC = 200000.0 * Ca_i * (1.0 - O_TMgC - O_TMgMg) - 6.6 * O_TMgC;
    *_new_O_C = O_C + dt*dot_O_C;
    *_new_O_TC = O_TC + dt*dot_O_TC;
    *_new_O_TMgC = O_TMgC + dt*dot_O_TMgC;
    *_new_O_TMgMg = O_TMgMg + dt*(2000.0 * Mg_i * (1.0 - O_TMgC - O_TMgMg) - 666.0 * O_TMgMg);

    // sarcolemmal calcium pump current
    const Real i_CaP = i_CaP_max * Ca_i / (Ca_i + k_CaP);

    // h1 gate
    const Real h_inf = 1.0 / (1.0 + exp((V + 63.6) / 5.3));
    const Real tau_h1 = 0.03 / (1.0 + exp((V + 35.1) / 3.2)) + 0.0003;
    *_new_h1 = h_inf + (h1 - h_inf) * exp(-(dt / tau_h1));

    // m gate
    const Real m_inf = 1.0 / (1.0 + exp((V + 27.12) / -8.21));
    const Real tau_m = 4.2e-05 * exp(-pow((V + 25.57) / 28.8, 2.0)) + 2.4e-05;
    *_new_m = m_inf + (m - m_inf) * exp(-(dt / tau_m));

    // sodium potassium pump
    const Real i_NaK = i_NaK_max * K_c / (K_c + k_NaK_K) * pow(Na_i, 1.5) / (pow(Na_i, 1.5) + pow(k_NaK_Na, 1.5)) * safe_divide(V + 150.0, V + 200.0);

    // r_sus gate
    const Real r_sus_inf = 1.0 / (1.0 + exp((V + 4.3) / -8.0));
    const Real tau_r_sus = 0.009 / (1.0 + exp((V + 5.0) / 12.0)) + 0.0005;
    *_new_r_sus = r_sus_inf + (r_sus - r_sus_inf) * exp(-(dt / tau_r_sus));

    // s_sus gate
    const Real s_sus_inf = 0.4 / (1.0 + exp((V + 20.0) / 10.0)) + 0.6;
    const Real tau_s_sus = 0.047 / (1.0 + exp((V + 60.0) / 10.0)) + 0.3;
    *_new_s_sus = s_sus_inf + (s_sus - s_sus_inf) * exp(-(dt / tau_s_sus));

    // f_L2 gate
    const Real tau_f_L2 = 1.3323 * exp(-pow((V + 40.0) / 14.2, 2.0)) + 0.0626;
    *_new_f_L2 = f_L_inf + (f_L2 - f_L_inf) * exp(-(dt / tau_f_L2));

    // h2 gate
    const Real tau_h2 = 0.12 / (1.0 + exp((V + 35.1) / 3.2)) + 0.003;
    *_new_h2 = h_inf + (h2 - h_inf) * exp(-(dt / tau_h2));

    // Ca handling by the SR
    const Real dot_O_Calse = 480.0 * Ca_rel * (1.0 - O_Calse) - 400.0 * O_Calse;
    const Real i_rel = alpha_rel * pow(F2 / (F2 + 0.25), 2.0) * (Ca_rel - Ca_i);
    const Real i_up = I_up_max * (Ca_i / k_cyca - k_xcs * k_xcs * Ca_up / k_srca) / ((Ca_i + k_cyca) / k_cyca + k_xcs * (Ca_up + k_srca) / k_srca);
    const Real r_act = 203.8 * (pow(Ca_i / (Ca_i + k_rel_i), 4.0) + pow(Ca_d / (Ca_d + k_rel_d), 4.0));
    const Real r_inact = 33.96 + 339.6 * pow(Ca_i / (Ca_i + k_rel_i), 4.0);
    *_new_O_Calse = O_Calse + dt*dot_O_Calse;
    *_new_F1 = F1 + dt*(r_recov * (1.0 - F1 - F2) - r_act * F1);
    *_new_F2 = F2 + dt*(r_act * F1 - r_inact * F2);

    // sodium current
    const Real E_Na = R * T / F * log(Na_c / Na_i);
    const Real i_Na =
      P_Na * m * m * m * (0.9 * h1 + 0.1 * h2) * Na_c * F * F / (R * T) *
      (fabs(V) < 1e-3
        ? R * T * (exp((-E_Na * F) / (R * T)) - 1.0) / F
        : V * (exp((V - E_Na) * F / (R * T)) - 1.0)
            / (exp(V * F / (R * T)) - 1.0)
      );

    // remaining
    const Real i_tr = (Ca_up - Ca_rel) * 2.0 * F * Vol_rel / tau_tr;
    const Real E_K = R * T / F * log(K_c / K_i);
    const Real i_NaCa = k_NaCa * (Na_i * Na_i * Na_i * Ca_c * exp(gamma * F * V / (R * T)) - Na_c * Na_c * Na_c * Ca_i * exp((gamma - 1.0) * V * F / (R * T))) / (1.0 + d_NaCa * (Na_c * Na_c * Na_c * Ca_i + Na_i * Na_i * Na_i * Ca_c));
    const Real E_Ca = R * T / (2.0 * F) * log(Ca_c / Ca_i);
    const Real i_B_Na = g_B_Na * (V - E_Na);
    const Real i_di = (Ca_d - Ca_i) * 2.0 * F * Vol_d / tau_di;
    *_new_Ca_rel = Ca_rel + dt*((i_tr - i_rel) / (2.0 * Vol_rel * F) - 31.0 * dot_O_Calse);
    *_new_Ca_up = Ca_up + dt*((i_up - i_tr) / (2.0 * Vol_up * F));
    const Real i_t = g_t * r * s * (V - E_K);
    const Real i_B_Ca = g_B_Ca * (V - E_Ca);
    *_new_Na_c = Na_c + dt*((Na_b - Na_c) / tau_Na + (i_Na + i_B_Na + 3.0 * i_NaK + 3.0 * i_NaCa + phi_Na_en) / (Vol_c * F));
    const Real i_Kr = g_Kr * p_a * p_i * (V - E_K);
    const Real i_Ks = g_Ks * n * (V - E_K);
    *_new_Ca_d = Ca_d + dt*(-(i_Ca_L + i_di) / (2.0 * Vol_d * F));
    *_new_Na_i = Na_i + dt*(-(i_Na + i_B_Na + 3.0 * i_NaK + 3.0 * i_NaCa + phi_Na_en) / (Vol_i * F));
    const Real i_K1 = g_K1 * pow(K_c / 1.0, 0.4457) * (V - E_K) / (1.0 + exp(1.5 * (V - E_K + 3.6) * F / (R * T)));
    const Real i_sus = g_sus * r_sus * s_sus * (V - E_K);
    *_new_Ca_c = Ca_c + dt*((Ca_b - Ca_c) / tau_Ca + (i_Ca_L + i_B_Ca + i_CaP - 2.0 * i_NaCa) / (2.0 * Vol_c * F));
    *_new_K_c = K_c + dt*((K_b - K_c) / tau_K + (i_t + i_sus + i_K1 + i_Kr + i_Ks - 2.0 * i_NaK) / (Vol_c * F));
    *_new_Ca_i = Ca_i + dt*(-(-i_di + i_B_Ca + i_CaP - 2.0 * i_NaCa + i_up - i_rel) / (2.0 * Vol_i * F) - (0.08 * dot_O_TC + 0.16 * dot_O_TMgC + 0.045 * dot_O_C));
    *_new_K_i = K_i + dt*(-(i_t + i_sus + i_K1 + i_Kr + i_Ks - 2.0 * i_NaK) / (Vol_i * F));
    *_new_V = V + dt*(_diffuse_V - (i_Na + i_Ca_L + i_t + i_sus + i_K1 + i_Kr + i_Ks + i_B_Na + i_B_Ca + i_NaK + i_CaP + i_NaCa) / Cm);

    // check for unphysical values
    if(*_new_Ca_c <= 0.0) { *_new_Ca_c = VERY_SMALL_NUMBER; }
    if(*_new_Ca_d <= 0.0) { *_new_Ca_d = VERY_SMALL_NUMBER; }
    if(*_new_Ca_i <= 0.0) { *_new_Ca_i = VERY_SMALL_NUMBER; }
    if(*_new_Ca_rel <= 0.0) { *_new_Ca_rel = VERY_SMALL_NUMBER; }
    if(*_new_Ca_up <= 0.0) { *_new_Ca_up = VERY_SMALL_NUMBER; }
    if(*_new_K_c <= 0.0) { *_new_K_c = VERY_SMALL_NUMBER; }
    if(*_new_K_i <= 0.0) { *_new_K_i = VERY_SMALL_NUMBER; }
    if(*_new_Na_c <= 0.0) { *_new_Na_c = VERY_SMALL_NUMBER; }
    if(*_new_Na_i <= 0.0) { *_new_Na_i = VERY_SMALL_NUMBER; }


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
    - atria

