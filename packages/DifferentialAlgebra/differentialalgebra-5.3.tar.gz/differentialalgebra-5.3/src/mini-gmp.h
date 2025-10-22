/* mini-gmp, a minimalistic implementation of a GNU GMP subset.

Copyright 2011-2015, 2017, 2019-2021 Free Software Foundation, Inc.

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

/* About mini-gmp: This is a minimal implementation of a subset of the
   GMP interface. It is intended for inclusion into applications which
   have modest bignums needs, as a fallback when the real GMP library
   is not installed.

   This file defines the public interface. */

#if !defined (__MINI_GMP_H__)
#define __MINI_GMP_H__
#include "ba0_common.h"

/* For size_t */
#include <stddef.h>

#if defined (__cplusplus)
extern "C" {
#endif

void bam_mp_set_memory_functions (void *(*) (size_t),
                  void *(*) (void *, size_t, size_t),
                  void (*) (void *, size_t));

void bam_mp_get_memory_functions (void *(**) (size_t),
                  void *(**) (void *, size_t, size_t),
                  void (**) (void *, size_t));

#if !defined (MINI_GMP_LIMB_TYPE)
#define MINI_GMP_LIMB_TYPE ba0_int_p
#endif

typedef unsigned MINI_GMP_LIMB_TYPE bam_mp_limb_t;
typedef ba0_int_p bam_mp_size_t;
typedef unsigned ba0_int_p bam_mp_bitcnt_t;

typedef bam_mp_limb_t *bam_mp_ptr;
typedef const bam_mp_limb_t *bam_mp_srcptr;

typedef struct
{
  int _mp_alloc;        /* Number of *limbs* allocated and pointed
                   to by the _mp_d field.  */
  int _mp_size;            /* abs(_mp_size) is the number of limbs the
                   last field points to.  If _mp_size is
                   negative this is a negative number.  */
  bam_mp_limb_t *_mp_d;        /* Pointer to the limbs.  */
} bam__mpz_struct;

typedef bam__mpz_struct bam_mpz_t[1];

typedef bam__mpz_struct *bam_mpz_ptr;
typedef const bam__mpz_struct *bam_mpz_srcptr;

extern const int bam_mp_bits_per_limb;

void bam_mpn_copyi (bam_mp_ptr, bam_mp_srcptr, bam_mp_size_t);
void bam_mpn_copyd (bam_mp_ptr, bam_mp_srcptr, bam_mp_size_t);
void bam_mpn_zero (bam_mp_ptr, bam_mp_size_t);

int bam_mpn_cmp (bam_mp_srcptr, bam_mp_srcptr, bam_mp_size_t);
int bam_mpn_zero_p (bam_mp_srcptr, bam_mp_size_t);

bam_mp_limb_t bam_mpn_add_1 (bam_mp_ptr, bam_mp_srcptr, bam_mp_size_t, bam_mp_limb_t);
bam_mp_limb_t bam_mpn_add_n (bam_mp_ptr, bam_mp_srcptr, bam_mp_srcptr, bam_mp_size_t);
bam_mp_limb_t bam_mpn_add (bam_mp_ptr, bam_mp_srcptr, bam_mp_size_t, bam_mp_srcptr, bam_mp_size_t);

bam_mp_limb_t bam_mpn_sub_1 (bam_mp_ptr, bam_mp_srcptr, bam_mp_size_t, bam_mp_limb_t);
bam_mp_limb_t bam_mpn_sub_n (bam_mp_ptr, bam_mp_srcptr, bam_mp_srcptr, bam_mp_size_t);
bam_mp_limb_t bam_mpn_sub (bam_mp_ptr, bam_mp_srcptr, bam_mp_size_t, bam_mp_srcptr, bam_mp_size_t);

bam_mp_limb_t bam_mpn_mul_1 (bam_mp_ptr, bam_mp_srcptr, bam_mp_size_t, bam_mp_limb_t);
bam_mp_limb_t bam_mpn_addmul_1 (bam_mp_ptr, bam_mp_srcptr, bam_mp_size_t, bam_mp_limb_t);
bam_mp_limb_t bam_mpn_submul_1 (bam_mp_ptr, bam_mp_srcptr, bam_mp_size_t, bam_mp_limb_t);

bam_mp_limb_t bam_mpn_mul (bam_mp_ptr, bam_mp_srcptr, bam_mp_size_t, bam_mp_srcptr, bam_mp_size_t);
void bam_mpn_mul_n (bam_mp_ptr, bam_mp_srcptr, bam_mp_srcptr, bam_mp_size_t);
void bam_mpn_sqr (bam_mp_ptr, bam_mp_srcptr, bam_mp_size_t);
int bam_mpn_perfect_square_p (bam_mp_srcptr, bam_mp_size_t);
bam_mp_size_t bam_mpn_sqrtrem (bam_mp_ptr, bam_mp_ptr, bam_mp_srcptr, bam_mp_size_t);

bam_mp_limb_t bam_mpn_lshift (bam_mp_ptr, bam_mp_srcptr, bam_mp_size_t, unsigned int);
bam_mp_limb_t bam_mpn_rshift (bam_mp_ptr, bam_mp_srcptr, bam_mp_size_t, unsigned int);

bam_mp_bitcnt_t bam_mpn_scan0 (bam_mp_srcptr, bam_mp_bitcnt_t);
bam_mp_bitcnt_t bam_mpn_scan1 (bam_mp_srcptr, bam_mp_bitcnt_t);

void bam_mpn_com (bam_mp_ptr, bam_mp_srcptr, bam_mp_size_t);
bam_mp_limb_t bam_mpn_neg (bam_mp_ptr, bam_mp_srcptr, bam_mp_size_t);

bam_mp_bitcnt_t bam_mpn_popcount (bam_mp_srcptr, bam_mp_size_t);

bam_mp_limb_t bam_mpn_invert_3by2 (bam_mp_limb_t, bam_mp_limb_t);
#define bam_mpn_invert_limb(x) bam_mpn_invert_3by2 ((x), 0)

size_t bam_mpn_get_str (unsigned char *, int, bam_mp_ptr, bam_mp_size_t);
bam_mp_size_t bam_mpn_set_str (bam_mp_ptr, const unsigned char *, size_t, int);

void bam_mpz_init (bam_mpz_t);
void bam_mpz_init2 (bam_mpz_t, bam_mp_bitcnt_t);
void bam_mpz_clear (bam_mpz_t);

#define bam_mpz_odd_p(z)   (((z)->_mp_size != 0) & (int) (z)->_mp_d[0])
#define bam_mpz_even_p(z)  (! bam_mpz_odd_p (z))

int bam_mpz_sgn (const bam_mpz_t);
int bam_mpz_cmp_si (const bam_mpz_t, ba0_int_p);
int bam_mpz_cmp_ui (const bam_mpz_t, unsigned ba0_int_p);
int bam_mpz_cmp (const bam_mpz_t, const bam_mpz_t);
int bam_mpz_cmpabs_ui (const bam_mpz_t, unsigned ba0_int_p);
int bam_mpz_cmpabs (const bam_mpz_t, const bam_mpz_t);
int bam_mpz_cmp_d (const bam_mpz_t, double);
int bam_mpz_cmpabs_d (const bam_mpz_t, double);

void bam_mpz_abs (bam_mpz_t, const bam_mpz_t);
void bam_mpz_neg (bam_mpz_t, const bam_mpz_t);
void bam_mpz_swap (bam_mpz_t, bam_mpz_t);

void bam_mpz_add_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
void bam_mpz_add (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
void bam_mpz_sub_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
void bam_mpz_ui_sub (bam_mpz_t, unsigned ba0_int_p, const bam_mpz_t);
void bam_mpz_sub (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);

void bam_mpz_mul_si (bam_mpz_t, const bam_mpz_t, ba0_int_p);
void bam_mpz_mul_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
void bam_mpz_mul (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
void bam_mpz_mul_2exp (bam_mpz_t, const bam_mpz_t, bam_mp_bitcnt_t);
void bam_mpz_addmul_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
void bam_mpz_addmul (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
void bam_mpz_submul_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
void bam_mpz_submul (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);

void bam_mpz_cdiv_qr (bam_mpz_t, bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
void bam_mpz_fdiv_qr (bam_mpz_t, bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
void bam_mpz_tdiv_qr (bam_mpz_t, bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
void bam_mpz_cdiv_q (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
void bam_mpz_fdiv_q (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
void bam_mpz_tdiv_q (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
void bam_mpz_cdiv_r (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
void bam_mpz_fdiv_r (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
void bam_mpz_tdiv_r (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);

void bam_mpz_cdiv_q_2exp (bam_mpz_t, const bam_mpz_t, bam_mp_bitcnt_t);
void bam_mpz_fdiv_q_2exp (bam_mpz_t, const bam_mpz_t, bam_mp_bitcnt_t);
void bam_mpz_tdiv_q_2exp (bam_mpz_t, const bam_mpz_t, bam_mp_bitcnt_t);
void bam_mpz_cdiv_r_2exp (bam_mpz_t, const bam_mpz_t, bam_mp_bitcnt_t);
void bam_mpz_fdiv_r_2exp (bam_mpz_t, const bam_mpz_t, bam_mp_bitcnt_t);
void bam_mpz_tdiv_r_2exp (bam_mpz_t, const bam_mpz_t, bam_mp_bitcnt_t);

void bam_mpz_mod (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);

void bam_mpz_divexact (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);

int bam_mpz_divisible_p (const bam_mpz_t, const bam_mpz_t);
int bam_mpz_congruent_p (const bam_mpz_t, const bam_mpz_t, const bam_mpz_t);

unsigned ba0_int_p bam_mpz_cdiv_qr_ui (bam_mpz_t, bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
unsigned ba0_int_p bam_mpz_fdiv_qr_ui (bam_mpz_t, bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
unsigned ba0_int_p bam_mpz_tdiv_qr_ui (bam_mpz_t, bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
unsigned ba0_int_p bam_mpz_cdiv_q_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
unsigned ba0_int_p bam_mpz_fdiv_q_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
unsigned ba0_int_p bam_mpz_tdiv_q_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
unsigned ba0_int_p bam_mpz_cdiv_r_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
unsigned ba0_int_p bam_mpz_fdiv_r_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
unsigned ba0_int_p bam_mpz_tdiv_r_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
unsigned ba0_int_p bam_mpz_cdiv_ui (const bam_mpz_t, unsigned ba0_int_p);
unsigned ba0_int_p bam_mpz_fdiv_ui (const bam_mpz_t, unsigned ba0_int_p);
unsigned ba0_int_p bam_mpz_tdiv_ui (const bam_mpz_t, unsigned ba0_int_p);

unsigned ba0_int_p bam_mpz_mod_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);

void bam_mpz_divexact_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);

int bam_mpz_divisible_ui_p (const bam_mpz_t, unsigned ba0_int_p);

unsigned ba0_int_p bam_mpz_gcd_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
void bam_mpz_gcd (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
void bam_mpz_gcdext (bam_mpz_t, bam_mpz_t, bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
void bam_mpz_lcm_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
void bam_mpz_lcm (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
int bam_mpz_invert (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);

void bam_mpz_sqrtrem (bam_mpz_t, bam_mpz_t, const bam_mpz_t);
void bam_mpz_sqrt (bam_mpz_t, const bam_mpz_t);
int bam_mpz_perfect_square_p (const bam_mpz_t);

void bam_mpz_pow_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
void bam_mpz_ui_pow_ui (bam_mpz_t, unsigned ba0_int_p, unsigned ba0_int_p);
void bam_mpz_powm (bam_mpz_t, const bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
void bam_mpz_powm_ui (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p, const bam_mpz_t);

void bam_mpz_rootrem (bam_mpz_t, bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);
int bam_mpz_root (bam_mpz_t, const bam_mpz_t, unsigned ba0_int_p);

void bam_mpz_fac_ui (bam_mpz_t, unsigned ba0_int_p);
void bam_mpz_2fac_ui (bam_mpz_t, unsigned ba0_int_p);
void bam_mpz_mfac_uiui (bam_mpz_t, unsigned ba0_int_p, unsigned ba0_int_p);
void bam_mpz_bin_uiui (bam_mpz_t, unsigned ba0_int_p, unsigned ba0_int_p);

int bam_mpz_probab_prime_p (const bam_mpz_t, int);

int bam_mpz_tstbit (const bam_mpz_t, bam_mp_bitcnt_t);
void bam_mpz_setbit (bam_mpz_t, bam_mp_bitcnt_t);
void bam_mpz_clrbit (bam_mpz_t, bam_mp_bitcnt_t);
void bam_mpz_combit (bam_mpz_t, bam_mp_bitcnt_t);

void bam_mpz_com (bam_mpz_t, const bam_mpz_t);
void bam_mpz_and (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
void bam_mpz_ior (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);
void bam_mpz_xor (bam_mpz_t, const bam_mpz_t, const bam_mpz_t);

bam_mp_bitcnt_t bam_mpz_popcount (const bam_mpz_t);
bam_mp_bitcnt_t bam_mpz_hamdist (const bam_mpz_t, const bam_mpz_t);
bam_mp_bitcnt_t bam_mpz_scan0 (const bam_mpz_t, bam_mp_bitcnt_t);
bam_mp_bitcnt_t bam_mpz_scan1 (const bam_mpz_t, bam_mp_bitcnt_t);

int bam_mpz_fits_sba0_int_p_p (const bam_mpz_t);
int bam_mpz_fits_uba0_int_p_p (const bam_mpz_t);
int bam_mpz_fits_sint_p (const bam_mpz_t);
int bam_mpz_fits_uint_p (const bam_mpz_t);
int bam_mpz_fits_sshort_p (const bam_mpz_t);
int bam_mpz_fits_ushort_p (const bam_mpz_t);
ba0_int_p bam_mpz_get_si (const bam_mpz_t);
unsigned ba0_int_p bam_mpz_get_ui (const bam_mpz_t);
double bam_mpz_get_d (const bam_mpz_t);
size_t bam_mpz_size (const bam_mpz_t);
bam_mp_limb_t bam_mpz_getlimbn (const bam_mpz_t, bam_mp_size_t);

void bam_mpz_realloc2 (bam_mpz_t, bam_mp_bitcnt_t);
bam_mp_srcptr bam_mpz_limbs_read (bam_mpz_srcptr);
bam_mp_ptr bam_mpz_limbs_modify (bam_mpz_t, bam_mp_size_t);
bam_mp_ptr bam_mpz_limbs_write (bam_mpz_t, bam_mp_size_t);
void bam_mpz_limbs_finish (bam_mpz_t, bam_mp_size_t);
bam_mpz_srcptr bam_mpz_roinit_n (bam_mpz_t, bam_mp_srcptr, bam_mp_size_t);

#define MPZ_ROINIT_N(xp, xs) {{0, (xs),(xp) }}

void bam_mpz_set_si (bam_mpz_t, signed ba0_int_p);
void bam_mpz_set_ui (bam_mpz_t, unsigned ba0_int_p);
void bam_mpz_set (bam_mpz_t, const bam_mpz_t);
void bam_mpz_set_d (bam_mpz_t, double);

void bam_mpz_init_set_si (bam_mpz_t, signed ba0_int_p);
void bam_mpz_init_set_ui (bam_mpz_t, unsigned ba0_int_p);
void bam_mpz_init_set (bam_mpz_t, const bam_mpz_t);
void bam_mpz_init_set_d (bam_mpz_t, double);

size_t bam_mpz_sizeinbase (const bam_mpz_t, int);
char *bam_mpz_get_str (char *, int, const bam_mpz_t);
int bam_mpz_set_str (bam_mpz_t, const char *, int);
int bam_mpz_init_set_str (bam_mpz_t, const char *, int);

/* This ba0_int_p list taken from gmp.h. */
/* For reference, "defined(EOF)" cannot be used here.  In g++ 2.95.4,
   <iostream> defines EOF but not FILE.  */
#if defined (FILE)                                              \
  || defined (H_STDIO)                                          \
  || defined (_H_STDIO)               /* AIX */                 \
  || defined (_STDIO_H)               /* glibc, Sun, SCO */     \
  || defined (_STDIO_H_)              /* BSD, OSF */            \
  || defined (__STDIO_H)              /* Borland */             \
  || defined (__STDIO_H__)            /* IRIX */                \
  || defined (_STDIO_INCLUDED)        /* HPUX */                \
  || defined (__dj_include_stdio_h_)  /* DJGPP */               \
  || defined (_FILE_DEFINED)          /* Microsoft */           \
  || defined (__STDIO__)              /* Apple MPW MrC */       \
  || defined (_MSL_STDIO_H)           /* Metrowerks */          \
  || defined (_STDIO_H_INCLUDED)      /* QNX4 */        \
  || defined (_ISO_STDIO_ISO_H)       /* Sun C++ */        \
  || defined (__STDIO_LOADED)         /* VMS */            \
  || defined (_STDIO)                 /* HPE NonStop */         \
  || defined (__DEFINED_FILE)         /* musl */
size_t bam_mpz_out_str (FILE *, int, const bam_mpz_t);
#endif

void bam_mpz_import (bam_mpz_t, size_t, int, size_t, int, size_t, const void *);
void *bam_mpz_export (void *, size_t *, int, size_t, int, size_t, const bam_mpz_t);

#if defined (__cplusplus)
}
#endif
#endif /* __MINI_GMP_H__ */
