#if !defined (BAD_GLOBAL_H)
#   define BAD_GLOBAL_H 1

#   include "bad_common.h"
#   include "bad_reduction.h"
#   include "bad_regularize.h"
#   include "bad_low_power_theorem.h"

BEGIN_C_DECLS

struct bad_global
{
  struct
  {
/* 
 * Local variable to bad_reduction.
 * Used to pass some extra information to a subfunction in
 * bad_random_eval_variables_under_the_stairs
 * Its value is meaningless between two calls to this function.
 */
    struct bav_tableof_variable *stairs;
  } reduction;
  struct
  {
/* 
 * Statistical information set by bad_Rosenfeld_Groebner and bad_pardi
 */
    time_t begin;
    time_t end;
    ba0_int_p critical_pairs_processed;
    ba0_int_p reductions_to_zero;
  } stats;
};

struct bad_initialized_global
{
  struct
  {
/* 
 * reduction_strategy = the type of reduction strategy applied
 * redzero_strategy   = the type of reduction test to zero applied
 * number_of_redzero_tries = tuning for probabilistic methods
 * Local to bad_reduction.
 */
    enum bad_typeof_reduction_strategy reduction_strategy;
    enum bad_typeof_redzero_strategy redzero_strategy;
    ba0_int_p number_of_redzero_tries;
  } reduction;
  struct
  {
/* 
 * strategy = the type of regularization strategy applied
 * Local to bad_regularize.
 */
    enum bad_typeof_regularize_strategy strategy;
  } regularize;
  struct
  {
/*
 * The string used for denoting differential regular chain elements
 * in the context of preparation equations (cf. Low Power Theorem).
 */
    char *zstring;
  } preparation;
};

extern BAD_DLL struct bad_global bad_global;

extern BAD_DLL struct bad_initialized_global bad_initialized_global;

END_C_DECLS
#endif /* !BAD_GLOBAL_H */
