#if !defined (BAP_INVERT_mpq_H)
#   define BAP_INVERT_mpq_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpq.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpq

extern BAP_DLL void bap_numeric_initial_one_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_Euclidean_division_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_Euclid_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_extended_Euclid_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

#   undef BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP_INVERT_mpq_H */
