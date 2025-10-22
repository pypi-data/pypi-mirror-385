#if !defined (BAD_QUADRUPLE_H)
#   define BAD_QUADRUPLE_H 1

#   include "bad_common.h"
#   include "bad_regchain.h"
#   include "bad_intersectof_regchain.h"
#   include "bad_selection_strategy.h"
#   include "bad_critical_pair.h"
#   include "bad_base_field.h"

BEGIN_C_DECLS

/* 
 * texinfo: bad_quadruple
 * This data type implements quadruples 
 *      @math{G = \langle A,\, D,\, P,\, S \rangle},
 * which are processed by the RosenfeldGroebner algorithm.
 *
 * The field @code{A} contains a regular differential chain.
 *
 * The field @code{D} contains the list of the critical pairs
 * to be processed.
 *
 * The field @code{P} contains the list of the differential polynomials
 * to be processed.
 *
 * The field @code{S} contains a list of inequations.
 *
 * Quadruples are identified in splitting trees by a @emph{number}
 * which is held by the @code{number} field of @code{A}.
 *
 * The RosenfeldGroebner algorithm starts with
 *      @math{G = \langle \emptyset,\, \emptyset,\, P_0,\, S_0 \rangle}
 * where @math{P_0} and @math{S_0} are the input lists of equations 
 * and inequations. It computes a finite set of quadruples containing
 * regular systems i.e. of the form
 *      @math{G = \langle A,\, \emptyset,\, \emptyset,\, S \rangle}
 * and @var{S} partially reduced with respect to @var{A}.
 * These regular systems are then processed by the regCharacteristic
 * algorithm to produce a finite set of regular differential chains.
 */

struct bad_quadruple
{
// the (somehow) already processed differential polynomials
  struct bad_regchain A;
// the list of critical pairs waiting to be processed
  struct bad_listof_critical_pair *D;
// the list of differential polynomials waiting to be processed
  struct bap_listof_polynom_mpz *P;
// the list of inequations (different from zero) 
  struct bap_listof_polynom_mpz *S;
};

struct bad_tableof_quadruple
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bad_quadruple **tab;
};

struct bad_listof_quadruple
{
  struct bad_quadruple *value;
  struct bad_listof_quadruple *next;
};

struct bad_splitting_tree;

extern BAD_DLL void bad_init_quadruple (
    struct bad_quadruple *);

extern BAD_DLL struct bad_quadruple *bad_new_quadruple (
    void);

extern BAD_DLL void bad_set_number_quadruple (
    struct bad_quadruple *,
    ba0_int_p);

extern BAD_DLL void bad_set_next_number_quadruple (
    struct bad_quadruple *,
    struct bad_splitting_tree *);

extern BAD_DLL ba0_int_p bad_get_number_quadruple (
    struct bad_quadruple *);

extern BAD_DLL void bad_set_quadruple (
    struct bad_quadruple *,
    struct bad_quadruple *);

extern BAD_DLL void bad_mark_indets_quadruple (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bad_quadruple *);

extern BAD_DLL void bad_extend_quadruple_regchain (
    struct bad_quadruple *,
    struct bad_regchain *,
    struct bad_base_field *);

extern BAD_DLL void bad_insert_in_P_quadruple (
    struct bad_quadruple *,
    struct bad_quadruple *,
    struct bap_polynom_mpz *);

extern BAD_DLL void bad_insert_in_S_quadruple (
    struct bad_quadruple *,
    struct bad_quadruple *,
    struct bap_polynom_mpz *);

extern BAD_DLL struct bap_listof_polynom_mpz *bad_insert_in_listof_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_listof_polynom_mpz *);

extern BAD_DLL struct bap_listof_polynom_mpz *bad_delete_from_listof_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_listof_polynom_mpz *,
    bool *);

extern BAD_DLL void bad_preprocess_equation_quadruple (
    struct bap_product_mpz *,
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_product_mpz *,
    bool *,
    struct bad_quadruple *,
    struct bad_base_field *);

extern BAD_DLL void bad_report_simplification_of_inequations_quadruple (
    struct bad_tableof_quadruple *,
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_product_mpz *);

extern BAD_DLL void bad_split_on_factors_of_equations_quadruple (
    struct bad_tableof_quadruple *,
    struct bad_splitting_tree *,
    struct bap_product_mpz *,
    struct ba0_tableof_bool *,
    struct bap_polynom_mpz *);

extern BAD_DLL bool bad_simplify_and_store_in_P_quadruple (
    struct bad_quadruple *,
    bool *,
    struct bap_polynom_mpz *,
    struct bad_base_field *);

extern BAD_DLL bool bad_simplify_and_store_in_S_quadruple (
    struct bad_quadruple *,
    bool *,
    struct bap_polynom_mpz *,
    struct bad_base_field *);

extern BAD_DLL void bad_pick_and_remove_quadruple (
    struct bap_polynom_mpz *,
    struct bad_quadruple *,
    struct bad_critical_pair **,
    struct bad_selection_strategy *);

extern BAD_DLL void bad_reg_characteristic_quadruple (
    struct bad_intersectof_regchain *,
    struct bad_quadruple *,
    struct bad_regchain *,
    struct bad_base_field *);

extern BAD_DLL void bad_complete_quadruple (
    struct bad_tableof_quadruple *,
    struct bav_tableof_term *,
    bool *,
    struct bad_splitting_tree *,
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    struct bad_base_field *,
    struct bad_selection_strategy *);

extern BAD_DLL ba0_scanf_function bad_scanf_quadruple;

extern BAD_DLL ba0_printf_function bad_printf_quadruple;

extern BAD_DLL ba0_garbage1_function bad_garbage1_quadruple;

extern BAD_DLL ba0_garbage2_function bad_garbage2_quadruple;

extern BAD_DLL ba0_copy_function bad_copy_quadruple;

END_C_DECLS
#endif /* !BAD_QUADRUPLE_H */
