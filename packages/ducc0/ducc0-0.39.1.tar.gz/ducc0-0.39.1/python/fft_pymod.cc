/*
This file is part of pocketfft.

Copyright (C) 2010-2025 Max-Planck-Society
Copyright (C) 2019 Peter Bell

Authors: Martin Reinecke, Peter Bell

All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.
* Neither the name of the copyright holder nor the names of its contributors may
  be used to endorse or promote products derived from this software without
  specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

/*
 *  Python interface.
 */

#include <complex>

#include "ducc0/../../python/module_adders.h"
#include "ducc0/fft/fft.h"
#include "ducc0/bindings/pybind_utils.h"

namespace ducc0 {

namespace detail_pymodule_fft {

using namespace std;

namespace {

using shape_t = ducc0::fmav_info::shape_t;

#ifdef DUCC0_USE_NANOBIND
using ldbl_t = double;
#else
// Only instantiate long double transforms if they offer more precision
using ldbl_t = typename conditional<
  sizeof(long double)==sizeof(double), double, long double>::type;
#endif

using c64 = complex<float>;
using c128 = complex<double>;
using clong = complex<ldbl_t>;
using f32 = float;
using f64 = double;
using flong = ldbl_t;

using OptAxes = optional<vector<ptrdiff_t>>;

static shape_t makeaxes(const CNpArr &in, const OptAxes &axes)
  {
  if (!axes)
    {
    shape_t res(size_t(in.ndim()));
    for (size_t i=0; i<res.size(); ++i)
      res[i]=i;
    return res;
    }
  auto tmp=axes.value();
  auto ndim = in.ndim();
  if ((tmp.size()>size_t(ndim)) || (tmp.size()==0))
    throw runtime_error("bad axes argument");
  for (auto& sz: tmp)
    {
    if (sz<0)
      sz += ndim;
    if ((sz>=ptrdiff_t(ndim)) || (sz<0))
      throw invalid_argument("axes exceeds dimensionality of output");
    }
  return shape_t(tmp.begin(), tmp.end());
  }

#define DISPATCH(arr, T1, T2, T3, func, args) \
  { \
  if (isPyarr<T1>(arr)) return func<double> args; \
  if (isPyarr<T2>(arr)) return func<float> args;  \
  if (isPyarr<T3>(arr)) return func<ldbl_t> args; \
  throw runtime_error("unsupported data type"); \
  }

template<typename T> static T norm_fct(int inorm, size_t N)
  {
  if (inorm==0) return T(1);
  if (inorm==2) return T(1/ldbl_t(N));
  if (inorm==1) return T(1/sqrt(ldbl_t(N)));
  throw invalid_argument("invalid value for inorm (must be 0, 1, or 2)");
  }

template<typename T> static T norm_fct(int inorm, const shape_t &shape,
  const shape_t &axes, size_t fct=1, int delta=0)
  {
  if (inorm==0) return T(1);
  size_t N(1);
  for (auto a: axes)
    N *= fct * size_t(int64_t(shape[a])+delta);
  return norm_fct<T>(inorm, N);
  }

template<typename T> static NpArr c2c_internal(const CNpArr &in,
  const OptAxes &axes_, bool forward, int inorm, const OptNpArr &out_,
  size_t nthreads)
  {
  auto axes = makeaxes(in, axes_);
  auto ain = to_cfmav<complex<T>>(in, "a");
  auto [out, aout] = get_OptNpArr_and_vfmav<complex<T>>(out_, ain.shape(), "out");
  {
  py::gil_scoped_release release;
  T fct = norm_fct<T>(inorm, ain.shape(), axes);
  ducc0::c2c(ain, aout, axes, forward, fct, nthreads);
  }
  return out;
  }

template<typename T> static NpArr c2c_sym_internal(const CNpArr &in,
  const OptAxes &axes_, bool forward, int inorm, const OptNpArr &out_,
  size_t nthreads)
  {
  auto axes = makeaxes(in, axes_);
  auto ain = to_cfmav<T>(in, "a");
  auto [out, aout] = get_OptNpArr_and_vfmav<complex<T>>(out_, ain.shape(), "out");
  {
  py::gil_scoped_release release;
  T fct = norm_fct<T>(inorm, ain.shape(), axes);
  // select proper sub-array for FFT
  auto shp_half = aout.shape();
  shp_half[axes.back()] = shp_half[axes.back()]/2+1;
  vfmav<complex<T>> aout_half(aout, shp_half, aout.stride());
  ducc0::r2c(ain, aout_half, axes, forward, fct, nthreads);
  // now fill in second half
  using namespace ducc0::detail_fft;
  hermiteHelper(0, 0, 0, 0, aout, aout, axes, [](const complex<T> &c, complex<T> &, complex<T> &c1)
    {
    c1 = conj(c);
    }, nthreads);
  }
  return out;
  }

NpArr c2c(const CNpArr &a, const OptAxes &axes_, bool forward,
  int inorm, const OptNpArr &out_, size_t nthreads)
  {
  if (isPyarr<c64>(a)||isPyarr<c128>(a)||isPyarr<clong>(a))
    DISPATCH(a, c128, c64, clong, c2c_internal, (a, axes_, forward,
             inorm, out_, nthreads))

  DISPATCH(a, f64, f32, flong, c2c_sym_internal, (a, axes_, forward,
           inorm, out_, nthreads))
  }

template<typename T> static NpArr r2c_internal(const CNpArr &in,
  const OptAxes &axes_, bool forward, int inorm, const OptNpArr &out_,
  size_t nthreads)
  {
  auto axes = makeaxes(in, axes_);
  auto ain = to_cfmav<T>(in, "a");
  auto dims_out(ain.shape());
  dims_out[axes.back()] = (dims_out[axes.back()]>>1)+1;
  auto [out, aout] = get_OptNpArr_and_vfmav<complex<T>>(out_, dims_out, "out");
  {
  py::gil_scoped_release release;
  T fct = norm_fct<T>(inorm, ain.shape(), axes);
  ducc0::r2c(ain, aout, axes, forward, fct, nthreads);
  }
  return out;
  }

NpArr r2c(const CNpArr &in, const OptAxes &axes_, bool forward,
  int inorm, const OptNpArr &out_, size_t nthreads)
  {
  DISPATCH(in, f64, f32, flong, r2c_internal, (in, axes_, forward, inorm, out_,
    nthreads))
  }

template<typename T> static NpArr r2r_fftpack_internal(const CNpArr &in,
  const OptAxes &axes_, bool real2hermitian, bool forward, int inorm,
  const OptNpArr &out_, size_t nthreads)
  {
  auto axes = makeaxes(in, axes_);
  auto ain = to_cfmav<T>(in, "a");
  auto [out, aout] = get_OptNpArr_and_vfmav<T>(out_, ain.shape(), "out");
  {
  py::gil_scoped_release release;
  T fct = norm_fct<T>(inorm, ain.shape(), axes);
  ducc0::r2r_fftpack(ain, aout, axes, real2hermitian, forward, fct, nthreads);
  }
  return out;
  }

NpArr r2r_fftpack(const CNpArr &in, const OptAxes &axes_,
  bool real2hermitian, bool forward, int inorm, const OptNpArr &out_,
  size_t nthreads)
  {
  DISPATCH(in, f64, f32, flong, r2r_fftpack_internal, (in, axes_,
    real2hermitian, forward, inorm, out_, nthreads))
  }

template<typename T> static NpArr r2r_fftw_internal(const CNpArr &in,
  const OptAxes &axes_, bool forward, int inorm,
  const OptNpArr &out_, size_t nthreads)
  {
  auto axes = makeaxes(in, axes_);
  auto ain = to_cfmav<T>(in, "a");
  auto [out, aout] = get_OptNpArr_and_vfmav<T>(out_, ain.shape(), "out");
  {
  py::gil_scoped_release release;
  T fct = norm_fct<T>(inorm, ain.shape(), axes);
  ducc0::r2r_fftw(ain, aout, axes, forward, fct, nthreads);
  }
  return out;
  }

NpArr r2r_fftw(const CNpArr &in, const OptAxes &axes_,
  bool forward, int inorm, const OptNpArr &out_, size_t nthreads)
  {
  DISPATCH(in, f64, f32, flong, r2r_fftw_internal, (in, axes_,
    forward, inorm, out_, nthreads))
  }

template<typename T> static NpArr dct_internal(const CNpArr &in,
  const OptAxes &axes_, int type, int inorm, const OptNpArr &out_,
  size_t nthreads)
  {
  auto axes = makeaxes(in, axes_);
  auto ain = to_cfmav<T>(in, "a");
  auto [out, aout] = get_OptNpArr_and_vfmav<T>(out_, ain.shape(), "out");
  {
  py::gil_scoped_release release;
  T fct = (type==1) ? norm_fct<T>(inorm, ain.shape(), axes, 2, -1)
                    : norm_fct<T>(inorm, ain.shape(), axes, 2);
  bool ortho = (inorm==1);
  ducc0::dct(ain, aout, axes, type, fct, ortho, nthreads);
  }
  return out;
  }

NpArr dct(const CNpArr &in, int type, const OptAxes &axes_,
  int inorm, const OptNpArr &out_, size_t nthreads)
  {
  if ((type<1) || (type>4)) throw invalid_argument("invalid DCT type");
  DISPATCH(in, f64, f32, flong, dct_internal, (in, axes_, type, inorm, out_,
    nthreads))
  }

template<typename T> static NpArr dst_internal(const CNpArr &in,
  const OptAxes &axes_, int type, int inorm, const OptNpArr &out_,
  size_t nthreads)
  {
  auto axes = makeaxes(in, axes_);
  auto ain = to_cfmav<T>(in, "a");
  auto [out, aout] = get_OptNpArr_and_vfmav<T>(out_, ain.shape(), "out");
  {
  py::gil_scoped_release release;
  T fct = (type==1) ? norm_fct<T>(inorm, ain.shape(), axes, 2, 1)
                    : norm_fct<T>(inorm, ain.shape(), axes, 2);
  bool ortho = (inorm==1);
  ducc0::dst(ain, aout, axes, type, fct, ortho, nthreads);
  }
  return out;
  }

NpArr dst(const CNpArr &in, int type, const OptAxes &axes_,
  int inorm, const OptNpArr &out_, size_t nthreads)
  {
  if ((type<1) || (type>4)) throw invalid_argument("invalid DST type");
  DISPATCH(in, f64, f32, flong, dst_internal, (in, axes_, type, inorm,
    out_, nthreads))
  }

template<typename T> static NpArr c2r_internal(const NpArr &in,
  const OptAxes &axes_, size_t lastsize, bool forward, int inorm,
  const OptNpArr &out_, size_t nthreads, bool allow_overwriting_input)
  {
  auto axes = makeaxes(CNpArr(in), axes_);
  size_t axis = axes.back();
  auto ain_c = to_cfmav<complex<T>>(in, "a");
  shape_t dims_out(ain_c.shape());
  if (lastsize==0) lastsize=2*ain_c.shape(axis)-1;
  if ((lastsize/2) + 1 != ain_c.shape(axis))
    throw invalid_argument("bad lastsize");
  dims_out[axis] = lastsize;
  auto [out, aout] = get_OptNpArr_and_vfmav<T>(out_, dims_out, "out");
  T fct = norm_fct<T>(inorm, aout.shape(), axes);
  if (allow_overwriting_input)
    {
    auto ain = to_vfmav<complex<T>>(in, "a");
    {
    py::gil_scoped_release release;
    ducc0::c2r_mut(ain, aout, axes, forward, fct, nthreads);
    }
    }
  else
    {
    py::gil_scoped_release release;
    ducc0::c2r(ain_c, aout, axes, forward, fct, nthreads);
    }
  return out;
  }

NpArr c2r(NpArr &in, const OptAxes &axes_, size_t lastsize,
  bool forward, int inorm, const OptNpArr &out_, size_t nthreads,
  bool allow_overwriting_input)
  {
  DISPATCH(in, c128, c64, clong, c2r_internal, (in, axes_, lastsize, forward,
    inorm, out_, nthreads, allow_overwriting_input))
  }

template<typename T> static NpArr separable_hartley_internal(const CNpArr &in,
  const OptAxes &axes_, int inorm, const OptNpArr &out_, size_t nthreads)
  {
  auto axes = makeaxes(in, axes_);
  auto ain = to_cfmav<T>(in, "a");
  auto [out, aout] = get_OptNpArr_and_vfmav<T>(out_, ain.shape(), "out");
  {
  py::gil_scoped_release release;
  T fct = norm_fct<T>(inorm, ain.shape(), axes);
  ducc0::r2r_separable_hartley(ain, aout, axes, fct, nthreads);
  }
  return out;
  }

NpArr separable_hartley(const CNpArr &in, const OptAxes &axes_,
  int inorm, const OptNpArr &out_, size_t nthreads)
  {
  DISPATCH(in, f64, f32, flong, separable_hartley_internal, (in, axes_, inorm,
    out_, nthreads))
  }

template<typename T> static NpArr genuine_hartley_internal(const CNpArr &in,
  const OptAxes &axes_, int inorm, const OptNpArr &out_, size_t nthreads)
  {
  auto axes = makeaxes(in, axes_);
  auto ain = to_cfmav<T>(in, "a");
  auto [out, aout] = get_OptNpArr_and_vfmav<T>(out_, ain.shape(), "out");
  {
  py::gil_scoped_release release;
  T fct = norm_fct<T>(inorm, ain.shape(), axes);
  ducc0::r2r_genuine_hartley(ain, aout, axes, fct, nthreads);
  }
  return out;
  }

NpArr genuine_hartley(const CNpArr &in, const OptAxes &axes_,
  int inorm, const OptNpArr &out_, size_t nthreads)
  {
  DISPATCH(in, f64, f32, flong, genuine_hartley_internal, (in, axes_, inorm,
    out_, nthreads))
  }

template<typename T> static NpArr separable_fht_internal(const CNpArr &in,
  const OptAxes &axes_, int inorm, const OptNpArr &out_, size_t nthreads)
  {
  auto axes = makeaxes(in, axes_);
  auto ain = to_cfmav<T>(in, "a");
  auto [out, aout] = get_OptNpArr_and_vfmav<T>(out_, ain.shape(), "out");
  {
  py::gil_scoped_release release;
  T fct = norm_fct<T>(inorm, ain.shape(), axes);
  ducc0::r2r_separable_fht(ain, aout, axes, fct, nthreads);
  }
  return out;
  }

NpArr separable_fht(const CNpArr &in, const OptAxes &axes_,
  int inorm, const OptNpArr &out_, size_t nthreads)
  {
  DISPATCH(in, f64, f32, flong, separable_fht_internal, (in, axes_, inorm,
    out_, nthreads))
  }

template<typename T> static NpArr genuine_fht_internal(const CNpArr &in,
  const OptAxes &axes_, int inorm, const OptNpArr &out_, size_t nthreads)
  {
  auto axes = makeaxes(in, axes_);
  auto ain = to_cfmav<T>(in, "a");
  auto [out, aout] = get_OptNpArr_and_vfmav<T>(out_, ain.shape(), "out");
  {
  py::gil_scoped_release release;
  T fct = norm_fct<T>(inorm, ain.shape(), axes);
  ducc0::r2r_genuine_fht(ain, aout, axes, fct, nthreads);
  }
  return out;
  }

NpArr genuine_fht(const CNpArr &in, const OptAxes &axes_,
  int inorm, const OptNpArr &out_, size_t nthreads)
  {
  DISPATCH(in, f64, f32, flong, genuine_fht_internal, (in, axes_, inorm,
    out_, nthreads))
  }

// Export good_size in raw C-API to reduce overhead (~4x faster)
PyObject * good_size(PyObject * /*self*/, PyObject * args)
  {
  Py_ssize_t n_ = -1;
  int real = false;
  if (!PyArg_ParseTuple(args, "n|p:good_size", &n_, &real))
    return nullptr;

  if (n_<0)
    {
    PyErr_SetString(PyExc_ValueError, "Target length must be positive");
    return nullptr;
    }
  if ((n_-1) > static_cast<Py_ssize_t>(numeric_limits<size_t>::max() / 11))
    {
    PyErr_Format(PyExc_ValueError,
                 "Target length is too large to perform an FFT: %zi", n_);
    return nullptr;
    }
  const auto n = static_cast<size_t>(n_);
  using namespace ducc0::detail_fft;
  return PyLong_FromSize_t(
    real ? util1d::good_size_real(n) : util1d::good_size_cmplx(n));
  }

template<typename T> static NpArr convolve_axis_internal(const CNpArr &in_,
  NpArr &out_, size_t axis, const CNpArr &kernel_, size_t nthreads)
  {
  auto in = to_cfmav<T>(in_, "in");
  auto out = to_vfmav<T>(out_, "out");
  auto kernel = to_cmav<T,1>(kernel_, "kernel");
  {
  py::gil_scoped_release release;
  ducc0::convolve_axis(in, out, axis, kernel, nthreads);
  }
  return out_;
  }

template<typename T> static NpArr convolve_axis_internal_c(const CNpArr &in_,
  NpArr &out_, size_t axis, const CNpArr &kernel_, size_t nthreads)
  {
  return convolve_axis_internal<complex<T>>(in_, out_, axis, kernel_, nthreads);
  }

NpArr convolve_axis(const CNpArr &in, NpArr &out, size_t axis,
  const CNpArr &kernel, size_t nthreads)
  {
  if (isPyarr<c64>(in)||isPyarr<c128>(in)||isPyarr<clong>(in))
    DISPATCH(in, c128, c64, clong, convolve_axis_internal_c, (in, out, axis,
      kernel, nthreads))
  else
    DISPATCH(in, f64, f32, flong, convolve_axis_internal, (in, out, axis,
      kernel, nthreads))
  }

const char *fft_DS = R"""(Fast Fourier, sine/cosine, and Hartley transforms.

This module supports
 - single, double, and long double precision
 - complex and real-valued transforms
 - multi-dimensional transforms

For two- and higher-dimensional transforms the code will use SSE2 and AVX
vector instructions for faster execution if these are supported by the CPU and
were enabled during compilation.
)""";

const char *c2c_DS = R"""(Performs a complex FFT.

Parameters
----------
a : numpy.ndarray (any complex or real type)
    The input data. If its type is real, a more efficient real-to-complex
    transform will be used.
axes : list of integers
    The axes along which the FFT is carried out (first axis has number 0).
    If not set, all axes will be transformed.
forward : bool
    If `True`, a negative sign is used in the exponent, else a positive one.
inorm : int
    Normalization type
      | 0 : no normalization
      | 1 : divide by sqrt(N)
      | 2 : divide by N

    where N is the product of the lengths of the transformed axes.
out : numpy.ndarray (same shape as `a`, complex type with same accuracy as `a`)
    May be identical to `a`, but if it isn't, it must not overlap with `a`.
    If None, a new array is allocated to store the output.
nthreads : int
    Number of threads to use. If 0, use the system default (typically the number
    of hardware threads on the compute node).

Returns
-------
numpy.ndarray (same shape as `a`, complex type with same accuracy as `a`)
    The transformed data.

Notes
-----

For one-dimensional arrays of length :math:`N`, this function computes:
:math:`\forall\ k = 0 \dots n-1`

.. math::
    Y_k = \frac{1}{\sqrt{n}^{\textrm{inorm}}} \sum_{j=0}^{n-1}  X_j  e^{s 2\pi i \frac{j k}{N}}

where

.. math::
    s = \left\{
    \begin{align}
    -1 & \quad \text{if forward} \\
    +1 & \quad \text{else}
    \end{align}
    \right.

For multi-dimensional arrays, the function computes one-dimensional transforms
on each of the specified axes sequentially. For instance, for a two-dimensional
array :math:`X` of shape :math:`(N,M)` (with ``axes=(0,1)``), this function
computes the two-dimensional array of the same shape :math:`Z` as:

.. math::
    Y_{k,p} = \frac{1}{\sqrt{N}^{\textrm{inorm}}} \sum_{j=0}^{N-1} X_{j,p} e^{s 2\pi i \frac{j k}{N}} \\
    Z_{k,q} = \frac{1}{\sqrt{M}^{\textrm{inorm}}} \sum_{p=0}^{M-1} Y_{k,p} e^{s 2\pi i \frac{p q}{M}} 
)""";

const char *r2c_DS = R"""(Performs an FFT whose input is strictly real.

Parameters
----------
a : numpy.ndarray (any real type)
    The input data
axes : list of integers
    The axes along which the FFT is carried out.
    If not set, this is assumed to be `list(range(a.ndim))`.
    The real-to-complex transform will be executed along `axes[-1]`,
    and will be executed first.
forward : bool
    If `True`, a negative sign is used in the exponent, else a positive one.
inorm : int
    Normalization type
      | 0 : no normalization
      | 1 : divide by sqrt(N)
      | 2 : divide by N

    where N is the product of the lengths of the transformed input axes.
out : numpy.ndarray (complex type with same accuracy as `a`)
    For the required shape, see the `Returns` section.
    Must not overlap with `a`.
    If None, a new array is allocated to store the output.
nthreads : int
    Number of threads to use. If 0, use the system default (typically the number
    of hardware threads on the compute node).

Returns
-------
numpy.ndarray (complex type with same accuracy as `a`)
    The transformed data. The shape is identical to that of the input array,
    except for `axes[-1]`. If the length of that axis was n on input,
    it is n//2+1 on output.

Notes
-----
Mathematically this function performs exactly the same operations as
:func:`c2c`, but since the resulting array has Hermitian symmetry, the output
array will be cut from ``n`` entries to ``n//2+1`` entries along ``axes[-1]``.
)""";

const char *c2r_DS = R"""(Performs an FFT whose output is strictly real.

Parameters
----------
a : numpy.ndarray (any complex type)
    The input data
axes : list of integers
    The axes along which the FFT is carried out.
    If not set, this is assumed to be `list(range(a.ndim))`.
    The complex-to-real transform will be executed along `axes[-1]`,
    and will be executed last.
lastsize : the output size of the last axis to be transformed.
    If the corresponding input axis has size n, this can be 2*n-2 or 2*n-1.
forward : bool
    If `True`, a negative sign is used in the exponent, else a positive one.
inorm : int
    Normalization type
      | 0 : no normalization
      | 1 : divide by sqrt(N)
      | 2 : divide by N

    where N is the product of the lengths of the transformed output axes.
out : numpy.ndarray (real type with same accuracy as `a`)
    For the required shape, see the `Returns` section.
    Must not overlap with `a`.
    If None, a new array is allocated to store the output.
nthreads : int
    Number of threads to use. If 0, use the system default (typically the number
    of hardware threads on the compute node).
allow_overwriting_input : bool
    If `True`, the input array may be overwritten with some intermediate data.
    This can avoid allocating temporary variables and improve performance.

Returns
-------
numpy.ndarray (real type with same accuracy as `a`)
    The transformed data. The shape is identical to that of the input array,
    except for `axes[-1]`, which has now `lastsize` entries.
)""";

const char *r2r_fftpack_DS = R"""(Performs a real-valued FFT using FFTPACK's halfcomplex storage scheme.

Parameters
----------
a : numpy.ndarray (any real type)
    The input data
axes : list of integers
    The axes along which the FFT is carried out.
    If not set, this is assumed to be `list(range(a.ndim))`.
    Axes will be transformed in the specified order.
real2hermitian : bool
    if True, the input is purely real and the output will have Hermitian
    symmetry and be stored in FFTPACK's halfcomplex ordering, otherwise the
    opposite.
forward : bool
    If `True`, a negative sign is used in the exponent, else a positive one.
inorm : int
    Normalization type
      | 0 : no normalization
      | 1 : divide by sqrt(N)
      | 2 : divide by N

    where N is the length of `axis`.
out : numpy.ndarray (same shape and data type as `a`)
    May be identical to `a`, but if it isn't, it must not overlap with `a`.
    If None, a new array is allocated to store the output.
nthreads : int
    Number of threads to use. If 0, use the system default (typically the number
    of hardware threads on the compute node).

Returns
-------
numpy.ndarray (same shape and data type as `a`)
    The transformed data. The shape is identical to that of the input array.
)""";

const char *r2r_fftw_DS = R"""(Performs a real-valued FFT using FFTW's halfcomplex storage scheme.

Parameters
----------
a : numpy.ndarray (any real type)
    The input data
axes : list of integers
    The axes along which the FFT is carried out.
    If not set, this is assumed to be `list(range(a.ndim))`.
    Axes will be transformed in the specified order.
forward : bool
    If `True`, a negative sign is used in the exponent, else a positive one.
inorm : int
    Normalization type
      | 0 : no normalization
      | 1 : divide by sqrt(N)
      | 2 : divide by N

    where N is the length of `axis`.
out : numpy.ndarray (same shape and data type as `a`)
    May be identical to `a`, but if it isn't, it must not overlap with `a`.
    If None, a new array is allocated to store the output.
nthreads : int
    Number of threads to use. If 0, use the system default (typically the number
    of hardware threads on the compute node).

Returns
-------
numpy.ndarray (same shape and data type as `a`)
    The transformed data. The shape is identical to that of the input array.
)""";

const char *separable_hartley_DS = R"""(
Notes
-----
This function uses a nonstandard Hartley convention and is deprecated.
Do not use in newly written code!
)""";

const char *genuine_hartley_DS = R"""(
Notes
-----
This function uses a nonstandard Hartley convention and is deprecated.
Do not use in newly written code!
)""";

const char *separable_fht_DS = R"""(Performs a separable Hartley transform.
For every requested axis, a 1D forward Fourier transform is carried out, and
the intermediate result is its real part minus its imaginary part.
Then the next axis is processed.

Parameters
----------
a : numpy.ndarray (any real type)
    The input data
axes : list of integers
    The axes along which the transform is carried out.
    If not set, this is assumed to be `list(range(a.ndim))`.
    Axes will be transformed in the specified order.
inorm : int
    Normalization type
      | 0 : no normalization
      | 1 : divide by sqrt(N)
      | 2 : divide by N

    where N is the product of the lengths of the transformed axes.
out : numpy.ndarray (same shape and data type as `a`)
    May be identical to `a`, but if it isn't, it must not overlap with `a`.
    If None, a new array is allocated to store the output.
nthreads : int
    Number of threads to use. If 0, use the system default (typically the number
    of hardware threads on the compute node).

Returns
-------
numpy.ndarray (same shape and data type as `a`)
    The transformed data
)""";

const char *genuine_fht_DS = R"""(Performs a full Hartley transform.
A full forward Fourier transform is carried out over the requested axes, and the
real part minus the imaginary part of the result is stored in the output
array. For a single transformed axis, this is identical to `separable_fht`,
but when transforming multiple axes, the results are different.

Parameters
----------
a : numpy.ndarray (any real type)
    The input data
axes : list of integers
    The axes along which the transform is carried out.
    If not set, all axes will be transformed.
inorm : int
    Normalization type
      | 0 : no normalization
      | 1 : divide by sqrt(N)
      | 2 : divide by N

    where N is the product of the lengths of the transformed axes.
out : numpy.ndarray (same shape and data type as `a`)
    May be identical to `a`, but if it isn't, it must not overlap with `a`.
    If None, a new array is allocated to store the output.
nthreads : int
    Number of threads to use. If 0, use the system default (typically the number
    of hardware threads on the compute node).

Returns
-------
numpy.ndarray (same shape and data type as `a`)
    The transformed data

Notes
-----
Mathematically this function performs exactly the same operations as
:func:`c2c` (with ``forward=True``), but returns a real-valued array containing
:math:`\Re(a)-\Im(a)`, where :math:`a` is the :func:`c2c` output.
)""";

const char *dct_DS = R"""(Performs a discrete cosine transform.

Parameters
----------
a : numpy.ndarray (any real type)
    The input data
type : integer
    the type of DCT. Must be in [1; 4].
axes : list of integers
    The axes along which the transform is carried out.
    If not set, this is assumed to be `list(range(a.ndim))`.
    Axes will be transformed in the specified order.
inorm : integer
    the normalization type
      | 0 : no normalization
      | 1 : make transform orthogonal and divide by sqrt(N)
      | 2 : divide by N

    where N is the product of n_i for every transformed axis i.
    n_i is 2*(<axis_length>-1 for type 1 and 2*<axis length>
    for types 2, 3, 4.
    Making the transform orthogonal involves the following additional steps
    for every 1D sub-transform:

    Type 1
      multiply first and last input value by sqrt(2);
      divide first and last output value by sqrt(2)
    Type 2
      divide first output value by sqrt(2)
    Type 3
      multiply first input value by sqrt(2)
    Type 4
      nothing

out : numpy.ndarray (same shape and data type as `a`)
    May be identical to `a`, but if it isn't, it must not overlap with `a`.
    If None, a new array is allocated to store the output.
nthreads : int
    Number of threads to use. If 0, use the system default (typically the number
    of hardware threads on the compute node).

Returns
-------
numpy.ndarray (same shape and data type as `a`)
    The transformed data
)""";

const char *dst_DS = R"""(Performs a discrete sine transform.

Parameters
----------
a : numpy.ndarray (any real type)
    The input data
type : integer
    the type of DST. Must be in [1; 4].
axes : list of integers
    The axes along which the transform is carried out.
    If not set, this is assumed to be `list(range(a.ndim))`.
    Axes will be transformed in the specified order.
inorm : int
    Normalization type
      | 0 : no normalization
      | 1 : make transform orthogonal and divide by sqrt(N)
      | 2 : divide by N

    where N is the product of n_i for every transformed axis i.
    n_i is 2*(<axis_length>+1 for type 1 and 2*<axis length>
    for types 2, 3, 4.
    Making the transform orthogonal involves the following additional steps
    for every 1D sub-transform:

    Type 1
      nothing
    Type 2
      divide last output value by sqrt(2)
    Type 3
      multiply last input value by sqrt(2)
    Type 4
      nothing

out : numpy.ndarray (same shape and data type as `a`)
    May be identical to `a`, but if it isn't, it must not overlap with `a`.
    If None, a new array is allocated to store the output.
nthreads : int
    Number of threads to use. If 0, use the system default (typically the number
    of hardware threads on the compute node).

Returns
-------
numpy.ndarray (same shape and data type as `a`)
    The transformed data
)""";

const char *convolve_axis_DS = R"""(Performs a circular convolution along one axis.

The result is equivalent to

.. code-block:: Python

    import scipy.ndimage
    import scipy.signal
    import scipy.fft
    kernel = scipy.fft.fftshift(kernel)
    tmp = scipy.ndimage.convolve1d(in, kernel, axis, mode='wrap')
    out[()] = scipy.signal.resample(tmp, out.shape[axis], axis=axis)
    return out

Parameters
----------
in : numpy.ndarray (any real or complex type)
    The input data
out : numpy.ndarray (same type as `in`)
    The output data. Must have the same shape as `in` except for the axis
    to be convolved
axis : integer
    The axis along which the convolution is carried out.
kernel : one-dimensional numpy.ndarray (same type as `in`)
    The kernel to be used for convolution
    The length of this array must be equal to in.shape[axis]
nthreads : int
    Number of threads to use. If 0, use the system default (typically the number
    of hardware threads on the compute node).

Returns
-------
numpy.ndarray (identical to `out`)
    The convolved input

Notes
-----
The main purpose of this routine is efficiency: the combination of the above
operations can be carried out more quickly than running the individual
operations in succession.

If `in.shape[axis]!=out.shape[axis]`, the appropriate amount of zero-padding or
truncation will be carried out after the convolution step.

`in` and `out` may overlap in memory. If they do, their first elements must
be at the same memory location, and all their strides must be equal.
)""";

const char * good_size_DS = R"""(Returns a good length to pad an FFT to.

Parameters
----------
n : int
    Minimum transform length
real : bool, optional
    True if either input or output of FFT should be fully real.

Returns
-------
out : int
    The smallest fast size >= n

)""";

} // unnamed namespace

void add_fft(py::module_ &msup)
  {
  using namespace py::literals;
  auto m = msup.def_submodule("fft");
  m.doc() = fft_DS;
  m.def("c2c", c2c, c2c_DS, "a"_a, "axes"_a=None, "forward"_a=true,
    "inorm"_a=0, "out"_a=None, "nthreads"_a=1);
  m.def("r2c", r2c, r2c_DS, "a"_a, "axes"_a=None, "forward"_a=true,
    "inorm"_a=0, "out"_a=None, "nthreads"_a=1);
  m.def("c2r", c2r, c2r_DS, "a"_a, "axes"_a=None, "lastsize"_a=0,
    "forward"_a=true, "inorm"_a=0, "out"_a=None, "nthreads"_a=1,
    "allow_overwriting_input"_a=false);
  m.def("r2r_fftpack", r2r_fftpack, r2r_fftpack_DS, "a"_a, "axes"_a,
    "real2hermitian"_a, "forward"_a, "inorm"_a=0, "out"_a=None, "nthreads"_a=1);
  m.def("r2r_fftw", r2r_fftw, r2r_fftw_DS, "a"_a, "axes"_a,
    "forward"_a, "inorm"_a=0, "out"_a=None, "nthreads"_a=1);
  m.def("separable_hartley", separable_hartley, separable_hartley_DS, "a"_a,
    "axes"_a=None, "inorm"_a=0, "out"_a=None, "nthreads"_a=1);
  m.def("genuine_hartley", genuine_hartley, genuine_hartley_DS, "a"_a,
    "axes"_a=None, "inorm"_a=0, "out"_a=None, "nthreads"_a=1);
  m.def("separable_fht", separable_fht, separable_fht_DS, "a"_a,
    "axes"_a=None, "inorm"_a=0, "out"_a=None, "nthreads"_a=1);
  m.def("genuine_fht", genuine_fht, genuine_fht_DS, "a"_a,
    "axes"_a=None, "inorm"_a=0, "out"_a=None, "nthreads"_a=1);
  m.def("dct", dct, dct_DS, "a"_a, "type"_a, "axes"_a=None, "inorm"_a=0,
    "out"_a=None, "nthreads"_a=1);
  m.def("dst", dst, dst_DS, "a"_a, "type"_a, "axes"_a=None, "inorm"_a=0,
    "out"_a=None, "nthreads"_a=1);
  m.def("convolve_axis", convolve_axis, convolve_axis_DS, "in"_a, "out"_a,
    "axis"_a, "kernel"_a, "nthreads"_a=1);

  static PyMethodDef good_size_meth[] =
    {{"good_size", good_size, METH_VARARGS, good_size_DS},
     {nullptr, nullptr, 0, nullptr}};
  PyModule_AddFunctions(m.ptr(), good_size_meth);
  }

}

using detail_pymodule_fft::add_fft;

}
