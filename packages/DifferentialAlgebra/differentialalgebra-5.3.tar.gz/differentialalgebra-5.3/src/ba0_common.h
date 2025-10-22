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

#   include "ba0_config.h"

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
