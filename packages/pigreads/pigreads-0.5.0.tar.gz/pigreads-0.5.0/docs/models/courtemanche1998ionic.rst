.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.h``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.

Courtemanche et al. 1998
========================

**Key:** ``courtemanche1998ionic``

The human atrial electrophysiology model by Courtemanche, Ramirez and Nattel
1998 is widely used in both single-cell and tissue-level simulations,
particularly in studies of atrial fibrillation and action potential dynamics.
As one of the first detailed and extensively validated atrial model, it is
considered a benchmark in the field of cardiac electrophysiology.

Suggested parameters: dt = 0.005ms, dx = 0.25mm, diffusivity = 0.1544 mm^2/ms.

References
----------
1. https://doi.org/10.1152/ajpheart.1998.275.1.H301

Variables
---------
0. ``V = -81.18``
1. ``Na_i = 11.17``
2. ``K_i = 139.0``
3. ``Ca_i = 0.0001013``
4. ``Ca_up = 1.488``
5. ``Ca_rel = 1.488``
6. ``m = 0.002908``
7. ``h = 0.9649``
8. ``j = 0.9775``
9. ``oa = 0.03043``
10. ``oi = 0.9992``
11. ``ua = 0.004966``
12. ``ui = 0.9986``
13. ``xr = 3.296e-05``
14. ``xs = 0.01869``
15. ``d = 0.0001367``
16. ``f = 0.9996``
17. ``f_Ca = 0.7755``
18. ``u = 0.0``
19. ``v = 1.0``
20. ``w = 0.9992``

Parameters
----------
- ``diffusivity_V = 1.0``
- ``T = 310.0``
- ``F = 96.4867``
- ``R = 8.3143``
- ``V_cell = 20100.0``
- ``Cm = 100.0``
- ``V_rel = 96.48``
- ``V_i = 13668.0``
- ``V_up = 1109.52``
- ``sigma = 1.0009103049457284``
- ``Ca_o = 1.8``
- ``K_o = 5.4``
- ``Na_o = 140.0``
- ``g_Na = 7.8``
- ``g_K1 = 0.09``
- ``g_to = 0.1652``
- ``K_Q10 = 3.0``
- ``g_Kr = 0.029411765``
- ``g_Ks = 0.12941176``
- ``g_Ca_L = 0.12375``
- ``ical_f_Ca_tau = 2.0``
- ``i_NaK_max = 0.59933874``
- ``Km_Na_i = 10.0``
- ``Km_K_o = 1.5``
- ``I_NaCa_max = 1600.0``
- ``inaca_gamma = 0.35``
- ``K_mNa = 87.5``
- ``K_mCa = 1.38``
- ``K_sat = 0.1``
- ``g_B_Na = 0.0006744375``
- ``g_B_Ca = 0.001131``
- ``g_B_K = 0.0``
- ``i_PCa_max = 0.275``
- ``I_up_max = 0.005``
- ``K_up = 0.00092``
- ``Ca_up_max = 15.0``
- ``cajsr_u_tau = 8.0``
- ``tau_tr = 180.0``
- ``K_rel = 30.0``
- ``CMDN_max = 0.05``
- ``CSQN_max = 10.0``
- ``TRPN_max = 0.07``
- ``Km_CMDN = 0.00238``
- ``Km_CSQN = 0.8``
- ``Km_TRPN = 0.0005``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    // extracellular currents
    // calculate i_Na
    const Real ina_j_beta = ((V < -40.0) ? 0.1212 * exp(-0.01052 * V) / (1.0 + exp(-0.1378 * (V + 40.14))) : 0.3 * exp(-2.535e-07 * V) / (1.0 + exp(-0.1 * (V + 32.0))));
    const Real ina_j_alpha = ((V < -40.0) ? (-127140.0 * exp(0.2444 * V) - 3.474e-05 * exp(-0.04391 * V)) * (V + 37.78) / (1.0 + exp(0.311 * (V + 79.23))) : 0.0);
    const Real ina_j_tau = 1.0 / (ina_j_alpha + ina_j_beta);
    const Real ina_j_inf = ina_j_alpha / (ina_j_alpha + ina_j_beta);
    *_new_j = ina_j_inf + (j - ina_j_inf)*exp(-dt/ina_j_tau);

    const Real ina_m_beta = 0.08 * exp(-V / 11.0);
    // (singularity)
    const Real ina_m_alpha = ((fabs(V + 47.13) < 1e-5) ? 3.2 : 0.32 * (V + 47.13) / (1.0 - exp(-0.1 * (V + 47.13))));
    const Real ina_m_inf = ina_m_alpha / (ina_m_alpha + ina_m_beta);
    const Real ina_m_tau = 1.0 / (ina_m_alpha + ina_m_beta);
    *_new_m = ina_m_inf + (m - ina_m_inf)*exp(-dt/ina_m_tau);

    const Real ina_h_alpha = ((V < -40.0) ? 0.135 * exp((V + 80.0) / -6.8) : 0.0);
    const Real ina_h_beta = ((V < -40.0) ? 3.56 * exp(0.079 * V) + 310000.0 * exp(0.35 * V) : 1.0 / (0.13 * (1.0 + exp((V + 10.66) / -11.1))));
    const Real ina_h_inf = ina_h_alpha / (ina_h_alpha + ina_h_beta);
    const Real ina_h_tau = 1.0 / (ina_h_alpha + ina_h_beta);
    *_new_h = ina_h_inf + (h - ina_h_inf)*exp(-dt/ina_h_tau);

    const Real E_Na = R * T / F * log(Na_o / Na_i);
    const Real i_Na =  Cm * g_Na * m*m*m * h * j * (V - E_Na);

    // calculate i_K1
    const Real E_K = R * T / F * log(K_o / K_i);
    const Real i_K1 = Cm * g_K1 * (V - E_K) / (1.0 + exp(0.07 * (V + 80.0)));

    // calculate i_to
    const Real ito_oi_beta = pow(35.56 + 1.0 * exp((V - -10.0 - 8.74) / -7.44), -1.0);
    const Real ito_oi_alpha = pow(18.53 + 1.0 * exp((V - -10.0 + 103.7) / 10.95), -1.0);
    const Real ito_oi_inf = pow(1.0 + exp((V - -10.0 + 33.1) / 5.3), -1.0);
    const Real ito_oi_tau = pow(ito_oi_alpha + ito_oi_beta, -1.0) / K_Q10;
    *_new_oi = ito_oi_inf + (oi - ito_oi_inf)*exp(-dt/ito_oi_tau);

    const Real ito_oa_alpha = 0.65 / (exp((V - -10.0) / -8.5) + exp((V - -10.0 - 40.0) / -59.0));
    const Real ito_oa_beta = 0.65 / (2.5 + exp((V - -10.0 + 72.0) / 17.0));
    const Real ito_oa_inf = pow(1.0 + exp((V - -10.0 + 10.47) / -17.54), -1.0);
    const Real ito_oa_tau = pow(ito_oa_alpha + ito_oa_beta, -1.0) / K_Q10;
    *_new_oa = ito_oa_inf + (oa - ito_oa_inf)*exp(-dt/ito_oa_tau);

    const Real i_to = Cm * g_to * oa*oa*oa * oi * (V - E_K);

    // calculate i_Kur
    const Real ikur_ua_inf = pow(1.0 + exp((V - -10.0 + 20.3) / -9.6), -1.0);
    const Real ikur_ua_beta = 0.65 / (2.5 + exp((V - -10.0 + 72.0) / 17.0));
    const Real ikur_ua_alpha = 0.65 / (exp((V - -10.0) / -8.5) + exp((V - -10.0 - 40.0) / -59.0));
    const Real ikur_ua_tau = pow(ikur_ua_alpha + ikur_ua_beta, -1.0) / K_Q10;
    *_new_ua = ikur_ua_inf + (ua - ikur_ua_inf)*exp(-dt/ikur_ua_tau);

    const Real ikur_ui_inf = pow(1.0 + exp((V - -10.0 - 109.45) / 27.48), -1.0);
    const Real ikur_ui_tau_alpha = pow(21.0 + 1.0 * exp((V - -10.0 - 195.0) / -28.0), -1.0);
    const Real ikur_ui_tau_beta = 1.0 / exp((V - -10.0 - 168.0) / -16.0);
    const Real ikur_ui_tau = pow(ikur_ui_tau_alpha + ikur_ui_tau_beta, -1.0) / K_Q10;
    *_new_ui = ikur_ui_inf + (ui - ikur_ui_inf)*exp(-dt/ikur_ui_tau);

    const Real g_Kur = 0.005 + 0.05 / (1.0 + exp((V - 15.0) / -13.0));

    const Real i_Kur = Cm * g_Kur * ua*ua*ua * ui * (V - E_K);

    // calculate i_Kr
    const Real ikr_xr_inf = pow(1.0 + exp((V + 14.1) / -6.5), -1.0);
    // (singularity)
    const Real ikr_xr_tau_beta = ((fabs(V - 3.3328) < 1e-5) ? 3.7836118e-04 : 7.3898e-05 * (V - 3.3328) / (exp((V - 3.3328) / 5.1237) - 1.0));
    const Real ikr_xr_tau_alpha = ((fabs(V + 14.1) < 1e-5) ? 0.0015 : 0.0003 * (V + 14.1) / (1.0 - exp((V + 14.1) / -5.0)));
    const Real ikr_xr_tau = pow(ikr_xr_tau_alpha + ikr_xr_tau_beta, -1.0);
    *_new_xr = ikr_xr_inf + (xr - ikr_xr_inf)*exp(-dt/ikr_xr_tau);

    const Real i_Kr = Cm * g_Kr * xr * (V - E_K) / (1.0 + exp((V + 15.0) / 22.4));

    // calculate i_Ks
    const Real iks_xs_inf = pow(1.0 + exp((V - 19.9) / -12.7), -0.5);
    // (singularity)
    const Real iks_xs_tau_beta = ((fabs(V - 19.9) < 1e-5) ? 0.000315 : 3.5e-05 * (V - 19.9) / (exp((V - 19.9) / 9.0) - 1.0));
    const Real iks_xs_tau_alpha = ((fabs(V - 19.9) < 1e-5) ? 0.00068 : 4e-05 * (V - 19.9) / (1.0 - exp((V - 19.9) / -17.0)));
    const Real iks_xs_tau = 0.5 / (iks_xs_tau_alpha + iks_xs_tau_beta);
    *_new_xs = iks_xs_inf + (xs - iks_xs_inf)*exp(-dt/iks_xs_tau);
    const Real i_Ks = Cm * g_Ks * xs*xs * (V - E_K);

    // calculate i_Ca_L
    const Real ical_f_inf = exp(-(V + 28.0) / 6.9) / (1.0 + exp(-(V + 28.0) / 6.9));
    const Real ical_f_tau = 9.0 * pow(0.0197 * exp(-pow(0.0337, 2.0) * pow(V + 10.0, 2.0)) + 0.02, -1.0);
    *_new_f = ical_f_inf + (f - ical_f_inf)*exp(-dt/ical_f_tau);

    const Real ical_f_Ca_inf = pow(1.0 + Ca_i / 0.00035, -1.0);
    *_new_f_Ca = ical_f_Ca_inf + (f_Ca - ical_f_Ca_inf)*exp(-dt/ical_f_Ca_tau);

    const Real ical_d_inf = pow(1.0 + exp((V + 10.0) / -8.0), -1.0);
    const Real ical_d_tau = ((fabs(V + 10.0) < 1e-10) ? 4.579 / (1.0 + exp((V + 10.0) / -6.24)) : (1.0 - exp((V + 10.0) / -6.24)) / (0.035 * (V + 10.0) * (1.0 + exp((V + 10.0) / -6.24))));
    *_new_d = ical_d_inf + (d - ical_d_inf)*exp(-dt/ical_d_tau);

    const Real i_Ca_L = Cm * g_Ca_L * d * f * f_Ca * (V - 65.0);

    // calculate I_B_*
    const Real E_Ca = R * T / (2.0 * F) * log(Ca_o / Ca_i);
    const Real i_B_K = Cm * g_B_K * (V - E_K);
    const Real i_B_Ca = Cm * g_B_Ca * (V - E_Ca);
    const Real i_B_Na = Cm * g_B_Na * (V - E_Na);

    // calculate i_NaK
    const Real f_NaK = pow(1.0 + 0.1245 * exp(-0.1 * F * V / (R * T)) + 0.0365 * sigma * exp(-F * V / (R * T)), -1.0);
    const Real i_NaK = Cm * i_NaK_max * f_NaK * 1.0 / (1.0 + pow(Km_Na_i / Na_i, 1.5)) * K_o / (K_o + Km_K_o);

    // calculate i_PCa
    const Real i_PCa = Cm * i_PCa_max * Ca_i / (0.0005 + Ca_i);

    // calculate i_NaCa
    const Real i_NaCa = Cm * I_NaCa_max * (exp(inaca_gamma * F * V / (R * T)) * Na_i*Na_i*Na_i * Ca_o - exp((inaca_gamma - 1.0) * F * V / (R * T)) * Na_o*Na_o*Na_o * Ca_i) / ((K_mNa*K_mNa*K_mNa + Na_o*Na_o*Na_o) * (K_mCa + Ca_o) * (1.0 + K_sat * exp((inaca_gamma - 1.0) * V * F / (R * T))));

    // misc
    const Real i_up = I_up_max / (1.0 + K_up / Ca_i);
    const Real i_up_leak = I_up_max * Ca_up / Ca_up_max;
    const Real i_tr = (Ca_up - Ca_rel) / tau_tr;

    // intracellular Ca-currents
    const Real i_rel = K_rel * u*u * v * w * (Ca_rel - Ca_i);
    const Real cajsr_w_inf = 1.0 - pow(1.0 + exp(-(V - 40.0) / 17.0), -1.0);
    const Real cajsr_w_tau = (fabs(V - 7.9) < 1e-4) ? 6.0 * 0.2 / 1.3 : 6.0 * (1.0 - exp(-(V - 7.9) / 5.0)) / ((1.0 + 0.3 * exp(-(V - 7.9) / 5.0)) * 1.0 * (V - 7.9));
    *_new_w = cajsr_w_inf + (w - cajsr_w_inf)*exp(-dt/cajsr_w_tau);

    const Real Fn = 1000.0 * (1e-15 * V_rel * i_rel - 1e-15 / (2.0 * F) * (0.5 * i_Ca_L - 0.2 * i_NaCa));
    const Real cajsr_v_inf = 1.0 - pow(1.0 + exp(-(Fn - 6.835e-14) / 1.367e-15), -1.0);
    const Real cajsr_v_tau = 1.91 + 2.09 / (1.0 + exp(-(Fn - 3.4175e-13) / 1.367e-15));
    *_new_v = cajsr_v_inf + (v - cajsr_v_inf)*exp(-dt/cajsr_v_tau);

    const Real cajsr_u_inf = pow(1.0 + exp(-(Fn - 3.4175e-13) / 1.367e-15), -1.0);
    *_new_u = cajsr_u_inf + (u - cajsr_u_inf)*exp(-dt/cajsr_u_tau);

    // total current
    const Real i_ion = i_Na + i_K1 + i_to + i_Kur + i_Kr + i_Ks + i_B_Na + i_B_Ca + i_NaK + i_PCa + i_NaCa + i_Ca_L;

    // update concentrations
    *_new_Na_i = Na_i + dt * ((-3.0 * i_NaK - (3.0 * i_NaCa + i_B_Na + i_Na)) / (V_i * F));
    *_new_K_i = K_i + dt * ((2.0 * i_NaK - (i_K1 + i_to + i_Kur + i_Kr + i_Ks + i_B_K)) / (V_i * F));
    *_new_Ca_rel = Ca_rel + dt * ((i_tr - i_rel) * pow(1.0 + CSQN_max * Km_CSQN / pow(Ca_rel + Km_CSQN, 2.0), -1.0));
    *_new_Ca_up = Ca_up + dt * (i_up - (i_up_leak + i_tr * V_rel / V_up));
    *_new_Ca_i = Ca_i + dt * ((2.0 * i_NaCa - (i_PCa + i_Ca_L + i_B_Ca)) / (2.0 * V_i * F) + (V_up * (i_up_leak - i_up) + i_rel * V_rel) / V_i) / (1.0 + TRPN_max * Km_TRPN / pow(Ca_i + Km_TRPN, 2.0) + CMDN_max * Km_CMDN / pow(Ca_i + Km_CMDN, 2.0));

    // update voltage
    *_new_V = V + dt * (_diffuse_V - i_ion/Cm);


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

