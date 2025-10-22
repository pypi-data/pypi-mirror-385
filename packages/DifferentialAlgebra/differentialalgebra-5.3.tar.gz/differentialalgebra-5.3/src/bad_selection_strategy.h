#if ! defined (BAD_SELECTION_STRATEGY)
#   define BAD_SELECTION_STRATEGY 1

#   include "bad_common.h"

BEGIN_C_DECLS

/*
 * texinfo: bad_typeof_selection_strategy
 * This data type is used to specify a strategy, carried out by
 * differential elimination algorithm, in order to select the next
 * polynomial to process.
 */

enum bad_typeof_selection_strategy
{
// plain polynomials are preferred to polynomials arising from critical pairs
  bad_equation_first_selection_strategy,
// polynomials with lower leaders are preferred
  bad_lower_leader_first_selection_strategy
};

/*
 * texinfo: bad_selection_strategy
 * This data type specifies a strategy, carried out by
 * differential elimination algorithm, in order to select the next
 * polynomial to process.
 */

struct bad_selection_strategy
{
  enum bad_typeof_selection_strategy strategy;
// a penalty used to penalize some critical pairs
  ba0_int_p penalty;
};


extern BAD_DLL void bad_init_selection_strategy (
    struct bad_selection_strategy *);

extern BAD_DLL struct bad_selection_strategy *bad_new_selection_strategy (
    void);

extern BAD_DLL void bad_set_strategy_selection_strategy (
    struct bad_selection_strategy *,
    enum bad_typeof_selection_strategy);

extern BAD_DLL void bad_set_penalty_selection_strategy (
    struct bad_selection_strategy *,
    ba0_int_p);

extern BAD_DLL void bad_double_penalty_selection_strategy (
    struct bad_selection_strategy *);

END_C_DECLS
#endif
