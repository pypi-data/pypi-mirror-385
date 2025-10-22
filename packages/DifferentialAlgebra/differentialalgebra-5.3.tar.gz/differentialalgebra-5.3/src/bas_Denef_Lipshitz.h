#if ! defined (BAS_DENEF_LIPSHITZ_H)
#   define BAS_DENEF_LIPSHITZ_H 1

#   include "bas_DLuple.h"
#   include "bas_DL_tree.h"

BEGIN_C_DECLS

extern BAS_DLL void bas_prolongate_DLuple (
    struct bas_DLuple *,
    struct bas_DLuple *,
    struct bav_tableof_variable *);

extern BAS_DLL void bas_Denef_Lipshitz_resume (
    struct bas_tableof_DLuple *,
    struct bas_DLuple *,
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_polynom_mpz *);

extern BAS_DLL ba0_int_p bas_Denef_Lipshitz_leaf (
    struct bas_tableof_DLuple *,
    struct bas_DL_tree *,
    ba0_int_p,
    struct bas_Yuple *,
    struct bad_regchain *,
    struct bad_base_field *);

extern BAS_DLL ba0_int_p bas_Denef_Lipshitz_aux (
    struct bas_tableof_DLuple *,
    struct bas_DL_tree *,
    ba0_int_p,
    struct bas_Yuple *,
    struct bad_intersectof_regchain *,
    struct bad_splitting_tree *,
    ba0_int_p,
    struct bad_base_field *);

extern BAS_DLL void bas_Denef_Lipshitz (
    struct bas_tableof_DLuple *,
    struct bas_DL_tree *,
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_polynom_mpz *,
    struct ba0_tableof_string *,
    struct bav_tableof_symbol *,
    struct baz_prolongation_pattern *,
    struct bav_variable *,
    struct bav_symbol *);

END_C_DECLS
#endif /* !BAS_DENEF_LIPSHITZ_H */
