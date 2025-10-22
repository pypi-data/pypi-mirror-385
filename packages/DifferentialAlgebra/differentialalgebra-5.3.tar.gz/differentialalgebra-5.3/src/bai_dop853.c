#include "bai_dop853.h"
#include "bai_dop853_coeffs.h"

/**********************************************************************
 Because fmin and fmax are only defined in c99
 **********************************************************************/

static double
_fmin (
    double x,
    double y)
{
  return x < y ? x : y;
}

static double
_fmax (
    double x,
    double y)
{
  return x > y ? x : y;
}

/**********************************************************************
 INITIAL VALUES
 **********************************************************************/

/*
 * texinfo: bai_dop853_init_initial_values
 * Initialize @var{iv}.
 */

BAI_DLL void
bai_dop853_init_initial_values (
    struct bai_dop853_initial_values *iv)
{
  iv->t0 = iv->t1 = 0.;
  ba0_init_array ((struct ba0_array *) &iv->y0);
}

/*
 * texinfo: bai_dop853_reset_initial_values
 * Reset @var{iv} to zero.
 */

BAI_DLL void
bai_dop853_reset_initial_values (
    struct bai_dop853_initial_values *iv)
{
  iv->t0 = iv->t1 = 0.;
  ba0_reset_array ((struct ba0_array *) &iv->y0);
}

/*
 * texinfo: bai_dop853_new_initial_values
 * Allocate a new structure, initialize it and return it.
 */

BAI_DLL struct bai_dop853_initial_values *
bai_dop853_new_initial_values (
    void)
{
  struct bai_dop853_initial_values *iv;

  iv = (struct bai_dop853_initial_values *) ba0_alloc (sizeof (struct
          bai_dop853_initial_values));
  bai_dop853_init_initial_values (iv);
  return iv;
}

/*
 * texinfo: bai_dop853_realloc_initial_values
 * Ensure that the field @code{y0} may receive at least @var{n} values.
 * If any, the already existing values are preserved.
 */

BAI_DLL void
bai_dop853_realloc_initial_values (
    struct bai_dop853_initial_values *iv,
    ba0_int_p n)
{
  ba0_realloc_array ((struct ba0_array *) &iv->y0, n, sizeof (double));
}

/*
 * texinfo: bai_dop853_set_initial_values_time
 * Assign @var{t0} and @var{t1} to the corresponding fields of @var{iv}.
 */

BAI_DLL void
bai_dop853_set_initial_values_time (
    struct bai_dop853_initial_values *iv,
    double t0,
    double t1)
{
  iv->t0 = t0;
  iv->t1 = t1;
}

/*
 * May raise BAI_ERRUNK
 */

/*
 * texinfo: bai_dop853_set_initial_values_variable
 * Set to @var{d} the initial value of @var{v}.
 * The indices in @code{y0} are assumed to correspond to that in @code{S->lhs}.
 * Raise exception @code{BAI_ERRUNK} if @var{v} is undefined.
 */

BAI_DLL void
bai_dop853_set_initial_values_variable (
    struct bai_dop853_initial_values *iv,
    struct bav_variable *v,
    struct bai_odex_system *S,
    double d)
{
  ba0_int_p i;

  if (!bai_odex_is_lhs (v, S, &i))
    BA0_RAISE_EXCEPTION (BAI_ERRUNK);

  bai_dop853_realloc_initial_values (iv, S->lhs.size);
  iv->y0.size = S->lhs.size;
  iv->y0.tab[i] = d;
}

/*
 * texinfo: bai_dop853_set_initial_values
 * Assign @var{iw} to @var{iv}.
 */

BAI_DLL void
bai_dop853_set_initial_values (
    struct bai_dop853_initial_values *iv,
    struct bai_dop853_initial_values *iw)
{
  if (iv != iw)
    {
      iv->t0 = iw->t0;
      iv->t1 = iw->t1;
      ba0_set_array ((struct ba0_array *) &iv->y0,
          (struct ba0_array *) &iw->y0);
    }
}

/**********************************************************************
 CONTROL
 **********************************************************************/

/*
 * texinfo: bai_dop853_init_control
 * Initialize @var{s} to default values.
 */

BAI_DLL void
bai_dop853_init_control (
    struct bai_dop853_control *s)
{
  memset (s, 0, sizeof (struct bai_dop853_control));
}

/*
 * texinfo: bai_dop853_reset_control
 * Reset @var{s}.
 */

BAI_DLL void
bai_dop853_reset_control (
    struct bai_dop853_control *s)
{
  memset (s, 0, sizeof (struct bai_dop853_control));
}

/*
 * texinfo: bai_dop853_set_control
 * Assign @var{t} to @var{s}.
 */

BAI_DLL void
bai_dop853_set_control (
    struct bai_dop853_control *s,
    struct bai_dop853_control *t)
{
  if (s != t)
    memcpy (s, t, sizeof (struct bai_dop853_control));
}

/*
 * texinfo: bai_dop853_set_default_control
 * Set the fields of @var{s} to some default values, extracted from
 * the original FORTRAN code. The field @code{uround} is taken as 
 * @math{2.3\, 10^{-16}},
 * The fields @code{safe_fac}, @code{fac1} and @code{fac2} are taken
 * as @math{9/10}, @math{1/3} and @math{6}. 
 * The field @code{beta} is taken as zero.
 * The field @code{nb_max_steps} is taken as @math{10^5}.
 * The field @code{stiffness_test_step} is taken as @math{10^3}.
 */

BAI_DLL void
bai_dop853_set_default_control (
    struct bai_dop853_control *s)
{
  s->uround = 2.3e-16;
  s->safe_fac = 0.9;
  s->fac1 = 1. / 3.;
  s->fac2 = 6.;
  s->nb_max_steps = 1000000;
  s->stiffness_test_step = 1000;
}

/**********************************************************************
 STATISTICS
 **********************************************************************/

/*
 * texinfo: bai_dop853_init_stats
 * Initialize @var{st}.
 */

BAI_DLL void
bai_dop853_init_stats (
    struct bai_dop853_stats *st)
{
  memset (st, 0, sizeof (struct bai_dop853_stats));
}

/*
 * texinfo: bai_dop853_reset_stats
 * Reser @var{st}.
 */

BAI_DLL void
bai_dop853_reset_stats (
    struct bai_dop853_stats *st)
{
  memset (st, 0, sizeof (struct bai_dop853_stats));
}

/*
 * texinfo: bai_dop853_set_stats
 * Assign @var{dt} to @var{st}.
 */

BAI_DLL void
bai_dop853_set_stats (
    struct bai_dop853_stats *st,
    struct bai_dop853_stats *dt)
{
  if (st != dt)
    memcpy (st, dt, sizeof (struct bai_dop853_stats));
}

/**********************************************************************
 ERROR TOLERANCES
 **********************************************************************/

/*
 * texinfo: bai_dop853_init_errtol
 * Initialize @var{tol}.
 */

BAI_DLL void
bai_dop853_init_errtol (
    struct bai_dop853_errtol *tol)
{
  ba0_init_array ((struct ba0_array *) &tol->relative);
  ba0_init_array ((struct ba0_array *) &tol->absolute);
}

/*
 * texinfo: bai_dop853_reset_errtol
 * Reset @var{tol}.
 */

BAI_DLL void
bai_dop853_reset_errtol (
    struct bai_dop853_errtol *tol)
{
  ba0_reset_array ((struct ba0_array *) &tol->relative);
  ba0_reset_array ((struct ba0_array *) &tol->absolute);
}

/*
 * texinfo: bai_dop853_set_default_errtol
 * Set the error tolerance to a default value:
 * the field @code{type} is taken as @code{bai_dop853_global_errtol}.
 * The relative error (at index 0) is taken as zero.
 * The absolute error (at index 0) is taken as @math{10^{-6}}.
 */

BAI_DLL void
bai_dop853_set_default_errtol (
    struct bai_dop853_errtol *tol)
{
  tol->type = bai_dop853_global_errtol;
  bai_dop853_realloc_errtol (tol, 1);
  tol->relative.tab[tol->relative.size++] = 0.0;
  tol->absolute.tab[tol->absolute.size++] = 1e-6;
}

/*
 * texinfo: bai_dop853_set_errtol
 * Assign @var{stol} to @var{ttol}.
 */

BAI_DLL void
bai_dop853_set_errtol (
    struct bai_dop853_errtol *ttol,
    struct bai_dop853_errtol *stol)
{
  if (ttol != stol)
    {
      ttol->type = stol->type;
      ba0_set_array ((struct ba0_array *) &ttol->relative,
          (struct ba0_array *) &stol->relative);
      ba0_set_array ((struct ba0_array *) &ttol->absolute,
          (struct ba0_array *) &stol->absolute);
    }
}

/*
 * texinfo: bai_dop853_realloc_errtol
 * Ensure that the two arrays @code{relative} and @code{absolute} have
 * at least @var{n} entries. If any, the existing values are preserved.
 */

BAI_DLL void
bai_dop853_realloc_errtol (
    struct bai_dop853_errtol *tol,
    ba0_int_p n)
{
  ba0_realloc_array ((struct ba0_array *) &tol->relative, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &tol->absolute, n, sizeof (double));
}

/**********************************************************************
 VIEW
 **********************************************************************/

/*
 * texinfo: bai_dop853_init_view
 * Initialize @var{view}.
 */

BAI_DLL void
bai_dop853_init_view (
    struct bai_dop853_view *view)
{
  view->view_t = false;
  ba0_init_array ((struct ba0_array *) &view->elts);
}

/*
 * texinfo: bai_dop853_reset_view
 * Reset @var{view}.
 */

BAI_DLL void
bai_dop853_reset_view (
    struct bai_dop853_view *view)
{
  view->view_t = false;
  ba0_reset_array ((struct ba0_array *) &view->elts);
}

/*
 * texinfo: bai_dop853_realloc_view
 * Ensure that the array @code{elts} of @var{view} can receive at least
 * @var{n} elements.
 */

BAI_DLL void
bai_dop853_realloc_view (
    struct bai_dop853_view *view,
    ba0_int_p n)
{
  ba0_realloc_array ((struct ba0_array *) &view->elts, n,
      sizeof (struct bai_dop853_view_elt));
}

/*
 * texinfo: bai_dop853_set_view_variable
 * Append the variable @var{v} at the end of the array @code{elts} of @var{view}. 
 * Does nothing if the variable is already present in @code{elts}.
 * The exception @code{BAI_ERRUNK} is raised if the variable is undefined
 * in @var{S}.
 */

BAI_DLL void
bai_dop853_set_view_variable (
    struct bai_dop853_view *view,
    struct bav_variable *v,
    struct bai_odex_system *S)
{
  ba0_int_p i, j;

  if (!bai_odex_is_lhs (v, S, &i))
    BA0_RAISE_EXCEPTION (BAI_ERRUNK);

  for (j = 0; j < view->elts.size; j++)
    if (view->elts.tab[j].isvar && i == view->elts.tab[j].varnum)
      return;
  bai_dop853_realloc_view (view, view->elts.size + 1);
  view->elts.tab[view->elts.size].isvar = true;
  view->elts.tab[view->elts.size].varnum = i;
  view->elts.tab[view->elts.size].eval = 0;
  view->elts.size++;
}

/*
 * texinfo: bai_dop853_set_view_function
 * Append the function address @var{eval} at the end of the array @code{elts} 
 * of @var{view}. Does nothing if the address is already present.
 */

BAI_DLL void
bai_dop853_set_view_function (
    struct bai_dop853_view *view,
    bai_dop853_eval_function *eval)
{
  ba0_int_p j;

  for (j = 0; j < view->elts.size; j++)
    if (!view->elts.tab[j].isvar && eval == view->elts.tab[j].eval)
      return;

  bai_dop853_realloc_view (view, view->elts.size + 1);
  view->elts.tab[view->elts.size].isvar = false;
  view->elts.tab[view->elts.size].varnum = -1;
  view->elts.tab[view->elts.size].eval = eval;
  view->elts.size++;
}

/**********************************************************************
 SOLOUT

 May raise BAI_ERRDOW
 **********************************************************************/

/*
 * texinfo: bai_dop853_solout
 * Print in @var{f} some (possibly many) rows, following @var{view} and
 * taking values in the numerical integrator workspace @var{w}. 
 * If @var{interpolate} is @code{true} then some interpolation
 * is performed so that the range between the time value of two consecutive 
 * printed rows does not exceed @var{step}. 
 * This interpolation feature may cause many rows to be printed.
 * Applying it requires that the viewed variables are prepared for
 * dense output (see below). If any viewed variable is not prepared
 * and if interpolation is requested then the exception @code{BAI_ERRDOW} 
 * is raised.
 */

BAI_DLL void
bai_dop853_solout (
    FILE *f,
    struct bai_dop853_workspace *w,
    struct bai_dop853_view *view,
    bool interpolate,
    double step)
{
  double t, y;
  double posneg;
  ba0_int_p i;
/*
   Print the very first point
*/
  if (w->told == w->iv.t0)
    {
      if (view->view_t)
        fprintf (f, "%e ", w->iv.t0);
      for (i = 0; i < view->elts.size; i++)
        {
          if (view->elts.tab[i].isvar)
            fprintf (f, "%e ", w->iv.y0.tab[view->elts.tab[i].varnum]);
          else
            fprintf (f, "%e ", (*view->elts.tab[i].eval) (w->iv.t0, w));
        }
      fprintf (f, "\n");
    }

  if (interpolate)
    {
      posneg = w->iv.t1 > w->iv.t0 ? 1. : -1.;
/*
   strictly > 0 is important because of the first call
*/
      t = w->told + step * posneg;
      while (posneg * (w->t - t) > 0.)
        {
          if (view->view_t)
            fprintf (f, "%e ", t);
          for (i = 0; i < view->elts.size; i++)
            {
              if (view->elts.tab[i].isvar)
                y = bai_dop853_dense_output_evaluate (view->elts.tab[i].varnum,
                    t, w);
              else
                y = (*view->elts.tab[i].eval) (t, w);
              fprintf (f, "%e ", y);
            }
          fprintf (f, "\n");
          t += step * posneg;
        }
    }
/*
   Print the last point
*/
  if (view->view_t)
    fprintf (f, "%e ", w->t);
  for (i = 0; i < view->elts.size; i++)
    {
      if (view->elts.tab[i].isvar)
        fprintf (f, "%e ", w->y.tab[view->elts.tab[i].varnum]);
      else
        fprintf (f, "%e ", (*view->elts.tab[i].eval) (w->t, w));
    }
  fprintf (f, "\n");
}

/**********************************************************************
 DOP 853
 **********************************************************************/

/*
 * texinfo: bai_dop853_init_workspace
 * Initialize @var{w}.
 */

BAI_DLL void
bai_dop853_init_workspace (
    struct bai_dop853_workspace *w)
{
  w->told = 0.0;
  w->t = 0.0;
  w->h = 0.0;
  ba0_init_array ((struct ba0_array *) &w->y);
  ba0_init_array ((struct ba0_array *) &w->y1);
  ba0_init_array ((struct ba0_array *) &w->k1);
  ba0_init_array ((struct ba0_array *) &w->k2);
  ba0_init_array ((struct ba0_array *) &w->k3);
  ba0_init_array ((struct ba0_array *) &w->k4);
  ba0_init_array ((struct ba0_array *) &w->k5);
  ba0_init_array ((struct ba0_array *) &w->k6);
  ba0_init_array ((struct ba0_array *) &w->k7);
  ba0_init_array ((struct ba0_array *) &w->k8);
  ba0_init_array ((struct ba0_array *) &w->k9);
  ba0_init_array ((struct ba0_array *) &w->k10);
  w->hlamb = 0.0;
  w->nb_stiffs = 0;
  w->nb_non_stiffs = 0;
  w->facold = 0.0;
  bai_dop853_init_stats (&w->stat);
  w->fcn = (bai_odex_integrated_function *) 0;
  bai_dop853_init_initial_values (&w->iv);
  bai_dop853_init_errtol (&w->tol);
  bai_dop853_init_control (&w->control);
  bai_dop853_init_dense_output (&w->dow);
  w->params = (void *) 0;
}

/*
 * texinfo: bai_dop853_reset_workspace
 * Reset @var{w}.
 */

BAI_DLL void
bai_dop853_reset_workspace (
    struct bai_dop853_workspace *w)
{
  w->told = 0.0;
  w->t = 0.0;
  w->h = 0.0;
  ba0_reset_array ((struct ba0_array *) &w->y);
  ba0_reset_array ((struct ba0_array *) &w->y1);
  ba0_reset_array ((struct ba0_array *) &w->k1);
  ba0_reset_array ((struct ba0_array *) &w->k2);
  ba0_reset_array ((struct ba0_array *) &w->k3);
  ba0_reset_array ((struct ba0_array *) &w->k4);
  ba0_reset_array ((struct ba0_array *) &w->k5);
  ba0_reset_array ((struct ba0_array *) &w->k6);
  ba0_reset_array ((struct ba0_array *) &w->k7);
  ba0_reset_array ((struct ba0_array *) &w->k8);
  ba0_reset_array ((struct ba0_array *) &w->k9);
  ba0_reset_array ((struct ba0_array *) &w->k10);
  w->hlamb = 0.0;
  w->nb_stiffs = 0;
  w->nb_non_stiffs = 0;
  w->facold = 0.0;
  bai_dop853_reset_stats (&w->stat);
  w->fcn = (bai_odex_integrated_function *) 0;
  bai_dop853_reset_initial_values (&w->iv);
  bai_dop853_reset_errtol (&w->tol);
  bai_dop853_reset_control (&w->control);
  bai_dop853_reset_dense_output (&w->dow);
  w->params = (void *) 0;
}

static void
bai_dop853_realloc_workspace (
    struct bai_dop853_workspace *w,
    ba0_int_p n)
{
  ba0_realloc_array ((struct ba0_array *) &w->y, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &w->y1, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &w->k1, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &w->k2, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &w->k3, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &w->k4, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &w->k5, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &w->k6, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &w->k7, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &w->k8, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &w->k9, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &w->k10, n, sizeof (double));
  bai_dop853_realloc_initial_values (&w->iv, n);
  bai_dop853_realloc_errtol (&w->tol, n);
  bai_dop853_realloc_dense_output (&w->dow, n);
}

/*
 * texinfo: bai_dop853_set_workspace
 * Assign @var{w} to @var{v}.
 */

BAI_DLL void
bai_dop853_set_workspace (
    struct bai_dop853_workspace *v,
    struct bai_dop853_workspace *w)
{
  if (v == w)
    return;

  bai_dop853_realloc_workspace (v, w->iv.y0.size);
  v->told = w->told;
  v->t = w->t;
  v->h = w->h;
  ba0_set_array ((struct ba0_array *) &v->y, (struct ba0_array *) &w->y);
  ba0_set_array ((struct ba0_array *) &v->y1, (struct ba0_array *) &w->y1);
  ba0_set_array ((struct ba0_array *) &v->k1, (struct ba0_array *) &w->k1);
  ba0_set_array ((struct ba0_array *) &v->k2, (struct ba0_array *) &w->k2);
  ba0_set_array ((struct ba0_array *) &v->k3, (struct ba0_array *) &w->k3);
  ba0_set_array ((struct ba0_array *) &v->k4, (struct ba0_array *) &w->k4);
  ba0_set_array ((struct ba0_array *) &v->k5, (struct ba0_array *) &w->k5);
  ba0_set_array ((struct ba0_array *) &v->k6, (struct ba0_array *) &w->k6);
  ba0_set_array ((struct ba0_array *) &v->k7, (struct ba0_array *) &w->k7);
  ba0_set_array ((struct ba0_array *) &v->k8, (struct ba0_array *) &w->k8);
  ba0_set_array ((struct ba0_array *) &v->k9, (struct ba0_array *) &w->k9);
  ba0_set_array ((struct ba0_array *) &v->k10, (struct ba0_array *) &w->k10);
  v->hlamb = w->hlamb;
  v->nb_stiffs = w->nb_stiffs;
  v->nb_non_stiffs = w->nb_non_stiffs;
  v->facold = w->facold;
  bai_dop853_set_stats (&v->stat, &w->stat);
  v->fcn = w->fcn;
  bai_dop853_set_initial_values (&v->iv, &w->iv);
  bai_dop853_set_errtol (&v->tol, &w->tol);
  bai_dop853_set_control (&v->control, &w->control);
  bai_dop853_set_dense_output (&v->dow, &w->dow);
  v->params = w->params;
}

/*
   Note: the array k1=F0 is read by the function. It contains the result
   of the first evaluation of the function to be integrated.

   The arrays k2=F1, k3=Y1 are modified by bai_dop853_set_heuristic_h0.
   These modifications are overwritten by the calling function.

   Sets w->h. 

   May raise BAI_EXEVAL
*/

static void
bai_dop853_set_heuristic_h0 (
    struct bai_dop853_workspace *w)
{
  bai_odex_integrated_function *fcn = w->fcn;
  enum bai_exit_code code;
  struct bai_dop853_initial_values *iv = &w->iv;
  struct bai_dop853_errtol *tol = &w->tol;
  struct bai_dop853_control *control = &w->control;
  void *params = w->params;
  double *y = w->y.tab;
  double *k1 = w->k1.tab;
  double *k2 = w->k2.tab;
  double *k3 = w->k3.tab;
  double h, dnf, dny, der2, der12, h1;
  double posneg, hmax;
  ba0_int_p i, n;
/*
      FUNCTION HINIT(N,FCN,X,Y,XEND,POSNEG,F0,F1,Y1,IORD,
     &                       HMAX,ATOL,RTOL,ITOL,RPAR,IPAR)
C ----------------------------------------------------------
C ----  COMPUTATION OF AN INITIAL STEP SIZE GUESS
C ----------------------------------------------------------
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
      DIMENSION Y(N),Y1(N),F0(N),F1(N),ATOL(*),RTOL(*)
      DIMENSION RPAR(*),IPAR(*)
C ---- COMPUTE A FIRST GUESS FOR EXPLICIT EULER AS
C ----   H = 0.01 * NORM (Y0) / NORM (F0)
C ---- THE INCREMENT FOR EXPLICIT EULER IS SMALL
C ---- COMPARED TO THE SOLUTION
      DNF=0.0D0
      DNY=0.0D0 
      ATOLI=ATOL(1)
      RTOLI=RTOL(1)    
      IF (ITOL.EQ.0) THEN   
        DO 10 I=1,N 
        SK=ATOLI+RTOLI*ABS(Y(I))
        DNF=DNF+(F0(I)/SK)**2
  10    DNY=DNY+(Y(I)/SK)**2 
      ELSE
        DO 11 I=1,N 
        SK=ATOL(I)+RTOL(I)*ABS(Y(I))
        DNF=DNF+(F0(I)/SK)**2
  11    DNY=DNY+(Y(I)/SK)**2 
      END IF
*/
  n = iv->y0.size;
  posneg = iv->t1 > iv->t0 ? 1. : -1.;

  hmax = control->hmax != 0.0 ? control->hmax : fabs (iv->t1 - iv->t0);

  dnf = 0.0;
  dny = 0.0;
  if (tol->type == bai_dop853_global_errtol)
    {
      for (i = 0; i < n; i++)
        {
          double sk;
          sk = tol->absolute.tab[0] + tol->relative.tab[0] * fabs (y[i]);
          dnf = dnf + pow (k1[i] / sk, 2.);
          dny = dny + pow (y[i] / sk, 2.);
        }
    }
  else
    {
      for (i = 0; i < n; i++)
        {
          double sk;
          sk = tol->absolute.tab[i] + tol->relative.tab[i] * fabs (y[i]);
          dnf = dnf + pow (k1[i] / sk, 2.);
          dny = dny + pow (y[i] / sk, 2.);
        }
    }
/*
      IF (DNF.LE.1.D-10.OR.DNY.LE.1.D-10) THEN
         H=1.0D-6
      ELSE
         H=SQRT(DNY/DNF)*0.01D0 
      END IF
      H=MIN(H,HMAX)
      H=SIGN(H,POSNEG) 
*/
  if (dnf <= 1.e-10 || dny <= 1.e-10)
    h = 1.0e-6;
  else
    h = sqrt (dny / dnf) * 0.01;
  h = _fmin (h, hmax);
  h = h * posneg;
/*
C ---- PERFORM AN EXPLICIT EULER STEP
      DO 12 I=1,N
  12  Y1(I)=Y(I)+H*F0(I)
      CALL FCN(N,X+H,Y1,F1,RPAR,IPAR)
*/
  for (i = 0; i < n; i++)
    k3[i] = y[i] + h * k1[i];
  code = (*fcn) (w->t + h, k3, k2, params);
  if (code != bai_odex_success)
    BA0_RAISE_EXCEPTION (BAI_EXEVAL);
/*
C ---- ESTIMATE THE SECOND DERIVATIVE OF THE SOLUTION
      DER2=0.0D0
      IF (ITOL.EQ.0) THEN
        DO 15 I=1,N
        SK=ATOLI+RTOLI*ABS(Y(I))
  15    DER2=DER2+((F1(I)-F0(I))/SK)**2
      ELSE
        DO 16 I=1,N
        SK=ATOL(I)+RTOL(I)*ABS(Y(I))
  16    DER2=DER2+((F1(I)-F0(I))/SK)**2
      END IF
      DER2=SQRT(DER2)/H
*/
  der2 = 0.;
  if (tol->type == bai_dop853_global_errtol)
    {
      for (i = 0; i < n; i++)
        {
          double sk;
          sk = tol->absolute.tab[0] + tol->relative.tab[0] * fabs (y[i]);
          der2 = der2 + pow ((k2[i] - k1[i]) / sk, 2.);
        }
    }
  else
    {
      for (i = 0; i < n; i++)
        {
          double sk;
          sk = tol->absolute.tab[i] - tol->relative.tab[i] * fabs (y[i]);
          der2 = der2 + pow ((k2[i] - k1[i]) / sk, 2.);
        }
    }
  der2 = sqrt (der2) / h;
/*
C ---- STEP SIZE IS COMPUTED SUCH THAT
C ----  H**IORD * MAX ( NORM (F0), NORM (DER2)) = 0.01
      DER12=MAX(ABS(DER2),SQRT(DNF))
      IF (DER12.LE.1.D-15) THEN
         H1=MAX(1.0D-6,ABS(H)*1.0D-3)
      ELSE
         H1=(0.01D0/DER12)**(1.D0/IORD)
      END IF
      H=MIN(100*ABS(H),H1,HMAX)
      HINIT=SIGN(H,POSNEG)
      RETURN
      END
*/
  der12 = _fmax (fabs (der2), sqrt (dnf));
  if (der12 <= 1.e-15)
    h1 = _fmax (1.0e-6, fabs (h) * 1.e-3);
  else
    h1 = pow (0.01 / der12, 1. / 8.);
  h = _fmin (100. * fabs (h), _fmin (h1, hmax));
  w->h = posneg * h;
}

/*
 * May raise BAI_EXEVAL
 */

/*
 * texinfo: bai_dop853_start_workspace
 * Initialize @var{w} using the other parameters (the structures are copied).
 * If @code{control->h0} is zero then the initial stepsize is automatically
 * computed. If *@var{fcn} returns a nonzero value (due to a non finite
 * computed double) then the exception @code{BAI_EXEVAL} is raised.
 */

BAI_DLL void
bai_dop853_start_workspace (
    struct bai_dop853_workspace *w,
    bai_odex_integrated_function *fcn,
    struct bai_dop853_initial_values *iv,
    struct bai_dop853_errtol *tol,
    struct bai_dop853_control *control,
    struct bai_dop853_dense_output *dow,
    void *params)
{
  enum bai_exit_code code;

  bai_dop853_realloc_workspace (w, iv->y0.size);

  w->t = iv->t0;
  ba0_set_array ((struct ba0_array *) &w->y, (struct ba0_array *) &iv->y0);

  w->hlamb = 0.0;
  w->nb_stiffs = 0;
  w->nb_non_stiffs = 0;
  w->facold = 1.e-4;

  bai_dop853_reset_stats (&w->stat);

  w->fcn = fcn;
  bai_dop853_set_initial_values (&w->iv, iv);
  bai_dop853_set_errtol (&w->tol, tol);
  bai_dop853_set_control (&w->control, control);
  bai_dop853_set_dense_output (&w->dow, dow);
  w->params = params;

  code = (*fcn) (w->t, w->y.tab, w->k1.tab, params);
  w->stat.nb_evals += 1;
  if (code != bai_odex_success)
    BA0_RAISE_EXCEPTION (BAI_EXEVAL);

  if (control->h0 != 0)
    w->h = control->h0;
  else
    {
      bai_dop853_set_heuristic_h0 (w);
      w->stat.nb_evals += 1;
    }
}

/*
 * May return BAI_EXEVAL, BAI_EXSSIZ, BAI_EXMAXS, BAI_EXSTIF
 */

/*
 * texinfo: bai_dop853_step_workspace
 * Perform one step of the DOP853 Runge-Kutta method.
 * The workspace is assumed to be initialized by the above function.
 * If @code{control->hmax} is zero then the maximum stepsize is taken
 * as @math{|t_1 - t_0|}.
 * This function may raise @code{BAI_EXEVAL} if some call to
 * @code{w->fcn} returns a nonzero value (due to a non finite
 * computed double). It may raise @code{BAI_EXSSIZ} if the stepsize
 * becomes too small (essentially less than @code{control->uround}).
 * It may raise @code{BAI_EXMAXS} if the cumulated number of steps
 * exceeds the authorized maximum number of steps. 
 * It may raise @code{BAI_EXSTIF} if some stiffness is detected at
 * some step.
 */

BAI_DLL void
bai_dop853_step_workspace (
    struct bai_dop853_workspace *w)
{
  bai_odex_integrated_function *fcn = w->fcn;
  enum bai_exit_code code;
  struct bai_dop853_initial_values *iv = &w->iv;
  struct bai_dop853_errtol *tol = &w->tol;
  struct bai_dop853_control *control = &w->control;
  struct bai_dop853_stats *stat = &w->stat;
  struct bai_dop853_dense_output *dow = &w->dow;
  void *params = w->params;
  double *y = w->y.tab;
  double *y1 = w->y1.tab;
  double *k1 = w->k1.tab;
  double *k2 = w->k2.tab;
  double *k3 = w->k3.tab;
  double *k4 = w->k4.tab;
  double *k5 = w->k5.tab;
  double *k6 = w->k6.tab;
  double *k7 = w->k7.tab;
  double *k8 = w->k8.tab;
  double *k9 = w->k9.tab;
  double *k10 = w->k10.tab;
  double hnew;                  /* steps */
  double expo1;                 /* used for computing safety factors */
  double facc1, facc2, fac11;   /* safety factors */
  double posneg;                /* +/- 1 direction for integration */
  double hmax;                  /* max step size */
  double err, err2;             /* errors */
  ba0_int_p i, j;               /* plain indices */
  ba0_int_p n;                  /* dimension of the system */
  ba0_int_p nrdens;             /* number of yi subject to dense output */
  bool first, last, reject, enough;

  n = iv->y0.size;
  nrdens = dow->index.size;
/*
      FACOLD=1.D-4
      EXPO1=1.d0/8.d0-BETA*0.2D0
      FACC1=1.D0/FAC1
      FACC2=1.D0/FAC2
      POSNEG=SIGN(1.D0,XEND-X)
*/
  expo1 = 1. / 8. - control->beta * 0.2;
  facc1 = 1. / control->fac1;
  facc2 = 1. / control->fac2;
  posneg = iv->t1 - iv->t0 > 0. ? 1. : -1.;

  hmax = control->hmax != 0.0 ? control->hmax : fabs (iv->t1 - iv->t0);
/*
C --- INITIAL PREPARATIONS   
      ATOLI=ATOL(1)
      RTOLI=RTOL(1)    
      LAST=.FALSE. 
      HLAMB=0.D0
?     IASTI=0
--> nb_stiffs, nb_non_stiffs
      CALL FCN(N,X,Y,K1,RPAR,IPAR)
      HMAX=ABS(HMAX)
--> not translated. In the specifications.
?     IORD=8  
--> IORD probably is the order of the Runge-Kutta scheme : 8
--> pas traduit. Sert pour HINIT.
?     IF (H.EQ.0.D0) H=HINIT(N,FCN,X,Y,XEND,POSNEG,K1,K2,K3,IORD,
     &                       HMAX,ATOL,RTOL,ITOL,RPAR,IPAR)
      NFCN=NFCN+2
      REJECT=.FALSE.
      XOLD=X
      IF (IOUT.GE.1) THEN 
          IRTRN=1 
?          HOUT=1.D0
--> pas traduit
          CALL SOLOUT(NACCPT+1,XOLD,X,Y,N,CONT,ICOMP,NRD,
     &                RPAR,IPAR,IRTRN)
          IF (IRTRN.LT.0) GOTO 79
--> while
      END IF
*/
  w->told = w->t;

  enough = false;               /* to avoid a warning */
  first = true;
  reject = false;
  last = false;
/*
C --- BASIC INTEGRATION STEP  
   1  CONTINUE
      IF (NSTEP.GT.NMAX) GOTO 78
      IF (0.1D0*ABS(H).LE.ABS(X)*UROUND)GOTO 77
--> while
      IF ((X+1.01D0*H-XEND)*POSNEG.GT.0.D0) THEN
         H=XEND-X 
         LAST=.TRUE.
      END IF
      NSTEP=NSTEP+1
*/
  while ((first || reject) && stat->nb_steps < control->nb_max_steps
      && (enough = (0.1 * fabs (w->h) > control->uround * fabs (w->t))))
    {
      first = false;
      if ((w->t + 1.01 * w->h - iv->t1) * posneg > 0.)
        {
          w->h = iv->t1 - w->t;
          last = true;
        }
      stat->nb_steps += 1;
/*
C --- THE TWELVE STAGES
      IF (IRTRN.GE.2) THEN
         CALL FCN(N,X,Y,K1,RPAR,IPAR)
      END IF
      DO 22 I=1,N 
  22  Y1(I)=Y(I)+H*A21*K1(I)  
      CALL FCN(N,X+C2*H,Y1,K2,RPAR,IPAR)
*/
/*
   This possibility is not offered anymore
	if (irtrn == bai_dop853_keep_integrating_y_is_altered)
	    code = (*fcn) (w->t, w->y, w->k1, params);
*/
      for (i = 0; i < n; i++)
        y1[i] = y[i] + w->h * a21 * k1[i];
      code = (*fcn) (w->t + c2 * w->h, y1, k2, params);
      stat->nb_evals += 1;
      if (code != bai_odex_success)
        BA0_RAISE_EXCEPTION (BAI_EXEVAL);
/*
      DO 23 I=1,N 
  23  Y1(I)=Y(I)+H*(A31*K1(I)+A32*K2(I))  
      CALL FCN(N,X+C3*H,Y1,K3,RPAR,IPAR)
*/
      for (i = 0; i < n; i++)
        y1[i] = y[i] + w->h * (a31 * k1[i] + a32 * k2[i]);
      code = (*fcn) (w->t + c3 * w->h, y1, k3, params);
      stat->nb_evals += 1;
      if (code != bai_odex_success)
        BA0_RAISE_EXCEPTION (BAI_EXEVAL);
/*
      DO 24 I=1,N 
  24  Y1(I)=Y(I)+H*(A41*K1(I)+A43*K3(I))  
      CALL FCN(N,X+C4*H,Y1,K4,RPAR,IPAR)
*/
      for (i = 0; i < n; i++)
        y1[i] = y[i] + w->h * (a41 * k1[i] + a43 * k3[i]);
      code = (*fcn) (w->t + c4 * w->h, y1, k4, params);
      stat->nb_evals += 1;
      if (code != bai_odex_success)
        BA0_RAISE_EXCEPTION (BAI_EXEVAL);
/*
      DO 25 I=1,N 
  25  Y1(I)=Y(I)+H*(A51*K1(I)+A53*K3(I)+A54*K4(I))
      CALL FCN(N,X+C5*H,Y1,K5,RPAR,IPAR)
*/
      for (i = 0; i < n; i++)
        y1[i] = y[i] + w->h * (a51 * k1[i] + a53 * k3[i] + a54 * k4[i]);
      code = (*fcn) (w->t + c5 * w->h, y1, k5, params);
      stat->nb_evals += 1;
      if (code != bai_odex_success)
        BA0_RAISE_EXCEPTION (BAI_EXEVAL);
/*
      DO 26 I=1,N 
  26  Y1(I)=Y(I)+H*(A61*K1(I)+A64*K4(I)+A65*K5(I))
      CALL FCN(N,X+C6*H,Y1,K6,RPAR,IPAR)
*/
      for (i = 0; i < n; i++)
        y1[i] = y[i] + w->h * (a61 * k1[i] + a64 * k4[i] + a65 * k5[i]);
      code = (*fcn) (w->t + c6 * w->h, y1, k6, params);
      stat->nb_evals += 1;
      if (code != bai_odex_success)
        BA0_RAISE_EXCEPTION (BAI_EXEVAL);
/*
      DO 27 I=1,N 
  27  Y1(I)=Y(I)+H*(A71*K1(I)+A74*K4(I)+A75*K5(I)+A76*K6(I))
      CALL FCN(N,X+C7*H,Y1,K7,RPAR,IPAR)
*/
      for (i = 0; i < n; i++)
        y1[i] =
            y[i] + w->h * (a71 * k1[i] + a74 * k4[i] + a75 * k5[i] +
            a76 * k6[i]);
      code = (*fcn) (w->t + c7 * w->h, y1, k7, params);
      stat->nb_evals += 1;
      if (code != bai_odex_success)
        BA0_RAISE_EXCEPTION (BAI_EXEVAL);
/*
      DO 28 I=1,N 
  28  Y1(I)=Y(I)+H*(A81*K1(I)+A84*K4(I)+A85*K5(I)+A86*K6(I)+A87*K7(I))  
      CALL FCN(N,X+C8*H,Y1,K8,RPAR,IPAR)
*/
      for (i = 0; i < n; i++)
        y1[i] =
            y[i] + w->h * (a81 * k1[i] + a84 * k4[i] + a85 * k5[i] +
            a86 * k6[i] + a87 * k7[i]);
      code = (*fcn) (w->t + c8 * w->h, y1, k8, params);
      stat->nb_evals += 1;
      if (code != bai_odex_success)
        BA0_RAISE_EXCEPTION (BAI_EXEVAL);
/*
      DO 29 I=1,N 
  29  Y1(I)=Y(I)+H*(A91*K1(I)+A94*K4(I)+A95*K5(I)+A96*K6(I)+A97*K7(I)
     &   +A98*K8(I))
      CALL FCN(N,X+C9*H,Y1,K9,RPAR,IPAR)
*/
      for (i = 0; i < n; i++)
        y1[i] =
            y[i] + w->h * (a91 * k1[i] + a94 * k4[i] + a95 * k5[i] +
            a96 * k6[i] + a97 * k7[i] + a98 * k8[i]);
      code = (*fcn) (w->t + c9 * w->h, y1, k9, params);
      stat->nb_evals += 1;
      if (code != bai_odex_success)
        BA0_RAISE_EXCEPTION (BAI_EXEVAL);
/*
      DO 30 I=1,N 
  30  Y1(I)=Y(I)+H*(A101*K1(I)+A104*K4(I)+A105*K5(I)+A106*K6(I)
     &   +A107*K7(I)+A108*K8(I)+A109*K9(I))
      CALL FCN(N,X+C10*H,Y1,K10,RPAR,IPAR)
*/
      for (i = 0; i < n; i++)
        y1[i] =
            y[i] + w->h * (a101 * k1[i] + a104 * k4[i] + a105 * k5[i] +
            a106 * k6[i] + a107 * k7[i] + a108 * k8[i] + a109 * k9[i]);
      code = (*fcn) (w->t + c10 * w->h, y1, k10, params);
      stat->nb_evals += 1;
      if (code != bai_odex_success)
        BA0_RAISE_EXCEPTION (BAI_EXEVAL);
/*
      DO 31 I=1,N 
  31  Y1(I)=Y(I)+H*(A111*K1(I)+A114*K4(I)+A115*K5(I)+A116*K6(I)
     &   +A117*K7(I)+A118*K8(I)+A119*K9(I)+A1110*K10(I))
      CALL FCN(N,X+C11*H,Y1,K2,RPAR,IPAR)
*/
      for (i = 0; i < n; i++)
        y1[i] =
            y[i] + w->h * (a111 * k1[i] + a114 * k4[i] + a115 * k5[i] +
            a116 * k6[i] + a117 * k7[i] + a118 * k8[i] + a119 * k9[i] +
            a1110 * k10[i]);
      code = (*fcn) (w->t + c11 * w->h, y1, k2, params);
      stat->nb_evals += 1;
      if (code != bai_odex_success)
        BA0_RAISE_EXCEPTION (BAI_EXEVAL);
/*
      XPH=X+H
      DO 32 I=1,N 
  32  Y1(I)=Y(I)+H*(A121*K1(I)+A124*K4(I)+A125*K5(I)+A126*K6(I)
     &   +A127*K7(I)+A128*K8(I)+A129*K9(I)+A1210*K10(I)+A1211*K2(I))
      CALL FCN(N,XPH,Y1,K3,RPAR,IPAR)
      NFCN=NFCN+11
*/
      for (i = 0; i < n; i++)
        y1[i] =
            y[i] + w->h * (a121 * k1[i] + a124 * k4[i] + a125 * k5[i] +
            a126 * k6[i] + a127 * k7[i] + a128 * k8[i] + a129 * k9[i] +
            a1210 * k10[i] + a1211 * k2[i]);
      code = (*fcn) (w->t + w->h, y1, k3, params);
      stat->nb_evals += 1;
      if (code != bai_odex_success)
        BA0_RAISE_EXCEPTION (BAI_EXEVAL);
/*
      DO 35 I=1,N 
      K4(I)=B1*K1(I)+B6*K6(I)+B7*K7(I)+B8*K8(I)+B9*K9(I)
     &   +B10*K10(I)+B11*K2(I)+B12*K3(I)
  35  K5(I)=Y(I)+H*K4(I)
*/
      for (i = 0; i < n; i++)
        {
          k4[i] =
              b1 * k1[i] + b6 * k6[i] + b7 * k7[i] + b8 * k8[i] + b9 * k9[i] +
              b10 * k10[i] + b11 * k2[i] + b12 * k3[i];
          k5[i] = y[i] + w->h * k4[i];
        }
/*
C --- ERROR ESTIMATION  
      ERR=0.D0
      ERR2=0.D0
      IF (ITOL.EQ.0) THEN   
        DO 41 I=1,N 
        SK=ATOLI+RTOLI*MAX(ABS(Y(I)),ABS(K5(I)))
        ERRI=K4(I)-BHH1*K1(I)-BHH2*K9(I)-BHH3*K3(I)
        ERR2=ERR2+(ERRI/SK)**2
        ERRI=ER1*K1(I)+ER6*K6(I)+ER7*K7(I)+ER8*K8(I)+ER9*K9(I)
     &      +ER10*K10(I)+ER11*K2(I)+ER12*K3(I)
  41    ERR=ERR+(ERRI/SK)**2
      ELSE
        DO 42 I=1,N 
        SK=ATOL(I)+RTOL(I)*MAX(ABS(Y(I)),ABS(K5(I)))
        ERRI=K4(I)-BHH1*K1(I)-BHH2*K9(I)-BHH3*K3(I)
        ERR2=ERR2+(ERRI/SK)**2
        ERRI=ER1*K1(I)+ER6*K6(I)+ER7*K7(I)+ER8*K8(I)+ER9*K9(I)
     &      +ER10*K10(I)+ER11*K2(I)+ER12*K3(I)
  42    ERR=ERR+(ERRI/SK)**2
      END IF  
*/
      err = 0.;
      err2 = 0.;
      if (tol->type == bai_dop853_global_errtol)
        {
          double atol, rtol;
          atol = tol->absolute.tab[0];
          rtol = tol->relative.tab[0];
          for (i = 0; i < n; i++)
            {
              double sk, err1;
              sk = atol + rtol * _fmax (fabs (y[i]), fabs (k5[i]));
              err1 = k4[i] - bhh1 * k1[i] - bhh2 * k9[i] - bhh3 * k3[i];
              err2 = err2 + pow (err1 / sk, 2.);
              err1 =
                  er1 * k1[i] + er6 * k6[i] + er7 * k7[i] + er8 * k8[i] +
                  er9 * k9[i] + er10 * k10[i] + er11 * k2[i] + er12 * k3[i];
              err = err + pow (err1 / sk, 2.);
            }
        }
      else
        {
          for (i = 0; i < n; i++)
            {
              double sk, err1;
              sk = tol->absolute.tab[i] +
                  tol->relative.tab[i] * _fmax (fabs (y[i]), fabs (k5[i]));
              err1 = k4[i] - bhh1 * k1[i] - bhh2 * k9[i] - bhh3 * k3[i];
              err2 = err2 + pow (err1 / sk, 2.);
              err1 =
                  er1 * k1[i] + er6 * k6[i] + er7 * k7[i] + er8 * k8[i] +
                  er9 * k9[i] + er10 * k10[i] + er11 * k2[i] + er12 * k3[i];
              err = err + pow (err1 / sk, 2.);
            }
        }
/*
      DENO=ERR+0.01D0*ERR2
      IF (DENO.LE.0.D0) DENO=1.D0
      ERR=ABS(H)*ERR*SQRT(1.D0/(N*DENO))

   It seems to be the formula page 255. See also page 168.
   err = err_5 (estimation using the order 5 formula) and 
   err2 = err_3 (estimation using the order 3 formula).
*/
      {
        double denom = err + 0.01 * err2;
        if (denom <= 0.)
          denom = 1.;
        err = fabs (w->h) * err * sqrt (1. / (n * denom));
      }
/*
C --- COMPUTATION OF HNEW
      FAC11=ERR**EXPO1
C --- LUND-STABILIZATION
      FAC=FAC11/FACOLD**BETA
C --- WE REQUIRE  FAC1 <= HNEW/H <= FAC2
      FAC=MAX(FACC2,MIN(FACC1,FAC/SAFE))
      HNEW=H/FAC  
*/
      {
        double fac;
        fac11 = pow (err, expo1);
        fac = fac11 / pow (w->facold, control->beta);
        fac = _fmax (facc2, _fmin (facc1, fac / control->safe_fac));
        hnew = w->h / fac;
      }
/*
      IF(ERR.LE.1.D0)THEN
C --- STEP IS ACCEPTED  
         FACOLD=MAX(ERR,1.0D-4)
         NACCPT=NACCPT+1
         CALL FCN(N,XPH,K5,K4,RPAR,IPAR)
         NFCN=NFCN+1
*/
      if (err <= 1.)
        {
          w->facold = _fmax (err, 1.0e-4);
          stat->nb_accepts += 1;
          code = (*fcn) (w->t + w->h, k5, k4, params);
          if (code != bai_odex_success)
            BA0_RAISE_EXCEPTION (BAI_EXEVAL);
          stat->nb_evals += 1;
/*
C ------- STIFFNESS DETECTION
         IF (MOD(NACCPT,NSTIFF).EQ.0.OR.IASTI.GT.0) THEN
            STNUM=0.D0
            STDEN=0.D0
            DO 64 I=1,N 
               STNUM=STNUM+(K4(I)-K3(I))**2
               STDEN=STDEN+(K5(I)-Y1(I))**2
 64         CONTINUE  
            IF (STDEN.GT.0.D0) HLAMB=ABS(H)*SQRT(STNUM/STDEN) 
            IF (HLAMB.GT.6.1D0) THEN
               NONSTI=0
               IASTI=IASTI+1  
               IF (IASTI.EQ.15) THEN
                  IF (IPRINT.GT.0) WRITE (IPRINT,*) 
     &               ' THE PROBLEM SEEMS TO BECOME STIFF AT X = ',X   
                  IF (IPRINT.LE.0) GOTO 76
               END IF
            ELSE
               NONSTI=NONSTI+1  
               IF (NONSTI.EQ.6) IASTI=0
            END IF
         END IF 
*/
          if (w->nb_stiffs > 0 || (control->stiffness_test_step
                  && stat->nb_steps % control->stiffness_test_step == 0))
            {
              double numer, denom;
              numer = 0.;
              denom = 0.;
              for (i = 0; i < n; i++)
                {
                  numer = numer + pow (k4[i] - k3[i], 2.);
                  denom = denom + pow (k5[i] - k1[i], 2.);
                }
              if (denom > 0.)
                w->hlamb = fabs (w->h) * sqrt (numer / denom);
              if (w->hlamb > 6.1)
                {
                  w->nb_non_stiffs = 0;
                  w->nb_stiffs += 1;
                  if (w->nb_stiffs == 15)
                    BA0_RAISE_EXCEPTION (BAI_EXSTIF);
                }
              else
                {
                  w->nb_non_stiffs += 1;
                  if (w->nb_non_stiffs == 6)
                    w->nb_stiffs = 0;
                }
            }
/*
         IF (IOUT.GE.2) THEN
C ----    SAVE THE FIRST FUNCTION EVALUATIONS   
            DO 62 J=1,NRD
               I=ICOMP(J)
               CONT(J)=Y(I)
               YDIFF=K5(I)-Y(I)
               CONT(J+NRD)=YDIFF
               BSPL=H*K1(I)-YDIFF
               CONT(J+NRD*2)=BSPL
               CONT(J+NRD*3)=YDIFF-H*K4(I)-BSPL
               CONT(J+NRD*4)=D41*K1(I)+D46*K6(I)+D47*K7(I)+D48*K8(I)
     &                  +D49*K9(I)+D410*K10(I)+D411*K2(I)+D412*K3(I)
               CONT(J+NRD*5)=D51*K1(I)+D56*K6(I)+D57*K7(I)+D58*K8(I)
     &                  +D59*K9(I)+D510*K10(I)+D511*K2(I)+D512*K3(I)
               CONT(J+NRD*6)=D61*K1(I)+D66*K6(I)+D67*K7(I)+D68*K8(I)
     &                  +D69*K9(I)+D610*K10(I)+D611*K2(I)+D612*K3(I)
               CONT(J+NRD*7)=D71*K1(I)+D76*K6(I)+D77*K7(I)+D78*K8(I)
     &                  +D79*K9(I)+D710*K10(I)+D711*K2(I)+D712*K3(I)
   62       CONTINUE 
*/
          if (nrdens > 0)
            {
              for (j = 0; j < nrdens; j++)
                {
                  double ydiff, bspl;
                  i = dow->index.tab[j];
                  dow->cont0.tab[j] = y[i];
                  ydiff = k5[i] - y[i];
                  dow->cont1.tab[j] = ydiff;
                  bspl = w->h * k1[i] - ydiff;
                  dow->cont2.tab[j] = bspl;
                  dow->cont3.tab[j] = ydiff - w->h * k4[i] - bspl;
                  dow->cont4.tab[j] =
                      d41 * k1[i] + d46 * k6[i] + d47 * k7[i] + d48 * k8[i] +
                      d49 * k9[i] + d410 * k10[i] + d411 * k2[i] + d412 * k3[i];
                  dow->cont5.tab[j] =
                      d51 * k1[i] + d56 * k6[i] + d57 * k7[i] + d58 * k8[i] +
                      d59 * k9[i] + d510 * k10[i] + d511 * k2[i] + d512 * k3[i];
                  dow->cont6.tab[j] =
                      d61 * k1[i] + d66 * k6[i] + d67 * k7[i] + d68 * k8[i] +
                      d69 * k9[i] + d610 * k10[i] + d611 * k2[i] + d612 * k3[i];
                  dow->cont7.tab[j] =
                      d71 * k1[i] + d76 * k6[i] + d77 * k7[i] + d78 * k8[i] +
                      d79 * k9[i] + d710 * k10[i] + d711 * k2[i] + d712 * k3[i];
                }
/*
C ---     THE NEXT THREE FUNCTION EVALUATIONS
            DO 51 I=1,N 
  51           Y1(I)=Y(I)+H*(A141*K1(I)+A147*K7(I)+A148*K8(I)
     &            +A149*K9(I)+A1410*K10(I)+A1411*K2(I)+A1412*K3(I)
     &            +A1413*K4(I))
            CALL FCN(N,X+C14*H,Y1,K10,RPAR,IPAR)
*/
              for (i = 0; i < n; i++)
                y1[i] =
                    y[i] + w->h * (a141 * k1[i] + a147 * k7[i] + a148 * k8[i] +
                    a149 * k9[i] + a1410 * k10[i] + a1411 * k2[i] +
                    a1412 * k3[i] + a1413 * k4[i]);
              code = (*fcn) (w->t + c14 * w->h, y1, k10, params);
              stat->nb_evals += 1;
              if (code != bai_odex_success)
                BA0_RAISE_EXCEPTION (BAI_EXEVAL);
/*
            DO 52 I=1,N 
  52           Y1(I)=Y(I)+H*(A151*K1(I)+A156*K6(I)+A157*K7(I)
     &            +A158*K8(I)+A1511*K2(I)+A1512*K3(I)+A1513*K4(I)
     &            +A1514*K10(I))
            CALL FCN(N,X+C15*H,Y1,K2,RPAR,IPAR)
*/
              for (i = 0; i < n; i++)
                y1[i] =
                    y[i] + w->h * (a151 * k1[i] + a156 * k6[i] + a157 * k7[i] +
                    a158 * k8[i] + a1511 * k2[i] + a1512 * k3[i] +
                    a1513 * k4[i] + a1514 * k10[i]);
              code = (*fcn) (w->t + c15 * w->h, y1, k2, params);
              stat->nb_evals += 1;
              if (code != bai_odex_success)
                BA0_RAISE_EXCEPTION (BAI_EXEVAL);
/*

            DO 53 I=1,N 
  53           Y1(I)=Y(I)+H*(A161*K1(I)+A166*K6(I)+A167*K7(I)
     &            +A168*K8(I)+A169*K9(I)+A1613*K4(I)+A1614*K10(I)
     &            +A1615*K2(I))
            CALL FCN(N,X+C16*H,Y1,K3,RPAR,IPAR)
            NFCN=NFCN+3 
*/
              for (i = 0; i < n; i++)
                y1[i] =
                    y[i] + w->h * (a161 * k1[i] + a166 * k6[i] + a167 * k7[i] +
                    a168 * k8[i] + a169 * k9[i] + a1613 * k4[i] +
                    a1614 * k10[i] + a1615 * k2[i]);
              code = (*fcn) (w->t + c16 * w->h, y1, k3, params);
              stat->nb_evals += 1;
              if (code != bai_odex_success)
                BA0_RAISE_EXCEPTION (BAI_EXEVAL);
/*
C ---     FINAL PREPARATION
            DO 63 J=1,NRD
               I=ICOMP(J)
               CONT(J+NRD*4)=H*(CONT(J+NRD*4)+D413*K4(I)+D414*K10(I)
     &            +D415*K2(I)+D416*K3(I))
               CONT(J+NRD*5)=H*(CONT(J+NRD*5)+D513*K4(I)+D514*K10(I)
     &            +D515*K2(I)+D516*K3(I))
               CONT(J+NRD*6)=H*(CONT(J+NRD*6)+D613*K4(I)+D614*K10(I)
     &            +D615*K2(I)+D616*K3(I))
               CONT(J+NRD*7)=H*(CONT(J+NRD*7)+D713*K4(I)+D714*K10(I)
     &            +D715*K2(I)+D716*K3(I))
  63        CONTINUE
            HOUT=H
--> pas traduit
         END IF
*/
              for (j = 0; j < nrdens; j++)
                {
                  i = dow->index.tab[j];
                  dow->cont4.tab[j] =
                      w->h * (dow->cont4.tab[j] + d413 * k4[i] + d414 * k10[i] +
                      d415 * k2[i] + d416 * k3[i]);
                  dow->cont5.tab[j] =
                      w->h * (dow->cont5.tab[j] + d513 * k4[i] + d514 * k10[i] +
                      d515 * k2[i] + d516 * k3[i]);
                  dow->cont6.tab[j] =
                      w->h * (dow->cont6.tab[j] + d613 * k4[i] + d614 * k10[i] +
                      d615 * k2[i] + d616 * k3[i]);
                  dow->cont7.tab[j] =
                      w->h * (dow->cont7.tab[j] + d713 * k4[i] + d714 * k10[i] +
                      d715 * k2[i] + d716 * k3[i]);
                }
            }
/*
         DO 67 I=1,N
         K1(I)=K4(I)
  67     Y(I)=K5(I)
         XOLD=X
         X=XPH
         IF (IOUT.GE.1) THEN
            CALL SOLOUT(NACCPT+1,XOLD,X,Y,N,CONT,ICOMP,NRD,
     &                  RPAR,IPAR,IRTRN)
            IF (IRTRN.LT.0) GOTO 79
         END IF 
*/
          for (i = 0; i < n; i++)
            {
              k1[i] = k4[i];
              y[i] = k5[i];
            }
          w->told = w->t;
          w->t = w->t + w->h;
/*
C ------- NORMAL EXIT
         IF (LAST) THEN
            H=HNEW
            IDID=1
            RETURN
         END IF
         IF(ABS(HNEW).GT.HMAX)HNEW=POSNEG*HMAX  
         IF(REJECT)HNEW=POSNEG*MIN(ABS(HNEW),ABS(H))
         REJECT=.FALSE. 
*/
          if (last)
            w->h = hnew;
          if (fabs (hnew) > hmax)
            hnew = posneg * hmax;
          if (reject)
            hnew = posneg * _fmin (fabs (hnew), fabs (w->h));
          reject = false;
        }
      else
        {
/*
C --- STEP IS REJECTED   
         HNEW=H/MIN(FACC1,FAC11/SAFE)
         REJECT=.TRUE.  
         IF(NACCPT.GE.1)NREJCT=NREJCT+1   
         LAST=.FALSE.
      END IF
      H=HNEW
      GOTO 1
*/
          hnew = w->h / _fmin (facc1, fac11 / control->safe_fac);
          reject = true;
          if (stat->nb_accepts >= 1)
            stat->nb_rejects += 1;
          last = false;
        }
      w->h = hnew;
    }
/*
C --- FAIL EXIT         
  76  CONTINUE 
      IDID=-4           
      RETURN
--> nothing to do
  77  CONTINUE
      IF (IPRINT.GT.0) WRITE(IPRINT,979)X   
      IF (IPRINT.GT.0) WRITE(IPRINT,*)' STEP SIZE TOO SMALL, H=',H
      IDID=-3
      RETURN
  78  CONTINUE
      IF (IPRINT.GT.0) WRITE(IPRINT,979)X   
      IF (IPRINT.GT.0) WRITE(IPRINT,*)
     &     ' MORE THAN NMAX =',NMAX,'STEPS ARE NEEDED' 
      IDID=-2
      RETURN
  79  CONTINUE
      IF (IPRINT.GT.0) WRITE(IPRINT,979)X
 979  FORMAT(' EXIT OF DOP853 AT X=',E18.4) 
      IDID=2
      RETURN
      END
*/
  if (!enough)
    BA0_RAISE_EXCEPTION (BAI_EXSSIZ);
  else if (stat->nb_steps >= control->nb_max_steps)
    BA0_RAISE_EXCEPTION (BAI_EXMAXS);
}

/**********************************************************************
 DENSE OUTPUT
 **********************************************************************/

/*
 * texinfo: bai_dop853_init_dense_output
 * Initialize @var{dow}.
 */

BAI_DLL void
bai_dop853_init_dense_output (
    struct bai_dop853_dense_output *dow)
{
  ba0_init_table ((struct ba0_table *) &dow->index);
  ba0_init_array ((struct ba0_array *) &dow->cont0);
  ba0_init_array ((struct ba0_array *) &dow->cont1);
  ba0_init_array ((struct ba0_array *) &dow->cont2);
  ba0_init_array ((struct ba0_array *) &dow->cont3);
  ba0_init_array ((struct ba0_array *) &dow->cont4);
  ba0_init_array ((struct ba0_array *) &dow->cont5);
  ba0_init_array ((struct ba0_array *) &dow->cont6);
  ba0_init_array ((struct ba0_array *) &dow->cont7);
}

/*
 * texinfo: bai_dop853_reset_dense_output
 * Reset @var{dow}.
 */

BAI_DLL void
bai_dop853_reset_dense_output (
    struct bai_dop853_dense_output *dow)
{
  ba0_reset_table ((struct ba0_table *) &dow->index);
  ba0_reset_array ((struct ba0_array *) &dow->cont0);
  ba0_reset_array ((struct ba0_array *) &dow->cont1);
  ba0_reset_array ((struct ba0_array *) &dow->cont2);
  ba0_reset_array ((struct ba0_array *) &dow->cont3);
  ba0_reset_array ((struct ba0_array *) &dow->cont4);
  ba0_reset_array ((struct ba0_array *) &dow->cont5);
  ba0_reset_array ((struct ba0_array *) &dow->cont6);
  ba0_reset_array ((struct ba0_array *) &dow->cont7);
}

/*
 * texinfo: bai_dop853_realloc_dense_output
 * Ensure that the arrays of @var{dow} can receive at least @var{n} elements.
 */

BAI_DLL void
bai_dop853_realloc_dense_output (
    struct bai_dop853_dense_output *dow,
    ba0_int_p n)
{
  ba0_realloc_table ((struct ba0_table *) &dow->index, n);
  ba0_realloc_array ((struct ba0_array *) &dow->cont0, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &dow->cont1, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &dow->cont2, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &dow->cont3, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &dow->cont4, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &dow->cont5, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &dow->cont6, n, sizeof (double));
  ba0_realloc_array ((struct ba0_array *) &dow->cont7, n, sizeof (double));
}

/*
 * Cannot actually raise BAI_ERRUNK
 */

/*
 * texinfo: bai_dop853_set_dense_output_all_variables
 * Prepare all the dependent variables of @var{S} for dense output.
 */

BAI_DLL void
bai_dop853_set_dense_output_all_variables (
    struct bai_dop853_dense_output *dow,
    struct bai_odex_system *S)
{
  ba0_int_p i;
  bai_dop853_realloc_dense_output (dow, S->lhs.size);
  for (i = 0; i < S->lhs.size; i++)
    bai_dop853_set_dense_output_variable (dow,
        bav_order_zero_variable (S->lhs.tab[i]), S);
}

/*
 * texinfo: bai_dop853_set_dense_output_variable
 * Prepare the variable @var{v} for dense output.
 * Raises exception @code{BAI_ERRUNK} if @var{v} is not a dependent 
 * variable of @var{S}.
 */

BAI_DLL void
bai_dop853_set_dense_output_variable (
    struct bai_dop853_dense_output *dow,
    struct bav_variable *v,
    struct bai_odex_system *S)
{
  ba0_int_p i;

  if (!bai_odex_is_lhs (v, S, &i))
    BA0_RAISE_EXCEPTION (BAI_ERRUNK);

  if (!ba0_member_table ((void *) i, (struct ba0_table *) &dow->index))
    {
      bai_dop853_realloc_dense_output (dow, dow->index.size + 1);
      dow->index.tab[dow->index.size++] = i;
    }
}

/*
 * texinfo: bai_dop853_set_dense_output
 * Assign @var{dow} to @var{dov}.
 */

BAI_DLL void
bai_dop853_set_dense_output (
    struct bai_dop853_dense_output *dov,
    struct bai_dop853_dense_output *dow)
{
  ba0_set_table ((struct ba0_table *) &dov->index,
      (struct ba0_table *) &dow->index);
  ba0_set_array ((struct ba0_array *) &dov->cont0,
      (struct ba0_array *) &dow->cont0);
  ba0_set_array ((struct ba0_array *) &dov->cont1,
      (struct ba0_array *) &dow->cont1);
  ba0_set_array ((struct ba0_array *) &dov->cont2,
      (struct ba0_array *) &dow->cont2);
  ba0_set_array ((struct ba0_array *) &dov->cont3,
      (struct ba0_array *) &dow->cont3);
  ba0_set_array ((struct ba0_array *) &dov->cont4,
      (struct ba0_array *) &dow->cont4);
  ba0_set_array ((struct ba0_array *) &dov->cont5,
      (struct ba0_array *) &dow->cont5);
  ba0_set_array ((struct ba0_array *) &dov->cont6,
      (struct ba0_array *) &dow->cont6);
  ba0_set_array ((struct ba0_array *) &dov->cont7,
      (struct ba0_array *) &dow->cont7);
}

/*
      FUNCTION CONTD8(II,X,CON,ICOMP,ND)
C ----------------------------------------------------------
C     THIS FUNCTION CAN BE USED FOR CONTINUOUS OUTPUT IN CONNECTION
C     WITH THE OUTPUT-SUBROUTINE FOR DOP853. IT PROVIDES AN
C     APPROXIMATION TO THE II-TH COMPONENT OF THE SOLUTION AT X.
C ----------------------------------------------------------
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
      DIMENSION CON(8*ND),ICOMP(ND)
      COMMON /CONDO8/XOLD,H
C ----- COMPUTE PLACE OF II-TH COMPONENT 
      I=0 
      DO 5 J=1,ND 
      IF (ICOMP(J).EQ.II) I=J
   5  CONTINUE
      IF (I.EQ.0) THEN
         WRITE (6,*) ' NO DENSE OUTPUT AVAILABLE FOR COMP.',II 
         RETURN
      END IF  
      S=(X-XOLD)/H
      S1=1.D0-S
      CONPAR=CON(I+ND*4)+S*(CON(I+ND*5)+S1*(CON(I+ND*6)+S*CON(I+ND*7)))
      CONTD8=CON(I)+S*(CON(I+ND)+S1*(CON(I+ND*2)+S*(CON(I+ND*3)
     &        +S1*CONPAR)))
      RETURN
      END
*/

/*
 * texinfo: bai_dop853_dense_output_evaluate
 * Interpolate the integral curve of the variable with number @var{ii}
 * between the former step (time @var{told}) and the current step (time @var{t}). 
 * Returns the value of the variable at time @var{tt}.
 * The value of @var{tt} should be in the range defined by
 * @var{told} and @var{t}.
 * The number @var{ii} must be prepared for dense output i.e. present in 
 * the field @code{index} of @code{w->dow}. If not, the exception 
 * @code{BAI_ERRDOW} is raised. 
 * This function is called by @code{bai_dop853_solout}.
 */

BAI_DLL double
bai_dop853_dense_output_evaluate (
    ba0_int_p ii,
    double tt,
    struct bai_dop853_workspace *w)
{
  struct bai_dop853_dense_output *dow = &w->dow;
  double z, s, s1, conpar, h;
  ba0_int_p i;
/*
   Looks for an index i such that dow->index [i] == ii
*/
  if (!ba0_member2_table ((void *) ii, (struct ba0_table *) &dow->index, &i))
    BA0_RAISE_EXCEPTION (BAI_ERRDOW);
/*
   The right value of h was changed by bai_dop853_step_workspace.
   We need to recompute it.
*/
  h = w->t - w->told;
  s = (tt - w->told) / h;
  s1 = 1. - s;
  conpar =
      dow->cont4.tab[i] + s * (dow->cont5.tab[i] + s1 * (dow->cont6.tab[i] +
          s * dow->cont7.tab[i]));
  z = dow->cont0.tab[i] + s * (dow->cont1.tab[i] + s1 * (dow->cont2.tab[i] +
          s * (dow->cont3.tab[i] + s1 * conpar)));
  return z;
}

/**********************************************************************
 EVALUATION FUNCTION
 **********************************************************************/

/*
 * May raise BAI_ERRDOW, BAI_EXEVAL, BAI_EXSSIZ, BAI_EXMAXS, BAI_EXSTIF
 */

static double
bai_dop853_evaluate (
    ba0_int_p i,
    double t,
    struct bai_dop853_workspace *w)
{
  double posneg;

  if (t == w->iv.t0)
    return w->iv.y0.tab[i];

  posneg = w->iv.t1 > w->iv.t0 ? 1. : -1.;

  if (t * posneg < w->told * posneg)
    bai_dop853_start_workspace (w, w->fcn, &w->iv, &w->tol, &w->control,
        &w->dow, w->params);
  while (t * posneg > w->t * posneg)
    bai_dop853_step_workspace (w);
  return bai_dop853_dense_output_evaluate (i, t, w);
}

/*
 * May raise BAI_ERRUNK, BAI_ERRDOW, BAI_EXEVAL, 
 * 					BAI_EXSSIZ, BAI_EXMAXS, BAI_EXSTIF
 */

/*
 * texinfo: bai_dop853_evaluate_variable
 * Return @math{v(t)} for any @var{t} in the range defined by @math{t_0}
 * and @math{t_1}. The variable @var{v} must be one of the dependent
 * variables of @var{S} (else exception @code{BAI_ERRUNK} is raised).
 * It must be prepared for dense output (else exception @code{BAI_ERRDOW}
 * is raised). The workspace is assumed to be initialized by
 * @code{bai_dop853_start_workspace}.
 * The function may also raise the exceptions @code{BAI_EXEVAL}, 
 * @code{BAI_EXSSIZ}, @code{BAI_EXMAXS} and @code{BAI_EXSTIF} (see above).
 * The @code{stat} field is reset at the beginning of each call.
 */

BAI_DLL double
bai_dop853_evaluate_variable (
    struct bav_variable *v,
    double t,
    struct bai_dop853_workspace *w,
    struct bai_odex_system *S)
{
  ba0_int_p i;

  if (!bai_odex_is_lhs (v, S, &i))
    BA0_RAISE_EXCEPTION (BAI_ERRUNK);
  bai_dop853_reset_stats (&w->stat);
  return bai_dop853_evaluate (i, t, w);
}
