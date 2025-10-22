#if !defined (BAI_ODEX_H)
#   define BAI_ODEX_H 1

#   include "bai_common.h"

BEGIN_C_DECLS

/*
 * texinfo: bai_odex_system
 * This data type permits to implement an explicit parametric
 * ordinary differential system, possibly with commands.
 */

struct bai_odex_system
{
// the independent variable
  struct bav_variable *t;
// the left hand sides of the differential equations
  struct bav_tableof_variable lhs;
// the right hand sides
  struct baz_tableof_ratfrac rhs;
// the parameters
  struct bav_tableof_variable params;
// the commands
  struct bav_tableof_variable commands;
};


extern BAI_DLL void bai_init_odex_system (
    struct bai_odex_system *);

extern BAI_DLL void bai_reset_odex_system (
    struct bai_odex_system *);

extern BAI_DLL struct bai_odex_system *bai_new_odex_system (
    void);

extern BAI_DLL void bai_set_odex_system (
    struct bai_odex_system *,
    struct bai_odex_system *);

extern BAI_DLL void bai_set_odex_system_tables (
    struct bai_odex_system *,
    struct bav_variable *,
    struct bav_tableof_variable *,
    struct bav_tableof_variable *,
    struct bav_tableof_variable *,
    struct baz_tableof_ratfrac *);

extern BAI_DLL void bai_set_odex_system_regchain (
    struct bai_odex_system *,
    struct bav_variable *,
    struct bav_tableof_variable *,
    struct bav_tableof_variable *,
    struct bav_tableof_variable *,
    struct bad_regchain *);

extern BAI_DLL bool bai_odex_is_lhs (
    struct bav_variable *,
    struct bai_odex_system *,
    ba0_int_p *);

extern BAI_DLL ba0_scanf_function bai_scanf_odex_system;

extern BAI_DLL ba0_printf_function bai_printf_odex_system;

extern BAI_DLL ba0_garbage1_function bai_garbage1_odex_system;

extern BAI_DLL ba0_garbage2_function bai_garbage2_odex_system;

extern BAI_DLL ba0_copy_function bai_copy_odex_system;

extern BAI_DLL void bai_odex_generate_rhs_C_code (
    FILE *,
    char *,
    struct bai_odex_system *);

extern BAI_DLL void bai_odex_generate_jacobianof_rhs_C_code (
    FILE *,
    char *,
    struct bai_odex_system *);

END_C_DECLS
#endif /* !BAI_ODEX_H */
