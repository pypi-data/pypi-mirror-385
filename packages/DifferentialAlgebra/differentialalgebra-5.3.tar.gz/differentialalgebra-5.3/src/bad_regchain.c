#include "bad_regchain.h"
#include "bad_quench_regchain.h"
#include "bad_regularize.h"
#include "bad_intersectof_regchain.h"
#include "bad_reduction.h"
#include "bad_global.h"
#include "bad_invert.h"

/****************************************************************************
 CONSTRUCTORS AND RELATED FUNCTIONS
 ****************************************************************************/

/*
 * texinfo: bad_init_regchain
 * Initialize @var{C} to the empty chain.
 */

BAD_DLL void
bad_init_regchain (
    struct bad_regchain *C)
{
  C->number = BAD_NOT_A_NUMBER;
  bad_init_attchain (&C->attrib);
  ba0_init_table ((struct ba0_table *) &C->decision_system);
/*
    ba0_init_table ((struct ba0_table *)&C->simplification_system);
*/
}

/*
 * texinfo: bad_reset_regchain
 * Reset @var{C} to the empty chain.
 */

BAD_DLL void
bad_reset_regchain (
    struct bad_regchain *C)
{
  bad_reset_attchain (&C->attrib);
  ba0_reset_table ((struct ba0_table *) &C->decision_system);
/*
    ba0_reset_table ((struct ba0_table *)&C->simplification_system);
*/
}

/*
 * texinfo: bad_new_regchain
 * Allocate a new regular chain, initialize it and return it.
 */

BAD_DLL struct bad_regchain *
bad_new_regchain (
    void)
{
  struct bad_regchain *C;

  C = (struct bad_regchain *) ba0_alloc (sizeof (struct bad_regchain));
  bad_init_regchain (C);
  return C;
}

/*
 * texinfo: bad_realloc_regchain
 * Realloc the decision system of @var{C} so that
 * it can receive at least @var{n} polynomials.
 * Existing elements are preserved.
 */

BAD_DLL void
bad_realloc_regchain (
    struct bad_regchain *C,
    ba0_int_p n)
{
  ba0_realloc2_table ((struct ba0_table *) &C->decision_system, n,
      (ba0_new_function *) & bap_new_polynom_mpz);
/*
    ba0_realloc2_table
	((struct ba0_table *)&C->simplification_system, m,
				(ba0_new_function*)&bap_new_polynom_mpz);
*/
}

/*
 * texinfo: bad_extend_regchain
 * Append the polynomials of @var{B} to @var{A}.
 * If @var{A} is empty, assign the properties of @var{B} to @var{A}.
 * Exception @code{BAD_ERRCRC} is raised if @var{B} is not compatible
 * with @var{A} (see @code{bad_is_a_compatible_regchain}) or if
 * the lowest leader of @var{B} is less than or equal to the highest
 * leader of @var{A}.
 */

BAD_DLL void
bad_extend_regchain (
    struct bad_regchain *A,
    struct bad_regchain *B)
{
  bool A_is_empty;
  ba0_int_p i;

  if (!bad_is_a_compatible_regchain (B, &A->attrib))
    BA0_RAISE_EXCEPTION (BAD_ERRCRC);

  if (bad_is_zero_regchain (B))
    return;

  A_is_empty = bad_is_zero_regchain (A);
  if (!A_is_empty)
    {
      struct bav_variable *v;
      struct bav_variable *w;

      v = bap_leader_polynom_mpz
          (A->decision_system.tab[A->decision_system.size - 1]);
      w = bap_leader_polynom_mpz (B->decision_system.tab[0]);
      if (bav_variable_number (v) >= bav_variable_number (w))
        BA0_RAISE_EXCEPTION (BAD_ERRCRC);
    }

  bad_realloc_regchain (A, A->decision_system.size + B->decision_system.size);
  for (i = 0; i < B->decision_system.size; i++)
    {
      bap_set_polynom_mpz (A->decision_system.tab[A->decision_system.size],
          B->decision_system.tab[i]);
      A->decision_system.size += 1;
    }

  if (A_is_empty)
    bad_set_attchain (&A->attrib, &B->attrib);
}

/*
 * texinfo: bad_set_regchain
 * Assign @var{B} to @var{A}.
 */

BAD_DLL void
bad_set_regchain (
    struct bad_regchain *A,
    struct bad_regchain *B)
{
  ba0_int_p i;

  if (A == B)
    return;

  bav_push_ordering (B->attrib.ordering);

  bad_realloc_regchain (A, B->decision_system.size);
  for (i = 0; i < B->decision_system.size; i++)
    bap_set_polynom_mpz (A->decision_system.tab[i], B->decision_system.tab[i]);
  A->decision_system.size = B->decision_system.size;

  bad_set_attchain (&A->attrib, &B->attrib);

  bav_pull_ordering ();
}

/*
 * texinfo: bad_fast_primality_test_regchain
 * Set the @code{bad_prime_ideal_property} of @var{C}, if @var{C}
 * is proven (after a fast test) to define a prime ideal.
 */

BAD_DLL void
bad_fast_primality_test_regchain (
    struct bad_regchain *C)
{
  bool b;

  b = bad_is_zero_regchain (C);
  if (!b && bad_is_explicit_regchain (C))
    bad_set_property_attchain (&C->attrib, bad_prime_ideal_property);
  else if (b)
    bad_clear_property_attchain (&C->attrib, bad_prime_ideal_property);
}

/*
 * texinfo: bad_is_a_compatible_regchain
 * Return @code{true} if @var{C} can be included as is in a regular
 * chain having properties @var{attrib}. 
 * The orderings must be the same and every property of @var{attrib}
 * must be a property of @var{C}.
 */

BAD_DLL bool
bad_is_a_compatible_regchain (
    struct bad_regchain *C,
    struct bad_attchain *attrib)
{
/*
 * If C is empty then it is okay
 */
  if (C->decision_system.size == 0)
    return true;
/*
 * Orderings must be the same
 */
  if (C->attrib.ordering != attrib->ordering)
    return false;
/*  
 * If attrib holds the differential ideal property then C also
 */
  if (bad_has_property_attchain (attrib, bad_differential_ideal_property)
      && !bad_defines_a_differential_ideal_regchain (C))
    return false;
/*
 * If attrib holds the prime ideal property then C also
 */
  if (bad_has_property_attchain (attrib, bad_prime_ideal_property))
    {
      if (!bad_defines_a_prime_ideal_regchain (C) &&
          !bad_is_explicit_regchain (C))
        return false;
    }
/*
 * Each desired property of attrib must be held by C
 */
  if (bad_has_property_attchain (attrib, bad_coherence_property)
      && !bad_has_property_regchain (C, bad_coherence_property))
    return false;
  if (bad_has_property_attchain (attrib, bad_autoreduced_property)
      && !bad_has_property_regchain (C, bad_autoreduced_property))
    return false;
  if (bad_has_property_attchain (attrib, bad_squarefree_property)
      && !bad_has_property_regchain (C, bad_squarefree_property))
    return false;
  if (bad_has_property_attchain (attrib, bad_primitive_property)
      && !bad_has_property_regchain (C, bad_primitive_property))
    return false;
  if (bad_has_property_attchain (attrib, bad_normalized_property)
      && !bad_has_property_regchain (C, bad_normalized_property))
    return false;
  return true;
}

/*
 * C must be [non empty,] free of independent polynomials, triangular
 * differential => differentially triangular
 */

static void
bad_check_consistency_regchain (
    struct bad_regchain *C)
{
  struct bav_variable *u, *v;
  ba0_int_p i, j;

  for (i = 0; i < C->decision_system.size; i++)
    if (bap_is_independent_polynom_mpz (C->decision_system.tab[i]))
      BA0_RAISE_EXCEPTION (BAD_ERRNRC);

  for (i = 0; i < C->decision_system.size; i++)
    {
      u = bap_leader_polynom_mpz (C->decision_system.tab[i]);
      for (j = i + 1; j < C->decision_system.size; j++)
        {
          v = bap_leader_polynom_mpz (C->decision_system.tab[j]);
          if (u == v)
            BA0_RAISE_EXCEPTION (BAD_ERRNRC);
          if (bad_defines_a_differential_ideal_regchain (C)
              && (bav_is_derivative (u, v) || bav_is_derivative (v, u)))
            BA0_RAISE_EXCEPTION (BAD_ERRNRC);
        }
    }
}

/*
 * texinfo: bad_set_regchain_tableof_polynom_mpz
 * Assign to @var{C} the table @var{T} with properties
 * given in @var{properties} plus some other ones
 * (see @code{bad_set_automatic_properties_attchain}).
 * 
 * The table @var{T} does not need to be sorted.
 * If the boolean @var{pretend} is @code{true}, then that's all.
 * 
 * Otherwise, the function checks that the polynomials depend
 * on dependent variables and form a triangular set (and a 
 * differentially triangular one in the differential case).
 * If they do not, exception @code{BAD_ERRNRC} is raised.
 * Lastly, the function @code{bad_quench_regchain} is called to make the 
 * regular chain hold the properties with the exception of the
 * coherence, prime ideal and differential ideal properties. 
 * This function may raise the exceptions @code{BAD_EXRCNC}
 * or @code{BAD_EXRDDZ}.
 */

BAD_DLL void
bad_set_regchain_tableof_polynom_mpz (
    struct bad_regchain *C,
    struct bap_tableof_polynom_mpz *T,
    struct ba0_tableof_string *properties,
    bool pretend)
{
  ba0_int_p i;
/*
 * Set. T may actually be C->decision_system
 */
  if (&C->decision_system != T)
    {
      bad_realloc_regchain (C, T->size);
      for (i = 0; i < T->size; i++)
        bap_set_polynom_mpz (C->decision_system.tab[i], T->tab[i]);
      C->decision_system.size = T->size;
    }
/*
 * Sort decision_system before checking
 */
  qsort (C->decision_system.tab, C->decision_system.size,
      sizeof (struct bap_polynom_mpz *), &bap_compare_rank_polynom_mpz);
/*
 * Set the properties (+ automatic)
 */
  bad_set_properties_attchain (&C->attrib, properties);
  bad_set_automatic_properties_attchain (&C->attrib);

  if (!pretend)
    {
      struct bad_base_field K0;
      struct bad_quench_map map;
      struct ba0_mark M;

      bad_init_base_field (&K0);

      bad_check_consistency_regchain (C);

      ba0_push_another_stack ();
      ba0_record (&M);
      bad_init_quench_map (&map, C);
      ba0_pull_stack ();

      bad_quench_regchain (C, &map, (struct bav_tableof_term *) 0, (bool *) 0,
          C, &K0, (struct bap_polynom_mpz * *) 0);

      ba0_restore (&M);
    }
}

/*
 * texinfo: bad_set_regchain_tableof_ratfrac_mpz
 * Apply @code{bad_set_regchain_tableof_polynom_mpz}
 * over the set of numerators of the rational fractions.
 * See that function.
 */

BAD_DLL void
bad_set_regchain_tableof_ratfrac_mpz (
    struct bad_regchain *C,
    struct baz_tableof_ratfrac *T,
    struct ba0_tableof_string *properties,
    bool pretend)
{
  struct baz_ratfrac R;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_push_another_stack ();
  ba0_record (&M);
  baz_init_ratfrac (&R);
  ba0_pull_stack ();

  bad_realloc_regchain (C, T->size);
  for (i = 0; i < T->size; i++)
    {
      ba0_push_another_stack ();
      baz_reduce_ratfrac (&R, T->tab[i]);
      ba0_pull_stack ();
      baz_numer_ratfrac (C->decision_system.tab[i], &R);
    }
  C->decision_system.size = T->size;

  bad_set_regchain_tableof_polynom_mpz (C, &C->decision_system, properties,
      pretend);
}

/*
 * texinfo: bad_set_number_regchain
 * Assign @var{number} to the field @code{number} of @var{C}.
 */

BAD_DLL void
bad_set_number_regchain (
    struct bad_regchain *C,
    ba0_int_p number)
{
  C->number = number;
}

/*
 * texinfo: bad_get_number_regchain
 * Return the value of the field @code{number} of @var{C}.
 */

BAD_DLL ba0_int_p
bad_get_number_regchain (
    struct bad_regchain *C)
{
  return C->number;
}

/*
 * texinfo: bad_set_property_regchain
 * Set property @var{prop} of @var{C}.
 */

BAD_DLL void
bad_set_property_regchain (
    struct bad_regchain *C,
    enum bad_property_attchain prop)
{
  bad_set_property_attchain (&C->attrib, prop);
}

/*
 * texinfo: bad_clear_property_regchain
 * Clear property @var{prop} of @var{C}.
 */

BAD_DLL void
bad_clear_property_regchain (
    struct bad_regchain *C,
    enum bad_property_attchain prop)
{
  bad_clear_property_attchain (&C->attrib, prop);
}

/*
 * texinfo: bad_set_properties_regchain
 * Set the properties of @var{C} with @var{T}.
 * Do not set properties automatically 
 * (see @code{bad_set_automatic_properties_attchain}).
 */

BAD_DLL void
bad_set_properties_regchain (
    struct bad_regchain *C,
    struct ba0_tableof_string *T)
{
  bad_set_properties_attchain (&C->attrib, T);
}

/*
 * texinfo: bad_set_automatic_properties_regchain
 * Set the automatic properties of @var{C}.
 * See @code{bad_set_automatic_properties_attchain}.
 */

BAD_DLL void
bad_set_automatic_properties_regchain (
    struct bad_regchain *C)
{
  bad_set_automatic_properties_attchain (&C->attrib);
}

/*
 * texinfo: bad_has_property_regchain
 * Return @code{true} if @var{C} has the property @var{P}.
 */

BAD_DLL bool
bad_has_property_regchain (
    struct bad_regchain *C,
    enum bad_property_attchain P)
{
  return bad_has_property_attchain (&C->attrib, P);
}

/*
 * texinfo: bad_properties_regchain
 * Assign to @var{properties} the properties of @var{C}.
 */

BAD_DLL void
bad_properties_regchain (
    struct ba0_tableof_string *properties,
    struct bad_regchain *C)
{
  bad_properties_attchain (properties, &C->attrib);
}

/*
 * texinfo: bad_defines_a_differential_ideal_regchain
 * Return @code{true} if @var{C} holds the 
 * @code{bad_differential_ideal_property} else @code{false}.
 */

BAD_DLL bool
bad_defines_a_differential_ideal_regchain (
    struct bad_regchain *C)
{
  return bad_defines_a_differential_ideal_attchain (&C->attrib);
}

/*
 * texinfo: bad_defines_a_prime_ideal_regchain
 * Return @code{true} if @var{C} holds the @code{bad_prime_ideal_property}
 * else @code{false}.
 */

BAD_DLL bool
bad_defines_a_prime_ideal_regchain (
    struct bad_regchain *C)
{
  return bad_defines_a_prime_ideal_attchain (&C->attrib);
}

/*
 * texinfo: bad_sort_regchain
 * Assign to @var{A} the regular chain obtained by sorting the polynomials
 * of @var{B} with respect to the current ordering. 
 * The elements of @var{A} are readonly.
 * Properties of @var{B} become properties of @var{A}.
 */

BAD_DLL void
bad_sort_regchain (
    struct bad_regchain *A,
    struct bad_regchain *B)
{
  ba0_int_p i;

  if (A != B)
    {
      bad_reset_regchain (A);
      bad_realloc_regchain (A, B->decision_system.size);
      for (i = 0; i < B->decision_system.size; i++)
        bap_sort_polynom_mpz (A->decision_system.tab[i],
            B->decision_system.tab[i]);
      A->decision_system.size = B->decision_system.size;
      A->attrib.ordering = bav_current_ordering ();
      A->attrib.property = B->attrib.property;
    }
  else
    {
      for (i = 0; i < A->decision_system.size; i++)
        bap_sort_polynom_mpz (A->decision_system.tab[i],
            A->decision_system.tab[i]);
      A->attrib.ordering = bav_current_ordering ();
    }
}

/*
 * texinfo: bad_inequations_regchain
 * Assign to @var{res} the initials and separants of @var{C}.
 * Numeric polynomials are discarded. 
 * Polynomials are made primitive. 
 * Redundant polynomials are discarded.
 * Some polynomials may be factored by means of
 * @code{baz_factor_easy_polynom_mpz}.
 */

BAD_DLL void
bad_inequations_regchain (
    struct bap_tableof_polynom_mpz *res,
    struct bad_regchain *C)
{
  struct bap_tableof_polynom_mpz ineqs;
  struct bap_polynom_mpz init, sep;
  struct bap_product_mpz prod;
  struct ba0_tableof_bool keep;
  struct ba0_mark M;
  ba0_int_p i, k, l;
  bool found;

  ba0_push_another_stack ();
  ba0_record (&M);
  bap_init_product_mpz (&prod);
  bap_init_readonly_polynom_mpz (&init);
  bap_init_polynom_mpz (&sep);
  ba0_init_table ((struct ba0_table *) &ineqs);
  ba0_init_table ((struct ba0_table *) &keep);

  for (i = 0; i < C->decision_system.size; i++)
    {
      bap_initial_polynom_mpz (&init, C->decision_system.tab[i]);
      if (!bap_is_numeric_polynom_mpz (&init))
        {
          baz_factor_easy_polynom_mpz (&prod, &keep, &init, 0);
          for (k = 0; k < prod.size; k++)
            {
              found = false;
              for (l = 0; l < ineqs.size && !found; l++)
                found =
                    bap_equal_polynom_mpz (&prod.tab[k].factor, ineqs.tab[l]);
              if (!found)
                {
                  if (ineqs.size >= ineqs.alloc)
                    ba0_realloc2_table ((struct ba0_table *) &ineqs,
                        2 * ineqs.size + 1,
                        (ba0_new_function *) & bap_new_polynom_mpz);
                  bap_set_polynom_mpz (ineqs.tab[ineqs.size],
                      &prod.tab[k].factor);
                  ineqs.size += 1;
                }
            }
        }
    }
  for (i = 0; i < C->decision_system.size; i++)
    {
      if (bap_leading_degree_polynom_mpz (C->decision_system.tab[i]) > 1)
        {
          bap_separant_polynom_mpz (&sep, C->decision_system.tab[i]);
          bap_normal_numeric_primpart_polynom_mpz (&sep, &sep);
          found = false;
          for (l = 0; l < ineqs.size && !found; l++)
            {
              if (bap_is_factor_polynom_mpz (&sep, ineqs.tab[l], &sep))
                found = bap_is_numeric_polynom_mpz (&sep);
            }
          if (!found)
            {
              if (ineqs.size >= ineqs.alloc)
                ba0_realloc2_table ((struct ba0_table *) &ineqs,
                    2 * ineqs.size + 1,
                    (ba0_new_function *) & bap_new_polynom_mpz);
              bap_set_polynom_mpz (ineqs.tab[ineqs.size], &sep);
              ineqs.size += 1;
            }
        }
    }

  ba0_pull_stack ();

  res->size = 0;
  ba0_realloc2_table ((struct ba0_table *) res, ineqs.size,
      (ba0_new_function *) & bap_new_polynom_mpz);
  for (i = 0; i < ineqs.size; i++)
    {
      bap_set_polynom_mpz (res->tab[res->size], ineqs.tab[i]);
      res->size += 1;
    }
  ba0_restore (&M);
}

/*
 * texinfo: bad_scanf_regchain
 * A parsing function for regular chains.
 * It is called by @code{ba0_scanf/%regchain}.
 * The parsed string is expected to have the form
 * @code{regchain ([rational fractions], [properties])}.
 * The input list of rational fractions needs not be sorted.
 * The function checks that the numerators of @var{ratfrac} 
 * form a regular chain.
 * It calls @code{bad_quench_regchain} to make the chain
 * satisfy the properties listed in @var{property}
 * except the coherence, prime ideal and differential ideal properties.
 */

BAD_DLL void *
bad_scanf_regchain (
    void *A)
{
  struct bad_regchain *C;
  struct baz_tableof_ratfrac *ratfrac;
  struct ba0_tableof_string *properties;
  struct ba0_mark M;

  if (A == (void *) 0)
    C = bad_new_regchain ();
  else
    {
      C = (struct bad_regchain *) A;
      bad_reset_attchain (&C->attrib);
    }

  ba0_push_another_stack ();
  ba0_record (&M);
  ratfrac = (struct baz_tableof_ratfrac *) ba0_new_table ();
  properties = (struct ba0_tableof_string *) ba0_new_table ();
  ba0_scanf ("regchain (%t[%simplify_Qz], %t[%s])", ratfrac, properties);
  ba0_pull_stack ();
  bad_set_regchain_tableof_ratfrac_mpz (C, ratfrac, properties, false);
  ba0_restore (&M);
  return C;
}

/*
 * texinfo: bad_scanf_pretend_regchain
 * A parsing function for regular chains.
 * It is called by @code{ba0_scanf/%pretend_regchain}.
 * The parsed string is expected to have the form
 * @code{regchain ([rational fractions], [properties])}.
 * The input list of rational fractions needs not be sorted.
 * The regular chain property of the resulting list is not checked.
 */

BAD_DLL void *
bad_scanf_pretend_regchain (
    void *A)
{
  struct bad_regchain *C;
  struct baz_tableof_ratfrac *ratfrac;
  struct ba0_tableof_string *properties;
  struct ba0_mark M;

  if (A == (void *) 0)
    C = bad_new_regchain ();
  else
    {
      C = (struct bad_regchain *) A;
      bad_reset_attchain (&C->attrib);
    }

  ba0_push_another_stack ();
  ba0_record (&M);
  ratfrac = (struct baz_tableof_ratfrac *) ba0_new_table ();
  properties = (struct ba0_tableof_string *) ba0_new_table ();
  ba0_scanf ("regchain (%t[%Qz], %t[%s])", ratfrac, properties);
  ba0_pull_stack ();
  bad_set_regchain_tableof_ratfrac_mpz (C, ratfrac, properties, true);
  ba0_restore (&M);
  return C;
}

/*
 * texinfo: bad_printf_regchain
 * A printing function for regular chains.
 * It is called by @code{ba0_printf/%regchain}.
 * The output format is @code{regchain ([rational fractions], [properties])}.
 */

BAD_DLL void
bad_printf_regchain (
    void *A)
{
  struct bad_regchain *C = (struct bad_regchain *) A;
  struct ba0_tableof_string *P;
  struct ba0_mark M;

  ba0_record (&M);

  P = (struct ba0_tableof_string *) ba0_new_table ();
  bad_properties_attchain (P, &C->attrib);
  ba0_printf ("regchain (%t[%Az], %t[%s])", &C->decision_system, P);

  ba0_restore (&M);
}

/*
 * texinfo: bad_printf_regchain_equations
 * A printing function for regular chains.
 * It is called by @code{ba0_printf/%regchain_equations}.
 * The output format is the one of a table of polynomials.
 */

BAD_DLL void
bad_printf_regchain_equations (
    void *A)
{
  struct bad_regchain *C = (struct bad_regchain *) A;

  ba0_printf ("%t[%Az]", &C->decision_system);
}

/*
 * Readonly static data
 */

static char _regchain[] = "struct bad_regchain";
static char _regchain_decision[] = "struct bad_regchain *->decision_system.tab";

BAD_DLL ba0_int_p
bad_garbage1_regchain (
    void *A,
    enum ba0_garbage_code code)
{
  struct bad_regchain *C = (struct bad_regchain *) A;
  ba0_int_p i, n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (C, sizeof (struct bad_regchain), _regchain);

  if (C->decision_system.alloc > 0)
    {
      n += ba0_new_gc_info (C->decision_system.tab,
          C->decision_system.alloc * sizeof (struct bap_polynom_mpz *),
          _regchain_decision);

      for (i = 0; i < C->decision_system.alloc; i++)
        n += bap_garbage1_polynom_mpz (C->decision_system.tab[i], ba0_isolated);
    }
  return n;
}

BAD_DLL void *
bad_garbage2_regchain (
    void *A,
    enum ba0_garbage_code code)
{
  struct bad_regchain *C;
  ba0_int_p i;

  if (code == ba0_isolated)
    C = (struct bad_regchain *) ba0_new_addr_gc_info (A, _regchain);
  else
    C = (struct bad_regchain *) A;

  if (C->decision_system.alloc > 0)
    {
      C->decision_system.tab =
          (struct bap_polynom_mpz *
          *) ba0_new_addr_gc_info (C->decision_system.tab, _regchain_decision);

      for (i = 0; i < C->decision_system.alloc; i++)
        C->decision_system.tab[i] =
            bap_garbage2_polynom_mpz (C->decision_system.tab[i], ba0_isolated);
    }
  return C;
}

BAD_DLL void *
bad_copy_regchain (
    void *A)
{
  struct bad_regchain *B;
  struct bad_regchain *C = (struct bad_regchain *) A;

  B = bad_new_regchain ();
  bad_set_regchain (B, C);
  return B;
}

/****************************************************************************
 PREDICATES
 ****************************************************************************/

/*
 * texinfo: bad_is_rank_of_regchain
 * Return @code{true} if @var{rg} is the rank of some element of @var{C}.
 * If so and @var{i} is not the zero pointer, @var{i} receives the index of 
 * the element.
 */

BAD_DLL bool
bad_is_rank_of_regchain (
    struct bav_rank *rg,
    struct bad_regchain *C,
    ba0_int_p *i)
{
  ba0_int_p k;
  bool b;

  bav_push_ordering (C->attrib.ordering);
  if (!bad_is_leader_of_regchain (rg->var, C, &k))
    b = false;
  else if (rg->deg !=
      bap_leading_degree_polynom_mpz (C->decision_system.tab[k]))
    b = false;
  else
    {
      if (i != (ba0_int_p *) 0)
        *i = k;
      b = true;
    }
  bav_pull_ordering ();
  return b;
}

/*
 * texinfo: bad_is_leader_of_regchain
 * Return @code{true} if @var{v} is the leading derivative of some
 * element of @var{C}. 
 * If so and @var{i} is not the zero pointer, *@var{i} receives the index of
 * the element.
 */

BAD_DLL bool
bad_is_leader_of_regchain (
    struct bav_variable *v,
    struct bad_regchain *C,
    ba0_int_p *i)
{
  bool b;
  ba0_int_p k;

  bav_push_ordering (C->attrib.ordering);
  b = false;
  for (k = 0; (!b) && k < C->decision_system.size; k++)
    {
      if (v == bap_leader_polynom_mpz (C->decision_system.tab[k]))
        {
          if (i != (ba0_int_p *) 0)
            *i = k;
          b = true;
        }
    }
  bav_pull_ordering ();
  return b;
}

/*
 * texinfo: bad_depends_on_leader_of_regchain
 * Return @code{true} if @var{A} depends on the leader of some
 * element of @var{C}, else @code{false}.
 */

BAD_DLL bool
bad_depends_on_leader_of_regchain (
    struct bap_polynom_mpz *A,
    struct bad_regchain *C)
{
  bool b;

  b = false;
  for (int k = 0; (!b) && k < A->total_rank.size; k++)
    b = bad_is_leader_of_regchain (A->total_rank.rg[k].var, C, (ba0_int_p *) 0);
  return b;
}

/*
 * texinfo: bad_leaders_of_regchain
 * Store in @var{leaders} the leaders of the @code{decision_system}
 * field of @var{A}.
 */

BAD_DLL void
bad_leaders_of_regchain (
    struct bav_tableof_variable *leaders,
    struct bad_regchain *C)
{
  ba0_int_p i;

  ba0_reset_table ((struct ba0_table *) leaders);
  ba0_realloc_table ((struct ba0_table *) leaders, C->decision_system.size);
  for (i = 0; i < C->decision_system.size; i++)
    leaders->tab[i] = bap_leader_polynom_mpz (C->decision_system.tab[i]);
  leaders->size = C->decision_system.size;
}


/*
 * texinfo: bad_is_derivative_of_leader_of_regchain
 * Return @code{true} if @var{v} is a derivative of the leading derivative
 * of some element of @var{C}. 
 * If so and @var{i} is not the zero pointer, *@var{i} receives the index of
 * the element.
 */

BAD_DLL bool
bad_is_derivative_of_leader_of_regchain (
    struct bav_variable *v,
    struct bad_regchain *C,
    ba0_int_p *i)
{
  struct bav_variable *w;
  bool b;
  ba0_int_p k;

  bav_push_ordering (C->attrib.ordering);
  b = false;
  for (k = 0; k < C->decision_system.size && (!b); k++)
    {
      w = bap_leader_polynom_mpz (C->decision_system.tab[k]);
      if (bav_is_derivative (v, w))
        {
          if (i != (ba0_int_p *) 0)
            *i = k;
          b = true;
        }
    }
  bav_pull_ordering ();
  return b;
}

/*
 * texinfo: bad_mark_indets_regchain
 * Append to @var{vars} the variables occurring in @var{C} which
 * are not already present in @var{vars}.
 * Every element of @var{vars} is supposed to be registered in
 * the dictionary @var{dict}.
 */

BAD_DLL void
bad_mark_indets_regchain (
    struct bav_dictionary_variable *dict,
    struct bav_tableof_variable *vars,
    struct bad_regchain *C)
{
  bap_mark_indets_tableof_polynom_mpz (dict, vars, &C->decision_system);
}

/*
 * texinfo: bad_is_solved_regchain
 * Return @code{true} if @var{C} could be written as
 * @math{p(x_1) = 0}, @math{x_2 = f_2(x_1)}, @dots{}, @math{x_n = f_n(x_1)}
 * where @math{p} and the @math{f_i} are polynomials.
 */

BAD_DLL bool
bad_is_solved_regchain (
    struct bad_regchain *C)
{
  struct bav_variable *x;
  struct bap_tableof_polynom_mpz *T;
  ba0_int_p i;

  T = &C->decision_system;
  if (T->size == 0 || T->tab[0]->total_rank.size > 1)
    return false;
  x = bap_leader_polynom_mpz (T->tab[0]);
  for (i = 1; i < T->size; i++)
    {
      if (!bap_is_solved_polynom_mpz (T->tab[i]))
        return false;
      if (T->tab[i]->total_rank.size > 2 || (T->tab[i]->total_rank.size == 2
              && !bap_depend_polynom_mpz (T->tab[i], x)))
        return false;
    }
  return true;
}

/*
 * texinfo: bad_is_orthonomic_regchain
 * Return @code{true} if the elements of @var{C} have leading degrees @math{1}
 * and initials in @var{K}.
 */

BAD_DLL bool
bad_is_orthonomic_regchain (
    struct bad_regchain *C,
    struct bad_base_field *K)
{
  struct bap_polynom_mpz init;
  ba0_int_p i;
  bool b;

  bap_init_readonly_polynom_mpz (&init);
  b = true;
  for (i = 0; b && i < C->decision_system.size; i++)
    {
      if (bap_leading_degree_polynom_mpz (C->decision_system.tab[i]) != 1)
        b = false;
      else
        {
          bap_initial_polynom_mpz (&init, C->decision_system.tab[i]);
          if (!bap_is_numeric_polynom_mpz (&init))
            {
              struct bav_variable *u = bap_leader_polynom_mpz (&init);
              b = bad_member_variable_base_field (u, K);
            }
        }
    }
  return b;
}

/*
 * texinfo: bad_is_explicit_regchain
 * Return @code{true} if the elements of @var{C} have leading degrees @math{1}.
 */

BAD_DLL bool
bad_is_explicit_regchain (
    struct bad_regchain *C)
{
  ba0_int_p i;

  for (i = 0; i < C->decision_system.size; i++)
    if (bap_leading_degree_polynom_mpz (C->decision_system.tab[i]) != 1)
      return false;
  return true;
}

/*
 * texinfo: bad_is_zero_regchain
 * Return @code{true} if @var{C} is empty.
 */

BAD_DLL bool
bad_is_zero_regchain (
    struct bad_regchain *C)
{
  return C->decision_system.size == 0;
}

/*
 * texinfo: bad_product_of_leading_degrees_regchain
 * Return the product of the leading degrees of the elements of @var{C}.
 */

BAD_DLL ba0_int_p
bad_product_of_leading_degrees_regchain (
    struct bad_regchain *C)
{
  ba0_int_p r, i;

  r = 1;
  for (i = 0; i < C->decision_system.size; i++)
    r *= bap_leading_degree_polynom_mpz (C->decision_system.tab[i]);
  return r;
}


/************************************************************************
 MISCELLANEOUS FUNCTIONS
 ************************************************************************/

/*
 * texinfo: bad_ordering_eliminating_leaders_of_regchain
 * Return an ordering @var{r} with respect to which the leaders of the elements of @var{C}
 * are greater than any other variable. The ordering is not necessarily
 * a ranking in the sense of Kolchin. The ordering between the leaders on
 * the one hand and and other variables on the other hand are preserved.
 * This function does not change the current ordering.
 */

BAD_DLL bav_Iordering
bad_ordering_eliminating_leaders_of_regchain (
    struct bad_regchain *C)
{
  bav_Iordering r;
  ba0_int_p i;

  r = bav_R_copy_ordering (C->attrib.ordering);
  bav_push_ordering (r);
  for (i = 0; i < C->decision_system.size; i++)
    bav_R_set_maximal_variable (bap_leader_polynom_mpz (C->
            decision_system.tab[i]));
  bav_pull_ordering ();
  return r;
}

/*
 * texinfo: bad_codimension_regchain
 * Return the codimension (differential or not, depending if @var{C} holds
 * the @code{bad_differential_ideal_property}) of the ideal
 * defined by @var{C} over the field @var{K}. 
 *
 * Differential polynomials are assumed to have coefficients in @var{K}. 
 * In the algebraic case, the codimension is just the number
 * of equations of @var{C} which do not belong to @var{K}.
 *
 * In the ordinary case, the codimension is the number
 * of equations of @var{C} which do not belong to @var{K} plus
 * the number of parameters involved in these equations which 
 * are not leaders (we have to count the implicit equations 
 * which state that the derivatives of the parameters are zero).
 *
 * In the partial differential case, the formula is the same
 * as in the ordinary case but differential polynomials whose 
 * leaders are derivatives of the same differential indeterminate
 * are counted only once.
 */

BAD_DLL ba0_int_p
bad_codimension_regchain (
    struct bad_regchain *C,
    struct bad_base_field *K)
{
  struct bap_polynom_mpz *P;
  struct bav_variable *u;
  struct bav_tableof_symbol pars, syms;
  struct bav_dictionary_symbol dict_pars, dict_syms;
  struct bav_symbol *y;
  ba0_int_p i, parameter_leaders, codim;
  struct ba0_mark M;

  ba0_record (&M);

  if (!bad_defines_a_differential_ideal_regchain (C))
    {
/*
 * Algebraic case. 
 * codimension = the number of polynomials in C which are not in K
 */
      codim = 0;
      i = C->decision_system.size - 1;
      if (i >= 0)
        {
          P = C->decision_system.tab[i];
          u = bap_leader_polynom_mpz (P);
        }
      while (i >= 0 && !bad_member_variable_base_field (u, K))
        {
          codim += 1;
          i -= 1;
          if (i >= 0)
            {
              P = C->decision_system.tab[i];
              u = bap_leader_polynom_mpz (P);
            }
        }
    }
  else if (bav_global.R.ders.size == 1)
    {
/*
 * ODE case or PDE case if decision_system is false
 */
      bav_init_dictionary_symbol (&dict_pars, 8);
      ba0_init_table ((struct ba0_table *) &pars);
      ba0_realloc_table ((struct ba0_table *) &pars, 256);

      parameter_leaders = 0;

      codim = 0;
      i = C->decision_system.size - 1;
      if (i >= 0)
        {
          P = C->decision_system.tab[i];
          u = bap_leader_polynom_mpz (P);
        }
/*
 * Compute       codim = the number of polynomials whose leaders are not in K
 *                pars = the parameters involved in these polynomials
 *   parameter_leaders = the number of parameters which are leaders
 *
 * The codimension     = codim + pars.size - parameter_leaders
 */
      while (i >= 0 && !bad_member_variable_base_field (u, K))
        {
          bap_involved_parameters_polynom_mpz (&dict_pars, &pars, P);

          if (bav_is_a_parameter (u->root, (struct bav_parameter **) 0))
            parameter_leaders += 1;

          codim += 1;
          i -= 1;
          if (i >= 0)
            {
              P = C->decision_system.tab[i];
              u = bap_leader_polynom_mpz (P);
            }
        }
      codim = codim + pars.size - parameter_leaders;
    }
  else
    {
/*
 * PDE case
 */
      bav_init_dictionary_symbol (&dict_syms, 8);
      ba0_init_table ((struct ba0_table *) &syms);
      ba0_realloc_table ((struct ba0_table *) &syms, 256);

      bav_init_dictionary_symbol (&dict_pars, 8);
      ba0_init_table ((struct ba0_table *) &pars);
      ba0_realloc_table ((struct ba0_table *) &pars, 256);

      parameter_leaders = 0;

      codim = 0;
      i = C->decision_system.size - 1;
      if (i >= 0)
        {
          P = C->decision_system.tab[i];
          u = bap_leader_polynom_mpz (P);
        }
/*
 * Compute       codim = the number of polynomials whose leaders are not in K
 *                pars = the parameters involved in these polynomials
 *   parameter_leaders = the number of parameters which are leaders
 *
 * The codimension     = codim + pars.size - parameter_leaders
 *
 * The difference with the ODE case is: we count one polynomial for
 * all polynomials whose leaders are derivatives of the same symbol.
 */
      while (i >= 0 && !bad_member_variable_base_field (u, K))
        {
          bap_involved_parameters_polynom_mpz (&dict_pars, &pars, P);

          y = u->root;

          if (bav_get_dictionary_symbol (&dict_syms, &syms, y)
              == BA0_NOT_AN_INDEX)
            {
              bav_add_dictionary_symbol (&dict_syms, &syms, y, syms.size);

              if (syms.size == syms.alloc)
                {
                  ba0_int_p new_alloc = 2 * syms.alloc + 1;
                  ba0_realloc_table ((struct ba0_table *) &syms, new_alloc);
                }
              syms.tab[syms.size] = y;
              syms.size += 1;

              if (bav_is_a_parameter (y, (struct bav_parameter **) 0))
                parameter_leaders += 1;

              codim += 1;
            }

          i -= 1;
          if (i >= 0)
            {
              P = C->decision_system.tab[i];
              u = bap_leader_polynom_mpz (P);
            }
        }
      codim = codim + pars.size - parameter_leaders;
    }

  ba0_restore (&M);
  return codim;
}

/*
 * texinfo: bad_sizeof_regchain
 * Return the size of the memory needed to perform a copy of @var{C}.
 * If @var{code} is @code{ba0_embedded} then @var{C} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 */

BAD_DLL unsigned ba0_int_p
bad_sizeof_regchain (
    struct bad_regchain *C,
    enum ba0_garbage_code code)
{
  unsigned ba0_int_p size;
  ba0_int_p i;

  if (code == ba0_isolated)
    size = ba0_allocated_size (sizeof (struct bad_regchain));
  else
    size = 0;
  size +=
      ba0_allocated_size (C->decision_system.size *
      sizeof (struct bap_polynom_mpz *));
  for (i = 0; i < C->decision_system.size; i++)
    size += bap_sizeof_polynom_mpz (C->decision_system.tab[i], ba0_isolated);
  return size;
}

/*
 * texinfo: bad_switch_ring_regchain
 * This low level function should be used in conjunction with 
 * @code{bav_set_differential_ring}: if @var{R} is a ring obtained by 
 * application of @code{bav_set_differential_ring}
 * to the ring @var{C} refers to, then this function makes @var{C} 
 * refer to @var{R}. The chain @var{C} is modified.
 */

BAD_DLL void
bad_switch_ring_regchain (
    struct bad_regchain *C,
    struct bav_differential_ring *R)
{
  ba0_int_p i;

  for (i = 0; i < C->decision_system.size; i++)
    bap_switch_ring_polynom_mpz (C->decision_system.tab[i], R);
}
