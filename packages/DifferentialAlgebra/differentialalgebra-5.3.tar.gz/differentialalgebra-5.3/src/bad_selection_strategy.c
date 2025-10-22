#include "bad_selection_strategy.h"

/*
 * texinfo: bad_init_selection_strategy
 * Initialize @var{S} with @code{strategy} equal to
 * @code{bad_lower_leader_first_selection_strategy} and @code{penalty}
 * equal to @math{2}.
 */

BAD_DLL void
bad_init_selection_strategy (
    struct bad_selection_strategy *S)
{
  S->strategy = bad_lower_leader_first_selection_strategy;
  S->penalty = 2;
}

/*
 * texinfo: bad_new_selection_strategy
 * Allocate a new @code{struct bad_selection_strategy}, initialize
 * it and return it.
 */

BAD_DLL struct bad_selection_strategy *
bad_new_selection_strategy (
    void)
{
  struct bad_selection_strategy *S;

  S = (struct bad_selection_strategy *) ba0_alloc (sizeof (struct
          bad_selection_strategy));
  bad_init_selection_strategy (S);
  return S;
}

/*
 * texinfo: bad_set_strategy_selection_strategy
 * Set the field @code{strategy} of @var{S} to @var{strategy}.
 */

BAD_DLL void
bad_set_strategy_selection_strategy (
    struct bad_selection_strategy *S,
    enum bad_typeof_selection_strategy strategy)
{
  S->strategy = strategy;
}

/*
 * texinfo: bad_set_penalty_selection_strategy
 * Set the field @code{penalty} of @var{S} to @var{penalty}.
 */

BAD_DLL void
bad_set_penalty_selection_strategy (
    struct bad_selection_strategy *S,
    ba0_int_p penalty)
{
  S->penalty = penalty;
}

/*
 * texinfo: bad_double_penalty_selection_strategy
 * Double the value of the field @code{penalty} of @var{S}, unless an
 * overflow occurs.
 */

BAD_DLL void
bad_double_penalty_selection_strategy (
    struct bad_selection_strategy *S)
{
  if (2 * S->penalty > 0)
    S->penalty *= 2;
}
