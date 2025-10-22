/* mini-gmp, a minimalistic implementation of a GNU GMP subset.

   Contributed to the GNU project by Niels Möller
   Additional functionalities and improvements by Marco Bodrato.

Copyright 1991-1997, 1999-2022 Free Software Foundation, Inc.

This file is part of the GNU MP Library.

The GNU MP Library is free software; you can redistribute it and/or modify
it under the terms of either:

  * the GNU Lesser General Public License as published by the Free
    Software Foundation; either version 3 of the License, or (at your
    option) any later version.

or

  * the GNU General Public License as published by the Free Software
    Foundation; either version 2 of the License, or (at your option) any
    later version.

or both in parallel, as here.

The GNU MP Library is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
for more details.

You should have received copies of the GNU General Public License and the
GNU Lesser General Public License aba0_int_p with the GNU MP Library.  If not,
see https://www.gnu.org/licenses/.  */

/* NOTE: All functions in this file which are not declared in
   mini-gmp.h are internal, and are not intended to be compatible
   with GMP or with future versions of mini-gmp. */

/* Much of the material copied from GMP files, including: gmp-impl.h,
   ba0_int_pba0_int_p.h, mpn/generic/add_n.c, mpn/generic/addmul_1.c,
   mpn/generic/lshift.c, mpn/generic/mul_1.c,
   mpn/generic/mul_basecase.c, mpn/generic/rshift.c,
   mpn/generic/sbpi1_div_qr.c, mpn/generic/sub_n.c,
   mpn/generic/submul_1.c. */

#include <assert.h>
#include <ctype.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "mini-gmp.h"

#if !defined(MINI_GMP_DONT_USE_FLOAT_H)
#include <float.h>
#endif

/* Macros */
#define GMP_LIMB_BITS (sizeof(bam_mp_limb_t) * CHAR_BIT)

#define GMP_LIMB_MAX ((bam_mp_limb_t) ~ (bam_mp_limb_t) 0)
#define GMP_LIMB_HIGHBIT ((bam_mp_limb_t) 1 << (GMP_LIMB_BITS - 1))

#define GMP_HLIMB_BIT ((bam_mp_limb_t) 1 << (GMP_LIMB_BITS / 2))
#define GMP_LLIMB_MASK (GMP_HLIMB_BIT - 1)

#define GMP_ULONG_BITS (sizeof(unsigned ba0_int_p) * CHAR_BIT)
#define GMP_ULONG_HIGHBIT ((unsigned ba0_int_p) 1 << (GMP_ULONG_BITS - 1))

#define GMP_ABS(x) ((x) >= 0 ? (x) : -(x))
#define GMP_NEG_CAST(T,x) (-((T)((x) + 1) - 1))

#define GMP_MIN(a, b) ((a) < (b) ? (a) : (b))
#define GMP_MAX(a, b) ((a) > (b) ? (a) : (b))

#define GMP_CMP(a,b) (((a) > (b)) - ((a) < (b)))

#if defined(DBL_MANT_DIG) && FLT_RADIX == 2
#define GMP_DBL_MANT_BITS DBL_MANT_DIG
#else
#define GMP_DBL_MANT_BITS (53)
#endif

/* Return non-zero if xp,xsize and yp,ysize overlap.
   If xp+xsize<=yp there's no overlap, or if yp+ysize<=xp there's no
   overlap.  If both these are false, there's an overlap. */
#define GMP_MPN_OVERLAP_P(xp, xsize, yp, ysize)                \
  ((xp) + (xsize) > (yp) && (yp) + (ysize) > (xp))

#define bam_gmp_assert_nocarry(x) do { \
    bam_mp_limb_t __cy = (x);       \
    assert (__cy == 0);           \
    (void) (__cy);           \
  } while (0)

#define bam_gmp_clz(count, x) do {                        \
    bam_mp_limb_t __clz_x = (x);                        \
    unsigned __clz_c = 0;                        \
    int LOCAL_SHIFT_BITS = 8;                        \
    if (GMP_LIMB_BITS > LOCAL_SHIFT_BITS)                \
      for (;                                \
       (__clz_x & ((bam_mp_limb_t) 0xff << (GMP_LIMB_BITS - 8))) == 0;    \
       __clz_c += 8)                        \
    { __clz_x <<= LOCAL_SHIFT_BITS;    }                \
    for (; (__clz_x & GMP_LIMB_HIGHBIT) == 0; __clz_c++)        \
      __clz_x <<= 1;                            \
    (count) = __clz_c;                            \
  } while (0)

#define bam_gmp_ctz(count, x) do {                        \
    bam_mp_limb_t __ctz_x = (x);                        \
    unsigned __ctz_c = 0;                        \
    bam_gmp_clz (__ctz_c, __ctz_x & - __ctz_x);                \
    (count) = GMP_LIMB_BITS - 1 - __ctz_c;                \
  } while (0)

#define bam_gmp_add_ssaaaa(sh, sl, ah, al, bh, bl) \
  do {                                    \
    bam_mp_limb_t __x;                            \
    __x = (al) + (bl);                            \
    (sh) = (ah) + (bh) + (__x < (al));                    \
    (sl) = __x;                                \
  } while (0)

#define bam_gmp_sub_ddmmss(sh, sl, ah, al, bh, bl) \
  do {                                    \
    bam_mp_limb_t __x;                            \
    __x = (al) - (bl);                            \
    (sh) = (ah) - (bh) - ((al) < (bl));                    \
    (sl) = __x;                                \
  } while (0)

#define bam_gmp_umul_ppmm(w1, w0, u, v)                    \
  do {                                    \
    int LOCAL_GMP_LIMB_BITS = GMP_LIMB_BITS;                \
    if (sizeof(unsigned int) * CHAR_BIT >= 2 * GMP_LIMB_BITS)        \
      {                                    \
    unsigned int __ww = (unsigned int) (u) * (v);            \
    w0 = (bam_mp_limb_t) __ww;                        \
    w1 = (bam_mp_limb_t) (__ww >> LOCAL_GMP_LIMB_BITS);            \
      }                                    \
    else if (GMP_ULONG_BITS >= 2 * GMP_LIMB_BITS)            \
      {                                    \
    unsigned ba0_int_p __ww = (unsigned ba0_int_p) (u) * (v);        \
    w0 = (bam_mp_limb_t) __ww;                        \
    w1 = (bam_mp_limb_t) (__ww >> LOCAL_GMP_LIMB_BITS);            \
      }                                    \
    else {                                \
      bam_mp_limb_t __x0, __x1, __x2, __x3;                    \
      unsigned __ul, __vl, __uh, __vh;                    \
      bam_mp_limb_t __u = (u), __v = (v);                    \
      assert (sizeof (unsigned) * 2 >= sizeof (bam_mp_limb_t));        \
                                    \
      __ul = __u & GMP_LLIMB_MASK;                    \
      __uh = __u >> (GMP_LIMB_BITS / 2);                \
      __vl = __v & GMP_LLIMB_MASK;                    \
      __vh = __v >> (GMP_LIMB_BITS / 2);                \
                                    \
      __x0 = (bam_mp_limb_t) __ul * __vl;                    \
      __x1 = (bam_mp_limb_t) __ul * __vh;                    \
      __x2 = (bam_mp_limb_t) __uh * __vl;                    \
      __x3 = (bam_mp_limb_t) __uh * __vh;                    \
                                    \
      __x1 += __x0 >> (GMP_LIMB_BITS / 2);/* this can't give carry */    \
      __x1 += __x2;        /* but this indeed can */        \
      if (__x1 < __x2)        /* did we get it? */            \
    __x3 += GMP_HLIMB_BIT;    /* yes, add it in the proper pos. */    \
                                    \
      (w1) = __x3 + (__x1 >> (GMP_LIMB_BITS / 2));            \
      (w0) = (__x1 << (GMP_LIMB_BITS / 2)) + (__x0 & GMP_LLIMB_MASK);    \
    }                                    \
  } while (0)

/* If bam_mp_limb_t is of size smaller than int, plain u*v implies
   automatic promotion to *signed* int, and then multiply may overflow
   and cause undefined behavior. Explicitly cast to unsigned int for
   that case. */
#define bam_gmp_umullo_limb(u, v) \
  ((sizeof(bam_mp_limb_t) >= sizeof(int)) ? (u)*(v) : (unsigned int)(u) * (v))

#define bam_gmp_udiv_qrnnd_preinv(q, r, nh, nl, d, di)            \
  do {                                    \
    bam_mp_limb_t _qh, _ql, _r, _mask;                    \
    bam_gmp_umul_ppmm (_qh, _ql, (nh), (di));                \
    bam_gmp_add_ssaaaa (_qh, _ql, _qh, _ql, (nh) + 1, (nl));        \
    _r = (nl) - bam_gmp_umullo_limb (_qh, (d));                \
    _mask = -(bam_mp_limb_t) (_r > _ql); /* both > and >= are OK */        \
    _qh += _mask;                            \
    _r += _mask & (d);                            \
    if (_r >= (d))                            \
      {                                    \
    _r -= (d);                            \
    _qh++;                                \
      }                                    \
                                    \
    (r) = _r;                                \
    (q) = _qh;                                \
  } while (0)

#define bam_gmp_udiv_qr_3by2(q, r1, r0, n2, n1, n0, d1, d0, dinv)        \
  do {                                    \
    bam_mp_limb_t _q0, _t1, _t0, _mask;                    \
    bam_gmp_umul_ppmm ((q), _q0, (n2), (dinv));                \
    bam_gmp_add_ssaaaa ((q), _q0, (q), _q0, (n2), (n1));            \
                                    \
    /* Compute the two most significant limbs of n - q'd */        \
    (r1) = (n1) - bam_gmp_umullo_limb ((d1), (q));                \
    bam_gmp_sub_ddmmss ((r1), (r0), (r1), (n0), (d1), (d0));        \
    bam_gmp_umul_ppmm (_t1, _t0, (d0), (q));                \
    bam_gmp_sub_ddmmss ((r1), (r0), (r1), (r0), _t1, _t0);            \
    (q)++;                                \
                                    \
    /* Conditionally adjust q and the remainders */            \
    _mask = - (bam_mp_limb_t) ((r1) >= _q0);                \
    (q) += _mask;                            \
    bam_gmp_add_ssaaaa ((r1), (r0), (r1), (r0), _mask & (d1), _mask & (d0)); \
    if ((r1) >= (d1))                            \
      {                                    \
    if ((r1) > (d1) || (r0) >= (d0))                \
      {                                \
        (q)++;                            \
        bam_gmp_sub_ddmmss ((r1), (r0), (r1), (r0), (d1), (d0));    \
      }                                \
      }                                    \
  } while (0)

/* Swap macros. */
#define MP_LIMB_T_SWAP(x, y)                        \
  do {                                    \
    bam_mp_limb_t __mp_limb_t_swap__tmp = (x);                \
    (x) = (y);                                \
    (y) = __mp_limb_t_swap__tmp;                    \
  } while (0)
#define MP_SIZE_T_SWAP(x, y)                        \
  do {                                    \
    bam_mp_size_t __mp_size_t_swap__tmp = (x);                \
    (x) = (y);                                \
    (y) = __mp_size_t_swap__tmp;                    \
  } while (0)
#define MP_BITCNT_T_SWAP(x,y)            \
  do {                        \
    bam_mp_bitcnt_t __mp_bitcnt_t_swap__tmp = (x);    \
    (x) = (y);                    \
    (y) = __mp_bitcnt_t_swap__tmp;        \
  } while (0)
#define MP_PTR_SWAP(x, y)                        \
  do {                                    \
    bam_mp_ptr __mp_ptr_swap__tmp = (x);                    \
    (x) = (y);                                \
    (y) = __mp_ptr_swap__tmp;                        \
  } while (0)
#define MP_SRCPTR_SWAP(x, y)                        \
  do {                                    \
    bam_mp_srcptr __mp_srcptr_swap__tmp = (x);                \
    (x) = (y);                                \
    (y) = __mp_srcptr_swap__tmp;                    \
  } while (0)

#define MPN_PTR_SWAP(xp,xs, yp,ys)                    \
  do {                                    \
    MP_PTR_SWAP (xp, yp);                        \
    MP_SIZE_T_SWAP (xs, ys);                        \
  } while(0)
#define MPN_SRCPTR_SWAP(xp,xs, yp,ys)                    \
  do {                                    \
    MP_SRCPTR_SWAP (xp, yp);                        \
    MP_SIZE_T_SWAP (xs, ys);                        \
  } while(0)

#define MPZ_PTR_SWAP(x, y)                        \
  do {                                    \
    bam_mpz_ptr bam__mpz_ptr_swap__tmp = (x);                    \
    (x) = (y);                                \
    (y) = bam__mpz_ptr_swap__tmp;                        \
  } while (0)
#define MPZ_SRCPTR_SWAP(x, y)                        \
  do {                                    \
    bam_mpz_srcptr bam__mpz_srcptr_swap__tmp = (x);                \
    (x) = (y);                                \
    (y) = bam__mpz_srcptr_swap__tmp;                    \
  } while (0)

const int bam_mp_bits_per_limb = GMP_LIMB_BITS;

/* Memory allocation and other helper functions. */
static void
bam_gmp_die (const char *msg)
{
  fprintf (stderr, "%s\n", msg);
  abort();
}

static void *
bam_gmp_default_alloc (size_t size)
{
  void *p;

  assert (size > 0);

  p = malloc (size);
  if (!p)
    bam_gmp_die("bam_gmp_default_alloc: Virtual memory exhausted.");

  return p;
}

static void *
bam_gmp_default_realloc (void *old, size_t unused_old_size, size_t new_size)
{
  void * p;

  p = realloc (old, new_size);

  if (!p)
    bam_gmp_die("bam_gmp_default_realloc: Virtual memory exhausted.");

  return p;
}

static void
bam_gmp_default_free (void *p, size_t unused_size)
{
  free (p);
}

static void * (*bam_gmp_allocate_func) (size_t) = bam_gmp_default_alloc;
static void * (*bam_gmp_reallocate_func) (void *, size_t, size_t) = bam_gmp_default_realloc;
static void (*bam_gmp_free_func) (void *, size_t) = bam_gmp_default_free;

void
bam_mp_get_memory_functions (void *(**alloc_func) (size_t),
             void *(**realloc_func) (void *, size_t, size_t),
             void (**free_func) (void *, size_t))
{
  if (alloc_func)
    *alloc_func = bam_gmp_allocate_func;

  if (realloc_func)
    *realloc_func = bam_gmp_reallocate_func;

  if (free_func)
    *free_func = bam_gmp_free_func;
}

void
bam_mp_set_memory_functions (void *(*alloc_func) (size_t),
             void *(*realloc_func) (void *, size_t, size_t),
             void (*free_func) (void *, size_t))
{
  if (!alloc_func)
    alloc_func = bam_gmp_default_alloc;
  if (!realloc_func)
    realloc_func = bam_gmp_default_realloc;
  if (!free_func)
    free_func = bam_gmp_default_free;

  bam_gmp_allocate_func = alloc_func;
  bam_gmp_reallocate_func = realloc_func;
  bam_gmp_free_func = free_func;
}

#define bam_gmp_alloc(size) ((*bam_gmp_allocate_func)((size)))
#define bam_gmp_free(p, size) ((*bam_gmp_free_func) ((p), (size)))
#define bam_gmp_realloc(ptr, old_size, size) ((*bam_gmp_reallocate_func)(ptr, old_size, size))

static bam_mp_ptr
bam_gmp_alloc_limbs (bam_mp_size_t size)
{
  return (bam_mp_ptr) bam_gmp_alloc (size * sizeof (bam_mp_limb_t));
}

static bam_mp_ptr
bam_gmp_realloc_limbs (bam_mp_ptr old, bam_mp_size_t old_size, bam_mp_size_t size)
{
  assert (size > 0);
  return (bam_mp_ptr) bam_gmp_realloc (old, old_size * sizeof (bam_mp_limb_t), size * sizeof (bam_mp_limb_t));
}

static void
bam_gmp_free_limbs (bam_mp_ptr old, bam_mp_size_t size)
{
  bam_gmp_free (old, size * sizeof (bam_mp_limb_t));
}

/* MPN interface */

void
bam_mpn_copyi (bam_mp_ptr d, bam_mp_srcptr s, bam_mp_size_t n)
{
  bam_mp_size_t i;
  for (i = 0; i < n; i++)
    d[i] = s[i];
}

void
bam_mpn_copyd (bam_mp_ptr d, bam_mp_srcptr s, bam_mp_size_t n)
{
  while (--n >= 0)
    d[n] = s[n];
}

int
bam_mpn_cmp (bam_mp_srcptr ap, bam_mp_srcptr bp, bam_mp_size_t n)
{
  while (--n >= 0)
    {
      if (ap[n] != bp[n])
    return ap[n] > bp[n] ? 1 : -1;
    }
  return 0;
}

static int
bam_mpn_cmp4 (bam_mp_srcptr ap, bam_mp_size_t an, bam_mp_srcptr bp, bam_mp_size_t bn)
{
  if (an != bn)
    return an < bn ? -1 : 1;
  else
    return bam_mpn_cmp (ap, bp, an);
}

static bam_mp_size_t
bam_mpn_normalized_size (bam_mp_srcptr xp, bam_mp_size_t n)
{
  while (n > 0 && xp[n-1] == 0)
    --n;
  return n;
}

int
bam_mpn_zero_p(bam_mp_srcptr rp, bam_mp_size_t n)
{
  return bam_mpn_normalized_size (rp, n) == 0;
}

void
bam_mpn_zero (bam_mp_ptr rp, bam_mp_size_t n)
{
  while (--n >= 0)
    rp[n] = 0;
}

bam_mp_limb_t
bam_mpn_add_1 (bam_mp_ptr rp, bam_mp_srcptr ap, bam_mp_size_t n, bam_mp_limb_t b)
{
  bam_mp_size_t i;

  assert (n > 0);
  i = 0;
  do
    {
      bam_mp_limb_t r = ap[i] + b;
      /* Carry out */
      b = (r < b);
      rp[i] = r;
    }
  while (++i < n);

  return b;
}

bam_mp_limb_t
bam_mpn_add_n (bam_mp_ptr rp, bam_mp_srcptr ap, bam_mp_srcptr bp, bam_mp_size_t n)
{
  bam_mp_size_t i;
  bam_mp_limb_t cy;

  for (i = 0, cy = 0; i < n; i++)
    {
      bam_mp_limb_t a, b, r;
      a = ap[i]; b = bp[i];
      r = a + cy;
      cy = (r < cy);
      r += b;
      cy += (r < b);
      rp[i] = r;
    }
  return cy;
}

bam_mp_limb_t
bam_mpn_add (bam_mp_ptr rp, bam_mp_srcptr ap, bam_mp_size_t an, bam_mp_srcptr bp, bam_mp_size_t bn)
{
  bam_mp_limb_t cy;

  assert (an >= bn);

  cy = bam_mpn_add_n (rp, ap, bp, bn);
  if (an > bn)
    cy = bam_mpn_add_1 (rp + bn, ap + bn, an - bn, cy);
  return cy;
}

bam_mp_limb_t
bam_mpn_sub_1 (bam_mp_ptr rp, bam_mp_srcptr ap, bam_mp_size_t n, bam_mp_limb_t b)
{
  bam_mp_size_t i;

  assert (n > 0);

  i = 0;
  do
    {
      bam_mp_limb_t a = ap[i];
      /* Carry out */
      bam_mp_limb_t cy = a < b;
      rp[i] = a - b;
      b = cy;
    }
  while (++i < n);

  return b;
}

bam_mp_limb_t
bam_mpn_sub_n (bam_mp_ptr rp, bam_mp_srcptr ap, bam_mp_srcptr bp, bam_mp_size_t n)
{
  bam_mp_size_t i;
  bam_mp_limb_t cy;

  for (i = 0, cy = 0; i < n; i++)
    {
      bam_mp_limb_t a, b;
      a = ap[i]; b = bp[i];
      b += cy;
      cy = (b < cy);
      cy += (a < b);
      rp[i] = a - b;
    }
  return cy;
}

bam_mp_limb_t
bam_mpn_sub (bam_mp_ptr rp, bam_mp_srcptr ap, bam_mp_size_t an, bam_mp_srcptr bp, bam_mp_size_t bn)
{
  bam_mp_limb_t cy;

  assert (an >= bn);

  cy = bam_mpn_sub_n (rp, ap, bp, bn);
  if (an > bn)
    cy = bam_mpn_sub_1 (rp + bn, ap + bn, an - bn, cy);
  return cy;
}

bam_mp_limb_t
bam_mpn_mul_1 (bam_mp_ptr rp, bam_mp_srcptr up, bam_mp_size_t n, bam_mp_limb_t vl)
{
  bam_mp_limb_t ul, cl, hpl, lpl;

  assert (n >= 1);

  cl = 0;
  do
    {
      ul = *up++;
      bam_gmp_umul_ppmm (hpl, lpl, ul, vl);

      lpl += cl;
      cl = (lpl < cl) + hpl;

      *rp++ = lpl;
    }
  while (--n != 0);

  return cl;
}

bam_mp_limb_t
bam_mpn_addmul_1 (bam_mp_ptr rp, bam_mp_srcptr up, bam_mp_size_t n, bam_mp_limb_t vl)
{
  bam_mp_limb_t ul, cl, hpl, lpl, rl;

  assert (n >= 1);

  cl = 0;
  do
    {
      ul = *up++;
      bam_gmp_umul_ppmm (hpl, lpl, ul, vl);

      lpl += cl;
      cl = (lpl < cl) + hpl;

      rl = *rp;
      lpl = rl + lpl;
      cl += lpl < rl;
      *rp++ = lpl;
    }
  while (--n != 0);

  return cl;
}

bam_mp_limb_t
bam_mpn_submul_1 (bam_mp_ptr rp, bam_mp_srcptr up, bam_mp_size_t n, bam_mp_limb_t vl)
{
  bam_mp_limb_t ul, cl, hpl, lpl, rl;

  assert (n >= 1);

  cl = 0;
  do
    {
      ul = *up++;
      bam_gmp_umul_ppmm (hpl, lpl, ul, vl);

      lpl += cl;
      cl = (lpl < cl) + hpl;

      rl = *rp;
      lpl = rl - lpl;
      cl += lpl > rl;
      *rp++ = lpl;
    }
  while (--n != 0);

  return cl;
}

bam_mp_limb_t
bam_mpn_mul (bam_mp_ptr rp, bam_mp_srcptr up, bam_mp_size_t un, bam_mp_srcptr vp, bam_mp_size_t vn)
{
  assert (un >= vn);
  assert (vn >= 1);
  assert (!GMP_MPN_OVERLAP_P(rp, un + vn, up, un));
  assert (!GMP_MPN_OVERLAP_P(rp, un + vn, vp, vn));

  /* We first multiply by the low order limb. This result can be
     stored, not added, to rp. We also avoid a loop for zeroing this
     way. */

  rp[un] = bam_mpn_mul_1 (rp, up, un, vp[0]);

  /* Now accumulate the product of up[] and the next higher limb from
     vp[]. */

  while (--vn >= 1)
    {
      rp += 1, vp += 1;
      rp[un] = bam_mpn_addmul_1 (rp, up, un, vp[0]);
    }
  return rp[un];
}

void
bam_mpn_mul_n (bam_mp_ptr rp, bam_mp_srcptr ap, bam_mp_srcptr bp, bam_mp_size_t n)
{
  bam_mpn_mul (rp, ap, n, bp, n);
}

void
bam_mpn_sqr (bam_mp_ptr rp, bam_mp_srcptr ap, bam_mp_size_t n)
{
  bam_mpn_mul (rp, ap, n, ap, n);
}

bam_mp_limb_t
bam_mpn_lshift (bam_mp_ptr rp, bam_mp_srcptr up, bam_mp_size_t n, unsigned int cnt)
{
  bam_mp_limb_t high_limb, low_limb;
  unsigned int tnc;
  bam_mp_limb_t retval;

  assert (n >= 1);
  assert (cnt >= 1);
  assert (cnt < GMP_LIMB_BITS);

  up += n;
  rp += n;

  tnc = GMP_LIMB_BITS - cnt;
  low_limb = *--up;
  retval = low_limb >> tnc;
  high_limb = (low_limb << cnt);

  while (--n != 0)
    {
      low_limb = *--up;
      *--rp = high_limb | (low_limb >> tnc);
      high_limb = (low_limb << cnt);
    }
  *--rp = high_limb;

  return retval;
}

bam_mp_limb_t
bam_mpn_rshift (bam_mp_ptr rp, bam_mp_srcptr up, bam_mp_size_t n, unsigned int cnt)
{
  bam_mp_limb_t high_limb, low_limb;
  unsigned int tnc;
  bam_mp_limb_t retval;

  assert (n >= 1);
  assert (cnt >= 1);
  assert (cnt < GMP_LIMB_BITS);

  tnc = GMP_LIMB_BITS - cnt;
  high_limb = *up++;
  retval = (high_limb << tnc);
  low_limb = high_limb >> cnt;

  while (--n != 0)
    {
      high_limb = *up++;
      *rp++ = low_limb | (high_limb << tnc);
      low_limb = high_limb >> cnt;
    }
  *rp = low_limb;

  return retval;
}

static bam_mp_bitcnt_t
bam_mpn_common_scan (bam_mp_limb_t limb, bam_mp_size_t i, bam_mp_srcptr up, bam_mp_size_t un,
         bam_mp_limb_t ux)
{
  unsigned cnt;

  assert (ux == 0 || ux == GMP_LIMB_MAX);
  assert (0 <= i && i <= un );

  while (limb == 0)
    {
      i++;
      if (i == un)
    return (ux == 0 ? ~(bam_mp_bitcnt_t) 0 : un * GMP_LIMB_BITS);
      limb = ux ^ up[i];
    }
  bam_gmp_ctz (cnt, limb);
  return (bam_mp_bitcnt_t) i * GMP_LIMB_BITS + cnt;
}

bam_mp_bitcnt_t
bam_mpn_scan1 (bam_mp_srcptr ptr, bam_mp_bitcnt_t bit)
{
  bam_mp_size_t i;
  i = bit / GMP_LIMB_BITS;

  return bam_mpn_common_scan ( ptr[i] & (GMP_LIMB_MAX << (bit % GMP_LIMB_BITS)),
              i, ptr, i, 0);
}

bam_mp_bitcnt_t
bam_mpn_scan0 (bam_mp_srcptr ptr, bam_mp_bitcnt_t bit)
{
  bam_mp_size_t i;
  i = bit / GMP_LIMB_BITS;

  return bam_mpn_common_scan (~ptr[i] & (GMP_LIMB_MAX << (bit % GMP_LIMB_BITS)),
              i, ptr, i, GMP_LIMB_MAX);
}

void
bam_mpn_com (bam_mp_ptr rp, bam_mp_srcptr up, bam_mp_size_t n)
{
  while (--n >= 0)
    *rp++ = ~ *up++;
}

bam_mp_limb_t
bam_mpn_neg (bam_mp_ptr rp, bam_mp_srcptr up, bam_mp_size_t n)
{
  while (*up == 0)
    {
      *rp = 0;
      if (!--n)
    return 0;
      ++up; ++rp;
    }
  *rp = - *up;
  bam_mpn_com (++rp, ++up, --n);
  return 1;
}

/* MPN division interface. */

/* The 3/2 inverse is defined as

     m = floor( (B^3-1) / (B u1 + u0)) - B
*/
bam_mp_limb_t
bam_mpn_invert_3by2 (bam_mp_limb_t u1, bam_mp_limb_t u0)
{
  bam_mp_limb_t r, m;

  {
    bam_mp_limb_t p, ql;
    unsigned ul, uh, qh;

    assert (sizeof (unsigned) * 2 >= sizeof (bam_mp_limb_t));
    /* For notation, let b denote the half-limb base, so that B = b^2.
       Split u1 = b uh + ul. */
    ul = u1 & GMP_LLIMB_MASK;
    uh = u1 >> (GMP_LIMB_BITS / 2);

    /* Approximation of the high half of quotient. Differs from the 2/1
       inverse of the half limb uh, since we have already subtracted
       u0. */
    qh = (u1 ^ GMP_LIMB_MAX) / uh;

    /* Adjust to get a half-limb 3/2 inverse, i.e., we want

       qh' = floor( (b^3 - 1) / u) - b = floor ((b^3 - b u - 1) / u
       = floor( (b (~u) + b-1) / u),

       and the remainder

       r = b (~u) + b-1 - qh (b uh + ul)
       = b (~u - qh uh) + b-1 - qh ul

       Subtraction of qh ul may underflow, which implies adjustments.
       But by normalization, 2 u >= B > qh ul, so we need to adjust by
       at most 2.
    */

    r = ((~u1 - (bam_mp_limb_t) qh * uh) << (GMP_LIMB_BITS / 2)) | GMP_LLIMB_MASK;

    p = (bam_mp_limb_t) qh * ul;
    /* Adjustment steps taken from udiv_qrnnd_c */
    if (r < p)
      {
    qh--;
    r += u1;
    if (r >= u1) /* i.e. we didn't get carry when adding to r */
      if (r < p)
        {
          qh--;
          r += u1;
        }
      }
    r -= p;

    /* Low half of the quotient is

       ql = floor ( (b r + b-1) / u1).

       This is a 3/2 division (on half-limbs), for which qh is a
       suitable inverse. */

    p = (r >> (GMP_LIMB_BITS / 2)) * qh + r;
    /* Unlike full-limb 3/2, we can add 1 without overflow. For this to
       work, it is essential that ql is a full bam_mp_limb_t. */
    ql = (p >> (GMP_LIMB_BITS / 2)) + 1;

    /* By the 3/2 trick, we don't need the high half limb. */
    r = (r << (GMP_LIMB_BITS / 2)) + GMP_LLIMB_MASK - ql * u1;

    if (r >= (GMP_LIMB_MAX & (p << (GMP_LIMB_BITS / 2))))
      {
    ql--;
    r += u1;
      }
    m = ((bam_mp_limb_t) qh << (GMP_LIMB_BITS / 2)) + ql;
    if (r >= u1)
      {
    m++;
    r -= u1;
      }
  }

  /* Now m is the 2/1 inverse of u1. If u0 > 0, adjust it to become a
     3/2 inverse. */
  if (u0 > 0)
    {
      bam_mp_limb_t th, tl;
      r = ~r;
      r += u0;
      if (r < u0)
    {
      m--;
      if (r >= u1)
        {
          m--;
          r -= u1;
        }
      r -= u1;
    }
      bam_gmp_umul_ppmm (th, tl, u0, m);
      r += th;
      if (r < th)
    {
      m--;
      m -= ((r > u1) | ((r == u1) & (tl > u0)));
    }
    }

  return m;
}

struct bam_gmp_div_inverse
{
  /* Normalization shift count. */
  unsigned shift;
  /* Normalized divisor (d0 unused for bam_mpn_div_qr_1) */
  bam_mp_limb_t d1, d0;
  /* Inverse, for 2/1 or 3/2. */
  bam_mp_limb_t di;
};

static void
bam_mpn_div_qr_1_invert (struct bam_gmp_div_inverse *inv, bam_mp_limb_t d)
{
  unsigned shift;

  assert (d > 0);
  bam_gmp_clz (shift, d);
  inv->shift = shift;
  inv->d1 = d << shift;
  inv->di = bam_mpn_invert_limb (inv->d1);
}

static void
bam_mpn_div_qr_2_invert (struct bam_gmp_div_inverse *inv,
             bam_mp_limb_t d1, bam_mp_limb_t d0)
{
  unsigned shift;

  assert (d1 > 0);
  bam_gmp_clz (shift, d1);
  inv->shift = shift;
  if (shift > 0)
    {
      d1 = (d1 << shift) | (d0 >> (GMP_LIMB_BITS - shift));
      d0 <<= shift;
    }
  inv->d1 = d1;
  inv->d0 = d0;
  inv->di = bam_mpn_invert_3by2 (d1, d0);
}

static void
bam_mpn_div_qr_invert (struct bam_gmp_div_inverse *inv,
           bam_mp_srcptr dp, bam_mp_size_t dn)
{
  assert (dn > 0);

  if (dn == 1)
    bam_mpn_div_qr_1_invert (inv, dp[0]);
  else if (dn == 2)
    bam_mpn_div_qr_2_invert (inv, dp[1], dp[0]);
  else
    {
      unsigned shift;
      bam_mp_limb_t d1, d0;

      d1 = dp[dn-1];
      d0 = dp[dn-2];
      assert (d1 > 0);
      bam_gmp_clz (shift, d1);
      inv->shift = shift;
      if (shift > 0)
    {
      d1 = (d1 << shift) | (d0 >> (GMP_LIMB_BITS - shift));
      d0 = (d0 << shift) | (dp[dn-3] >> (GMP_LIMB_BITS - shift));
    }
      inv->d1 = d1;
      inv->d0 = d0;
      inv->di = bam_mpn_invert_3by2 (d1, d0);
    }
}

/* Not matching current public gmp interface, rather corresponding to
   the sbpi1_div_* functions. */
static bam_mp_limb_t
bam_mpn_div_qr_1_preinv (bam_mp_ptr qp, bam_mp_srcptr np, bam_mp_size_t nn,
             const struct bam_gmp_div_inverse *inv)
{
  bam_mp_limb_t d, di;
  bam_mp_limb_t r;
  bam_mp_ptr tp = NULL;
  bam_mp_size_t tn = 0;

  if (inv->shift > 0)
    {
      /* Shift, reusing qp area if possible. In-place shift if qp == np. */
      tp = qp;
      if (!tp)
        {
       tn = nn;
       tp = bam_gmp_alloc_limbs (tn);
        }
      r = bam_mpn_lshift (tp, np, nn, inv->shift);
      np = tp;
    }
  else
    r = 0;

  d = inv->d1;
  di = inv->di;
  while (--nn >= 0)
    {
      bam_mp_limb_t q;

      bam_gmp_udiv_qrnnd_preinv (q, r, r, np[nn], d, di);
      if (qp)
    qp[nn] = q;
    }
  if (tn)
    bam_gmp_free_limbs (tp, tn);

  return r >> inv->shift;
}

static void
bam_mpn_div_qr_2_preinv (bam_mp_ptr qp, bam_mp_ptr np, bam_mp_size_t nn,
             const struct bam_gmp_div_inverse *inv)
{
  unsigned shift;
  bam_mp_size_t i;
  bam_mp_limb_t d1, d0, di, r1, r0;

  assert (nn >= 2);
  shift = inv->shift;
  d1 = inv->d1;
  d0 = inv->d0;
  di = inv->di;

  if (shift > 0)
    r1 = bam_mpn_lshift (np, np, nn, shift);
  else
    r1 = 0;

  r0 = np[nn - 1];

  i = nn - 2;
  do
    {
      bam_mp_limb_t n0, q;
      n0 = np[i];
      bam_gmp_udiv_qr_3by2 (q, r1, r0, r1, r0, n0, d1, d0, di);

      if (qp)
    qp[i] = q;
    }
  while (--i >= 0);

  if (shift > 0)
    {
      assert ((r0 & (GMP_LIMB_MAX >> (GMP_LIMB_BITS - shift))) == 0);
      r0 = (r0 >> shift) | (r1 << (GMP_LIMB_BITS - shift));
      r1 >>= shift;
    }

  np[1] = r1;
  np[0] = r0;
}

static void
bam_mpn_div_qr_pi1 (bam_mp_ptr qp,
        bam_mp_ptr np, bam_mp_size_t nn, bam_mp_limb_t n1,
        bam_mp_srcptr dp, bam_mp_size_t dn,
        bam_mp_limb_t dinv)
{
  bam_mp_size_t i;

  bam_mp_limb_t d1, d0;
  bam_mp_limb_t cy, cy1;
  bam_mp_limb_t q;

  assert (dn > 2);
  assert (nn >= dn);

  d1 = dp[dn - 1];
  d0 = dp[dn - 2];

  assert ((d1 & GMP_LIMB_HIGHBIT) != 0);
  /* Iteration variable is the index of the q limb.
   *
   * We divide <n1, np[dn-1+i], np[dn-2+i], np[dn-3+i],..., np[i]>
   * by            <d1,          d0,        dp[dn-3],  ..., dp[0] >
   */

  i = nn - dn;
  do
    {
      bam_mp_limb_t n0 = np[dn-1+i];

      if (n1 == d1 && n0 == d0)
    {
      q = GMP_LIMB_MAX;
      bam_mpn_submul_1 (np+i, dp, dn, q);
      n1 = np[dn-1+i];    /* update n1, last loop's value will now be invalid */
    }
      else
    {
      bam_gmp_udiv_qr_3by2 (q, n1, n0, n1, n0, np[dn-2+i], d1, d0, dinv);

      cy = bam_mpn_submul_1 (np + i, dp, dn-2, q);

      cy1 = n0 < cy;
      n0 = n0 - cy;
      cy = n1 < cy1;
      n1 = n1 - cy1;
      np[dn-2+i] = n0;

      if (cy != 0)
        {
          n1 += d1 + bam_mpn_add_n (np + i, np + i, dp, dn - 1);
          q--;
        }
    }

      if (qp)
    qp[i] = q;
    }
  while (--i >= 0);

  np[dn - 1] = n1;
}

static void
bam_mpn_div_qr_preinv (bam_mp_ptr qp, bam_mp_ptr np, bam_mp_size_t nn,
           bam_mp_srcptr dp, bam_mp_size_t dn,
           const struct bam_gmp_div_inverse *inv)
{
  assert (dn > 0);
  assert (nn >= dn);

  if (dn == 1)
    np[0] = bam_mpn_div_qr_1_preinv (qp, np, nn, inv);
  else if (dn == 2)
    bam_mpn_div_qr_2_preinv (qp, np, nn, inv);
  else
    {
      bam_mp_limb_t nh;
      unsigned shift;

      assert (inv->d1 == dp[dn-1]);
      assert (inv->d0 == dp[dn-2]);
      assert ((inv->d1 & GMP_LIMB_HIGHBIT) != 0);

      shift = inv->shift;
      if (shift > 0)
    nh = bam_mpn_lshift (np, np, nn, shift);
      else
    nh = 0;

      bam_mpn_div_qr_pi1 (qp, np, nn, nh, dp, dn, inv->di);

      if (shift > 0)
    bam_gmp_assert_nocarry (bam_mpn_rshift (np, np, dn, shift));
    }
}

static void
bam_mpn_div_qr (bam_mp_ptr qp, bam_mp_ptr np, bam_mp_size_t nn, bam_mp_srcptr dp, bam_mp_size_t dn)
{
  struct bam_gmp_div_inverse inv;
  bam_mp_ptr tp = NULL;

  assert (dn > 0);
  assert (nn >= dn);

  bam_mpn_div_qr_invert (&inv, dp, dn);
  if (dn > 2 && inv.shift > 0)
    {
      tp = bam_gmp_alloc_limbs (dn);
      bam_gmp_assert_nocarry (bam_mpn_lshift (tp, dp, dn, inv.shift));
      dp = tp;
    }
  bam_mpn_div_qr_preinv (qp, np, nn, dp, dn, &inv);
  if (tp)
    bam_gmp_free_limbs (tp, dn);
}

/* MPN base conversion. */
static unsigned
bam_mpn_base_power_of_two_p (unsigned b)
{
  switch (b)
    {
    case 2: return 1;
    case 4: return 2;
    case 8: return 3;
    case 16: return 4;
    case 32: return 5;
    case 64: return 6;
    case 128: return 7;
    case 256: return 8;
    default: return 0;
    }
}

struct bam_mpn_base_info
{
  /* bb is the largest power of the base which fits in one limb, and
     exp is the corresponding exponent. */
  unsigned exp;
  bam_mp_limb_t bb;
};

static void
bam_mpn_get_base_info (struct bam_mpn_base_info *info, bam_mp_limb_t b)
{
  bam_mp_limb_t m;
  bam_mp_limb_t p;
  unsigned exp;

  m = GMP_LIMB_MAX / b;
  for (exp = 1, p = b; p <= m; exp++)
    p *= b;

  info->exp = exp;
  info->bb = p;
}

static bam_mp_bitcnt_t
bam_mpn_limb_size_in_base_2 (bam_mp_limb_t u)
{
  unsigned shift;

  assert (u > 0);
  bam_gmp_clz (shift, u);
  return GMP_LIMB_BITS - shift;
}

static size_t
bam_mpn_get_str_bits (unsigned char *sp, unsigned bits, bam_mp_srcptr up, bam_mp_size_t un)
{
  unsigned char mask;
  size_t sn, j;
  bam_mp_size_t i;
  unsigned shift;

  sn = ((un - 1) * GMP_LIMB_BITS + bam_mpn_limb_size_in_base_2 (up[un-1])
    + bits - 1) / bits;

  mask = (1U << bits) - 1;

  for (i = 0, j = sn, shift = 0; j-- > 0;)
    {
      unsigned char digit = up[i] >> shift;

      shift += bits;

      if (shift >= GMP_LIMB_BITS && ++i < un)
    {
      shift -= GMP_LIMB_BITS;
      digit |= up[i] << (bits - shift);
    }
      sp[j] = digit & mask;
    }
  return sn;
}

/* We generate digits from the least significant end, and reverse at
   the end. */
static size_t
bam_mpn_limb_get_str (unsigned char *sp, bam_mp_limb_t w,
          const struct bam_gmp_div_inverse *binv)
{
  bam_mp_size_t i;
  for (i = 0; w > 0; i++)
    {
      bam_mp_limb_t h, l, r;

      h = w >> (GMP_LIMB_BITS - binv->shift);
      l = w << binv->shift;

      bam_gmp_udiv_qrnnd_preinv (w, r, h, l, binv->d1, binv->di);
      assert ((r & (GMP_LIMB_MAX >> (GMP_LIMB_BITS - binv->shift))) == 0);
      r >>= binv->shift;

      sp[i] = r;
    }
  return i;
}

static size_t
bam_mpn_get_str_other (unsigned char *sp,
           int base, const struct bam_mpn_base_info *info,
           bam_mp_ptr up, bam_mp_size_t un)
{
  struct bam_gmp_div_inverse binv;
  size_t sn;
  size_t i;

  bam_mpn_div_qr_1_invert (&binv, base);

  sn = 0;

  if (un > 1)
    {
      struct bam_gmp_div_inverse bbinv;
      bam_mpn_div_qr_1_invert (&bbinv, info->bb);

      do
    {
      bam_mp_limb_t w;
      size_t done;
      w = bam_mpn_div_qr_1_preinv (up, up, un, &bbinv);
      un -= (up[un-1] == 0);
      done = bam_mpn_limb_get_str (sp + sn, w, &binv);

      for (sn += done; done < info->exp; done++)
        sp[sn++] = 0;
    }
      while (un > 1);
    }
  sn += bam_mpn_limb_get_str (sp + sn, up[0], &binv);

  /* Reverse order */
  for (i = 0; 2*i + 1 < sn; i++)
    {
      unsigned char t = sp[i];
      sp[i] = sp[sn - i - 1];
      sp[sn - i - 1] = t;
    }

  return sn;
}

size_t
bam_mpn_get_str (unsigned char *sp, int base, bam_mp_ptr up, bam_mp_size_t un)
{
  unsigned bits;

  assert (un > 0);
  assert (up[un-1] > 0);

  bits = bam_mpn_base_power_of_two_p (base);
  if (bits)
    return bam_mpn_get_str_bits (sp, bits, up, un);
  else
    {
      struct bam_mpn_base_info info;

      bam_mpn_get_base_info (&info, base);
      return bam_mpn_get_str_other (sp, base, &info, up, un);
    }
}

static bam_mp_size_t
bam_mpn_set_str_bits (bam_mp_ptr rp, const unsigned char *sp, size_t sn,
          unsigned bits)
{
  bam_mp_size_t rn;
  bam_mp_limb_t limb;
  unsigned shift;

  for (limb = 0, rn = 0, shift = 0; sn-- > 0; )
    {
      limb |= (bam_mp_limb_t) sp[sn] << shift;
      shift += bits;
      if (shift >= GMP_LIMB_BITS)
    {
      shift -= GMP_LIMB_BITS;
      rp[rn++] = limb;
      /* Next line is correct also if shift == 0,
         bits == 8, and bam_mp_limb_t == unsigned char. */
      limb = (unsigned int) sp[sn] >> (bits - shift);
    }
    }
  if (limb != 0)
    rp[rn++] = limb;
  else
    rn = bam_mpn_normalized_size (rp, rn);
  return rn;
}

/* Result is usually normalized, except for all-zero input, in which
   case a single zero limb is written at *RP, and 1 is returned. */
static bam_mp_size_t
bam_mpn_set_str_other (bam_mp_ptr rp, const unsigned char *sp, size_t sn,
           bam_mp_limb_t b, const struct bam_mpn_base_info *info)
{
  bam_mp_size_t rn;
  bam_mp_limb_t w;
  unsigned k;
  size_t j;

  assert (sn > 0);

  k = 1 + (sn - 1) % info->exp;

  j = 0;
  w = sp[j++];
  while (--k != 0)
    w = w * b + sp[j++];

  rp[0] = w;

  for (rn = 1; j < sn;)
    {
      bam_mp_limb_t cy;

      w = sp[j++];
      for (k = 1; k < info->exp; k++)
    w = w * b + sp[j++];

      cy = bam_mpn_mul_1 (rp, rp, rn, info->bb);
      cy += bam_mpn_add_1 (rp, rp, rn, w);
      if (cy > 0)
    rp[rn++] = cy;
    }
  assert (j == sn);

  return rn;
}

bam_mp_size_t
bam_mpn_set_str (bam_mp_ptr rp, const unsigned char *sp, size_t sn, int base)
{
  unsigned bits;

  if (sn == 0)
    return 0;

  bits = bam_mpn_base_power_of_two_p (base);
  if (bits)
    return bam_mpn_set_str_bits (rp, sp, sn, bits);
  else
    {
      struct bam_mpn_base_info info;

      bam_mpn_get_base_info (&info, base);
      return bam_mpn_set_str_other (rp, sp, sn, base, &info);
    }
}

/* MPZ interface */
void
bam_mpz_init (bam_mpz_t r)
{
  static const bam_mp_limb_t dummy_limb = GMP_LIMB_MAX & 0xc1a0;

  r->_mp_alloc = 0;
  r->_mp_size = 0;
  r->_mp_d = (bam_mp_ptr) &dummy_limb;
}

/* The utility of this function is a bit limited, since many functions
   assigns the result variable using bam_mpz_swap. */
void
bam_mpz_init2 (bam_mpz_t r, bam_mp_bitcnt_t bits)
{
  bam_mp_size_t rn;

  bits -= (bits != 0);        /* Round down, except if 0 */
  rn = 1 + bits / GMP_LIMB_BITS;

  r->_mp_alloc = rn;
  r->_mp_size = 0;
  r->_mp_d = bam_gmp_alloc_limbs (rn);
}

void
bam_mpz_clear (bam_mpz_t r)
{
  if (r->_mp_alloc)
    bam_gmp_free_limbs (r->_mp_d, r->_mp_alloc);
}

static bam_mp_ptr
bam_mpz_realloc (bam_mpz_t r, bam_mp_size_t size)
{
  size = GMP_MAX (size, 1);

  if (r->_mp_alloc)
    r->_mp_d = bam_gmp_realloc_limbs (r->_mp_d, r->_mp_alloc, size);
  else
    r->_mp_d = bam_gmp_alloc_limbs (size);
  r->_mp_alloc = size;

  if (GMP_ABS (r->_mp_size) > size)
    r->_mp_size = 0;

  return r->_mp_d;
}

/* Realloc for an bam_mpz_t WHAT if it has less than NEEDED limbs.  */
#define MPZ_REALLOC(z,n) ((n) > (z)->_mp_alloc            \
              ? bam_mpz_realloc(z,n)            \
              : (z)->_mp_d)

/* MPZ assignment and basic conversions. */
void
bam_mpz_set_si (bam_mpz_t r, signed ba0_int_p x)
{
  if (x >= 0)
    bam_mpz_set_ui (r, x);
  else /* (x < 0) */
    if (GMP_LIMB_BITS < GMP_ULONG_BITS)
      {
    bam_mpz_set_ui (r, GMP_NEG_CAST (unsigned ba0_int_p, x));
    bam_mpz_neg (r, r);
      }
  else
    {
      r->_mp_size = -1;
      MPZ_REALLOC (r, 1)[0] = GMP_NEG_CAST (unsigned ba0_int_p, x);
    }
}

void
bam_mpz_set_ui (bam_mpz_t r, unsigned ba0_int_p x)
{
  if (x > 0)
    {
      r->_mp_size = 1;
      MPZ_REALLOC (r, 1)[0] = x;
      if (GMP_LIMB_BITS < GMP_ULONG_BITS)
    {
      int LOCAL_GMP_LIMB_BITS = GMP_LIMB_BITS;
      while (x >>= LOCAL_GMP_LIMB_BITS)
        {
          ++ r->_mp_size;
          MPZ_REALLOC (r, r->_mp_size)[r->_mp_size - 1] = x;
        }
    }
    }
  else
    r->_mp_size = 0;
}

void
bam_mpz_set (bam_mpz_t r, const bam_mpz_t x)
{
  /* Allow the NOP r == x */
  if (r != x)
    {
      bam_mp_size_t n;
      bam_mp_ptr rp;

      n = GMP_ABS (x->_mp_size);
      rp = MPZ_REALLOC (r, n);

      bam_mpn_copyi (rp, x->_mp_d, n);
      r->_mp_size = x->_mp_size;
    }
}

void
bam_mpz_init_set_si (bam_mpz_t r, signed ba0_int_p x)
{
  bam_mpz_init (r);
  bam_mpz_set_si (r, x);
}

void
bam_mpz_init_set_ui (bam_mpz_t r, unsigned ba0_int_p x)
{
  bam_mpz_init (r);
  bam_mpz_set_ui (r, x);
}

void
bam_mpz_init_set (bam_mpz_t r, const bam_mpz_t x)
{
  bam_mpz_init (r);
  bam_mpz_set (r, x);
}

int
bam_mpz_fits_sba0_int_p_p (const bam_mpz_t u)
{
  return bam_mpz_cmp_si (u, LONG_MAX) <= 0 && bam_mpz_cmp_si (u, LONG_MIN) >= 0;
}

static int
bam_mpn_absfits_uba0_int_p_p (bam_mp_srcptr up, bam_mp_size_t un)
{
  int uba0_int_psize = GMP_ULONG_BITS / GMP_LIMB_BITS;
  bam_mp_limb_t uba0_int_prem = 0;

  if (GMP_ULONG_BITS % GMP_LIMB_BITS != 0)
    uba0_int_prem = (bam_mp_limb_t) (ULONG_MAX >> GMP_LIMB_BITS * uba0_int_psize) + 1;

  return un <= uba0_int_psize || (up[uba0_int_psize] < uba0_int_prem && un == uba0_int_psize + 1);
}

int
bam_mpz_fits_uba0_int_p_p (const bam_mpz_t u)
{
  bam_mp_size_t us = u->_mp_size;

  return us >= 0 && bam_mpn_absfits_uba0_int_p_p (u->_mp_d, us);
}

int
bam_mpz_fits_sint_p (const bam_mpz_t u)
{
  return bam_mpz_cmp_si (u, INT_MAX) <= 0 && bam_mpz_cmp_si (u, INT_MIN) >= 0;
}

int
bam_mpz_fits_uint_p (const bam_mpz_t u)
{
  return u->_mp_size >= 0 && bam_mpz_cmpabs_ui (u, UINT_MAX) <= 0;
}

int
bam_mpz_fits_sshort_p (const bam_mpz_t u)
{
  return bam_mpz_cmp_si (u, SHRT_MAX) <= 0 && bam_mpz_cmp_si (u, SHRT_MIN) >= 0;
}

int
bam_mpz_fits_ushort_p (const bam_mpz_t u)
{
  return u->_mp_size >= 0 && bam_mpz_cmpabs_ui (u, USHRT_MAX) <= 0;
}

ba0_int_p
bam_mpz_get_si (const bam_mpz_t u)
{
  unsigned ba0_int_p r = bam_mpz_get_ui (u);
  unsigned ba0_int_p c = -LONG_MAX - LONG_MIN;

  if (u->_mp_size < 0)
    /* This expression is necessary to properly handle -LONG_MIN */
    return -(ba0_int_p) c - (ba0_int_p) ((r - c) & LONG_MAX);
  else
    return (ba0_int_p) (r & LONG_MAX);
}

unsigned ba0_int_p
bam_mpz_get_ui (const bam_mpz_t u)
{
  if (GMP_LIMB_BITS < GMP_ULONG_BITS)
    {
      int LOCAL_GMP_LIMB_BITS = GMP_LIMB_BITS;
      unsigned ba0_int_p r = 0;
      bam_mp_size_t n = GMP_ABS (u->_mp_size);
      n = GMP_MIN (n, 1 + (bam_mp_size_t) (GMP_ULONG_BITS - 1) / GMP_LIMB_BITS);
      while (--n >= 0)
    r = (r << LOCAL_GMP_LIMB_BITS) + u->_mp_d[n];
      return r;
    }

  return u->_mp_size == 0 ? 0 : u->_mp_d[0];
}

size_t
bam_mpz_size (const bam_mpz_t u)
{
  return GMP_ABS (u->_mp_size);
}

bam_mp_limb_t
bam_mpz_getlimbn (const bam_mpz_t u, bam_mp_size_t n)
{
  if (n >= 0 && n < GMP_ABS (u->_mp_size))
    return u->_mp_d[n];
  else
    return 0;
}

void
bam_mpz_realloc2 (bam_mpz_t x, bam_mp_bitcnt_t n)
{
  bam_mpz_realloc (x, 1 + (n - (n != 0)) / GMP_LIMB_BITS);
}

bam_mp_srcptr
bam_mpz_limbs_read (bam_mpz_srcptr x)
{
  return x->_mp_d;
}

bam_mp_ptr
bam_mpz_limbs_modify (bam_mpz_t x, bam_mp_size_t n)
{
  assert (n > 0);
  return MPZ_REALLOC (x, n);
}

bam_mp_ptr
bam_mpz_limbs_write (bam_mpz_t x, bam_mp_size_t n)
{
  return bam_mpz_limbs_modify (x, n);
}

void
bam_mpz_limbs_finish (bam_mpz_t x, bam_mp_size_t xs)
{
  bam_mp_size_t xn;
  xn = bam_mpn_normalized_size (x->_mp_d, GMP_ABS (xs));
  x->_mp_size = xs < 0 ? -xn : xn;
}

static bam_mpz_srcptr
bam_mpz_roinit_normal_n (bam_mpz_t x, bam_mp_srcptr xp, bam_mp_size_t xs)
{
  x->_mp_alloc = 0;
  x->_mp_d = (bam_mp_ptr) xp;
  x->_mp_size = xs;
  return x;
}

bam_mpz_srcptr
bam_mpz_roinit_n (bam_mpz_t x, bam_mp_srcptr xp, bam_mp_size_t xs)
{
  bam_mpz_roinit_normal_n (x, xp, xs);
  bam_mpz_limbs_finish (x, xs);
  return x;
}

/* Conversions and comparison to double. */
void
bam_mpz_set_d (bam_mpz_t r, double x)
{
  int sign;
  bam_mp_ptr rp;
  bam_mp_size_t rn, i;
  double B;
  double Bi;
  bam_mp_limb_t f;

  /* x != x is true when x is a NaN, and x == x * 0.5 is true when x is
     zero or infinity. */
  if (x != x || x == x * 0.5)
    {
      r->_mp_size = 0;
      return;
    }

  sign = x < 0.0;
  if (sign)
    x = - x;

  if (x < 1.0)
    {
      r->_mp_size = 0;
      return;
    }
  B = 4.0 * (double) (GMP_LIMB_HIGHBIT >> 1);
  Bi = 1.0 / B;
  for (rn = 1; x >= B; rn++)
    x *= Bi;

  rp = MPZ_REALLOC (r, rn);

  f = (bam_mp_limb_t) x;
  x -= f;
  assert (x < 1.0);
  i = rn-1;
  rp[i] = f;
  while (--i >= 0)
    {
      x = B * x;
      f = (bam_mp_limb_t) x;
      x -= f;
      assert (x < 1.0);
      rp[i] = f;
    }

  r->_mp_size = sign ? - rn : rn;
}

void
bam_mpz_init_set_d (bam_mpz_t r, double x)
{
  bam_mpz_init (r);
  bam_mpz_set_d (r, x);
}

double
bam_mpz_get_d (const bam_mpz_t u)
{
  int m;
  bam_mp_limb_t l;
  bam_mp_size_t un;
  double x;
  double B = 4.0 * (double) (GMP_LIMB_HIGHBIT >> 1);

  un = GMP_ABS (u->_mp_size);

  if (un == 0)
    return 0.0;

  l = u->_mp_d[--un];
  bam_gmp_clz (m, l);
  m = m + GMP_DBL_MANT_BITS - GMP_LIMB_BITS;
  if (m < 0)
    l &= GMP_LIMB_MAX << -m;

  for (x = l; --un >= 0;)
    {
      x = B*x;
      if (m > 0) {
    l = u->_mp_d[un];
    m -= GMP_LIMB_BITS;
    if (m < 0)
      l &= GMP_LIMB_MAX << -m;
    x += l;
      }
    }

  if (u->_mp_size < 0)
    x = -x;

  return x;
}

int
bam_mpz_cmpabs_d (const bam_mpz_t x, double d)
{
  bam_mp_size_t xn;
  double B, Bi;
  bam_mp_size_t i;

  xn = x->_mp_size;
  d = GMP_ABS (d);

  if (xn != 0)
    {
      xn = GMP_ABS (xn);

      B = 4.0 * (double) (GMP_LIMB_HIGHBIT >> 1);
      Bi = 1.0 / B;

      /* Scale d so it can be compared with the top limb. */
      for (i = 1; i < xn; i++)
    d *= Bi;

      if (d >= B)
    return -1;

      /* Compare floor(d) to top limb, subtract and cancel when equal. */
      for (i = xn; i-- > 0;)
    {
      bam_mp_limb_t f, xl;

      f = (bam_mp_limb_t) d;
      xl = x->_mp_d[i];
      if (xl > f)
        return 1;
      else if (xl < f)
        return -1;
      d = B * (d - f);
    }
    }
  return - (d > 0.0);
}

int
bam_mpz_cmp_d (const bam_mpz_t x, double d)
{
  if (x->_mp_size < 0)
    {
      if (d >= 0.0)
    return -1;
      else
    return -bam_mpz_cmpabs_d (x, d);
    }
  else
    {
      if (d < 0.0)
    return 1;
      else
    return bam_mpz_cmpabs_d (x, d);
    }
}

/* MPZ comparisons and the like. */
int
bam_mpz_sgn (const bam_mpz_t u)
{
  return GMP_CMP (u->_mp_size, 0);
}

int
bam_mpz_cmp_si (const bam_mpz_t u, ba0_int_p v)
{
  bam_mp_size_t usize = u->_mp_size;

  if (v >= 0)
    return bam_mpz_cmp_ui (u, v);
  else if (usize >= 0)
    return 1;
  else
    return - bam_mpz_cmpabs_ui (u, GMP_NEG_CAST (unsigned ba0_int_p, v));
}

int
bam_mpz_cmp_ui (const bam_mpz_t u, unsigned ba0_int_p v)
{
  bam_mp_size_t usize = u->_mp_size;

  if (usize < 0)
    return -1;
  else
    return bam_mpz_cmpabs_ui (u, v);
}

int
bam_mpz_cmp (const bam_mpz_t a, const bam_mpz_t b)
{
  bam_mp_size_t asize = a->_mp_size;
  bam_mp_size_t bsize = b->_mp_size;

  if (asize != bsize)
    return (asize < bsize) ? -1 : 1;
  else if (asize >= 0)
    return bam_mpn_cmp (a->_mp_d, b->_mp_d, asize);
  else
    return bam_mpn_cmp (b->_mp_d, a->_mp_d, -asize);
}

int
bam_mpz_cmpabs_ui (const bam_mpz_t u, unsigned ba0_int_p v)
{
  bam_mp_size_t un = GMP_ABS (u->_mp_size);

  if (! bam_mpn_absfits_uba0_int_p_p (u->_mp_d, un))
    return 1;
  else
    {
      unsigned ba0_int_p uu = bam_mpz_get_ui (u);
      return GMP_CMP(uu, v);
    }
}

int
bam_mpz_cmpabs (const bam_mpz_t u, const bam_mpz_t v)
{
  return bam_mpn_cmp4 (u->_mp_d, GMP_ABS (u->_mp_size),
           v->_mp_d, GMP_ABS (v->_mp_size));
}

void
bam_mpz_abs (bam_mpz_t r, const bam_mpz_t u)
{
  bam_mpz_set (r, u);
  r->_mp_size = GMP_ABS (r->_mp_size);
}

void
bam_mpz_neg (bam_mpz_t r, const bam_mpz_t u)
{
  bam_mpz_set (r, u);
  r->_mp_size = -r->_mp_size;
}

void
bam_mpz_swap (bam_mpz_t u, bam_mpz_t v)
{
  MP_SIZE_T_SWAP (u->_mp_alloc, v->_mp_alloc);
  MPN_PTR_SWAP (u->_mp_d, u->_mp_size, v->_mp_d, v->_mp_size);
}

/* MPZ addition and subtraction */

void
bam_mpz_add_ui (bam_mpz_t r, const bam_mpz_t a, unsigned ba0_int_p b)
{
  bam_mpz_t bb;
  bam_mpz_init_set_ui (bb, b);
  bam_mpz_add (r, a, bb);
  bam_mpz_clear (bb);
}

void
bam_mpz_sub_ui (bam_mpz_t r, const bam_mpz_t a, unsigned ba0_int_p b)
{
  bam_mpz_ui_sub (r, b, a);
  bam_mpz_neg (r, r);
}

void
bam_mpz_ui_sub (bam_mpz_t r, unsigned ba0_int_p a, const bam_mpz_t b)
{
  bam_mpz_neg (r, b);
  bam_mpz_add_ui (r, r, a);
}

static bam_mp_size_t
bam_mpz_abs_add (bam_mpz_t r, const bam_mpz_t a, const bam_mpz_t b)
{
  bam_mp_size_t an = GMP_ABS (a->_mp_size);
  bam_mp_size_t bn = GMP_ABS (b->_mp_size);
  bam_mp_ptr rp;
  bam_mp_limb_t cy;

  if (an < bn)
    {
      MPZ_SRCPTR_SWAP (a, b);
      MP_SIZE_T_SWAP (an, bn);
    }

  rp = MPZ_REALLOC (r, an + 1);
  cy = bam_mpn_add (rp, a->_mp_d, an, b->_mp_d, bn);

  rp[an] = cy;

  return an + cy;
}

static bam_mp_size_t
bam_mpz_abs_sub (bam_mpz_t r, const bam_mpz_t a, const bam_mpz_t b)
{
  bam_mp_size_t an = GMP_ABS (a->_mp_size);
  bam_mp_size_t bn = GMP_ABS (b->_mp_size);
  int cmp;
  bam_mp_ptr rp;

  cmp = bam_mpn_cmp4 (a->_mp_d, an, b->_mp_d, bn);
  if (cmp > 0)
    {
      rp = MPZ_REALLOC (r, an);
      bam_gmp_assert_nocarry (bam_mpn_sub (rp, a->_mp_d, an, b->_mp_d, bn));
      return bam_mpn_normalized_size (rp, an);
    }
  else if (cmp < 0)
    {
      rp = MPZ_REALLOC (r, bn);
      bam_gmp_assert_nocarry (bam_mpn_sub (rp, b->_mp_d, bn, a->_mp_d, an));
      return -bam_mpn_normalized_size (rp, bn);
    }
  else
    return 0;
}

void
bam_mpz_add (bam_mpz_t r, const bam_mpz_t a, const bam_mpz_t b)
{
  bam_mp_size_t rn;

  if ( (a->_mp_size ^ b->_mp_size) >= 0)
    rn = bam_mpz_abs_add (r, a, b);
  else
    rn = bam_mpz_abs_sub (r, a, b);

  r->_mp_size = a->_mp_size >= 0 ? rn : - rn;
}

void
bam_mpz_sub (bam_mpz_t r, const bam_mpz_t a, const bam_mpz_t b)
{
  bam_mp_size_t rn;

  if ( (a->_mp_size ^ b->_mp_size) >= 0)
    rn = bam_mpz_abs_sub (r, a, b);
  else
    rn = bam_mpz_abs_add (r, a, b);

  r->_mp_size = a->_mp_size >= 0 ? rn : - rn;
}

/* MPZ multiplication */
void
bam_mpz_mul_si (bam_mpz_t r, const bam_mpz_t u, ba0_int_p v)
{
  if (v < 0)
    {
      bam_mpz_mul_ui (r, u, GMP_NEG_CAST (unsigned ba0_int_p, v));
      bam_mpz_neg (r, r);
    }
  else
    bam_mpz_mul_ui (r, u, v);
}

void
bam_mpz_mul_ui (bam_mpz_t r, const bam_mpz_t u, unsigned ba0_int_p v)
{
  bam_mpz_t vv;
  bam_mpz_init_set_ui (vv, v);
  bam_mpz_mul (r, u, vv);
  bam_mpz_clear (vv);
  return;
}

void
bam_mpz_mul (bam_mpz_t r, const bam_mpz_t u, const bam_mpz_t v)
{
  int sign;
  bam_mp_size_t un, vn, rn;
  bam_mpz_t t;
  bam_mp_ptr tp;

  un = u->_mp_size;
  vn = v->_mp_size;

  if (un == 0 || vn == 0)
    {
      r->_mp_size = 0;
      return;
    }

  sign = (un ^ vn) < 0;

  un = GMP_ABS (un);
  vn = GMP_ABS (vn);

  bam_mpz_init2 (t, (un + vn) * GMP_LIMB_BITS);

  tp = t->_mp_d;
  if (un >= vn)
    bam_mpn_mul (tp, u->_mp_d, un, v->_mp_d, vn);
  else
    bam_mpn_mul (tp, v->_mp_d, vn, u->_mp_d, un);

  rn = un + vn;
  rn -= tp[rn-1] == 0;

  t->_mp_size = sign ? - rn : rn;
  bam_mpz_swap (r, t);
  bam_mpz_clear (t);
}

void
bam_mpz_mul_2exp (bam_mpz_t r, const bam_mpz_t u, bam_mp_bitcnt_t bits)
{
  bam_mp_size_t un, rn;
  bam_mp_size_t limbs;
  unsigned shift;
  bam_mp_ptr rp;

  un = GMP_ABS (u->_mp_size);
  if (un == 0)
    {
      r->_mp_size = 0;
      return;
    }

  limbs = bits / GMP_LIMB_BITS;
  shift = bits % GMP_LIMB_BITS;

  rn = un + limbs + (shift > 0);
  rp = MPZ_REALLOC (r, rn);
  if (shift > 0)
    {
      bam_mp_limb_t cy = bam_mpn_lshift (rp + limbs, u->_mp_d, un, shift);
      rp[rn-1] = cy;
      rn -= (cy == 0);
    }
  else
    bam_mpn_copyd (rp + limbs, u->_mp_d, un);

  bam_mpn_zero (rp, limbs);

  r->_mp_size = (u->_mp_size < 0) ? - rn : rn;
}

void
bam_mpz_addmul_ui (bam_mpz_t r, const bam_mpz_t u, unsigned ba0_int_p v)
{
  bam_mpz_t t;
  bam_mpz_init_set_ui (t, v);
  bam_mpz_mul (t, u, t);
  bam_mpz_add (r, r, t);
  bam_mpz_clear (t);
}

void
bam_mpz_submul_ui (bam_mpz_t r, const bam_mpz_t u, unsigned ba0_int_p v)
{
  bam_mpz_t t;
  bam_mpz_init_set_ui (t, v);
  bam_mpz_mul (t, u, t);
  bam_mpz_sub (r, r, t);
  bam_mpz_clear (t);
}

void
bam_mpz_addmul (bam_mpz_t r, const bam_mpz_t u, const bam_mpz_t v)
{
  bam_mpz_t t;
  bam_mpz_init (t);
  bam_mpz_mul (t, u, v);
  bam_mpz_add (r, r, t);
  bam_mpz_clear (t);
}

void
bam_mpz_submul (bam_mpz_t r, const bam_mpz_t u, const bam_mpz_t v)
{
  bam_mpz_t t;
  bam_mpz_init (t);
  bam_mpz_mul (t, u, v);
  bam_mpz_sub (r, r, t);
  bam_mpz_clear (t);
}

/* MPZ division */
enum bam_mpz_div_round_mode { GMP_DIV_FLOOR, GMP_DIV_CEIL, GMP_DIV_TRUNC };

/* Allows q or r to be zero. Returns 1 iff remainder is non-zero. */
static int
bam_mpz_div_qr (bam_mpz_t q, bam_mpz_t r,
        const bam_mpz_t n, const bam_mpz_t d, enum bam_mpz_div_round_mode mode)
{
  bam_mp_size_t ns, ds, nn, dn, qs;
  ns = n->_mp_size;
  ds = d->_mp_size;

  if (ds == 0)
    bam_gmp_die("mpz_div_qr: Divide by zero.");

  if (ns == 0)
    {
      if (q)
    q->_mp_size = 0;
      if (r)
    r->_mp_size = 0;
      return 0;
    }

  nn = GMP_ABS (ns);
  dn = GMP_ABS (ds);

  qs = ds ^ ns;

  if (nn < dn)
    {
      if (mode == GMP_DIV_CEIL && qs >= 0)
    {
      /* q = 1, r = n - d */
      if (r)
        bam_mpz_sub (r, n, d);
      if (q)
        bam_mpz_set_ui (q, 1);
    }
      else if (mode == GMP_DIV_FLOOR && qs < 0)
    {
      /* q = -1, r = n + d */
      if (r)
        bam_mpz_add (r, n, d);
      if (q)
        bam_mpz_set_si (q, -1);
    }
      else
    {
      /* q = 0, r = d */
      if (r)
        bam_mpz_set (r, n);
      if (q)
        q->_mp_size = 0;
    }
      return 1;
    }
  else
    {
      bam_mp_ptr np, qp;
      bam_mp_size_t qn, rn;
      bam_mpz_t tq, tr;

      bam_mpz_init_set (tr, n);
      np = tr->_mp_d;

      qn = nn - dn + 1;

      if (q)
    {
      bam_mpz_init2 (tq, qn * GMP_LIMB_BITS);
      qp = tq->_mp_d;
    }
      else
    qp = NULL;

      bam_mpn_div_qr (qp, np, nn, d->_mp_d, dn);

      if (qp)
    {
      qn -= (qp[qn-1] == 0);

      tq->_mp_size = qs < 0 ? -qn : qn;
    }
      rn = bam_mpn_normalized_size (np, dn);
      tr->_mp_size = ns < 0 ? - rn : rn;

      if (mode == GMP_DIV_FLOOR && qs < 0 && rn != 0)
    {
      if (q)
        bam_mpz_sub_ui (tq, tq, 1);
      if (r)
        bam_mpz_add (tr, tr, d);
    }
      else if (mode == GMP_DIV_CEIL && qs >= 0 && rn != 0)
    {
      if (q)
        bam_mpz_add_ui (tq, tq, 1);
      if (r)
        bam_mpz_sub (tr, tr, d);
    }

      if (q)
    {
      bam_mpz_swap (tq, q);
      bam_mpz_clear (tq);
    }
      if (r)
    bam_mpz_swap (tr, r);

      bam_mpz_clear (tr);

      return rn != 0;
    }
}

void
bam_mpz_cdiv_qr (bam_mpz_t q, bam_mpz_t r, const bam_mpz_t n, const bam_mpz_t d)
{
  bam_mpz_div_qr (q, r, n, d, GMP_DIV_CEIL);
}

void
bam_mpz_fdiv_qr (bam_mpz_t q, bam_mpz_t r, const bam_mpz_t n, const bam_mpz_t d)
{
  bam_mpz_div_qr (q, r, n, d, GMP_DIV_FLOOR);
}

void
bam_mpz_tdiv_qr (bam_mpz_t q, bam_mpz_t r, const bam_mpz_t n, const bam_mpz_t d)
{
  bam_mpz_div_qr (q, r, n, d, GMP_DIV_TRUNC);
}

void
bam_mpz_cdiv_q (bam_mpz_t q, const bam_mpz_t n, const bam_mpz_t d)
{
  bam_mpz_div_qr (q, NULL, n, d, GMP_DIV_CEIL);
}

void
bam_mpz_fdiv_q (bam_mpz_t q, const bam_mpz_t n, const bam_mpz_t d)
{
  bam_mpz_div_qr (q, NULL, n, d, GMP_DIV_FLOOR);
}

void
bam_mpz_tdiv_q (bam_mpz_t q, const bam_mpz_t n, const bam_mpz_t d)
{
  bam_mpz_div_qr (q, NULL, n, d, GMP_DIV_TRUNC);
}

void
bam_mpz_cdiv_r (bam_mpz_t r, const bam_mpz_t n, const bam_mpz_t d)
{
  bam_mpz_div_qr (NULL, r, n, d, GMP_DIV_CEIL);
}

void
bam_mpz_fdiv_r (bam_mpz_t r, const bam_mpz_t n, const bam_mpz_t d)
{
  bam_mpz_div_qr (NULL, r, n, d, GMP_DIV_FLOOR);
}

void
bam_mpz_tdiv_r (bam_mpz_t r, const bam_mpz_t n, const bam_mpz_t d)
{
  bam_mpz_div_qr (NULL, r, n, d, GMP_DIV_TRUNC);
}

void
bam_mpz_mod (bam_mpz_t r, const bam_mpz_t n, const bam_mpz_t d)
{
  bam_mpz_div_qr (NULL, r, n, d, d->_mp_size >= 0 ? GMP_DIV_FLOOR : GMP_DIV_CEIL);
}

static void
bam_mpz_div_q_2exp (bam_mpz_t q, const bam_mpz_t u, bam_mp_bitcnt_t bit_index,
        enum bam_mpz_div_round_mode mode)
{
  bam_mp_size_t un, qn;
  bam_mp_size_t limb_cnt;
  bam_mp_ptr qp;
  int adjust;

  un = u->_mp_size;
  if (un == 0)
    {
      q->_mp_size = 0;
      return;
    }
  limb_cnt = bit_index / GMP_LIMB_BITS;
  qn = GMP_ABS (un) - limb_cnt;
  bit_index %= GMP_LIMB_BITS;

  if (mode == ((un > 0) ? GMP_DIV_CEIL : GMP_DIV_FLOOR)) /* un != 0 here. */
    /* Note: Below, the final indexing at limb_cnt is valid because at
       that point we have qn > 0. */
    adjust = (qn <= 0
          || !bam_mpn_zero_p (u->_mp_d, limb_cnt)
          || (u->_mp_d[limb_cnt]
          & (((bam_mp_limb_t) 1 << bit_index) - 1)));
  else
    adjust = 0;

  if (qn <= 0)
    qn = 0;
  else
    {
      qp = MPZ_REALLOC (q, qn);

      if (bit_index != 0)
    {
      bam_mpn_rshift (qp, u->_mp_d + limb_cnt, qn, bit_index);
      qn -= qp[qn - 1] == 0;
    }
      else
    {
      bam_mpn_copyi (qp, u->_mp_d + limb_cnt, qn);
    }
    }

  q->_mp_size = qn;

  if (adjust)
    bam_mpz_add_ui (q, q, 1);
  if (un < 0)
    bam_mpz_neg (q, q);
}

static void
bam_mpz_div_r_2exp (bam_mpz_t r, const bam_mpz_t u, bam_mp_bitcnt_t bit_index,
        enum bam_mpz_div_round_mode mode)
{
  bam_mp_size_t us, un, rn;
  bam_mp_ptr rp;
  bam_mp_limb_t mask;

  us = u->_mp_size;
  if (us == 0 || bit_index == 0)
    {
      r->_mp_size = 0;
      return;
    }
  rn = (bit_index + GMP_LIMB_BITS - 1) / GMP_LIMB_BITS;
  assert (rn > 0);

  rp = MPZ_REALLOC (r, rn);
  un = GMP_ABS (us);

  mask = GMP_LIMB_MAX >> (rn * GMP_LIMB_BITS - bit_index);

  if (rn > un)
    {
      /* Quotient (with truncation) is zero, and remainder is
     non-zero */
      if (mode == ((us > 0) ? GMP_DIV_CEIL : GMP_DIV_FLOOR)) /* us != 0 here. */
    {
      /* Have to negate and sign extend. */
      bam_mp_size_t i;

      bam_gmp_assert_nocarry (! bam_mpn_neg (rp, u->_mp_d, un));
      for (i = un; i < rn - 1; i++)
        rp[i] = GMP_LIMB_MAX;

      rp[rn-1] = mask;
      us = -us;
    }
      else
    {
      /* Just copy */
      if (r != u)
        bam_mpn_copyi (rp, u->_mp_d, un);

      rn = un;
    }
    }
  else
    {
      if (r != u)
    bam_mpn_copyi (rp, u->_mp_d, rn - 1);

      rp[rn-1] = u->_mp_d[rn-1] & mask;

      if (mode == ((us > 0) ? GMP_DIV_CEIL : GMP_DIV_FLOOR)) /* us != 0 here. */
    {
      /* If r != 0, compute 2^{bit_count} - r. */
      bam_mpn_neg (rp, rp, rn);

      rp[rn-1] &= mask;

      /* us is not used for anything else, so we can modify it
         here to indicate flipped sign. */
      us = -us;
    }
    }
  rn = bam_mpn_normalized_size (rp, rn);
  r->_mp_size = us < 0 ? -rn : rn;
}

void
bam_mpz_cdiv_q_2exp (bam_mpz_t r, const bam_mpz_t u, bam_mp_bitcnt_t cnt)
{
  bam_mpz_div_q_2exp (r, u, cnt, GMP_DIV_CEIL);
}

void
bam_mpz_fdiv_q_2exp (bam_mpz_t r, const bam_mpz_t u, bam_mp_bitcnt_t cnt)
{
  bam_mpz_div_q_2exp (r, u, cnt, GMP_DIV_FLOOR);
}

void
bam_mpz_tdiv_q_2exp (bam_mpz_t r, const bam_mpz_t u, bam_mp_bitcnt_t cnt)
{
  bam_mpz_div_q_2exp (r, u, cnt, GMP_DIV_TRUNC);
}

void
bam_mpz_cdiv_r_2exp (bam_mpz_t r, const bam_mpz_t u, bam_mp_bitcnt_t cnt)
{
  bam_mpz_div_r_2exp (r, u, cnt, GMP_DIV_CEIL);
}

void
bam_mpz_fdiv_r_2exp (bam_mpz_t r, const bam_mpz_t u, bam_mp_bitcnt_t cnt)
{
  bam_mpz_div_r_2exp (r, u, cnt, GMP_DIV_FLOOR);
}

void
bam_mpz_tdiv_r_2exp (bam_mpz_t r, const bam_mpz_t u, bam_mp_bitcnt_t cnt)
{
  bam_mpz_div_r_2exp (r, u, cnt, GMP_DIV_TRUNC);
}

void
bam_mpz_divexact (bam_mpz_t q, const bam_mpz_t n, const bam_mpz_t d)
{
  bam_gmp_assert_nocarry (bam_mpz_div_qr (q, NULL, n, d, GMP_DIV_TRUNC));
}

int
bam_mpz_divisible_p (const bam_mpz_t n, const bam_mpz_t d)
{
  return bam_mpz_div_qr (NULL, NULL, n, d, GMP_DIV_TRUNC) == 0;
}

int
bam_mpz_congruent_p (const bam_mpz_t a, const bam_mpz_t b, const bam_mpz_t m)
{
  bam_mpz_t t;
  int res;

  /* a == b (mod 0) iff a == b */
  if (bam_mpz_sgn (m) == 0)
    return (bam_mpz_cmp (a, b) == 0);

  bam_mpz_init (t);
  bam_mpz_sub (t, a, b);
  res = bam_mpz_divisible_p (t, m);
  bam_mpz_clear (t);

  return res;
}

static unsigned ba0_int_p
bam_mpz_div_qr_ui (bam_mpz_t q, bam_mpz_t r,
           const bam_mpz_t n, unsigned ba0_int_p d, enum bam_mpz_div_round_mode mode)
{
  unsigned ba0_int_p ret;
  bam_mpz_t rr, dd;

  bam_mpz_init (rr);
  bam_mpz_init_set_ui (dd, d);
  bam_mpz_div_qr (q, rr, n, dd, mode);
  bam_mpz_clear (dd);
  ret = bam_mpz_get_ui (rr);

  if (r)
    bam_mpz_swap (r, rr);
  bam_mpz_clear (rr);

  return ret;
}

unsigned ba0_int_p
bam_mpz_cdiv_qr_ui (bam_mpz_t q, bam_mpz_t r, const bam_mpz_t n, unsigned ba0_int_p d)
{
  return bam_mpz_div_qr_ui (q, r, n, d, GMP_DIV_CEIL);
}

unsigned ba0_int_p
bam_mpz_fdiv_qr_ui (bam_mpz_t q, bam_mpz_t r, const bam_mpz_t n, unsigned ba0_int_p d)
{
  return bam_mpz_div_qr_ui (q, r, n, d, GMP_DIV_FLOOR);
}

unsigned ba0_int_p
bam_mpz_tdiv_qr_ui (bam_mpz_t q, bam_mpz_t r, const bam_mpz_t n, unsigned ba0_int_p d)
{
  return bam_mpz_div_qr_ui (q, r, n, d, GMP_DIV_TRUNC);
}

unsigned ba0_int_p
bam_mpz_cdiv_q_ui (bam_mpz_t q, const bam_mpz_t n, unsigned ba0_int_p d)
{
  return bam_mpz_div_qr_ui (q, NULL, n, d, GMP_DIV_CEIL);
}

unsigned ba0_int_p
bam_mpz_fdiv_q_ui (bam_mpz_t q, const bam_mpz_t n, unsigned ba0_int_p d)
{
  return bam_mpz_div_qr_ui (q, NULL, n, d, GMP_DIV_FLOOR);
}

unsigned ba0_int_p
bam_mpz_tdiv_q_ui (bam_mpz_t q, const bam_mpz_t n, unsigned ba0_int_p d)
{
  return bam_mpz_div_qr_ui (q, NULL, n, d, GMP_DIV_TRUNC);
}

unsigned ba0_int_p
bam_mpz_cdiv_r_ui (bam_mpz_t r, const bam_mpz_t n, unsigned ba0_int_p d)
{
  return bam_mpz_div_qr_ui (NULL, r, n, d, GMP_DIV_CEIL);
}
unsigned ba0_int_p
bam_mpz_fdiv_r_ui (bam_mpz_t r, const bam_mpz_t n, unsigned ba0_int_p d)
{
  return bam_mpz_div_qr_ui (NULL, r, n, d, GMP_DIV_FLOOR);
}
unsigned ba0_int_p
bam_mpz_tdiv_r_ui (bam_mpz_t r, const bam_mpz_t n, unsigned ba0_int_p d)
{
  return bam_mpz_div_qr_ui (NULL, r, n, d, GMP_DIV_TRUNC);
}

unsigned ba0_int_p
bam_mpz_cdiv_ui (const bam_mpz_t n, unsigned ba0_int_p d)
{
  return bam_mpz_div_qr_ui (NULL, NULL, n, d, GMP_DIV_CEIL);
}

unsigned ba0_int_p
bam_mpz_fdiv_ui (const bam_mpz_t n, unsigned ba0_int_p d)
{
  return bam_mpz_div_qr_ui (NULL, NULL, n, d, GMP_DIV_FLOOR);
}

unsigned ba0_int_p
bam_mpz_tdiv_ui (const bam_mpz_t n, unsigned ba0_int_p d)
{
  return bam_mpz_div_qr_ui (NULL, NULL, n, d, GMP_DIV_TRUNC);
}

unsigned ba0_int_p
bam_mpz_mod_ui (bam_mpz_t r, const bam_mpz_t n, unsigned ba0_int_p d)
{
  return bam_mpz_div_qr_ui (NULL, r, n, d, GMP_DIV_FLOOR);
}

void
bam_mpz_divexact_ui (bam_mpz_t q, const bam_mpz_t n, unsigned ba0_int_p d)
{
  bam_gmp_assert_nocarry (bam_mpz_div_qr_ui (q, NULL, n, d, GMP_DIV_TRUNC));
}

int
bam_mpz_divisible_ui_p (const bam_mpz_t n, unsigned ba0_int_p d)
{
  return bam_mpz_div_qr_ui (NULL, NULL, n, d, GMP_DIV_TRUNC) == 0;
}

/* GCD */
static bam_mp_limb_t
bam_mpn_gcd_11 (bam_mp_limb_t u, bam_mp_limb_t v)
{
  unsigned shift;

  assert ( (u | v) > 0);

  if (u == 0)
    return v;
  else if (v == 0)
    return u;

  bam_gmp_ctz (shift, u | v);

  u >>= shift;
  v >>= shift;

  if ( (u & 1) == 0)
    MP_LIMB_T_SWAP (u, v);

  while ( (v & 1) == 0)
    v >>= 1;

  while (u != v)
    {
      if (u > v)
    {
      u -= v;
      do
        u >>= 1;
      while ( (u & 1) == 0);
    }
      else
    {
      v -= u;
      do
        v >>= 1;
      while ( (v & 1) == 0);
    }
    }
  return u << shift;
}

unsigned ba0_int_p
bam_mpz_gcd_ui (bam_mpz_t g, const bam_mpz_t u, unsigned ba0_int_p v)
{
  bam_mpz_t t;
  bam_mpz_init_set_ui(t, v);
  bam_mpz_gcd (t, u, t);
  if (v > 0)
    v = bam_mpz_get_ui (t);

  if (g)
    bam_mpz_swap (t, g);

  bam_mpz_clear (t);

  return v;
}

static bam_mp_bitcnt_t
bam_mpz_make_odd (bam_mpz_t r)
{
  bam_mp_bitcnt_t shift;

  assert (r->_mp_size > 0);
  /* Count trailing zeros, equivalent to bam_mpn_scan1, because we know that there is a 1 */
  shift = bam_mpn_scan1 (r->_mp_d, 0);
  bam_mpz_tdiv_q_2exp (r, r, shift);

  return shift;
}

void
bam_mpz_gcd (bam_mpz_t g, const bam_mpz_t u, const bam_mpz_t v)
{
  bam_mpz_t tu, tv;
  bam_mp_bitcnt_t uz, vz, gz;

  if (u->_mp_size == 0)
    {
      bam_mpz_abs (g, v);
      return;
    }
  if (v->_mp_size == 0)
    {
      bam_mpz_abs (g, u);
      return;
    }

  bam_mpz_init (tu);
  bam_mpz_init (tv);

  bam_mpz_abs (tu, u);
  uz = bam_mpz_make_odd (tu);
  bam_mpz_abs (tv, v);
  vz = bam_mpz_make_odd (tv);
  gz = GMP_MIN (uz, vz);

  if (tu->_mp_size < tv->_mp_size)
    bam_mpz_swap (tu, tv);

  bam_mpz_tdiv_r (tu, tu, tv);
  if (tu->_mp_size == 0)
    {
      bam_mpz_swap (g, tv);
    }
  else
    for (;;)
      {
    int c;

    bam_mpz_make_odd (tu);
    c = bam_mpz_cmp (tu, tv);
    if (c == 0)
      {
        bam_mpz_swap (g, tu);
        break;
      }
    if (c < 0)
      bam_mpz_swap (tu, tv);

    if (tv->_mp_size == 1)
      {
        bam_mp_limb_t *gp;

        bam_mpz_tdiv_r (tu, tu, tv);
        gp = MPZ_REALLOC (g, 1); /* gp = bam_mpz_limbs_modify (g, 1); */
        *gp = bam_mpn_gcd_11 (tu->_mp_d[0], tv->_mp_d[0]);

        g->_mp_size = *gp != 0; /* bam_mpz_limbs_finish (g, 1); */
        break;
      }
    bam_mpz_sub (tu, tu, tv);
      }
  bam_mpz_clear (tu);
  bam_mpz_clear (tv);
  bam_mpz_mul_2exp (g, g, gz);
}

void
bam_mpz_gcdext (bam_mpz_t g, bam_mpz_t s, bam_mpz_t t, const bam_mpz_t u, const bam_mpz_t v)
{
  bam_mpz_t tu, tv, s0, s1, t0, t1;
  bam_mp_bitcnt_t uz, vz, gz;
  bam_mp_bitcnt_t power;

  if (u->_mp_size == 0)
    {
      /* g = 0 u + sgn(v) v */
      signed ba0_int_p sign = bam_mpz_sgn (v);
      bam_mpz_abs (g, v);
      if (s)
    s->_mp_size = 0;
      if (t)
    bam_mpz_set_si (t, sign);
      return;
    }

  if (v->_mp_size == 0)
    {
      /* g = sgn(u) u + 0 v */
      signed ba0_int_p sign = bam_mpz_sgn (u);
      bam_mpz_abs (g, u);
      if (s)
    bam_mpz_set_si (s, sign);
      if (t)
    t->_mp_size = 0;
      return;
    }

  bam_mpz_init (tu);
  bam_mpz_init (tv);
  bam_mpz_init (s0);
  bam_mpz_init (s1);
  bam_mpz_init (t0);
  bam_mpz_init (t1);

  bam_mpz_abs (tu, u);
  uz = bam_mpz_make_odd (tu);
  bam_mpz_abs (tv, v);
  vz = bam_mpz_make_odd (tv);
  gz = GMP_MIN (uz, vz);

  uz -= gz;
  vz -= gz;

  /* Cofactors corresponding to odd gcd. gz handled later. */
  if (tu->_mp_size < tv->_mp_size)
    {
      bam_mpz_swap (tu, tv);
      MPZ_SRCPTR_SWAP (u, v);
      MPZ_PTR_SWAP (s, t);
      MP_BITCNT_T_SWAP (uz, vz);
    }

  /* Maintain
   *
   * u = t0 tu + t1 tv
   * v = s0 tu + s1 tv
   *
   * where u and v denote the inputs with common factors of two
   * eliminated, and det (s0, t0; s1, t1) = 2^p. Then
   *
   * 2^p tu =  s1 u - t1 v
   * 2^p tv = -s0 u + t0 v
   */

  /* After initial division, tu = q tv + tu', we have
   *
   * u = 2^uz (tu' + q tv)
   * v = 2^vz tv
   *
   * or
   *
   * t0 = 2^uz, t1 = 2^uz q
   * s0 = 0,    s1 = 2^vz
   */

  bam_mpz_tdiv_qr (t1, tu, tu, tv);
  bam_mpz_mul_2exp (t1, t1, uz);

  bam_mpz_setbit (s1, vz);
  power = uz + vz;

  if (tu->_mp_size > 0)
    {
      bam_mp_bitcnt_t shift;
      shift = bam_mpz_make_odd (tu);
      bam_mpz_setbit (t0, uz + shift);
      power += shift;

      for (;;)
    {
      int c;
      c = bam_mpz_cmp (tu, tv);
      if (c == 0)
        break;

      if (c < 0)
        {
          /* tv = tv' + tu
           *
           * u = t0 tu + t1 (tv' + tu) = (t0 + t1) tu + t1 tv'
           * v = s0 tu + s1 (tv' + tu) = (s0 + s1) tu + s1 tv' */

          bam_mpz_sub (tv, tv, tu);
          bam_mpz_add (t0, t0, t1);
          bam_mpz_add (s0, s0, s1);

          shift = bam_mpz_make_odd (tv);
          bam_mpz_mul_2exp (t1, t1, shift);
          bam_mpz_mul_2exp (s1, s1, shift);
        }
      else
        {
          bam_mpz_sub (tu, tu, tv);
          bam_mpz_add (t1, t0, t1);
          bam_mpz_add (s1, s0, s1);

          shift = bam_mpz_make_odd (tu);
          bam_mpz_mul_2exp (t0, t0, shift);
          bam_mpz_mul_2exp (s0, s0, shift);
        }
      power += shift;
    }
    }
  else
    bam_mpz_setbit (t0, uz);

  /* Now tv = odd part of gcd, and -s0 and t0 are corresponding
     cofactors. */

  bam_mpz_mul_2exp (tv, tv, gz);
  bam_mpz_neg (s0, s0);

  /* 2^p g = s0 u + t0 v. Eliminate one factor of two at a time. To
     adjust cofactors, we need u / g and v / g */

  bam_mpz_divexact (s1, v, tv);
  bam_mpz_abs (s1, s1);
  bam_mpz_divexact (t1, u, tv);
  bam_mpz_abs (t1, t1);

  while (power-- > 0)
    {
      /* s0 u + t0 v = (s0 - v/g) u - (t0 + u/g) v */
      if (bam_mpz_odd_p (s0) || bam_mpz_odd_p (t0))
    {
      bam_mpz_sub (s0, s0, s1);
      bam_mpz_add (t0, t0, t1);
    }
      assert (bam_mpz_even_p (t0) && bam_mpz_even_p (s0));
      bam_mpz_tdiv_q_2exp (s0, s0, 1);
      bam_mpz_tdiv_q_2exp (t0, t0, 1);
    }

  /* Arrange so that |s| < |u| / 2g */
  bam_mpz_add (s1, s0, s1);
  if (bam_mpz_cmpabs (s0, s1) > 0)
    {
      bam_mpz_swap (s0, s1);
      bam_mpz_sub (t0, t0, t1);
    }
  if (u->_mp_size < 0)
    bam_mpz_neg (s0, s0);
  if (v->_mp_size < 0)
    bam_mpz_neg (t0, t0);

  bam_mpz_swap (g, tv);
  if (s)
    bam_mpz_swap (s, s0);
  if (t)
    bam_mpz_swap (t, t0);

  bam_mpz_clear (tu);
  bam_mpz_clear (tv);
  bam_mpz_clear (s0);
  bam_mpz_clear (s1);
  bam_mpz_clear (t0);
  bam_mpz_clear (t1);
}

void
bam_mpz_lcm (bam_mpz_t r, const bam_mpz_t u, const bam_mpz_t v)
{
  bam_mpz_t g;

  if (u->_mp_size == 0 || v->_mp_size == 0)
    {
      r->_mp_size = 0;
      return;
    }

  bam_mpz_init (g);

  bam_mpz_gcd (g, u, v);
  bam_mpz_divexact (g, u, g);
  bam_mpz_mul (r, g, v);

  bam_mpz_clear (g);
  bam_mpz_abs (r, r);
}

void
bam_mpz_lcm_ui (bam_mpz_t r, const bam_mpz_t u, unsigned ba0_int_p v)
{
  if (v == 0 || u->_mp_size == 0)
    {
      r->_mp_size = 0;
      return;
    }

  v /= bam_mpz_gcd_ui (NULL, u, v);
  bam_mpz_mul_ui (r, u, v);

  bam_mpz_abs (r, r);
}

int
bam_mpz_invert (bam_mpz_t r, const bam_mpz_t u, const bam_mpz_t m)
{
  bam_mpz_t g, tr;
  int invertible;

  if (u->_mp_size == 0 || bam_mpz_cmpabs_ui (m, 1) <= 0)
    return 0;

  bam_mpz_init (g);
  bam_mpz_init (tr);

  bam_mpz_gcdext (g, tr, NULL, u, m);
  invertible = (bam_mpz_cmp_ui (g, 1) == 0);

  if (invertible)
    {
      if (tr->_mp_size < 0)
    {
      if (m->_mp_size >= 0)
        bam_mpz_add (tr, tr, m);
      else
        bam_mpz_sub (tr, tr, m);
    }
      bam_mpz_swap (r, tr);
    }

  bam_mpz_clear (g);
  bam_mpz_clear (tr);
  return invertible;
}

/* Higher level operations (sqrt, pow and root) */

void
bam_mpz_pow_ui (bam_mpz_t r, const bam_mpz_t b, unsigned ba0_int_p e)
{
  unsigned ba0_int_p bit;
  bam_mpz_t tr;
  bam_mpz_init_set_ui (tr, 1);

  bit = GMP_ULONG_HIGHBIT;
  do
    {
      bam_mpz_mul (tr, tr, tr);
      if (e & bit)
    bam_mpz_mul (tr, tr, b);
      bit >>= 1;
    }
  while (bit > 0);

  bam_mpz_swap (r, tr);
  bam_mpz_clear (tr);
}

void
bam_mpz_ui_pow_ui (bam_mpz_t r, unsigned ba0_int_p blimb, unsigned ba0_int_p e)
{
  bam_mpz_t b;

  bam_mpz_init_set_ui (b, blimb);
  bam_mpz_pow_ui (r, b, e);
  bam_mpz_clear (b);
}

void
bam_mpz_powm (bam_mpz_t r, const bam_mpz_t b, const bam_mpz_t e, const bam_mpz_t m)
{
  bam_mpz_t tr;
  bam_mpz_t base;
  bam_mp_size_t en, mn;
  bam_mp_srcptr mp;
  struct bam_gmp_div_inverse minv;
  unsigned shift;
  bam_mp_ptr tp = NULL;

  en = GMP_ABS (e->_mp_size);
  mn = GMP_ABS (m->_mp_size);
  if (mn == 0)
    bam_gmp_die ("mpz_powm: Zero modulo.");

  if (en == 0)
    {
      bam_mpz_set_ui (r, bam_mpz_cmpabs_ui (m, 1));
      return;
    }

  mp = m->_mp_d;
  bam_mpn_div_qr_invert (&minv, mp, mn);
  shift = minv.shift;

  if (shift > 0)
    {
      /* To avoid shifts, we do all our reductions, except the final
     one, using a *normalized* m. */
      minv.shift = 0;

      tp = bam_gmp_alloc_limbs (mn);
      bam_gmp_assert_nocarry (bam_mpn_lshift (tp, mp, mn, shift));
      mp = tp;
    }

  bam_mpz_init (base);

  if (e->_mp_size < 0)
    {
      if (!bam_mpz_invert (base, b, m))
    bam_gmp_die ("mpz_powm: Negative exponent and non-invertible base.");
    }
  else
    {
      bam_mp_size_t bn;
      bam_mpz_abs (base, b);

      bn = base->_mp_size;
      if (bn >= mn)
    {
      bam_mpn_div_qr_preinv (NULL, base->_mp_d, base->_mp_size, mp, mn, &minv);
      bn = mn;
    }

      /* We have reduced the absolute value. Now take care of the
     sign. Note that we get zero represented non-canonically as
     m. */
      if (b->_mp_size < 0)
    {
      bam_mp_ptr bp = MPZ_REALLOC (base, mn);
      bam_gmp_assert_nocarry (bam_mpn_sub (bp, mp, mn, bp, bn));
      bn = mn;
    }
      base->_mp_size = bam_mpn_normalized_size (base->_mp_d, bn);
    }
  bam_mpz_init_set_ui (tr, 1);

  while (--en >= 0)
    {
      bam_mp_limb_t w = e->_mp_d[en];
      bam_mp_limb_t bit;

      bit = GMP_LIMB_HIGHBIT;
      do
    {
      bam_mpz_mul (tr, tr, tr);
      if (w & bit)
        bam_mpz_mul (tr, tr, base);
      if (tr->_mp_size > mn)
        {
          bam_mpn_div_qr_preinv (NULL, tr->_mp_d, tr->_mp_size, mp, mn, &minv);
          tr->_mp_size = bam_mpn_normalized_size (tr->_mp_d, mn);
        }
      bit >>= 1;
    }
      while (bit > 0);
    }

  /* Final reduction */
  if (tr->_mp_size >= mn)
    {
      minv.shift = shift;
      bam_mpn_div_qr_preinv (NULL, tr->_mp_d, tr->_mp_size, mp, mn, &minv);
      tr->_mp_size = bam_mpn_normalized_size (tr->_mp_d, mn);
    }
  if (tp)
    bam_gmp_free_limbs (tp, mn);

  bam_mpz_swap (r, tr);
  bam_mpz_clear (tr);
  bam_mpz_clear (base);
}

void
bam_mpz_powm_ui (bam_mpz_t r, const bam_mpz_t b, unsigned ba0_int_p elimb, const bam_mpz_t m)
{
  bam_mpz_t e;

  bam_mpz_init_set_ui (e, elimb);
  bam_mpz_powm (r, b, e, m);
  bam_mpz_clear (e);
}

/* x=trunc(y^(1/z)), r=y-x^z */
void
bam_mpz_rootrem (bam_mpz_t x, bam_mpz_t r, const bam_mpz_t y, unsigned ba0_int_p z)
{
  int sgn;
  bam_mp_bitcnt_t bc;
  bam_mpz_t t, u;

  sgn = y->_mp_size < 0;
  if ((~z & sgn) != 0)
    bam_gmp_die ("mpz_rootrem: Negative argument, with even root.");
  if (z == 0)
    bam_gmp_die ("mpz_rootrem: Zeroth root.");

  if (bam_mpz_cmpabs_ui (y, 1) <= 0) {
    if (x)
      bam_mpz_set (x, y);
    if (r)
      r->_mp_size = 0;
    return;
  }

  bam_mpz_init (u);
  bam_mpz_init (t);
  bc = (bam_mpz_sizeinbase (y, 2) - 1) / z + 1;
  bam_mpz_setbit (t, bc);

  if (z == 2) /* simplify sqrt loop: z-1 == 1 */
    do {
      bam_mpz_swap (u, t);            /* u = x */
      bam_mpz_tdiv_q (t, y, u);        /* t = y/x */
      bam_mpz_add (t, t, u);        /* t = y/x + x */
      bam_mpz_tdiv_q_2exp (t, t, 1);    /* x'= (y/x + x)/2 */
    } while (bam_mpz_cmpabs (t, u) < 0);    /* |x'| < |x| */
  else /* z != 2 */ {
    bam_mpz_t v;

    bam_mpz_init (v);
    if (sgn)
      bam_mpz_neg (t, t);

    do {
      bam_mpz_swap (u, t);            /* u = x */
      bam_mpz_pow_ui (t, u, z - 1);        /* t = x^(z-1) */
      bam_mpz_tdiv_q (t, y, t);        /* t = y/x^(z-1) */
      bam_mpz_mul_ui (v, u, z - 1);        /* v = x*(z-1) */
      bam_mpz_add (t, t, v);        /* t = y/x^(z-1) + x*(z-1) */
      bam_mpz_tdiv_q_ui (t, t, z);        /* x'=(y/x^(z-1) + x*(z-1))/z */
    } while (bam_mpz_cmpabs (t, u) < 0);    /* |x'| < |x| */

    bam_mpz_clear (v);
  }

  if (r) {
    bam_mpz_pow_ui (t, u, z);
    bam_mpz_sub (r, y, t);
  }
  if (x)
    bam_mpz_swap (x, u);
  bam_mpz_clear (u);
  bam_mpz_clear (t);
}

int
bam_mpz_root (bam_mpz_t x, const bam_mpz_t y, unsigned ba0_int_p z)
{
  int res;
  bam_mpz_t r;

  bam_mpz_init (r);
  bam_mpz_rootrem (x, r, y, z);
  res = r->_mp_size == 0;
  bam_mpz_clear (r);

  return res;
}

/* Compute s = floor(sqrt(u)) and r = u - s^2. Allows r == NULL */
void
bam_mpz_sqrtrem (bam_mpz_t s, bam_mpz_t r, const bam_mpz_t u)
{
  bam_mpz_rootrem (s, r, u, 2);
}

void
bam_mpz_sqrt (bam_mpz_t s, const bam_mpz_t u)
{
  bam_mpz_rootrem (s, NULL, u, 2);
}

int
bam_mpz_perfect_square_p (const bam_mpz_t u)
{
  if (u->_mp_size <= 0)
    return (u->_mp_size == 0);
  else
    return bam_mpz_root (NULL, u, 2);
}

int
bam_mpn_perfect_square_p (bam_mp_srcptr p, bam_mp_size_t n)
{
  bam_mpz_t t;

  assert (n > 0);
  assert (p [n-1] != 0);
  return bam_mpz_root (NULL, bam_mpz_roinit_normal_n (t, p, n), 2);
}

bam_mp_size_t
bam_mpn_sqrtrem (bam_mp_ptr sp, bam_mp_ptr rp, bam_mp_srcptr p, bam_mp_size_t n)
{
  bam_mpz_t s, r, u;
  bam_mp_size_t res;

  assert (n > 0);
  assert (p [n-1] != 0);

  bam_mpz_init (r);
  bam_mpz_init (s);
  bam_mpz_rootrem (s, r, bam_mpz_roinit_normal_n (u, p, n), 2);

  assert (s->_mp_size == (n+1)/2);
  bam_mpn_copyd (sp, s->_mp_d, s->_mp_size);
  bam_mpz_clear (s);
  res = r->_mp_size;
  if (rp)
    bam_mpn_copyd (rp, r->_mp_d, res);
  bam_mpz_clear (r);
  return res;
}

/* Combinatorics */

void
bam_mpz_mfac_uiui (bam_mpz_t x, unsigned ba0_int_p n, unsigned ba0_int_p m)
{
  bam_mpz_set_ui (x, n + (n == 0));
  if (m + 1 < 2) return;
  while (n > m + 1)
    bam_mpz_mul_ui (x, x, n -= m);
}

void
bam_mpz_2fac_ui (bam_mpz_t x, unsigned ba0_int_p n)
{
  bam_mpz_mfac_uiui (x, n, 2);
}

void
bam_mpz_fac_ui (bam_mpz_t x, unsigned ba0_int_p n)
{
  bam_mpz_mfac_uiui (x, n, 1);
}

void
bam_mpz_bin_uiui (bam_mpz_t r, unsigned ba0_int_p n, unsigned ba0_int_p k)
{
  bam_mpz_t t;

  bam_mpz_set_ui (r, k <= n);

  if (k > (n >> 1))
    k = (k <= n) ? n - k : 0;

  bam_mpz_init (t);
  bam_mpz_fac_ui (t, k);

  for (; k > 0; --k)
    bam_mpz_mul_ui (r, r, n--);

  bam_mpz_divexact (r, r, t);
  bam_mpz_clear (t);
}

/* Primality testing */

/* Computes Kronecker (a/b) with odd b, a!=0 and GCD(a,b) = 1 */
/* Adapted from JACOBI_BASE_METHOD==4 in mpn/generic/jacbase.c */
static int
bam_gmp_jacobi_coprime (bam_mp_limb_t a, bam_mp_limb_t b)
{
  int c, bit = 0;

  assert (b & 1);
  assert (a != 0);
  /* assert (bam_mpn_gcd_11 (a, b) == 1); */

  /* Below, we represent a and b shifted right so that the least
     significant one bit is implicit. */
  b >>= 1;

  bam_gmp_ctz(c, a);
  a >>= 1;

  for (;;)
    {
      a >>= c;
      /* (2/b) = -1 if b = 3 or 5 mod 8 */
      bit ^= c & (b ^ (b >> 1));
      if (a < b)
    {
      if (a == 0)
        return bit & 1 ? -1 : 1;
      bit ^= a & b;
      a = b - a;
      b -= a;
    }
      else
    {
      a -= b;
      assert (a != 0);
    }

      bam_gmp_ctz(c, a);
      ++c;
    }
}

static void
bam_gmp_lucas_step_k_2k (bam_mpz_t V, bam_mpz_t Qk, const bam_mpz_t n)
{
  bam_mpz_mod (Qk, Qk, n);
  /* V_{2k} <- V_k ^ 2 - 2Q^k */
  bam_mpz_mul (V, V, V);
  bam_mpz_submul_ui (V, Qk, 2);
  bam_mpz_tdiv_r (V, V, n);
  /* Q^{2k} = (Q^k)^2 */
  bam_mpz_mul (Qk, Qk, Qk);
}

/* Computes V_k, Q^k (mod n) for the Lucas' sequence */
/* with P=1, Q=Q; k = (n>>b0)|1. */
/* Requires an odd n > 4; b0 > 0; -2*Q must not overflow a ba0_int_p */
/* Returns (U_k == 0) and sets V=V_k and Qk=Q^k. */
static int
bam_gmp_lucas_mod (bam_mpz_t V, bam_mpz_t Qk, ba0_int_p Q,
           bam_mp_bitcnt_t b0, const bam_mpz_t n)
{
  bam_mp_bitcnt_t bs;
  bam_mpz_t U;
  int res;

  assert (b0 > 0);
  assert (Q <= - (LONG_MIN / 2));
  assert (Q >= - (LONG_MAX / 2));
  assert (bam_mpz_cmp_ui (n, 4) > 0);
  assert (bam_mpz_odd_p (n));

  bam_mpz_init_set_ui (U, 1); /* U1 = 1 */
  bam_mpz_set_ui (V, 1); /* V1 = 1 */
  bam_mpz_set_si (Qk, Q);

  for (bs = bam_mpz_sizeinbase (n, 2) - 1; --bs >= b0;)
    {
      /* U_{2k} <- U_k * V_k */
      bam_mpz_mul (U, U, V);
      /* V_{2k} <- V_k ^ 2 - 2Q^k */
      /* Q^{2k} = (Q^k)^2 */
      bam_gmp_lucas_step_k_2k (V, Qk, n);

      /* A step k->k+1 is performed if the bit in $n$ is 1    */
      /* bam_mpz_tstbit(n,bs) or the bit is 0 in $n$ but    */
      /* should be 1 in $n+1$ (bs == b0)            */
      if (b0 == bs || bam_mpz_tstbit (n, bs))
    {
      /* Q^{k+1} <- Q^k * Q */
      bam_mpz_mul_si (Qk, Qk, Q);
      /* U_{k+1} <- (U_k + V_k) / 2 */
      bam_mpz_swap (U, V); /* Keep in V the old value of U_k */
      bam_mpz_add (U, U, V);
      /* We have to compute U/2, so we need an even value, */
      /* equivalent (mod n) */
      if (bam_mpz_odd_p (U))
        bam_mpz_add (U, U, n);
      bam_mpz_tdiv_q_2exp (U, U, 1);
      /* V_{k+1} <-(D*U_k + V_k) / 2 =
            U_{k+1} + (D-1)/2*U_k = U_{k+1} - 2Q*U_k */
      bam_mpz_mul_si (V, V, -2*Q);
      bam_mpz_add (V, U, V);
      bam_mpz_tdiv_r (V, V, n);
    }
      bam_mpz_tdiv_r (U, U, n);
    }

  res = U->_mp_size == 0;
  bam_mpz_clear (U);
  return res;
}

/* Performs strong Lucas' test on x, with parameters suggested */
/* for the BPSW test. Qk is only passed to recycle a variable. */
/* Requires GCD (x,6) = 1.*/
static int
bam_gmp_stronglucas (const bam_mpz_t x, bam_mpz_t Qk)
{
  bam_mp_bitcnt_t b0;
  bam_mpz_t V, n;
  bam_mp_limb_t maxD, D; /* The absolute value is stored. */
  ba0_int_p Q;
  bam_mp_limb_t tl;

  /* Test on the absolute value. */
  bam_mpz_roinit_normal_n (n, x->_mp_d, GMP_ABS (x->_mp_size));

  assert (bam_mpz_odd_p (n));
  /* assert (bam_mpz_gcd_ui (NULL, n, 6) == 1); */
  if (bam_mpz_root (Qk, n, 2))
    return 0; /* A square is composite. */

  /* Check Ds up to square root (in case, n is prime)
     or avoid overflows */
  maxD = (Qk->_mp_size == 1) ? Qk->_mp_d [0] - 1 : GMP_LIMB_MAX;

  D = 3;
  /* Search a D such that (D/n) = -1 in the sequence 5,-7,9,-11,.. */
  /* For those Ds we have (D/n) = (n/|D|) */
  do
    {
      if (D >= maxD)
    return 1 + (D != GMP_LIMB_MAX); /* (1 + ! ~ D) */
      D += 2;
      tl = bam_mpz_tdiv_ui (n, D);
      if (tl == 0)
    return 0;
    }
  while (bam_gmp_jacobi_coprime (tl, D) == 1);

  bam_mpz_init (V);

  /* n-(D/n) = n+1 = d*2^{b0}, with d = (n>>b0) | 1 */
  b0 = bam_mpn_common_scan (~ n->_mp_d[0], 0, n->_mp_d, n->_mp_size, GMP_LIMB_MAX);
  /* b0 = bam_mpz_scan0 (n, 0); */

  /* D= P^2 - 4Q; P = 1; Q = (1-D)/4 */
  Q = (D & 2) ? (ba0_int_p) (D >> 2) + 1 : -(ba0_int_p) (D >> 2);

  if (! bam_gmp_lucas_mod (V, Qk, Q, b0, n))    /* If Ud != 0 */
    while (V->_mp_size != 0 && --b0 != 0)    /* while Vk != 0 */
      /* V <- V ^ 2 - 2Q^k */
      /* Q^{2k} = (Q^k)^2 */
      bam_gmp_lucas_step_k_2k (V, Qk, n);

  bam_mpz_clear (V);
  return (b0 != 0);
}

static int
bam_gmp_millerrabin (const bam_mpz_t n, const bam_mpz_t nm1, bam_mpz_t y,
         const bam_mpz_t q, bam_mp_bitcnt_t k)
{
  assert (k > 0);

  /* Caller must initialize y to the base. */
  bam_mpz_powm (y, y, q, n);

  if (bam_mpz_cmp_ui (y, 1) == 0 || bam_mpz_cmp (y, nm1) == 0)
    return 1;

  while (--k > 0)
    {
      bam_mpz_powm_ui (y, y, 2, n);
      if (bam_mpz_cmp (y, nm1) == 0)
    return 1;
    }
  return 0;
}

/* This product is 0xc0cfd797, and fits in 32 bits. */
#define GMP_PRIME_PRODUCT \
  (3UL*5UL*7UL*11UL*13UL*17UL*19UL*23UL*29UL)

/* Bit (p+1)/2 is set, for each odd prime <= 61 */
#define GMP_PRIME_MASK 0xc96996dcUL

int
bam_mpz_probab_prime_p (const bam_mpz_t n, int reps)
{
  bam_mpz_t nm1;
  bam_mpz_t q;
  bam_mpz_t y;
  bam_mp_bitcnt_t k;
  int is_prime;
  int j;

  /* Note that we use the absolute value of n only, for compatibility
     with the real GMP. */
  if (bam_mpz_even_p (n))
    return (bam_mpz_cmpabs_ui (n, 2) == 0) ? 2 : 0;

  /* Above test excludes n == 0 */
  assert (n->_mp_size != 0);

  if (bam_mpz_cmpabs_ui (n, 64) < 0)
    return (GMP_PRIME_MASK >> (n->_mp_d[0] >> 1)) & 2;

  if (bam_mpz_gcd_ui (NULL, n, GMP_PRIME_PRODUCT) != 1)
    return 0;

  /* All prime factors are >= 31. */
  if (bam_mpz_cmpabs_ui (n, 31*31) < 0)
    return 2;

  bam_mpz_init (nm1);
  bam_mpz_init (q);

  /* Find q and k, where q is odd and n = 1 + 2**k * q.  */
  bam_mpz_abs (nm1, n);
  nm1->_mp_d[0] -= 1;
  /* Count trailing zeros, equivalent to bam_mpn_scan1, because we know that there is a 1 */
  k = bam_mpn_scan1 (nm1->_mp_d, 0);
  bam_mpz_tdiv_q_2exp (q, nm1, k);

  /* BPSW test */
  bam_mpz_init_set_ui (y, 2);
  is_prime = bam_gmp_millerrabin (n, nm1, y, q, k) && bam_gmp_stronglucas (n, y);
  reps -= 24; /* skip the first 24 repetitions */

  /* Use Miller-Rabin, with a deterministic sequence of bases, a[j] =
     j^2 + j + 41 using Euler's polynomial. We potentially stop early,
     if a[j] >= n - 1. Since n >= 31*31, this can happen only if reps >
     30 (a[30] == 971 > 31*31 == 961). */

  for (j = 0; is_prime & (j < reps); j++)
    {
      bam_mpz_set_ui (y, (unsigned ba0_int_p) j*j+j+41);
      if (bam_mpz_cmp (y, nm1) >= 0)
    {
      /* Don't try any further bases. This "early" break does not affect
         the result for any reasonable reps value (<=5000 was tested) */
      assert (j >= 30);
      break;
    }
      is_prime = bam_gmp_millerrabin (n, nm1, y, q, k);
    }
  bam_mpz_clear (nm1);
  bam_mpz_clear (q);
  bam_mpz_clear (y);

  return is_prime;
}

/* Logical operations and bit manipulation. */

/* Numbers are treated as if represented in two's complement (and
   infinitely sign extended). For a negative values we get the two's
   complement from -x = ~x + 1, where ~ is bitwise complement.
   Negation transforms

     xxxx10...0

   into

     yyyy10...0

   where yyyy is the bitwise complement of xxxx. So least significant
   bits, up to and including the first one bit, are unchanged, and
   the more significant bits are all complemented.

   To change a bit from zero to one in a negative number, subtract the
   corresponding power of two from the absolute value. This can never
   underflow. To change a bit from one to zero, add the corresponding
   power of two, and this might overflow. E.g., if x = -001111, the
   two's complement is 110001. Clearing the least significant bit, we
   get two's complement 110000, and -010000. */

int
bam_mpz_tstbit (const bam_mpz_t d, bam_mp_bitcnt_t bit_index)
{
  bam_mp_size_t limb_index;
  unsigned shift;
  bam_mp_size_t ds;
  bam_mp_size_t dn;
  bam_mp_limb_t w;
  int bit;

  ds = d->_mp_size;
  dn = GMP_ABS (ds);
  limb_index = bit_index / GMP_LIMB_BITS;
  if (limb_index >= dn)
    return ds < 0;

  shift = bit_index % GMP_LIMB_BITS;
  w = d->_mp_d[limb_index];
  bit = (w >> shift) & 1;

  if (ds < 0)
    {
      /* d < 0. Check if any of the bits below is set: If so, our bit
     must be complemented. */
      if (shift > 0 && (bam_mp_limb_t) (w << (GMP_LIMB_BITS - shift)) > 0)
    return bit ^ 1;
      while (--limb_index >= 0)
    if (d->_mp_d[limb_index] > 0)
      return bit ^ 1;
    }
  return bit;
}

static void
bam_mpz_abs_add_bit (bam_mpz_t d, bam_mp_bitcnt_t bit_index)
{
  bam_mp_size_t dn, limb_index;
  bam_mp_limb_t bit;
  bam_mp_ptr dp;

  dn = GMP_ABS (d->_mp_size);

  limb_index = bit_index / GMP_LIMB_BITS;
  bit = (bam_mp_limb_t) 1 << (bit_index % GMP_LIMB_BITS);

  if (limb_index >= dn)
    {
      bam_mp_size_t i;
      /* The bit should be set outside of the end of the number.
     We have to increase the size of the number. */
      dp = MPZ_REALLOC (d, limb_index + 1);

      dp[limb_index] = bit;
      for (i = dn; i < limb_index; i++)
    dp[i] = 0;
      dn = limb_index + 1;
    }
  else
    {
      bam_mp_limb_t cy;

      dp = d->_mp_d;

      cy = bam_mpn_add_1 (dp + limb_index, dp + limb_index, dn - limb_index, bit);
      if (cy > 0)
    {
      dp = MPZ_REALLOC (d, dn + 1);
      dp[dn++] = cy;
    }
    }

  d->_mp_size = (d->_mp_size < 0) ? - dn : dn;
}

static void
bam_mpz_abs_sub_bit (bam_mpz_t d, bam_mp_bitcnt_t bit_index)
{
  bam_mp_size_t dn, limb_index;
  bam_mp_ptr dp;
  bam_mp_limb_t bit;

  dn = GMP_ABS (d->_mp_size);
  dp = d->_mp_d;

  limb_index = bit_index / GMP_LIMB_BITS;
  bit = (bam_mp_limb_t) 1 << (bit_index % GMP_LIMB_BITS);

  assert (limb_index < dn);

  bam_gmp_assert_nocarry (bam_mpn_sub_1 (dp + limb_index, dp + limb_index,
                 dn - limb_index, bit));
  dn = bam_mpn_normalized_size (dp, dn);
  d->_mp_size = (d->_mp_size < 0) ? - dn : dn;
}

void
bam_mpz_setbit (bam_mpz_t d, bam_mp_bitcnt_t bit_index)
{
  if (!bam_mpz_tstbit (d, bit_index))
    {
      if (d->_mp_size >= 0)
    bam_mpz_abs_add_bit (d, bit_index);
      else
    bam_mpz_abs_sub_bit (d, bit_index);
    }
}

void
bam_mpz_clrbit (bam_mpz_t d, bam_mp_bitcnt_t bit_index)
{
  if (bam_mpz_tstbit (d, bit_index))
    {
      if (d->_mp_size >= 0)
    bam_mpz_abs_sub_bit (d, bit_index);
      else
    bam_mpz_abs_add_bit (d, bit_index);
    }
}

void
bam_mpz_combit (bam_mpz_t d, bam_mp_bitcnt_t bit_index)
{
  if (bam_mpz_tstbit (d, bit_index) ^ (d->_mp_size < 0))
    bam_mpz_abs_sub_bit (d, bit_index);
  else
    bam_mpz_abs_add_bit (d, bit_index);
}

void
bam_mpz_com (bam_mpz_t r, const bam_mpz_t u)
{
  bam_mpz_add_ui (r, u, 1);
  bam_mpz_neg (r, r);
}

void
bam_mpz_and (bam_mpz_t r, const bam_mpz_t u, const bam_mpz_t v)
{
  bam_mp_size_t un, vn, rn, i;
  bam_mp_ptr up, vp, rp;

  bam_mp_limb_t ux, vx, rx;
  bam_mp_limb_t uc, vc, rc;
  bam_mp_limb_t ul, vl, rl;

  un = GMP_ABS (u->_mp_size);
  vn = GMP_ABS (v->_mp_size);
  if (un < vn)
    {
      MPZ_SRCPTR_SWAP (u, v);
      MP_SIZE_T_SWAP (un, vn);
    }
  if (vn == 0)
    {
      r->_mp_size = 0;
      return;
    }

  uc = u->_mp_size < 0;
  vc = v->_mp_size < 0;
  rc = uc & vc;

  ux = -uc;
  vx = -vc;
  rx = -rc;

  /* If the smaller input is positive, higher limbs don't matter. */
  rn = vx ? un : vn;

  rp = MPZ_REALLOC (r, rn + (bam_mp_size_t) rc);

  up = u->_mp_d;
  vp = v->_mp_d;

  i = 0;
  do
    {
      ul = (up[i] ^ ux) + uc;
      uc = ul < uc;

      vl = (vp[i] ^ vx) + vc;
      vc = vl < vc;

      rl = ( (ul & vl) ^ rx) + rc;
      rc = rl < rc;
      rp[i] = rl;
    }
  while (++i < vn);
  assert (vc == 0);

  for (; i < rn; i++)
    {
      ul = (up[i] ^ ux) + uc;
      uc = ul < uc;

      rl = ( (ul & vx) ^ rx) + rc;
      rc = rl < rc;
      rp[i] = rl;
    }
  if (rc)
    rp[rn++] = rc;
  else
    rn = bam_mpn_normalized_size (rp, rn);

  r->_mp_size = rx ? -rn : rn;
}

void
bam_mpz_ior (bam_mpz_t r, const bam_mpz_t u, const bam_mpz_t v)
{
  bam_mp_size_t un, vn, rn, i;
  bam_mp_ptr up, vp, rp;

  bam_mp_limb_t ux, vx, rx;
  bam_mp_limb_t uc, vc, rc;
  bam_mp_limb_t ul, vl, rl;

  un = GMP_ABS (u->_mp_size);
  vn = GMP_ABS (v->_mp_size);
  if (un < vn)
    {
      MPZ_SRCPTR_SWAP (u, v);
      MP_SIZE_T_SWAP (un, vn);
    }
  if (vn == 0)
    {
      bam_mpz_set (r, u);
      return;
    }

  uc = u->_mp_size < 0;
  vc = v->_mp_size < 0;
  rc = uc | vc;

  ux = -uc;
  vx = -vc;
  rx = -rc;

  /* If the smaller input is negative, by sign extension higher limbs
     don't matter. */
  rn = vx ? vn : un;

  rp = MPZ_REALLOC (r, rn + (bam_mp_size_t) rc);

  up = u->_mp_d;
  vp = v->_mp_d;

  i = 0;
  do
    {
      ul = (up[i] ^ ux) + uc;
      uc = ul < uc;

      vl = (vp[i] ^ vx) + vc;
      vc = vl < vc;

      rl = ( (ul | vl) ^ rx) + rc;
      rc = rl < rc;
      rp[i] = rl;
    }
  while (++i < vn);
  assert (vc == 0);

  for (; i < rn; i++)
    {
      ul = (up[i] ^ ux) + uc;
      uc = ul < uc;

      rl = ( (ul | vx) ^ rx) + rc;
      rc = rl < rc;
      rp[i] = rl;
    }
  if (rc)
    rp[rn++] = rc;
  else
    rn = bam_mpn_normalized_size (rp, rn);

  r->_mp_size = rx ? -rn : rn;
}

void
bam_mpz_xor (bam_mpz_t r, const bam_mpz_t u, const bam_mpz_t v)
{
  bam_mp_size_t un, vn, i;
  bam_mp_ptr up, vp, rp;

  bam_mp_limb_t ux, vx, rx;
  bam_mp_limb_t uc, vc, rc;
  bam_mp_limb_t ul, vl, rl;

  un = GMP_ABS (u->_mp_size);
  vn = GMP_ABS (v->_mp_size);
  if (un < vn)
    {
      MPZ_SRCPTR_SWAP (u, v);
      MP_SIZE_T_SWAP (un, vn);
    }
  if (vn == 0)
    {
      bam_mpz_set (r, u);
      return;
    }

  uc = u->_mp_size < 0;
  vc = v->_mp_size < 0;
  rc = uc ^ vc;

  ux = -uc;
  vx = -vc;
  rx = -rc;

  rp = MPZ_REALLOC (r, un + (bam_mp_size_t) rc);

  up = u->_mp_d;
  vp = v->_mp_d;

  i = 0;
  do
    {
      ul = (up[i] ^ ux) + uc;
      uc = ul < uc;

      vl = (vp[i] ^ vx) + vc;
      vc = vl < vc;

      rl = (ul ^ vl ^ rx) + rc;
      rc = rl < rc;
      rp[i] = rl;
    }
  while (++i < vn);
  assert (vc == 0);

  for (; i < un; i++)
    {
      ul = (up[i] ^ ux) + uc;
      uc = ul < uc;

      rl = (ul ^ ux) + rc;
      rc = rl < rc;
      rp[i] = rl;
    }
  if (rc)
    rp[un++] = rc;
  else
    un = bam_mpn_normalized_size (rp, un);

  r->_mp_size = rx ? -un : un;
}

static unsigned
bam_gmp_popcount_limb (bam_mp_limb_t x)
{
  unsigned c;

  /* Do 16 bits at a time, to avoid limb-sized constants. */
  int LOCAL_SHIFT_BITS = 16;
  for (c = 0; x > 0;)
    {
      unsigned w = x - ((x >> 1) & 0x5555);
      w = ((w >> 2) & 0x3333) + (w & 0x3333);
      w =  (w >> 4) + w;
      w = ((w >> 8) & 0x000f) + (w & 0x000f);
      c += w;
      if (GMP_LIMB_BITS > LOCAL_SHIFT_BITS)
    x >>= LOCAL_SHIFT_BITS;
      else
    x = 0;
    }
  return c;
}

bam_mp_bitcnt_t
bam_mpn_popcount (bam_mp_srcptr p, bam_mp_size_t n)
{
  bam_mp_size_t i;
  bam_mp_bitcnt_t c;

  for (c = 0, i = 0; i < n; i++)
    c += bam_gmp_popcount_limb (p[i]);

  return c;
}

bam_mp_bitcnt_t
bam_mpz_popcount (const bam_mpz_t u)
{
  bam_mp_size_t un;

  un = u->_mp_size;

  if (un < 0)
    return ~(bam_mp_bitcnt_t) 0;

  return bam_mpn_popcount (u->_mp_d, un);
}

bam_mp_bitcnt_t
bam_mpz_hamdist (const bam_mpz_t u, const bam_mpz_t v)
{
  bam_mp_size_t un, vn, i;
  bam_mp_limb_t uc, vc, ul, vl, comp;
  bam_mp_srcptr up, vp;
  bam_mp_bitcnt_t c;

  un = u->_mp_size;
  vn = v->_mp_size;

  if ( (un ^ vn) < 0)
    return ~(bam_mp_bitcnt_t) 0;

  comp = - (uc = vc = (un < 0));
  if (uc)
    {
      assert (vn < 0);
      un = -un;
      vn = -vn;
    }

  up = u->_mp_d;
  vp = v->_mp_d;

  if (un < vn)
    MPN_SRCPTR_SWAP (up, un, vp, vn);

  for (i = 0, c = 0; i < vn; i++)
    {
      ul = (up[i] ^ comp) + uc;
      uc = ul < uc;

      vl = (vp[i] ^ comp) + vc;
      vc = vl < vc;

      c += bam_gmp_popcount_limb (ul ^ vl);
    }
  assert (vc == 0);

  for (; i < un; i++)
    {
      ul = (up[i] ^ comp) + uc;
      uc = ul < uc;

      c += bam_gmp_popcount_limb (ul ^ comp);
    }

  return c;
}

bam_mp_bitcnt_t
bam_mpz_scan1 (const bam_mpz_t u, bam_mp_bitcnt_t starting_bit)
{
  bam_mp_ptr up;
  bam_mp_size_t us, un, i;
  bam_mp_limb_t limb, ux;

  us = u->_mp_size;
  un = GMP_ABS (us);
  i = starting_bit / GMP_LIMB_BITS;

  /* Past the end there's no 1 bits for u>=0, or an immediate 1 bit
     for u<0. Notice this test picks up any u==0 too. */
  if (i >= un)
    return (us >= 0 ? ~(bam_mp_bitcnt_t) 0 : starting_bit);

  up = u->_mp_d;
  ux = 0;
  limb = up[i];

  if (starting_bit != 0)
    {
      if (us < 0)
    {
      ux = bam_mpn_zero_p (up, i);
      limb = ~ limb + ux;
      ux = - (bam_mp_limb_t) (limb >= ux);
    }

      /* Mask to 0 all bits before starting_bit, thus ignoring them. */
      limb &= GMP_LIMB_MAX << (starting_bit % GMP_LIMB_BITS);
    }

  return bam_mpn_common_scan (limb, i, up, un, ux);
}

bam_mp_bitcnt_t
bam_mpz_scan0 (const bam_mpz_t u, bam_mp_bitcnt_t starting_bit)
{
  bam_mp_ptr up;
  bam_mp_size_t us, un, i;
  bam_mp_limb_t limb, ux;

  us = u->_mp_size;
  ux = - (bam_mp_limb_t) (us >= 0);
  un = GMP_ABS (us);
  i = starting_bit / GMP_LIMB_BITS;

  /* When past end, there's an immediate 0 bit for u>=0, or no 0 bits for
     u<0.  Notice this test picks up all cases of u==0 too. */
  if (i >= un)
    return (ux ? starting_bit : ~(bam_mp_bitcnt_t) 0);

  up = u->_mp_d;
  limb = up[i] ^ ux;

  if (ux == 0)
    limb -= bam_mpn_zero_p (up, i); /* limb = ~(~limb + zero_p) */

  /* Mask all bits before starting_bit, thus ignoring them. */
  limb &= GMP_LIMB_MAX << (starting_bit % GMP_LIMB_BITS);

  return bam_mpn_common_scan (limb, i, up, un, ux);
}

/* MPZ base conversion. */

size_t
bam_mpz_sizeinbase (const bam_mpz_t u, int base)
{
  bam_mp_size_t un, tn;
  bam_mp_srcptr up;
  bam_mp_ptr tp;
  bam_mp_bitcnt_t bits;
  struct bam_gmp_div_inverse bi;
  size_t ndigits;

  assert (base >= 2);
  assert (base <= 62);

  un = GMP_ABS (u->_mp_size);
  if (un == 0)
    return 1;

  up = u->_mp_d;

  bits = (un - 1) * GMP_LIMB_BITS + bam_mpn_limb_size_in_base_2 (up[un-1]);
  switch (base)
    {
    case 2:
      return bits;
    case 4:
      return (bits + 1) / 2;
    case 8:
      return (bits + 2) / 3;
    case 16:
      return (bits + 3) / 4;
    case 32:
      return (bits + 4) / 5;
      /* FIXME: Do something more clever for the common case of base
     10. */
    }

  tp = bam_gmp_alloc_limbs (un);
  bam_mpn_copyi (tp, up, un);
  bam_mpn_div_qr_1_invert (&bi, base);

  tn = un;
  ndigits = 0;
  do
    {
      ndigits++;
      bam_mpn_div_qr_1_preinv (tp, tp, tn, &bi);
      tn -= (tp[tn-1] == 0);
    }
  while (tn > 0);

  bam_gmp_free_limbs (tp, un);
  return ndigits;
}

char *
bam_mpz_get_str (char *sp, int base, const bam_mpz_t u)
{
  unsigned bits;
  const char *digits;
  bam_mp_size_t un;
  size_t i, sn, osn;

  digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
  if (base > 1)
    {
      if (base <= 36)
    digits = "0123456789abcdefghijklmnopqrstuvwxyz";
      else if (base > 62)
    return NULL;
    }
  else if (base >= -1)
    base = 10;
  else
    {
      base = -base;
      if (base > 36)
    return NULL;
    }

  sn = 1 + bam_mpz_sizeinbase (u, base);
  if (!sp)
    {
      osn = 1 + sn;
      sp = (char *) bam_gmp_alloc (osn);
    }
  else
    osn = 0;
  un = GMP_ABS (u->_mp_size);

  if (un == 0)
    {
      sp[0] = '0';
      sn = 1;
      goto ret;
    }

  i = 0;

  if (u->_mp_size < 0)
    sp[i++] = '-';

  bits = bam_mpn_base_power_of_two_p (base);

  if (bits)
    /* Not modified in this case. */
    sn = i + bam_mpn_get_str_bits ((unsigned char *) sp + i, bits, u->_mp_d, un);
  else
    {
      struct bam_mpn_base_info info;
      bam_mp_ptr tp;

      bam_mpn_get_base_info (&info, base);
      tp = bam_gmp_alloc_limbs (un);
      bam_mpn_copyi (tp, u->_mp_d, un);

      sn = i + bam_mpn_get_str_other ((unsigned char *) sp + i, base, &info, tp, un);
      bam_gmp_free_limbs (tp, un);
    }

  for (; i < sn; i++)
    sp[i] = digits[(unsigned char) sp[i]];

ret:
  sp[sn] = '\0';
  if (osn && osn != sn + 1)
    sp = (char*) bam_gmp_realloc (sp, osn, sn + 1);
  return sp;
}

int
bam_mpz_set_str (bam_mpz_t r, const char *sp, int base)
{
  unsigned bits, value_of_a;
  bam_mp_size_t rn, alloc;
  bam_mp_ptr rp;
  size_t dn, sn;
  int sign;
  unsigned char *dp;

  assert (base == 0 || (base >= 2 && base <= 62));

  while (isspace( (unsigned char) *sp))
    sp++;

  sign = (*sp == '-');
  sp += sign;

  if (base == 0)
    {
      if (sp[0] == '0')
    {
      if (sp[1] == 'x' || sp[1] == 'X')
        {
          base = 16;
          sp += 2;
        }
      else if (sp[1] == 'b' || sp[1] == 'B')
        {
          base = 2;
          sp += 2;
        }
      else
        base = 8;
    }
      else
    base = 10;
    }

  if (!*sp)
    {
      r->_mp_size = 0;
      return -1;
    }
  sn = strlen(sp);
  dp = (unsigned char *) bam_gmp_alloc (sn);

  value_of_a = (base > 36) ? 36 : 10;
  for (dn = 0; *sp; sp++)
    {
      unsigned digit;

      if (isspace ((unsigned char) *sp))
    continue;
      else if (*sp >= '0' && *sp <= '9')
    digit = *sp - '0';
      else if (*sp >= 'a' && *sp <= 'z')
    digit = *sp - 'a' + value_of_a;
      else if (*sp >= 'A' && *sp <= 'Z')
    digit = *sp - 'A' + 10;
      else
    digit = base; /* fail */

      if (digit >= (unsigned) base)
    {
      bam_gmp_free (dp, sn);
      r->_mp_size = 0;
      return -1;
    }

      dp[dn++] = digit;
    }

  if (!dn)
    {
      bam_gmp_free (dp, sn);
      r->_mp_size = 0;
      return -1;
    }
  bits = bam_mpn_base_power_of_two_p (base);

  if (bits > 0)
    {
      alloc = (dn * bits + GMP_LIMB_BITS - 1) / GMP_LIMB_BITS;
      rp = MPZ_REALLOC (r, alloc);
      rn = bam_mpn_set_str_bits (rp, dp, dn, bits);
    }
  else
    {
      struct bam_mpn_base_info info;
      bam_mpn_get_base_info (&info, base);
      alloc = (dn + info.exp - 1) / info.exp;
      rp = MPZ_REALLOC (r, alloc);
      rn = bam_mpn_set_str_other (rp, dp, dn, base, &info);
      /* Normalization, needed for all-zero input. */
      assert (rn > 0);
      rn -= rp[rn-1] == 0;
    }
  assert (rn <= alloc);
  bam_gmp_free (dp, sn);

  r->_mp_size = sign ? - rn : rn;

  return 0;
}

int
bam_mpz_init_set_str (bam_mpz_t r, const char *sp, int base)
{
  bam_mpz_init (r);
  return bam_mpz_set_str (r, sp, base);
}

size_t
bam_mpz_out_str (FILE *stream, int base, const bam_mpz_t x)
{
  char *str;
  size_t len, n;

  str = bam_mpz_get_str (NULL, base, x);
  if (!str)
    return 0;
  len = strlen (str);
  n = fwrite (str, 1, len, stream);
  bam_gmp_free (str, len + 1);
  return n;
}

static int
bam_gmp_detect_endian (void)
{
  static const int i = 2;
  const unsigned char *p = (const unsigned char *) &i;
  return 1 - *p;
}

/* Import and export. Does not support nails. */
void
bam_mpz_import (bam_mpz_t r, size_t count, int order, size_t size, int endian,
        size_t nails, const void *src)
{
  const unsigned char *p;
  ptrdiff_t word_step;
  bam_mp_ptr rp;
  bam_mp_size_t rn;

  /* The current (partial) limb. */
  bam_mp_limb_t limb;
  /* The number of bytes already copied to this limb (starting from
     the low end). */
  size_t bytes;
  /* The index where the limb should be stored, when completed. */
  bam_mp_size_t i;

  if (nails != 0)
    bam_gmp_die ("mpz_import: Nails not supported.");

  assert (order == 1 || order == -1);
  assert (endian >= -1 && endian <= 1);

  if (endian == 0)
    endian = bam_gmp_detect_endian ();

  p = (unsigned char *) src;

  word_step = (order != endian) ? 2 * size : 0;

  /* Process bytes from the least significant end, so point p at the
     least significant word. */
  if (order == 1)
    {
      p += size * (count - 1);
      word_step = - word_step;
    }

  /* And at least significant byte of that word. */
  if (endian == 1)
    p += (size - 1);

  rn = (size * count + sizeof(bam_mp_limb_t) - 1) / sizeof(bam_mp_limb_t);
  rp = MPZ_REALLOC (r, rn);

  for (limb = 0, bytes = 0, i = 0; count > 0; count--, p += word_step)
    {
      size_t j;
      for (j = 0; j < size; j++, p -= (ptrdiff_t) endian)
    {
      limb |= (bam_mp_limb_t) *p << (bytes++ * CHAR_BIT);
      if (bytes == sizeof(bam_mp_limb_t))
        {
          rp[i++] = limb;
          bytes = 0;
          limb = 0;
        }
    }
    }
  assert (i + (bytes > 0) == rn);
  if (limb != 0)
    rp[i++] = limb;
  else
    i = bam_mpn_normalized_size (rp, i);

  r->_mp_size = i;
}

void *
bam_mpz_export (void *r, size_t *countp, int order, size_t size, int endian,
        size_t nails, const bam_mpz_t u)
{
  size_t count;
  bam_mp_size_t un;

  if (nails != 0)
    bam_gmp_die ("mpz_export: Nails not supported.");

  assert (order == 1 || order == -1);
  assert (endian >= -1 && endian <= 1);
  assert (size > 0 || u->_mp_size == 0);

  un = u->_mp_size;
  count = 0;
  if (un != 0)
    {
      size_t k;
      unsigned char *p;
      ptrdiff_t word_step;
      /* The current (partial) limb. */
      bam_mp_limb_t limb;
      /* The number of bytes left to do in this limb. */
      size_t bytes;
      /* The index where the limb was read. */
      bam_mp_size_t i;

      un = GMP_ABS (un);

      /* Count bytes in top limb. */
      limb = u->_mp_d[un-1];
      assert (limb != 0);

      k = (GMP_LIMB_BITS <= CHAR_BIT);
      if (!k)
    {
      do {
        int LOCAL_CHAR_BIT = CHAR_BIT;
        k++; limb >>= LOCAL_CHAR_BIT;
      } while (limb != 0);
    }
      /* else limb = 0; */

      count = (k + (un-1) * sizeof (bam_mp_limb_t) + size - 1) / size;

      if (!r)
    r = bam_gmp_alloc (count * size);

      if (endian == 0)
    endian = bam_gmp_detect_endian ();

      p = (unsigned char *) r;

      word_step = (order != endian) ? 2 * size : 0;

      /* Process bytes from the least significant end, so point p at the
     least significant word. */
      if (order == 1)
    {
      p += size * (count - 1);
      word_step = - word_step;
    }

      /* And at least significant byte of that word. */
      if (endian == 1)
    p += (size - 1);

      for (bytes = 0, i = 0, k = 0; k < count; k++, p += word_step)
    {
      size_t j;
      for (j = 0; j < size; ++j, p -= (ptrdiff_t) endian)
        {
          if (sizeof (bam_mp_limb_t) == 1)
        {
          if (i < un)
            *p = u->_mp_d[i++];
          else
            *p = 0;
        }
          else
        {
          int LOCAL_CHAR_BIT = CHAR_BIT;
          if (bytes == 0)
            {
              if (i < un)
            limb = u->_mp_d[i++];
              bytes = sizeof (bam_mp_limb_t);
            }
          *p = limb;
          limb >>= LOCAL_CHAR_BIT;
          bytes--;
        }
        }
    }
      assert (i == un);
      assert (k == count);
    }

  if (countp)
    *countp = count;

  return r;
}
