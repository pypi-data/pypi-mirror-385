#if !defined (BAI_GLOBAL_H)
#   define BAI_GLOBAL_H 1

#   include "bai_common.h"
#   include "bai_odex.h"

BEGIN_C_DECLS

struct bai_global
{
  struct
  {
/* 
 * Points to the ODEX system being considered.
 * Local to bai_odex.
 * Meaningless value between two calls.
 */
    struct bai_odex_system *system;
  } odex;
};

extern BAI_DLL struct bai_global bai_global;

END_C_DECLS
#endif /* !BAI_GLOBAL_H */
