#if !defined (BAV_POINT_H)
#   define BAV_POINT_H

#   include "bav_common.h"

BEGIN_C_DECLS

extern BAV_DLL bool bav_is_differentially_ambiguous_point (
    struct ba0_point *);

extern BAV_DLL void bav_delete_independent_values_point (
    struct ba0_point *,
    struct ba0_point *);

END_C_DECLS
#endif /* !BAV_POINT */
