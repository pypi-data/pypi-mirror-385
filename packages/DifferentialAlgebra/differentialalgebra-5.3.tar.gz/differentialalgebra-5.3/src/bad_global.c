#include "bad_global.h"

BAD_DLL struct bad_global bad_global;

BAD_DLL struct bad_initialized_global bad_initialized_global = {
  {bad_gcd_prem_and_factor_reduction_strategy,
        bad_deterministic_using_probabilistic_redzero_strategy,
      2},
  {bad_subresultant_regularize_strategy},
  {BAD_ZSTRING}
};
