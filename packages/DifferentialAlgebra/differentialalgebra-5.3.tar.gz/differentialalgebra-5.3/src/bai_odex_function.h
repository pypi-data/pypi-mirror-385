#if !defined (BAI_ODEX_FUNCTION_H)
#   define BAI_ODEX_FUNCTION_H 1

#   include "bai_common.h"

BEGIN_C_DECLS

/*
 * texinfo: bai_parameters
 * This data type associates floating point values to symbolic parameters.
 */

struct bai_parameters
{
// parameter values
  double *values;
// actually points to a struct bav_tableof_variable
// it is a copy of the field S->params of the differential system S
  void *names;
};

/*
 * texinfo: bai_command_function
 * This data type provides the signature of command functions.
 */

typedef double bai_command_function (
// the independent variable
    double t,
// actually points to a struct bai_params
    void *params);

/*
 * texinfo: bai_commands
 * This data type associates bai_command_function to symbolic function names.
 */

struct bai_commands
{
// the function pointers
  bai_command_function **fptrs;
// actually points to a struct bav_tableof_variable
// it is a copy of the field S->commands of the differential system S
  void *names;
};

/*
 * texinfo: bai_params
 * This data type describes the data structure passed as an extra argument
 * to the functions which need be evaluated by ODE integrators.
 */

struct bai_params
{
// the parameters
  struct bai_parameters pars;
// the commands
  struct bai_commands cmds;
// unused
  void *extra;
};

/* 
 * texinfo: bai_exit_code
 * This data type defines the possible exit codes for 
 * explicit ODE integrators.
 */

enum bai_exit_code
{
// compatible with the Gnu Scientific Library : GSL_SUCCESS = 0
  bai_odex_success = 0,
  bai_odex_non_finite = 1
};

END_C_DECLS
#endif /* !BAI_ODEX_FUNCTION_H */
