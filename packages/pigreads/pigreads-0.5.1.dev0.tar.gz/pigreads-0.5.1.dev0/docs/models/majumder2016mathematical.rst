.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.h``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.

Majumder et al. 2016
====================

**Key:** ``majumder2016mathematical``

This model was designed to closely correspond to monolayers of neonatal rat
atrial cardiomyocytes (NRAMs) observed via optical mapping.
It is based on several existing cardiac cell models; key changes include
incorporation of a constitutively active IKACh, fitting to neonatal
rat atrial patch-clamp data, and inclusion of myofibroblasts and cellular
heterogeneity. The model reproduces action potential dynamics, restitution
curves, and spiral wave behavior, supporting studies of atrial
arrhythmogenesis.

The voltage- and light-sensitive Channelrhodopsin-2 ion channel as proposed by
Williams et al. (2013) has been added to this model.

References
----------
1. https://doi.org/10.1371/journal.pcbi.1004946
2. https://doi.org/10.1371/journal.pcbi.1003220

Variables
---------
0. ``V = -70.0``
1. ``m = 0.001729``
2. ``h = 0.624946``
3. ``j = 0.624946``
4. ``d = 0.000109``
5. ``f = 0.999929``
6. ``fCa = 1.001951``
7. ``r = 0.003223``
8. ``s = 0.999969``
9. ``s_slow = 0.999969``
10. ``y = 0.562306``
11. ``b = 0.000708``
12. ``g = 0.914717``
13. ``ua = 0.000554``
14. ``ui = 1.0``
15. ``P_o1 = 0.002247``
16. ``Ca_JSR = 790.502388``
17. ``Ca_NSR = 794.054383``
18. ``Ca_i = 0.137822``
19. ``Xr = 0.025742210977``
20. ``Xs1 = 0.012668791315``
21. ``Xs2 = 0.028399873909``
22. ``O1 = 0.0``
23. ``O2 = 0.0``
24. ``C1 = 1.0``
25. ``C2 = 0.0``
26. ``p = 0.1``

Parameters
----------
- ``diffusivity_V = 1.0``
- ``light = 0.0``
- ``F = 96.5``
- ``R = 8.314``
- ``T = 310.0``
- ``C_m = 1.0``
- ``Q10Na = 1.8``
- ``Q10Ca = 1.8``
- ``Q10K = 1.8``
- ``r_SR = 6.0``
- ``r_SL = 10.5``
- ``G_ChR2 = 2.0``
- ``Ogamma = 0.1``
- ``Ee = 3.0``
- ``w_loss = 0.76``
- ``tau_ChR2 = 1.3``
- ``eps1 = 0.8535``
- ``eps2 = 0.14``
- ``lambda = 470``
- ``G_d1 = 0.1``
- ``G_d2 = 0.05``
- ``G_r = 0.004``
- ``phi0 = 0.024``
- ``EChR2 = 0.0``
- ``Ca_o = 1796.0``
- ``Na_o = 154578.0``
- ``K_o = 5400.0``
- ``Na_i = 13818.5982638``
- ``K_i = 130953.3914836``
- ``k_NCX = 1.134e-16``
- ``d_NCX = 1e-16``
- ``gamma = 0.5``
- ``INaK_max = 3.1993``
- ``K_mNai = 18600.0``
- ``n_NaK = 3.2``
- ``K_mKo = 1500.0``
- ``k_f = 0.023761``
- ``k_b = 0.036778``
- ``IpCa_max = 0.2``
- ``K_mpCa = 0.5``
- ``P_NaK = 0.01833``
- ``ACh = 1.0``
- ``k_RyR = 0.005``
- ``k_open = 1.0``
- ``k_close = 0.16``
- ``Vmaxf = 0.9996``
- ``Vmaxr = 0.9996``
- ``K_mf = 0.5``
- ``K_mr = 3500.0``
- ``Hf = 2.0``
- ``Hr = 2.0``
- ``k_leak = 5e-6``
- ``tau_tr = 200``
- ``K_mup = 0.5``
- ``delta_r = 0.1``
- ``TRPN_tot = 35.0``
- ``K_mTRPN = 0.5``
- ``CMDN_tot = 50.0``
- ``K_mCMDN = 2.38``
- ``CSQN_tot = 24750.0``
- ``K_mCSQN = 800.0``
- ``D_Ca = 7.0``
- ``N = 4``
- ``nu1 = 0.01``
- ``k_a_plus = 1``
- ``k_a_minus = 0.16``
- ``G_CaL = 8e-05``
- ``G_CaT = 0.0054``
- ``G_Cab = 0.0008``
- ``G_Nab = 0.0039``
- ``G_Kb = 0.001``
- ``G_Kur = 0.02``
- ``G_f = 0.021``
- ``G_to = 0.007``
- ``G_Na = 150.0``
- ``G_Kv = 0.25``
- ``G_bNaf = 0.0095``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    // derived parameters
    const Real RT_F = (R * T) / F;
    const Real F_RT = 1.0 / RT_F;
    const Real A_cap = 4.0 * M_PI * r_SL * r_SL * 1e-8; // cm^2
    const Real V_SR = 0.043 * 1.5 * 1.4; // pl
    const Real V_NSR = 0.9 * V_SR; // pl
    const Real V_JSR = V_SR - V_NSR; // pl
    const Real V_myo = (4.0 * M_PI * (r_SL * r_SL * r_SL - r_SR * r_SR * r_SR)) / 3000.0; // pl
    const Real S0 = 0.5 * (1 + tanh(120 * (Ee - 0.1)));
    const Real e12 = 0.011 + 0.005 * log10(Ee / phi0); // Trayanova
    const Real e21 = 0.008 + 0.004 * log10(Ee / phi0); // Trayanova
    const Real tau_fCa = 10.0 / Q10Ca;

    // reversal potentials
    const Real ECa = 0.5 * RT_F * log(Ca_o / Ca_i);
    const Real EK = RT_F * log(K_o / K_i);
    const Real ENa = RT_F * log(Na_o / Na_i);
    const Real EKs = RT_F * log((K_o + P_NaK * Na_o) / (K_i + P_NaK * Na_i));

    // gating variables for fast sodium current
    const Real alpha_m = 0.32 * safe_divide(V + 47.13, 1.0 - exp(-0.1 * (V + 47.13)));
    const Real beta_m = 0.056 * exp(-V / 11.0);

    Real alpha_h = 0.0;
    Real beta_h = 1.0 / (0.13 * (1 + exp(-(V + 10.66) / 11.1)));
    Real alpha_j = 0.0;
    Real beta_j = (0.3 * exp(-2.535e-7 * V)) / (1.0 + exp(-0.1 * (V + 32.0)));
    if (V < -40.0) {
      alpha_h = 0.135 * exp(-(V + 70.0) / 6.8);
      beta_h = 3.56 * exp(0.079 * V) + 3.1e5 * exp(0.35 * V);
      alpha_j = (2.0 * (-1.2714e5 * exp(0.2444 * V) - 3.474e-5 * exp(-0.04391 * V)) * (V + 37.78)) / (1.0 + exp(0.311 * (V + 79.23)));
      beta_j = (0.1212 * exp(-0.01052 * V)) / (1 + exp(-0.1378 * (V + 40.14)));
    }

    const Real m_inf = 1.0 / (1.0 + exp((37.0 + V) / -6.8));
    const Real h_inf = 1.0 / (1.0 + exp((78.0 + V) / 7.8));
    Real tau_m = 1.0 / (alpha_m + beta_m);
    Real tau_h = V < -40.0 ? 0.06 / (alpha_h + beta_h) + 1.5 : 0.75 / (alpha_h + beta_h) + 0.15;
    Real tau_j = 1.0 / (alpha_j + beta_j);
    const Real j_inf = h_inf;

    // gating variables for hyperpolarization activated current
    const Real y_inf = 1.0 / (1.0 + exp((V + 78.65) / 6.33));
    const Real tau_y = 1000.0 / (0.11885 * exp((V + 75.0) / 28.37) + 0.56236 * exp((V + 75.0) / -14.19));

    // gating variables for ultra-rapid K+ current
    const Real ua_inf = 1.0 / (1.0 + exp(-(V + 12.5) / 25.0));
    Real tau_ua = 0.493 * exp(-0.0629 * V) + 2.058;
    const Real ui_inf = 1.0 / (1.0 + exp((V - 100.0) / 5.7));
    Real tau_ui = 1200.0 - 170.0 / (1 + exp((V + 45.2) / 5.7));

    // gating variables for slow delayed rectifier K+ current
    const Real Xs1_inf = 1.0 / (1.0 + exp(-(V - 10.0) / 20.0));
    const Real Xs2_inf = Xs1_inf;
    Real tau_Xs1 = safe_divide(1.0, safe_divide(7.19e-5 * (V + 30.0), 1.0 - exp(-0.148 * (V + 30.0))) + safe_divide(1.31e-4 * (V + 30.0), exp(0.0687 * (V + 30.0)) - 1.0));
    Real tau_Xs2 = 4.0 * tau_Xs1;

    // gating variables for rapid delayed rectifier K+ current
    const Real Xr_inf = 1.0 / (1.0 + exp(-(V + 12.5) / 10.0));
    Real tau_Xr = safe_divide(1.0, safe_divide(0.00138 * (V + 14.2), 1.0 - exp(-0.123 * (V + 14.2))) + safe_divide(0.00061 * (V + 38.9), exp(0.145 * (V + 38.9)) - 1.0));
    const Real Rr = 1.0 / (1.0 + exp((V + 9.0) / 22.4));

    // gating variables for transient-outward K+ current
    const Real r_inf = 1.0 / (1.0 + exp(-(V + 3.0) / 12.0));
    const Real s_inf = 1.0 / (1.0 + exp((V + 31.97156) / 4.64291));
    const Real sslow_inf = s_inf;
    const Real tau_r = 1000.0 / (45.16 * exp(0.03577 * (V + 50.0)) + 98.9 * exp(-0.1 * (V + 38.0)));
    const Real tau_s = 1000.0 * (0.35 * exp(-1.0 * pow((V + 70.0) / 15.0, 2)) + 0.035) - 26.9;
    const Real tau_sslow = 1000.0 * (3.7 * exp(-1.0 * pow((V + 70.0) / 30.0, 2)) + 0.035) + 37.4;

    // gating variables for L-type Ca2+ current
    const Real d_inf = 1.0 / (1.0 + exp((-1.8 - V) / 8.6));
    const Real a_d = 0.25 + 1.4 / (1.0 + exp((-35.0 - V) / 13.0));
    const Real b_d = 1.4 / (1.0 + exp((V + 5.0) / 5.0));
    const Real c_d = 1.0 / (1.0 + exp((50.0 - V) / 20.0));
    Real tau_d = a_d * b_d + c_d + 10.0;
    const Real f_inf = 1.0 / (1.0 + exp((22.0 + V) / 6.1));
    Real tau_f = 562.5 * exp((-1.0 * pow(V + 27.0, 2)) / 1000.0) + 10.0 / (1.0 + exp((25.0 - V) / 1.0)) + 10.0;
    const Real a_fCa = 1.0 / (1.0 + pow(Ca_i / 0.325, 8));
    const Real b_fCa = 0.1 / (1.0 + exp((Ca_i - 0.5) / 0.1));
    const Real c_fCa = 0.2 / (1.0 + exp((Ca_i - 0.75) / 0.8));
    const Real fCa_inf = (a_fCa + b_fCa + c_fCa + 0.23) / 1.46;
    const Real k = (fCa_inf > fCa && V > -60.0) ? 0.0 : 1.0;

    // gating variables for T-type Ca2+ current
    const Real b_inf = 1.0 / (1.0 + exp(-(V + 36.0) / 6.1));
    const Real tau_b = 0.6 + 5.4 / (1.0 + exp(0.03 * (V + 100.0)));
    const Real g_inf = 1.0 / (1.0 + exp((V + 66.0) / 6.0));
    const Real tau_g = 1.0 + 40.0 / (1.0 + exp(0.08 * (V + 65.0)));

    // gating variables for Na+/K+ ATPase
    const Real sigma = (exp(Na_o / 67300.0) - 1.0) / 7.0;
    const Real fNaK = 1.0 / (1.0 + 0.1245 * exp(-0.1 * V * F_RT) + 0.0365 * sigma * exp(-V * F_RT));

    // Q10 compensation
    tau_m = tau_m / Q10Na;
    tau_h = tau_h / Q10Na;
    tau_j = tau_j / Q10Na;
    tau_d = tau_d / Q10Ca;
    tau_f = tau_f / Q10Ca;
    tau_ua = tau_ua / Q10K;
    tau_ui = tau_ui / Q10K;
    tau_Xs1 = tau_Xs1 / Q10K;
    tau_Xs2 = tau_Xs2 / Q10K;
    tau_Xr = tau_Xr / Q10K;

    // photocurrent parameters
    Real k1 = 0.0;
    Real k2 = 0.0;
    if (light > 0.5) { // if Lit == 1 && light_on <= t && t <= light_off
      const Real k0 = Ee * lambda * p;
      k1 = 3.89196e-05 * k0;
      k2 = 6.384e-06 * k0;
    }

    // fast Na+ current
    const Real INa = G_Na * m * m * m * h * j * (V - ENa);

    // hyperpolarization-activated current
    const Real IfNa = G_f * y * (0.2 * (V - ENa));
    const Real IfK = G_f * y * (0.8 * (V - EK));
    const Real If = IfNa+IfK;

    // ultra-rapid outward K+ current
    const Real IKur = G_Kur * ua * ui * (V - EK);

    // slow delayed rectifier K+ current
    const Real G_Ks = 0.0866 * (1.0 + 0.6 / (1.0 + pow(0.000038 / Ca_i, 1.4)));
    const Real IKs = G_Ks * Xs1 * Xs2 * (V - EKs);

    // rapid delayed rectifier K+ current
    const Real G_Kr = 0.0005228 * sqrt(K_o / 5.4);
    const Real IKr = G_Kr * Xr * Rr * (V - EK);

    // sustained outward K+ current
    const Real IKsus = 0.001 * (IKur + IKs + IKr);

    // time-independent K+ current
    const Real IK1 = 0.8 * ((0.0515 * K_o / (K_o + 210.0) * (V - EK - 10)) / (0.5 + exp(0.025 * (V - EK - 10))));

    // transient outward K+ current
    const Real Ito = 0.01 * G_to * r * (0.706 * s + 0.294 * s_slow) * (V - EK);

    // L-type Ca2+ current
    const Real ICaL = safe_divide(0.8 * 4.0 * G_CaL * d * f * fCa * V * F * F_RT * (Ca_i * exp(2.0 * V * F_RT) - 0.341 * Ca_o), exp(2.0 * V * F_RT) - 1.0);

    // T-type Ca2+ current
    const Real ICaT = G_CaT * b * g * (V - ECa + 106.5);

    // Na+/Ca2+ exchanger current
    const Real INCX = (0.6 * k_NCX * (Na_i * Na_i * Na_i * Ca_o * exp(0.03743 * gamma * V) - Na_o * Na_o * Na_o * Ca_i * exp(0.03743 * (gamma - 1) * V))) / (1.0 + d_NCX * (Na_o * Na_o * Na_o * Ca_i + Na_i * Na_i * Na_i * Ca_o));

    // background Ca2+ and Na+ currents
    const Real ICab = G_Cab * (V - ECa);
    const Real INab = 0.01 * G_Nab * (V - ENa);
    const Real IKb = 0.001 * G_Kb * (V - EK);

    // Na+/K+ ATPase
    const Real INaK = 1.2 * INaK_max * fNaK / ((1.0 + pow(K_mNai / Na_i, n_NaK)) * (1.0 + K_mKo / K_o));

    // constitutively active KACh current
    const Real IKACh = 5.5 / (1.0 + 9.13652 / pow(ACh, 0.477811)) * (0.0517 + 0.4516 / (1.0 + exp((V + 105.0) / 17.18))) * (V - EK);

    // photocurrent (if Lit == 1)
    const Real IChR2 = light > 0.25 ? G_ChR2 * (V - EChR2) * (O1 + Ogamma * O2) : 0.0;

    // calcium fluxes
    const Real J_rel = nu1 * P_o1 * (Ca_JSR - Ca_i);
    const Real J_leak = k_leak * (Ca_NSR - Ca_i);
    const Real J_tr = (Ca_NSR - Ca_JSR) / tau_tr;

    // Ca2+ buffering
    const Real beta_SR = 1.0 / (1.0 + CSQN_tot * K_mCSQN / pow(Ca_JSR + K_mCSQN, 2));

    // ryanodine receptor gating
    const Real K_mRyR = 3.51 / (1.0 + exp((Ca_JSR - 530.0) / 200.0)) + 0.25;
    const Real P_C1 = 1 - P_o1;

    // SERCA
    const Real s1 = pow(Ca_i / K_mf, Hf);
    const Real s2 = pow(Ca_NSR / K_mr, Hr);
    const Real J_up = (Vmaxf * s1 - Vmaxr * s2) / (1.0 + s1 + s2);
    const Real J_CaSR = J_rel - J_up + J_leak;
    const Real J_CaSL = (2.0 * INCX - ICaL - ICaT - ICab) * A_cap * C_m / (2.0e-6 * F);

    // total ion current
    const Real I_ion = ICaL + ICaT + INCX + ICab + INab + INaK + INa + If + IK1 + Ito + IKsus + IKb + IKACh + IChR2;

    // time evolution of variables
    *_new_V = V + dt * (_diffuse_V - I_ion / C_m);
    *_new_m = m_inf + (m - m_inf) * exp(-dt / tau_m);
    *_new_h = h_inf + (h - h_inf) * exp(-dt / tau_h);
    *_new_j = j_inf + (j - j_inf) * exp(-dt / tau_j);
    *_new_d = d_inf + (d - d_inf) * exp(-dt / tau_d);
    *_new_f = f_inf + (f - f_inf) * exp(-dt / tau_f);
    *_new_fCa = (dt * k * (fCa_inf - fCa)) / tau_fCa + fCa;
    *_new_b = b_inf + (b - b_inf) * exp(-dt / tau_b);
    *_new_g = g_inf + (g - g_inf) * exp(-dt / tau_g);
    *_new_y = y_inf + (y - y_inf) * exp(-dt / tau_y);
    *_new_r = r_inf + (r - r_inf) * exp(-dt / tau_r);
    *_new_s = s_inf + (s - s_inf) * exp(-dt / tau_s);
    *_new_s_slow = sslow_inf + (s_slow - sslow_inf) * exp(-dt / tau_sslow);
    *_new_ua = ua_inf + (ua - ua_inf) * exp(-dt / tau_ua);
    *_new_ui = ui_inf + (ui - ui_inf) * exp(-dt / tau_ui);
    *_new_Xr = Xr_inf + (Xr - Xr_inf) * exp(-dt / tau_Xr);
    *_new_Xs1 = Xs1_inf + (Xs1 - Xs1_inf) * exp(-dt / tau_Xs1);
    *_new_Xs2 = Xs2_inf + (Xs2 - Xs2_inf) * exp(-dt / tau_Xs2);
    *_new_P_o1 = P_o1 + dt * (k_a_plus * pow(Ca_i, N) / (pow(Ca_i, N) + pow(K_mRyR, N)) * P_C1 - k_a_minus * P_o1);

    // calcium equations
    *_new_Ca_NSR = Ca_NSR + dt * (J_up - J_leak - J_tr) / V_NSR;
    *_new_Ca_JSR = Ca_JSR + dt * beta_SR * (-J_rel + J_tr) / V_JSR;

    // Channelrhodopsin
    *_new_O1 = (k1 * C1 - (G_d1 + e12) * O1 + e21 * O2) * dt + O1;
    *_new_O2 = (k2 * C2 - (G_d2 + e21) * O2 + e12 * O1) * dt + O2;
    *_new_C1 = (G_r * C2 + G_d1 * O1 - k1 * C1) * dt + C1;
    *_new_C2 = (G_d2 * O2 - (k2 + G_r) * C2) * dt + C2;
    *_new_p = p + dt * ((S0 - p) / tau_ChR2);

    // for spherical core structure
    const Real beta_Cai = 1.0 / (1.0 + TRPN_tot * K_mTRPN / pow(Ca_i + K_mTRPN, 2.0) + CMDN_tot * K_mCMDN / pow(Ca_i + K_mCMDN, 2.0));
    const Real dCai_dt = beta_Cai * (J_CaSR + J_CaSL) / V_myo;
    *_new_Ca_i = Ca_i + dt * dCai_dt;


.. raw:: html

    </details>

Additional metadata
-------------------

.. code-block:: yaml

    keywords:
    - excitable media
    - electrophysiology
    - heart
    - rat
    - atria

