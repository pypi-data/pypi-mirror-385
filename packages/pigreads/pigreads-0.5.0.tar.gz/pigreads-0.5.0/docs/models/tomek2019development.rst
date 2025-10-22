.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.h``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.

Tomek et al. 2019
=================

**Key:** ``tomek2019development``

A human-based ventricular model (ToR-Ord, endocardial, epicardial,
midmyocardial) for simulations of electrophysiology and
excitation-contraction coupling, from ionic to whole-organ dynamics,
including the electrocardiogram. Validation based on substantial multiscale
simulations supports the credibility of the ToR-ORd model under healthy and
key disease conditions, as well as drug blockade. In addition, the process
uncovers new theoretical insights into the biophysical properties of the
L-type calcium current, which are critical for sodium and calcium dynamics.
These insights enable the reformulation of L-type calcium current, as well as
replacement of the hERG current model.

References
----------
1. https://doi.org/10.7554/eLife.48890

Variables
---------
0. ``V = -88.7638``
1. ``CaMKt = 0.0111``
2. ``Nai = 12.1025``
3. ``Nass = 12.1029``
4. ``Ki = 142.3002``
5. ``Kss = 142.3002``
6. ``Cass = 7.0305e-05``
7. ``Cansr = 1.5211``
8. ``Cajsr = 1.5214``
9. ``Cai = 8.1583e-05``
10. ``m = 0.00080572``
11. ``h = 0.8286``
12. ``j = 0.8284``
13. ``hp = 0.6707``
14. ``jp = 0.8281``
15. ``mL = 0.0001629``
16. ``hL = 0.5255``
17. ``hLp = 0.2872``
18. ``a = 0.00095098``
19. ``iF = 0.9996``
20. ``iS = 0.5936``
21. ``ap = 0.00048454``
22. ``iFp = 0.9996``
23. ``iSp = 0.6538``
24. ``d = 8.1084e-09``
25. ``ff = 1.0``
26. ``fs = 0.939``
27. ``fcaf = 1.0``
28. ``fcas = 0.9999``
29. ``jca = 1.0``
30. ``ffp = 1.0``
31. ``fcafp = 1.0``
32. ``nca_ss = 0.00066462``
33. ``nca_i = 0.0012``
34. ``C1 = 0.00070344``
35. ``C2 = 0.00085109``
36. ``C3 = 0.9981``
37. ``I = 1.3289e-05``
38. ``O = 0.00037585``
39. ``xs1 = 0.248``
40. ``xs2 = 0.00017707``
41. ``Jrel_np = 1.6129e-22``
42. ``Jrel_p = 1.2475e-20``

Parameters
----------
- ``diffusivity_V = 1.0``
- ``CaMKo = 0.05``
- ``KmCaM = 0.0015``
- ``KmCaMK = 0.15``
- ``aCaMK = 0.05``
- ``bCaMK = 0.00068``
- ``GpCa = 0.0005``
- ``KmCap = 0.0005``
- ``L = 0.01``
- ``rad = 0.0011``
- ``Ageo = 7.667880000000002e-05``
- ``vcell = 3.799400000000001e-05``
- ``Acap = 0.00015335760000000003``
- ``vjsr = 1.8237120000000002e-07``
- ``vmyo = 2.583592000000001e-05``
- ``vnsr = 2.0972688000000006e-06``
- ``vss = 7.598800000000002e-07``
- ``tauCa = 0.2``
- ``tauK = 2.0``
- ``tauNa = 2.0``
- ``celltype = 0.0``
- ``cao = 1.8``
- ``clo = 150.0``
- ``ko = 5.0``
- ``nao = 140.0``
- ``F = 96485.0``
- ``R = 8314.0``
- ``T = 310.0``
- ``zca = 2.0``
- ``zcl = -1.0``
- ``zk = 1.0``
- ``zna = 1.0``
- ``Jup_b = 1.0``
- ``upScale = 1.0``
- ``BSLmax = 1.124``
- ``BSRmax = 0.047``
- ``KmBSL = 0.0087``
- ``KmBSR = 0.00087``
- ``cli = 24.0``
- ``cmdnmax_b = 0.05``
- ``csqnmax = 10.0``
- ``kmcmdn = 0.00238``
- ``kmcsqn = 0.8``
- ``kmtrpn = 0.0005``
- ``trpnmax = 0.07``
- ``cmdnmax = 0.05``
- ``ECl = -48.95253676506265``
- ``PKNa = 0.01833``
- ``A_atp = 2.0``
- ``K_atp = 0.25``
- ``K_o_n = 5.0``
- ``fkatp = 0.0``
- ``gkatp = 4.3195``
- ``akik = 1.0``
- ``bkik = 0.015384615384615385``
- ``GNa = 11.7802``
- ``GNaL_b = 0.0279``
- ``thL = 200.0``
- ``GNaL = 0.0279``
- ``thLp = 600.0``
- ``EKshift = 0.0``
- ``Gto_b = 0.16``
- ``Gto = 0.16``
- ``Aff = 0.6``
- ``ICaL_fractionSS = 0.8``
- ``Io = 0.15109999999999998``
- ``Kmn = 0.002``
- ``PCa_b = 8.3757e-05``
- ``dielConstant = 74.0``
- ``k2n = 500.0``
- ``offset = 0.0``
- ``tjca = 75.0``
- ``vShift = 0.0``
- ``Afs = 0.4``
- ``PCa = 8.3757e-05``
- ``constA = 0.5238190247282047``
- ``PCaK = 2.99347518e-08``
- ``PCaNa = 1.0469625000000001e-07``
- ``PCap = 9.213270000000001e-05``
- ``gamma_cao = 0.6117017520062547``
- ``gamma_ko = 0.8843718923169582``
- ``gamma_nao = 0.8843718923169582``
- ``PCaKp = 3.292822698000001e-08``
- ``PCaNap = 1.1516587500000002e-07``
- ``GKr_b = 0.0321``
- ``alpha_1 = 0.154375``
- ``beta_1 = 0.1911``
- ``GKr = 0.0321``
- ``GKs_b = 0.0011``
- ``GKs = 0.0011``
- ``GK1_b = 0.6992``
- ``GK1 = 0.6992``
- ``Gncx_b = 0.0034``
- ``INaCa_fractionSS = 0.35``
- ``KmCaAct = 0.00015``
- ``kasymm = 12.5``
- ``kcaoff = 5000.0``
- ``kcaon = 1500000.0``
- ``kna1 = 15.0``
- ``kna2 = 5.0``
- ``kna3 = 88.12``
- ``qca = 0.167``
- ``qna = 0.5224``
- ``wca = 60000.0``
- ``wna = 60000.0``
- ``wnaca = 5000.0``
- ``Gncx = 0.0034``
- ``h10_i = 284.1666666666667``
- ``h10_ss = 284.1666666666667``
- ``k2_i = 5000.0``
- ``k2_ss = 5000.0``
- ``k5_i = 5000.0``
- ``k5_ss = 5000.0``
- ``h11_i = 0.9196480938416423``
- ``h11_ss = 0.9196480938416423``
- ``h12_i = 0.003519061583577712``
- ``h12_ss = 0.003519061583577712``
- ``k1_i = 9501.466275659823``
- ``k1_ss = 9501.466275659823``
- ``H = 1e-07``
- ``Khp = 1.698e-07``
- ``Kki = 0.5``
- ``Kko = 0.3582``
- ``Kmgatp = 1.698e-07``
- ``Knai0 = 9.073``
- ``Knao0 = 27.78``
- ``Knap = 224.0``
- ``Kxkur = 292.0``
- ``MgADP = 0.05``
- ``MgATP = 9.8``
- ``Pnak_b = 15.4509``
- ``delta = -0.155``
- ``eP = 4.2``
- ``k1m = 182.4``
- ``k1p = 949.5``
- ``k2m = 39.4``
- ``k2p = 687.2``
- ``k3m = 79300.0``
- ``k3p = 1899.0``
- ``k4m = 40.0``
- ``k4p = 639.0``
- ``Pnak = 15.4509``
- ``a2 = 687.2``
- ``a4 = 638.9999889283472``
- ``b1 = 9.120000000000001``
- ``GKb_b = 0.0189``
- ``GKb = 0.0189``
- ``PNab = 1.9239e-09``
- ``PCab = 5.9194e-08``
- ``Fjunc = 1.0``
- ``GClCa = 0.2843``
- ``GClb = 0.00198``
- ``KdClCa = 0.1``
- ``Jrel_b = 1.5378``
- ``bt = 4.75``
- ``cajsr_half = 1.7``
- ``a_rel = 2.375``
- ``btp = 5.9375``
- ``a_relp = 2.96875``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    // CaMK
    const Real CaMKb = CaMKo * (1.0 - CaMKt) / (1.0 + KmCaM / (Cass));
    const Real CaMKa = CaMKb + CaMKt;
    *_new_CaMKt = CaMKt + dt*(aCaMK * CaMKb * (CaMKb + CaMKt) - bCaMK * CaMKt);

    // IpCa
    const Real IpCa = GpCa * Cai / (KmCap + Cai);

    // diff
    const Real Jdiff = (Cass - Cai) / tauCa;
    const Real JdiffK = (Kss - Ki) / tauK;
    const Real JdiffNa = (Nass - Nai) / tauNa;

    // trans_flux
    const Real Jtr = (Cansr - Cajsr) / 60.0;

    // SERCA
    const Real Jleak = 0.0048825 * Cansr / 15.0;
    const Real fJupp = 1.0 / (1.0 + KmCaMK / (CaMKa));
    const Real Jupnp = upScale * 0.005425 * Cai / (Cai + 0.00092);
    const Real Jupp = upScale * 2.75 * 0.005425 * Cai / (Cai + 0.00092 - 0.00017);
    const Real Jup = Jup_b * ((1.0 - fJupp) * Jupnp + fJupp * Jupp - Jleak);

    // membrane
    const Real vffrt = V * F * F / (R * T);
    const Real vfrt = V * F / (R * T);

    // intracellular_ions
    *_new_Cansr = Cansr + dt*(Jup - Jtr * vjsr / vnsr);
    const Real Bcajsr = 1.0 / (1.0 + csqnmax * kmcsqn / (pow(kmcsqn + Cajsr, 2.0)));
    const Real Bcass = 1.0 / (1.0 + BSRmax * KmBSR / (pow(KmBSR + Cass, 2.0)) + BSLmax * KmBSL / (pow(KmBSL + Cass, 2.0)));
    const Real Bcai = 1.0 / (1.0 + cmdnmax * kmcmdn / (pow(kmcmdn + Cai, 2.0)) + trpnmax * kmtrpn / (pow(kmtrpn + Cai, 2.0)));

    // reversal_potentials
    const Real EK = R * T / (zk * F) * log(ko / (Ki));
    const Real ENa = R * T / (zna * F) * log(nao / (Nai));
    const Real EKs = R * T / (zk * F) * log((ko + PKNa * nao) / (Ki + PKNa * Nai));

    // I_katp
    const Real I_katp = fkatp * gkatp * akik * bkik * (V - EK);

    // INa
    const Real ah = ((V >= -40.0) ? 0.0 : 0.057 * exp(-(V + 80.0) / 6.8));
    const Real aj = ((V >= -40.0) ? 0.0 : (-25428.0 * exp(0.2444 * V) - 6.948e-06 * exp(-0.04391 * V)) * (V + 37.78) / (1.0 + exp(0.311 * (V + 79.23))));
    const Real bh = ((V >= -40.0) ? 0.77 / (0.13 * (1.0 + exp(-(V + 10.66) / 11.1))) : 2.7 * exp(0.079 * V) + 310000.0 * exp(0.3485 * V));
    const Real bj = ((V >= -40.0) ? 0.6 * exp(0.057 * V) / (1.0 + exp(-0.1 * (V + 32.0))) : 0.02424 * exp(-0.01052 * V) / (1.0 + exp(-0.1378 * (V + 40.14))));
    const Real fINap = 1.0 / (1.0 + KmCaMK / (CaMKa));
    const Real hss = 1.0 / (pow(1.0 + exp((V + 71.55) / 7.43), 2.0));
    const Real hssp = 1.0 / (pow(1.0 + exp((V + 77.55) / 7.43), 2.0));
    const Real mss = 1.0 / (pow(1.0 + exp(-(V + 56.86) / 9.03), 2.0));
    const Real tm = 0.1292 * exp(-pow((V + 45.79) / 15.54, 2.0)) + 0.06487 * exp(-pow((V - 4.823) / 51.12, 2.0));
    const Real INa = GNa * (V - ENa) * pow(m, 3.0) * ((1.0 - fINap) * h * j + fINap * hp * jp);
    const Real jss = hss;
    const Real th = 1.0 / (ah + bh);
    const Real tj = 1.0 / (aj + bj);
    *_new_m = mss + (m - mss) * exp(-(dt / tm));
    const Real tjp = 1.46 * tj;
    *_new_h = hss + (h - hss) * exp(-(dt / th));
    *_new_hp = hssp + (hp - hssp) * exp(-(dt / th));
    *_new_j = jss + (j - jss) * exp(-(dt / tj));
    *_new_jp = jss + (jp - jss) * exp(-(dt / tjp));

    // INaL
    const Real fINaLp = 1.0 / (1.0 + KmCaMK / (CaMKa));
    const Real hLss = 1.0 / (1.0 + exp((V + 87.61) / 7.488));
    const Real hLssp = 1.0 / (1.0 + exp((V + 93.81) / 7.488));
    const Real mLss = 1.0 / (1.0 + exp(-(V + 42.85) / 5.264));
    const Real tmL = 0.1292 * exp(-pow((V + 45.79) / 15.54, 2.0)) + 0.06487 * exp(-pow((V - 4.823) / 51.12, 2.0));
    *_new_hL = hLss + (hL - hLss) * exp(-(dt / thL));
    *_new_mL = mLss + (mL - mLss) * exp(-(dt / tmL));
    const Real INaL = GNaL * (V - ENa) * mL * ((1.0 - fINaLp) * hL + fINaLp * hLp);
    *_new_hLp = hLssp + (hLp - hLssp) * exp(-(dt / thLp));

    // Ito
    const Real fItop = 1.0 / (1.0 + KmCaMK / (CaMKa));
    const Real AiF = 1.0 / (1.0 + exp((V + EKshift - 213.6) / 151.2));
    const Real ass = 1.0 / (1.0 + exp(-(V + EKshift - 14.34) / 14.82));
    const Real assp = 1.0 / (1.0 + exp(-(V + EKshift - 24.34) / 14.82));
    const Real delta_epi = ((celltype == 1.0) ? 1.0 - 0.95 / (1.0 + exp((V + EKshift + 70.0) / 5.0)) : 1.0);
    const Real dti_develop = 1.354 + 0.0001 / (exp((V + EKshift - 167.4) / 15.89) + exp(-(V + EKshift - 12.23) / 0.2154));
    const Real dti_recover = 1.0 - 0.5 / (1.0 + exp((V + EKshift + 70.0) / 20.0));
    const Real iss = 1.0 / (1.0 + exp((V + EKshift + 43.94) / 5.711));
    const Real ta = 1.0515 / (1.0 / (1.2089 * (1.0 + exp(-(V + EKshift - 18.4099) / 29.3814))) + 3.5 / (1.0 + exp((V + EKshift + 100.0) / 29.3814)));
    const Real tiF_b = 4.562 + 1.0 / (0.3933 * exp(-(V + EKshift + 100.0) / 100.0) + 0.08004 * exp((V + EKshift + 50.0) / 16.59));
    const Real tiS_b = 23.62 + 1.0 / (0.001416 * exp(-(V + EKshift + 96.52) / 59.05) + 1.78e-08 * exp((V + EKshift + 114.1) / 8.079));
    const Real AiS = 1.0 - AiF;
    const Real tiF = tiF_b * delta_epi;
    const Real tiS = tiS_b * delta_epi;
    *_new_a = ass + (a - ass) * exp(-(dt / ta));
    *_new_ap = assp + (ap - assp) * exp(-(dt / ta));
    const Real i = AiF * iF + AiS * iS;
    const Real ip = AiF * iFp + AiS * iSp;
    const Real tiFp = dti_develop * dti_recover * tiF;
    const Real tiSp = dti_develop * dti_recover * tiS;
    *_new_iF = iss + (iF - iss) * exp(-(dt / tiF));
    *_new_iS = iss + (iS - iss) * exp(-(dt / tiS));
    const Real Ito = Gto * (V - EK) * ((1.0 - fItop) * a * i + fItop * ap * ip);
    *_new_iFp = iss + (iFp - iss) * exp(-(dt / tiFp));
    *_new_iSp = iss + (iSp - iss) * exp(-(dt / tiSp));

    // ICaL
    const Real Afcaf = 0.3 + 0.6 / (1.0 + exp((V - 10.0) / 10.0));
    const Real Ii = 0.5 * (Nai + Ki + cli + 4.0 * Cai) / 1000.0;
    const Real Iss = 0.5 * (Nass + Kss + cli + 4.0 * Cass) / 1000.0;
    const Real dss = ((V >= 31.4978) ? 1.0 : 1.0763 * exp(-1.007 * exp(-0.0829 * V)));
    const Real fICaLp = 1.0 / (1.0 + KmCaMK / (CaMKa));
    const Real fss = 1.0 / (1.0 + exp((V + 19.58) / 3.696));
    const Real jcass = 1.0 / (1.0 + exp((V + 18.08) / 2.7916));
    const Real km2n = jca * 1.0;
    const Real tfcaf = 7.0 + 1.0 / (0.04 * exp(-(V - 4.0) / 7.0) + 0.04 * exp((V - 4.0) / 7.0));
    const Real tfcas = 100.0 + 1.0 / (0.00012 * exp(-V / 3.0) + 0.00012 * exp(V / 7.0));
    const Real tff = 7.0 + 1.0 / (0.0045 * exp(-(V + 20.0) / 10.0) + 0.0045 * exp((V + 20.0) / 10.0));
    const Real tfs = 1000.0 + 1.0 / (3.5e-05 * exp(-(V + 5.0) / 4.0) + 3.5e-05 * exp((V + 5.0) / 6.0));
    const Real Afcas = 1.0 - Afcaf;
    const Real anca_i = 1.0 / (k2n / (km2n) + pow(1.0 + Kmn / (Cai), 4.0));
    const Real anca_ss = 1.0 / (k2n / (km2n) + pow(1.0 + Kmn / (Cass), 4.0));
    const Real fcass = fss;
    const Real td = offset + 0.6 + 1.0 / (exp(-0.05 * (V + vShift + 6.0)) + exp(0.09 * (V + vShift + 14.0)));
    const Real tfcafp = 2.5 * tfcaf;
    const Real tffp = 2.5 * tff;
    *_new_ff = fss + (ff - fss) * exp(-(dt / tff));
    *_new_fs = fss + (fs - fss) * exp(-(dt / tfs));
    *_new_jca = jcass + (jca - jcass) * exp(-(dt / tjca));
    const Real f = Aff * ff + Afs * fs;
    const Real fca = Afcaf * fcaf + Afcas * fcas;
    const Real fcap = Afcaf * fcafp + Afcas * fcas;
    const Real fp = Aff * ffp + Afs * fs;
    const Real gamma_cai = exp(-constA * 4.0 * (sqrt(Ii) / (1.0 + sqrt(Ii)) - 0.3 * Ii));
    const Real gamma_cass = exp(-constA * 4.0 * (sqrt(Iss) / (1.0 + sqrt(Iss)) - 0.3 * Iss));
    const Real gamma_ki = exp(-constA * (sqrt(Ii) / (1.0 + sqrt(Ii)) - 0.3 * Ii));
    const Real gamma_kss = exp(-constA * (sqrt(Iss) / (1.0 + sqrt(Iss)) - 0.3 * Iss));
    const Real gamma_nai = exp(-constA * (sqrt(Ii) / (1.0 + sqrt(Ii)) - 0.3 * Ii));
    const Real gamma_nass = exp(-constA * (sqrt(Iss) / (1.0 + sqrt(Iss)) - 0.3 * Iss));
    *_new_d = dss + (d - dss) * exp(-(dt / td));
    *_new_fcaf = fcass + (fcaf - fcass) * exp(-(dt / tfcaf));
    *_new_fcafp = fcass + (fcafp - fcass) * exp(-(dt / tfcafp));
    *_new_fcas = fcass + (fcas - fcass) * exp(-(dt / tfcas));
    *_new_ffp = fss + (ffp - fss) * exp(-(dt / tffp));
    *_new_nca_i = nca_i + dt*(anca_i * k2n - nca_i * km2n);
    *_new_nca_ss = nca_ss + dt*(anca_ss * k2n - nca_ss * km2n);
    const Real PhiCaK_i = vffrt * safe_divide(gamma_ki * Ki * exp(vfrt) - gamma_ko * ko, exp(vfrt) - 1.0);
    const Real PhiCaK_ss = vffrt * safe_divide(gamma_kss * Kss * exp(vfrt) - gamma_ko * ko, exp(vfrt) - 1.0);
    const Real PhiCaL_i = 4.0 * vffrt * safe_divide(gamma_cai * Cai * exp(2.0 * vfrt) - gamma_cao * cao, exp(2.0 * vfrt) - 1.0);
    const Real PhiCaL_ss = 4.0 * vffrt * safe_divide(gamma_cass * Cass * exp(2.0 * vfrt) - gamma_cao * cao, exp(2.0 * vfrt) - 1.0);
    const Real PhiCaNa_i = vffrt * safe_divide(gamma_nai * Nai * exp(vfrt) - gamma_nao * nao, exp(vfrt) - 1.0);
    const Real PhiCaNa_ss = vffrt * safe_divide(gamma_nass * Nass * exp(vfrt) - gamma_nao * nao, exp(vfrt) - 1.0);
    const Real ICaK_i = (1.0 - ICaL_fractionSS) * ((1.0 - fICaLp) * PCaK * PhiCaK_i * d * (f * (1.0 - nca_i) + jca * fca * nca_i) + fICaLp * PCaKp * PhiCaK_i * d * (fp * (1.0 - nca_i) + jca * fcap * nca_i));
    const Real ICaK_ss = ICaL_fractionSS * ((1.0 - fICaLp) * PCaK * PhiCaK_ss * d * (f * (1.0 - nca_ss) + jca * fca * nca_ss) + fICaLp * PCaKp * PhiCaK_ss * d * (fp * (1.0 - nca_ss) + jca * fcap * nca_ss));
    const Real ICaL_i = (1.0 - ICaL_fractionSS) * ((1.0 - fICaLp) * PCa * PhiCaL_i * d * (f * (1.0 - nca_i) + jca * fca * nca_i) + fICaLp * PCap * PhiCaL_i * d * (fp * (1.0 - nca_i) + jca * fcap * nca_i));
    const Real ICaL_ss = ICaL_fractionSS * ((1.0 - fICaLp) * PCa * PhiCaL_ss * d * (f * (1.0 - nca_ss) + jca * fca * nca_ss) + fICaLp * PCap * PhiCaL_ss * d * (fp * (1.0 - nca_ss) + jca * fcap * nca_ss));
    const Real ICaNa_i = (1.0 - ICaL_fractionSS) * ((1.0 - fICaLp) * PCaNa * PhiCaNa_i * d * (f * (1.0 - nca_i) + jca * fca * nca_i) + fICaLp * PCaNap * PhiCaNa_i * d * (fp * (1.0 - nca_i) + jca * fcap * nca_i));
    const Real ICaNa_ss = ICaL_fractionSS * ((1.0 - fICaLp) * PCaNa * PhiCaNa_ss * d * (f * (1.0 - nca_ss) + jca * fca * nca_ss) + fICaLp * PCaNap * PhiCaNa_ss * d * (fp * (1.0 - nca_ss) + jca * fcap * nca_ss));
    const Real ICaK = ICaK_ss + ICaK_i;
    const Real ICaL = ICaL_ss + ICaL_i;
    const Real ICaNa = ICaNa_ss + ICaNa_i;

    // IKr
    const Real alpha = 0.1161 * exp(0.299 * vfrt);
    const Real alpha_2 = 0.0578 * exp(0.971 * vfrt);
    const Real alpha_C2ToI = 5.2e-05 * exp(1.525 * vfrt);
    const Real alpha_i = 0.2533 * exp(0.5953 * vfrt);
    const Real beta = 0.2442 * exp(-1.604 * vfrt);
    const Real beta_2 = 0.000349 * exp(-1.062 * vfrt);
    const Real beta_i = 0.06525 * exp(-0.8209 * vfrt);
    const Real beta_ItoC2 = beta_2 * beta_i * alpha_C2ToI / (alpha_2 * alpha_i);
    *_new_C2 = C2 + dt*(alpha * C3 + beta_1 * C1 - (beta + alpha_1) * C2);
    *_new_C3 = C3 + dt*(beta * C2 - alpha * C3);
    *_new_O = O + dt*(alpha_2 * C1 + beta_i * I - (beta_2 + alpha_i) * O);
    const Real IKr = GKr * sqrt(ko / 5.0) * O * (V - EK);
    *_new_C1 = C1 + dt*(alpha_1 * C2 + beta_2 * O + beta_ItoC2 * I - (beta_1 + alpha_2 + alpha_C2ToI) * C1);
    *_new_I = I + dt*(alpha_C2ToI * C1 + alpha_i * O - (beta_ItoC2 + beta_i) * I);

    // IKs
    const Real KsCa = 1.0 + 0.6 / (1.0 + pow(3.8e-05 / (Cai), 1.4));
    const Real txs1 = 817.3 + 1.0 / (0.0002326 * exp((V + 48.28) / 17.8) + 0.001292 * exp(-(V + 210.0) / 230.0));
    const Real txs2 = 1.0 / (0.01 * exp((V - 50.0) / 20.0) + 0.0193 * exp(-(V + 66.54) / 31.0));
    const Real xs1ss = 1.0 / (1.0 + exp(-(V + 11.6) / 8.932));
    const Real xs2ss = xs1ss;
    *_new_xs1 = xs1ss + (xs1 - xs1ss) * exp(-(dt / txs1));
    const Real IKs = GKs * KsCa * xs1 * xs2 * (V - EKs);
    *_new_xs2 = xs2ss + (xs2 - xs2ss) * exp(-(dt / txs2));

    // IK1
    const Real aK1 = 4.094 / (1.0 + exp(0.1217 * (V - EK - 49.934)));
    const Real bK1 = (15.72 * exp(0.0674 * (V - EK - 3.257)) + exp(0.0618 * (V - EK - 594.31))) / (1.0 + exp(-0.1629 * (V - EK + 14.207)));
    const Real K1ss = aK1 / (aK1 + bK1);
    const Real IK1 = GK1 * sqrt(ko / 5.0) * K1ss * (V - EK);

    // INaCa
    const Real allo_i = 1.0 / (1.0 + pow(KmCaAct / (Cai), 2.0));
    const Real allo_ss = 1.0 / (1.0 + pow(KmCaAct / (Cass), 2.0));
    const Real h4_i = 1.0 + Nai / kna1 * (1.0 + Nai / kna2);
    const Real h4_ss = 1.0 + Nass / kna1 * (1.0 + Nass / kna2);
    const Real hca = exp(qca * vfrt);
    const Real hna = exp(qna * vfrt);
    const Real h1_i = 1.0 + Nai / kna3 * (1.0 + hna);
    const Real h1_ss = 1.0 + Nass / kna3 * (1.0 + hna);
    const Real h5_i = Nai * Nai / (h4_i * kna1 * kna2);
    const Real h5_ss = Nass * Nass / (h4_ss * kna1 * kna2);
    const Real h6_i = 1.0 / (h4_i);
    const Real h6_ss = 1.0 / (h4_ss);
    const Real h7_i = 1.0 + nao / kna3 * (1.0 + 1.0 / (hna));
    const Real h7_ss = 1.0 + nao / kna3 * (1.0 + 1.0 / (hna));
    const Real h2_i = Nai * hna / (kna3 * h1_i);
    const Real h2_ss = Nass * hna / (kna3 * h1_ss);
    const Real h3_i = 1.0 / (h1_i);
    const Real h3_ss = 1.0 / (h1_ss);
    const Real h8_i = nao / (kna3 * hna * h7_i);
    const Real h8_ss = nao / (kna3 * hna * h7_ss);
    const Real h9_i = 1.0 / (h7_i);
    const Real h9_ss = 1.0 / (h7_ss);
    const Real k6_i = h6_i * Cai * kcaon;
    const Real k6_ss = h6_ss * Cass * kcaon;
    const Real k3p_i = h9_i * wca;
    const Real k3p_ss = h9_ss * wca;
    const Real k3pp_i = h8_i * wnaca;
    const Real k3pp_ss = h8_ss * wnaca;
    const Real k4p_i = h3_i * wca / (hca);
    const Real k4p_ss = h3_ss * wca / (hca);
    const Real k4pp_i = h2_i * wnaca;
    const Real k4pp_ss = h2_ss * wnaca;
    const Real k7_i = h5_i * h2_i * wna;
    const Real k7_ss = h5_ss * h2_ss * wna;
    const Real k8_i = h8_i * h11_i * wna;
    const Real k8_ss = h8_ss * h11_ss * wna;
    const Real k3_i = k3p_i + k3pp_i;
    const Real k3_ss = k3p_ss + k3pp_ss;
    const Real k4_i = k4p_i + k4pp_i;
    const Real k4_ss = k4p_ss + k4pp_ss;
    const Real x1_i = k2_i * k4_i * (k7_i + k6_i) + k5_i * k7_i * (k2_i + k3_i);
    const Real x1_ss = k2_ss * k4_ss * (k7_ss + k6_ss) + k5_ss * k7_ss * (k2_ss + k3_ss);
    const Real x2_i = k1_i * k7_i * (k4_i + k5_i) + k4_i * k6_i * (k1_i + k8_i);
    const Real x2_ss = k1_ss * k7_ss * (k4_ss + k5_ss) + k4_ss * k6_ss * (k1_ss + k8_ss);
    const Real x3_i = k1_i * k3_i * (k7_i + k6_i) + k8_i * k6_i * (k2_i + k3_i);
    const Real x3_ss = k1_ss * k3_ss * (k7_ss + k6_ss) + k8_ss * k6_ss * (k2_ss + k3_ss);
    const Real x4_i = k2_i * k8_i * (k4_i + k5_i) + k3_i * k5_i * (k1_i + k8_i);
    const Real x4_ss = k2_ss * k8_ss * (k4_ss + k5_ss) + k3_ss * k5_ss * (k1_ss + k8_ss);
    const Real E1_i = x1_i / (x1_i + x2_i + x3_i + x4_i);
    const Real E1_ss = x1_ss / (x1_ss + x2_ss + x3_ss + x4_ss);
    const Real E2_i = x2_i / (x1_i + x2_i + x3_i + x4_i);
    const Real E2_ss = x2_ss / (x1_ss + x2_ss + x3_ss + x4_ss);
    const Real E3_i = x3_i / (x1_i + x2_i + x3_i + x4_i);
    const Real E3_ss = x3_ss / (x1_ss + x2_ss + x3_ss + x4_ss);
    const Real E4_i = x4_i / (x1_i + x2_i + x3_i + x4_i);
    const Real E4_ss = x4_ss / (x1_ss + x2_ss + x3_ss + x4_ss);
    const Real JncxCa_i = E2_i * k2_i - E1_i * k1_i;
    const Real JncxCa_ss = E2_ss * k2_ss - E1_ss * k1_ss;
    const Real JncxNa_i = 3.0 * (E4_i * k7_i - E1_i * k8_i) + E3_i * k4pp_i - E2_i * k3pp_i;
    const Real JncxNa_ss = 3.0 * (E4_ss * k7_ss - E1_ss * k8_ss) + E3_ss * k4pp_ss - E2_ss * k3pp_ss;
    const Real INaCa_i = (1.0 - INaCa_fractionSS) * Gncx * allo_i * (zna * JncxNa_i + zca * JncxCa_i);
    const Real INaCa_ss = INaCa_fractionSS * Gncx * allo_ss * (zna * JncxNa_ss + zca * JncxCa_ss);

    // INaK
    const Real Knai = Knai0 * exp(delta * vfrt / 3.0);
    const Real Knao = Knao0 * exp((1.0 - delta) * vfrt / 3.0);
    const Real P = eP / (1.0 + H / Khp + Nai / Knap + Ki / Kxkur);
    const Real a1 = k1p * pow(Nai / (Knai), 3.0) / (pow(1.0 + Nai / (Knai), 3.0) + pow(1.0 + Ki / Kki, 2.0) - 1.0);
    const Real a3 = k3p * pow(ko / Kko, 2.0) / (pow(1.0 + nao / (Knao), 3.0) + pow(1.0 + ko / Kko, 2.0) - 1.0);
    const Real b2 = k2m * pow(nao / (Knao), 3.0) / (pow(1.0 + nao / (Knao), 3.0) + pow(1.0 + ko / Kko, 2.0) - 1.0);
    const Real b3 = k3m * P * H / (1.0 + MgATP / Kmgatp);
    const Real b4 = k4m * pow(Ki / Kki, 2.0) / (pow(1.0 + Nai / (Knai), 3.0) + pow(1.0 + Ki / Kki, 2.0) - 1.0);
    const Real x1 = a4 * a1 * a2 + b2 * b4 * b3 + a2 * b4 * b3 + b3 * a1 * a2;
    const Real x2 = b2 * b1 * b4 + a1 * a2 * a3 + a3 * b1 * b4 + a2 * a3 * b4;
    const Real x3 = a2 * a3 * a4 + b3 * b2 * b1 + b2 * b1 * a4 + a3 * a4 * b1;
    const Real x4 = b4 * b3 * b2 + a3 * a4 * a1 + b2 * a4 * a1 + b3 * b2 * a1;
    const Real E1 = x1 / (x1 + x2 + x3 + x4);
    const Real E2 = x2 / (x1 + x2 + x3 + x4);
    const Real E3 = x3 / (x1 + x2 + x3 + x4);
    const Real E4 = x4 / (x1 + x2 + x3 + x4);
    const Real JnakK = 2.0 * (E4 * b1 - E3 * a1);
    const Real JnakNa = 3.0 * (E1 * a3 - E2 * b3);
    const Real INaK = Pnak * (zna * JnakNa + zk * JnakK);

    // IKb
    const Real xkb = 1.0 / (1.0 + exp(-(V - 10.8968) / 23.9871));
    const Real IKb = GKb * xkb * (V - EK);

    // INab
    const Real INab = PNab * vffrt * safe_divide(Nai * exp(vfrt) - nao, exp(vfrt) - 1.0);

    // ICab
    const Real ICab = PCab * 4.0 * vffrt * safe_divide(gamma_cai * Cai * exp(2.0 * vfrt) - gamma_cao * cao, exp(2.0 * vfrt) - 1.0);

    // ICl
    const Real IClCa_junc = Fjunc * GClCa / (1.0 + KdClCa / (Cass)) * (V - ECl);
    const Real IClCa_sl = (1.0 - Fjunc) * GClCa / (1.0 + KdClCa / (Cai)) * (V - ECl);
    const Real IClb = GClb * (V - ECl);
    const Real IClCa = IClCa_junc + IClCa_sl;

    // ryr
    const Real fJrelp = 1.0 / (1.0 + KmCaMK / (CaMKa));
    const Real Jrel = Jrel_b * ((1.0 - fJrelp) * Jrel_np + fJrelp * Jrel_p);
    const Real tau_rel_b = bt / (1.0 + 0.0123 / (Cajsr));
    const Real Jrel_inf_b = -a_rel * ICaL_ss / 1.0 / (1.0 + pow(cajsr_half / (Cajsr), 8.0));
    const Real tau_rel = ((tau_rel_b < 0.001) ? 0.001 : tau_rel_b);
    const Real tau_relp_b = btp / (1.0 + 0.0123 / (Cajsr));
    const Real Jrel_inf = ((celltype == 2.0) ? Jrel_inf_b * 1.7 : Jrel_inf_b);
    const Real Jrel_infp_b = -a_relp * ICaL_ss / 1.0 / (1.0 + pow(cajsr_half / (Cajsr), 8.0));
    const Real tau_relp = ((tau_relp_b < 0.001) ? 0.001 : tau_relp_b);
    *_new_Jrel_np = Jrel_inf + (Jrel_np - Jrel_inf) * exp(-(dt / tau_rel));
    const Real Jrel_infp = ((celltype == 2.0) ? Jrel_infp_b * 1.7 : Jrel_infp_b);
    *_new_Jrel_p = Jrel_infp + (Jrel_p - Jrel_infp) * exp(-(dt / tau_relp));

    // *remaining*
    *_new_V = V + dt*(-(INa + INaL + Ito + ICaL + ICaNa + ICaK + IKr + IKs + IK1 + INaCa_i + INaCa_ss + INaK + INab + IKb + IpCa + ICab + IClCa + IClb + I_katp) + _diffuse_V);
    *_new_Cai = Cai + dt*(Bcai * (-(ICaL_i + IpCa + ICab - 2.0 * INaCa_i) * Acap / (2.0 * F * vmyo) - Jup * vnsr / vmyo + Jdiff * vss / vmyo));
    *_new_Cajsr = Cajsr + dt*(Bcajsr * (Jtr - Jrel));
    *_new_Cass = Cass + dt*(Bcass * (-(ICaL_ss - 2.0 * INaCa_ss) * Acap / (2.0 * F * vss) + Jrel * vjsr / vss - Jdiff));
    *_new_Ki = Ki + dt*(-(Ito + IKr + IKs + IK1 + IKb + I_katp - 2.0 * INaK + ICaK_i) * Acap / (F * vmyo) + JdiffK * vss / vmyo);
    *_new_Kss = Kss + dt*(-ICaK_ss * Acap / (F * vss) - JdiffK);
    *_new_Nai = Nai + dt*(-(INa + INaL + 3.0 * INaCa_i + ICaNa_i + 3.0 * INaK + INab) * Acap / (F * vmyo) + JdiffNa * vss / vmyo);
    *_new_Nass = Nass + dt*(-(ICaNa_ss + 3.0 * INaCa_ss) * Acap / (F * vss) - JdiffNa);


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
    initial conditions:
      endo:
        V: -88.7638
        CaMKt: 0.0111
        Nai: 12.1025
        Nass: 12.1029
        Ki: 142.3002
        Kss: 142.3002
        Cass: 7.0305e-05
        Cansr: 1.5211
        Cajsr: 1.5214
        Cai: 8.1583e-05
        m: 0.00080572
        h: 0.8286
        j: 0.8284
        hp: 0.6707
        jp: 0.8281
        mL: 0.0001629
        hL: 0.5255
        hLp: 0.2872
        a: 0.00095098
        iF: 0.9996
        iS: 0.5936
        ap: 0.00048454
        iFp: 0.9996
        iSp: 0.6538
        d: 8.1084e-09
        ff: 1.0
        fs: 0.939
        fcaf: 1.0
        fcas: 0.9999
        jca: 1.0
        ffp: 1.0
        fcafp: 1.0
        nca_ss: 0.00066462
        nca_i: 0.0012
        C1: 0.00070344
        C2: 0.00085109
        C3: 0.9981
        I: 1.3289e-05
        O: 0.00037585
        xs1: 0.248
        xs2: 0.00017707
        Jrel_np: 1.6129e-22
        Jrel_p: 1.2475e-20
      epi:
        V: -89.14
        CaMKt: 0.0129
        Nai: 12.8363
        Nass: 12.8366
        Ki: 142.6951
        Kss: 142.6951
        Cass: 5.7672e-05
        Cansr: 1.8119
        Cajsr: 1.8102
        Cai: 6.6309e-05
        m: 0.00074303
        h: 0.836
        j: 0.8359
        hp: 0.6828
        jp: 0.8357
        mL: 0.00015166
        hL: 0.5401
        hLp: 0.3034
        a: 0.00092716
        iF: 0.9996
        iS: 0.9996
        ap: 0.0004724
        iFp: 0.9996
        iSp: 0.9996
        d: 0.0
        ff: 1.0
        fs: 0.9485
        fcaf: 1.0
        fcas: 0.9999
        jca: 1.0
        ffp: 1.0
        fcafp: 1.0
        nca_ss: 0.00030853
        nca_i: 0.00053006
        C1: 0.00067941
        C2: 0.00082869
        C3: 0.9982
        I: 9.5416e-06
        O: 0.00027561
        xs1: 0.2309
        xs2: 0.00016975
        Jrel_np: 2.8189e-24
        Jrel_p: 0.0
      mid:
        V: -89.1704
        CaMKt: 0.0192
        Nai: 15.0038
        Nass: 15.0043
        Ki: 143.0403
        Kss: 143.0402
        Cass: 6.5781e-05
        Cansr: 1.9557
        Cajsr: 1.9593
        Cai: 8.166e-05
        m: 0.00073818
        h: 0.8365
        j: 0.8363
        hp: 0.6838
        jp: 0.8358
        mL: 0.00015079
        hL: 0.5327
        hLp: 0.2834
        a: 0.00092527
        iF: 0.9996
        iS: 0.5671
        ap: 0.00047143
        iFp: 0.9996
        iSp: 0.6261
        d: 0.0
        ff: 1.0
        fs: 0.92
        fcaf: 1.0
        fcas: 0.9998
        jca: 1.0
        ffp: 1.0
        fcafp: 1.0
        nca_ss: 0.00051399
        nca_i: 0.0012
        C1: 0.0006956
        C2: 0.00082672
        C3: 0.9979
        I: 1.8784e-05
        O: 0.00054206
        xs1: 0.2653
        xs2: 0.00016921
        Jrel_np: 0.0
        Jrel_p: 0.0
    parameter sets:
      endo:
        CaMKo: 0.05
        KmCaM: 0.0015
        KmCaMK: 0.15
        aCaMK: 0.05
        bCaMK: 0.00068
        GpCa: 0.0005
        KmCap: 0.0005
        L: 0.01
        rad: 0.0011
        Ageo: 7.667880000000002e-05
        vcell: 3.799400000000001e-05
        Acap: 0.00015335760000000003
        vjsr: 1.8237120000000002e-07
        vmyo: 2.583592000000001e-05
        vnsr: 2.0972688000000006e-06
        vss: 7.598800000000002e-07
        tauCa: 0.2
        tauK: 2.0
        tauNa: 2.0
        celltype: 0.0
        cao: 1.8
        clo: 150.0
        ko: 5.0
        nao: 140.0
        F: 96485.0
        R: 8314.0
        T: 310.0
        zca: 2.0
        zcl: -1.0
        zk: 1.0
        zna: 1.0
        Jup_b: 1.0
        upScale: 1.0
        BSLmax: 1.124
        BSRmax: 0.047
        KmBSL: 0.0087
        KmBSR: 0.00087
        cli: 24.0
        cmdnmax_b: 0.05
        csqnmax: 10.0
        kmcmdn: 0.00238
        kmcsqn: 0.8
        kmtrpn: 0.0005
        trpnmax: 0.07
        cmdnmax: 0.05
        ECl: -48.95253676506265
        PKNa: 0.01833
        A_atp: 2.0
        K_atp: 0.25
        K_o_n: 5.0
        fkatp: 0.0
        gkatp: 4.3195
        akik: 1.0
        bkik: 0.015384615384615385
        GNa: 11.7802
        GNaL_b: 0.0279
        thL: 200.0
        GNaL: 0.0279
        thLp: 600.0
        EKshift: 0.0
        Gto_b: 0.16
        Gto: 0.16
        Aff: 0.6
        ICaL_fractionSS: 0.8
        Io: 0.15109999999999998
        Kmn: 0.002
        PCa_b: 8.3757e-05
        dielConstant: 74.0
        k2n: 500.0
        offset: 0.0
        tjca: 75.0
        vShift: 0.0
        Afs: 0.4
        PCa: 8.3757e-05
        constA: 0.5238190247282047
        PCaK: 2.99347518e-08
        PCaNa: 1.0469625000000001e-07
        PCap: 9.213270000000001e-05
        gamma_cao: 0.6117017520062547
        gamma_ko: 0.8843718923169582
        gamma_nao: 0.8843718923169582
        PCaKp: 3.292822698000001e-08
        PCaNap: 1.1516587500000002e-07
        GKr_b: 0.0321
        alpha_1: 0.154375
        beta_1: 0.1911
        GKr: 0.0321
        GKs_b: 0.0011
        GKs: 0.0011
        GK1_b: 0.6992
        GK1: 0.6992
        Gncx_b: 0.0034
        INaCa_fractionSS: 0.35
        KmCaAct: 0.00015
        kasymm: 12.5
        kcaoff: 5000.0
        kcaon: 1500000.0
        kna1: 15.0
        kna2: 5.0
        kna3: 88.12
        qca: 0.167
        qna: 0.5224
        wca: 60000.0
        wna: 60000.0
        wnaca: 5000.0
        Gncx: 0.0034
        h10_i: 284.1666666666667
        h10_ss: 284.1666666666667
        k2_i: 5000.0
        k2_ss: 5000.0
        k5_i: 5000.0
        k5_ss: 5000.0
        h11_i: 0.9196480938416423
        h11_ss: 0.9196480938416423
        h12_i: 0.003519061583577712
        h12_ss: 0.003519061583577712
        k1_i: 9501.466275659823
        k1_ss: 9501.466275659823
        H: 1.0e-07
        Khp: 1.698e-07
        Kki: 0.5
        Kko: 0.3582
        Kmgatp: 1.698e-07
        Knai0: 9.073
        Knao0: 27.78
        Knap: 224.0
        Kxkur: 292.0
        MgADP: 0.05
        MgATP: 9.8
        Pnak_b: 15.4509
        delta: -0.155
        eP: 4.2
        k1m: 182.4
        k1p: 949.5
        k2m: 39.4
        k2p: 687.2
        k3m: 79300.0
        k3p: 1899.0
        k4m: 40.0
        k4p: 639.0
        Pnak: 15.4509
        a2: 687.2
        a4: 638.9999889283472
        b1: 9.120000000000001
        GKb_b: 0.0189
        GKb: 0.0189
        PNab: 1.9239e-09
        PCab: 5.9194e-08
        Fjunc: 1.0
        GClCa: 0.2843
        GClb: 0.00198
        KdClCa: 0.1
        Jrel_b: 1.5378
        bt: 4.75
        cajsr_half: 1.7
        a_rel: 2.375
        btp: 5.9375
        a_relp: 2.96875
      epi:
        CaMKo: 0.05
        KmCaM: 0.0015
        KmCaMK: 0.15
        aCaMK: 0.05
        bCaMK: 0.00068
        GpCa: 0.0005
        KmCap: 0.0005
        L: 0.01
        rad: 0.0011
        Ageo: 7.667880000000002e-05
        vcell: 3.799400000000001e-05
        Acap: 0.00015335760000000003
        vjsr: 1.8237120000000002e-07
        vmyo: 2.583592000000001e-05
        vnsr: 2.0972688000000006e-06
        vss: 7.598800000000002e-07
        tauCa: 0.2
        tauK: 2.0
        tauNa: 2.0
        celltype: 1.0
        cao: 1.8
        clo: 150.0
        ko: 5.0
        nao: 140.0
        F: 96485.0
        R: 8314.0
        T: 310.0
        zca: 2.0
        zcl: -1.0
        zk: 1.0
        zna: 1.0
        Jup_b: 1.0
        upScale: 1.3
        BSLmax: 1.124
        BSRmax: 0.047
        KmBSL: 0.0087
        KmBSR: 0.00087
        cli: 24.0
        cmdnmax_b: 0.05
        csqnmax: 10.0
        kmcmdn: 0.00238
        kmcsqn: 0.8
        kmtrpn: 0.0005
        trpnmax: 0.07
        cmdnmax: 0.065
        ECl: -48.95253676506265
        PKNa: 0.01833
        A_atp: 2.0
        K_atp: 0.25
        K_o_n: 5.0
        fkatp: 0.0
        gkatp: 4.3195
        akik: 1.0
        bkik: 0.015384615384615385
        GNa: 11.7802
        GNaL_b: 0.0279
        thL: 200.0
        GNaL: 0.01674
        thLp: 600.0
        EKshift: 0.0
        Gto_b: 0.16
        Gto: 0.32
        Aff: 0.6
        ICaL_fractionSS: 0.8
        Io: 0.15109999999999998
        Kmn: 0.002
        PCa_b: 8.3757e-05
        dielConstant: 74.0
        k2n: 500.0
        offset: 0.0
        tjca: 75.0
        vShift: 0.0
        Afs: 0.4
        PCa: 0.00010050840000000001
        constA: 0.5238190247282047
        PCaK: 3.5921702160000004e-08
        PCaNa: 1.2563550000000001e-07
        PCap: 0.00011055924000000001
        gamma_cao: 0.6117017520062547
        gamma_ko: 0.8843718923169582
        gamma_nao: 0.8843718923169582
        PCaKp: 3.951387237600001e-08
        PCaNap: 1.3819905000000003e-07
        GKr_b: 0.0321
        alpha_1: 0.154375
        beta_1: 0.1911
        GKr: 0.041729999999999996
        GKs_b: 0.0011
        GKs: 0.00154
        GK1_b: 0.6992
        GK1: 0.83904
        Gncx_b: 0.0034
        INaCa_fractionSS: 0.35
        KmCaAct: 0.00015
        kasymm: 12.5
        kcaoff: 5000.0
        kcaon: 1500000.0
        kna1: 15.0
        kna2: 5.0
        kna3: 88.12
        qca: 0.167
        qna: 0.5224
        wca: 60000.0
        wna: 60000.0
        wnaca: 5000.0
        Gncx: 0.0037400000000000003
        h10_i: 284.1666666666667
        h10_ss: 284.1666666666667
        k2_i: 5000.0
        k2_ss: 5000.0
        k5_i: 5000.0
        k5_ss: 5000.0
        h11_i: 0.9196480938416423
        h11_ss: 0.9196480938416423
        h12_i: 0.003519061583577712
        h12_ss: 0.003519061583577712
        k1_i: 9501.466275659823
        k1_ss: 9501.466275659823
        H: 1.0e-07
        Khp: 1.698e-07
        Kki: 0.5
        Kko: 0.3582
        Kmgatp: 1.698e-07
        Knai0: 9.073
        Knao0: 27.78
        Knap: 224.0
        Kxkur: 292.0
        MgADP: 0.05
        MgATP: 9.8
        Pnak_b: 15.4509
        delta: -0.155
        eP: 4.2
        k1m: 182.4
        k1p: 949.5
        k2m: 39.4
        k2p: 687.2
        k3m: 79300.0
        k3p: 1899.0
        k4m: 40.0
        k4p: 639.0
        Pnak: 13.90581
        a2: 687.2
        a4: 638.9999889283472
        b1: 9.120000000000001
        GKb_b: 0.0189
        GKb: 0.01134
        PNab: 1.9239e-09
        PCab: 5.9194e-08
        Fjunc: 1.0
        GClCa: 0.2843
        GClb: 0.00198
        KdClCa: 0.1
        Jrel_b: 1.5378
        bt: 4.75
        cajsr_half: 1.7
        a_rel: 2.375
        btp: 5.9375
        a_relp: 2.96875
      mid:
        CaMKo: 0.05
        KmCaM: 0.0015
        KmCaMK: 0.15
        aCaMK: 0.05
        bCaMK: 0.00068
        GpCa: 0.0005
        KmCap: 0.0005
        L: 0.01
        rad: 0.0011
        Ageo: 7.667880000000002e-05
        vcell: 3.799400000000001e-05
        Acap: 0.00015335760000000003
        vjsr: 1.8237120000000002e-07
        vmyo: 2.583592000000001e-05
        vnsr: 2.0972688000000006e-06
        vss: 7.598800000000002e-07
        tauCa: 0.2
        tauK: 2.0
        tauNa: 2.0
        celltype: 2.0
        cao: 1.8
        clo: 150.0
        ko: 5.0
        nao: 140.0
        F: 96485.0
        R: 8314.0
        T: 310.0
        zca: 2.0
        zcl: -1.0
        zk: 1.0
        zna: 1.0
        Jup_b: 1.0
        upScale: 1.0
        BSLmax: 1.124
        BSRmax: 0.047
        KmBSL: 0.0087
        KmBSR: 0.00087
        cli: 24.0
        cmdnmax_b: 0.05
        csqnmax: 10.0
        kmcmdn: 0.00238
        kmcsqn: 0.8
        kmtrpn: 0.0005
        trpnmax: 0.07
        cmdnmax: 0.05
        ECl: -48.95253676506265
        PKNa: 0.01833
        A_atp: 2.0
        K_atp: 0.25
        K_o_n: 5.0
        fkatp: 0.0
        gkatp: 4.3195
        akik: 1.0
        bkik: 0.015384615384615385
        GNa: 11.7802
        GNaL_b: 0.0279
        thL: 200.0
        GNaL: 0.0279
        thLp: 600.0
        EKshift: 0.0
        Gto_b: 0.16
        Gto: 0.32
        Aff: 0.6
        ICaL_fractionSS: 0.8
        Io: 0.15109999999999998
        Kmn: 0.002
        PCa_b: 8.3757e-05
        dielConstant: 74.0
        k2n: 500.0
        offset: 0.0
        tjca: 75.0
        vShift: 0.0
        Afs: 0.4
        PCa: 0.000167514
        constA: 0.5238190247282047
        PCaK: 5.98695036e-08
        PCaNa: 2.0939250000000001e-07
        PCap: 0.00018426540000000003
        gamma_cao: 0.6117017520062547
        gamma_ko: 0.8843718923169582
        gamma_nao: 0.8843718923169582
        PCaKp: 6.585645396000002e-08
        PCaNap: 2.3033175000000005e-07
        GKr_b: 0.0321
        alpha_1: 0.154375
        beta_1: 0.1911
        GKr: 0.025679999999999998
        GKs_b: 0.0011
        GKs: 0.0011
        GK1_b: 0.6992
        GK1: 0.9089600000000001
        Gncx_b: 0.0034
        INaCa_fractionSS: 0.35
        KmCaAct: 0.00015
        kasymm: 12.5
        kcaoff: 5000.0
        kcaon: 1500000.0
        kna1: 15.0
        kna2: 5.0
        kna3: 88.12
        qca: 0.167
        qna: 0.5224
        wca: 60000.0
        wna: 60000.0
        wnaca: 5000.0
        Gncx: 0.0047599999999999995
        h10_i: 284.1666666666667
        h10_ss: 284.1666666666667
        k2_i: 5000.0
        k2_ss: 5000.0
        k5_i: 5000.0
        k5_ss: 5000.0
        h11_i: 0.9196480938416423
        h11_ss: 0.9196480938416423
        h12_i: 0.003519061583577712
        h12_ss: 0.003519061583577712
        k1_i: 9501.466275659823
        k1_ss: 9501.466275659823
        H: 1.0e-07
        Khp: 1.698e-07
        Kki: 0.5
        Kko: 0.3582
        Kmgatp: 1.698e-07
        Knai0: 9.073
        Knao0: 27.78
        Knap: 224.0
        Kxkur: 292.0
        MgADP: 0.05
        MgATP: 9.8
        Pnak_b: 15.4509
        delta: -0.155
        eP: 4.2
        k1m: 182.4
        k1p: 949.5
        k2m: 39.4
        k2p: 687.2
        k3m: 79300.0
        k3p: 1899.0
        k4m: 40.0
        k4p: 639.0
        Pnak: 10.81563
        a2: 687.2
        a4: 638.9999889283472
        b1: 9.120000000000001
        GKb_b: 0.0189
        GKb: 0.0189
        PNab: 1.9239e-09
        PCab: 5.9194e-08
        Fjunc: 1.0
        GClCa: 0.2843
        GClb: 0.00198
        KdClCa: 0.1
        Jrel_b: 1.5378
        bt: 4.75
        cajsr_half: 1.7
        a_rel: 2.375
        btp: 5.9375
        a_relp: 2.96875

