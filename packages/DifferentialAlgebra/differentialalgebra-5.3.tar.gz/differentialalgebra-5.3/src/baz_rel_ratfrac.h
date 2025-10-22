#if ! defined (BAZ_REL_RATFRAC_H)
#   define BAZ_REL_RATFRAC_H 1

#   include "baz_ratfrac.h"

BEGIN_C_DECLS

/*
 * texinfo: baz_typeof_relop
 * This data type provides an encoding for relational operators.
 */

enum baz_typeof_relop
{
  baz_none_relop,
  baz_equal_relop,
  baz_not_equal_relop,
  baz_greater_relop,
  baz_greater_or_equal_relop,
  baz_less_relop,
  baz_less_or_equal_relop
};

/*
 * texinfo: baz_rel_ratfrac
 * This data type implements a pair of rational fractions connected
 * by a relational operator.
 */

struct baz_rel_ratfrac
{
  struct baz_ratfrac lhs;
  struct baz_ratfrac rhs;
  enum baz_typeof_relop op;
};


struct baz_tableof_rel_ratfrac
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct baz_rel_ratfrac **tab;
};


extern BAZ_DLL void baz_init_rel_ratfrac (
    struct baz_rel_ratfrac *);

extern BAZ_DLL struct baz_rel_ratfrac *baz_new_rel_ratfrac (
    void);

extern BAZ_DLL void baz_set_rel_ratfrac (
    struct baz_rel_ratfrac *,
    struct baz_rel_ratfrac *);

extern BAZ_DLL void baz_set_ratfrac_rel_ratfrac (
    struct baz_ratfrac *,
    struct baz_rel_ratfrac *);

extern BAZ_DLL ba0_scanf_function baz_scanf_rel_ratfrac;

extern BAZ_DLL ba0_printf_function baz_printf_rel_ratfrac;

extern BAZ_DLL ba0_garbage1_function baz_garbage1_rel_ratfrac;

extern BAZ_DLL ba0_garbage2_function baz_garbage2_rel_ratfrac;

extern BAZ_DLL ba0_copy_function baz_copy_rel_ratfrac;

END_C_DECLS
#endif /*!BAZ_REL_RATFRAC_H */
