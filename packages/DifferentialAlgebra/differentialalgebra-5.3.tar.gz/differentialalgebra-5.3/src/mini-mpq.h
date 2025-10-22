/* mini-mpq, a minimalistic implementation of a GNU GMP subset.

Copyright 2018, 2019 Free Software Foundation, Inc.

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

/* Header */

#if !defined (__MINI_MPQ_H__)
#define __MINI_MPQ_H__

#include "mini-gmp.h"

#if defined (__cplusplus)
extern "C" {
#endif

typedef struct
{
  bam__mpz_struct _mp_num;
  bam__mpz_struct _mp_den;
} bam__mpq_struct;

typedef bam__mpq_struct bam_mpq_t[1];

typedef const bam__mpq_struct *bam_mpq_srcptr;
typedef bam__mpq_struct *bam_mpq_ptr;

#define bam_mpq_numref(Q) (&((Q)->_mp_num))
#define bam_mpq_denref(Q) (&((Q)->_mp_den))

void bam_mpq_abs (bam_mpq_t, const bam_mpq_t);
void bam_mpq_add (bam_mpq_t, const bam_mpq_t, const bam_mpq_t);
void bam_mpq_canonicalize (bam_mpq_t);
void bam_mpq_clear (bam_mpq_t);
int bam_mpq_cmp (const bam_mpq_t, const bam_mpq_t);
int bam_mpq_cmp_si (const bam_mpq_t, signed ba0_int_p, unsigned ba0_int_p);
int bam_mpq_cmp_ui (const bam_mpq_t, unsigned ba0_int_p, unsigned ba0_int_p);
int bam_mpq_cmp_z (const bam_mpq_t, const bam_mpz_t);
void bam_mpq_div (bam_mpq_t, const bam_mpq_t, const bam_mpq_t);
void bam_mpq_div_2exp (bam_mpq_t, const bam_mpq_t, bam_mp_bitcnt_t);
int bam_mpq_equal (const bam_mpq_t, const bam_mpq_t);
double bam_mpq_get_d (const bam_mpq_t);
void bam_mpq_get_den (bam_mpz_t, const bam_mpq_t);
void bam_mpq_get_num (bam_mpz_t, const bam_mpq_t);
char * bam_mpq_get_str (char *, int, const bam_mpq_t q);
void bam_mpq_init (bam_mpq_t);
void bam_mpq_inv (bam_mpq_t, const bam_mpq_t);
void bam_mpq_mul (bam_mpq_t, const bam_mpq_t, const bam_mpq_t);
void bam_mpq_mul_2exp (bam_mpq_t, const bam_mpq_t, bam_mp_bitcnt_t);
void bam_mpq_neg (bam_mpq_t, const bam_mpq_t);
void bam_mpq_set (bam_mpq_t, const bam_mpq_t);
void bam_mpq_set_d (bam_mpq_t, double);
void bam_mpq_set_den (bam_mpq_t, const bam_mpz_t);
void bam_mpq_set_num (bam_mpq_t, const bam_mpz_t);
void bam_mpq_set_si (bam_mpq_t, signed ba0_int_p, unsigned ba0_int_p);
int bam_mpq_set_str (bam_mpq_t, const char *, int);
void bam_mpq_set_ui (bam_mpq_t, unsigned ba0_int_p, unsigned ba0_int_p);
void bam_mpq_set_z (bam_mpq_t, const bam_mpz_t);
int bam_mpq_sgn (const bam_mpq_t);
void bam_mpq_sub (bam_mpq_t, const bam_mpq_t, const bam_mpq_t);
void bam_mpq_swap (bam_mpq_t, bam_mpq_t);

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
  || defined (_STDIO_H_INCLUDED)      /* QNX4 */                \
  || defined (_ISO_STDIO_ISO_H)       /* Sun C++ */             \
  || defined (__STDIO_LOADED)         /* VMS */
size_t bam_mpq_out_str (FILE *, int, const bam_mpq_t);
#endif

void bam_mpz_set_q (bam_mpz_t, const bam_mpq_t);

#if defined (__cplusplus)
}
#endif
#endif /* __MINI_MPQ_H__ */
