#if !defined (BA0_DOUBLE_H)
#   define BA0_DOUBLE_H 1

#   include "ba0_common.h"

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
