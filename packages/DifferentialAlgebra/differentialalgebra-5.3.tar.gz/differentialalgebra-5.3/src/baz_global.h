#if ! defined (BAZ_GLOBAL_H)
#   define BAZ_GLOBAL_H 1

#   include "baz_common.h"

BEGIN_C_DECLS

struct baz_initialized_global
{
  struct
  {
/*
 * If nonzero, the lhs of prolongation patterns are quoted using
 * its first character
 */
    char *lhs_quotes;
  } prolongation_pattern;
};

extern BAZ_DLL struct baz_initialized_global baz_initialized_global;

END_C_DECLS
#endif /* !BAZ_GLOBAL_H */
