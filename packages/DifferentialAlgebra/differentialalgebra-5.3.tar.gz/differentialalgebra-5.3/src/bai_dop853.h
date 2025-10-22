#if !defined (BAI_DOP853_H)
#   define BAI_DOP853_H 1

/**********************************************************************
   Adaptation of the FORTRAN code provided by Ernst Hairer for DOP853.
   Page numbers refer to 

   Solving Ordinary Differential Equations I
   Ernst Hairer, Syvert Norsett, Gerhard Wanner
   Springer Verlag
   Second Revised Edition

   The Runge-Kutta method has order 8.
   There are two different embedded methods of respective orders 5 and 3
   in order to increase stability w.r.t. the "basic" 8(6) method. See page 254.

   The dense output method has order 7. See page 194.

   ODE y'(t) = f (t, y(t))

   The signature of the functions to be integrated.
   t = the independent variable
   y = the current value of the dependent variables y(t)
   f = the values to be computed f (t, y(t))
   params = whatever you want as extra parameters to provide to the function

   The function returns 0 on success and any nonzero value on failure.
 **********************************************************************/

#   include "bai_common.h"
#   include "bai_odex.h"
#   include "bai_odex_integrated_function.h"

/**********************************************************************
 INITIAL VALUES

 There should be one y0 [i] per dependent variable.
 The ODE is integrated from t0 to t1. t0 > t1 is allowed.
 **********************************************************************/

BEGIN_C_DECLS

/*
 * texinfo: bai_dop853_initial_values
 * This data type permits to specify initial values for the DOP853
 * explicit ODE integrator.
 */

struct bai_dop853_initial_values
{
// starting value for the independent variable
  double t0;
// ending value
  double t1;
// initial values for the dependent variables
  struct ba0_arrayof_double y0;
};


extern BAI_DLL void bai_dop853_init_initial_values (
    struct bai_dop853_initial_values *);

extern BAI_DLL void bai_dop853_reset_initial_values (
    struct bai_dop853_initial_values *);

extern BAI_DLL struct bai_dop853_initial_values *bai_dop853_new_initial_values (
    void);

extern BAI_DLL void bai_dop853_realloc_initial_values (
    struct bai_dop853_initial_values *,
    ba0_int_p);

extern BAI_DLL void bai_dop853_set_initial_values_time (
    struct bai_dop853_initial_values *,
    double,
    double);

extern BAI_DLL void bai_dop853_set_initial_values_variable (
    struct bai_dop853_initial_values *,
    struct bav_variable *,
    struct bai_odex_system *,
    double);

extern BAI_DLL void bai_dop853_set_initial_values (
    struct bai_dop853_initial_values *,
    struct bai_dop853_initial_values *);

/**********************************************************************
   CONTROL
   Some default values can be provided using the initial values 

   uround = 2.3e-16
   safe_fac = 0.9
   fac1 = 1./3.
   fac2 = 6.
   beta = 0.
   hmax = |t1 - t0|
   h0 = determined by computation
   nb_max_steps = 100000
   stiffness_test_step = 1000

 **********************************************************************/

/*
 * texinfo: bai_dop853_control
 * This data structure controls the behaviour of the DOP 853 numerical
 * integrator.
 */

struct bai_dop853_control
{
// rounding unit
  double uround;
// factors which prevent stepsizes to increase/decrease too fast
  double safe_fac;
  double fac1;
  double fac2;
  double beta;
// maximum absolute value of the stepsize
  double hmax;
// signed initial stepsize
  double h0;
// maximum number of steps
  ba0_int_p nb_max_steps;
// used to decide when stiffness steps need be performed
  ba0_int_p stiffness_test_step;
};


extern BAI_DLL void bai_dop853_init_control (
    struct bai_dop853_control *);

extern BAI_DLL void bai_dop853_reset_control (
    struct bai_dop853_control *);

extern BAI_DLL void bai_dop853_set_control (
    struct bai_dop853_control *,
    struct bai_dop853_control *);

extern BAI_DLL void bai_dop853_set_default_control (
    struct bai_dop853_control *);

/**********************************************************************
 STATISTICS

 They are inlined now in the struct bai_dop853_workspace* structure
 **********************************************************************/

/*
 * texinfo: bai_dop853_stats
 * This data structure permits to provide statistics
 * on a numerical integration.
 */

struct bai_dop853_stats
{
// number of calls to the function to be integrated
  ba0_int_p nb_evals;
// number of steps
  ba0_int_p nb_steps;
// number of accepted steps
  ba0_int_p nb_accepts;
// number of rejected steps
  ba0_int_p nb_rejects;
};


extern BAI_DLL void bai_dop853_init_stats (
    struct bai_dop853_stats *);

extern BAI_DLL void bai_dop853_reset_stats (
    struct bai_dop853_stats *);

extern BAI_DLL void bai_dop853_set_stats (
    struct bai_dop853_stats *,
    struct bai_dop853_stats *);

/**********************************************************************
 ERROR TOLERANCE

 There are two types of error tolerance.
 bai_dop853_global_errtol: the entries relative [0] and absolute [0] are used
 bai_dop853_componentwise_errtol: the entries relative [i] and absolute [i]
	are used for each i (there should be an entry per dependent variable).
 **********************************************************************/

/*
 * texinfo: bai_dop853_typeof_errtol
 * This data type describes the two types of error tolerance.
 */

enum bai_dop853_typeof_errtol
{
  bai_dop853_global_errtol,
  bai_dop853_componentwise_errtol
};

/*
 * texinfo: bai_dop853_errtol
 * This data type permits to control the numerical integrator
 * by means of error tolerances.
 */

struct bai_dop853_errtol
{
  enum bai_dop853_typeof_errtol type;
// if type is bai_dop853_global_errtol then
//      the first entries of the next two arrays are used
// if type is bai_dop853_componentwise_errtol then
//      there should be one entry per dependent variable
  struct ba0_arrayof_double relative;
  struct ba0_arrayof_double absolute;
};


/* 
 * Initializes to bai_dop853_global_errtol with a absolute [0] = 1e-6 
 */

extern BAI_DLL void bai_dop853_init_errtol (
    struct bai_dop853_errtol *);

extern BAI_DLL void bai_dop853_reset_errtol (
    struct bai_dop853_errtol *);

extern BAI_DLL void bai_dop853_set_default_errtol (
    struct bai_dop853_errtol *);

extern BAI_DLL void bai_dop853_set_errtol (
    struct bai_dop853_errtol *,
    struct bai_dop853_errtol *);

extern BAI_DLL void bai_dop853_realloc_errtol (
    struct bai_dop853_errtol *,
    ba0_int_p);

/**********************************************************************
   VIEW

   What should be displayed

   view_t indicates if the independent variable must be displayed.
   Each entry of tab provides a variable or, more generally, a value
	to be displayed.
   If isvar is true then the value of the variable number varnum must be
	displayed. If isvar is false, then the* eval function is called
	and its returned value is displayed.
 **********************************************************************/

/*
 * texinfo: bai_dop853_eval_function
 * This data type provides the signature of user-defined function
 * called for printing the output of a numerical integration.
 */

typedef double bai_dop853_eval_function (
    double t,
// the numerical integrator workspace
    void *workspace);

/*
 * texinfo: bai_dop853_view_elt
 * This data type describes what should be printed on some given column.
 */

struct bai_dop853_view_elt
{
// if true the value of the dependent variable with index varnum is printed
// if false the result of the call to eval is printed
  bool isvar;
  ba0_int_p varnum;
  bai_dop853_eval_function *eval;
};


struct bai_arrayof_view_elt
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bai_dop853_view_elt *tab;
  ba0_int_p sizelt;
};


/*
 * texinfo: bai_dop853_view
 * This data type describes what should be printed during numerical
 * integration by the @code{bai_dop853_solout} function.
 * Each printed row involves many different columns.
 */

struct bai_dop853_view
{
// should the independent variable be printed ?
  bool view_t;
// one bai_dop853_view_elt per column
  struct bai_arrayof_view_elt elts;
};


extern BAI_DLL void bai_dop853_init_view (
    struct bai_dop853_view *);

extern BAI_DLL void bai_dop853_reset_view (
    struct bai_dop853_view *);

extern BAI_DLL void bai_dop853_realloc_view (
    struct bai_dop853_view *,
    ba0_int_p);

extern BAI_DLL void bai_dop853_set_view_variable (
    struct bai_dop853_view *,
    struct bav_variable *,
    struct bai_odex_system *);

extern BAI_DLL void bai_dop853_set_view_function (
    struct bai_dop853_view *,
    bai_dop853_eval_function *);

/**********************************************************************
 SOLOUT

 Prints in file f the values in w of the variables given in view.
 The boolean indicates if some interpolation must be performed, i.e. if
 a curve must be printed instead of a single point.
 If the boolean is true then
 - the double provides the interpolation step.
 - the variables in view must be prepared for dense output.
 
 **********************************************************************/

struct bai_dop853_workspace;

extern BAI_DLL void bai_dop853_solout (
    FILE *,
    struct bai_dop853_workspace *,
    struct bai_dop853_view *,
    bool,
    double);

/**********************************************************************
 DENSE OUTPUT 

 Dense output permits to interpolate the values of some dependent variables
 between two integration steps. 

 The indices of the variables over which dense output is going to be
 processed should be stored in index.
 **********************************************************************/

/*
 * texinfo: bai_dop853_dense_output
 * This data structure permits to provide dense output for some
 * dependent variables.
 */

struct bai_dop853_dense_output
{
// the indices of the variables for which dense output is desired
  struct ba0_tableof_int_p index;
// technical arrays
  struct ba0_arrayof_double cont0;
  struct ba0_arrayof_double cont1;
  struct ba0_arrayof_double cont2;
  struct ba0_arrayof_double cont3;
  struct ba0_arrayof_double cont4;
  struct ba0_arrayof_double cont5;
  struct ba0_arrayof_double cont6;
  struct ba0_arrayof_double cont7;
};


extern BAI_DLL void bai_dop853_init_dense_output (
    struct bai_dop853_dense_output *);

extern BAI_DLL void bai_dop853_reset_dense_output (
    struct bai_dop853_dense_output *);

extern BAI_DLL void bai_dop853_realloc_dense_output (
    struct bai_dop853_dense_output *,
    ba0_int_p);

extern BAI_DLL void bai_dop853_set_dense_output_all_variables (
    struct bai_dop853_dense_output *,
    struct bai_odex_system *);

extern BAI_DLL void bai_dop853_set_dense_output_variable (
    struct bai_dop853_dense_output *,
    struct bav_variable *,
    struct bai_odex_system *);

extern BAI_DLL void bai_dop853_set_dense_output (
    struct bai_dop853_dense_output *v,
    struct bai_dop853_dense_output *w);

/* 
 * Assigns yi (t) to *res. The value of t should be in the range w->told .. w->t */

extern BAI_DLL double bai_dop853_dense_output_evaluate (
    ba0_int_p i,
    double t,
    struct bai_dop853_workspace *w);

/**********************************************************************
 DOP 853
 **********************************************************************/

/*
 * texinfo: bai_dop853_workspace
 * This data type describes the workspace (the internal variables)
 * of the numerical integrator.
 */

struct bai_dop853_workspace
{
// old value of the independent variable
  double told;
// current value of the independent variable
  double t;
// current step size
  double h;
// values of the dependent variables at t
  struct ba0_arrayof_double y;
  struct ba0_arrayof_double y1;
  struct ba0_arrayof_double k1;
  struct ba0_arrayof_double k2;
  struct ba0_arrayof_double k3;
  struct ba0_arrayof_double k4;
  struct ba0_arrayof_double k5;
  struct ba0_arrayof_double k6;
  struct ba0_arrayof_double k7;
  struct ba0_arrayof_double k8;
  struct ba0_arrayof_double k9;
  struct ba0_arrayof_double k10;
  double hlamb;
  ba0_int_p nb_stiffs;
  ba0_int_p nb_non_stiffs;
  double facold;
  struct bai_dop853_stats stat;
// the function which evaluates the ODE right hand side
  bai_odex_integrated_function *fcn;
// initial values, error tolerance, control and dense output
  struct bai_dop853_initial_values iv;
  struct bai_dop853_errtol tol;
  struct bai_dop853_control control;
  struct bai_dop853_dense_output dow;
// if fcn is generated by bai_odex_generate_rhs_C_code then
// should point towards a struct bai_params structure
  void *params;
};


extern BAI_DLL void bai_dop853_init_workspace (
    struct bai_dop853_workspace *);

extern BAI_DLL void bai_dop853_reset_workspace (
    struct bai_dop853_workspace *);

extern BAI_DLL void bai_dop853_set_workspace (
    struct bai_dop853_workspace *,
    struct bai_dop853_workspace *);

extern BAI_DLL void bai_dop853_start_workspace (
    struct bai_dop853_workspace *,
    bai_odex_integrated_function * fcn,
    struct bai_dop853_initial_values *iv,
    struct bai_dop853_errtol *tol,
    struct bai_dop853_control *control,
    struct bai_dop853_dense_output *dow,
    void *params);

/* 
 * Performs one Runge-Kutta step. The main function. 
 */

extern BAI_DLL void bai_dop853_step_workspace (
    struct bai_dop853_workspace *);

/**********************************************************************
 EVALUATION FUNCTION

 The function index i must be prepared for dense output (it must
 appear in the index array of w->dow). res is a pointer to one double.

 Assigns to yi (t) to* res. 
 **********************************************************************/

extern BAI_DLL double bai_dop853_evaluate_variable (
    struct bav_variable *v,
    double t,
    struct bai_dop853_workspace *w,
    struct bai_odex_system *);

END_C_DECLS
#endif /* !BAI_DOP853_H */
