#if ! defined (BA0_GMP_H)
#   define BA0_GMP_H 1

#   include "ba0_common.h"

#   if defined (BA0_USE_GMP)
#      include <gmp.h>
#   else
#      include "mini-gmp.h"
#      include "mini-mpq.h"
#   endif

#   include "ba0_macros_mpz.h"
#   include "ba0_macros_mpq.h"

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
