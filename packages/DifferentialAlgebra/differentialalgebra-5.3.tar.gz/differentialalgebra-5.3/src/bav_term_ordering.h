#if !defined (BAV_TERM_ORDERING_H)
#   define BAV_TERM_ORDERING_H 1

#   include "bav_term.h"

BEGIN_C_DECLS

extern BAV_DLL enum ba0_compare_code bav_compare_term (
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL enum ba0_compare_code bav_compare_stripped_term (
    struct bav_term *,
    struct bav_term *,
    bav_Inumber);

extern BAV_DLL void bav_set_term_ordering (
    char *);

END_C_DECLS
#endif /* !BAV_TERM_ORDERING_H */
