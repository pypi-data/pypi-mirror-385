#if !defined (BAD_STATS_H)
#   define BAD_STATS_H 1

#   include "bad_common.h"

BEGIN_C_DECLS

extern BAD_DLL void bad_init_stats (
    void);

extern BAD_DLL ba0_printf_function bad_printf_stats;

END_C_DECLS
#endif /* ! BAD_STATS_H */
