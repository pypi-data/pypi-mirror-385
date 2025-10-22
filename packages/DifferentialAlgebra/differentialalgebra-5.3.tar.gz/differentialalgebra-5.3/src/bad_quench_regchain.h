#if !defined (BAD_QUENCH_REGCHAIN_H)
#   define BAD_QUENCH_REGCHAIN_H 1

#   include "bad_common.h"
#   include "bad_attchain.h"
#   include "bad_regchain.h"
#   include "bad_quench_map.h"

BEGIN_C_DECLS

struct bad_base_field;
struct bad_intersectof_regchain;

extern BAD_DLL void bad_quench_regchain (
    struct bad_regchain *,
    struct bad_quench_map *,
    struct bav_tableof_term *,
    bool *,
    struct bad_regchain *,
    struct bad_base_field *,
    struct bap_polynom_mpz **);

extern BAD_DLL void bad_quench_and_handle_exceptions_regchain (
    struct bad_intersectof_regchain *,
    struct bad_quench_map *,
    struct bav_tableof_term *,
    bool *,
    struct bad_regchain *,
    struct bad_base_field *);

extern BAD_DLL void bad_handle_splitting_exceptions_regchain (
    struct bad_intersectof_regchain *,
    struct bad_quench_map *,
    struct bav_tableof_term *,
    bool *,
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    char *,
    struct bad_base_field *);

END_C_DECLS
#endif /* !BAD_QUENCH_REGCHAIN_H */
