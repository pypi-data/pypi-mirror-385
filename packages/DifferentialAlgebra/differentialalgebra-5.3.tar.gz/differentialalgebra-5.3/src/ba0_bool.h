#if !defined (BA0_BOOL)
#   define BA0_BOOL 1

#   include "ba0_common.h"

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
