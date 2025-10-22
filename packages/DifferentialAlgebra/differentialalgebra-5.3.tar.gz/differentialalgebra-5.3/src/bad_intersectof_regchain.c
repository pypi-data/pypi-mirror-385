#include "bad_intersectof_regchain.h"

/*
 * texinfo: bad_init_intersectof_regchain
 * Initialize @var{ideal} to the empty intersection.
 */

BAD_DLL void
bad_init_intersectof_regchain (
    struct bad_intersectof_regchain *ideal)
{
  bad_init_attchain (&ideal->attrib);
  ba0_init_table ((struct ba0_table *) &ideal->inter);
}

/*
 * texinfo: bad_new_intersectof_regchain
 * Allocate a new intersection, initialize it and return it.
 */

BAD_DLL struct bad_intersectof_regchain *
bad_new_intersectof_regchain (
    void)
{
  struct bad_intersectof_regchain *ideal;

  ideal =
      (struct bad_intersectof_regchain *) ba0_alloc (sizeof (struct
          bad_intersectof_regchain));
  bad_init_intersectof_regchain (ideal);
  return ideal;
}

/*
 * texinfo: bad_reset_intersectof_regchain
 * Reset @var{ideal} to the empty intersection.
 */

BAD_DLL void
bad_reset_intersectof_regchain (
    struct bad_intersectof_regchain *ideal)
{
  bad_reset_attchain (&ideal->attrib);
  ba0_reset_table ((struct ba0_table *) &ideal->inter);
}

/*
 * texinfo: bad_realloc_intersectof_regchain
 * Realloc the table @code{inter} of @var{ideal} if needed in such a way that 
 * the table can receive at least @var{n} regular chains. 
 * Formerly stored regular chains are kept.
 */

BAD_DLL void
bad_realloc_intersectof_regchain (
    struct bad_intersectof_regchain *ideal,
    ba0_int_p n)
{
  ba0_realloc2_table ((struct ba0_table *) &ideal->inter, n,
      (ba0_new_function *) & bad_new_regchain);
}

/*
 * texinfo: bad_set_intersectof_regchain_regchain
 * Assign @var{C} to @var{ideal}.
 */

BAD_DLL void
bad_set_intersectof_regchain_regchain (
    struct bad_intersectof_regchain *ideal,
    struct bad_regchain *C)
{
  bad_set_attchain (&ideal->attrib, &C->attrib);
  bad_realloc_intersectof_regchain (ideal, 1);
  if (ideal->inter.tab[0] != C)
    bad_set_regchain (ideal->inter.tab[0], C);
  ideal->inter.size = 1;
}

/*
 * texinfo: bad_append_intersectof_regchain_regchain
 * Append the regular chain @var{C} to @var{ideal}.
 * If @var{ideal} is empty, assign the attributes of @var{C} to 
 * those of @var{ideal} 
 * else intersects the attributes of @var{C} with those of @var{ideal}
 * by calling @code{bad_intersect_attchain}. 
 * Exception @code{BAD_ERRIAC} may be raised.
 */

BAD_DLL void
bad_append_intersectof_regchain_regchain (
    struct bad_intersectof_regchain *ideal,
    struct bad_regchain *C)
{
  if (ideal->inter.size == 0)
    bad_set_intersectof_regchain_regchain (ideal, C);
  else
    {
      bad_realloc_intersectof_regchain (ideal, ideal->inter.size + 1);
      if (!ba0_member_table (C, (struct ba0_table *) &ideal->inter))
        {
          bad_intersect_attchain (&ideal->attrib, &C->attrib);
          bad_set_regchain (ideal->inter.tab[ideal->inter.size++], C);
        }
    }
}

/*
 * texinfo: bad_append_intersectof_regchain
 * Append the regular chains of @var{J} to @var{I}.
 */

BAD_DLL void
bad_append_intersectof_regchain (
    struct bad_intersectof_regchain *I,
    struct bad_intersectof_regchain *J)
{
  ba0_int_p i;

  if (I != J)
    {
      bad_realloc_intersectof_regchain (I, I->inter.size + J->inter.size);
      for (i = 0; i < J->inter.size; i++)
        bad_append_intersectof_regchain_regchain (I, J->inter.tab[i]);
    }
}

/*
 * texinfo: bad_set_intersectof_regchain
 * Assign @var{J} to @var{I}.
 */

BAD_DLL void
bad_set_intersectof_regchain (
    struct bad_intersectof_regchain *I,
    struct bad_intersectof_regchain *J)
{
  ba0_int_p i;

  if (I != J)
    {
      bad_set_attchain (&I->attrib, &J->attrib);
      I->inter.size = 0;
      bad_realloc_intersectof_regchain (I, J->inter.size);
      for (i = 0; i < J->inter.size; i++)
        bad_set_regchain (I->inter.tab[i], J->inter.tab[i]);
      I->inter.size = J->inter.size;
    }
}

/*
 * texinfo: bad_set_properties_intersectof_regchain
 * Set the properties of @var{I} with @var{T}.
 */

BAD_DLL void
bad_set_properties_intersectof_regchain (
    struct bad_intersectof_regchain *I,
    struct ba0_tableof_string *P)
{
  bad_set_properties_attchain (&I->attrib, P);
}

/*
 * texinfo: bad_set_automatic_properties_intersectof_regchain
 * Set the automatic properties of @var{I}.
 * See @code{bad_set_automatic_properties_attchain}.
 */

BAD_DLL void
bad_set_automatic_properties_intersectof_regchain (
    struct bad_intersectof_regchain *I)
{
  bad_set_automatic_properties_attchain (&I->attrib);
}

/*
 * texinfo: bad_clear_property_intersectof_regchain
 * Clear the property @var{P} of @var{I}.
 */

BAD_DLL void
bad_clear_property_intersectof_regchain (
    struct bad_intersectof_regchain *I,
    enum bad_property_attchain P)
{
  bad_clear_property_attchain (&I->attrib, P);
}

/*
 * texinfo: bad_set_property_intersectof_regchain
 * Set the property @var{P} of @var{I}.
 */

BAD_DLL void
bad_set_property_intersectof_regchain (
    struct bad_intersectof_regchain *I,
    enum bad_property_attchain P)
{
  bad_set_property_attchain (&I->attrib, P);
}

/*
 * texinfo: bad_has_property_intersectof_regchain
 * Return @code{true} if @var{I} has the property @var{P}.
 */

BAD_DLL bool
bad_has_property_intersectof_regchain (
    struct bad_intersectof_regchain *I,
    enum bad_property_attchain P)
{
  return bad_has_property_attchain (&I->attrib, P);
}

/*
 * texinfo: bad_properties_intersectof_regchain
 * Assign to @var{properties} the properties of @var{I}.
 */

BAD_DLL void
bad_properties_intersectof_regchain (
    struct ba0_tableof_string *properties,
    struct bad_intersectof_regchain *I)
{
  bad_properties_attchain (properties, &I->attrib);
}

/*
 * texinfo: bad_get_regchain_intersectof_regchain
 * Return the component of @var{I} whose @code{number} field
 * is equal to @var{number}. Return zero if not found.
 */

BAD_DLL struct bad_regchain *
bad_get_regchain_intersectof_regchain (
    struct bad_intersectof_regchain *I,
    ba0_int_p number)
{
  struct bad_regchain *C = (struct bad_regchain *) 0;
  ba0_int_p i;

  i = 0;
  while (i < I->inter.size && C == (struct bad_regchain *) 0)
    {
      if (bad_get_number_regchain (I->inter.tab[i]) == number)
        C = I->inter.tab[i];
      else
        i += 1;
    }
  return C;
}

static int
bad_compare_rank_regchain (
    struct bad_regchain *C,
    struct bad_regchain *D)
{
  ba0_int_p i;
/*
 * first compare ranks of polynomials from bottom up
 * if C < D then it should appear later hence 1
 */
  for (i = 0; i < C->decision_system.size && i < D->decision_system.size; i++)
    {
      struct bap_polynom_mpz *P = C->decision_system.tab[i];
      struct bap_polynom_mpz *Q = D->decision_system.tab[i];
      if (bap_lt_rank_polynom_mpz (P, Q))
        return 1;
      else if (bap_lt_rank_polynom_mpz (Q, P))
        return -1;
    }
/*
 * ranks are equal: compare lengths
 * the longer set is smaller
 */
  if (C->decision_system.size > D->decision_system.size)
    return 1;
  else if (C->decision_system.size < D->decision_system.size)
    return -1;
  else
    return 0;
}

/*
 * Comparison function for bad_sort_intersectof_regchain
 * We need a total order!
 */

static int
bad_comp_regchain (
    const void *C0,
    const void *D0)
{
  struct bad_regchain *C = *(struct bad_regchain **) C0;
  struct bad_regchain *D = *(struct bad_regchain **) D0;
  struct bap_polynom_mpz R;
  struct ba0_mark M;
  ba0_int_p i;
  int code;
/*
 * first compare ranks of polynomials from bottom up
 * if C < D then it should appear later hence 1
 */
  code = bad_compare_rank_regchain (C, D);

  if (code != 0)
    return code;
/*
 * same ranks! but monomials may differ
 */
  for (i = 0; i < C->decision_system.size && code == 0; i++)
    {
      struct bap_polynom_mpz *P = C->decision_system.tab[i];
      struct bap_polynom_mpz *Q = D->decision_system.tab[i];
      enum ba0_compare_code ret = bap_compare_polynom_mpz (P, Q);
      if (ret == ba0_lt)
        code = 1;
      else if (ret == ba0_gt)
        code = -1;
    }

  if (code != 0)
    return code;
/*
 * same monomials: but coefficients may differ
 */
  ba0_record (&M);
  bap_init_polynom_mpz (&R);

  for (i = 0; i < C->decision_system.size && code == 0; i++)
    {
      struct bap_polynom_mpz *P = C->decision_system.tab[i];
      struct bap_polynom_mpz *Q = D->decision_system.tab[i];

      bap_sub_polynom_mpz (&R, P, Q);
      if (!bap_is_zero_polynom_mpz (&R))
        {
          ba0_mpz_t *lc;
          lc = bap_numeric_initial_polynom_mpz (&R);
          if (ba0_mpz_sgn (*lc) < 0)
            code = 1;
          else
            code = -1;
        }
    }

  ba0_restore (&M);
  return code;
}

/*
 * texinfo: bad_sort_intersectof_regchain
 * Sort the regular chains of @var{J} by decreasing order. 
 * The result is stored in @var{I}.
 * Regular chains are compared following the classical ordering
 * on differentially triangular sets: ranks of polynomials are
 * compared from bottom up and, in case no difference of ranks is
 * observed, the longer set is considered as lower than the shorter one.
 */

BAD_DLL void
bad_sort_intersectof_regchain (
    struct bad_intersectof_regchain *I,
    struct bad_intersectof_regchain *J)
{
  if (I != J)
    bad_set_intersectof_regchain (I, J);

  qsort (I->inter.tab, I->inter.size, sizeof (struct bad_regchain *),
      &bad_comp_regchain);
}

/*
 * texinfo: bad_remove_redundant_components_intersectof_regchain
 * Perform the inclusion test between the components of @var{J}.
 * For each regular chain @var{C}, if there exists another 
 * regular chain @var{D} such
 * that the inclusion test @math{D \subset C} is positive, then 
 * @var{C} is removed from the intersection. 
 * 
 * This function relies on @code{bad_is_included_regchain} which may fail 
 * to decide if a regchain is included in another one. The computed
 * intersection is thus not guaranteed to be minimal. Polynomials are supposed
 * to have coefficients in @var{K}.
 *
 * The resulting intersection is sorted 
 * (see @code{bad_sort_intersectof_regchain}).
 */

BAD_DLL void
bad_remove_redundant_components_intersectof_regchain (
    struct bad_intersectof_regchain *I,
    struct bad_intersectof_regchain *J,
    struct bad_base_field *K)
{
  ba0_int_p i, j, start, end;
  ba0_int_p n = J->inter.size;
  struct ba0_tableof_int_p b;   // b[i] = keep component i
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_init_table ((struct ba0_table *) &b);
  ba0_realloc_table ((struct ba0_table *) &b, n);
  for (i = 0; i < n; i++)
    b.tab[i] = true;
  b.size = n;
  ba0_pull_stack ();

/*
 * Components are sorted decreasingly with respect to a total ordering
 * which is compatible with the classical pre-ordering on triangular sets
 */
  bad_sort_intersectof_regchain (I, J);

  start = 0;
  while (start < n)
    {
/*
 * A start - end block contains regular chains having the same rank
 * Thus, inside such a block, all pairs must be tested for inclusion
 */
      end = start + 1;
      while (end < n
          && bad_compare_rank_regchain (I->inter.tab[start],
              I->inter.tab[end]) == 0)
        end += 1;
      for (i = start; i < end; i++)
        {
          for (j = start; j < end; j++)
            {
              if (i != j && b.tab[i] && b.tab[j])
                {
                  if (bad_is_included_regchain (I->inter.tab[i],
                          I->inter.tab[j], K) == bad_inclusion_test_positive)
                    b.tab[j] = false;
                }
            }
        }
/*
 * For each regular chain of the block start - end, we still need
 * to test for inclusion with the regular chains before start.
 * But for these chains, inclusion tests must only be performed in one way
 */
      for (i = start; i < end; i++)
        {
          for (j = 0; b.tab[i] && j < start; j++)
            {
              if (b.tab[j]
                  && bad_is_included_regchain (I->inter.tab[j],
                      I->inter.tab[i], K) == bad_inclusion_test_positive)
                b.tab[i] = false;
            }
        }
      start = end;
    }
#if defined (BA0_HEAVY_DEBUG)
  for (i = 0; i < n; i++)
    {
      bool found;
      if (!b.tab[i])
        {
          found = false;
          for (j = 0; j < n && !found; j++)
            if (i != j && bad_is_included_regchain (I->inter.tab[j],
                    I->inter.tab[i], K) == bad_inclusion_test_positive)
              found = true;
          if (!found)
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
        }
    }
#endif
  for (i = n - 1; i >= 0; i--)
    {
      if (!b.tab[i])
        ba0_delete_table ((struct ba0_table *) &I->inter, i);
    }
#if defined (BA0_HEAVY_DEBUG)
  for (i = 0; i < I->inter.size; i++)
    for (j = 0; j < I->inter.size; j++)
      if (i != j && bad_is_included_regchain (I->inter.tab[i],
              I->inter.tab[j], K) == bad_inclusion_test_positive)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
#endif
  ba0_restore (&M);
}

/*
 * texinfo: bad_fast_primality_test_intersectof_regchain
 * Apply @code{bad_fast_primality_test_regchain} over each component
 * of @var{ideal}. 
 */

BAD_DLL void
bad_fast_primality_test_intersectof_regchain (
    struct bad_intersectof_regchain *ideal)
{
  ba0_int_p i;

  for (i = 0; i < ideal->inter.size; i++)
    bad_fast_primality_test_regchain (ideal->inter.tab[i]);
}

/*
 * texinfo: bad_scanf_intersectof_regchain
 * A parsing function for intersections of regular chains.
 * It is called by @code{ba0_scanf/%intersectof_regchain}.
 * It relies on @code{bad_scanf_regchain}.
 */

BAD_DLL void *
bad_scanf_intersectof_regchain (
    void *I)
{
  struct bad_intersectof_regchain *ideal;
  struct ba0_tableof_string *P;
  ba0_int_p i, differentiel;

  if (I == (void *) 0)
    ideal = bad_new_intersectof_regchain ();
  else
    ideal = (struct bad_intersectof_regchain *) I;

  P = (struct ba0_tableof_string *) ba0_new_table ();
  ba0_scanf ("intersectof_regchain (%t[%regchain], %t[%s])", &ideal->inter, P);

  bad_set_properties_attchain (&ideal->attrib, P);

  differentiel = 0;
  if (bad_defines_a_differential_ideal_attchain (&ideal->attrib))
    differentiel++;
  for (i = 0; i < ideal->inter.size; i++)
    if (bad_defines_a_differential_ideal_attchain (&ideal->inter.
            tab[i]->attrib))
      differentiel++;
  if (differentiel > 0 && differentiel < 1 + ideal->inter.size)
    BA0_RAISE_EXCEPTION (BAD_ERRIRC);

  if (bad_defines_a_prime_ideal_attchain (&ideal->attrib))
    {
      if (ideal->inter.size > 1)
        BA0_RAISE_EXCEPTION (BAD_ERRIRC);
      else if (ideal->inter.size == 1
          && !bad_defines_a_prime_ideal_attchain (&ideal->inter.tab[0]->attrib))
        BA0_RAISE_EXCEPTION (BAD_ERRIRC);
    }

  return ideal;
}

/*
 * texinfo: bad_scanf_intersectof_pretend_regchain
 * A parsing function for intersections of regular chains.
 * It is called by @code{ba0_scanf/%intersectof_pretend_regchain}.
 * It relies on @code{bad_scanf_pretend_regchain}.
 */

BAD_DLL void *
bad_scanf_intersectof_pretend_regchain (
    void *I)
{
  struct bad_intersectof_regchain *ideal;
  struct ba0_tableof_string *P;
  ba0_int_p i, differentiel;

  if (I == (void *) 0)
    ideal = bad_new_intersectof_regchain ();
  else
    ideal = (struct bad_intersectof_regchain *) I;

  P = (struct ba0_tableof_string *) ba0_new_table ();
  ba0_scanf ("intersectof_regchain (%t[%pretend_regchain], %t[%s])",
      &ideal->inter, P);

  bad_set_properties_attchain (&ideal->attrib, P);

  differentiel = 0;
  if (bad_defines_a_differential_ideal_attchain (&ideal->attrib))
    differentiel++;
  for (i = 0; i < ideal->inter.size; i++)
    if (bad_defines_a_differential_ideal_attchain (&ideal->inter.
            tab[i]->attrib))
      differentiel++;
  if (differentiel > 0 && differentiel < 1 + ideal->inter.size)
    BA0_RAISE_EXCEPTION (BAD_ERRIRC);

  if (bad_defines_a_prime_ideal_attchain (&ideal->attrib))
    {
      if (ideal->inter.size > 1)
        BA0_RAISE_EXCEPTION (BAD_ERRIRC);
      else if (ideal->inter.size == 1
          && !bad_defines_a_prime_ideal_attchain (&ideal->inter.tab[0]->attrib))
        BA0_RAISE_EXCEPTION (BAD_ERRIRC);
    }

  return ideal;
}

/*
 * texinfo: bad_printf_intersectof_regchain
 * A printing function for intersections of regular chains.
 * It is called by @code{ba0_printf/%intersectof_regchain}.
 */

BAD_DLL void
bad_printf_intersectof_regchain (
    void *I)
{
  struct bad_intersectof_regchain *ideal =
      (struct bad_intersectof_regchain *) I;
  struct ba0_tableof_string *P;
  struct ba0_mark M;

  ba0_record (&M);
  P = (struct ba0_tableof_string *) ba0_new_table ();
  bad_properties_attchain (P, &ideal->attrib);
  ba0_printf ("intersectof_regchain (%t[%regchain], %t[%s])", &ideal->inter, P);
  ba0_restore (&M);
}

/*
 * texinfo: bad_printf_intersectof_regchain_equations
 * A printing function for intersections of regular chains.
 * It is called by @code{ba0_printf/%intersectof_regchain_equations}.
 * It relies on @code{bad_printf_regchain_equations}.
 */

BAD_DLL void
bad_printf_intersectof_regchain_equations (
    void *I)
{
  struct bad_intersectof_regchain *ideal =
      (struct bad_intersectof_regchain *) I;

  ba0_printf ("%t[%regchain_equations]", &ideal->inter);
}

/*
 * Readonly static data
 */

static char _struct_intersect[] = "struct bad_intersectof_regchain *";
static char _struct_intersect_tab[] =
    "struct bad_intersectof_regchain *->inter.tab";

BAD_DLL ba0_int_p
bad_garbage1_intersectof_regchain (
    void *I,
    enum ba0_garbage_code code)
{
  struct bad_intersectof_regchain *ideal =
      (struct bad_intersectof_regchain *) I;
  ba0_int_p i, n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (ideal, sizeof (struct bad_intersectof_regchain),
        _struct_intersect);

  if (ideal->inter.alloc > 0)
    {
      n += ba0_new_gc_info (ideal->inter.tab,
          ideal->inter.alloc * sizeof (struct bad_regchain *),
          _struct_intersect_tab);
      for (i = 0; i < ideal->inter.alloc; i++)
        n += bad_garbage1_regchain (ideal->inter.tab[i], ba0_isolated);
    }

  return n;
}

BAD_DLL void *
bad_garbage2_intersectof_regchain (
    void *I,
    enum ba0_garbage_code code)
{
  struct bad_intersectof_regchain *ideal;
  ba0_int_p i;

  if (code == ba0_isolated)
    ideal =
        (struct bad_intersectof_regchain *) ba0_new_addr_gc_info (I,
        _struct_intersect);
  else
    ideal = (struct bad_intersectof_regchain *) I;

  if (ideal->inter.alloc > 0)
    {
      ideal->inter.tab =
          (struct bad_regchain * *) ba0_new_addr_gc_info (ideal->inter.tab,
          _struct_intersect_tab);
      for (i = 0; i < ideal->inter.alloc; i++)
        ideal->inter.tab[i] =
            bad_garbage2_regchain (ideal->inter.tab[i], ba0_isolated);
    }

  return ideal;
}

BAD_DLL void *
bad_copy_intersectof_regchain (
    void *I)
{
  struct bad_intersectof_regchain *ideal;

  ideal = bad_new_intersectof_regchain ();
  bad_set_intersectof_regchain (ideal, (struct bad_intersectof_regchain *) I);
  return ideal;
}
