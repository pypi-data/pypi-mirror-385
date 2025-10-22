/* ba0/src/config.h.  Generated from config-h.in by configure.  */
/* ba0/src/config-h.in.  Generated from configure.ac by autoheader.  */

/* If defined, compile for a 64 bits architecture */
#define BA0_64BITS 1

/* To be defined when generating Apple Universal OSX code */
/* #undef BA0_APPLE_UNIVERSAL_OSX */

/* If defined, force the value of BA0_ALIGN */
/* #undef BA0_FORCE_ALIGN */

/* If defined, use GMP rather than MINI-GMP */
/* #undef BA0_USE_GMP */

/* If defined, use sigsetjmp rather than setjmp */
/* #undef BA0_USE_SIGSETJMP */

/* Define to 1 if you have the <ctype.h> header file. */
#define HAVE_CTYPE_H 1

/* Define to 1 if you have the <dlfcn.h> header file. */
#define HAVE_DLFCN_H 1

/* The GNU SCIENTIFIC LIBRARY If defined, some tests relying on the GSL are
   performed */
/* #undef HAVE_GSL_H */

/* Define to 1 if you have the <ieeefp.h> header file. */
/* #undef HAVE_IEEEFP_H */

/* Define to 1 if you have the <inttypes.h> header file. */
#define HAVE_INTTYPES_H 1

/* Define to 1 if you have the <io.h> header file. */
/* #undef HAVE_IO_H */

/* Define to 1 if you have the <limits.h> header file. */
#define HAVE_LIMITS_H 1

/* Define to 1 if you have the <math.h> header file. */
#define HAVE_MATH_H 1

/* Define to 1 if you have the <setjmp.h> header file. */
#define HAVE_SETJMP_H 1

/* Define to 1 if you have the <stdarg.h> header file. */
#define HAVE_STDARG_H 1

/* Define to 1 if you have the <stdbool.h> header file. */
#define HAVE_STDBOOL_H 1

/* Define to 1 if you have the <stdint.h> header file. */
#define HAVE_STDINT_H 1

/* Define to 1 if you have the <stdio.h> header file. */
#define HAVE_STDIO_H 1

/* Define to 1 if you have the <stdlib.h> header file. */
#define HAVE_STDLIB_H 1

/* Define to 1 if you have the <strings.h> header file. */
#define HAVE_STRINGS_H 1

/* Define to 1 if you have the <string.h> header file. */
#define HAVE_STRING_H 1

/* Define to 1 if you have the <sys/stat.h> header file. */
#define HAVE_SYS_STAT_H 1

/* Define to 1 if you have the <sys/types.h> header file. */
#define HAVE_SYS_TYPES_H 1

/* Define to 1 if you have the <time.h> header file. */
#define HAVE_TIME_H 1

/* Define to 1 if you have the <unistd.h> header file. */
#define HAVE_UNISTD_H 1

/* Define to the sub-directory where libtool stores uninstalled libraries. */
#define LT_OBJDIR ".libs/"

/* Name of package */

/* Define to the address where bug reports for this package should be sent. */
#define BLAD_BUGREPORT ""

/* Define to the full name of this package. */
#define BLAD_NAME "blad"

/* Define to the full name and version of this package. */
#define BLAD_STRING "blad 5.3"

/* Define to the one symbol short name of this package. */
#define BLAD_TARNAME "blad"

/* Define to the home page for this package. */
#define BLAD_URL ""

/* Define to the version of this package. */
#define BLAD_VERSION "5.3"

/* Define to 1 if all of the C89 standard headers exist (not just the ones
   required in a freestanding environment). This macro is provided for
   backward compatibility; new code need not use it. */
#define STDC_HEADERS 1

/* Version number of package */
#if !defined (BA0_COMMON_H)
#   define BA0_COMMON_H 1

/* 
 * The _MSC_VER flag is set if the code is compiled under WINDOWS
 * by using Microsoft Visual C (through Visual Studio 2008).
 *
 * In that case, some specific annotations must be added for DLL exports
 * Beware to the fact that this header file is going to be used either
 * for/while building BLAD or for using BLAD from an outer software.
 *
 * In the first case, functions are exported.
 * In the second one, they are imported.
 *
 * The flag BA0_BLAD_BUILDING must thus be set in the Makefile and passed 
 * to the C preprocessor at BA0 building time. Do not set it when using BA0.
 *
 * When compiling static libraries under Windows, set BA0_STATIC.
 */

#   if defined (_MSC_VER) && ! defined (BA0_STATIC)
#      if defined (BLAD_BUILDING) || defined (BA0_BLAD_BUILDING)
#         	define BA0_DLL	__declspec(dllexport)
#      else
#         define BA0_DLL	__declspec(dllimport)
#      endif
#   else
#      define BA0_DLL
#   endif

/* 
 * The __cplusplus flag is set if the code is compiled by a C++ compiler
 */

#   if defined (__cplusplus) && !defined (BEGIN_C_DECLS)
#      define BEGIN_C_DECLS   extern "C" {
#      define END_C_DECLS     }
#   else
#      define BEGIN_C_DECLS
#      define END_C_DECLS
#   endif

/* 
 * This one we generate
 */

/* #   include "ba0_config.h" */

/* 
 * Windows setting
 */

#   if defined (_MSC_VER)
#      undef  HAVE_DLFCN_H
#      undef  HAVE_INTTYPES_H
#      undef  HAVE_STDINT_H
#      undef  HAVE_STRINGS_H
#      undef  HAVE_SYS_STAT_H
#      undef  HAVE_SYS_TYPES_H
#      undef  HAVE_UNISTD_H

#      undef  BA0_USE_SIGSETJMP

#      define HAVE_IO_H 1
#      define HAVE_FLOAT_H 1

#      undef  HAVE_GSL_H
#      undef  HAVE_MPFR_H
#   endif

#   if HAVE_STDIO_H
#      include <stdio.h>
#   endif

#   if HAVE_STDLIB_H
#      include <stdlib.h>
#   endif

#   if HAVE_UNISTD_H
#      include <unistd.h>
#   endif

#   if HAVE_STDARG_H
#      include <stdarg.h>
#   endif

#   if HAVE_STDBOOL_H
#      include <stdbool.h>
#   else
#      define bool	int
#      define false	0
#      define true	1
#   endif

#   if HAVE_LIMITS_H
#      include <limits.h>
#   endif

#   if HAVE_STRINGS_H
#      include <strings.h>
#   endif

#   if HAVE_STRING_H
#      include <string.h>
#   endif

#   if HAVE_CTYPE_H
#      include <ctype.h>
#   endif

#   if HAVE_TIME_H
#      include <time.h>
#   endif

#   if HAVE_MATH_H
#      include <math.h>
#   endif

#   if HAVE_FLOAT_H
#      include <float.h>
#   endif

#   if HAVE_SETJMP_H
#      include <setjmp.h>
#   endif
#   if BA0_USE_SIGSETJMP
#      define ba0_jmp_buf sigjmp_buf
#      define ba0_setjmp(env,flag) sigsetjmp(env,flag)
#      define ba0_longjmp(env,sig) siglongjmp(env,sig)
#   else
#      define ba0_jmp_buf jmp_buf
#      define ba0_setjmp(env,flag) setjmp(env)
#      define ba0_longjmp(env,sig) longjmp(env,sig)
#   endif

/* 
 * io.h is Windows specific
 */

#   if !defined (HAVE_IO_H)

/*
 * header undefined with -std=c99
 */

extern int fileno (
    FILE *);

#      define ba0_isatty isatty
#      define ba0_fileno fileno
#   else
#      include <io.h>
#      define ba0_isatty _isatty
#      define ba0_fileno _fileno
#   endif

#   if defined (BA0_FORCE_64BITS)
#      undef BA0_64BITS
#      define BA0_64BITS 1
#   else
#      if defined (BA0_FORCE_32BITS)
#         undef BA0_64BITS
#      endif
#   endif

/* 
 * Largest small prime numbers
 */

#   define BA0_MAX_PRIME_32BITS    4294967291
#   define BA0_MAX_PRIME_16BITS    65521

/* 
 * ba0_int_p integer of the size of a pointer 
 * ba0_int_hp of the size of half a pointer (except for APPLE_UNIVERSAL_OSX)
 */

#   if defined (BA0_64BITS)
#      if defined (_MSC_VER)
#         define ba0_int_p long long
#         define ba0_int_hp	int
#         define ba0_mint_hp	unsigned ba0_int_hp
#         define BA0_FORMAT_INT_P	"%lld"
#         define BA0_FORMAT_HEXINT_P	"0x%llx"
#         define BA0_ALIGN	8
#         define BA0_MAX_INT_P	LLONG_MAX
#         define BA0_MAX_INT_HP	INT_MAX
#         define BA0_MAX_MINT_HP	UINT_MAX
#         define BA0_MAX_PRIME_MINT_HP	BA0_MAX_PRIME_32BITS
#      else
#         define ba0_int_p	long int
#         define ba0_int_hp	int
#         define ba0_mint_hp	unsigned ba0_int_hp
#         define BA0_FORMAT_INT_P	"%ld"
#         define BA0_FORMAT_HEXINT_P	"0x%lx"
#         define BA0_ALIGN	8
#         define BA0_MAX_INT_P	LONG_MAX
#         define BA0_MAX_INT_HP	INT_MAX
#         define BA0_MAX_MINT_HP	UINT_MAX
#         define BA0_MAX_PRIME_MINT_HP	BA0_MAX_PRIME_32BITS
#      endif
#   else
#      define ba0_int_p	int
#      define ba0_int_hp	short int
#      define ba0_mint_hp	unsigned ba0_int_hp
#      define BA0_FORMAT_INT_P        "%d"
#      define BA0_FORMAT_HEXINT_P	"0x%x"
#      define BA0_ALIGN	4
#      define BA0_MAX_INT_P	INT_MAX
#      define BA0_MAX_INT_HP	SHRT_MAX
#      define BA0_MAX_MINT_HP	USHRT_MAX
#      define BA0_MAX_PRIME_MINT_HP	BA0_MAX_PRIME_16BITS
#   endif

/* 
 * On 32 bits Solaris, 64 bits alignment is mandatory for double 
 * BA0_FORCE_ALIGN=8 is used in that case.
 */

#   if defined (BA0_FORCE_ALIGN)
#      undef BA0_ALIGN
#      define BA0_ALIGN BA0_FORCE_ALIGN
#   endif

#   define BA0_BUFSIZE	256

#   define BA0_NBBITS_INT_P	(CHAR_BIT * sizeof(ba0_int_p))
#   define BA0_NBBITS_INT_HP	(CHAR_BIT * sizeof(ba0_int_hp))

#   define BA0_ABS(z) ((z) >= 0 ? (z) : - (z))
#   define BA0_MAX(x,y) ((x) >= (y) ? (x) : (y))
#   define BA0_MIN(x,y) ((x) >= (y) ? (y) : (x))
#   define BA0_SWAP(type,x,y) do { type _bunk_ = x; x = y; y = _bunk_; } while (0)

#   define BA0_NOT_AN_INDEX -1

/* 
 * Type declarations
 */

BEGIN_C_DECLS

enum ba0_compare_code
{
  ba0_lt,
  ba0_eq,
  ba0_equiv,
  ba0_gt
};

enum ba0_sort_mode
{
  ba0_descending_mode,
  ba0_ascending_mode
};

/*
 * texinfo: ba0_garbage_code
 * This data type is passed as an argument to @code{ba0_garbage1_function}
 * and @code{ba0_garbage2_function} functions when applying the garbage
 * collector to a data structure. 
 */

enum ba0_garbage_code
{
// the data structure stands alone
  ba0_isolated,
// the data structure is a field of a bigger data structure
  ba0_embedded
};

enum ba0_restart_level
{
  ba0_init_level = 1,
  ba0_reset_level,
  ba0_done_level
};

enum ba0_wang_code
{
  ba0_rational_found,
  ba0_rational_not_found,
  ba0_zero_divisor
};

typedef void *ba0_scanf_function (
    void *);

typedef void ba0_printf_function (
    void *);

typedef ba0_int_p ba0_garbage1_function (
    void *,
    enum ba0_garbage_code);

typedef void *ba0_garbage2_function (
    void *,
    enum ba0_garbage_code);

typedef void *ba0_copy_function (
    void *);

typedef void *ba0_unary_function (
    void *);

typedef bool ba0_cmp_function (
    void *,
    void *);

typedef bool ba0_cmp2_function (
    void *,
    void *,
    void *);

typedef bool ba0_unary_predicate (
    void *);

typedef void *ba0_new_function (
    void);

typedef void ba0_set_function (
    void *,
    void *);

typedef void ba0_init_function (
    void *);

typedef void ba0_unary_operation (
    void *);

typedef void ba0_binary_operation (
    void *,
    void *);

typedef void ba0_ternary_operation (
    void *,
    void *,
    void *);

extern BA0_DLL void ba0_reset_all_settings (
    void);

extern BA0_DLL void ba0_set_settings_interrupt (
    void (*)(void),
    time_t);

extern BA0_DLL void ba0_set_settings_common (
    enum ba0_restart_level);

extern BA0_DLL void ba0_get_settings_interrupt (
    void (**)(void),
    time_t *);

extern BA0_DLL void ba0_set_settings_no_oot (
    bool);

extern BA0_DLL void ba0_get_settings_no_oot (
    bool *);

extern BA0_DLL void ba0_get_settings_common (
    enum ba0_restart_level *);

struct ba0_PFE_settings;

extern BA0_DLL void ba0_cancel_PFE_settings (
    struct ba0_PFE_settings *);

extern BA0_DLL void ba0_restore_PFE_settings (
    struct ba0_PFE_settings *);

extern BA0_DLL void ba0_process_check_interrupt (
    void);

extern BA0_DLL char *ba0_get_version (
    void);

extern BA0_DLL void ba0_restart (
    ba0_int_p,
    ba0_int_p);

extern BA0_DLL void ba0_terminate (
    enum ba0_restart_level);

END_C_DECLS
#endif /* !BA0_COMMON_H */
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
/* #include "ba0_common.h" */

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

/* #include "mini-gmp.h" */

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
#if ! defined (BA0_MESGERR_H)
#   define BA0_MESGERR_H

/* #   include "ba0_common.h" */

BEGIN_C_DECLS
/* 
 * A bug is discovered in the library (should not happen error).
 *  Repair: fix the bug.
 */
extern BA0_DLL char BA0_ERRALG[];

extern BA0_DLL char BA0_ERRNYP[];

extern BA0_DLL char BA0_ERRNCE[];

/* 
 * Memory problems.
 * Repair: reconfigure the library (resize some constants).
 */

extern BA0_DLL char BA0_ERROOM[];

extern BA0_DLL char BA0_ERRSOV[];

extern BA0_DLL char BA0_ERRMFR[];

/* 
 * Giving up computations because of a signal.
 */

extern BA0_DLL char BA0_ERRSIG[];

extern BA0_DLL char BA0_ERRALR[];

extern BA0_DLL char BA0_ERRNCI[];

/* 
 * Mathematical errors
 */

extern BA0_DLL char BA0_ERRIVZ[];

extern BA0_DLL char BA0_ERRDDZ[];

extern BA0_DLL char BA0_EXWRNT[];

extern BA0_DLL char BA0_EXWDDZ[];

extern BA0_DLL char BA0_ERRMAT[];

extern BA0_DLL char BA0_ERRNIL[];

extern BA0_DLL char BA0_ERRZCI[];

/* 
 * Parser errors
 */

extern BA0_DLL char BA0_ERREOF[];

extern BA0_DLL char BA0_ERRSYN[];

extern BA0_DLL char BA0_ERRSTR[];

extern BA0_DLL char BA0_ERRINT[];

extern BA0_DLL char BA0_ERRBOOL[];

extern BA0_DLL char BA0_ERRFLT[];

extern BA0_DLL char BA0_ERRRAT[];

extern BA0_DLL char BA0_ERRAMB[];

/*
 * Other errors
 */

extern BA0_DLL char BA0_ERRKEY[];

END_C_DECLS
#endif /* !BA0_MESGERR_H */
#if !defined (BA0_TABLE_H)
#   define BA0_TABLE_H 1

/* #   include "ba0_common.h" */

BEGIN_C_DECLS

struct ba0_table
{
  ba0_int_p alloc;
  ba0_int_p size;
  void **tab;
};

struct ba0_tableof_table
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_table **tab;
};

extern BA0_DLL unsigned ba0_int_p ba0_sizeof_table (
    struct ba0_table *,
    enum ba0_garbage_code);

extern BA0_DLL void ba0_re_malloc_table (
    struct ba0_table *,
    ba0_int_p);

extern BA0_DLL void ba0_realloc_table (
    struct ba0_table *,
    ba0_int_p);

extern BA0_DLL void ba0_realloc2_table (
    struct ba0_table *,
    ba0_int_p,
    ba0_new_function *);

extern BA0_DLL void ba0_init_table (
    struct ba0_table *);

extern BA0_DLL void ba0_reset_table (
    struct ba0_table *);

extern BA0_DLL struct ba0_table *ba0_new_table (
    void);

extern BA0_DLL void ba0_set_table (
    struct ba0_table *,
    struct ba0_table *);

extern BA0_DLL void ba0_set2_table (
    struct ba0_table *,
    struct ba0_table *,
    ba0_new_function *,
    ba0_set_function *);

extern BA0_DLL void ba0_delete_table (
    struct ba0_table *,
    ba0_int_p);

extern BA0_DLL void ba0_insert_table (
    struct ba0_table *,
    ba0_int_p,
    void *);

extern BA0_DLL bool ba0_member_table (
    void *,
    struct ba0_table *);

extern BA0_DLL bool ba0_member2_table (
    void *,
    struct ba0_table *,
    ba0_int_p *);

extern BA0_DLL bool ba0_equal_table (
    struct ba0_table *,
    struct ba0_table *);

extern BA0_DLL void ba0_sort_table (
    struct ba0_table *,
    struct ba0_table *);

extern BA0_DLL void ba0_unique_table (
    struct ba0_table *,
    struct ba0_table *);

extern BA0_DLL bool ba0_is_unique_table (
    struct ba0_table *);

extern BA0_DLL void ba0_reverse_table (
    struct ba0_table *,
    struct ba0_table *);

extern BA0_DLL void ba0_concat_table (
    struct ba0_table *,
    struct ba0_table *,
    struct ba0_table *);

extern BA0_DLL void ba0_move_to_tail_table (
    struct ba0_table *,
    struct ba0_table *,
    ba0_int_p);

extern BA0_DLL void ba0_move_from_tail_table (
    struct ba0_table *,
    struct ba0_table *,
    ba0_int_p);

struct ba0_list;

extern BA0_DLL void ba0_append_table_list (
    struct ba0_table *,
    struct ba0_list *);

extern BA0_DLL void ba0_set_table_list (
    struct ba0_table *,
    struct ba0_list *);

END_C_DECLS
#endif /* ! BA0_TABLE_H */
#if !defined (BA0_ARRAY_H)
#   define BA0_ARRAY_H 1

/* #   include "ba0_common.h" */

BEGIN_C_DECLS

struct ba0_array
{
  ba0_int_p alloc;
  ba0_int_p size;
  char *tab;
  ba0_int_p sizelt;
};


#   define BA0_ARRAY(A,i) ((A)->tab + (i)*  (A)->sizelt)

extern BA0_DLL void ba0_realloc_array (
    struct ba0_array *,
    ba0_int_p,
    ba0_int_p);

extern BA0_DLL void ba0_realloc2_array (
    struct ba0_array *,
    ba0_int_p,
    ba0_int_p,
    ba0_init_function *);

extern BA0_DLL void ba0_init_array (
    struct ba0_array *);

extern BA0_DLL void ba0_reset_array (
    struct ba0_array *);

extern BA0_DLL struct ba0_array *ba0_new_array (
    void);

extern BA0_DLL void ba0_set_array (
    struct ba0_array *,
    struct ba0_array *);

extern BA0_DLL void ba0_delete_array (
    struct ba0_array *,
    ba0_int_p);

extern BA0_DLL void ba0_reverse_array (
    struct ba0_array *,
    struct ba0_array *);

extern BA0_DLL void ba0_concat_array (
    struct ba0_array *,
    struct ba0_array *,
    struct ba0_array *);

END_C_DECLS
#endif /* ! BA0_ARRAY_H */
#if !defined (BA0_LIST_H)
#   define BA0_LIST_H

/* #   include "ba0_common.h" */

BEGIN_C_DECLS

struct ba0_list
{
  void *value;
  struct ba0_list *next;
};


extern BA0_DLL struct ba0_list *ba0_sort_list (
    struct ba0_list *,
    ba0_cmp_function *);

extern BA0_DLL struct ba0_list *ba0_sort2_list (
    struct ba0_list *,
    ba0_cmp2_function *,
    void *);

extern BA0_DLL struct ba0_list *ba0_select_list (
    struct ba0_list *,
    ba0_unary_predicate *);

extern BA0_DLL struct ba0_list *ba0_delete_list (
    struct ba0_list *,
    ba0_unary_predicate *);

extern BA0_DLL struct ba0_list *ba0_insert_list (
    void *,
    struct ba0_list *,
    ba0_cmp_function *);

extern BA0_DLL struct ba0_list *ba0_insert2_list (
    void *,
    struct ba0_list *,
    ba0_cmp2_function *,
    void *);

extern BA0_DLL bool ba0_member_list (
    void *,
    struct ba0_list *);

extern BA0_DLL void *ba0_last_list (
    struct ba0_list *);

extern BA0_DLL struct ba0_list *ba0_butlast_list (
    struct ba0_list *);

extern BA0_DLL struct ba0_list *ba0_copy_list (
    struct ba0_list *);

extern BA0_DLL struct ba0_list *ba0_cons_list (
    void *,
    struct ba0_list *);

extern BA0_DLL struct ba0_list *ba0_endcons_list (
    void *,
    struct ba0_list *);

extern BA0_DLL struct ba0_list *ba0_reverse_list (
    struct ba0_list *);

extern BA0_DLL struct ba0_list *ba0_concat_list (
    struct ba0_list *,
    struct ba0_list *);

extern BA0_DLL void ba0_move_to_head_list (
    struct ba0_list *,
    ba0_int_p);

extern BA0_DLL ba0_int_p ba0_length_list (
    struct ba0_list *);

extern BA0_DLL void *ba0_ith_list (
    struct ba0_list *,
    ba0_int_p);

extern BA0_DLL struct ba0_list *ba0_map_list (
    ba0_unary_function *,
    struct ba0_list *);

END_C_DECLS
#endif /* !BA0_LIST_H */
#if !defined (BA0_MATRIX_H)
#   define BA0_MATRIX_H 1

/* #   include "ba0_common.h" */

BEGIN_C_DECLS

struct ba0_matrix
{
  ba0_int_p alloc;
  ba0_int_p nrow;
  ba0_int_p ncol;
  void **entry;
};


#   define BA0_MAT(M,i,j) (M)->entry [(M)->ncol*  (i) + j]

extern BA0_DLL void ba0_realloc_matrix (
    struct ba0_matrix *,
    ba0_int_p,
    ba0_int_p);

extern BA0_DLL void ba0_realloc2_matrix (
    struct ba0_matrix *,
    ba0_int_p,
    ba0_int_p,
    ba0_new_function *);

extern BA0_DLL void ba0_init_matrix (
    struct ba0_matrix *);

extern BA0_DLL void ba0_reset_matrix (
    struct ba0_matrix *);

extern BA0_DLL struct ba0_matrix *ba0_new_matrix (
    void);

extern BA0_DLL void ba0_set_matrix_unity (
    struct ba0_matrix *,
    ba0_int_p,
    ba0_new_function *,
    ba0_unary_operation *,
    ba0_unary_operation *);

extern BA0_DLL void ba0_set_matrix (
    struct ba0_matrix *,
    struct ba0_matrix *);

extern BA0_DLL void ba0_set_matrix2 (
    struct ba0_matrix *,
    struct ba0_matrix *,
    ba0_new_function *,
    ba0_binary_operation *);

extern BA0_DLL void ba0_set_matrix_unity (
    struct ba0_matrix *,
    ba0_int_p,
    ba0_new_function *,
    ba0_unary_operation *,
    ba0_unary_operation *);

extern BA0_DLL bool ba0_is_zero_matrix (
    struct ba0_matrix *,
    ba0_unary_predicate *);

extern BA0_DLL bool ba0_is_unity_matrix (
    struct ba0_matrix *,
    ba0_unary_predicate *,
    ba0_unary_predicate *);

extern BA0_DLL void ba0_swap_rows_matrix (
    struct ba0_matrix *,
    ba0_int_p,
    ba0_int_p);

extern BA0_DLL void ba0_swap_columns_matrix (
    struct ba0_matrix *,
    ba0_int_p,
    ba0_int_p);

extern BA0_DLL void ba0_add_matrix (
    struct ba0_matrix *,
    struct ba0_matrix *,
    struct ba0_matrix *,
    ba0_new_function *,
    ba0_ternary_operation *);

extern BA0_DLL void ba0_mul_matrix (
    struct ba0_matrix *,
    struct ba0_matrix *,
    struct ba0_matrix *,
    ba0_new_function *,
    ba0_unary_operation *,
    ba0_binary_operation *,
    ba0_ternary_operation *,
    ba0_ternary_operation *);

END_C_DECLS
#endif /* !BA0_MATRIX_H */
#if ! defined (BA0_POINT_H)
#   define BA0_POINT_H 1

/* #   include "ba0_common.h" */

BEGIN_C_DECLS

/*
 * texinfo: ba0_value
 * This data type permits to associate a value to a variable
 * (variables are defined in the @code{bav} library).
 *
 * It can be parsed and printed using formats of the form
 * @code{%value(%something)}. The input output syntax for values
 * is @code{var = value}. The equality sign can be customized
 * (see @code{ba0_set_settings_value}).
 */

struct ba0_value
{
  void *var;
  void *value;
};

#   define BA0_NOT_A_VALUE (struct ba0_value *)0

#   define BA0_NOT_A_VARIABLE 0

#   define BA0_POINT_OPER "="

/*
 * texinfo: ba0_point
 * This data type permits to associate values to many different variables.
 * It actually is a duplicate of @code{struct ba0_table} so that many
 * table functions may be applied to points.
 * Many functions require the @code{tab} field to be
 * sorted (see @code{ba0_sort_point}).
 *
 * It can be parsed and printed using formats of the form 
 * @code{%point(%something)} which is more precise than
 * @code{%t(%value(%something))} since parsed points are sorted
 * and tested against ambiguity (exception @code{BA0_ERRAMB} is
 * raised by the parser if the variables are not pairwise distinct).
 *
 * This data type gets specialized as @code{struct bav_point_int_p}
 * and @code{struct bav_point_interval_mpq} in the @code{bav} library
 * and as @code{baz_point_ratfrac} in the @code{baz} library.
 */

struct ba0_point
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_value **tab;
};


extern BA0_DLL void ba0_set_settings_value (
    char *);

extern BA0_DLL void ba0_get_settings_value (
    char **);

extern BA0_DLL void ba0_init_value (
    struct ba0_value *);

extern BA0_DLL struct ba0_value *ba0_new_value (
    void);

extern BA0_DLL void ba0_init_point (
    struct ba0_point *);

extern BA0_DLL struct ba0_point *ba0_new_point (
    void);

extern BA0_DLL void ba0_set_point (
    struct ba0_point *,
    struct ba0_point *);

extern BA0_DLL void ba0_sort_point (
    struct ba0_point *,
    struct ba0_point *);

extern BA0_DLL bool ba0_is_sorted_point (
    struct ba0_point *);

extern BA0_DLL bool ba0_is_ambiguous_point (
    struct ba0_point *);

extern BA0_DLL void ba0_delete_point (
    struct ba0_point *,
    struct ba0_point *,
    ba0_int_p);

extern BA0_DLL struct ba0_value *ba0_bsearch_point (
    void *,
    struct ba0_point *,
    ba0_int_p *);

extern BA0_DLL struct ba0_value *ba0_assoc_point (
    void *,
    struct ba0_point *,
    ba0_int_p *);

END_C_DECLS
#endif /* !BA0_POINT_H */
#if !defined (BA0_INT_P)
#   define BA0_INT_P 1

/* #   include "ba0_common.h" */

BEGIN_C_DECLS

struct ba0_tableof_int_p
{
  ba0_int_p alloc;
  ba0_int_p size;
  ba0_int_p *tab;
};

struct ba0_tableof_unsigned_int_p
{
  ba0_int_p alloc;
  ba0_int_p size;
  unsigned ba0_int_p *tab;
};

struct ba0_matrixof_int_p
{
  ba0_int_p alloc;
  ba0_int_p nrow;
  ba0_int_p ncol;
  ba0_int_p *entry;
};

struct ba0_listof_int_p
{
  ba0_int_p value;
  struct ba0_listof_int_p *next;
};

struct ba0_tableof_tableof_int_p
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_tableof_int_p **tab;
};

extern BA0_DLL ba0_int_p ba0_log2_int_p (
    ba0_int_p);

extern BA0_DLL ba0_scanf_function ba0_scanf_int_p;

extern BA0_DLL ba0_printf_function ba0_printf_int_p;

extern BA0_DLL ba0_scanf_function ba0_scanf_hexint_p;

extern BA0_DLL ba0_printf_function ba0_printf_hexint_p;

END_C_DECLS
#endif /* !BA0_INT_P */
#if !defined (BA0_BOOL)
#   define BA0_BOOL 1

/* #   include "ba0_common.h" */

BEGIN_C_DECLS

#   define ba0_bool ba0_int_p

struct ba0_tableof_bool
{
  ba0_int_p alloc;
  ba0_int_p size;
  ba0_bool *tab;
};

struct ba0_tableof_tableof_bool
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_tableof_bool **tab;
};

extern BA0_DLL ba0_scanf_function ba0_scanf_bool;

extern BA0_DLL ba0_printf_function ba0_printf_bool;

END_C_DECLS
#endif /* !BA0_BOOL */
#if !defined (BA0_STACK_H)
#   define BA0_STACK_H

/* #   include "ba0_common.h" */
/* #   include "ba0_table.h" */
/* #   include "ba0_int_p.h" */

BEGIN_C_DECLS

/*
 * texinfo: ba0_mark
 * The data structure @code{ba0_mark} implements marks.
 * From the user point of view, a @dfn{mark} is a pointer in a stack.
 * Marks are used for garbage collection.
 */

struct ba0_mark
{
// the stack the address belongs to
  struct ba0_stack *stack;      // the stack the address belongs to 
// the index of the stack cell the address belongs to
  ba0_int_p index_in_cells;
  void *address;                // the address
// the number of free bytes in the cell, after the mark
  unsigned ba0_int_p memory_left;
};

/* texinfo: ba0_stack
 * The data structure @code{ba0_stack} mplements stacks.
 * From the user point of view, a stack is a huge piece of memory in
 * which memory allocation is possible.
 * A stack is implemented as an array of cells.
 * Cells are blocks of memory allocated in the process heap via
 * @code{ba0_alloc}.
 */

struct ba0_stack
{
// the identifier (nickname) of the stack
  char *ident;
// the array of cells and the corresponding array of cell sizes
  struct ba0_table cells;
  struct ba0_tableof_unsigned_int_p sizes;
// the default size of cells (may increase during computations)
  unsigned ba0_int_p default_size;
// default value is true (if false, cell sizes do not increase)
  bool resizable;
// the border between the used and the free parts of the stack
  struct ba0_mark free;
// the max address reached by the free pointer
  struct ba0_mark max_alloc;
// counts the number of allocations in the process heap
  ba0_int_p nb_calls_to_alloc;
// for debugging purposes
  ba0_int_p *bound;
};

struct ba0_tableof_stack
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_stack **tab;
};


/* 
 * Some default values
 */

#   define BA0_SIZE_CELL_MAIN_STACK   0x20000
#   define BA0_SIZE_CELL_QUIET_STACK  0x20000
#   define BA0_SIZE_CELL_ANALEX_STACK 0x10000
#   define BA0_NB_CELLS_PER_STACK       0x100
#   define BA0_SIZE_STACK_OF_STACK      0x100

extern BA0_DLL void ba0_set_settings_no_oom (
    bool);

extern BA0_DLL void ba0_get_settings_no_oom (
    bool *);

extern BA0_DLL void ba0_set_settings_stack (
    ba0_int_p,
    ba0_int_p,
    ba0_int_p,
    ba0_int_p,
    ba0_int_p);

extern BA0_DLL void ba0_get_settings_stack (
    ba0_int_p *,
    ba0_int_p *,
    ba0_int_p *,
    ba0_int_p *,
    ba0_int_p *);

extern BA0_DLL void ba0_init_stack_of_stacks (
    void);

extern BA0_DLL void ba0_reset_stack_of_stacks (
    void);

extern BA0_DLL void ba0_clear_stack_of_stacks (
    void);

#   define ba0_alloc_counter	ba0_global.stack.alloc_counter
#   define ba0_malloc_counter	ba0_global.stack.malloc_counter
#   define ba0_malloc_nbcalls	ba0_global.stack.malloc_nbcalls

extern BA0_DLL void ba0_set_settings_memory_functions (
    void *(*)(size_t),
    void (*)(void *));

extern BA0_DLL void ba0_get_settings_memory_functions (
    void *(**)(size_t),
    void (**)(void *));

extern BA0_DLL unsigned ba0_int_p ba0_ceil_align (
    unsigned ba0_int_p);

extern BA0_DLL unsigned ba0_int_p ba0_allocated_size (
    unsigned ba0_int_p);

extern BA0_DLL void *ba0_malloc (
    ba0_int_p);

extern BA0_DLL void *ba0_persistent_malloc (
    ba0_int_p);

extern BA0_DLL void ba0_free (
    void *);

extern BA0_DLL ba0_int_p ba0_cell_index_mark (
    void *,
    struct ba0_mark *);

extern BA0_DLL bool ba0_in_stack (
    void *,
    struct ba0_stack *);

extern BA0_DLL struct ba0_stack *ba0_which_stack (
    void *);

extern BA0_DLL struct ba0_stack *ba0_current_stack (
    void);

extern BA0_DLL unsigned ba0_int_p ba0_max_alloc_stack (
    struct ba0_stack *);

extern BA0_DLL void ba0_push_stack (
    struct ba0_stack *);

extern BA0_DLL void ba0_pull_stack (
    void);

extern BA0_DLL void ba0_push_another_stack (
    void);

extern BA0_DLL void ba0_init_stack (
    struct ba0_stack *);

extern BA0_DLL void ba0_init_one_cell_stack (
    struct ba0_stack *,
    char *,
    void *,
    ba0_int_p);

extern BA0_DLL void ba0_reset_stack (
    struct ba0_stack *);

extern BA0_DLL void ba0_reset_cell_stack (
    struct ba0_stack *);

extern BA0_DLL void ba0_clear_cells_stack (
    struct ba0_stack *);

extern BA0_DLL void ba0_clear_one_cell_stack (
    struct ba0_stack *);

extern BA0_DLL void ba0_clear_stack (
    struct ba0_stack *);

extern BA0_DLL void *ba0_alloc_but_do_not_set_magic (
    unsigned ba0_int_p);

extern BA0_DLL void ba0_alloc_set_magic (
    void);

extern BA0_DLL void *ba0_alloc (
    unsigned ba0_int_p);

extern BA0_DLL unsigned ba0_int_p ba0_memory_left_in_cell (
    void);

extern BA0_DLL void ba0_t1_alloc (
    unsigned ba0_int_p,
    unsigned ba0_int_p,
    void **,
    unsigned ba0_int_p *);

extern BA0_DLL void ba0_t2_alloc (
    unsigned ba0_int_p,
    unsigned ba0_int_p,
    unsigned ba0_int_p,
    void **,
    void **,
    unsigned ba0_int_p *);

extern BA0_DLL void ba0_rotate_cells (
    ba0_int_p);

extern BA0_DLL void *ba0_alloc_mark (
    struct ba0_mark *,
    unsigned ba0_int_p);

extern BA0_DLL void ba0_record (
    struct ba0_mark *);

extern BA0_DLL void ba0_restore (
    struct ba0_mark *);

extern BA0_DLL unsigned ba0_int_p ba0_range_mark (
    struct ba0_mark *,
    struct ba0_mark *);

END_C_DECLS
#endif /* !BA0_STACK_H */
#if !defined (BA0_EXCEPTION_H)
#   define BA0_EXCEPTION_H

/* #   include "ba0_common.h" */
/* #   include "ba0_stack.h" */
/* #   include "ba0_analex.h" */
/* #   include "ba0_mesgerr.h" */

BEGIN_C_DECLS

/*
 * Depending on the architecture, the implementation differs.
 * It is simpler to bundle jmpbuf in a struct
 */

struct ba0_jmp_buf_struct
{
  ba0_jmp_buf data;
};

/* 
 * Used by ba0_global.exception
 * The size of the exception stack.
 * The size of the exception log fifo.
 * The size of the extra stack is used also in ba0_exception_code
 */

#   define BA0_SIZE_EXCEPTION_STACK	100
#   define BA0_SIZE_EXCEPTION_LOG	10
#   define	BA0_SIZE_EXCEPTION_EXTRA_STACK 10

/* 
 * texinfo: ba0_exception
 * This data type implements the data stored in the entries of
 * @code{ba0_global.exception.stack}. These entries are filled when an
 * exception catching point is set. They are used for restoring
 * values when an exception is caught.
 */

struct ba0_exception
{
  struct ba0_jmp_buf_struct jmp_b;      // for setjmp/longjmp
// a pointer to the local variable __code__ set by BA0_TRY
  struct ba0_exception_code *code;
};

/* 
 * texinfo: ba0_exception_code
 * The data type for local variables @code{__code__} set by @code{BA0_TRY}.
 */

struct ba0_exception_code
{
// a copy of ba0_global.exception.stack.size for debugging purpose
  ba0_int_p exception_stack_size;
  bool cancelled;               // set to true by BA0_ENDTRY
  int jmp_code;                 // the returned value of setjmp
// values recorded when an exception catching point is set
  struct ba0_mark main;         // the free pointer of the main stack
  struct ba0_mark second;       // the one of the second stack
  ba0_int_p stack_of_stacks_size;       // the field size of the stack of stacks
// values of extra variables to be saved/restored
// the pointers to the variables are in ba0_global.exception.extra_stack
  struct
  {
    ba0_int_p tab[BA0_SIZE_EXCEPTION_EXTRA_STACK];
    ba0_int_p size;
  } extra_stack;
};

/* 
 * The macros for throwing exceptions
 */

#   define BA0_RAISE_EXCEPTION(msg) ba0_raise_exception (__FILE__, __LINE__, msg)

#   define BA0_RE_RAISE_EXCEPTION ba0_raise_exception (__FILE__, __LINE__, ba0_global.exception.raised)

#   define BA0_RAISE_PARSER_EXCEPTION(msg) do { \
    ba0_write_context_analex ();	      \
    ba0_raise_exception (__FILE__, __LINE__, msg); \
    } while (0)

#   define BA0_RAISE_EXCEPTION2(msg,f,o) \
	ba0_raise_exception2 (__FILE__, __LINE__, msg, f, (void **) o)

#   define BA0_CERR(msg) ba0_cerr (__FILE__, __LINE__, msg)

#   define BA0_ASSERT(condition) do { \
      if (!(condition)) BA0_RAISE_EXCEPTION (BA0_ERRALG) ; \
    } while (0)

/*
 * The macros for catching exceptions
 */

#   define BA0_TRY \
    { \
      struct ba0_exception_code __code__; \
      ba0_push_exception (&__code__);			\
      __code__.jmp_code = ba0_setjmp (ba0_global.exception.stack.tab [ba0_global.exception.stack.size-1].jmp_b.data,1);\
      if (ba0_exception_is_set (&__code__))

#   define BA0_CANCEL_EXCEPTION \
      ba0_pull_exception (&__code__);

#   define BA0_CATCH else

#   define BA0_ENDTRY \
      ba0_pull_exception (&__code__); \
    }

extern BA0_DLL void ba0_reset_exception_extra_stack (
    void);

extern BA0_DLL void ba0_push_exception_extra_stack (
    ba0_int_p *,
    void (*)(ba0_int_p));

extern BA0_DLL void ba0_pull_exception_extra_stack (
    void);

extern BA0_DLL void ba0_reset_exception (
    void);

extern BA0_DLL void ba0_push_exception (
    struct ba0_exception_code *);

extern BA0_DLL void ba0_pull_exception (
    struct ba0_exception_code *);

extern BA0_DLL bool ba0_exception_is_raised (
    struct ba0_exception_code *);

extern BA0_DLL bool ba0_exception_is_set (
    struct ba0_exception_code *);

extern BA0_DLL void ba0_raise_exception (
    char *,
    int,
    char *);

extern BA0_DLL void ba0_raise_exception2 (
    char *,
    int,
    char *,
    char *,
    void **);

extern BA0_DLL void ba0_cerr (
    char *,
    int,
    char *);

END_C_DECLS
#endif /* !BA0_EXCEPTION_H */
#if !defined (BA0_MACROS_MINT_HP_H)
#   define BA0_MACROS_MINT_HP_H 1

/* #   include "ba0_common.h" */

/* Macros for ba0_mint_hp */

#   define ba0_mint_hp_t ba0_mint_hp
#   define ba0_mint_hp_init(rop)            rop = 0
#   define ba0_mint_hp_set(rop,op)          rop = op
#   define ba0_mint_hp_affect(rop,op)       rop = op
#   define ba0_mint_hp_swap(opa,opb)        BA0_SWAP (ba0_mint_hp, opa, opb)

#   define ba0_mint_hp_set_si(rop,op)                    \
    rop = op > 0 ? op % ba0_mint_hp_module :             \
            (op + ba0_mint_hp_module) % ba0_mint_hp_module    \

#   define ba0_mint_hp_set_ui(rop,op)       rop = op % ba0_mint_hp_module

#   define ba0_mint_hp_init_set(rop,op)     rop = op

#   define ba0_mint_hp_init_set_si(rop,op)               \
    rop = op > 0 ? op % ba0_mint_hp_module :             \
            (op + ba0_mint_hp_module) % ba0_mint_hp_module

#   define ba0_mint_hp_init_set_ui(rop,op) rop = op % ba0_mint_hp_module

#   define ba0_mint_hp_is_zero(op)          ((op) == 0)
#   define ba0_mint_hp_is_one(op)           ((op) == 1)

#   define ba0_mint_hp_is_negative(op)      ((op) < 0)
#   define ba0_mint_hp_are_equal(opa,opb)   ((opa) == (opb))

#   define ba0_mint_hp_neg(rop,op)          rop = ba0_mint_hp_module - op

#   define ba0_mint_hp_add(rop,opa,opb)                  \
    rop = (ba0_mint_hp)(((unsigned ba0_int_p)(opa) +     \
                (unsigned ba0_int_p)(opb))               \
                % (unsigned ba0_int_p)ba0_mint_hp_module)

#   define ba0_mint_hp_sub(rop,opa,opb)                  \
    rop = (ba0_mint_hp)(((unsigned ba0_int_p)ba0_mint_hp_module + \
                (unsigned ba0_int_p)(opa) -              \
                (unsigned ba0_int_p)(opb))               \
                % (unsigned ba0_int_p)ba0_mint_hp_module)

#   define ba0_mint_hp_mul(rop,opa,opb)                  \
    rop = (ba0_mint_hp)(((unsigned ba0_int_p)(opa)*      \
                (unsigned ba0_int_p)(opb))               \
                % (unsigned ba0_int_p)ba0_mint_hp_module)

#   define ba0_mint_hp_mul_ui(rop,opa,opb)               \
    rop = (ba0_mint_hp)(((unsigned ba0_int_p)(opa)*      \
                (unsigned ba0_int_p)(opb))               \
                % (unsigned ba0_int_p)ba0_mint_hp_module)

#   define ba0_mint_hp_mul_si(rop,opa,opb)               \
    rop = (ba0_mint_hp)(((ba0_int_p)(opa)*((opb) > 0 ? (opb) : \
            ba0_mint_hp_module - (opb)))                 \
            % (unsigned ba0_int_p)ba0_mint_hp_module)

#   define ba0_mint_hp_pow_ui(rop,opa,opb)    rop = ba0_pow_mint_hp(opa,opb)

#   define ba0_mint_hp_div(rop,opa,opb)                  \
    rop = (ba0_mint_hp)(((unsigned ba0_int_p)(opa)*      \
            (unsigned ba0_int_p)ba0_invert_mint_hp(opb)) \
            % (unsigned ba0_int_p)ba0_mint_hp_module)

#   define ba0_mint_hp_invert(rop,op)    rop = ba0_invert_mint_hp (op)

#endif /* !BA0_MACROS_MINT_HP_H */
#if ! defined (BA0_MACROS_MPZ_H)
#   define BA0_MACROS_MPZ_H 1

/* #   include "ba0_common.h" */

/*
 * Macros for mpz_t
 *
 * These macros are mostly needed for generic code in the bap library
 */

#   if defined (BA0_USE_GMP)

/*
 * All ba0_functions are mapped to the GMP ones
 */

#      define ba0_mp_set_memory_functions mp_set_memory_functions
#      define ba0_mp_get_memory_functions mp_get_memory_functions

#      define ba0_mpz_t                   mpz_t
#      define ba0__mpz_struct             __mpz_struct
#      define ba0_mp_limb_t               mp_limb_t

#      define ba0_mpz_affect(rop,op)      rop [0] = op [0]
#      define ba0_mpz_init(rop)           mpz_init(rop)
#      define ba0_mpz_clear(rop)          mpz_clear(rop)
#      define ba0_mpz_set(rop,op)         mpz_set(rop,op)
#      define ba0_mpz_swap(rop,op)        mpz_swap(rop,op)
#      define ba0_mpz_init_set(rop,op)    mpz_init_set(rop,op)
#      define ba0_mpz_get_si(op)          mpz_get_si(op)
#      define ba0_mpz_set_str(rop,opa,opb) mpz_set_str(rop,opa,opb)
#      define ba0_mpz_get_str(rop,opa,opb) mpz_get_str(rop,opa,opb)
#      define ba0_mpz_size(op)            mpz_size(op)
#      define ba0_mpz_sizeinbase(opa,opb) mpz_sizeinbase(opa,opb)

#      if ! defined (BA0_USE_X64_GMP)

/*
 * The Linux / MacOS case
 */

#         define ba0_mpz_set_si(rop,op)         mpz_set_si(rop,op)
#         define ba0_mpz_set_ui(rop,op)         mpz_set_ui(rop,op)
#         define ba0_mpz_init_set_si(rop,op)    mpz_init_set_si(rop,op)
#         define ba0_mpz_init_set_ui(rop,op)    mpz_init_set_ui(rop,op)
#         define ba0_mpz_mul_si(rop,opa,opb)    mpz_mul_si(rop,opa,opb)
#         define ba0_mpz_mul_ui(rop,opa,opb)    mpz_mul_ui(rop,opa,opb)
#         define ba0_mpz_mul_2exp(rop,opa,opb)  mpz_mul_2exp(rop,opa,opb)
#         define ba0_mpz_pow_ui(rop,opa,opb)    mpz_pow_ui(rop,opa,opb)
#         define ba0_mpz_ui_pow_ui(rop,opa,opb) mpz_ui_pow_ui(rop,opa,opb)
#         define ba0_mpz_si_pow_ui(rop,opa,opb) \
                    ba0_x64_mpz_si_pow_ui(rop,opa,opb)

#      else
      /*
       * BA0_USE_X64_GMP 
       */

/*
 * The Windows case
 */

#         define ba0_mpz_set_si(rop,op)        ba0_x64_mpz_set_si(rop,op)
#         define ba0_mpz_set_ui(rop,op)        ba0_x64_mpz_set_ui(rop,op)

#         define ba0_mpz_init_set_si(rop,op)    do { \
                    mpz_init(rop);                \
                    ba0_x64_mpz_set_si(rop,op);   \
                    } while (0)

#         define ba0_mpz_init_set_ui(rop,op)    do { \
                    mpz_init(rop);                \
                    ba0_x64_mpz_set_ui(rop,op);   \
                    } while (0)

#         define ba0_mpz_mul_si(rop,opa,opb)    ba0_x64_mpz_mul_si(rop,opa,opb)
#         define ba0_mpz_mul_ui(rop,opa,opb)    ba0_x64_mpz_mul_ui(rop,opa,opb)
#         define ba0_mpz_mul_2exp(rop,opa,opb) \
                    ba0_x64_mpz_mul_2exp(rop,opa,opb)
#         define ba0_mpz_pow_ui(rop,opa,opb)    ba0_x64_mpz_pow_ui(rop,opa,opb)
#         define ba0_mpz_ui_pow_ui(rop,opa,opb) \
                    ba0_x64_mpz_ui_pow_ui(rop,opa,opb)
#         define ba0_mpz_si_pow_ui(rop,opa,opb) \
                    ba0_x64_mpz_si_pow_ui(rop,opa,opb)

#      endif
       /*
        * BA0_USE_X64_GMP 
        */

#      define ba0_mpz_sgn(op)               mpz_sgn(op)
#      define ba0_mpz_is_zero(op)           (mpz_sgn(op) == 0)
#      define ba0_mpz_is_nonzero(op)        (mpz_sgn(op) != 0)
#      define ba0_mpz_is_one(op)            (mpz_cmp_ui(op,1) == 0)
#      define ba0_mpz_is_negative(op)       (mpz_sgn(op) < 0)
#      define ba0_mpz_are_equal(opa,opb)    (mpz_cmp((opa),(opb)) == 0)
#      define ba0_mpz_neg(opa,opb)          mpz_neg(opa,opb)
#      define ba0_mpz_abs(rop,op)           mpz_abs(rop,op)
#      define ba0_mpz_fac_ui(rop,op)        mpz_fac_ui(rop,op)
#      define ba0_mpz_add(rop,opa,opb)      mpz_add(rop,opa,opb)
#      define ba0_mpz_add_ui(rop,opa,opb)   mpz_add_ui(rop,opa,opb)
#      define ba0_mpz_sub(rop,opa,opb)      mpz_sub(rop,opa,opb)
#      define ba0_mpz_sub_ui(rop,opa,opb)   mpz_sub_ui(rop,opa,opb)
#      define ba0_mpz_mul(rop,opa,opb)      mpz_mul(rop,opa,opb)
#      define ba0_mpz_div(rop,opa,opb)      mpz_fdiv_q(rop,opa,opb)
#      define ba0_mpz_mod(rop,opa,opb)      mpz_mod(rop,opa,opb)
#      define ba0_mpz_mod_ui(rop,opa,opb)   mpz_mod_ui(rop,opa,opb)
#      define ba0_mpz_powm(rop,opa,opb,opc) mpz_powm(rop,opa,opb,opc)
#      define ba0_mpz_powm_ui(rop,opa,opb,opc) mpz_powm_ui(rop,opa,opb,opc)
#      define ba0_mpz_cmpabs(opa,opb)       mpz_cmpabs(opa,opb)
#      define ba0_mpz_cmp_si(opa,opb)       mpz_cmp_si(opa,opb)
#      define ba0_mpz_cmp_ui(opa,opb)       mpz_cmp_ui(opa,opb)
#      define ba0_mpz_cmp(opa,opb)          mpz_cmp(opa,opb)
#      define ba0_mpz_invert(rop,opa,opb)   mpz_invert(rop,opa,opb)
#      define ba0_mpz_fdiv_ui(rop,op)       mpz_fdiv_ui(rop,op)
#      define ba0_mpz_fdiv_q_2exp(rop,opa,opb) mpz_fdiv_q_2exp(rop,opa,opb)
#      define ba0_mpz_tdiv_q_2exp(rop,opa,opb) mpz_tdiv_q_2exp(rop,opa,opb)
#      define ba0_mpz_tdiv_qr(ropa,ropb,opa,opb) mpz_tdiv_qr(ropa,ropb,opa,opb)
#      define ba0_mpz_tdiv_q(rop,opa,opb)   mpz_tdiv_q(rop,opa,opb)
#      define ba0_mpz_tdiv_q_ui(rop,opa,opb) mpz_tdiv_q_ui(rop,opa,opb)
#      define ba0_mpz_tdiv_r_ui(rop,opa,opb) mpz_tdiv_r_ui(rop,opa,opb)
#      define ba0_mpz_gcd(rop,opa,opb)      mpz_gcd(rop,opa,opb)
#      define ba0_mpz_gcdext(rop,opa,opb,opc,opd) mpz_gcdext(rop,opa,opb,opc,opd)
#      define ba0_mpz_lcm(rop,opa,opb)      mpz_lcm(rop,opa,opb)
#      define ba0_mpz_divexact(rop,opa,opb) mpz_divexact(rop,opa,opb)
#      define ba0_mpz_sqrt(rop,op)          mpz_sqrt(rop,op)
#      define ba0_mpz_bin_uiui(rop,opa,opb) mpz_bin_uiui(rop,opa,opb)
#      define ba0_mpz_tstbit(opa,opb)       mpz_tstbit(opa,opb)
#      define ba0_mpz_even_p(op)            mpz_even_p(op)

#   else
      /*
       * BA0_USE_GMP 
       */

/*
 * All ba0_functions are mapped to the mini-gmp ones
 */

#      define ba0_mp_set_memory_functions bam_mp_set_memory_functions
#      define ba0_mp_get_memory_functions bam_mp_get_memory_functions

#      define ba0_mpz_t                   bam_mpz_t
#      define ba0__mpz_struct             bam__mpz_struct
#      define ba0_mp_limb_t               bam_mp_limb_t

#      define ba0_mpz_affect(rop,op)      rop [0] = op [0]
#      define ba0_mpz_init(rop)           bam_mpz_init(rop)
#      define ba0_mpz_clear(rop)          bam_mpz_clear(rop)
#      define ba0_mpz_set(rop,op)         bam_mpz_set(rop,op)
#      define ba0_mpz_swap(rop,op)        bam_mpz_swap(rop,op)
#      define ba0_mpz_init_set(rop,op)    bam_mpz_init_set(rop,op)
#      define ba0_mpz_set_str(rop,opa,opb) bam_mpz_set_str(rop,opa,opb)
#      define ba0_mpz_get_str(rop,opa,opb) bam_mpz_get_str(rop,opa,opb)
#      define ba0_mpz_get_si(op)          bam_mpz_get_si(op)
#      define ba0_mpz_size(op)            bam_mpz_size(op)
#      define ba0_mpz_sizeinbase(opa,opb) bam_mpz_sizeinbase(opa,opb)

#      if ! defined (BA0_USE_X64_GMP)

/*
 * The Linux / MacOS case
 */

#         define ba0_mpz_set_si(rop,op)         bam_mpz_set_si(rop,op)
#         define ba0_mpz_set_ui(rop,op)         bam_mpz_set_ui(rop,op)
#         define ba0_mpz_init_set_si(rop,op)    bam_mpz_init_set_si(rop,op)
#         define ba0_mpz_init_set_ui(rop,op)    bam_mpz_init_set_ui(rop,op)
#         define ba0_mpz_mul_si(rop,opa,opb)    bam_mpz_mul_si(rop,opa,opb)
#         define ba0_mpz_mul_ui(rop,opa,opb)    bam_mpz_mul_ui(rop,opa,opb)
#         define ba0_mpz_mul_2exp(rop,opa,opb)  bam_mpz_mul_2exp(rop,opa,opb)
#         define ba0_mpz_pow_ui(rop,opa,opb)    bam_mpz_pow_ui(rop,opa,opb)
#         define ba0_mpz_ui_pow_ui(rop,opa,opb) bam_mpz_ui_pow_ui(rop,opa,opb)

#      else
      /*
       * BA0_USE_X64_GMP 
       */

/*
 * The Windows case
 */

#         define ba0_mpz_set_si(rop,op)        ba0_x64_mpz_set_si(rop,op)
#         define ba0_mpz_set_ui(rop,op)        ba0_x64_mpz_set_ui(rop,op)

#         define ba0_mpz_init_set_si(rop,op)    do { \
                    bam_mpz_init(rop);                \
                    ba0_x64_mpz_set_si(rop,op);   \
                    } while (0)

#         define ba0_mpz_init_set_ui(rop,op)    do { \
                    bam_mpz_init(rop);                \
                    ba0_x64_mpz_set_ui(rop,op);   \
                    } while (0)

#         define ba0_mpz_mul_si(rop,opa,opb)    ba0_x64_mpz_mul_si(rop,opa,opb)
#         define ba0_mpz_mul_ui(rop,opa,opb)    ba0_x64_mpz_mul_ui(rop,opa,opb)
#         define ba0_mpz_mul_2exp(rop,opa,opb) \
                    ba0_x64_mpz_mul_2exp(rop,opa,opb)
#         define ba0_mpz_pow_ui(rop,opa,opb)    ba0_x64_mpz_pow_ui(rop,opa,opb)
#         define ba0_mpz_ui_pow_ui(rop,opa,opb) \
                    ba0_x64_mpz_ui_pow_ui(rop,opa,opb)

#      endif
       /*
        * BA0_USE_X64_GMP 
        */

#      define ba0_mpz_sgn(op)               bam_mpz_sgn(op)
#      define ba0_mpz_is_zero(op)           (bam_mpz_sgn(op) == 0)
#      define ba0_mpz_is_nonzero(op)        (bam_mpz_sgn(op) != 0)
#      define ba0_mpz_is_one(op)            (bam_mpz_cmp_ui(op,1) == 0)
#      define ba0_mpz_is_negative(op)       (bam_mpz_sgn(op) < 0)
#      define ba0_mpz_are_equal(opa,opb)    (bam_mpz_cmp((opa),(opb)) == 0)
#      define ba0_mpz_neg(opa,opb)          bam_mpz_neg(opa,opb)
#      define ba0_mpz_abs(rop,op)           bam_mpz_abs(rop,op)
#      define ba0_mpz_fac_ui(rop,op)        bam_mpz_fac_ui(rop,op)
#      define ba0_mpz_add(rop,opa,opb)      bam_mpz_add(rop,opa,opb)
#      define ba0_mpz_add_ui(rop,opa,opb)   bam_mpz_add_ui(rop,opa,opb)
#      define ba0_mpz_sub(rop,opa,opb)      bam_mpz_sub(rop,opa,opb)
#      define ba0_mpz_sub_ui(rop,opa,opb)   bam_mpz_sub_ui(rop,opa,opb)
#      define ba0_mpz_mul(rop,opa,opb)      bam_mpz_mul(rop,opa,opb)
#      define ba0_mpz_div(rop,opa,opb)      bam_mpz_fdiv_q(rop,opa,opb)
#      define ba0_mpz_mod(rop,opa,opb)      bam_mpz_mod(rop,opa,opb)
#      define ba0_mpz_mod_ui(rop,opa,opb)   bam_mpz_mod_ui(rop,opa,opb)
#      define ba0_mpz_powm(rop,opa,opb,opc) bam_mpz_powm(rop,opa,opb,opc)
#      define ba0_mpz_powm_ui(rop,opa,opb,opc) bam_mpz_powm_ui(rop,opa,opb,opc)
#      define ba0_mpz_cmpabs(opa,opb)       bam_mpz_cmpabs(opa,opb)
#      define ba0_mpz_cmp_si(opa,opb)       bam_mpz_cmp_si(opa,opb)
#      define ba0_mpz_cmp_ui(opa,opb)       bam_mpz_cmp_ui(opa,opb)
#      define ba0_mpz_cmp(opa,opb)          bam_mpz_cmp(opa,opb)
#      define ba0_mpz_invert(rop,opa,opb)   bam_mpz_invert(rop,opa,opb)
#      define ba0_mpz_fdiv_ui(rop,op)       bam_mpz_fdiv_ui(rop,op)
#      define ba0_mpz_fdiv_q_2exp(rop,opa,opb) bam_mpz_fdiv_q_2exp(rop,opa,opb)
#      define ba0_mpz_tdiv_q_2exp(rop,opa,opb) bam_mpz_tdiv_q_2exp(rop,opa,opb)
#      define ba0_mpz_tdiv_qr(ropa,ropb,opa,opb) bam_mpz_tdiv_qr(ropa,ropb,opa,opb)
#      define ba0_mpz_tdiv_q(rop,opa,opb)   bam_mpz_tdiv_q(rop,opa,opb)
#      define ba0_mpz_tdiv_q_ui(rop,opa,opb) bam_mpz_tdiv_q_ui(rop,opa,opb)
#      define ba0_mpz_tdiv_r_ui(rop,opa,opb) bam_mpz_tdiv_r_ui(rop,opa,opb)
#      define ba0_mpz_gcd(rop,opa,opb)      bam_mpz_gcd(rop,opa,opb)
#      define ba0_mpz_gcdext(rop,opa,opb,opc,opd) bam_mpz_gcdext(rop,opa,opb,opc,opd)
#      define ba0_mpz_lcm(rop,opa,opb)      bam_mpz_lcm(rop,opa,opb)
#      define ba0_mpz_divexact(rop,opa,opb) bam_mpz_divexact(rop,opa,opb)
#      define ba0_mpz_sqrt(rop,op)          bam_mpz_sqrt(rop,op)
#      define ba0_mpz_bin_uiui(rop,opa,opb) bam_mpz_bin_uiui(rop,opa,opb)
#      define ba0_mpz_tstbit(opa,opb)       bam_mpz_tstbit(opa,opb)
#      define ba0_mpz_even_p(op)            bam_mpz_even_p(op)

#   endif
       /*
        * BA0_USE_GMP 
        */

#endif /* !BA0_MACROS_MPZ_H */
#if !defined (BA0_MACROS_MPQ_H)
#   define BA0_MACROS_MPQ_H 1

/* #   include "ba0_common.h" */
/* #   include "ba0_macros_mpz.h" */

/* 
 * Macros for mpq_t
 */

#   if defined (BA0_USE_GMP)

#      define ba0_mpq_t                            mpq_t
#      define ba0__mpq_struct                      __mpq_struct

#      define ba0_mpq_affect(rop,op)               rop [0] = op [0]
#      define ba0_mpq_init(rop)                    mpq_init(rop)
#      define ba0_mpq_clear(rop)                   mpq_clear(rop)
#      define ba0_mpq_set(rop,op)                  mpq_set(rop,op)
#      define ba0_mpq_swap(rop,op)                 mpq_swap(rop,op)

#      if ! defined (BA0_USE_X64_GMP)
/*
 * The Linux / Mac OS case
 */
#         define ba0_mpq_set_si(rop,op)            mpq_set_si(rop,op,1)
#         define ba0_mpq_set_si_si(rop,opa,opb)    mpq_set_si(rop,opa,opb)
#         define ba0_mpq_set_ui(rop,op)            mpq_set_ui(rop,op,1)

#      else
/*
 * The Windows case
 */
#         define ba0_mpq_set_si(rop,op)            ba0_x64_mpq_set_si(rop,op,1)
#         define ba0_mpq_set_si_si(rop,opa,opb)    ba0_x64_mpq_set_si(rop,opa,opb)
#         define ba0_mpq_set_ui(rop,op)            ba0_x64_mpq_set_ui(rop,op,1)

#      endif
       /*
        * BA0_USE_X64_GMP 
        */

#      define ba0_mpq_sgn(op)                      mpq_sgn(op)
#      define ba0_mpq_cmp(opa,opb)                 mpq_cmp(opa,opb)
#      define ba0_mpq_cmp_si(opa,opb,opc)          mpq_cmp_si((opa),(opb),(opc))
#      define ba0_mpq_is_zero(op)                  (mpq_cmp_ui((op),0,1) == 0)
#      define ba0_mpq_is_one(op)                   (mpq_cmp_ui((op),1,1) == 0)
#      define ba0_mpq_is_negative(op)              (mpq_cmp_ui((op),0,1) < 0)
#      define ba0_mpq_are_equal(opa,opb)           (mpq_cmp((opa),(opb)) == 0)
#      define ba0_mpq_neg(opa,opb)                 mpq_neg(opa,opb)
#      define ba0_mpq_add(rop,opa,opb)             mpq_add(rop,opa,opb)
#      define ba0_mpq_sub(rop,opa,opb)             mpq_sub(rop,opa,opb)
#      define ba0_mpq_mul(rop,opa,opb)             mpq_mul(rop,opa,opb)

#      define ba0_mpq_canonicalize(rop)            mpq_canonicalize(rop)
#      define ba0_mpq_numref(rop)                  mpq_numref(rop)
#      define ba0_mpq_denref(rop)                  mpq_denref(rop)
#      define ba0_mpq_get_d(rop)                   mpq_get_d(rop)
#      define ba0_mpq_set_d(rop,op)                mpq_set_d(rop,op)
#      define ba0_mpq_set_num(rop,op)              mpq_set_num(rop,op)
#      define ba0_mpq_set_den(rop,op)              mpq_set_den(rop,op)
#      define ba0_mpq_set_z(rop,op)                mpq_set_z(rop,op)

#      define ba0_mpq_div(rop,opa,opb)             mpq_div(rop,opa,opb)
#      define ba0_mpq_invert(rop,op)               mpq_inv(rop,op)

#   else
      /*
       * BA0_USE_GMP 
       */

#      define ba0_mpq_t                            bam_mpq_t
#      define ba0__mpq_struct                      bam__mpq_struct

#      define ba0_mpq_affect(rop,op)               rop [0] = op [0]
#      define ba0_mpq_init(rop)                    bam_mpq_init(rop)
#      define ba0_mpq_clear(rop)                   bam_mpq_clear(rop)
#      define ba0_mpq_set(rop,op)                  bam_mpq_set(rop,op)
#      define ba0_mpq_swap(rop,op)                 bam_mpq_swap(rop,op)

#      if ! defined (BA0_USE_X64_GMP)
/*
 * The Linux / Mac OS case
 */
#         define ba0_mpq_set_si(rop,op)            bam_mpq_set_si(rop,op,1)
#         define ba0_mpq_set_si_si(rop,opa,opb)    bam_mpq_set_si(rop,opa,opb)
#         define ba0_mpq_set_ui(rop,op)            bam_mpq_set_ui(rop,op,1)

#      else
/*
 * The Windows case
 */
#         define ba0_mpq_set_si(rop,op)            ba0_x64_mpq_set_si(rop,op,1)
#         define ba0_mpq_set_si_si(rop,opa,opb)    ba0_x64_mpq_set_si(rop,opa,opb)
#         define ba0_mpq_set_ui(rop,op)            ba0_x64_mpq_set_ui(rop,op,1)

#      endif
       /*
        * BA0_USE_X64_GMP 
        */

#      define ba0_mpq_sgn(op)                      bam_mpq_sgn(op)
#      define ba0_mpq_cmp(opa,opb)                 bam_mpq_cmp(opa,opb)
#      define ba0_mpq_cmp_si(opa,opb,opc)          bam_mpq_cmp_si((opa),(opb),(opc))
#      define ba0_mpq_is_zero(op)                  (bam_mpq_cmp_ui((op),0,1) == 0)
#      define ba0_mpq_is_one(op)                   (bam_mpq_cmp_ui((op),1,1) == 0)
#      define ba0_mpq_is_negative(op)              (bam_mpq_cmp_ui((op),0,1) < 0)
#      define ba0_mpq_are_equal(opa,opb)           (bam_mpq_cmp((opa),(opb)) == 0)
#      define ba0_mpq_neg(opa,opb)                 bam_mpq_neg(opa,opb)
#      define ba0_mpq_add(rop,opa,opb)             bam_mpq_add(rop,opa,opb)
#      define ba0_mpq_sub(rop,opa,opb)             bam_mpq_sub(rop,opa,opb)
#      define ba0_mpq_mul(rop,opa,opb)             bam_mpq_mul(rop,opa,opb)

#      define ba0_mpq_canonicalize(rop)            bam_mpq_canonicalize(rop)
#      define ba0_mpq_numref(rop)                  bam_mpq_numref(rop)
#      define ba0_mpq_denref(rop)                  bam_mpq_denref(rop)
#      define ba0_mpq_get_d(rop)                   bam_mpq_get_d(rop)
#      define ba0_mpq_set_d(rop,op)                bam_mpq_set_d(rop,op)
#      define ba0_mpq_set_num(rop,op)              bam_mpq_set_num(rop,op)
#      define ba0_mpq_set_den(rop,op)              bam_mpq_set_den(rop,op)
#      define ba0_mpq_set_z(rop,op)                bam_mpq_set_z(rop,op)

#      define ba0_mpq_div(rop,opa,opb)             bam_mpq_div(rop,opa,opb)
#      define ba0_mpq_invert(rop,op)               bam_mpq_inv(rop,op)

#   endif
       /*
        * BA0_USE_GMP 
        */

/*
 * Generic macros
 */

#   define ba0_mpq_init_set(rop,op)             \
        do {                                    \
          ba0_mpq_init(rop);                    \
          ba0_mpq_set(rop,op);                  \
        } while (0)

#   define ba0_mpq_init_set_si(rop,op)          \
        do {                                    \
          ba0_mpq_init(rop);                    \
          ba0_mpq_set_si(rop,op);               \
        } while (0)

#   define ba0_mpq_init_set_ui(rop,op)          \
        do {                                    \
          ba0_mpq_init(rop);                    \
          ba0_mpq_set_ui(rop,op);               \
        } while (0)

#   define ba0_mpq_mul_ui(rop,opa,opb)          \
        do {                                    \
          ba0_mpq_set(rop,opa);                 \
          ba0_mpz_mul_ui(ba0_mpq_numref(rop),ba0_mpq_numref(opa),opb); \
          ba0_mpq_canonicalize(rop);            \
        } while (0)

#   define ba0_mpq_mul_si(rop,opa,opb)          \
        do {                                    \
          ba0_mpq_set(rop,opa);                 \
          ba0_mpz_mul_si(ba0_mpq_numref(rop),ba0_mpq_numref(rop),opb); \
          ba0_mpq_canonicalize(rop);            \
        } while (0)

#   define ba0_mpq_pow_ui(rop,opa,opb)          \
        do {                                    \
          ba0_mpz_pow_ui(ba0_mpq_numref(rop),ba0_mpq_numref(opa),opb); \
          ba0_mpz_pow_ui(ba0_mpq_denref(rop),ba0_mpq_denref(opa),opb); \
        } while (0)

#endif /* !BA0_MACROS_MPQ_H */
#if !defined (BA0_MACROS_MPZM_H)
#   define BA0_MACROS_MPZM_H 1

/* #   include "ba0_common.h" */
/* #   include "ba0_macros_mpz.h" */

/* 
 * Macros for ba0_mpzm
 */

#   define ba0_mpzm_t                           ba0_mpz_t
#   define ba0_mpzm_module                      ba0_global.mpzm.module
#   define ba0_mpzm_init(rop)                   ba0_mpz_init(rop)
#   define ba0_mpzm_set(rop,op)                 ba0_mpz_set(rop,op)
#   define ba0_mpzm_affect(rop,op)              rop [0] = op [0]
#   define ba0_mpzm_swap(opa,opb)               ba0_mpz_swap(opa,opb)

#   define ba0_mpzm_set_si(rop,op)              \
        do {                                    \
          ba0_mpz_set_si(rop,op);               \
          ba0_mpz_mod(rop,rop,ba0_mpzm_module); \
        } while (0)

#   define ba0_mpzm_init_set(rop,op)    ba0_mpz_init_set(rop,op)

#   define ba0_mpzm_init_set_si(rop,op)         \
        do {                                    \
          ba0_mpz_init_set_si(rop,op);          \
          ba0_mpz_mod(rop,rop,ba0_mpzm_module); \
        } while (0)

#   define ba0_mpzm_init_set_ui(rop,op)         \
        do {                                    \
          ba0_mpz_init_set_ui(rop,op);          \
          ba0_mpz_mod(rop,rop,ba0_mpzm_module); \
        } while (0)

#   define ba0_mpzm_is_zero(op)                 (ba0_mpz_cmp_ui((op),0) == 0)
#   define ba0_mpzm_is_one(op)                  (ba0_mpz_cmp_ui((op),1) == 0)
#   define ba0_mpzm_is_negative(op)             false
#   define ba0_mpzm_are_equal(opa,opb)          (ba0_mpz_cmp((opa),(opb)) == 0)

#   define ba0_mpzm_neg(rop,op)                 \
        do {                                    \
          ba0_mpz_neg(rop,op);                  \
          ba0_mpz_mod(rop,rop,ba0_mpzm_module); \
        } while (0)

#   define ba0_mpzm_add(rop,opa,opb)            \
        do {                                    \
          ba0_mpz_add(rop,opa,opb);             \
          ba0_mpz_mod(rop,rop,ba0_mpzm_module); \
        } while (0)

#   define ba0_mpzm_sub(rop,opa,opb)            \
        do {                                    \
          ba0_mpz_sub(rop,opa,opb);             \
          ba0_mpz_mod(rop,rop,ba0_mpzm_module); \
        } while (0)

#   define ba0_mpzm_mul(rop,opa,opb)            \
        do {                                    \
          ba0_push_stack (&ba0_global.stack.quiet); \
          ba0_mpz_mul(ba0_mpzm_accum,opa,opb);  \
          ba0_pull_stack ();                    \
          ba0_mpz_mod(rop,ba0_mpzm_accum,ba0_mpzm_module); \
        } while (0)

#   define ba0_mpzm_mul_ui(rop,opa,opb)         \
        do {                                    \
          ba0_push_stack (&ba0_global.stack.quiet); \
          ba0_mpz_mul_ui(ba0_mpzm_accum,opa,opb);   \
          ba0_pull_stack ();                    \
          ba0_mpz_mod(rop,ba0_mpzm_accum,ba0_mpzm_module); \
        } while (0)

#   define ba0_mpzm_mul_si(rop,opa,opb)         \
        do {                                    \
          ba0_mpz_mul_si(rop,opa,opb);          \
          ba0_mpz_mod(rop,rop,ba0_mpzm_module); \
        } while (0)

#   if ! defined (BA0_USE_X64_GMP)
/*
 * The Linux / Mac OS Case
 */
#      define ba0_mpzm_pow_ui(rop,opa,opb)      \
        ba0_mpz_powm_ui(rop,opa,opb,ba0_mpzm_module)
#   else
/*
 * The Windows case
 */
#      define ba0_mpzm_pow_ui(rop,opa,opb)      \
        do {                                    \
          ba0_mpz_t bunk;                       \
          ba0_push_another_stack ();            \
          ba0_mpz_set_ui(bunk,opb);             \
          ba0_pull_stack ();                    \
          ba0_mpz_powm(rop,opa,bunk,ba0_mpzm_module); \
        } while (0)
#   endif

#   define ba0_mpzm_div(rop,opa,opb)            \
        do {                                    \
          ba0_push_stack (&ba0_global.stack.quiet);           \
          ba0_mpz_invert(ba0_mpzm_accum,opb,ba0_mpzm_module); \
          ba0_mpz_mul(ba0_mpzm_accum,ba0_mpzm_accum,opa);     \
          ba0_pull_stack ();                    \
          ba0_mpz_mod(rop,ba0_mpzm_accum,ba0_mpzm_module);    \
        } while (0)

#   define ba0_mpzm_invert(rop,op)              \
      ba0_mpz_invert(rop,op,ba0_mpzm_module)

#endif /* !BA0_MACROS_MPZM_H */
#if !defined (BA0_DOUBLE_H)
#   define BA0_DOUBLE_H 1

/* #   include "ba0_common.h" */

BEGIN_C_DECLS

typedef double *ba0_double;

struct ba0_tableof_double
{
  ba0_int_p alloc;
  ba0_int_p size;
  ba0_double *tab;
};

struct ba0_arrayof_double
{
  ba0_int_p alloc;
  ba0_int_p size;
  double *tab;
  ba0_int_p sizelt;
};

struct ba0_matrixof_double
{
  ba0_int_p alloc;
  ba0_int_p nrow;
  ba0_int_p ncol;
  ba0_double *entry;
};

extern BA0_DLL ba0_double ba0_new_double (
    void);

extern BA0_DLL ba0_scanf_function ba0_scanf_double;

extern BA0_DLL ba0_printf_function ba0_printf_double;

extern BA0_DLL ba0_garbage1_function ba0_garbage1_double;

extern BA0_DLL ba0_garbage2_function ba0_garbage2_double;

extern BA0_DLL ba0_copy_function ba0_copy_double;

extern BA0_DLL int ba0_isnan (
    double);

extern BA0_DLL int ba0_isinf (
    double);

extern BA0_DLL double ba0_atof (
    char *);

extern BA0_DLL unsigned ba0_int_p ba0_sizeof_arrayof_double (
    struct ba0_arrayof_double *,
    enum ba0_garbage_code);

END_C_DECLS
#endif /* !BA0_DOUBLE_H */
#if ! defined (BA0_GMP_H)
#   define BA0_GMP_H 1

/* #   include "ba0_common.h" */

#   if defined (BA0_USE_GMP)
#      include <gmp.h>
#   else
/* #      include "mini-gmp.h" */
/* #      include "mini-mpq.h" */
#   endif

/* #   include "ba0_macros_mpz.h" */
/* #   include "ba0_macros_mpq.h" */

BEGIN_C_DECLS

struct ba0_tableof_mpz
{
  ba0_int_p alloc;
  ba0_int_p size;
  ba0__mpz_struct **tab;
};

struct ba0_tableof_tableof_mpz
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_tableof_mpz **tab;
};

struct ba0_listof_mpz
{
  ba0__mpz_struct *value;
  struct ba0_listof_mpz *next;
};

struct ba0_tableof_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  ba0__mpq_struct **tab;
};

struct ba0_listof_mpq
{
  ba0__mpq_struct *value;
  struct ba0_listof_mpq *next;
};

typedef void ba0_set_memory_functions_function (
    void *(*)(size_t),
    void *(*)(void *,
        size_t,
        size_t),
    void (*)(void *,
        size_t));


extern BA0_DLL void ba0_set_settings_gmp (
    ba0_set_memory_functions_function *,
    char *);

extern BA0_DLL void ba0_get_settings_gmp (
    ba0_set_memory_functions_function **,
    char **);

extern BA0_DLL void ba0_record_gmp_memory_functions (
    void);

extern BA0_DLL void ba0_restore_gmp_memory_functions (
    void);

extern BA0_DLL bool ba0_domain_mpz (
    void);

extern BA0_DLL bool ba0_domain_mpq (
    void);

extern BA0_DLL void *ba0_gmp_alloc (
    size_t);

extern BA0_DLL void *ba0_gmp_realloc (
    void *,
    size_t,
    size_t);

extern BA0_DLL void ba0_gmp_free (
    void *,
    size_t);

extern BA0_DLL void ba0_set_tableof_mpz (
    struct ba0_tableof_mpz *,
    struct ba0_tableof_mpz *);

extern BA0_DLL void ba0_set_tableof_tableof_mpz (
    struct ba0_tableof_tableof_mpz *,
    struct ba0_tableof_tableof_mpz *);

extern BA0_DLL ba0__mpq_struct *ba0_new_mpq (
    void);

extern BA0_DLL ba0__mpz_struct *ba0_new_mpz (
    void);

extern BA0_DLL void ba0_mpz_si_pow_ui (
    ba0__mpz_struct *,
    ba0_int_p,
    unsigned ba0_int_p);

extern BA0_DLL void ba0_mpz_nextprime (
    ba0__mpz_struct *,
    ba0__mpz_struct *);

extern BA0_DLL ba0_scanf_function ba0_scanf_mpz;

extern BA0_DLL ba0_printf_function ba0_printf_mpz;

extern BA0_DLL ba0_garbage1_function ba0_garbage1_mpz;

extern BA0_DLL ba0_garbage2_function ba0_garbage2_mpz;

extern BA0_DLL ba0_copy_function ba0_copy_mpz;

extern BA0_DLL ba0_scanf_function ba0_scanf_mpq;

extern BA0_DLL ba0_printf_function ba0_printf_mpq;

extern BA0_DLL ba0_garbage1_function ba0_garbage1_mpq;

extern BA0_DLL ba0_garbage2_function ba0_garbage2_mpq;

extern BA0_DLL ba0_copy_function ba0_copy_mpq;

END_C_DECLS
#endif /* !BA0_GMP_H */
#if ! defined (BA0_INTERVAL_MPQ_H)
#   define BA0_INTERVAL_MPQ_H 1

/* #   include "ba0_common.h" */
/* #   include "ba0_gmp.h" */
/* #   include "ba0_macros_mpq.h" */

BEGIN_C_DECLS

enum ba0_typeof_interval
{
  ba0_closed_interval,
  ba0_open_interval,
  ba0_empty_interval,
  ba0_infinite_interval,
  ba0_left_infinite_interval,
  ba0_right_infinite_interval
};

struct ba0_interval_mpq
{
  ba0_mpq_t a;
  ba0_mpq_t b;
  enum ba0_typeof_interval type;
};


struct ba0_tableof_interval_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_interval_mpq **tab;
};


struct ba0_listof_interval_mpq
{
  struct ba0_interval_mpq *value;
  struct ba0_listof_interval_mpq *next;
};


extern BA0_DLL bool ba0_domain_interval_mpq (
    void);

extern BA0_DLL void ba0_init_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL struct ba0_interval_mpq *ba0_new_interval_mpq (
    void);

extern BA0_DLL void ba0_set_interval_mpq_si (
    struct ba0_interval_mpq *,
    ba0_int_p);

extern BA0_DLL void ba0_set_interval_mpq_ui (
    struct ba0_interval_mpq *,
    unsigned ba0_int_p);

extern BA0_DLL void ba0_set_interval_mpq_double (
    struct ba0_interval_mpq *,
    double);

extern BA0_DLL void ba0_set_interval_mpq_mpq (
    struct ba0_interval_mpq *,
    ba0_mpq_t,
    ba0_mpq_t);

extern BA0_DLL void ba0_set_interval_mpq_type_mpq (
    struct ba0_interval_mpq *,
    enum ba0_typeof_interval,
    ba0_mpq_t,
    ba0_mpq_t);

extern BA0_DLL void ba0_set_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_empty_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_closed_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_open_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_unbounded_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_zero_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_one_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_are_equal_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_contains_zero_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_positive_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_negative_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_nonpositive_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_nonnegative_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_less_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_are_disjoint_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_member_interval_mpq (
    ba0_mpq_t,
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_subset_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_element_interval_mpq (
    ba0_mpq_t,
    struct ba0_interval_mpq *,
    unsigned ba0_int_p);

extern BA0_DLL void ba0_middle_interval_mpq (
    ba0_mpq_t,
    struct ba0_interval_mpq *);

extern BA0_DLL double ba0_middle_interval_mpq_double (
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_width_interval_mpq (
    ba0_mpq_t,
    struct ba0_interval_mpq *);

extern BA0_DLL double ba0_width_interval_mpq_double (
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_middle_interval_mpq (
    ba0_mpq_t,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_intersect_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_abs_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_neg_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_add_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_add_interval_mpq_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    ba0_mpq_t);

extern BA0_DLL void ba0_sub_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_sub_mpq_interval_mpq (
    struct ba0_interval_mpq *,
    ba0_mpq_t,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_sub_interval_mpq_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    ba0_mpq_t);

extern BA0_DLL void ba0_mul_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_mul_interval_mpq_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    ba0_mpq_t);

extern BA0_DLL void ba0_mul_interval_mpq_si (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    ba0_int_p);

extern BA0_DLL void ba0_mul_interval_mpq_ui (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    unsigned ba0_int_p);

extern BA0_DLL void ba0_pow_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    ba0_int_p);

extern BA0_DLL void ba0_pow_interval_mpq_mpq (
    struct ba0_interval_mpq *,
    ba0_mpq_t,
    ba0_int_p n);

extern BA0_DLL void ba0_div_interval_mpq (
    struct ba0_tableof_interval_mpq *,
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_div_mpq_interval_mpq (
    struct ba0_tableof_interval_mpq *,
    ba0_mpq_t,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_div_interval_mpq_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    ba0_mpq_t);

extern BA0_DLL ba0_scanf_function ba0_scanf_interval_mpq;

extern BA0_DLL ba0_printf_function ba0_printf_interval_mpq;

extern BA0_DLL ba0_garbage1_function ba0_garbage1_interval_mpq;

extern BA0_DLL ba0_garbage2_function ba0_garbage2_interval_mpq;

extern BA0_DLL ba0_copy_function ba0_copy_interval_mpq;

END_C_DECLS
#endif
#if ! defined (BA0_MACROS_INTERVAL_MPQ_H)
#   define BA0_MACROS_INTERVAL_MPQ_H 1

/* #   include "ba0_common.h" */
/* #   include "ba0_interval_mpq.h" */

/* 
 * Macros for ba0_interval_mpq 
 */

typedef struct ba0_interval_mpq ba0_interval_mpq_t[1];

#   define ba0_interval_mpq_affect(rop,op)      ba0_set_interval_mpq (rop, op)
#   define ba0_interval_mpq_init(rop)           ba0_init_interval_mpq (rop)
#   define ba0_interval_mpq_set(rop,op)         ba0_set_interval_mpq (rop, op)
#   define ba0_interval_mpq_swap(rop,op)        BA0_SWAP(struct ba0_interval_mpq,rop[0],op[0])
#   define ba0_interval_mpq_set_si(rop,op)      ba0_set_interval_mpq_si (rop, op)
#   define ba0_interval_mpq_set_ui(rop,op)      ba0_set_interval_mpq_ui (rop, op)
#   define ba0_interval_mpq_init_set(rop,op)    ba0_set_interval_mpq (rop, op)

#   define ba0_interval_mpq_init_set_si(rop,op) \
       do {                                     \
         ba0_interval_mpq_init(rop);            \
         ba0_set_interval_mpq_si (rop, op);     \
       } while (0)

#   define ba0_interval_mpq_init_set_ui(rop,op) \
       do {                                     \
         ba0_interval_mpq_init(rop);            \
         ba0_set_interval_mpq_ui (rop, op);     \
       } while (0)

#   define ba0_interval_mpq_is_zero(op)         ba0_is_zero_interval_mpq (op)
#   define ba0_interval_mpq_is_one(op)          ba0_is_one_interval_mpq (op)
#   define ba0_interval_mpq_is_negative(op)     ba0_is_negative_interval_mpq (op)
#   define ba0_interval_mpq_are_equal(opa,opb)  ba0_are_equal_interval_mpq (opa, opb)
#   define ba0_interval_mpq_neg(rop,op)         ba0_neg_interval_mpq (rop, op)
#   define ba0_interval_mpq_add(rop,opa,opb)    ba0_add_interval_mpq (rop, opa, opb)
#   define ba0_interval_mpq_sub(rop,opa,opb)    ba0_sub_interval_mpq (rop, opa, opb)
#   define ba0_interval_mpq_mul(rop,opa,opb)    ba0_mul_interval_mpq (rop, opa, opb)
#   define ba0_interval_mpq_mul_ui(rop,opa,opb) ba0_mul_interval_mpq_ui (rop, opa, opb)
#   define ba0_interval_mpq_mul_si(rop,opa,opb) ba0_mul_interval_mpq_si (rop, opa, opb)
#   define ba0_interval_mpq_pow_ui(rop,opa,opb) ba0_pow_interval_mpq (rop, opa, (ba0_int_p)opb)

#endif
#if !defined (BA0_STRING_H)
#   define BA0_STRING_H 1

/* #   include "ba0_common.h" */

BEGIN_C_DECLS

struct ba0_tableof_string
{
  ba0_int_p alloc;
  ba0_int_p size;
  char **tab;
};

struct ba0_matrixof_string
{
  ba0_int_p alloc;
  ba0_int_p nrow;
  ba0_int_p ncol;
  char **entry;
};

struct ba0_listof_string
{
  char *value;
  struct ba0_listof_string *next;
};

struct ba0_tableof_tableof_string
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_tableof_string **tab;
};

extern BA0_DLL char *ba0_not_a_string (
    void);

extern BA0_DLL char *ba0_new_string (
    void);

extern BA0_DLL char *ba0_strdup (
    char *);

extern BA0_DLL char *ba0_strcat (
    struct ba0_tableof_string *);

/* 
 * redefined since they are not ANSI */

extern BA0_DLL int ba0_strcasecmp (
    char *,
    char *);

extern BA0_DLL int ba0_strncasecmp (
    char *,
    char *,
    size_t);

extern BA0_DLL ba0_scanf_function ba0_scanf_string;

extern BA0_DLL ba0_printf_function ba0_printf_string;

extern BA0_DLL ba0_garbage1_function ba0_garbage1_string;

extern BA0_DLL ba0_garbage2_function ba0_garbage2_string;

extern BA0_DLL ba0_copy_function ba0_copy_string;

extern BA0_DLL void ba0_set_tableof_string (
    struct ba0_tableof_string *,
    struct ba0_tableof_string *);

extern BA0_DLL bool ba0_member2_tableof_string (
    char *,
    struct ba0_tableof_string *,
    ba0_int_p *);

extern BA0_DLL unsigned ba0_int_p ba0_sizeof_tableof_string (
    struct ba0_tableof_string *,
    enum ba0_garbage_code);

END_C_DECLS
#endif /* !BA0_STRING_H */
#if !defined (BA0_DICTIONARY_H)
#   define BA0_DICTIONARY_H 1

/* #   include "ba0_common.h" */
/* #   include "ba0_int_p.h" */
/* #   include "ba0_table.h" */

BEGIN_C_DECLS

/*
 * texinfo: ba0_dictionary
 * This data structure implements generic dictionaries which map 
 * @code{void *} pointers or @code{ba0_int_p} to other objects.
 * In this implementation, the values associated to the keys are integers, 
 * which are supposed to be indices in some table of objects of unspecified 
 * type.
 * It is implemented using the double hash strategy.
 * The entries of the field @code{area} contain either @math{-1} or 
 * the index, in some unspecified table, of some object.
 * The size of @code{area} is a power of two given by @code{log2_size}.
 *
 * For computing hash values, keys are first shifted @code{shift} bits
 * to the right. For a dictionary of integers @code{shift} should be zero.
 * For a dictionary of pointers to objects of type @var{T}, 
 * @code{shift} should be the highest exponent @math{e} such that 
 * @math{2^e} is less than or equal to the size in bytes of
 * the objects to type @var{T}.
 */

struct ba0_dictionary
{
// each entry contains either -1 or an index in some table of variables
  struct ba0_tableof_int_p area;
// the shift applied on keys before hashing them
  ba0_int_p shift;
// the base-2 logarithm of the size/alloc field of area if area is nonempty
  ba0_int_p log2_size;
// the number of used entries in area
  ba0_int_p used_entries;
};

extern BA0_DLL void ba0_init_dictionary (
    struct ba0_dictionary *,
    ba0_int_p,
    ba0_int_p);

extern BA0_DLL void ba0_reset_dictionary (
    struct ba0_dictionary *);

extern BA0_DLL unsigned ba0_int_p ba0_sizeof_dictionary (
    struct ba0_dictionary *,
    enum ba0_garbage_code);

extern BA0_DLL void ba0_set_dictionary (
    struct ba0_dictionary *,
    struct ba0_dictionary *);

extern BA0_DLL ba0_int_p ba0_get_dictionary (
    struct ba0_dictionary *,
    struct ba0_table *,
    void *);

extern BA0_DLL void ba0_add_dictionary (
    struct ba0_dictionary *,
    struct ba0_table *,
    void *,
    ba0_int_p);

END_C_DECLS
#endif /* !BA0_DICTIONARY_H */
#if !defined (BA0_DICTIONARY_STRING_H)
#   define BA0_DICTIONARY_STRING_H 1

/* #   include "ba0_common.h" */
/* #   include "ba0_int_p.h" */
/* #   include "ba0_table.h" */

BEGIN_C_DECLS

/*
 * texinfo: ba0_dictionary_string
 * This data structure implements generic dictionaries which map strings
 * to other objects. In this implementation, the values associated
 * to the keys are integers, which are supposed to be indices in some 
 * table of objects of unspecified type.
 * It is implemented using the double hash strategy.
 * The entries of the field @code{area} contain either @math{-1} or 
 * the index, in some unspecified table, of some object.
 * The size of @code{area} is a power of two given by @code{log2_size}.
 */

struct ba0_dictionary_string
{
// each entry contains either -1 or an index in some table of variables
  struct ba0_tableof_int_p area;
// the base-2 logarithm of the size/alloc field of area if area is nonempty
  ba0_int_p log2_size;
// the number of used entries in area
  ba0_int_p used_entries;
// a function which associates an identifier to an object
  char *(
      *object_to_ident) (
      void *);
};

extern BA0_DLL void ba0_init_dictionary_string (
    struct ba0_dictionary_string *,
    char *(*)(void *),
    ba0_int_p);

extern BA0_DLL void ba0_reset_dictionary_string (
    struct ba0_dictionary_string *);

extern BA0_DLL unsigned ba0_int_p ba0_sizeof_dictionary_string (
    struct ba0_dictionary_string *,
    enum ba0_garbage_code);

extern BA0_DLL void ba0_set_dictionary_string (
    struct ba0_dictionary_string *,
    struct ba0_dictionary_string *);

extern BA0_DLL ba0_int_p ba0_get_dictionary_string (
    struct ba0_dictionary_string *,
    struct ba0_table *,
    char *);

extern BA0_DLL void ba0_add_dictionary_string (
    struct ba0_dictionary_string *,
    struct ba0_table *,
    char *,
    ba0_int_p);

END_C_DECLS
#endif /* !BA0_DICTIONARY_STRING_H */
#if !defined (BA0_DICTIONARY_TYPED_STRING_H)
#   define BA0_DICTIONARY_TYPED_STRING_H 1

/* #   include "ba0_common.h" */
/* #   include "ba0_int_p.h" */
/* #   include "ba0_table.h" */

BEGIN_C_DECLS

/*
 * texinfo: ba0_dictionary_typed_string
 * Variant of the data structure @code{ba0_dictionary_string} where
 * keys are couples formed by a string and a type rather than simply
 * a string.
 */

struct ba0_dictionary_typed_string
{
// each entry contains either -1 or an index in some table of variables
  struct ba0_tableof_int_p area;
// the base-2 logarithm of the size/alloc field of area if area is nonempty
  ba0_int_p log2_size;
// the number of used entries in area
  ba0_int_p used_entries;
// a function which associates an identifier to an object
  char *(
      *object_to_ident) (
      void *);
// a function which associates a type to an object
    ba0_int_p (
      *object_to_type) (
      void *);
};

extern BA0_DLL void ba0_init_dictionary_typed_string (
    struct ba0_dictionary_typed_string *,
    char *(*)(void *),
    ba0_int_p (*)(void *),
    ba0_int_p);

extern BA0_DLL void ba0_reset_dictionary_typed_string (
    struct ba0_dictionary_typed_string *);

extern BA0_DLL unsigned ba0_int_p ba0_sizeof_dictionary_typed_string (
    struct ba0_dictionary_typed_string *,
    enum ba0_garbage_code);

extern BA0_DLL void ba0_set_dictionary_typed_string (
    struct ba0_dictionary_typed_string *,
    struct ba0_dictionary_typed_string *);

extern BA0_DLL ba0_int_p ba0_get_dictionary_typed_string (
    struct ba0_dictionary_typed_string *,
    struct ba0_table *,
    char *,
    ba0_int_p);

extern BA0_DLL void ba0_add_dictionary_typed_string (
    struct ba0_dictionary_typed_string *,
    struct ba0_table *,
    char *,
    ba0_int_p,
    ba0_int_p);

END_C_DECLS
#endif /* !BA0_DICTIONARY_TYPED_STRING_H */
#if !defined (BA0_BASIC_IO_H)
#   define BA0_BASIC_IO_H 1

/* #   include "ba0_common.h" */

BEGIN_C_DECLS

/*
 * texinfo: ba0_typeof_device
 * This data type permits to specify the device from/to which
 * the input is read of the output is written.
 */

enum ba0_typeof_device
{
  ba0_string_device,
  ba0_file_device,
  ba0_counter_device
};

/*
 * texinfo: ba0_output_device
 * This data type the device to which output is written.
 */

struct ba0_output_device
{
  enum ba0_typeof_device vers;
// if vers is equal to ba0_file_device
  FILE *file_flux;
// if vers is equal to ba0_string_device
  char *string_flux;
// index in string_flux
  ba0_int_p indice;
// if vers is equal to ba0_counter_device (number of output characters)
  ba0_int_p counter;
};

#   define BA0_DEFAULT_OUTPUT_LINE_LENGTH	80
#   define ba0_output_line_length ba0_global.basic_io.output_line_length

extern BA0_DLL void ba0_set_output_FILE (
    FILE *);

extern BA0_DLL void ba0_set_output_string (
    char *);

extern BA0_DLL void ba0_set_output_counter (
    void);

#   define BA0_BASIC_IO_SIZE_STACK 10

extern BA0_DLL void ba0_record_output (
    void);

extern BA0_DLL void ba0_restore_output (
    void);

extern BA0_DLL void ba0_reset_output (
    void);

extern BA0_DLL void ba0_put_char (
    char);

extern BA0_DLL void ba0_put_int_p (
    ba0_int_p);

extern BA0_DLL void ba0_put_hexint_p (
    ba0_int_p);

extern BA0_DLL ba0_printf_function ba0_put_string;

extern BA0_DLL ba0_int_p ba0_output_counter (
    void);

/*
 * texinfo: ba0_input_device
 * This data type the device from which input is read.
 */

struct ba0_input_device
{
  enum ba0_typeof_device from;
// if from == ba0_file_device
  FILE *file_flux;
// if from == ba0_string_device
  char *string_flux;
  ba0_int_p indice;
};

extern BA0_DLL void ba0_set_input_FILE (
    FILE *);

extern BA0_DLL void ba0_set_input_string (
    char *);

extern BA0_DLL bool ba0_isatty_input (
    void);

extern BA0_DLL void ba0_reset_input (
    void);

extern BA0_DLL void ba0_record_input (
    void);

extern BA0_DLL void ba0_restore_input (
    void);

extern BA0_DLL int ba0_get_char (
    void);

extern BA0_DLL void ba0_unget_char (
    int);

END_C_DECLS
#endif /* !BA0_BASIC_IO_H */
#if !defined (BA0_ANALEX_H)
#   define BA0_ANALEX_H 1

/* 
 * Lexical analyzer.
 */

/* #   include "ba0_common.h" */
/* #   include "ba0_string.h" */
/* #   include "ba0_dictionary_string.h" */

BEGIN_C_DECLS

/*
 * texinfo: ba0_typeof_token
 * This data type permits to assign a type to a token.
 */

enum ba0_typeof_token
{
// Special value
  ba0_no_token,
// The token is an integer starting with a digit (unsigned)
  ba0_integer_token,
// The token is a sign. Signs are single characters
  ba0_sign_token,
// The token is a string. 
// Any sequence of characters delimited by quotes is a string
  ba0_string_token
};

/* 
 * texinfo: ba0_token
 * This data type permits to store one token.
 */

struct ba0_token
{
// The type of the token
  enum ba0_typeof_token type;
// At least one space was present before the first token character
  bool spaces_before;
// The value of the token, stored in the analex stack.
  char *value;
};

/* 
 * texinfo: ba0_analex_token_fifo
 * This data type describes a FIFO of tokens implemented as a
 * circular array.
 * The only variables of this type are fields of @code{ba0_global}.
 */

struct ba0_analex_token_fifo
{
// The array of token containing the FIFO.
// Its length is stored in ba0_initialized_global.analex.nb_tokens
  struct ba0_token *fifo;
// The index of the first token in the FIFO i.e the current token
  ba0_int_p first;
// The index of the last token present in the FIFO
// It is usually equal to first unless a token has been "ungot"
  ba0_int_p last;
// The number of calls to ba0_get_token_analex since the last reset
  ba0_int_p counter;
};

/* 
 * The default max length of the FIFO
 * The characters that can be used for quoting
 */

#   define BA0_NBTOKENS    20
#   define BA0_QUOTES      "'\""

/* 
 * The length of the error context string (see ba0_global)
 */

#   define BA0_CONTEXT_LMAX 60

/*
 * The size of the substitution dictionary stack (see ba0_global)
 */

#   define BA0_SIZE_SUBS_DICT_STACK 4

extern BA0_DLL void ba0_set_settings_analex (
    ba0_int_p,
    char *);

extern BA0_DLL void ba0_get_settings_analex (
    ba0_int_p *,
    char **);

extern BA0_DLL char *ba0_get_context_analex (
    void);

extern BA0_DLL void ba0_write_context_analex (
    void);

extern BA0_DLL void ba0_init_analex (
    void);

extern BA0_DLL void ba0_clear_analex (
    void);

extern BA0_DLL void ba0_reset_analex (
    void);

extern BA0_DLL void ba0_record_analex (
    void);

extern BA0_DLL void ba0_restore_analex (
    void);

extern BA0_DLL void ba0_reset_subs_dict_analex (
    void);

extern BA0_DLL void ba0_push_subs_dict_analex (
    struct ba0_dictionary_string *,
    struct ba0_tableof_string *,
    struct ba0_tableof_string *);

extern BA0_DLL void ba0_pull_subs_dict_analex (
    void);

extern BA0_DLL void ba0_set_analex_FILE (
    FILE *);

extern BA0_DLL void ba0_set_analex_string (
    char *);

extern BA0_DLL ba0_int_p ba0_get_counter_analex (
    void);

extern BA0_DLL void ba0_get_token_analex (
    void);

extern BA0_DLL void ba0_unget_token_analex (
    ba0_int_p);

extern BA0_DLL void ba0_unget_given_token_analex (
    char *,
    enum ba0_typeof_token,
    bool);

extern BA0_DLL bool ba0_sign_token_analex (
    char *);

extern BA0_DLL bool ba0_spaces_before_token_analex (
    void);

extern BA0_DLL enum ba0_typeof_token ba0_type_token_analex (
    void);

extern BA0_DLL char *ba0_value_token_analex (
    void);

END_C_DECLS
#endif /* !BA0_ANALEX_H */
#if !defined (BA0_FORMAT_H)
#   define BA0_FORMAT_H 1

/* #   include "ba0_common.h" */

BEGIN_C_DECLS

/* 
 * The size of the H-Table for formats.
 * Should be a prime number.
 */

#   define BA0_SIZE_HTABLE_FORMAT      8009

/*
 * texinfo: ba0_typeof_format
 * This data type is a subtype of @code{ba0_subformat}.
 */

enum ba0_typeof_format
{
  ba0_leaf_format,
  ba0_table_format,
  ba0_list_format,
  ba0_matrix_format,
  ba0_array_format,
  ba0_value_format,
  ba0_point_format
};

struct ba0_format;

/*
 * texinfo: ba0_subformat
 * This data type is a subtype of @code{ba0_format}.
 * An element of this type describes a @code{%something}
 * substring of a format. Such substrings may have parameters.
 * Examples are: @code{%t[%v]} (tables of variables), 
 * @code{%l[%t[%z]]} (lists of tables of big integers).
 */

struct ba0_subformat
{
// The type of the subformat
  enum ba0_typeof_format code;
  union
  {
// If type is different from ba0_leaf_format
    struct _node
    {
// The format
      struct ba0_format *op;
// The opening parenthesis of the subformat parameter
      char po;
// The closing parenthesis
      char pf;
    } node;
// If type is ba0_leaf_format
    struct _leaf
    {
// The size of one data structure associated to the type
// and pointers towards associated functions
      ba0_int_p sizelt;
      ba0_scanf_function *scanf;
      ba0_printf_function *printf;
      ba0_garbage1_function *garbage1;
      ba0_garbage2_function *garbage2;
      ba0_copy_function *copy;
    } leaf;
  } u;
};


/*
 * texinfo: ba0_format
 * This data type describes a format, which is a string that can
 * be passed to functions such as @code{ba0_scanf}, @code{ba0_printf},
 * @code{ba0_copy} or @code{ba0_garbage}. Examples are:
 * @code{"poly = %Az\n"} or @code{"%t[%v], %qi"}.
 *
 * The subformats @code{%something} which occur in such strings
 * are preprocessed. 
 *
 * Each format is stored in a hash table of
 * formats, stored in the format stack whenever it is encountered.
 * Note that the addresses of the strings are hashed, not the
 * strings themselves.
 */

struct ba0_format
{
// the string
  char *text;
// an array of pointers towards the subformats of the string
  struct ba0_subformat **link;
// the number of subformats and the size of link
  ba0_int_p linknmb;
};


extern BA0_DLL void ba0_initialize_format (
    void);

extern BA0_DLL void ba0_define_format (
    char *,
    ba0_scanf_function *,
    ba0_printf_function *,
    ba0_garbage1_function *,
    ba0_garbage2_function *,
    ba0_copy_function *);

extern BA0_DLL void ba0_define_format_with_sizelt (
    char *,
    ba0_int_p,
    ba0_scanf_function *,
    ba0_printf_function *,
    ba0_garbage1_function *,
    ba0_garbage2_function *,
    ba0_copy_function *);

extern BA0_DLL struct ba0_format *ba0_get_format (
    char *);

extern BA0_DLL ba0_garbage1_function ba0_empty_garbage1;

extern BA0_DLL ba0_garbage2_function ba0_empty_garbage2;

struct ba0_pair
{
  char *identificateur;
  void *value;
};

struct ba0_tableof_pair
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_pair **tab;
};

END_C_DECLS
#endif /* !BA0_FORMAT_H */
#if !defined (BA0_GARBAGE_H)
#   define BA0_GARBAGE_H 1

/* #   include "ba0_common.h" */
/* #   include "ba0_stack.h" */
/* #   include "ba0_list.h" */
/* #   include "ba0_table.h" */
/* #   include "ba0_format.h" */

/* Garbage collector of J.-C. Faugere */

BEGIN_C_DECLS

/*
 * texinfo: ba0_gc_info
 * Structures of this data type are created by @code{ba0_garbage1_function}
 * and read by @code{ba0_garbage2_function} functions. They permit to
 * move data structures involving pointers.
 */

struct ba0_gc_info
{
// the index of the stack cell which contains the garbaged data structure
  ba0_int_p old_index_in_cells;
// the old address of the data structure
  void *old_addr;
  union
  {
// the size in bytes of the data structure (set at garbage1 pass)
    unsigned ba0_int_p size;
// the new address of the data structure (set at garbage2 pass)
    void *new_addr;
  } u;
// a readonly string describing the structure for debugging purposes
  char *text;
};


extern BA0_DLL void ba0_garbage (
    char *,
    struct ba0_mark *,
    ...);

extern BA0_DLL ba0_int_p ba0_garbage1 (
    char *,
    void *,
    enum ba0_garbage_code);

extern BA0_DLL void *ba0_garbage2 (
    char *,
    void *,
    enum ba0_garbage_code);

extern BA0_DLL ba0_int_p ba0_new_gc_info (
    void *,
    unsigned ba0_int_p,
    char *);

extern BA0_DLL void *ba0_new_addr_gc_info (
    void *,
    char *);

END_C_DECLS
#endif /* !BA0_GARBAGE_H */
#if !defined (BA0_COPY_H)
#   define BA0_COPY_H 1

/* #   include "ba0_common.h" */

BEGIN_C_DECLS

extern BA0_DLL void *ba0_copy (
    char *,
    void *);

END_C_DECLS
#endif /* !BA0_COPY_H */
#if !defined (BA0_SCANF_H)
#   define BA0_SCANF_H 1

/* #   include "ba0_common.h" */
/* #   include "ba0_format.h" */

BEGIN_C_DECLS

extern BA0_DLL void ba0__scanf__ (
    struct ba0_format *,
    void **,
    bool);

extern BA0_DLL void ba0_scanf (
    char *,
    ...);

extern BA0_DLL void ba0_scanf2 (
    char *,
    ...);

extern BA0_DLL void ba0_sscanf (
    char *,
    char *,
    ...);

extern BA0_DLL void ba0_sscanf2 (
    char *,
    char *,
    ...);

extern BA0_DLL void ba0_fscanf (
    FILE *,
    char *,
    ...);

extern BA0_DLL void ba0_fscanf2 (
    FILE *,
    char *,
    ...);

END_C_DECLS
#endif /* !BA0_SCANF_H */
#if !defined (BA0_PRINTF_H)
#   define BA0_PRINTF_H 1

/* #   include "ba0_common.h" */
/* #   include "ba0_format.h" */

BEGIN_C_DECLS

extern BA0_DLL void ba0__printf__ (
    struct ba0_format *,
    void **);

extern BA0_DLL void ba0_printf (
    char *,
    ...);

extern BA0_DLL void ba0_sprintf (
    char *,
    char *,
    ...);

extern BA0_DLL void ba0_fprintf (
    FILE *,
    char *,
    ...);

extern BA0_DLL char *ba0_new_printf (
    char *,
    ...);

END_C_DECLS
#endif /* !BA0_PRINTF_H */
#if !defined (BA0_SCANF_PRINTF_H)
#   define BA0_SCANF_PRINTF_H 1

/* #   include "ba0_common.h" */

BEGIN_C_DECLS

extern BA0_DLL void ba0_scanf_printf (
    char *,
    char *,
    ...);

END_C_DECLS
#endif /* !BA0_SCANF_PRINTF_H */
#if !defined (BA0_SMALL_P_H)
#   define BA0_SMALL_P_H 1

/* #   include "ba0_common.h" */

BEGIN_C_DECLS

extern BA0_DLL ba0_mint_hp ba0_largest_small_prime (
    void);

extern BA0_DLL ba0_mint_hp ba0_smallest_small_prime (
    void);

extern BA0_DLL ba0_mint_hp ba0_next_small_prime (
    ba0_mint_hp);

extern BA0_DLL ba0_mint_hp ba0_previous_small_prime (
    ba0_mint_hp);

END_C_DECLS
#endif /* !BA0_SMALL_P_H */
#if ! defined (BA0_MINT_HP_H)
#   define BA0_MINT_HP_H 1

/* #   include "ba0_common.h" */
/* #   include "ba0_gmp.h" */
/* #   include "ba0_macros_mint_hp.h" */
/* #   include "ba0_macros_mpq.h" */

BEGIN_C_DECLS

struct ba0_tableof_mint_hp
{
  ba0_int_p alloc;
  ba0_int_p size;
  ba0_int_p **tab;              /* not ba0_mint_hp ! */
};


struct ba0_listof_mint_hp
{
  ba0_int_p value;              /* not ba0_mint_hp ! */
  struct ba0_listof_mint_hp *next;
};


#   define ba0_mint_hp_module		ba0_global.mint_hp.module
#   define ba0_mint_hp_module_is_prime	ba0_global.mint_hp.module_is_prime

extern BA0_DLL void ba0_reset_mint_hp_module (
    void);

extern BA0_DLL bool ba0_domain_mint_hp (
    void);

extern BA0_DLL void ba0_mint_hp_module_set (
    ba0_mint_hp,
    bool);

extern BA0_DLL ba0_mint_hp ba0_pow_mint_hp (
    ba0_mint_hp,
    ba0_int_p);

extern BA0_DLL ba0_scanf_function ba0_scanf_mint_hp;

extern BA0_DLL ba0_printf_function ba0_printf_mint_hp;

extern BA0_DLL ba0_mint_hp ba0_invert_mint_hp (
    ba0_mint_hp);

extern BA0_DLL enum ba0_wang_code ba0_wang_mint_hp (
    ba0_mpq_t,
    ba0_mint_hp,
    ba0_int_hp *);

END_C_DECLS
#endif /* !BA0_MINT_HP_H */
#if !defined (BA0_MPZM_H)
#   define BA0_MPZM_H 1

/* #   include "ba0_common.h" */
/* #   include "ba0_macros_mpzm.h" */

BEGIN_C_DECLS

struct ba0_tableof_mpzm
{
  ba0_int_p alloc;
  ba0_int_p size;
  ba0__mpz_struct **tab;
};


struct ba0_listof_mpzm
{
  ba0__mpz_struct *value;
  struct ba0_listof_mpzm *next;
};


#   define ba0_mpzm_module_is_prime        ba0_global.mpzm.module_is_prime
#   define ba0_mpzm_module			ba0_global.mpzm.module
#   define ba0_mpzm_half_module		ba0_global.mpzm.half_module
#   define ba0_mpzm_accum			ba0_global.mpzm.accum

extern BA0_DLL void ba0_init_mpzm_module (
    void);

extern BA0_DLL void ba0_reset_mpzm_module (
    void);

extern BA0_DLL bool ba0_domain_mpzm (
    void);

extern BA0_DLL void ba0_mpzm_module_set_ui (
    unsigned ba0_int_p,
    bool);

extern BA0_DLL void ba0_mpzm_module_set (
    ba0_mpz_t,
    bool);

extern BA0_DLL void ba0_mpzm_module_mul (
    ba0_mpz_t);

extern BA0_DLL void ba0_mpzm_module_pow_ui (
    ba0_mpz_t,
    unsigned ba0_int_p,
    bool);

extern BA0_DLL ba0__mpz_struct *ba0_new_mpzm (
    void);

extern BA0_DLL ba0_scanf_function ba0_scanf_mpzm;

extern BA0_DLL ba0_printf_function ba0_printf_mpzm;

extern BA0_DLL ba0_garbage1_function ba0_garbage1_mpzm;

extern BA0_DLL ba0_garbage2_function ba0_garbage2_mpzm;

extern BA0_DLL ba0_copy_function ba0_copy_mpzm;

extern BA0_DLL enum ba0_wang_code ba0_wang_mpzm (
    ba0_mpq_t,
    ba0_mpz_t,
    ba0_mpz_t);

END_C_DECLS
#endif /* !BA0_MPZM_H */
#if !defined (BA0_INDEXED_STRING_H)
#   define BA0_INDEXED_STRING_H 1

/* #   include "ba0_common.h" */

/*
 * blad_indent: -l120
 */

BEGIN_C_DECLS

struct ba0_indexed_string;

struct ba0_indexed_string_indices;

struct ba0_tableof_indexed_string
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_indexed_string **tab;
};

struct ba0_tableof_indexed_string_indices
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_indexed_string_indices **tab;
};


/*
 * texinfo: ba0_indexed_string_indices
 * This data type is a subtype of @code{struct ba0_indexed_string}.
 * It permits to store @dfn{indexed string indices}.
 */

struct ba0_indexed_string_indices
{
// the opening and closing parenthesis
  char po, pf;
  struct ba0_tableof_indexed_string Tindex;
};


/*
 * texinfo: ba0_indexed_string
 * This data type permits to represent @dfn{indexed strings}
 * which are strings endowed with indexed string indices.
 * It is used for parsing symbols and variables.
 * Here are a few examples of indexed strings accepted by parsers:
 * @code{u}, @code{u[1]}, @code{u[[1],-4,[[3]]]}, @code{u[x[e]]}.
 * @verbatim
 * INDEXED ::= string INDICES ... INDICES              (*)
 *         ::= signed integer INDICES ... INDICES
 *         ::= INDICES ... INDICES
 *
 * INDICES ::= (INDEXED, ..., INDEXED)
 *         ::= [INDEXED, ..., INDEXED]
 *
 * (*) At top level, this form is the only one accepted.
 * @end verbatim
 */

struct ba0_indexed_string
{
// the string or the signed integer as a string or (char *)0
  char *string;
// the table of the indexed string indices
  struct ba0_tableof_indexed_string_indices Tindic;
};


typedef void ba0_indexed_string_function (
    struct ba0_indexed_string *);

extern BA0_DLL void ba0_init_indexed_string (
    struct ba0_indexed_string *);

extern BA0_DLL void ba0_reset_indexed_string (
    struct ba0_indexed_string *);

extern BA0_DLL struct ba0_indexed_string *ba0_new_indexed_string (
    void);

extern BA0_DLL void ba0_set_indexed_string (
    struct ba0_indexed_string *,
    struct ba0_indexed_string *);

extern BA0_DLL char *ba0_indexed_string_to_string (
    struct ba0_indexed_string *);

extern BA0_DLL char *ba0_stripped_indexed_string_to_string (
    struct ba0_indexed_string *);

extern BA0_DLL bool ba0_has_empty_trailing_indices_indexed_string (
    struct ba0_indexed_string *,
    char);

extern BA0_DLL bool ba0_has_trailing_indices_indexed_string (
    struct ba0_indexed_string *,
    bool (*)(char *));

extern BA0_DLL bool ba0_has_numeric_trailing_indices_indexed_string (
    struct ba0_indexed_string *,
    struct ba0_tableof_int_p *);

extern BA0_DLL ba0_garbage1_function ba0_garbage1_indexed_string;

extern BA0_DLL ba0_garbage2_function ba0_garbage2_indexed_string;

extern BA0_DLL ba0_copy_function ba0_copy_indexed_string;

extern BA0_DLL ba0_printf_function ba0_printf_indexed_string;

/* 
 * The first one returns the struct ba0_indexed_string* data structure
 * The second one converts the data structure into a string
 */

extern BA0_DLL ba0_scanf_function ba0_scanf_indexed_string;

extern BA0_DLL ba0_scanf_function ba0_scanf_indexed_string_as_a_string;

extern BA0_DLL struct ba0_indexed_string *ba0_scanf_indexed_string_with_counter (
    struct ba0_indexed_string *,
    ba0_int_p *);

END_C_DECLS
#endif /* !BA0_INDEXED_STRING_H */
#if !defined (BA0_RANGE_INDEXED_GROUP)
#   define BA0_RANGE_INDEXED_GROUP 1

/* #   include "ba0_common.h" */
/* #   include "ba0_double.h" */
/* #   include "ba0_string.h" */

BEGIN_C_DECLS

/*
 * texinfo: ba0_range_indexed_group
 * This data structure permits to describe a group of 
 * @dfn{range indexed strings}, which are strings indexed by integer numbers 
 * running over ranges. These strings (without their indices) are called
 * the @dfn{radicals} of the range indexed strings.
 * The arrays @code{lhs} and @code{rhs} have the same size, which
 * give the number of @dfn{range indices}.
 * Though stored in doubles, the left-hand and right-hand sides
 * of the ranges are either signed integers or @code{inf} or @code{-inf}.
 * The left-hand side of a range may be greater than, equal to or
 * lower than the right-hand side.
 * Here are a few examples: 
 * @verbatim
 * 1. y
 * 2. (x)[17:-3]
 * 3. (y,z)[0:inf,inf:-1]
 * @end verbatim
 * The radicals of the range indexed strings are @code{y}, @code{x}, 
 * @code{y} and @code{z}.
 * In Example 1, the range indexed group involves a single
 * range indexed string which has no range indices.
 * The range indexed group is said to describe a @dfn{plain string}.
 * In Example 2, the range indexed group involves a single
 * range indexed string which has a single range index.
 * In Example 3, the range indexed group involves two
 * range indexed strings; each of them admits two range indices.
 *
 * The aim of this data structure is to describe possibly infinite
 * ordered sets of variables. 
 * The range indexed group of Example 2
 * describes the ordered set: @code{x[17] > x[16] > ... > x[-2]} 
 * (the least index of the range is assumed to be excluded, as in Python,
 *  but this behaviour can be customized).
 * The variable @code{x[16]} is said to @dfn{fit} the range indexed string
 * @code{(x)[17:-3]}. The variables @code{x[18]} or @code{z[0]} do not.
 * In Example 3, the set of variables which fit the range indexed group is 
 * made of @code{y} and @code{z}, indexed by two nonnegative integers.
 */

struct ba0_range_indexed_group
{
// The left-hand sides of the ranges
  struct ba0_arrayof_double lhs;
// The right-hand sides of the ranges
  struct ba0_arrayof_double rhs;
// The table of the radicals of the range indexed strings
  struct ba0_tableof_string strs;
};

#   define BA0_NOT_A_RANGE_INDEXED_GROUP (struct ba0_range_indexed_group *)0

struct ba0_tableof_range_indexed_group
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_range_indexed_group **tab;
};

/*
 * Default values for entries in ba0_initialized_global
 */

#   define BA0_RANGE_INDEXED_GROUP_OPER ":"
#   define BA0_RANGE_INDEXED_GROUP_INFINITY "inf"

struct ba0_dictionary_string;

extern BA0_DLL void ba0_set_settings_range_indexed_group (
    char *,
    char *,
    bool,
    bool);

extern BA0_DLL void ba0_get_settings_range_indexed_group (
    char **,
    char **,
    bool *,
    bool *);

extern BA0_DLL unsigned ba0_int_p ba0_sizeof_range_indexed_group (
    struct ba0_range_indexed_group *,
    enum ba0_garbage_code,
    bool);

extern BA0_DLL unsigned ba0_int_p ba0_sizeof_tableof_range_indexed_group (
    struct ba0_tableof_range_indexed_group *,
    enum ba0_garbage_code,
    bool);

extern BA0_DLL void ba0_set_tableof_string_tableof_range_indexed_group (
    struct ba0_tableof_string *,
    struct ba0_tableof_range_indexed_group *);

extern BA0_DLL void ba0_set_range_indexed_group_with_tableof_string (
    struct ba0_range_indexed_group *,
    struct ba0_range_indexed_group *,
    struct ba0_dictionary_string *,
    struct ba0_tableof_string *);

extern BA0_DLL void ba0_set_tableof_range_indexed_group_with_tableof_string (
    struct ba0_tableof_range_indexed_group *,
    struct ba0_tableof_range_indexed_group *,
    struct ba0_dictionary_string *,
    struct ba0_tableof_string *);

extern BA0_DLL void ba0_init_range_indexed_group (
    struct ba0_range_indexed_group *);

extern BA0_DLL void ba0_reset_range_indexed_group (
    struct ba0_range_indexed_group *);

extern BA0_DLL struct ba0_range_indexed_group *ba0_new_range_indexed_group (
    void);

extern BA0_DLL void ba0_set_range_indexed_group (
    struct ba0_range_indexed_group *,
    struct ba0_range_indexed_group *);

extern BA0_DLL void ba0_set_range_indexed_group_string (
    struct ba0_range_indexed_group *,
    char *);

extern BA0_DLL bool ba0_is_plain_string_range_indexed_group (
    struct ba0_range_indexed_group *,
    char **);

extern BA0_DLL bool ba0_compatible_indices_range_indexed_group (
    struct ba0_range_indexed_group *,
    struct ba0_range_indexed_group *);

extern BA0_DLL bool ba0_fit_range_indexed_group (
    struct ba0_range_indexed_group *,
    char *,
    struct ba0_tableof_int_p *,
    ba0_int_p *);

extern BA0_DLL bool ba0_fit_indices_range_indexed_group (
    struct ba0_range_indexed_group *,
    struct ba0_tableof_int_p *);

extern BA0_DLL ba0_garbage1_function ba0_garbage1_range_indexed_group;

extern BA0_DLL ba0_garbage2_function ba0_garbage2_range_indexed_group;

extern BA0_DLL ba0_copy_function ba0_copy_range_indexed_group;

extern BA0_DLL ba0_scanf_function ba0_scanf_range_indexed_group;

extern BA0_DLL ba0_printf_function ba0_printf_range_indexed_group;

END_C_DECLS
#endif /* !BA0_RANGE_INDEXED_GROUP */
#if ! defined (BA0_GLOBAL_H)
#   define BA0_GLOBAL_H 1

/* #   include "ba0_common.h" */
/* #   include "ba0_exception.h" */
/* #   include "ba0_garbage.h" */
/* #   include "ba0_stack.h" */
/* #   include "ba0_format.h" */
/* #   include "ba0_basic_io.h" */
/* #   include "ba0_analex.h" */
/* #   include "ba0_gmp.h" */
/* #   include "ba0_point.h" */
/* #   include "ba0_range_indexed_group.h" */
/* #   include "ba0_dictionary_string.h" */

BEGIN_C_DECLS

/* 
 * texinfo: ba0_global
 * This data type is used for a single global variable.
 * Each field aims at customizing the behaviour of the @code{ba0} library.
 */

struct ba0_global
{
  struct
  {
/* 
 * Deprecated control for printing in LaTeX.
 * Used in ba0, bav and bap.
 */
    bool LaTeX;
/* 
 * Time out + Memory out + Interrupt checking
 *
 * time_limit           = the absolute value of the input time limit (restart)
 * memory_limit         = the input memory limit (restart)
 * switch_on_interrupt  = *check_interrupt should be called
 * within_interrupt     = bool to avoid self interruption
 * delay_interrupt      = the length of a time interval between two calls
 * before_timeout       = the overall remaining time before timeout
 * previous_time        = the value of time() when interrupt was last called
 */
    ba0_int_p time_limit;       /* local to ba0_common */
    ba0_int_p memory_limit;     /* local to ba0_common and ba0_stack */
    bool switch_on_interrupt;   /* local to ba0_common */
    bool within_interrupt;      /* local to ba0_common */
    time_t before_timeout;      /* local to ba0_common */
    time_t previous_time;       /* local to ba0_common */
  } common;
  struct
  {
/* 
 * The error/exception message.
 * Only set when raising an exception. Read everywhere.
 */
    char *raised;
    char mesg_cerr[BA0_BUFSIZE];
/* 
 * The stack of exception catching points.
 * Only set by the exception setting/raising MACROS.
 */
    struct
    {
      struct ba0_exception tab[BA0_SIZE_EXCEPTION_STACK];
      ba0_int_p size;
    } stack;
/* 
 * The stack of extra variables to be saved/restored when setting
 *      an exception point/raising an exception.
 * The field pointer points to the extra variable to be restored.
 * If the field restore is nonzero then it points to a function which is
 *      called in order to restore the extra variable with the value passed
 *      as a parameter.
 * The saved value is stored in a local variable at the catching point.
 */
    struct
    {
      struct
      {
        ba0_int_p *pointer;
        void (
            *restore) (
            ba0_int_p);
      } tab[BA0_SIZE_EXCEPTION_EXTRA_STACK];
      ba0_int_p size;
    } extra_stack;
/* 
 * bool to avoid self interruption
 */
    bool within_push_exception;
/*
 * A log fifo for debugging purposes
 * The entries of tab provide the sequence of file/line/exception raised
 *      since the last exception catching point was set.
 * The field qp contains the first free entry in tab
 */
    struct
    {
      struct
      {
        char *file;
        int line;
        char *raised;
      } tab[BA0_SIZE_EXCEPTION_LOG];
      ba0_int_p qp;
    } log;
  } exception;
  struct
  {
/* 
 * The garbage collector
 * tab                = an array for old->new addresses of areas
 * user_provided_mark = the mark M provided by garbage (format, M, ...)
 * ba0_current        = a running mark on struct ba0_gc_info(s)
 * old_free           = the value of the free pointer when garbage is called.
 *
 * All local to ba0_garbage. 
 * The values kept between two calls to ba0_garbage are meaningless.
 */
    struct ba0_gc_info **tab;
    struct ba0_mark user_provided_mark;
    struct ba0_mark current;
    struct ba0_mark old_free;
  } garbage;
  struct
  {
/* 
 * The predefined stacks. Used everywhere.
 */
    struct ba0_stack main;
    struct ba0_stack second;
    struct ba0_stack analex;
    struct ba0_stack quiet;
    struct ba0_stack format;
/* 
 * The current stack is the one on the top of stack_of_stacks.
 */
    struct ba0_tableof_stack stack_of_stacks;
/* 
 * For stats and debugging purposes.
 * Local to ba0_common, ba0_stack and ba0_analex.
 */
    ba0_int_p alloc_counter;
    ba0_int_p malloc_counter;
    ba0_int_p malloc_nbcalls;
  } stack;
  struct
  {
/* 
 * leaf_subformat = The formats defined by the library, such as %s, %d ...
 *                  Non-leaf formats are %t (tables) or %l (lists), .
 * htable         = The H-table of all the encountered formats.
 *                  Its size is a prime number. 
 * nbelem_htable  = The number of its elements.
 *
 * All are local to ba0_format.
 */
    struct ba0_tableof_pair leaf_subformat;
    struct ba0_tableof_pair htable;
    ba0_int_p nbelem_htable;
/* 
 * Management of the variables (scanf, printf) for the %value format.
 * Eventually, these pointers will point to bav_scanf_variable and
 * bav_printf_variable ... whenever these functions are defined (in bav).
 * Meanwhile, calling them raises BA0_ERRNYP
 */
    ba0_scanf_function *scanf_value_var;
    ba0_printf_function *printf_value_var;
  } format;
  struct
  {
/* 
 * output, input      = descriptions of the device in use.
 * output_line_length = to insert carriage returns. 
 *                      Reset by ba0_restart. Can be modified at runtime.
 *
 * All variables (except output_line_length) are local to ba0_basic_io.
 */
    struct ba0_output_device output_stack[BA0_BASIC_IO_SIZE_STACK];
    ba0_int_p output_sp;
    struct ba0_output_device output;
    ba0_int_p output_line_length;

    struct ba0_input_device input_stack[BA0_BASIC_IO_SIZE_STACK];
    ba0_int_p input_sp;
    struct ba0_input_device input;
  } basic_io;
  struct
  {
/* 
 * analex           = the FIFO of tokens
 * analex_save      = permits to record/restore analex (up to some point)
 * analex_save_full = indicates if analex_save is used
 * context          = an elaborated error message for parser errors
 *
 * subs_dict        = a pointer to a dictionary for performing token substitutions
 * subs_keys        = a pointer to the table which contains the dictionary keys
 * subs_vals        = a pointer to the table which contains the dictionary values
 */
    bool analex_save_full;
    struct ba0_analex_token_fifo analex;
    struct ba0_analex_token_fifo analex_save;

    char context[BA0_CONTEXT_LMAX];

    struct ba0_dictionary_string *subs_dict;
    struct ba0_tableof_string *subs_keys;
    struct ba0_tableof_string *subs_vals;
  } analex;
  struct
  {
/* 
 * These variables receive the values of the GMP memory functions before 
 * they get modified by BLAD.
 *
 * Set by ba0_restart. Read by ba0_terminate.
 * Set by ba0_process_check_interrupt before calling *check_interrupt
 * and restored afterwards.
 */
    bool alloc_function_called;
    void *(
        *alloc_function) (
        size_t);
    void *(
        *realloc_function) (
        void *,
        size_t,
        size_t);
    void (
        *free_function) (
        void *,
        size_t);
  } gmp;
  struct
  {
/* 
 * For computing in Z / module Z. Read everywhere.
 */
    bool module_is_prime;
    unsigned ba0_int_hp module;
  } mint_hp;
  struct
  {
/* 
 * For computing in Z / module Z with a GMP module. Read everywhere.
 */
    bool module_is_prime;
    ba0_mpz_t module;
    ba0_mpz_t half_module;
    ba0_mpz_t accum;
  } mpzm;
};

/*
 * texinfo: ba0_initialized_global
 * This data type is used by a single global variable.
 * It is decomposed into fields.
 * The values it contains permit to tune the library behaviour.
 */

struct ba0_initialized_global
{
  struct
  {
/* 
 * The only settings variable which is modified by ba0_restart/ba0_terminate.
 * Set by ba0_terminate. Read by all ba__restart functions.
 */
    enum ba0_restart_level restart_level;
/* 
 * check_interrupt = the pointer to the external check interrupt function,
 *                   called by ba0_process_check_interrupt.
 * delay_interrupt = the delay (in sec.) between two calls to *check_interrupt.
 * no_oot          = if true, ERRALR is disabled.
 */
    void (
        *check_interrupt) (
        void);
    time_t delay_interrupt;
    bool no_oot;
  } common;
  struct
  {
/* 
 * If true, the BLAD memory limit does not raise BA0_ERROOM.
 * Temporarily modified by all blad_restart functions.
 */
    bool no_oom;
  } malloc;
  struct
  {
    ba0_int_p sizeof_main_cell;
    ba0_int_p sizeof_quiet_cell;
    ba0_int_p sizeof_analex_cell;
    ba0_int_p nb_cells_per_stack;
    ba0_int_p sizeof_stack_of_stack;
/* 
 * Pointers to the functions that are called by BLAD for allocating/freeing
 * memory (mostly cells in stacks).
 */
    void *(
        *system_malloc) (
        size_t);
    void (
        *system_free) (
        void *);
  } stack;
  struct
  {
    ba0_set_memory_functions_function *set_memory_functions;
/*
 * If Integer_PFE is not (char *)0, every mpz_t z is printed Integer_PFE(z).
 * This mechanism prevents floating point evaluation of rational numbers
 *  in Python. Default value is (char *)0
 */
    char *Integer_PFE;
  } gmp;
  struct
  {
/* 
 * nb_tokens = the number of tokens in the analex FIFO
 * quotes    = a string containing the characters that can be used
 *              for quoting tokens
 */
    ba0_int_p nb_tokens;
    char *quotes;
  } analex;
  struct
  {
/*
 * The operator used for separating variable from values. Default "="
 */
    char *equal_sign;
  } value;
  struct
  {
/*
 * oper     = the range operator
 * infinity = the symbol for infinity
 * rhs_included = determines whether the right-hand side of range 
 *                indices should be included or not in the ranges
 * quote_PFE = if set to true, the range indexed groups which are not plain 
 *                strings are quoted when printed; this mechanism prevents 
 *                from evaluation failures in Python; default (char *)0
 */
    char *oper;
    char *infinity;
    bool rhs_included;
    bool quote_PFE;
  } range_indexed_group;
};

extern BA0_DLL struct ba0_global ba0_global;

extern BA0_DLL struct ba0_initialized_global ba0_initialized_global;

/*
 * texinfo: ba0_PFE_settings
 * This data structure is used to store copies of the settings variables
 * contained in the fields of @code{ba0_initialized_global} which
 * contain @code{PFE} variables.
 */

struct ba0_PFE_settings
{
  ba0_set_memory_functions_function *set_memory_functions;
  char *Integer_PFE;
  char *oper;
  char *infinity;
  bool rhs_included;
  bool quote_PFE;
};

END_C_DECLS
#endif /* !BA0_GLOBAL_H */
