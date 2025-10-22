.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.h``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.

Ten Tusscher et al. 2006
========================

**Key:** ``tentusscher2006alternans``

This detailed human ventricular cell model was developed to investigate the
mechanisms of electrical instability, alternans, and spiral wave breakup in
cardiac tissue. It builds on their 2004 model by incorporating a more
comprehensive description of intracellular calcium dynamics, including
subspace calcium compartments and a Markov model of the ryanodine receptor
for calcium-induced calcium release (CICR). The model also includes both fast
and slow voltage-dependent inactivation gates for the L-type calcium current,
enabling more accurate simulation of calcium handling and its role in
arrhythmogenesis. It reproduces a wide range of experimentally observed APD
restitution slopes (see the parameter sets ``slope``, default ``slope[1.1]``)
and explores the interaction between sodium current recovery dynamics and
tissue-level instability. The model is suited for studying reentry,
alternans, and ventricular fibrillation mechanisms in human cardiac tissue.
The model also has different parameter sets for epicardial (parameter set
``epi``, default), endocardial (``endo``), and midmyocardial cells (``m``).

References
----------
1. https://doi.org/10.1152/ajpheart.00109.2006
2. https://doi.org/10.1152/ajpheart.00794.2003

Variables
---------
0. ``V = -85.23``
1. ``Ca_SR = 3.64``
2. ``Ca_i = 0.000126``
3. ``Ca_ss = 0.00036``
4. ``K_i = 136.89``
5. ``Na_i = 8.604``
6. ``Rbar = 0.9073``
7. ``Xr1 = 0.00621``
8. ``Xr2 = 0.4712``
9. ``Xs = 0.0095``
10. ``d = 3.373e-05``
11. ``f2 = 0.9755``
12. ``f = 0.7888``
13. ``fCass = 0.9953``
14. ``h = 0.7444``
15. ``j = 0.7045``
16. ``m = 0.00172``
17. ``r = 2.42e-08``
18. ``s = 0.999998``

Parameters
----------
- ``diffusivity_V = 1.0``
- ``Buf_c = 0.2``
- ``Buf_sr = 10.0``
- ``Buf_ss = 0.4``
- ``C_m = 185.0``
- ``Ca_o = 2.0``
- ``EC = 1.5``
- ``F = 96.485``
- ``K_buf_c = 0.001``
- ``K_buf_sr = 0.3``
- ``K_buf_ss = 0.00025``
- ``K_mCa = 1.38``
- ``K_mNa = 40.0``
- ``K_mNa_i = 87.5``
- ``K_mk = 1.0``
- ``K_o = 5.4``
- ``K_pCa = 0.0005``
- ``K_up = 0.00025``
- ``Na_o = 140.0``
- ``P_NaK = 2.724``
- ``R = 8.314``
- ``T = 310.0``
- ``V_c = 16404.0``
- ``V_leak = 0.00036``
- ``V_maxup = 0.006375``
- ``V_rel = 0.102``
- ``V_sr = 1094.0``
- ``V_ss = 54.68``
- ``V_xfer = 0.0038``
- ``alpha = 2.5``
- ``factor_f_tau = 1.0``
- ``factor_g_Kr = 1.0``
- ``factor_g_Ks = 1.0``
- ``factor_g_pCa = 1.0``
- ``factor_g_pK = 1.0``
- ``g_CaL = 0.0398``
- ``g_K1 = 5.405``
- ``g_Kr = 0.153``
- ``g_Ks = 0.392``
- ``g_Na = 14.838``
- ``g_bCa = 0.000592``
- ``g_bNa = 0.00029``
- ``g_pCa = 0.1238``
- ``g_pK = 0.0146``
- ``g_to = 0.294``
- ``gamma = 0.35``
- ``k1_prime = 0.15``
- ``k2_prime = 0.045``
- ``k3 = 0.06``
- ``k4 = 0.005``
- ``k_NaCa = 1000.0``
- ``k_sat = 0.1``
- ``max_sr = 2.5``
- ``min_sr = 1.0``
- ``p_KNa = 0.03``
- ``s_offset = 20.0``
- ``s_variant = 0.0``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    // i_CaL: gating variable d
    const Real d_alpha = 1.4 / (1. + exp((-35. - V) / 13.)) + 0.25;
    const Real d_beta = 1.4 / (1. + exp((V + 5.) / 5.));
    const Real d_inf = 1. / (1. + exp((-8. - V) / 7.5));
    const Real d_gamma = 1. / (1. + exp((50. - V) / 20.));
    const Real d_tau = 1. * d_alpha * d_beta + d_gamma;
    *_new_d = d_inf + (d - d_inf) * exp(-(dt / d_tau));

    // i_CaL: gating variable f2
    const Real f2_inf = 0.67 / (1. + exp((V + 35.) / 7.)) + 0.33;
    const Real f2_tau = 562. * exp(-pow(V + 27., 2.) / 240.) + 31. / (1. + exp((25. - V) / 10.)) + 80. / (1. + exp((V + 30.) / 10.));
    *_new_f2 = f2_inf + (f2 - f2_inf) * exp(-(dt / f2_tau));

    // i_CaL: gating variable fCass
    const Real fCass_inf = 0.6 / (1. + pow(Ca_ss / 0.05, 2.)) + 0.4;
    const Real fCass_tau = 80. / (1. + pow(Ca_ss / 0.05, 2.)) + 2.;
    *_new_fCass = fCass_inf + (fCass - fCass_inf) * exp(-(dt / fCass_tau));

    // i_CaL: gating variable f
    const Real f_inf = 1. / (1. + exp((V + 20.) / 7.));
    const Real f_tau = 1102.5 * exp(-pow(V + 27., 2.) / 225.) + 200. / (1. + exp((13. - V) / 10.)) + 180. / (1. + exp((V + 30.) / 10.)) + 20.;
    *_new_f = f_inf + (f - f_inf) * exp(-(dt / (factor_f_tau * f_tau)));

    // i_pCa
    const Real i_pCa = factor_g_pCa * g_pCa * Ca_i / (Ca_i + K_pCa);

    // i_Na: gating variable h
    const Real h_alpha = ((V < -40.) ? 0.057 * exp(-(V + 80.) / 6.8) : 0.);
    const Real h_beta = ((V < -40.) ? 2.7 * exp(0.079 * V) + 310000. * exp(0.3485 * V) : 0.77 / (0.13 * (1. + exp((V + 10.66) / -11.1))));
    const Real h_inf = 1. / (pow(1. + exp((V + 71.55) / 7.43), 2.));
    const Real h_tau = 1. / (h_alpha + h_beta);
    *_new_h = h_inf + (h - h_inf) * exp(-(dt / h_tau));

    // i_Na: gating variable j
    const Real j_alpha = ((V < -40.) ? (-25428. * exp(0.2444 * V) - 6.948e-06 * exp(-0.04391 * V)) * (V + 37.78) / 1. / (1. + exp(0.311 * (V + 79.23))) : 0.);
    const Real j_beta = ((V < -40.) ? 0.02424 * exp(-0.01052 * V) / (1. + exp(-0.1378 * (V + 40.14))) : 0.6 * exp(0.057 * V) / (1. + exp(-0.1 * (V + 32.))));
    const Real j_inf = 1. / (pow(1. + exp((V + 71.55) / 7.43), 2.));
    const Real j_tau = 1. / (j_alpha + j_beta);
    *_new_j = j_inf + (j - j_inf) * exp(-(dt / j_tau));

    // i_Na: gating variable m
    const Real m_alpha = 1. / (1. + exp((-60. - V) / 5.));
    const Real m_beta = 0.1 / (1. + exp((V + 35.) / 5.)) + 0.1 / (1. + exp((V - 50.) / 200.));
    const Real m_inf = 1. / (pow(1. + exp((-56.86 - V) / 9.03), 2.));
    const Real m_tau = 1. * m_alpha * m_beta;
    *_new_m = m_inf + (m - m_inf) * exp(-(dt / m_tau));

    // i_Kr: gating variable Xr1
    const Real Xr1_alpha = 450. / (1. + exp((-45. - V) / 10.));
    const Real Xr1_beta = 6. / (1. + exp((V + 30.) / 11.5));
    const Real Xr1_inf = 1. / (1. + exp((-26. - V) / 7.));
    const Real Xr1_tau = 1. * Xr1_alpha * Xr1_beta;
    *_new_Xr1 = Xr1_inf + (Xr1 - Xr1_inf) * exp(-(dt / Xr1_tau));

    // i_Kr: gating variable Xr2
    const Real Xr2_alpha = 3. / (1. + exp((-60. - V) / 20.));
    const Real Xr2_beta = 1.12 / (1. + exp((V - 60.) / 20.));
    const Real Xr2_inf = 1. / (1. + exp((V + 88.) / 24.));
    const Real Xr2_tau = 1. * Xr2_alpha * Xr2_beta;
    *_new_Xr2 = Xr2_inf + (Xr2 - Xr2_inf) * exp(-(dt / Xr2_tau));

    // i_Ks: gating variable Xs
    const Real Xs_alpha = 1400. / (sqrt(1. + exp((5. - V) / 6.)));
    const Real Xs_beta = 1. / (1. + exp((V - 35.) / 15.));
    const Real Xs_inf = 1. / (1. + exp((-5. - V) / 14.));
    const Real Xs_tau = 1. * Xs_alpha * Xs_beta + 80.;
    *_new_Xs = Xs_inf + (Xs - Xs_inf) * exp(-(dt / Xs_tau));

    // i_to: gating variable r
    const Real r_inf = 1. / (1. + exp((20. - V) / 6.));
    const Real r_tau = 9.5 * exp(-pow(V + 40., 2.) / 1800.) + 0.8;
    *_new_r = r_inf + (r - r_inf) * exp(-(dt / r_tau));

    // i_to: gating variable s
    const Real s_inf = 1. / (1. + exp((V + s_offset) / 5.));
    Real s_tau = 0;
    if(s_variant > 0.5) {
        s_tau = 1000. * exp(-pow(V + 67., 2.) / 1000.) + 8.;
    } else {
        s_tau = 85. * exp(-pow(V + 45., 2.) / 320.) + 5. / (1. + exp((V - 20.) / 5.)) + 3.;
    }
    *_new_s = s_inf + (s - s_inf) * exp(-(dt / s_tau));

    // dynCa
    const Real f_JCa_i_free = 1. / (1. + Buf_c * K_buf_c / (pow(Ca_i + K_buf_c, 2.)));
    const Real f_JCa_sr_free = 1. / (1. + Buf_sr * K_buf_sr / (pow(Ca_SR + K_buf_sr, 2.)));
    const Real f_JCa_ss_free = 1. / (1. + Buf_ss * K_buf_ss / (pow(Ca_ss + K_buf_ss, 2.)));
    const Real i_leak = V_leak * (Ca_SR - Ca_i);
    const Real i_up = V_maxup / (1. + pow(K_up, 2.) / (pow(Ca_i, 2.)));
    const Real i_xfer = V_xfer * (Ca_ss - Ca_i);
    const Real kcasr = max_sr - (max_sr - min_sr) / (1. + pow(EC / (Ca_SR), 2.));
    const Real k1 = k1_prime / (kcasr);
    const Real k2 = k2_prime * kcasr;
    const Real O = k1 * pow(Ca_ss, 2.) * Rbar / (k3 + k1 * pow(Ca_ss, 2.));
    *_new_Rbar = Rbar + dt*(-k2 * Ca_ss * Rbar + k4 * (1. - Rbar));
    const Real i_rel = V_rel * O * (Ca_SR - Ca_ss);
    const Real ddt_Ca_sr_total = i_up - (i_rel + i_leak);
    *_new_Ca_SR = Ca_SR + dt*(ddt_Ca_sr_total * f_JCa_sr_free);

    // *remaining*
    const Real E_Ca = 0.5 * R * T / F * log(Ca_o / (Ca_i));
    const Real E_K = R * T / F * log(K_o / (K_i));
    const Real E_Ks = R * T / F * log((K_o + p_KNa * Na_o) / (K_i + p_KNa * Na_i));
    const Real E_Na = R * T / F * log(Na_o / (Na_i));
    const Real i_CaL = g_CaL * d * f * f2 * fCass * 4. * (V - 15.) * pow(F, 2.) / (R * T) * (0.25 * Ca_ss * exp(2. * (V - 15.) * F / (R * T)) - Ca_o) / ((fabs(exp(2. * (V - 15.) * F / (R * T)) - 1.) < VERY_SMALL_NUMBER) ? ((exp(2. * (V - 15.) * F / (R * T)) - 1. < 0.) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : exp(2. * (V - 15.) * F / (R * T)) - 1.);
    const Real i_NaK = P_NaK * K_o / (K_o + K_mk) * Na_i / (Na_i + K_mNa) / (1. + 0.1245 * exp(-0.1 * V * F / (R * T)) + 0.0353 * exp(-V * F / (R * T)));
    const Real i_NaCa = k_NaCa * (exp(gamma * V * F / (R * T)) * pow(Na_i, 3.) * Ca_o - exp((gamma - 1.) * V * F / (R * T)) * pow(Na_o, 3.) * Ca_i * alpha) / ((pow(K_mNa_i, 3.) + pow(Na_o, 3.)) * (K_mCa + Ca_o) * (1. + k_sat * exp((gamma - 1.) * V * F / (R * T))));
    const Real i_K1_alpha_K1 = 0.1 / (1. + exp(0.06 * (V - E_K - 200.)));
    const Real i_K1_beta_K1 = (3. * exp(0.0002 * (V - E_K + 100.)) + exp(0.1 * (V - E_K - 10.))) / (1. + exp(-0.5 * (V - E_K)));
    const Real i_Kr = factor_g_Kr * g_Kr * sqrt(K_o / 5.4) * Xr1 * Xr2 * (V - E_K);
    const Real i_Ks = factor_g_Ks * g_Ks * pow(Xs, 2.) * (V - E_Ks);
    const Real i_Na = g_Na * pow(m, 3.) * h * j * (V - E_Na);
    const Real i_bNa = g_bNa * (V - E_Na);
    const Real i_bCa = g_bCa * (V - E_Ca);
    const Real i_to = g_to * r * s * (V - E_K);
    const Real i_pK = factor_g_pK * g_pK * (V - E_K) / (1. + exp((25. - V) / 5.98));
    const Real ddt_Ca_ss_total = -i_CaL * C_m / (2. * V_ss * F) + i_rel * V_sr / V_ss - i_xfer * V_c / V_ss;
    const Real i_K1_xK1_inf = i_K1_alpha_K1 / (i_K1_alpha_K1 + i_K1_beta_K1);
    const Real ddt_Ca_i_total = -(i_bCa + i_pCa - 2. * i_NaCa) * C_m / (2. * V_c * F) + (i_leak - i_up) * V_sr / V_c + i_xfer;
    *_new_Ca_ss = Ca_ss + dt*(ddt_Ca_ss_total * f_JCa_ss_free);
    *_new_Na_i = Na_i + dt*(-(i_Na + i_bNa + 3. * i_NaK + 3. * i_NaCa) / (V_c * F) * C_m);
    const Real i_K1 = g_K1 * i_K1_xK1_inf * sqrt(K_o / 5.4) * (V - E_K);
    *_new_Ca_i = Ca_i + dt*(ddt_Ca_i_total * f_JCa_i_free);
    *_new_V = V + dt*(-(i_K1 + i_to + i_Kr + i_Ks + i_CaL + i_NaK + i_Na + i_bNa + i_NaCa + i_bCa + i_pK + i_pCa) + _diffuse_V);
    *_new_K_i = K_i + dt*(-(i_K1 + i_to + i_Kr + i_Ks + i_pK - 2. * i_NaK) / (V_c * F) * C_m);


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
    initial values:
      epi:
        V: -85.23
        Ca_SR: 3.64
        Ca_i: 0.000126
        Ca_ss: 0.00036
        K_i: 136.89
        Na_i: 8.604
        Rbar: 0.9073
        Xr1: 0.00621
        Xr2: 0.4712
        Xs: 0.0095
        d: 3.373e-05
        f2: 0.9755
        f: 0.7888
        fCass: 0.9953
        h: 0.7444
        j: 0.7045
        m: 0.00172
        r: 2.42e-08
        s: 0.999998
      endo:
        V: -86.709
        Ca_SR: 3.715
        Ca_i: 0.00013
        Ca_ss: 0.00036
        K_i: 138.4
        Na_i: 10.355
        Rbar: 0.9068
        Xr1: 0.00448
        Xr2: 0.476
        Xs: 0.0087
        d: 3.164e-05
        f2: 0.9778
        f: 0.8009
        fCass: 0.9953
        h: 0.7573
        j: 0.7225
        m: 0.00155
        r: 2.235e-08
        s: 0.3212
      m:
        V: -85.423
        Ca_SR: 4.272
        Ca_i: 0.000153
        Ca_ss: 0.00042
        K_i: 138.52
        Na_i: 10.132
        Rbar: 0.8978
        Xr1: 0.0165
        Xr2: 0.473
        Xs: 0.0174
        d: 3.288e-05
        f2: 0.9526
        f: 0.7026
        fCass: 0.9942
        h: 0.749
        j: 0.6788
        m: 0.00165
        r: 2.347e-08
        s: 0.999998
    parameter sets:
      slope:
        0.7:
          factor_g_Kr: 0.8758169934640524
          factor_g_Ks: 0.6887755102040817
          factor_g_pCa: 0.5
          factor_g_pK: 5.0
          factor_f_tau: 0.6
        1.1:
          factor_g_Kr: 1.0
          factor_g_Ks: 1.0
          factor_g_pCa: 1.0
          factor_g_pK: 1.0
          factor_f_tau: 1.0
        1.4:
          factor_g_Kr: 1.1241830065359477
          factor_g_Ks: 1.125
          factor_g_pCa: 3.0
          factor_g_pK: 0.5
          factor_f_tau: 1.5
        1.8:
          factor_g_Kr: 1.1241830065359477
          factor_g_Ks: 1.125
          factor_g_pCa: 7.0
          factor_g_pK: 0.15
          factor_f_tau: 2.0
      epi:
        g_Ks: 0.392
        g_to: 0.294
        s_offset: 20.0
        s_variant: 0.0
      endo:
        g_Ks: 0.392
        g_to: 0.073
        s_offset: 28.0
        s_variant: 1.0
      m:
        g_Ks: 0.098
        g_to: 0.294
        s_offset: 20.0
        s_variant: 0.0

