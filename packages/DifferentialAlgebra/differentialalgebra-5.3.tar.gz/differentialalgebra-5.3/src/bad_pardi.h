#if !defined (BAD_PARDI_H)
#   define BAD_PARDI_H 1

#   include "bad_common.h"
#   include "bad_regchain.h"

BEGIN_C_DECLS

extern BAD_DLL void bad_pardi (
    struct bad_regchain *,
    bav_Iordering,
    struct bad_regchain *);

END_C_DECLS
#endif /* !BAD_PARDI_H */
