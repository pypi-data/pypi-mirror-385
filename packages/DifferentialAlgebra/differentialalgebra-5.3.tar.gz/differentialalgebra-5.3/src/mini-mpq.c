/* mini-mpq, a minimalistic implementation of a GNU GMP subset.

   Contributed to the GNU project by Marco Bodrato

   Acknowledgment: special thanks to Bradley Lucier for his comments
   to the preliminary version of this code.

Copyright 2018-2022 Free Software Foundation, Inc.

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

#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "mini-mpq.h"

#ifndef GMP_LIMB_HIGHBIT
/* Define macros and static functions already defined by mini-gmp.c */
#define GMP_LIMB_BITS (sizeof(bam_mp_limb_t) * CHAR_BIT)
#define GMP_LIMB_HIGHBIT ((bam_mp_limb_t) 1 << (GMP_LIMB_BITS - 1))
#define GMP_LIMB_MAX ((bam_mp_limb_t) ~ (bam_mp_limb_t) 0)
#define GMP_NEG_CAST(T,x) (-((T)((x) + 1) - 1))
#define GMP_MIN(a, b) ((a) < (b) ? (a) : (b))

static bam_mpz_srcptr
bam_mpz_roinit_normal_n (bam_mpz_t x, bam_mp_srcptr xp, bam_mp_size_t xs)
{
  x->_mp_alloc = 0;
  x->_mp_d = (bam_mp_ptr) xp;
  x->_mp_size = xs;
  return x;
}

static void
bam_gmp_die (const char *msg)
{
  fprintf (stderr, "%s\n", msg);
  abort();
}
#endif

/* MPQ helper functions */
static bam_mpq_srcptr
bam_mpq_roinit_normal_nn (bam_mpq_t x, bam_mp_srcptr np, bam_mp_size_t ns,
             bam_mp_srcptr dp, bam_mp_size_t ds)
{
  bam_mpz_roinit_normal_n (bam_mpq_numref(x), np, ns);
  bam_mpz_roinit_normal_n (bam_mpq_denref(x), dp, ds);
  return x;
}

static bam_mpq_srcptr
bam_mpq_roinit_zz (bam_mpq_t x, bam_mpz_srcptr n, bam_mpz_srcptr d)
{
  return bam_mpq_roinit_normal_nn (x, n->_mp_d, n->_mp_size,
                   d->_mp_d, d->_mp_size);
}

static void
bam_mpq_nan_init (bam_mpq_t x)
{
  bam_mpz_init (bam_mpq_numref (x));
  bam_mpz_init (bam_mpq_denref (x));
}

void
bam_mpq_init (bam_mpq_t x)
{
  bam_mpz_init (bam_mpq_numref (x));
  bam_mpz_init_set_ui (bam_mpq_denref (x), 1);
}

void
bam_mpq_clear (bam_mpq_t x)
{
  bam_mpz_clear (bam_mpq_numref (x));
  bam_mpz_clear (bam_mpq_denref (x));
}

static void
bam_mpq_canonical_sign (bam_mpq_t r)
{
  bam_mp_size_t ds = bam_mpq_denref (r)->_mp_size;
  if (ds <= 0)
    {
      if (ds == 0)
    bam_gmp_die("mpq: Fraction with zero denominator.");
      bam_mpz_neg (bam_mpq_denref (r), bam_mpq_denref (r));
      bam_mpz_neg (bam_mpq_numref (r), bam_mpq_numref (r));
    }
}

static void
bam_mpq_helper_canonicalize (bam_mpq_t r, const bam_mpz_t num, const bam_mpz_t den)
{
  if (num->_mp_size == 0)
    bam_mpq_set_ui (r, 0, 1);
  else
    {
      bam_mpz_t g;

      bam_mpz_init (g);
      bam_mpz_gcd (g, num, den);
      bam_mpz_tdiv_q (bam_mpq_numref (r), num, g);
      bam_mpz_tdiv_q (bam_mpq_denref (r), den, g);
      bam_mpz_clear (g);
      bam_mpq_canonical_sign (r);
    }
}

void
bam_mpq_canonicalize (bam_mpq_t r)
{
  bam_mpq_helper_canonicalize (r, bam_mpq_numref (r), bam_mpq_denref (r));
}

void
bam_mpq_swap (bam_mpq_t a, bam_mpq_t b)
{
  bam_mpz_swap (bam_mpq_numref (a), bam_mpq_numref (b));
  bam_mpz_swap (bam_mpq_denref (a), bam_mpq_denref (b));
}

/* MPQ assignment and conversions. */
void
bam_mpz_set_q (bam_mpz_t r, const bam_mpq_t q)
{
  bam_mpz_tdiv_q (r, bam_mpq_numref (q), bam_mpq_denref (q));
}

void
bam_mpq_set (bam_mpq_t r, const bam_mpq_t q)
{
  bam_mpz_set (bam_mpq_numref (r), bam_mpq_numref (q));
  bam_mpz_set (bam_mpq_denref (r), bam_mpq_denref (q));
}

void
bam_mpq_set_ui (bam_mpq_t r, unsigned ba0_int_p n, unsigned ba0_int_p d)
{
  bam_mpz_set_ui (bam_mpq_numref (r), n);
  bam_mpz_set_ui (bam_mpq_denref (r), d);
}

void
bam_mpq_set_si (bam_mpq_t r, signed ba0_int_p n, unsigned ba0_int_p d)
{
  bam_mpz_set_si (bam_mpq_numref (r), n);
  bam_mpz_set_ui (bam_mpq_denref (r), d);
}

void
bam_mpq_set_z (bam_mpq_t r, const bam_mpz_t n)
{
  bam_mpz_set_ui (bam_mpq_denref (r), 1);
  bam_mpz_set (bam_mpq_numref (r), n);
}

void
bam_mpq_set_num (bam_mpq_t r, const bam_mpz_t z)
{
  bam_mpz_set (bam_mpq_numref (r), z);
}

void
bam_mpq_set_den (bam_mpq_t r, const bam_mpz_t z)
{
  bam_mpz_set (bam_mpq_denref (r), z);
}

void
bam_mpq_get_num (bam_mpz_t r, const bam_mpq_t q)
{
  bam_mpz_set (r, bam_mpq_numref (q));
}

void
bam_mpq_get_den (bam_mpz_t r, const bam_mpq_t q)
{
  bam_mpz_set (r, bam_mpq_denref (q));
}

/* MPQ comparisons and the like. */
int
bam_mpq_cmp (const bam_mpq_t a, const bam_mpq_t b)
{
  bam_mpz_t t1, t2;
  int res;

  bam_mpz_init (t1);
  bam_mpz_init (t2);
  bam_mpz_mul (t1, bam_mpq_numref (a), bam_mpq_denref (b));
  bam_mpz_mul (t2, bam_mpq_numref (b), bam_mpq_denref (a));
  res = bam_mpz_cmp (t1, t2);
  bam_mpz_clear (t1);
  bam_mpz_clear (t2);

  return res;
}

int
bam_mpq_cmp_z (const bam_mpq_t a, const bam_mpz_t b)
{
  bam_mpz_t t;
  int res;

  bam_mpz_init (t);
  bam_mpz_mul (t, b, bam_mpq_denref (a));
  res = bam_mpz_cmp (bam_mpq_numref (a), t);
  bam_mpz_clear (t);

  return res;
}

int
bam_mpq_equal (const bam_mpq_t a, const bam_mpq_t b)
{
  return (bam_mpz_cmp (bam_mpq_numref (a), bam_mpq_numref (b)) == 0) &&
    (bam_mpz_cmp (bam_mpq_denref (a), bam_mpq_denref (b)) == 0);
}

int
bam_mpq_cmp_ui (const bam_mpq_t q, unsigned ba0_int_p n, unsigned ba0_int_p d)
{
  bam_mpq_t t;
  assert (d != 0);
  if (ULONG_MAX <= GMP_LIMB_MAX) {
    bam_mp_limb_t nl = n, dl = d;
    return bam_mpq_cmp (q, bam_mpq_roinit_normal_nn (t, &nl, n != 0, &dl, 1));
  } else {
    int ret;

    bam_mpq_nan_init (t);
    bam_mpq_set_ui (t, n, d);
    ret = bam_mpq_cmp (q, t);
    bam_mpq_clear (t);

    return ret;
  }
}

int
bam_mpq_cmp_si (const bam_mpq_t q, signed ba0_int_p n, unsigned ba0_int_p d)
{
  assert (d != 0);

  if (n >= 0)
    return bam_mpq_cmp_ui (q, n, d);
  else
    {
      bam_mpq_t t;

      if (ULONG_MAX <= GMP_LIMB_MAX)
    {
      bam_mp_limb_t nl = GMP_NEG_CAST (unsigned ba0_int_p, n), dl = d;
      return bam_mpq_cmp (q, bam_mpq_roinit_normal_nn (t, &nl, -1, &dl, 1));
    }
      else
    {
      unsigned ba0_int_p l_n = GMP_NEG_CAST (unsigned ba0_int_p, n);

      bam_mpq_roinit_normal_nn (t, bam_mpq_numref (q)->_mp_d, - bam_mpq_numref (q)->_mp_size,
                bam_mpq_denref (q)->_mp_d, bam_mpq_denref (q)->_mp_size);
      return - bam_mpq_cmp_ui (t, l_n, d);
    }
    }
}

int
bam_mpq_sgn (const bam_mpq_t a)
{
  return bam_mpz_sgn (bam_mpq_numref (a));
}

/* MPQ arithmetic. */
void
bam_mpq_abs (bam_mpq_t r, const bam_mpq_t q)
{
  bam_mpz_abs (bam_mpq_numref (r), bam_mpq_numref (q));
  bam_mpz_set (bam_mpq_denref (r), bam_mpq_denref (q));
}

void
bam_mpq_neg (bam_mpq_t r, const bam_mpq_t q)
{
  bam_mpz_neg (bam_mpq_numref (r), bam_mpq_numref (q));
  bam_mpz_set (bam_mpq_denref (r), bam_mpq_denref (q));
}

void
bam_mpq_add (bam_mpq_t r, const bam_mpq_t a, const bam_mpq_t b)
{
  bam_mpz_t t;

  bam_mpz_init (t);
  bam_mpz_gcd (t, bam_mpq_denref (a), bam_mpq_denref (b));
  if (bam_mpz_cmp_ui (t, 1) == 0)
    {
      bam_mpz_mul (t, bam_mpq_numref (a), bam_mpq_denref (b));
      bam_mpz_addmul (t, bam_mpq_numref (b), bam_mpq_denref (a));
      bam_mpz_mul (bam_mpq_denref (r), bam_mpq_denref (a), bam_mpq_denref (b));
      bam_mpz_swap (bam_mpq_numref (r), t);
    }
  else
    {
      bam_mpz_t x, y;
      bam_mpz_init (x);
      bam_mpz_init (y);

      bam_mpz_tdiv_q (x, bam_mpq_denref (b), t);
      bam_mpz_tdiv_q (y, bam_mpq_denref (a), t);
      bam_mpz_mul (x, bam_mpq_numref (a), x);
      bam_mpz_addmul (x, bam_mpq_numref (b), y);

      bam_mpz_gcd (t, x, t);
      bam_mpz_tdiv_q (bam_mpq_numref (r), x, t);
      bam_mpz_tdiv_q (x, bam_mpq_denref (b), t);
      bam_mpz_mul (bam_mpq_denref (r), x, y);

      bam_mpz_clear (x);
      bam_mpz_clear (y);
    }
  bam_mpz_clear (t);
}

void
bam_mpq_sub (bam_mpq_t r, const bam_mpq_t a, const bam_mpq_t b)
{
  bam_mpq_t t;

  bam_mpq_roinit_normal_nn (t, bam_mpq_numref (b)->_mp_d, - bam_mpq_numref (b)->_mp_size,
            bam_mpq_denref (b)->_mp_d, bam_mpq_denref (b)->_mp_size);
  bam_mpq_add (r, a, t);
}

void
bam_mpq_div (bam_mpq_t r, const bam_mpq_t a, const bam_mpq_t b)
{
  bam_mpq_t t;
  bam_mpq_mul (r, a, bam_mpq_roinit_zz (t, bam_mpq_denref (b), bam_mpq_numref (b)));
}

void
bam_mpq_mul (bam_mpq_t r, const bam_mpq_t a, const bam_mpq_t b)
{
  bam_mpq_t t;
  bam_mpq_nan_init (t);

  if (a != b) {
    bam_mpq_helper_canonicalize (t, bam_mpq_numref (a), bam_mpq_denref (b));
    bam_mpq_helper_canonicalize (r, bam_mpq_numref (b), bam_mpq_denref (a));

    a = r;
    b = t;
  }

  bam_mpz_mul (bam_mpq_numref (r), bam_mpq_numref (a), bam_mpq_numref (b));
  bam_mpz_mul (bam_mpq_denref (r), bam_mpq_denref (a), bam_mpq_denref (b));
  bam_mpq_clear (t);
}

static void
bam_mpq_helper_2exp (bam_mpz_t rn, bam_mpz_t rd, const bam_mpz_t qn, const bam_mpz_t qd, bam_mp_bitcnt_t e)
{
  bam_mp_bitcnt_t z = bam_mpz_scan1 (qd, 0);
  z = GMP_MIN (z, e);
  bam_mpz_mul_2exp (rn, qn, e - z);
  bam_mpz_tdiv_q_2exp (rd, qd, z);
}

void
bam_mpq_div_2exp (bam_mpq_t r, const bam_mpq_t q, bam_mp_bitcnt_t e)
{
  bam_mpq_helper_2exp (bam_mpq_denref (r), bam_mpq_numref (r), bam_mpq_denref (q), bam_mpq_numref (q), e);
}

void
bam_mpq_mul_2exp (bam_mpq_t r, const bam_mpq_t q, bam_mp_bitcnt_t e)
{
  bam_mpq_helper_2exp (bam_mpq_numref (r), bam_mpq_denref (r), bam_mpq_numref (q), bam_mpq_denref (q), e);
}

void
bam_mpq_inv (bam_mpq_t r, const bam_mpq_t q)
{
  bam_mpq_set (r, q);
  bam_mpz_swap (bam_mpq_denref (r), bam_mpq_numref (r));
  bam_mpq_canonical_sign (r);
}

/* MPQ to/from double. */
void
bam_mpq_set_d (bam_mpq_t r, double x)
{
  bam_mpz_set_ui (bam_mpq_denref (r), 1);

  /* x != x is true when x is a NaN, and x == x * 0.5 is true when x is
     zero or infinity. */
  if (x == x * 0.5 || x != x)
    bam_mpq_numref (r)->_mp_size = 0;
  else
    {
      double B;
      bam_mp_bitcnt_t e;

      B = 4.0 * (double) (GMP_LIMB_HIGHBIT >> 1);
      for (e = 0; x != x + 0.5; e += GMP_LIMB_BITS)
    x *= B;

      bam_mpz_set_d (bam_mpq_numref (r), x);
      bam_mpq_div_2exp (r, r, e);
    }
}

double
bam_mpq_get_d (const bam_mpq_t u)
{
  bam_mp_bitcnt_t ne, de, ee;
  bam_mpz_t z;
  double B, ret;

  ne = bam_mpz_sizeinbase (bam_mpq_numref (u), 2);
  de = bam_mpz_sizeinbase (bam_mpq_denref (u), 2);

  ee = CHAR_BIT * sizeof (double);
  if (de == 1 || ne > de + ee)
    ee = 0;
  else
    ee = (ee + de - ne) / GMP_LIMB_BITS + 1;

  bam_mpz_init (z);
  bam_mpz_mul_2exp (z, bam_mpq_numref (u), ee * GMP_LIMB_BITS);
  bam_mpz_tdiv_q (z, z, bam_mpq_denref (u));
  ret = bam_mpz_get_d (z);
  bam_mpz_clear (z);

  B = 4.0 * (double) (GMP_LIMB_HIGHBIT >> 1);
  for (B = 1 / B; ee != 0; --ee)
    ret *= B;

  return ret;
}

/* MPQ and strings/streams. */
char *
bam_mpq_get_str (char *sp, int base, const bam_mpq_t q)
{
  char *res;
  char *rden;
  size_t len;

  res = bam_mpz_get_str (sp, base, bam_mpq_numref (q));
  if (res == NULL || bam_mpz_cmp_ui (bam_mpq_denref (q), 1) == 0)
    return res;

  len = strlen (res) + 1;
  rden = sp ? sp + len : NULL;
  rden = bam_mpz_get_str (rden, base, bam_mpq_denref (q));
  assert (rden != NULL);

  if (sp == NULL) {
    void * (*bam_gmp_reallocate_func) (void *, size_t, size_t);
    void (*bam_gmp_free_func) (void *, size_t);
    size_t lden;

    bam_mp_get_memory_functions (NULL, &bam_gmp_reallocate_func, &bam_gmp_free_func);
    lden = strlen (rden) + 1;
    res = (char *) bam_gmp_reallocate_func (res, len, (lden + len) * sizeof (char));
    memcpy (res + len, rden, lden);
    bam_gmp_free_func (rden, lden);
  }

  res [len - 1] = '/';
  return res;
}

size_t
bam_mpq_out_str (FILE *stream, int base, const bam_mpq_t x)
{
  char * str;
  size_t len, n;
  void (*bam_gmp_free_func) (void *, size_t);

  str = bam_mpq_get_str (NULL, base, x);
  if (!str)
    return 0;
  len = strlen (str);
  n = fwrite (str, 1, len, stream);
  bam_mp_get_memory_functions (NULL, NULL, &bam_gmp_free_func);
  bam_gmp_free_func (str, len + 1);
  return n;
}

int
bam_mpq_set_str (bam_mpq_t r, const char *sp, int base)
{
  const char *slash;

  slash = strchr (sp, '/');
  if (slash == NULL) {
    bam_mpz_set_ui (bam_mpq_denref(r), 1);
    return bam_mpz_set_str (bam_mpq_numref(r), sp, base);
  } else {
    char *num;
    size_t numlen;
    int ret;
    void * (*bam_gmp_allocate_func) (size_t);
    void (*bam_gmp_free_func) (void *, size_t);

    bam_mp_get_memory_functions (&bam_gmp_allocate_func, NULL, &bam_gmp_free_func);
    numlen = slash - sp;
    num = (char *) bam_gmp_allocate_func (numlen + 1);
    memcpy (num, sp, numlen);
    num[numlen] = '\0';
    ret = bam_mpz_set_str (bam_mpq_numref(r), num, base);
    bam_gmp_free_func (num, numlen + 1);

    if (ret != 0)
      return ret;

    return bam_mpz_set_str (bam_mpq_denref(r), slash + 1, base);
  }
}
