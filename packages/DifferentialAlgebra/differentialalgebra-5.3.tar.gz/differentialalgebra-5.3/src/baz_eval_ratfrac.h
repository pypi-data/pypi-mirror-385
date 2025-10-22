#if !defined (BAZ_EVAL_RATFRAC_H)
#   define BAZ_EVAL_RATFRAC_H

#   include "baz_ratfrac.h"

BEGIN_C_DECLS

extern BAZ_DLL void baz_eval_to_polynom_at_point_int_p_ratfrac (
    struct bap_polynom_mpq *,
    struct baz_ratfrac *,
    struct bav_point_int_p *);

extern BAZ_DLL void baz_eval_to_ratfrac_at_point_ratfrac_ratfrac (
    struct baz_ratfrac *,
    struct baz_ratfrac *,
    struct baz_point_ratfrac *);

extern BAZ_DLL void baz_evaluate_to_ratfrac_at_point_ratfrac_ratfrac (
    struct baz_ratfrac *,
    struct baz_ratfrac *,
    struct baz_point_ratfrac *);

extern BAZ_DLL void baz_twice_evaluate_to_ratfrac_at_point_ratfrac_ratfrac (
    struct baz_ratfrac *,
    struct baz_ratfrac *,
    struct baz_point_ratfrac *,
    struct baz_point_ratfrac *);

END_C_DECLS
#endif /* !BAZ_EVAL_RATFRAC_H */
