.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.h``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.

Paci et al. 2013
================

**Key:** ``paci2013computational``

This model comprises two electrophysiological models of human induced
pluripotent stem cell-derived cardiomyocytes (hiPSC-CMs), distinguishing
between ventricular-like and atrial-like phenotypes.
Based on experimental data from Ma et al. (2011), the models reproduce
spontaneous action potentials and responses to current blockers. They were
developed to investigate the immature electrophysiological characteristics of
hiPSC-CMs and the ionic mechanisms underlying their spontaneous activity and
long AP durations. The model uses a Hodgkin–Huxley framework and was
constructed to support drug testing and cardiac maturation studies.
The default parameters are based on the ventricular-like formulation, with an
increased IK1 to disable spontaneous activity, as suggested by the authors.

References
----------
1. https://doi.org/10.1007/s10439-013-0833-3

Variables
---------
0. ``Vm = -0.0743340057623841``
1. ``m = 0.102953468725004``
2. ``h = 0.786926637881461``
3. ``j = 0.253943221774722``
4. ``d = 8.96088425225182e-05``
5. ``f1 = 0.970411811263976``
6. ``f2 = 0.999965815466749``
7. ``fCa = 0.998925296531804``
8. ``Xr1 = 0.00778547011240132``
9. ``Xr2 = 0.432162576531617``
10. ``Xs = 0.0322944866983666``
11. ``Xf = 0.100615100568753``
12. ``q = 0.839295925773219``
13. ``r = 0.00573289893326379``
14. ``Nai = 10.9248496211574``
15. ``Cai = 1.80773974140477e-05``
16. ``Ca_SR = 0.2734234751931``
17. ``g = 0.999999981028517``

Parameters
----------
- ``diffusivity_Vm = 1.0``
- ``calcium_dynamics_Buf_C = 0.25``
- ``calcium_dynamics_Buf_SR = 10.0``
- ``calcium_dynamics_Kbuf_C = 0.001``
- ``calcium_dynamics_Kbuf_SR = 0.3``
- ``calcium_dynamics_Kup = 0.00025``
- ``calcium_dynamics_V_leak = 0.00044444``
- ``calcium_dynamics_VmaxUp = 0.56064``
- ``calcium_dynamics_a_rel = 16.464``
- ``calcium_dynamics_b_rel = 0.25``
- ``calcium_dynamics_c_rel = 8.232``
- ``calcium_dynamics_g_factor = 0.0411``
- ``calcium_dynamics_tau_g = 0.002``
- ``electric_potentials_E_K = -0.08880285397707481``
- ``electric_potentials_PkNa = 0.03``
- ``i_CaL_d_gate_offset_d = 9.1``
- ``i_CaL_f1_gate_offset_f1 = 26.0``
- ``i_CaL_f2_gate_constf2 = 1.0``
- ``i_CaL_f2_gate_offset_f2 = 35.0``
- ``i_CaL_fCa_gate_tau_fCa = 0.002``
- ``i_CaL_g_CaL = 8.635702e-05``
- ``i_CaL_nifed_coeff = 1.0``
- ``i_K1_g_K1 = 50.0``
- ``i_Kr_E4031_coeff = 1.0``
- ``i_Kr_Xr1_gate_L0 = 0.025``
- ``i_Kr_Xr1_gate_Q = 2.3``
- ``i_Kr_Xr1_gate_V_half = -20.69505995297709``
- ``i_Kr_g_Kr = 29.8667``
- ``i_Ks_Chromanol_coeff = 1.0``
- ``i_Ks_g_Ks = 2.041``
- ``i_NaCa_KmCa = 1.38``
- ``i_NaCa_KmNai = 87.5``
- ``i_NaCa_Ksat = 0.1``
- ``i_NaCa_alpha = 2.8571432``
- ``i_NaCa_gamma = 0.35``
- ``i_NaCa_kNaCa = 4900.0``
- ``i_NaK_Km_K = 1.0``
- ``i_NaK_Km_Na = 40.0``
- ``i_NaK_PNaK = 1.841424``
- ``i_Na_TTX_coeff = 1.0``
- ``i_Na_g_Na = 3671.2302``
- ``i_PCa_KPCa = 0.0005``
- ``i_PCa_g_PCa = 0.4125``
- ``i_b_Ca_g_b_Ca = 0.69264``
- ``i_b_Na_g_b_Na = 0.9``
- ``i_f_E_f = -0.017``
- ``i_f_g_f = 30.10312``
- ``i_to_g_to = 29.9038``
- ``model_parameters_Cao = 1.8``
- ``model_parameters_Cm = 9.87109e-11``
- ``model_parameters_F = 96485.3415``
- ``model_parameters_Ki = 150.0``
- ``model_parameters_Ko = 5.4``
- ``model_parameters_Nao = 151.0``
- ``model_parameters_R = 8.314472``
- ``model_parameters_T = 310.0``
- ``model_parameters_V_SR = 583.73``
- ``model_parameters_Vc = 8800.0``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    // i_CaL_d_gate
    const Real i_CaL_d_gate_alpha_d = 0.25 + 1.4 / (1.0 + exp((-Vm * 1000.0 - 35.0) / 13.0));
    const Real i_CaL_d_gate_beta_d = 1.4 / (1.0 + exp((Vm * 1000.0 + 5.0) / 5.0));
    const Real i_CaL_d_gate_d_infinity = 1.0 / (1.0 + exp(-(Vm * 1000.0 + i_CaL_d_gate_offset_d) / 7.0));
    const Real i_CaL_d_gate_gamma_d = 1.0 / (1.0 + exp((-Vm * 1000.0 + 50.0) / 20.0));
    const Real i_CaL_d_gate_tau_d = (i_CaL_d_gate_alpha_d * i_CaL_d_gate_beta_d + i_CaL_d_gate_gamma_d) * 1.0 / 1000.0;
    *_new_d = i_CaL_d_gate_d_infinity + (d - i_CaL_d_gate_d_infinity) * exp(-(dt / i_CaL_d_gate_tau_d));

    // i_CaL_f1_gate
    const Real i_CaL_f1_gate_f1_inf = 1.0 / (1.0 + exp((Vm * 1000.0 + i_CaL_f1_gate_offset_f1) / 3.0));
    const Real i_CaL_f1_gate_constf1 = ((i_CaL_f1_gate_f1_inf - f1 > 0.0) ? 1.0 + 1433.0 * (Cai - 50.0 * 1e-06) : 1.0);
    const Real i_CaL_f1_gate_tau_f1 = (20.0 + (1102.5 * exp(-pow(pow(Vm * 1000.0 + 27.0, 2.0) / 15.0, 2.0)) + (200.0 / (1.0 + exp((13.0 - Vm * 1000.0) / 10.0)) + 180.0 / (1.0 + exp((30.0 + Vm * 1000.0) / 10.0))))) * i_CaL_f1_gate_constf1 / 1000.0;
    *_new_f1 = i_CaL_f1_gate_f1_inf + (f1 - i_CaL_f1_gate_f1_inf) * exp(-(dt / i_CaL_f1_gate_tau_f1));

    // i_CaL_f2_gate
    const Real i_CaL_f2_gate_f2_inf = 0.33 + 0.67 / (1.0 + exp((Vm * 1000.0 + i_CaL_f2_gate_offset_f2) / 4.0));
    const Real i_CaL_f2_gate_tau_f2 = (600.0 * exp(-pow(Vm * 1000.0 + 25.0, 2.0) / 170.0) + (31.0 / (1.0 + exp((25.0 - Vm * 1000.0) / 10.0)) + 16.0 / (1.0 + exp((30.0 + Vm * 1000.0) / 10.0)))) * i_CaL_f2_gate_constf2 / 1000.0;
    *_new_f2 = i_CaL_f2_gate_f2_inf + (f2 - i_CaL_f2_gate_f2_inf) * exp(-(dt / i_CaL_f2_gate_tau_f2));

    // i_CaL_fCa_gate
    const Real i_CaL_fCa_gate_alpha_fCa = 1.0 / (1.0 + pow(Cai / 0.0006, 8.0));
    const Real i_CaL_fCa_gate_beta_fCa = 0.1 / (1.0 + exp((Cai - 0.0009) / 0.0001));
    const Real i_CaL_fCa_gate_gamma_fCa = 0.3 / (1.0 + exp((Cai - 0.00075) / 0.0008));
    const Real i_CaL_fCa_gate_fCa_inf = (i_CaL_fCa_gate_alpha_fCa + (i_CaL_fCa_gate_beta_fCa + i_CaL_fCa_gate_gamma_fCa)) / 1.3156;
    const Real i_CaL_fCa_gate_constfCa = (((Vm > -0.06) && (i_CaL_fCa_gate_fCa_inf > fCa)) ? 0.0 : 1.0);
    *_new_fCa = fCa + dt*(i_CaL_fCa_gate_constfCa * (i_CaL_fCa_gate_fCa_inf - fCa) / i_CaL_fCa_gate_tau_fCa);

    // i_Kr_Xr2_gate
    const Real i_Kr_Xr2_gate_Xr2_infinity = 1.0 / (1.0 + exp((Vm * 1000.0 + 88.0) / 50.0));
    const Real i_Kr_Xr2_gate_alpha_Xr2 = 3.0 / (1.0 + exp((-60.0 - Vm * 1000.0) / 20.0));
    const Real i_Kr_Xr2_gate_beta_Xr2 = 1.12 / (1.0 + exp((-60.0 + Vm * 1000.0) / 20.0));
    const Real i_Kr_Xr2_gate_tau_Xr2 = 1.0 * (i_Kr_Xr2_gate_alpha_Xr2 * i_Kr_Xr2_gate_beta_Xr2) / 1000.0;
    *_new_Xr2 = i_Kr_Xr2_gate_Xr2_infinity + (Xr2 - i_Kr_Xr2_gate_Xr2_infinity) * exp(-(dt / i_Kr_Xr2_gate_tau_Xr2));

    // i_Ks_Xs_gate
    const Real i_Ks_Xs_gate_Xs_infinity = 1.0 / (1.0 + exp((-Vm * 1000.0 - 20.0) / 16.0));
    const Real i_Ks_Xs_gate_alpha_Xs = 1100.0 / (sqrt(1.0 + exp((-10.0 - Vm * 1000.0) / 6.0)));
    const Real i_Ks_Xs_gate_beta_Xs = 1.0 / (1.0 + exp((-60.0 + Vm * 1000.0) / 20.0));
    const Real i_Ks_Xs_gate_tau_Xs = 1.0 * (i_Ks_Xs_gate_alpha_Xs * i_Ks_Xs_gate_beta_Xs) / 1000.0;
    *_new_Xs = i_Ks_Xs_gate_Xs_infinity + (Xs - i_Ks_Xs_gate_Xs_infinity) * exp(-(dt / i_Ks_Xs_gate_tau_Xs));

    // i_Na_h_gate
    const Real i_Na_h_gate_alpha_h = ((Vm < -0.04) ? 0.057 * exp(-(Vm * 1000.0 + 80.0) / 6.8) : 0.0);
    const Real i_Na_h_gate_beta_h = ((Vm < -0.04) ? 2.7 * exp(0.079 * (Vm * 1000.0)) + 3.1 * (pow(10.0, 5.0) * exp(0.3485 * (Vm * 1000.0))) : 0.77 / ((fabs(0.13 * (1.0 + exp((Vm * 1000.0 + 10.66) / -11.1))) < VERY_SMALL_NUMBER) ? ((0.13 * (1.0 + exp((Vm * 1000.0 + 10.66) / -11.1)) < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : 0.13 * (1.0 + exp((Vm * 1000.0 + 10.66) / -11.1))));
    const Real i_Na_h_gate_h_inf = 1.0 / (sqrt(1.0 + exp((Vm * 1000.0 + 72.1) / 5.7)));
    const Real i_Na_h_gate_tau_h = ((Vm < -0.04) ? 1.5 / ((i_Na_h_gate_alpha_h + i_Na_h_gate_beta_h) * 1000.0) : 2.542 / 1000.0);
    *_new_h = i_Na_h_gate_h_inf + (h - i_Na_h_gate_h_inf) * exp(-(dt / i_Na_h_gate_tau_h));

    // i_Na_j_gate
    const Real i_Na_j_gate_alpha_j = ((Vm < -0.04) ? (-25428.0 * exp(0.2444 * (Vm * 1000.0)) - 6.948 * (pow(10.0, -6.0) * exp(-0.04391 * (Vm * 1000.0)))) * (Vm * 1000.0 + 37.78) / (1.0 + exp(0.311 * (Vm * 1000.0 + 79.23))) : 0.0);
    const Real i_Na_j_gate_beta_j = ((Vm < -0.04) ? 0.02424 * exp(-0.01052 * (Vm * 1000.0)) / (1.0 + exp(-0.1378 * (Vm * 1000.0 + 40.14))) : 0.6 * exp(0.057 * (Vm * 1000.0)) / (1.0 + exp(-0.1 * (Vm * 1000.0 + 32.0))));
    const Real i_Na_j_gate_j_inf = 1.0 / (sqrt(1.0 + exp((Vm * 1000.0 + 72.1) / 5.7)));
    const Real i_Na_j_gate_tau_j = 7.0 / ((i_Na_j_gate_alpha_j + i_Na_j_gate_beta_j) * 1000.0);
    *_new_j = i_Na_j_gate_j_inf + (j - i_Na_j_gate_j_inf) * exp(-(dt / i_Na_j_gate_tau_j));

    // i_Na_m_gate
    const Real i_Na_m_gate_alpha_m = 1.0 / (1.0 + exp((-Vm * 1000.0 - 60.0) / 5.0));
    const Real i_Na_m_gate_beta_m = 0.1 / (1.0 + exp((Vm * 1000.0 + 35.0) / 5.0)) + 0.1 / (1.0 + exp((Vm * 1000.0 - 50.0) / 200.0));
    const Real i_Na_m_gate_m_inf = 1.0 / (pow(1.0 + exp((-Vm * 1000.0 - 34.1) / 5.9), 1.0 / 3.0));
    const Real i_Na_m_gate_tau_m = 1.0 * (i_Na_m_gate_alpha_m * i_Na_m_gate_beta_m) / 1000.0;
    *_new_m = i_Na_m_gate_m_inf + (m - i_Na_m_gate_m_inf) * exp(-(dt / i_Na_m_gate_tau_m));

    // i_PCa
    const Real i_PCa_i_PCa = i_PCa_g_PCa * Cai / (Cai + i_PCa_KPCa);

    // i_f
    const Real i_f_i_f = i_f_g_f * (Xf * (Vm - i_f_E_f));

    // i_f_Xf_gate
    const Real i_f_Xf_gate_Xf_infinity = 1.0 / (1.0 + exp((Vm * 1000.0 + 77.85) / 5.0));
    const Real i_f_Xf_gate_tau_Xf = 1900.0 / (1.0 + exp((Vm * 1000.0 + 15.0) / 10.0)) / 1000.0;
    *_new_Xf = i_f_Xf_gate_Xf_infinity + (Xf - i_f_Xf_gate_Xf_infinity) * exp(-(dt / i_f_Xf_gate_tau_Xf));

    // i_to_q_gate
    const Real i_to_q_gate_q_inf = 1.0 / (1.0 + exp((Vm * 1000.0 + 53.0) / 13.0));
    const Real i_to_q_gate_tau_q = (6.06 + 39.102 / (0.57 * exp(-0.08 * (Vm * 1000.0 + 44.0)) + 0.065 * exp(0.1 * (Vm * 1000.0 + 45.93)))) / 1000.0;
    *_new_q = i_to_q_gate_q_inf + (q - i_to_q_gate_q_inf) * exp(-(dt / i_to_q_gate_tau_q));

    // i_to_r_gate
    const Real i_to_r_gate_r_inf = 1.0 / (1.0 + exp(-(Vm * 1000.0 - 22.3) / 18.75));
    const Real i_to_r_gate_tau_r = (2.75352 + 14.40516 / (1.037 * exp(0.09 * (Vm * 1000.0 + 30.61)) + 0.369 * exp(-0.12 * (Vm * 1000.0 + 23.84)))) / 1000.0;
    *_new_r = i_to_r_gate_r_inf + (r - i_to_r_gate_r_inf) * exp(-(dt / i_to_r_gate_tau_r));

    // electric_potentials
    const Real electric_potentials_E_Ca = 0.5 * (model_parameters_R * model_parameters_T) / model_parameters_F * log(model_parameters_Cao / (Cai));
    const Real electric_potentials_E_Na = model_parameters_R * model_parameters_T / model_parameters_F * log(model_parameters_Nao / (Nai));
    const Real electric_potentials_E_Ks = model_parameters_R * model_parameters_T / model_parameters_F * log((model_parameters_Ko + electric_potentials_PkNa * model_parameters_Nao) / (model_parameters_Ki + electric_potentials_PkNa * Nai));

    // i_CaL
    const Real i_CaL_i_CaL = i_CaL_g_CaL * (4.0 * (Vm * pow(model_parameters_F, 2.0))) / (model_parameters_R * model_parameters_T) * (Cai * exp(2.0 * (Vm * model_parameters_F) / (model_parameters_R * model_parameters_T)) - 0.341 * model_parameters_Cao) / ((fabs(exp(2.0 * (Vm * model_parameters_F) / (model_parameters_R * model_parameters_T)) - 1.0) < VERY_SMALL_NUMBER) ? ((exp(2.0 * (Vm * model_parameters_F) / (model_parameters_R * model_parameters_T)) - 1.0 < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : exp(2.0 * (Vm * model_parameters_F) / (model_parameters_R * model_parameters_T)) - 1.0) * (d * (f1 * (f2 * fCa)));

    // i_Kr_Xr1_gate
    const Real i_Kr_Xr1_gate_alpha_Xr1 = 450.0 / (1.0 + exp((-45.0 - Vm * 1000.0) / 10.0));
    const Real i_Kr_Xr1_gate_beta_Xr1 = 6.0 / (1.0 + exp((30.0 + Vm * 1000.0) / 11.5));
    const Real i_Kr_Xr1_gate_tau_Xr1 = 1.0 * (i_Kr_Xr1_gate_alpha_Xr1 * i_Kr_Xr1_gate_beta_Xr1) / 1000.0;
    const Real i_Kr_Xr1_gate_Xr1_inf = 1.0 / (1.0 + exp((i_Kr_Xr1_gate_V_half - Vm * 1000.0) / 4.9));
    *_new_Xr1 = i_Kr_Xr1_gate_Xr1_inf + (Xr1 - i_Kr_Xr1_gate_Xr1_inf) * exp(-(dt / i_Kr_Xr1_gate_tau_Xr1));

    // i_NaCa
    const Real i_NaCa_i_NaCa = i_NaCa_kNaCa * (exp(i_NaCa_gamma * (Vm * model_parameters_F) / (model_parameters_R * model_parameters_T)) * (pow(Nai, 3.0) * model_parameters_Cao) - exp((i_NaCa_gamma - 1.0) * (Vm * model_parameters_F) / (model_parameters_R * model_parameters_T)) * (pow(model_parameters_Nao, 3.0) * (Cai * i_NaCa_alpha))) / ((pow(i_NaCa_KmNai, 3.0) + pow(model_parameters_Nao, 3.0)) * ((i_NaCa_KmCa + model_parameters_Cao) * (1.0 + i_NaCa_Ksat * exp((i_NaCa_gamma - 1.0) * (Vm * model_parameters_F) / (model_parameters_R * model_parameters_T)))));

    // i_NaK
    const Real i_NaK_i_NaK = i_NaK_PNaK * model_parameters_Ko / (model_parameters_Ko + i_NaK_Km_K) * Nai / (Nai + i_NaK_Km_Na) / (1.0 + (0.1245 * exp(-0.1 * (Vm * model_parameters_F) / (model_parameters_R * model_parameters_T)) + 0.0353 * exp(-Vm * model_parameters_F / (model_parameters_R * model_parameters_T))));

    // i_K1
    const Real i_K1_alpha_K1 = 3.91 / (1.0 + exp(0.5942 * (Vm * 1000.0 - electric_potentials_E_K * 1000.0 - 200.0)));
    const Real i_K1_beta_K1 = (-1.509 * exp(0.0002 * (Vm * 1000.0 - electric_potentials_E_K * 1000.0 + 100.0)) + exp(0.5886 * (Vm * 1000.0 - electric_potentials_E_K * 1000.0 - 10.0))) / (1.0 + exp(0.4547 * (Vm * 1000.0 - electric_potentials_E_K * 1000.0)));
    const Real i_K1_XK1_inf = i_K1_alpha_K1 / (i_K1_alpha_K1 + i_K1_beta_K1);
    const Real i_K1_i_K1 = i_K1_g_K1 * (i_K1_XK1_inf * ((Vm - electric_potentials_E_K) * sqrt(model_parameters_Ko / 5.4)));

    // i_Kr
    const Real i_Kr_i_Kr = i_Kr_E4031_coeff * (i_Kr_g_Kr * ((Vm - electric_potentials_E_K) * (Xr1 * (Xr2 * sqrt(model_parameters_Ko / 5.4)))));

    // i_Ks
    const Real i_Ks_i_Ks = i_Ks_Chromanol_coeff * (i_Ks_g_Ks * ((Vm - electric_potentials_E_Ks) * (pow(Xs, 2.0) * (1.0 + 0.6 / (1.0 + pow(3.8 * 1e-05 / (Cai), 1.4))))));

    // i_Na
    const Real i_Na_i_Na = i_Na_TTX_coeff * (i_Na_g_Na * (pow(m, 3.0) * (h * (j * (Vm - electric_potentials_E_Na)))));

    // i_b_Ca
    const Real i_b_Ca_i_b_Ca = i_b_Ca_g_b_Ca * (Vm - electric_potentials_E_Ca);

    // i_b_Na
    const Real i_b_Na_i_b_Na = i_b_Na_g_b_Na * (Vm - electric_potentials_E_Na);

    // i_to
    const Real i_to_i_to = i_to_g_to * ((Vm - electric_potentials_E_K) * (q * r));

    // Membrane
    *_new_Vm = Vm + dt*(_diffuse_Vm - (i_K1_i_K1 + i_to_i_to + i_Kr_i_Kr + i_Ks_i_Ks + i_CaL_i_CaL + i_NaK_i_NaK + i_Na_i_Na + i_NaCa_i_NaCa + i_PCa_i_PCa + i_f_i_f + i_b_Na_i_b_Na + i_b_Ca_i_b_Ca));

    // calcium_dynamics
    const Real calcium_dynamics_g_inf = ((Cai <= 0.00035) ? 1.0 / (1.0 + pow(Cai / 0.00035, 6.0)) : 1.0 / (1.0 + pow(Cai / 0.00035, 16.0)));
    const Real calcium_dynamics_Ca_SR_bufSR = 1.0 / (1.0 + calcium_dynamics_Buf_SR * calcium_dynamics_Kbuf_SR / (pow(Ca_SR + calcium_dynamics_Kbuf_SR, 2.0)));
    const Real calcium_dynamics_Cai_bufc = 1.0 / (1.0 + calcium_dynamics_Buf_C * calcium_dynamics_Kbuf_C / (pow(Cai + calcium_dynamics_Kbuf_C, 2.0)));
    const Real calcium_dynamics_const2 = (((calcium_dynamics_g_inf > g) && (Vm > -0.06)) ? 0.0 : 1.0);
    const Real calcium_dynamics_i_leak = (Ca_SR - Cai) * calcium_dynamics_V_leak;
    const Real calcium_dynamics_i_rel = (calcium_dynamics_c_rel + calcium_dynamics_a_rel * pow(Ca_SR, 2.0) / (pow(calcium_dynamics_b_rel, 2.0) + pow(Ca_SR, 2.0))) * (d * (g * calcium_dynamics_g_factor));
    const Real calcium_dynamics_i_up = calcium_dynamics_VmaxUp / (1.0 + pow(calcium_dynamics_Kup, 2.0) / (pow(Cai, 2.0)));
    *_new_Ca_SR = Ca_SR + dt*(calcium_dynamics_Ca_SR_bufSR * model_parameters_Vc / model_parameters_V_SR * (calcium_dynamics_i_up - (calcium_dynamics_i_rel + calcium_dynamics_i_leak)));
    *_new_Cai = Cai + dt*(calcium_dynamics_Cai_bufc * (calcium_dynamics_i_leak - calcium_dynamics_i_up + calcium_dynamics_i_rel - (i_CaL_i_CaL + (i_b_Ca_i_b_Ca + i_PCa_i_PCa) - 2.0 * i_NaCa_i_NaCa) * model_parameters_Cm / (2.0 * (model_parameters_Vc * (model_parameters_F * 1e-18)))));
    *_new_g = g + dt*(calcium_dynamics_const2 * (calcium_dynamics_g_inf - g) / calcium_dynamics_tau_g);

    // sodium_dynamics
    *_new_Nai = Nai + dt*(-model_parameters_Cm * (i_Na_i_Na + (i_b_Na_i_b_Na + (3.0 * i_NaK_i_NaK + 3.0 * i_NaCa_i_NaCa))) / (model_parameters_F * (model_parameters_Vc * 1e-18)));

    // check for unphysical values
    if(*_new_Nai <= 0.0) { *_new_Nai = VERY_SMALL_NUMBER; }
    if(*_new_Cai <= 0.0) { *_new_Cai = VERY_SMALL_NUMBER; }
    if(*_new_Ca_SR <= 0.0) { *_new_Ca_SR = VERY_SMALL_NUMBER; }


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
    initial values:
      ventricular:
        Vm: -0.0743340057623841
        m: 0.102953468725004
        h: 0.786926637881461
        j: 0.253943221774722
        d: 8.96088425225182e-05
        f1: 0.970411811263976
        f2: 0.999965815466749
        fCa: 0.998925296531804
        Xr1: 0.00778547011240132
        Xr2: 0.432162576531617
        Xs: 0.0322944866983666
        Xf: 0.100615100568753
        q: 0.839295925773219
        r: 0.00573289893326379
        Nai: 10.9248496211574
        Cai: 1.80773974140477e-05
        Ca_SR: 0.2734234751931
        g: 0.999999981028517
      ventricular resting:
        Vm: -0.0743340057623841
        m: 0.102953468725004
        h: 0.786926637881461
        j: 0.253943221774722
        d: 8.96088425225182e-05
        f1: 0.970411811263976
        f2: 0.999965815466749
        fCa: 0.998925296531804
        Xr1: 0.00778547011240132
        Xr2: 0.432162576531617
        Xs: 0.0322944866983666
        Xf: 0.100615100568753
        q: 0.839295925773219
        r: 0.00573289893326379
        Nai: 10.9248496211574
        Cai: 1.80773974140477e-05
        Ca_SR: 0.2734234751931
        g: 0.999999981028517
      atrial:
        Vm: -0.068733823452164
        m: 0.141183142078492
        h: 0.642108593994587
        j: 0.173566329483423
        d: 0.000127632520741878
        f1: 0.98038400433601
        f2: 0.999953006710394
        fCa: 0.997346890768643
        Xr1: 0.0257889110986083
        Xr2: 0.405046678739985
        Xs: 0.0447460799149437
        Xf: 0.0607988713874682
        q: 0.776163826643278
        r: 0.000503296941001262
        Nai: 14.4424010544424
        Cai: 4.49232909234503e-05
        Ca_SR: 0.149980051221604
        g: 1.0
    parameter sets:
      ventricular:
        calcium_dynamics_VmaxUp: 0.56064
        calcium_dynamics_g_factor: 0.0411
        i_CaL_d_gate_offset_d: 9.1
        i_CaL_f1_gate_offset_f1: 26.0
        i_CaL_f2_gate_constf2: 1.0
        i_CaL_f2_gate_offset_f2: 35.0
        i_K1_g_K1: 28.1492
        i_NaCa_kNaCa: 4900.0
        i_NaK_PNaK: 1.841424
        i_Na_g_Na: 3671.2302
        i_to_g_to: 29.9038
        model_parameters_Cm: 9.87109e-11
        model_parameters_V_SR: 583.73
        model_parameters_Vc: 8800.0
      atrial:
        calcium_dynamics_VmaxUp: 0.22
        calcium_dynamics_g_factor: 0.0556
        i_CaL_d_gate_offset_d: 5.986
        i_CaL_f1_gate_offset_f1: 25.226
        i_CaL_f2_gate_constf2: 2.0
        i_CaL_f2_gate_offset_f2: 31.226
        i_K1_g_K1: 19.1925
        i_NaCa_kNaCa: 2450.0
        i_NaK_PNaK: 1.4731392
        i_Na_g_Na: 6646.185
        i_to_g_to: 59.8077
        model_parameters_Cm: 7.86671e-11
        model_parameters_V_SR: 465.2
        model_parametegs_Vc: 7012.0

