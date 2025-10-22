#if !defined (BA0_INT_P)
#   define BA0_INT_P 1

#   include "ba0_common.h"

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
