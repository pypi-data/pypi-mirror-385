#if !defined (BMI_OPTIONS)
#   define BMI_OPTIONS 1

#   include "bmi_callback.h"

BEGIN_C_DECLS

/*
 * Here is an example of a call to bmi_blad_eval.
 *
 * arguments := "NormalForm" (convert (leqns, string), drideal)
 * arguments := arguments,
 *             ToBMIOptionSequence
 *             		(innot, outnot, _TIMEOUT_, _MEMOUT_, _CELLSZ_);
 * result := BMIBladEval (arguments);
 *
 * When bmi_blad_eval is called from MAPLE, the first argument
 * provides the exported function to be called with its arguments.
 *
 * The other arguments are the options, set by ToBMIOptionSequence.
 *
 * This module processes the options.
 *
 * Options are expected in the following order:
 * input notation, output notation, time limit, memory limit, cell size
 *
 * The boolean returned by many function indicates a success (if true) or
 * a failure (if false). Exceptions cannot be raised at this stage.
 */

enum bmi_typeof_notation
{
  bmi_jet_notation,
  bmi_tjet_notation,
  bmi_jet0_notation,
  bmi_diff_notation,
  bmi_udif_notation,
  bmi_D_notation,
  bmi_Derivative_notation
};

struct bmi_options
{
  enum bmi_typeof_notation input_notation;
  enum bmi_typeof_notation output_notation;
  long time_limit;
  long memory_limit;
  char cellsize[32];
};

extern void bmi_init_options (
    struct bmi_options *);

extern void bmi_clear_options (
    struct bmi_options *);

extern bool bmi_set_options (
    struct bmi_options *,
    struct bmi_callback *,
    ALGEB *,
    long);

END_C_DECLS
#endif /*! BMI_OPTIONS */
