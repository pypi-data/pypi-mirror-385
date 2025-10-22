.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.h``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.

Maleckar et al. 2008
====================

**Key:** ``maleckar2008mathematical``

A recently developed mathematical model of the human atrial myocyte including
heterogeneous cell-cell interaction on the action potential of the human
atrium. This model provides a basis for beginning to assess the utility of
mathematical modeling in understanding detailed cell-cell interactions within
the complex paracrine environment of the human atrial myocardium.

References
----------
1. https://doi.org/10.1016/j.pbiomolbio.2009.01.010

Variables
---------
0. ``V = -74.031982``
1. ``Ca_c = 1.815768``
2. ``Ca_d = 7.1e-05``
3. ``Ca_i = 6.5e-05``
4. ``Ca_rel = 0.632613``
5. ``Ca_up = 0.649195``
6. ``K_c = 5.560224``
7. ``K_i = 129.485991``
8. ``Na_c = 130.022096``
9. ``Na_i = 8.516766``
10. ``F1 = 0.470055``
11. ``F2 = 0.002814``
12. ``O = 1.38222``
13. ``O_C = 0.026766``
14. ``O_Calse = 0.431547``
15. ``O_TC = 0.012922``
16. ``O_TMgC = 0.190369``
17. ``O_TMgMg = 0.714463``
18. ``a_ur = 0.000367``
19. ``d_L = 1.4e-05``
20. ``f_L1 = 0.998597``
21. ``f_L2 = 0.998586``
22. ``h1 = 0.877202``
23. ``h2 = 0.873881``
24. ``i_ur = 0.96729``
25. ``m = 0.003289``
26. ``n = 0.004374``
27. ``pa = 5.3e-05``
28. ``r = 0.001089``
29. ``s = 0.948597``

Parameters
----------
- ``diffusivity_V = 1.0``
- ``Cm = 50.0``
- ``Ca_b = 1.8``
- ``E_Ca_app = 60.0``
- ``K_NaCa = 0.0374842``
- ``K_NaK_K = 1.0``
- ``K_b = 5.4``
- ``Mg_i = 2.5``
- ``Na_b = 130.0``
- ``ACh = 1e-24``
- ``F = 96487.0``
- ``R = 8314.0``
- ``T = 306.15``
- ``I_up_max = 2800.0``
- ``P_Na = 0.0018``
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
- ``g_K1 = 3.1``
- ``g_Kr = 0.5``
- ``g_Ks = 1.0``
- ``g_Kur = 2.25``
- ``g_t = 8.25``
- ``gamma_Na = 0.45``
- ``i_CaP_max = 4.0``
- ``i_NaK_max = 68.55``
- ``k_Ca = 0.025``
- ``k_CaP = 0.0002``
- ``k_cyca = 0.0003``
- ``k_rel_d = 0.003``
- ``k_rel_i = 0.0003``
- ``k_srca = 0.5``
- ``k_xcs = 0.4``
- ``phi_Na_en = 0.0``
- ``pow_K_NaK_Na_15 = 36.4829``
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
    const Real r_infinity = 1.0 / (1.0 + exp((V - 1.0) / -11.0));
    const Real tau_r = 0.0035 * exp(-V * V / 30.0 / 30.0) + 0.0015;
    *_new_r = r_infinity + (r - r_infinity) * exp(-(dt / tau_r));

    // s gate
    const Real s_factor = (V + 52.45) / 15.8827;
    const Real s_infinity = 1.0 / (1.0 + exp((V + 40.5) / 11.5));
    const Real tau_s = 0.025635 * exp(-s_factor * s_factor) + 0.01414;
    *_new_s = s_infinity + (s - s_infinity) * exp(-(dt / tau_s));

    // L type Ca channel
    const Real f_Ca = Ca_d / (Ca_d + k_Ca);
    const Real i_Ca_L = g_Ca_L * d_L * (f_Ca * f_L1 + (1.0 - f_Ca) * f_L2) * (V - E_Ca_app);

    // d_L gate
    const Real d_L_factor = (V + 35.0) / 30.0;
    const Real d_L_infinity = 1.0 / (1.0 + exp((V + 9.0) / -5.8));
    const Real tau_d_L = 0.0027 * exp(-d_L_factor * d_L_factor) + 0.002;
    *_new_d_L = d_L_infinity + (d_L - d_L_infinity) * exp(-(dt / tau_d_L));

    // f_L1 gate
    const Real f_L_factor = V + 40.0;
    const Real f_L_infinity = 1.0 / (1.0 + exp((V + 27.4) / 7.1));
    const Real tau_f_L1 = 0.161 * exp(-f_L_factor * f_L_factor / 14.4 / 14.4) + 0.01;
    *_new_f_L1 = f_L_infinity + (f_L1 - f_L_infinity) * exp(-(dt / tau_f_L1));

    // n gate
    const Real n_factor = (V - 20.0) / 20.0;
    const Real n_infinity = 1.0 / (1.0 + exp((V - 19.9) / -12.7));
    const Real tau_n = 0.7 + 0.4 * exp(-n_factor * n_factor);
    *_new_n = n_infinity + (n - n_infinity) * exp(-(dt / tau_n));

    // pa gate
    const Real pa_infinity = 1.0 / (1.0 + exp((V + 15.0) / -6.0));
    const Real pa_factor = (V + 20.1376) / 22.1996;
    const Real tau_pa = 0.03118 + 0.21718 * exp(-pa_factor * pa_factor);
    *_new_pa = pa_infinity + (pa - pa_infinity) * exp(-(dt / tau_pa));

    // pi gate
    const Real pi = 1.0 / (1.0 + exp((V + 55.0) / 24.0));

    // intracellular Ca buffering
    const Real J_O_C = 200000.0 * Ca_i * (1.0 - O_C) - 476.0 * O_C;
    const Real J_O_TC = 78400.0 * Ca_i * (1.0 - O_TC) - 392.0 * O_TC;
    const Real J_O_TMgC = 200000.0 * Ca_i * (1.0 - O_TMgC - O_TMgMg) - 6.6 * O_TMgC;
    *_new_O_C = O_C + dt*(J_O_C);
    *_new_O_TC = O_TC + dt*(J_O_TC);
    *_new_O_TMgC = O_TMgC + dt*(J_O_TMgC);
    const Real J_O = 0.08 * J_O_TC + 0.16 * J_O_TMgC + 0.045 * J_O_C;
    const Real J_O_TMgMg = 2000.0 * Mg_i * (1.0 - O_TMgC - O_TMgMg) - 666.0 * O_TMgMg;
    *_new_O = O + dt*(J_O);
    *_new_O_TMgMg = O_TMgMg + dt*(J_O_TMgMg);

    // sarcolemmal calcium pump current
    const Real i_CaP = i_CaP_max * Ca_i / (Ca_i + k_CaP);

    // h1 gate
    const Real h_factor = 1.0 / (1.0 + exp((V + 35.1) / 3.2));
    const Real h_infinity = 1.0 / (1.0 + exp((V + 63.6) / 5.3));
    const Real tau_h1 = 0.03 * h_factor + 0.0003;
    *_new_h1 = h_infinity + (h1 - h_infinity) * exp(-(dt / tau_h1));

    // m gate
    const Real m_factor = (V + 25.57) / 28.8;
    const Real m_infinity = 1.0 / (1.0 + exp((V + 27.12) / -8.21));
    const Real tau_m = 4.2e-05 * exp(-m_factor * m_factor) + 2.4e-05;
    *_new_m = m_infinity + (m - m_infinity) * exp(-(dt / tau_m));

    // sodium potassium pump
    const Real pow_Na_i_15 = pow(Na_i, 1.5);
    const Real i_NaK = i_NaK_max * K_c / (K_c + K_NaK_K) * pow_Na_i_15 / (pow_Na_i_15 + pow_K_NaK_Na_15) * (V + 150.0) / (V + 200.0);

    // a_ur gate
    const Real a_ur_infinity = 1.0 / (1.0 + exp(-(V + 6.0) / 8.6));
    const Real tau_a_ur = 0.009 / (1.0 + exp((V + 5.0) / 12.0)) + 0.0005;
    *_new_a_ur = a_ur_infinity + (a_ur - a_ur_infinity) * exp(-(dt / tau_a_ur));

    // i_ur gate
    const Real i_ur_infinity = 1.0 / (1.0 + exp((V + 7.5) / 10.0));
    const Real tau_i_ur = 0.59 / (1.0 + exp((V + 60.0) / 10.0)) + 3.05;
    *_new_i_ur = i_ur_infinity + (i_ur - i_ur_infinity) * exp(-(dt / tau_i_ur));

    // f_L2 gate
    const Real tau_f_L2 = 1.3323 * exp(-f_L_factor * f_L_factor / 14.2 / 14.2) + 0.0626;
    *_new_f_L2 = f_L_infinity + (f_L2 - f_L_infinity) * exp(-(dt / tau_f_L2));

    // h2 gate
    const Real tau_h2 = 0.12 * h_factor + 0.003;
    *_new_h2 = h_infinity + (h2 - h_infinity) * exp(-(dt / tau_h2));

    // membrane
    const Real Q_tot = 0.05 * V;

    // sodium current
    const Real E_Na = R * T / F * log(Na_c / Na_i);
    const Real i_Na =
      P_Na * m * m * m * (0.9 * h1 + 0.1 * h2) * Na_c * F * F / (R * T) *
      (fabs(V) < 1e-3
        ? R * T * (exp((-E_Na * F) / (R * T)) - 1.0) / F
        : V * (exp((V - E_Na) * F / (R * T)) - 1.0)
            / (exp(V * F / (R * T)) - 1.0)
      );

    // Ca independent transient outward K current
    const Real E_K = R * T / F * log(K_c / K_i);
    const Real i_t = g_t * r * s * (V - E_K);

    // ultra rapid K current
    const Real i_Kur = g_Kur * a_ur * i_ur * (V - E_K);

    // inward rectifier
    const Real i_K1 = g_K1 * pow(K_c / 1.0, 0.4457) * (V - E_K) / (1.0 + exp(1.5 * (V - E_K + 3.6) * F / (R * T)));

    // delayed rectifier K currents
    const Real i_Kr = g_Kr * pa * pi * (V - E_K);
    const Real i_Ks = g_Ks * n * (V - E_K);

    // background currents
    const Real E_Ca = R * T / (2.0 * F) * log(Ca_c / Ca_i);
    const Real i_B_Ca = g_B_Ca * (V - E_Ca);
    const Real i_B_Na = g_B_Na * (V - E_Na);

    // Na/Ca ion exchanger current
    const Real i_NaCa = K_NaCa * (Na_i * Na_i * Na_i * Ca_c * exp(F * V * gamma_Na / (R * T)) - Na_c * Na_c * Na_c * Ca_i * exp((gamma_Na - 1.0) * V * F / (R * T))) / (1.0 + d_NaCa * (Na_c * Na_c * Na_c * Ca_i + Na_i * Na_i * Na_i * Ca_c));

    // ACh dependent K current
    const Real i_KACh = 10.0 / (1.0 + 9.13652 / pow(ACh, 0.477811)) * (0.0517 + 0.4516 / (1.0 + exp((V + 59.53) / 17.18))) * (V - E_K) * Cm;

    // intracellular ion concentrations
    *_new_K_i = K_i + dt*(-(i_t + i_Kur + i_K1 + i_Ks + i_Kr - 2.0 * i_NaK) / (Vol_i * F));
    *_new_Na_i = Na_i + dt*(-(i_Na + i_B_Na + 3.0 * i_NaCa + 3.0 * i_NaK + phi_Na_en) / (Vol_i * F));
    const Real i_di = (Ca_d - Ca_i) * 2.0 * Vol_d * F / tau_di;
    *_new_Ca_d = Ca_d + dt*(-(i_Ca_L + i_di) / (2.0 * Vol_d * F));

    // cleft space ion concentrations
    *_new_Ca_c = Ca_c + dt*((Ca_b - Ca_c) / tau_Ca + (i_Ca_L + i_B_Ca + i_CaP - 2.0 * i_NaCa) / (2.0 * Vol_c * F));
    *_new_K_c = K_c + dt*((K_b - K_c) / tau_K + (i_t + i_Kur + i_K1 + i_Ks + i_Kr - 2.0 * i_NaK) / (Vol_c * F));
    *_new_Na_c = Na_c + dt*((Na_b - Na_c) / tau_Na + (i_Na + i_B_Na + 3.0 * i_NaCa + 3.0 * i_NaK + phi_Na_en) / (Vol_c * F));

    // Ca handling by the SR
    const Real J_O_Calse = 480.0 * Ca_rel * (1.0 - O_Calse) - 400.0 * O_Calse;
    const Real i_rel_f2 = F2 / (F2 + 0.25);
    const Real i_rel_factor = i_rel_f2 * i_rel_f2;
    const Real i_tr = (Ca_up - Ca_rel) * 2.0 * Vol_rel * F / tau_tr;
    const Real i_up = I_up_max * (Ca_i / k_cyca - k_xcs * k_xcs * Ca_up / k_srca) / ((Ca_i + k_cyca) / k_cyca + k_xcs * (Ca_up + k_srca) / k_srca);
    const Real r_Ca_d_term = Ca_d / (Ca_d + k_rel_d);
    const Real r_Ca_i_term = Ca_i / (Ca_i + k_rel_i);
    *_new_O_Calse = O_Calse + dt*(J_O_Calse);
    const Real i_rel = alpha_rel * i_rel_factor * (Ca_rel - Ca_i);
    const Real r_Ca_d_factor = r_Ca_d_term * r_Ca_d_term * r_Ca_d_term * r_Ca_d_term;
    const Real r_Ca_i_factor = r_Ca_i_term * r_Ca_i_term * r_Ca_i_term * r_Ca_i_term;
    *_new_Ca_up = Ca_up + dt*((i_up - i_tr) / (2.0 * Vol_up * F));
    const Real r_act = 203.8 * (r_Ca_i_factor + r_Ca_d_factor);
    const Real r_inact = 33.96 + 339.6 * r_Ca_i_factor;
    *_new_Ca_rel = Ca_rel + dt*((i_tr - i_rel) / (2.0 * Vol_rel * F) - 31.0 * J_O_Calse);
    *_new_F1 = F1 + dt*(r_recov * (1.0 - F1 - F2) - r_act * F1);
    *_new_F2 = F2 + dt*(r_act * F1 - r_inact * F2);

    // remaining
    const Real I = (i_Na + i_Ca_L + i_t + i_Kur + i_K1 + i_Kr + i_Ks + i_B_Na + i_B_Ca + i_NaK + i_CaP + i_NaCa + i_KACh) / Cm;
    *_new_Ca_i = Ca_i + dt*((i_di + i_rel + 2.0 * i_NaCa - i_B_Ca - i_CaP - i_up) / (2.0 * Vol_i * F) - 1.0 * J_O);
    *_new_V = V + dt*(_diffuse_V - I * 1000.0);

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

