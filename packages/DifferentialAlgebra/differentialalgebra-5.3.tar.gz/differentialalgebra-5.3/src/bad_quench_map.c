#include "bad_quench_map.h"

/*
 * prop is inactive: prop->size = 0
 */

static void
bad_init_inactive_quench_property (
    struct ba0_tableof_int_p *prop)
{
  ba0_init_table ((struct ba0_table *) prop);
}

/*
 * prop is active.
 * It is satisfied for indices 0 .. nb_elem-1
 * The max number of elements is nb_max_elem
 */

static void
bad_init_satisfied_quench_property (
    struct ba0_tableof_int_p *prop,
    ba0_int_p nb_max_elem,
    ba0_int_p nb_elem)
{
  ba0_init_table ((struct ba0_table *) prop);
  ba0_realloc_table ((struct ba0_table *) prop, nb_max_elem);
  prop->size = nb_max_elem;
  for (int i = 0; i < nb_elem; i++)
    prop->tab[i] = true;
  for (int i = nb_elem; i < nb_max_elem; i++)
    prop->tab[i] = false;
}

/*
 * prop is active.
 * It is satisfied for indices 0 .. nb_elem-1 except for index except
 * The max number of elements is nb_max_elem
 */

static void
bad_init_satisfied_except_quench_property (
    struct ba0_tableof_int_p *prop,
    ba0_int_p nb_max_elem,
    ba0_int_p nb_elem,
    ba0_int_p except)
{
  if (except < 0 || except >= nb_elem)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  bad_init_satisfied_quench_property (prop, nb_max_elem, nb_elem);
  prop->tab[except] = false;
}

/*
 * texinfo: bad_init_quench_map
 * Initialize @var{map}.
 * The properties of @var{A} are assumed not to hold.
 */

BAD_DLL void
bad_init_quench_map (
    struct bad_quench_map *map,
    struct bad_regchain *A)
{
  ba0_int_p nb_max_elem = A->decision_system.size;

  map->nb_max_elem = nb_max_elem;

  if (bad_defines_a_differential_ideal_regchain (A))
    bad_init_satisfied_quench_property (&map->partially_autoreduced,
        nb_max_elem, 0);
  else
    bad_init_inactive_quench_property (&map->partially_autoreduced);

  bad_init_satisfied_quench_property (&map->regular, nb_max_elem, 0);

  if (bad_has_property_regchain (A, bad_primitive_property))
    bad_init_satisfied_quench_property (&map->primitive, nb_max_elem, 0);
  else
    bad_init_inactive_quench_property (&map->primitive);

  if (bad_has_property_regchain (A, bad_autoreduced_property))
    bad_init_satisfied_quench_property (&map->autoreduced, nb_max_elem, 0);
  else
    bad_init_inactive_quench_property (&map->autoreduced);

  if (bad_has_property_regchain (A, bad_squarefree_property))
    bad_init_satisfied_quench_property (&map->squarefree, nb_max_elem, 0);
  else
    bad_init_inactive_quench_property (&map->squarefree);

  if (bad_has_property_regchain (A, bad_normalized_property))
    bad_init_satisfied_quench_property (&map->normalized, nb_max_elem, 0);
  else
    bad_init_inactive_quench_property (&map->normalized);
}

/*
 * texinfo: bad_set_property_quench_map
 * If @var{prop} is active, declare this property to hold 
 * (if @var{b} is @code{true}) or not to hold (if it is @code{false})
 * for each element of the triangular set under consideration. 
 */

BAD_DLL void
bad_set_property_quench_map (
    struct ba0_tableof_int_p *prop,
    bool b)
{
  for (int k = 0; k < prop->size; k++)
    prop->tab[k] = b;
}

/*
 * texinfo: bad_set_all_properties_quench_map
 * Declare all active properties of @var{map} to 
 * hold (if @var{b} is @code{true}) or not to hold (if it is @code{false})
 * for each element of the triangular set under consideration. 
 */

BAD_DLL void
bad_set_all_properties_quench_map (
    struct bad_quench_map *map,
    bool b)
{
  bad_set_property_quench_map (&map->partially_autoreduced, b);
  bad_set_property_quench_map (&map->autoreduced, b);
  bad_set_property_quench_map (&map->primitive, b);
  bad_set_property_quench_map (&map->normalized, b);
  bad_set_property_quench_map (&map->regular, b);
  bad_set_property_quench_map (&map->squarefree, b);
}

/*
 * texinfo: bad_init_from_complete_quench_map
 * Initialize @var{map} in the context of the @code{bad_complete_quadruple}
 * context (this function being called by @code{bad_Rosenfeld_Groebner} or
 * @code{bad_pardi}).
 *
 * The triangular set @var{A} has been obtained by inserting at
 * index @var{k}, one new polynomial, in a regular chain satisfying 
 * all the properties as @var{A} (except
 * @code{bad_normalized_property}).
 *
 * This new polynomial is primitive and fully reduced w.r.t @var{A}.
 *
 * The @code{bad_normalized_property} is inactivated. 
 */

BAD_DLL void
bad_init_from_complete_quench_map (
    struct bad_quench_map *map,
    ba0_int_p k,
    struct bad_regchain *A)
{
  ba0_int_p nb_max_elem = A->decision_system.size;

  map->nb_max_elem = nb_max_elem;

  if (bad_defines_a_differential_ideal_regchain (A))
    bad_init_satisfied_quench_property (&map->partially_autoreduced,
        nb_max_elem, k + 1);
  else
    bad_init_inactive_quench_property (&map->partially_autoreduced);
/*
 * The initials of p_k, ..., p_r are no more necessarily regular
 */
  bad_init_satisfied_quench_property (&map->regular, nb_max_elem, k);
/*
 * If the primitive property is satisfied by A, it is satisfied
 *  by all its elements except the new polynomial k
 */
  if (bad_has_property_regchain (A, bad_primitive_property))
    bad_init_satisfied_except_quench_property (&map->primitive, nb_max_elem,
        nb_max_elem, k);
  else
    bad_init_inactive_quench_property (&map->primitive);
/*
 * If the autoreduced property is satisfied by A, then
 *  it is satisfied by all its elements up to index k
 */
  if (bad_has_property_regchain (A, bad_autoreduced_property))
    bad_init_satisfied_quench_property (&map->autoreduced, nb_max_elem, k + 1);
  else
    bad_init_inactive_quench_property (&map->autoreduced);
/*
 * If the squarefree property is satisfied by A, then
 *  it is satisfied by all its elements up to index k-1
 */
  if (bad_has_property_regchain (A, bad_squarefree_property))
    bad_init_satisfied_quench_property (&map->squarefree, nb_max_elem, k);
  else
    bad_init_inactive_quench_property (&map->squarefree);
/*
 * As the completion algorithms are implemented (with no splittings
 * on the possible vanishing of the algebraic inverse), it is 
 * necessary to forbid the normalized property.
 */
  bad_init_inactive_quench_property (&map->normalized);
}

/*
 * texinfo: bad_inactivate_property_quench_map
 * Change the status of property @var{prop} to inactive.
 */

BAD_DLL void
bad_inactivate_property_quench_map (
    struct ba0_tableof_int_p *prop)
{
  prop->size = 0;
}

static void
bad_satisfied_for_k_quench_property (
    struct ba0_tableof_int_p *prop,
    ba0_int_p k)
{
  if (prop->size > 0)
    {
      if (k >= prop->size)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);

      prop->tab[k] = true;
    }
}

static void
bad_not_satisfied_for_k_quench_property (
    struct ba0_tableof_int_p *prop,
    ba0_int_p k)
{
  if (prop->size > 0)
    {
      if (k >= prop->size)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);

      prop->tab[k] = false;
    }
}

static void
bad_not_satisfied_for_k_and_above_quench_property (
    struct ba0_tableof_int_p *prop,
    ba0_int_p k)
{
  if (prop->size > 0)
    {
      if (k >= prop->size)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);

      for (int i = k; i < prop->size; i++)
        prop->tab[i] = false;
    }
}

/*
 * texinfo: bad_fully_reduced_polynom_quench_map
 * Update @var{map} in the following context.
 * The polynomial at index @var{k} has been replaced by
 * another polynomial, with the same rank, obtained by full reduction.
 */

BAD_DLL void
bad_fully_reduced_polynom_quench_map (
    struct bad_quench_map *map,
    ba0_int_p k)
{
  bad_satisfied_for_k_quench_property (&map->partially_autoreduced, k);
  bad_satisfied_for_k_quench_property (&map->autoreduced, k);
/*
 * The new polynomial may not be primitive
 */
  bad_not_satisfied_for_k_quench_property (&map->primitive, k);
/*
 * if a full differential reduction has been performed then the
 * normalized property may not hold anymore, even if the regular chain 
 * used for the reduction is normalized, because of the separants.
 */
  bad_not_satisfied_for_k_quench_property (&map->normalized, k);
}

/*
 * texinfo: bad_partially_reduced_polynom_quench_map
 * Update @var{map} in the following context.
 * The polynomial at index @var{k} has been replaced by
 * another polynomial, with the same rank, obtained by partial reduction.
 */

BAD_DLL void
bad_partially_reduced_polynom_quench_map (
    struct bad_quench_map *map,
    ba0_int_p k)
{
  bad_satisfied_for_k_quench_property (&map->partially_autoreduced, k);
/*
 * The new polynomial may not be primitive nor fully reduced
 */
  bad_not_satisfied_for_k_quench_property (&map->autoreduced, k);
  bad_not_satisfied_for_k_quench_property (&map->primitive, k);
/*
 * See above
 */
  bad_not_satisfied_for_k_quench_property (&map->normalized, k);
}

/*
 * texinfo: bad_is_an_already_satisfied_property_quench_map
 * Update @var{prop} in the following context.
 * The polynomial at index @var{k} is left unchanged because
 * it is already satisfying the property.
 * The dependencies between properties (autoreduced implies
 * partially autoreduced, normalized implies regular) are not carried out
 * by this function.
 */

BAD_DLL void
bad_is_an_already_satisfied_property_quench_map (
    struct ba0_tableof_int_p *prop,
    ba0_int_p k)
{
  bad_satisfied_for_k_quench_property (prop, k);
}

/*
 * texinfo: bad_address_property_quench_map
 * Return @code{true} if property @var{prop} is satisfied
 * for all indices strictly less than @var{k} but fails to hold
 * at index @var{k}.
 */

BAD_DLL bool
bad_address_property_quench_map (
    struct ba0_tableof_int_p *prop,
    ba0_int_p k)
{
  if (prop->size > 0)
    {
      if (k >= prop->size)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      return prop->tab[k] == false;
    }
  else
    return false;
}

/*
 * texinfo: bad_primitive_polynom_quench_map
 * Update @var{map} in the following context.
 * The polynomial at index @var{k} has been replaced by
 * its primitive part.
 */

BAD_DLL void
bad_primitive_polynom_quench_map (
    struct bad_quench_map *map,
    ba0_int_p k)
{
  bad_satisfied_for_k_quench_property (&map->primitive, k);
}

/*
 * texinfo: bad_normalized_polynom_quench_map
 * Update @var{map} in the following context.
 * The polynomial at index @var{k} has been replaced by 
 * another polynomial, with the same rank and a normalized leading 
 * coefficient, obtained by means of a multiplication by an algebraic inverse
 * followed by a reduction.
 */

BAD_DLL void
bad_normalized_polynom_quench_map (
    struct bad_quench_map *map,
    ba0_int_p k)
{
  bad_satisfied_for_k_quench_property (&map->normalized, k);
  bad_satisfied_for_k_quench_property (&map->regular, k);
/*
 * The new polynomial may not be primitive nor fully reduced.
 * Since the rank has not changed, the polynomials above are
 *  not affected
 */
  bad_not_satisfied_for_k_quench_property (&map->autoreduced, k);
  bad_not_satisfied_for_k_quench_property (&map->primitive, k);
}

/*
 * texinfo: bad_pseudo_divided_polynom_quench_map
 * Update @var{map} in the following context.
 * The polynomial at index @var{k} has been replaced by its
 * pseudo-quotient or pseudo-remainder computed with respect to
 * a polynomial with a regular initial. The new polynomial has
 * the same leader as the old one but a lower degree.
 */

BAD_DLL void
bad_pseudo_divided_polynom_quench_map (
    struct bad_quench_map *map,
    ba0_int_p k)
{
/*
 * Since the degree has decreased, polynomials at index k and above
 * may not be fully reduced anymore
 */
  bad_not_satisfied_for_k_and_above_quench_property (&map->autoreduced, k);
/*
 * The new polynomial may not be primitive
 */
  bad_not_satisfied_for_k_quench_property (&map->primitive, k);
/*
 * The new polynomial may not be normalized.
 * Since its leader has not changed, the polynomials at indices
 *  greater than k are not affected
 */
  bad_not_satisfied_for_k_quench_property (&map->normalized, k);
}

/*
 * texinfo: bad_init_set_quench_map
 * Assign @var{src} to @var{dst}.
 */

BAD_DLL void
bad_init_set_quench_map (
    struct bad_quench_map *dst,
    struct bad_quench_map *src)
{
  dst->nb_max_elem = src->nb_max_elem;
  ba0_init_table ((struct ba0_table *) &dst->partially_autoreduced);
  ba0_set_table ((struct ba0_table *) &dst->partially_autoreduced,
      (struct ba0_table *) &src->partially_autoreduced);
  ba0_init_table ((struct ba0_table *) &dst->autoreduced);
  ba0_set_table ((struct ba0_table *) &dst->autoreduced,
      (struct ba0_table *) &src->autoreduced);
  ba0_init_table ((struct ba0_table *) &dst->primitive);
  ba0_set_table ((struct ba0_table *) &dst->primitive,
      (struct ba0_table *) &src->primitive);
  ba0_init_table ((struct ba0_table *) &dst->normalized);
  ba0_set_table ((struct ba0_table *) &dst->normalized,
      (struct ba0_table *) &src->normalized);
  ba0_init_table ((struct ba0_table *) &dst->regular);
  ba0_set_table ((struct ba0_table *) &dst->regular,
      (struct ba0_table *) &src->regular);
  ba0_init_table ((struct ba0_table *) &dst->squarefree);
  ba0_set_table ((struct ba0_table *) &dst->squarefree,
      (struct ba0_table *) &src->squarefree);
}

/*
 * texinfo: bad_first_index_quench_map
 * Return the smallest index @var{k} such that some property
 * is not satisfied at this index.
 */

BAD_DLL ba0_int_p
bad_first_index_quench_map (
    struct bad_quench_map *map)
{
  ba0_int_p k;

  k = 0;
  while (k < map->nb_max_elem)
    {
      if (map->partially_autoreduced.size > 0
          && map->partially_autoreduced.tab[k] == false)
        return k;
      if (map->autoreduced.size > 0 && map->autoreduced.tab[k] == false)
        return k;
      if (map->primitive.size > 0 && map->primitive.tab[k] == false)
        return k;
      if (map->normalized.size > 0 && map->normalized.tab[k] == false)
        return k;
      if (map->regular.size > 0 && map->regular.tab[k] == false)
        return k;
      if (map->squarefree.size > 0 && map->squarefree.tab[k] == false)
        return k;
      k += 1;
    }
  return k;
}

/*
 * texinfo: bad_printf_quench_map
 * Print @var{map} on the standard output.
 * For debugging purposes.
 */

BAD_DLL void
bad_printf_quench_map (
    struct bad_quench_map *map)
{
  printf ("    | p. aut. | autord. | primit. | normal. | regular | sqrfree\n");
  printf ("    -----------------------------------------------------------\n");
  for (int k = 0; k < map->nb_max_elem; k++)
    {
      printf (" %2d ", k);
      if (map->partially_autoreduced.size > 0)
        if (map->partially_autoreduced.tab[k])
          printf ("|   true  ");
        else
          printf ("|  false  ");
      else
        printf ("          ");
      if (map->autoreduced.size > 0)
        if (map->autoreduced.tab[k])
          printf ("|   true  ");
        else
          printf ("|  false  ");
      else
        printf ("          ");
      if (map->primitive.size > 0)
        if (map->primitive.tab[k])
          printf ("|   true  ");
        else
          printf ("|  false  ");
      else
        printf ("          ");
      if (map->normalized.size > 0)
        if (map->normalized.tab[k])
          printf ("|   true  ");
        else
          printf ("|  false  ");
      else
        printf ("          ");
      if (map->regular.size > 0)
        if (map->regular.tab[k])
          printf ("|   true  ");
        else
          printf ("|  false  ");
      else
        printf ("          ");
      if (map->squarefree.size > 0)
        if (map->squarefree.tab[k])
          printf ("|   true  ");
        else
          printf ("|  false  ");
      else
        printf ("          ");
      printf ("\n");
    }
  printf ("\n");
}
