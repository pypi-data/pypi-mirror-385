#if ! defined (BAS_DLUPLE_H)
#   define BAS_DLUPLE_H 1

#   include "bas_Yuple.h"
#   include "bas_Zuple.h"

BEGIN_C_DECLS

/*
 * texinfo: bas_DLuple
 * This data structure is used to store the output of the
 * Denef Lipshitz algorithm. Its fields are copies of
 * the corresponding fields of a @code{struct bas_Yuple} and
 * a @code{struct bas_Zuple} produced by the 
 * @code{bas_Denef_Lipshitz_leaf} function.
 */

struct bas_DLuple
{
  struct bav_tableof_symbol Y;
  struct baz_prolongation_pattern Ybar;
  struct bav_symbol *x;
  struct ba0_tableof_int_p order;
  struct ba0_tableof_int_p kappa;
  struct bad_regchain C;
  struct bap_listof_polynom_mpz *S;
  struct ba0_tableof_int_p k;
  struct ba0_tableof_int_p r;
  struct bav_variable *q;
  struct baz_tableof_ratfrac A;
  struct ba0_tableof_int_p gamma;
  struct ba0_tableof_int_p mu;
  struct ba0_tableof_int_p sigma;
  struct ba0_tableof_int_p beta;
  struct ba0_tableof_int_p delta;
};

struct bas_tableof_DLuple
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bas_DLuple **tab;
};

extern BAS_DLL void bas_init_DLuple (
    struct bas_DLuple *);

extern BAS_DLL struct bas_DLuple *bas_new_DLuple (
    void);

extern BAS_DLL void bas_set_DLuple (
    struct bas_DLuple *,
    struct bas_DLuple *);

extern BAS_DLL void bas_set_YZuple_DLuple (
    struct bas_DLuple *,
    struct bas_Yuple *,
    struct bas_Zuple *);

extern BAS_DLL unsigned ba0_int_p bas_sizeof_DLuple (
    struct bas_DLuple *,
    enum ba0_garbage_code);

extern BAS_DLL void bas_switch_ring_DLuple (
    struct bas_DLuple *,
    struct bav_differential_ring *);

extern BAS_DLL void bas_constant_variables_DLuple (
    struct ba0_tableof_int_p *,
    struct bav_tableof_variable *,
    struct bas_DLuple *);

extern BAS_DLL void bas_series_coefficients_DLuple (
    struct baz_tableof_tableof_ratfrac *,
    struct bas_DLuple *);

extern BAS_DLL ba0_scanf_function bas_scanf_DLuple;

extern BAS_DLL ba0_printf_function bas_printf_DLuple;

extern BAS_DLL ba0_printf_function bas_printf_stripped_DLuple;

extern BAS_DLL ba0_garbage1_function bas_garbage1_DLuple;

extern BAS_DLL ba0_garbage2_function bas_garbage2_DLuple;

extern BAS_DLL ba0_copy_function bas_copy_DLuple;

END_C_DECLS
#endif /* !BAS_DL_UPLE_H */
