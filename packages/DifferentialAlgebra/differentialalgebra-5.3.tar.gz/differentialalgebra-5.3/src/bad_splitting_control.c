#include "bad_splitting_control.h"
#include "bad_base_field.h"

/*
 * texinfo: bad_init_splitting_control
 * Initialize @var{C}. The fields @code{first_leaf_only} and
 * @code{DenefLipshitz} are set
 * to @code{false}. The fields @code{dimlb} and @code{apply_dimlb_one_eq}
 * are set to @code{bad_algebraic_dimension_lower_bound} and @code{true}.
 */

BAD_DLL void
bad_init_splitting_control (
    struct bad_splitting_control *S)
{
  memset (S, 0, sizeof (struct bad_splitting_control));
  S->first_leaf_only = false;
  S->dimlb = bad_algebraic_dimension_lower_bound;
  S->apply_dimlb_one_eq = true;
  S->DenefLipshitz = false;
}

/*
 * texinfo: bad_new_splitting_control
 * Allocate a new @code{struct bad_splitting_control *}, initialize it and return it.
 */

BAD_DLL struct bad_splitting_control *
bad_new_splitting_control (
    void)
{
  struct bad_splitting_control *S;

  S = (struct bad_splitting_control *) ba0_alloc (sizeof (struct
          bad_splitting_control));
  bad_init_splitting_control (S);
  return S;
}

/*
 * texinfo: bad_set_splitting_control
 * Assign @var{T} to @var{S}.
 */

BAD_DLL void
bad_set_splitting_control (
    struct bad_splitting_control *S,
    struct bad_splitting_control *T)
{
  if (S != T)
    *S = *T;
}

/*
 * texinfo: bad_set_DenefLipshitz_splitting_control
 * Assign @var{b} to the field @code{DenefLipshitz} of @var{C}.
 * If @var{b} is @code{true} then 
 * @code{first_leaf_only} and @code{apply_dimlb_one_eq} are set
 * to @code{false} and @code{dimlb} is set
 * to @code{bad_no_dimension_lower_bound}.
 */

BAD_DLL void
bad_set_DenefLipshitz_splitting_control (
    struct bad_splitting_control *S,
    bool b)
{
  S->DenefLipshitz = b;
  if (b)
    {
      bad_set_first_leaf_only_splitting_control (S, false);
      bad_set_dimension_lower_bound_splitting_control (S,
          bad_no_dimension_lower_bound, false);
    }
}

/*
 * texinfo: bad_set_first_leaf_only_splitting_control
 * Assign @var{b} to the field @code{first_leaf_only} of @var{C}.
 */

BAD_DLL void
bad_set_first_leaf_only_splitting_control (
    struct bad_splitting_control *S,
    bool b)
{
  S->first_leaf_only = b;
}

/*
 * texinfo: bad_set_dimension_lower_bound_splitting_control
 * Assign @var{lb} and @var{one_eq} to the fields
 * @code{dimlb} and @code{apply_dimlb_one_eq} of @var{C}.
 */

BAD_DLL void
bad_set_dimension_lower_bound_splitting_control (
    struct bad_splitting_control *S,
    enum bad_typeof_dimension_lower_bound lb,
    bool one_eq)
{
  S->dimlb = lb;
  S->apply_dimlb_one_eq = one_eq;
}

/*
 * texinfo: bad_apply_dimension_lower_bound_splitting_control
 * Return @code{true} if differential elimination methods
 * must discard any output regular differential chain involving
 * more than the number of input equations.
 *
 * The decision depends on @var{S}, the number of input equations,
 * and the number of derivations involved in our problem and
 * whether the elimination process is differential or not
 * (information in @var{differential}).
 *
 * The number of input equations is defined as the size
 * of @var{C} plus the size of @var{eqns} plus the number
 * of implicit equations associated to the parameters occurring
 * in their polynomials which are not leaders.
 * This number is returned in *@var{numberof_input_equations}.
 */

BAD_DLL bool
bad_apply_dimension_lower_bound_splitting_control (
    struct bad_splitting_control *S,
    struct bad_regchain *C,
    struct bap_listof_polynom_mpz *eqns,
    struct bad_base_field *K,
    bool differential,
    ba0_int_p *numberof_input_equations)
{
  struct bav_dictionary_symbol dict_pars;
  struct bav_tableof_symbol pars;
  struct bav_tableof_variable T;
  struct bap_polynom_mpz *P;
  struct bav_variable *u;
  struct bap_listof_polynom_mpz *L;
  struct ba0_mark M;
  ba0_int_p i, n, nbders;
  bool b;
/*
 * First compute n = numberof_input_equations and
 *          nbders = the number of derivations involved in the problem
 */
  ba0_record (&M);
  bav_init_dictionary_symbol (&dict_pars, 8);
  ba0_init_table ((struct ba0_table *) &pars);
  ba0_realloc_table ((struct ba0_table *) &pars, 256);
  ba0_init_table ((struct ba0_table *) &T);
  ba0_realloc_table ((struct ba0_table *) &T, bav_global.R.ders.size);

  n = 0;
  nbders = 0;
/*
 * First loop on the elements of C, skipping elements of C in K
 */
  i = C->decision_system.size - 1;
  if (i >= 0)
    {
      P = C->decision_system.tab[i];
      u = bap_leader_polynom_mpz (P);
    }
  while (i >= 0 && !bad_member_variable_base_field (u, K))
    {
      if (differential)
        {
          bap_involved_parameters_polynom_mpz (&dict_pars, &pars, P);
          bap_involved_derivations_polynom_mpz (&T, P);
        }

      n += 1;
      i -= 1;
      if (i >= 0)
        {
          P = C->decision_system.tab[i];
          u = bap_leader_polynom_mpz (P);
        }
    }
/*
 * Then loop on the elements of L, which should not be elements of K
 */
  for (L = eqns; L != (struct bap_listof_polynom_mpz *) 0; L = L->next)
    {
      P = L->value;
      if (differential)
        {
          bap_involved_parameters_polynom_mpz (&dict_pars, &pars, P);
          bap_involved_derivations_polynom_mpz (&T, P);
        }
      n += 1;
    }
/*
 * What about the parameters?
 * The number of implicit equations introduced by a parameter
 *      is the number of derivations minus the size of its dependencies
 * Moreover, the derivations with respect to which the parameter is zero
 *      (the ones which are not in the dependencies) may introduce new
 *      derivations in the table T of the derivations involved in our system
 */
  for (i = 0; i < pars.size; i++)
    {
      struct bav_parameter *p;
      ba0_int_p j;

      bav_is_a_parameter (pars.tab[i], &p);

      n += bav_global.R.ders.size - p->dependencies.size;

      for (j = 0; j < bav_global.R.ders.size; j++)
        {
          if (!ba0_member_table ((void *) j, (struct ba0_table *)
                  &p->dependencies))
            {
              struct bav_variable *x = bav_derivation_index_to_derivation (j);
              if (!ba0_member_table (x, (struct ba0_table *) &T))
                {
                  T.tab[T.size] = x;
                  T.size += 1;
                }
            }
        }
    }
/*
 * Then
 */
  nbders = T.size;
  *numberof_input_equations = n;
/*
 * go
 */
  if (S->dimlb == bad_no_dimension_lower_bound)
    {
/*
 * bad_no_dimension_lower_bound overrides apply_dimlb_one_eq
 */
      b = false;
    }
  else if (*numberof_input_equations == 1 && S->apply_dimlb_one_eq)
    {
/*
 * The case of a single equation
 */
      b = true;
    }
  else
    {
      switch (S->dimlb)
        {
        case bad_no_dimension_lower_bound:
          b = false;
          break;
        case bad_algebraic_dimension_lower_bound:
/*
 * One may perform a non-differential decomposition over a differential system
 */
          if (!differential)
            b = true;
          else if (nbders == 0)
            b = true;
          else
            b = false;
          break;
        case bad_ode_dimension_lower_bound:
          if (nbders <= 1)
            b = true;
          else
            b = false;
          break;
        case bad_pde_dimension_lower_bound:
          b = true;
          break;
        }
    }
  ba0_restore (&M);
  return b;
}
