# AUTOMATICALLY GENERATED FILE!
# Edit the templates ``*.jinja``, the header files ``*.h``, or the model
# definitions in ``models/`` instead, then run the ``prepare.py``
# script in the main directory.

HEADER: str = r"""
#define Size ulong
#define Int int

#ifdef DOUBLE_PRECISION

#pragma OPENCL EXTENSION cl_khr_fp64 : enable
#define Real double
#define REAL(x) x
#define VERY_SMALL_NUMBER 1e-20

#else // single precision

#define Real float
#define REAL(x) x##f
#define VERY_SMALL_NUMBER 1e-10f

#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wmacro-redefined"
#define M_PI M_PI_F
#define exp(x) native_exp((Real)(x))
#define log(x) native_log((Real)(x))
#define sqrt(x) native_sqrt((Real)(x))
inline Real pow_(Real base, Real exp) { return pow(base, exp); }
#define pow(x, y) pow_((Real)(x), (Real)(y))
#pragma clang diagnostic pop

#endif

#define GET_NPY_SHAPE(arr, i)                                                  \
  (i <= Int(arr.ndim()) ? Int(arr.shape(Int(arr.ndim()) - i)) : 1)
#define STATES_ADDRESS(s)                                                      \
  ((((s.it * s.Nz + s.iz) * s.Ny + s.iy) * s.Nx + s.ix) * s.Nv + s.iv) * s.Ns
#define STATES_FROM_NPY(type, x)                                               \
  States_from_shape(sizeof(type), GET_NPY_SHAPE(x, 5), GET_NPY_SHAPE(x, 4),    \
                    GET_NPY_SHAPE(x, 3), GET_NPY_SHAPE(x, 2),                  \
                    GET_NPY_SHAPE(x, 1));
#define STATES_DATA_SIZE(s) s.Ns *STATES_SIZE(s)
#define STATES_SHAPE(s) {s.Nt, s.Nz, s.Ny, s.Nx, s.Nv}
#define STATES_SIZE(s) s.Nt *s.Nz *s.Ny *s.Nx *s.Nv
#define STATES_UNPACK(s)                                                       \
  s.Ns, s.Nt, s.Nz, s.Ny, s.Nx, s.Nv, s.it, s.iz, s.iy, s.ix, s.iv

struct States {
  __global void *data;
  Size Ns;                 // byte size of one element
  Size Nt, Nz, Ny, Nx, Nv; // points per dimension
  Size it, iz, iy, ix, iv; // indices per dimension
#ifndef __OPENCL_VERSION__
  cl_mem buffer;
#endif
};

struct StatesIdx {
  Size Ns;                 // byte size of one element
  Size Nt, Nz, Ny, Nx, Nv; // points per dimension
  Size it, iz, iy, ix, iv; // indices per dimension
};

Size offset(Size i, Int o, Size N) {
  if (o == 0) {
    return i;
  }
  return (((i + N) + o) % N + N) % N;
}

struct States States_from_shape(Size Ns, Size Nt, Size Nz, Size Ny, Size Nx,
                                Size Nv) {
  struct States s = {NULL, Ns, Nt, Nz, Ny, Nx, Nv, 0, 0, 0, 0, 0};
  return s;
}

struct States States_offset(struct States s, Int ot, // codespell:ignore ot
                            Int oz, Int oy, Int ox, Int ov) {
  s.it = offset(s.it, ot, s.Nt); // codespell:ignore ot
  s.iz = offset(s.iz, oz, s.Nz);
  s.iy = offset(s.iy, oy, s.Ny);
  s.ix = offset(s.ix, ox, s.Nx);
  s.iv = offset(s.iv, ov, s.Nv);
  return s;
}

struct States States_offset_t(Int o, struct States s) {
  s.it = offset(s.it, o, s.Nt);
  return s;
}
struct States States_offset_z(Int o, struct States s) {
  s.iz = offset(s.iz, o, s.Nz);
  return s;
}
struct States States_offset_y(Int o, struct States s) {
  s.iy = offset(s.iy, o, s.Ny);
  return s;
}
struct States States_offset_x(Int o, struct States s) {
  s.ix = offset(s.ix, o, s.Nx);
  return s;
}
struct States States_offset_v(Int o, struct States s) {
  s.iv = offset(s.iv, o, s.Nv);
  return s;
}

__global void *States_get_pointer(struct States s) {
  return (__global char *)(s.data) + STATES_ADDRESS(s);
}
__global Int *States_get_pointer_int(struct States s) {
  return (__global Int *)States_get_pointer(s);
}
__global Real *States_get_pointer_real(struct States s) {
  return (__global Real *)States_get_pointer(s);
}
Int States_get_int(struct States s) { return *States_get_pointer_int(s); }
Real States_get_real(struct States s) { return *States_get_pointer_real(s); }
Int States_get_bool(struct States s) { return States_get_int(s) != 0; }

#define _t States_offset_t
#define _z States_offset_z
#define _y States_offset_y
#define _x States_offset_x
#define _v States_offset_v
#define _p States_get_pointer
#define _pi States_get_pointer_int
#define _pr States_get_pointer_real
#define _i States_get_int
#define _r States_get_real
#define _b States_get_bool

Real safe_mult(Real w, Real x) {
  // safe multiplication that checks if w is zero,
  // such that safe_mult(0., nan) returns 0.
  return (w == REAL(0.0)) ? REAL(0.0) : w * x;
}

Real safe_divide(Real a, Real b) {
  // safe division that avoids division by zero,
  // i.e., if the denominator b is too close to zero,
  // it instead divides by a VERY_SMALL_NUMBER.
  if (fabs(b) < VERY_SMALL_NUMBER) {
    b = b < REAL(0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER;
  }
  return a / b;
}

Real diffuse(struct States w, struct States u) {
  return safe_mult(_r(_v(0, w)), _r(u)) +
         safe_mult(_r(_v(1, w)), _r(_x(+1, u))) +
         safe_mult(_r(_v(2, w)), _r(_x(-1, u))) +
         safe_mult(_r(_v(3, w)), _r(_y(+1, u))) +
         safe_mult(_r(_v(4, w)), _r(_y(-1, u))) +
         safe_mult(_r(_v(5, w)), _r(_z(+1, u))) +
         safe_mult(_r(_v(6, w)), _r(_z(-1, u))) +
         safe_mult(_r(_v(7, w)), _r(_y(+1, _z(+1, u)))) +
         safe_mult(_r(_v(8, w)), _r(_y(+1, _z(-1, u)))) +
         safe_mult(_r(_v(9, w)), _r(_y(-1, _z(+1, u)))) +
         safe_mult(_r(_v(10, w)), _r(_y(-1, _z(-1, u)))) +
         safe_mult(_r(_v(11, w)), _r(_x(+1, _z(+1, u)))) +
         safe_mult(_r(_v(12, w)), _r(_x(+1, _z(-1, u)))) +
         safe_mult(_r(_v(13, w)), _r(_x(-1, _z(+1, u)))) +
         safe_mult(_r(_v(14, w)), _r(_x(-1, _z(-1, u)))) +
         safe_mult(_r(_v(15, w)), _r(_x(+1, _y(+1, u)))) +
         safe_mult(_r(_v(16, w)), _r(_x(+1, _y(-1, u)))) +
         safe_mult(_r(_v(17, w)), _r(_x(-1, _y(+1, u)))) +
         safe_mult(_r(_v(18, w)), _r(_x(-1, _y(-1, u))));
}

"""

CORE: str = r"""
__kernel void calculate_weights(const Real dz, const Real dy, const Real dx,
                                __global void *mask_data,
                                struct StatesIdx mask_idx,
                                __global void *diffusivity_data,
                                struct StatesIdx diffusivity_idx,
                                __global void *weights_data,
                                struct StatesIdx weights_idx) {

  struct States mask = {mask_data, STATES_UNPACK(mask_idx)};
  struct States diffusivity = {diffusivity_data,
                               STATES_UNPACK(diffusivity_idx)};
  struct States weights = {weights_data, STATES_UNPACK(weights_idx)};

  const Size iz = get_global_id(0);
  const Size iy = get_global_id(1);
  const Size ix = get_global_id(2);

  const Real idxx = REAL(1.0) / (dx * dx);
  const Real idyy = REAL(1.0) / (dy * dy);
  const Real idzz = REAL(1.0) / (dz * dz);
  const Real idxy = REAL(0.25) / (dx * dy);
  const Real idxz = REAL(0.25) / (dx * dz);
  const Real idyz = REAL(0.25) / (dy * dz);

  // easier for notation, local copies of diffusion coefficients
  Real Dxx, Dyy, Dzz, Dxy, Dyz, Dxz;

  // mask:
  // v index: 1

  // diffusivity:
  // v index: xx, yy, zz, yz, xz, xy

  // weights:
  // v index: 19-point Laplacian
  // 0: central point
  // 1-6: main axes +x, -x +y, -y, z+,-z
  // 7-10: yz plane ++,+-,-+,--
  // 11-14: xz plane ++,+-,-+,--
  // 15-18: xy plane ++,+-,-+,--

  if (ix < weights.Nx && iy < weights.Ny && iz < weights.Nz) {
    struct States m = States_offset(mask, 0, iz, iy, ix, 0);
    struct States w = States_offset(weights, 0, iz, iy, ix, 0);
    struct States D = States_offset(diffusivity, 0, iz, iy, ix, 0);

    for (Size iv = 0; iv < weights.Nv; iv++) {
      *_pr(_v(iv, w)) = REAL(0.0);
    }

    if (_b(m)) {

      // 1. current Jx at ix+1/2
      if (_b(_x(+1, m))) {
        Dxx = REAL(0.5) * (_r(_v(0, _x(+1, D))) + _r(_v(0, D))) * idxx;
        Dxy = REAL(0.5) * (_r(_v(5, _x(+1, D))) + _r(_v(5, D))) * idxy;
        Dxz = REAL(0.5) * (_r(_v(4, _x(+1, D))) + _r(_v(4, D))) * idxz;

        // terms Dxx
        *_pr(_v(0, w)) -= Dxx;
        *_pr(_v(1, w)) += Dxx;

        // terms Dxy
        *_pr(_v(0, w)) += Dxy * (_b(_y(-1, m)) - _b(_y(+1, m)));
        *_pr(_v(1, w)) += Dxy * (_b(_y(-1, _x(+1, m))) - _b(_y(+1, _x(+1, m))));
        if (_b(_y(+1, _x(+1, m)))) {
          *_pr(_v(15, w)) += Dxy;
        }
        if (_b(_y(-1, _x(+1, m)))) {
          *_pr(_v(16, w)) -= Dxy;
        }
        if (_b(_y(+1, m))) {
          *_pr(_v(3, w)) += Dxy;
        }
        if (_b(_y(-1, m))) {
          *_pr(_v(4, w)) -= Dxy;
        }

        // terms Dxz
        *_pr(_v(0, w)) += Dxz * (_b(_z(-1, m)) - _b(_z(+1, m)));
        *_pr(_v(1, w)) += Dxz * (_b(_z(-1, _x(+1, m))) - _b(_z(+1, _x(+1, m))));
        if (_b(_z(+1, _x(+1, m)))) {
          *_pr(_v(11, w)) += Dxz;
        }
        if (_b(_z(-1, _x(+1, m)))) {
          *_pr(_v(12, w)) -= Dxz;
        }
        if (_b(_z(+1, m))) {
          *_pr(_v(5, w)) += Dxz;
        }
        if (_b(_z(-1, m))) {
          *_pr(_v(6, w)) -= Dxz;
        }
      }

      // 2. current Jx at ix-1/2
      if (_b(_x(-1, m))) {
        Dxx = -REAL(0.5) * (_r(_v(0, _x(-1, D))) + _r(_v(0, D))) * idxx;
        Dxy = -REAL(0.5) * (_r(_v(5, _x(-1, D))) + _r(_v(5, D))) * idxy;
        Dxz = -REAL(0.5) * (_r(_v(4, _x(-1, D))) + _r(_v(4, D))) * idxz;

        // terms Dxx
        *_pr(_v(2, w)) -= Dxx;
        *_pr(_v(0, w)) += Dxx;

        // terms Dxy
        *_pr(_v(2, w)) += Dxy * (_b(_y(-1, _x(-1, m))) - _b(_y(+1, _x(-1, m))));
        *_pr(_v(0, w)) += Dxy * (_b(_y(-1, m)) - _b(_y(+1, m)));
        if (_b(_y(+1, m))) {
          *_pr(_v(3, w)) += Dxy;
        }
        if (_b(_y(-1, m))) {
          *_pr(_v(4, w)) -= Dxy;
        }
        if (_b(_y(+1, _x(-1, m)))) {
          *_pr(_v(17, w)) += Dxy;
        }
        if (_b(_y(-1, _x(-1, m)))) {
          *_pr(_v(18, w)) -= Dxy;
        }

        // terms Dxz
        *_pr(_v(2, w)) += Dxz * (_b(_z(-1, _x(-1, m))) - _b(_z(+1, _x(-1, m))));
        *_pr(_v(0, w)) += Dxz * (_b(_z(-1, m)) - _b(_z(+1, m)));
        if (_b(_z(+1, m))) {
          *_pr(_v(5, w)) += Dxz;
        }
        if (_b(_z(-1, m))) {
          *_pr(_v(6, w)) -= Dxz;
        }
        if (_b(_z(+1, _x(-1, m)))) {
          *_pr(_v(13, w)) += Dxz;
        }
        if (_b(_z(-1, _x(-1, m)))) {
          *_pr(_v(14, w)) -= Dxz;
        }
      }

      // 3. current Jy at iy+1/2
      if (_b(_y(+1, m))) {
        Dyy = REAL(0.5) * (_r(_v(1, _y(+1, D))) + _r(_v(1, D))) * idyy;
        Dxy = REAL(0.5) * (_r(_v(5, _y(+1, D))) + _r(_v(5, D))) * idxy;
        Dyz = REAL(0.5) * (_r(_v(3, _y(+1, D))) + _r(_v(3, D))) * idyz;

        // terms Dyy
        *_pr(_v(0, w)) -= Dyy;
        *_pr(_v(3, w)) += Dyy;

        // terms Dyx
        *_pr(_v(0, w)) += Dxy * (_b(_x(-1, m)) - _b(_x(+1, m)));
        *_pr(_v(3, w)) += Dxy * (_b(_y(+1, _x(-1, m))) - _b(_y(+1, _x(+1, m))));
        if (_b(_y(+1, _x(+1, m)))) {
          *_pr(_v(15, w)) += Dxy;
        }
        if (_b(_y(+1, _x(-1, m)))) {
          *_pr(_v(17, w)) -= Dxy;
        }
        if (_b(_x(+1, m))) {
          *_pr(_v(1, w)) += Dxy;
        }
        if (_b(_x(-1, m))) {
          *_pr(_v(2, w)) -= Dxy;
        }

        // terms Dyz
        *_pr(_v(0, w)) += Dyz * (_b(_z(-1, m)) - _b(_z(+1, m)));
        *_pr(_v(3, w)) += Dyz * (_b(_z(-1, _y(+1, m))) - _b(_z(+1, _y(+1, m))));
        if (_b(_z(+1, _y(+1, m)))) {
          *_pr(_v(7, w)) += Dyz;
        }
        if (_b(_z(-1, _y(+1, m)))) {
          *_pr(_v(8, w)) -= Dyz;
        }
        if (_b(_z(+1, m))) {
          *_pr(_v(5, w)) += Dyz;
        }
        if (_b(_z(-1, m))) {
          *_pr(_v(6, w)) -= Dyz;
        }
      }

      // 4. current Jy at iy-1/2
      if (_b(_y(-1, m))) {
        Dyy = -REAL(0.5) * (_r(_v(1, _y(-1, D))) + _r(_v(1, D))) * idyy;
        Dxy = -REAL(0.5) * (_r(_v(5, _y(-1, D))) + _r(_v(5, D))) * idxy;
        Dyz = -REAL(0.5) * (_r(_v(3, _y(-1, D))) + _r(_v(3, D))) * idyz;

        // terms Dyy
        *_pr(_v(4, w)) -= Dyy;
        *_pr(_v(0, w)) += Dyy;

        // terms Dyx
        *_pr(_v(4, w)) += Dxy * (_b(_y(-1, _x(-1, m))) - _b(_y(-1, _x(+1, m))));
        *_pr(_v(0, w)) += Dxy * (_b(_x(-1, m)) - _b(_x(+1, m)));
        if (_b(_x(+1, m))) {
          *_pr(_v(1, w)) += Dxy;
        }
        if (_b(_x(-1, m))) {
          *_pr(_v(2, w)) -= Dxy;
        }
        if (_b(_y(-1, _x(+1, m)))) {
          *_pr(_v(16, w)) += Dxy;
        }
        if (_b(_y(-1, _x(-1, m)))) {
          *_pr(_v(18, w)) -= Dxy;
        }

        // terms Dyz
        *_pr(_v(4, w)) += Dyz * (_b(_z(-1, _y(-1, m))) - _b(_z(+1, _y(-1, m))));
        *_pr(_v(0, w)) += Dyz * (_b(_z(-1, m)) - _b(_z(+1, m)));
        if (_b(_z(+1, m))) {
          *_pr(_v(5, w)) += Dyz;
        }
        if (_b(_z(-1, m))) {
          *_pr(_v(6, w)) -= Dyz;
        }
        if (_b(_z(+1, _y(-1, m)))) {
          *_pr(_v(9, w)) += Dyz;
        }
        if (_b(_z(-1, _y(-1, m)))) {
          *_pr(_v(10, w)) -= Dyz;
        }
      }

      // 5. current Jz at iz+1/2
      if (_b(_z(+1, m))) {
        Dzz = REAL(0.5) * (_r(_v(2, _z(+1, D))) + _r(_v(2, D))) * idzz;
        Dxz = REAL(0.5) * (_r(_v(4, _z(+1, D))) + _r(_v(4, D))) * idxz;
        Dyz = REAL(0.5) * (_r(_v(3, _z(+1, D))) + _r(_v(3, D))) * idyz;

        // terms Dzz
        *_pr(_v(0, w)) -= Dzz;
        *_pr(_v(5, w)) += Dzz;

        // terms Dzy
        *_pr(_v(0, w)) += Dyz * (_b(_y(-1, m)) - _b(_y(+1, m)));
        *_pr(_v(5, w)) += Dyz * (_b(_z(+1, _y(-1, m))) - _b(_z(+1, _y(+1, m))));
        if (_b(_z(+1, _y(+1, m)))) {
          *_pr(_v(7, w)) += Dyz;
        }
        if (_b(_z(+1, _y(-1, m)))) {
          *_pr(_v(9, w)) -= Dyz;
        }
        if (_b(_y(+1, m))) {
          *_pr(_v(3, w)) += Dyz;
        }
        if (_b(_y(-1, m))) {
          *_pr(_v(4, w)) -= Dyz;
        }

        // terms Dzx
        *_pr(_v(0, w)) += Dxz * (_b(_x(-1, m)) - _b(_x(+1, m)));
        *_pr(_v(5, w)) += Dxz * (_b(_z(+1, _x(-1, m))) - _b(_z(+1, _x(+1, m))));
        if (_b(_z(+1, _x(+1, m)))) {
          *_pr(_v(11, w)) += Dxz;
        }
        if (_b(_z(+1, _x(-1, m)))) {
          *_pr(_v(13, w)) -= Dxz;
        }
        if (_b(_x(+1, m))) {
          *_pr(_v(1, w)) += Dxz;
        }
        if (_b(_x(-1, m))) {
          *_pr(_v(2, w)) -= Dxz;
        }
      }

      // 6. current Jz at iz-1/2
      if (_b(_z(-1, m))) {
        Dzz = -REAL(0.5) * (_r(_v(2, _z(-1, D))) + _r(_v(2, D))) * idzz;
        Dxz = -REAL(0.5) * (_r(_v(4, _z(-1, D))) + _r(_v(4, D))) * idxz;
        Dyz = -REAL(0.5) * (_r(_v(3, _z(-1, D))) + _r(_v(3, D))) * idyz;

        // terms Dzz
        *_pr(_v(6, w)) -= Dzz;
        *_pr(_v(0, w)) += Dzz;

        // terms Dzy
        *_pr(_v(6, w)) += Dyz * (_b(_z(-1, _y(-1, m))) - _b(_z(-1, _y(+1, m))));
        *_pr(_v(0, w)) += Dyz * (_b(_y(-1, m)) - _b(_y(+1, m)));
        if (_b(_y(+1, m))) {
          *_pr(_v(3, w)) += Dyz;
        }
        if (_b(_y(-1, m))) {
          *_pr(_v(4, w)) -= Dyz;
        }
        if (_b(_z(-1, _y(+1, m)))) {
          *_pr(_v(8, w)) += Dyz;
        }
        if (_b(_z(-1, _y(-1, m)))) {
          *_pr(_v(10, w)) -= Dyz;
        }

        // terms Dzx
        *_pr(_v(6, w)) += Dxz * (_b(_z(-1, _x(-1, m))) - _b(_z(-1, _x(+1, m))));
        *_pr(_v(0, w)) += Dxz * (_b(_x(-1, m)) - _b(_x(+1, m)));
        if (_b(_x(+1, m))) {
          *_pr(_v(1, w)) += Dxz;
        }
        if (_b(_x(-1, m))) {
          *_pr(_v(2, w)) -= Dxz;
        }
        if (_b(_z(-1, _x(+1, m)))) {
          *_pr(_v(12, w)) += Dxz;
        }
        if (_b(_z(-1, _x(-1, m)))) {
          *_pr(_v(14, w)) -= Dxz;
        }
      }
    }
  }
}

__kernel void add_stimulus(const Real amplitude, __global void *shape_data,
                           struct StatesIdx shape_idx,
                           __global void *states_data,
                           struct StatesIdx states_idx) {

  struct States shape = {shape_data, STATES_UNPACK(shape_idx)};
  struct States states = {states_data, STATES_UNPACK(states_idx)};

  const Size iz = get_global_id(0);
  const Size iy = get_global_id(1);
  const Size ix = get_global_id(2);

  if (ix < states.Nx && iy < states.Ny && iz < states.Nz) {
    const Real current = amplitude * _r(States_offset(shape, 0, iz, iy, ix, 0));
    if (fabs(current) > VERY_SMALL_NUMBER) {
      *_pr(States_offset(states, 0, iz, iy, ix, 0)) += current;
    }
  }
}

__kernel void set_outside(const Real value, __global void *mask_data,
                          struct StatesIdx mask_idx, __global void *states_data,
                          struct StatesIdx states_idx) {

  struct States mask = {mask_data, STATES_UNPACK(mask_idx)};
  struct States states = {states_data, STATES_UNPACK(states_idx)};

  const Size iz = get_global_id(0);
  const Size iy = get_global_id(1);
  const Size ix = get_global_id(2);

  if (ix < states.Nx && iy < states.Ny && iz < states.Nz) {
    if (!_b(States_offset(mask, 0, iz, iy, ix, 0))) {
      __global Real *u = _pr(States_offset(states, 0, iz, iy, ix, 0));
      for (Size iv = 0; iv < states.Nv; iv++) {
        u[iv] = value;
      }
    }
  }
}

"""