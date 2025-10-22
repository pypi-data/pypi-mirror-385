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
