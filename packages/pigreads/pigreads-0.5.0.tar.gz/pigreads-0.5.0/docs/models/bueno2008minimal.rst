.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.h``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.

Bueno-Orovio et al. 2008
========================

**Key:** ``bueno2008minimal``

This cardiac electrophysiology model by Bueno-Orovio, Cherry, and Fenton is a
four-variable extension of the model by Fenton & Karma 1998. It was designed
to reproduce action potential shapes and the restitution characteristics of
their duration and of conduction velocity.

The model comes with parameter sets for the epi- (default) and
endocardium of the human ventricule, as well as a midwall parameter sets.
Additionally, the authors provide parameter sets emulating the models by
Priebe & Beuckelmann 1998 (PB) and Ten Tusscher et al. 2004 (TNNP).

References
----------
1. https://doi.org/10.1016/j.jtbi.2008.03.029
2. https://doi.org/10.1063/1.166311
3. https://doi.org/10.1161/01.RES.82.11.1206
4. https://doi.org/10.1152/ajpheart.00794.2003

Variables
---------
0. ``u = 0.0``
1. ``v = 1.0``
2. ``w = 1.0``
3. ``s = 0.0``

Parameters
----------
- ``diffusivity_u = 0.1171``
- ``u0 = 0``
- ``u_u = 1.55``
- ``theta_v = 0.3``
- ``theta_w = 0.13``
- ``theta_vm = 0.006``
- ``theta_0 = 0.006``
- ``tau_v1m = 60``
- ``tau_v2m = 1150``
- ``tau_vp = 1.4506``
- ``tau_w1m = 60``
- ``tau_w2m = 15``
- ``k_wm = 65``
- ``u_wm = 0.03``
- ``tau_wp = 200``
- ``tau_fi = 0.11``
- ``tau_o1 = 400``
- ``tau_o2 = 6``
- ``tau_so1 = 30.0181``
- ``tau_so2 = 0.9957``
- ``k_so = 2.0458``
- ``u_so = 0.65``
- ``tau_s1 = 2.7342``
- ``tau_s2 = 16``
- ``k_s = 2.0994``
- ``u_s = 0.9087``
- ``tau_si = 1.8875``
- ``tau_winf = 0.07``
- ``w_infstar = 0.94``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    const Real Hthvm = (u - theta_vm > 0) ? 1 : 0;
    const Real Hthw = (u - theta_w > 0) ? 1 : 0;
    const Real Hth0 = (u - theta_0 > 0) ? 1 : 0;
    const Real Hthv = (u - theta_v > 0) ? 1 : 0;

    const Real Hkm = (1 + tanh(k_wm * (u-u_wm))) / 2;
    const Real Hko = (1 + tanh(k_so * (u-u_so))) / 2;
    const Real Hks = (1 + tanh(k_s * (u-u_s))) / 2;

    const Real tau_vm = tau_v1m + Hthvm*(tau_v2m-tau_v1m);
    const Real tau_wm = tau_w1m + (tau_w2m-tau_w1m)*Hkm;
    const Real tau_so = tau_so1 + (tau_so2-tau_so1)*Hko;
    const Real tau_s = tau_s1 + Hthw*(tau_s2-tau_s1);
    const Real tau_o = tau_o1 + Hth0*(tau_o2-tau_o1);

    const Real vinf = 1 - Hthvm;
    const Real winf = (1-Hth0)*(1-u/tau_winf) + Hth0*w_infstar;

    const Real Jfi = -v*Hthv*(u-theta_v)*(u_u-u)/tau_fi;
    const Real Jso = (theta_w>u) ? (u-u0)/tau_o : 1.0/tau_so;
    const Real Jsi = -Hthw*w*s/tau_si;

    const Real U = -(Jfi + Jso + Jsi);
    const Real V = (theta_v>u) ? (vinf-v)/tau_vm : - v/tau_vp;
    const Real W = (theta_w>u) ? (winf-w)/tau_wm : - w/tau_wp;
    const Real S = (Hks-s)/tau_s;

    *_new_u = u + dt * (U + _diffuse_u);
    *_new_v = v + dt * V;
    *_new_w = w + dt * W;
    *_new_s = s + dt * S;


.. raw:: html

    </details>

Additional metadata
-------------------

.. code-block:: yaml

    keywords:
    - excitable media
    - electrophysiology
    - heart
    - generic
    parameter sets:
      EPI:
        u0: 0
        u_u: 1.55
        theta_v: 0.3
        theta_w: 0.13
        theta_vm: 0.006
        theta_0: 0.006
        tau_v1m: 60
        tau_v2m: 1150
        tau_vp: 1.4506
        tau_w1m: 60
        tau_w2m: 15
        k_wm: 65
        u_wm: 0.03
        tau_wp: 200
        tau_fi: 0.11
        tau_o1: 400
        tau_o2: 6
        tau_so1: 30.0181
        tau_so2: 0.9957
        k_so: 2.0458
        u_so: 0.65
        tau_s1: 2.7342
        tau_s2: 16
        k_s: 2.0994
        u_s: 0.9087
        tau_si: 1.8875
        tau_winf: 0.07
        w_infstar: 0.94
      ENDO:
        u0: 0
        u_u: 1.56
        theta_v: 0.3
        theta_w: 0.13
        theta_vm: 0.2
        theta_0: 0.006
        tau_v1m: 75
        tau_v2m: 10
        tau_vp: 1.4506
        tau_w1m: 6
        tau_w2m: 140
        k_wm: 200
        u_wm: 0.016
        tau_wp: 280
        tau_fi: 0.1
        tau_o1: 470
        tau_o2: 6
        tau_so1: 40
        tau_so2: 1.2
        k_so: 2
        u_so: 0.65
        tau_s1: 2.7342
        tau_s2: 2
        k_s: 2.0994
        u_s: 0.9087
        tau_si: 2.9013
        tau_winf: 0.0273
        w_infstar: 0.78
      Midwall:
        u0: 0
        u_u: 1.61
        theta_v: 0.3
        theta_w: 0.13
        theta_vm: 0.1
        theta_0: 0.005
        tau_v1m: 80
        tau_v2m: 1.4506
        tau_vp: 1.4506
        tau_w1m: 70
        tau_w2m: 8
        k_wm: 200
        u_wm: 0.016
        tau_wp: 280
        tau_fi: 0.078
        tau_o1: 410
        tau_o2: 7
        tau_so1: 91
        tau_so2: 0.8
        k_so: 2.1
        u_so: 0.6
        tau_s1: 2.7342
        tau_s2: 4
        k_s: 2.0994
        u_s: 0.9087
        tau_si: 3.3849
        tau_winf: 0.01
        w_infstar: 0.5
      PB:
        u0: 0
        u_u: 1.45
        theta_v: 0.35
        theta_w: 0.13
        theta_vm: 0.175
        theta_0: 0.006
        tau_v1m: 10
        tau_v2m: 1150
        tau_vp: 1.4506
        tau_w1m: 140
        tau_w2m: 6.25
        k_wm: 65
        u_wm: 0.015
        tau_wp: 326
        tau_fi: 0.105
        tau_o1: 400
        tau_o2: 6
        tau_so1: 30.0181
        tau_so2: 0.9957
        k_so: 2.0458
        u_so: 0.65
        tau_s1: 2.7342
        tau_s2: 16
        k_s: 2.0994
        u_s: 0.9087
        tau_si: 1.8875
        tau_winf: 0.175
        w_infstar: 0.9
      TNNP:
        u0: 0
        u_u: 1.58
        theta_v: 0.3
        theta_w: 0.015
        theta_vm: 0.015
        theta_0: 0.006
        tau_v1m: 60
        tau_v2m: 1150
        tau_vp: 1.4506
        tau_w1m: 70
        tau_w2m: 20
        k_wm: 65
        u_wm: 0.03
        tau_wp: 280
        tau_fi: 0.11
        tau_o1: 6
        tau_o2: 6
        tau_so1: 43
        tau_so2: 0.2
        k_so: 2
        u_so: 0.65
        tau_s1: 2.7342
        tau_s2: 3
        k_s: 2.0994
        u_s: 0.9087
        tau_si: 2.8723
        tau_winf: 0.07
        w_infstar: 0.94

