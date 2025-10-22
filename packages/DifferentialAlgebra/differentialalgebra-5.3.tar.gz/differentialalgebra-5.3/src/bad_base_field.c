#include "bad_base_field.h"
#include "bad_reduction.h"

/*
 * texinfo: bad_init_base_field
 * Initialize the base field @var{K} to the field of the rational
 * fractions in the independent variables. 
 */

BAD_DLL void
bad_init_base_field (
    struct bad_base_field *K)
{
  bool differential = bav_global.R.ders.size > 0;
  bad_init_regchain (&K->relations);
  bad_set_base_field_relations_properties (&K->relations, differential);
  K->first_block_index = BA0_NOT_AN_INDEX;
  K->assume_reduced = false;
}

/*
 * texinfo: bad_new_base_field
 * Allocate a base field, initialize it and return it.
 */

BAD_DLL struct bad_base_field *
bad_new_base_field (
    void)
{
  struct bad_base_field *K;

  K = (struct bad_base_field *) ba0_alloc (sizeof (struct bad_base_field));
  bad_init_base_field (K);
  return K;
}

/*
 * texinfo: bad_is_differential_base_field
 * Return @code{true} if @var{K} is a differential field else @code{false}.
 */

BAD_DLL bool
bad_is_differential_base_field (
    struct bad_base_field *K)
{
  return bad_defines_a_differential_ideal_regchain (&K->relations);
}

/*
 * texinfo: bad_set_base_field
 * Assign @var{src} to @var{dst}.
 */

BAD_DLL void
bad_set_base_field (
    struct bad_base_field *dst,
    struct bad_base_field *src)
{
  dst->assume_reduced = src->assume_reduced;
  dst->first_block_index = src->first_block_index;
  bad_set_regchain (&dst->relations, &src->relations);
}

/*
 * texinfo: bad_base_field_generators
 * Assign to @var{G} the identifiers of the differential indeterminates
 * with plain symbols as well as the range indexed strings 
 * which belong to @var{K}. 
 */

BAD_DLL void
bad_base_field_generators (
    struct ba0_tableof_range_indexed_group *G,
    struct bad_base_field *K)
{
  bav_R_lower_block_range_indexed_strings (G, K->first_block_index);
}

/*
 * Set K->first_block_index to min (block index of v, K->first_block_index)
 */

static void
bad_move_generator_to_base_field (
    struct bad_base_field *K,
    ba0_int_p index)
{
  if (bav_has_varmax_current_ordering ())
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  if (K->first_block_index == BA0_NOT_AN_INDEX || index < K->first_block_index)
    K->first_block_index = index;
}

static void
bad_move_relations_generators_to_base_field (
    struct bad_base_field *K,
    struct bad_regchain *A)
{
  struct bav_variable *v;
  ba0_int_p k;

  if (bav_has_varmax_current_ordering ())
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  if (A->decision_system.size > 0)
    {
      v = bap_leader_polynom_mpz (A->decision_system.tab[A->decision_system.
              size - 1]);
      if (bav_symbol_type_variable (v) != bav_dependent_symbol)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      k = bav_block_index_symbol (v->root);
      bad_move_generator_to_base_field (K, k);
    }
}

/*
 * texinfo: bad_set_base_field_generators_and_relations
 * Assign to @var{K} the base field defined by @var{generators} and
 * @var{relations}.
 * 
 * The @var{generators} table is supposed to contain a subset of
 * the entries of the block tables of orderings.
 * All the symbols which occur in @var{generators} and @var{relations} 
 * are moved to the base field.
 *
 * If @var{pretend} is @code{false} then some
 * checking is performed to ensure the consistency of the relations.
 * The arguments @var{generators} and @var{relations} may be zero.
 */

BAD_DLL void
bad_set_base_field_generators_and_relations (
    struct bad_base_field *K,
    struct ba0_tableof_range_indexed_group *generators,
    struct bad_regchain *relations,
    bool pretend)
{
  struct bap_tableof_polynom_mpz *eqns;
  struct ba0_tableof_string prop;
  ba0_int_p i, k;
/*
 * First move all elements from generators to K
 */
  if (generators)
    for (i = 0; i < generators->size; i++)
      {
        k = bav_block_index_range_indexed_group (generators->tab[i]);
        if (k == BA0_NOT_AN_INDEX)
          BA0_RAISE_EXCEPTION (BAD_ERRBAS);
        bad_move_generator_to_base_field (K, k);
      }

  if (relations)
    bad_move_relations_generators_to_base_field (K, relations);

  bad_set_regchain (&K->relations, relations);
  bad_set_automatic_properties_attchain (&K->relations.attrib);
}

/*
 * texinfo: bad_is_a_compatible_base_field
 * Return @code{true} if the relations of @var{K} can be included in a
 * regular chain having properties @var{attrib}. 
 * See @code{bad_is_a_compatible_regchain}.
 */

BAD_DLL bool
bad_is_a_compatible_base_field (
    struct bad_base_field *K,
    struct bad_attchain *attrib)
{
  return bad_is_a_compatible_regchain (&K->relations, attrib);
}

/*
 * texinfo: bad_member_variable_base_field
 * Return @code{true} if @var{v} belongs to @var{K}, else @code{false}.
 */

BAD_DLL bool
bad_member_variable_base_field (
    struct bav_variable *v,
    struct bad_base_field *K)
{
  ba0_int_p index;
  bool differential;

  if (bav_has_varmax_current_ordering ())
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  if (bav_symbol_type_variable (v) == bav_independent_symbol)
    return true;
  else if (K->first_block_index == BA0_NOT_AN_INDEX)
    return false;
/*
 * we might have a non-differential field containing [m, g, l]
 * and the variable m[t]. In such a case, m[t] does not belong to the field
 */
  index = bav_block_index_symbol (v->root);
  if (bad_is_differential_base_field (K))
    return index >= K->first_block_index;
  else
    return index >= K->first_block_index && bav_total_order_variable (v) == 0;
}

/*
 * texinfo: bad_number_of_elements_over_base_field_regchain
 * Return the number of elements of @var{A} which do not belong to @var{K}.
 */

BAD_DLL ba0_int_p
bad_number_of_elements_over_base_field_regchain (
    struct bad_regchain *A,
    struct bad_base_field *K)
{
  struct bav_variable *u;
  ba0_int_p i, n;

  n = 0;
  i = A->decision_system.size - 1;
  if (i >= 0)
    u = bap_leader_polynom_mpz (A->decision_system.tab[i]);
  while (i >= 0 && !bad_member_variable_base_field (u, K))
    {
      n += 1;
      i -= 1;
      if (i >= 0)
        u = bap_leader_polynom_mpz (A->decision_system.tab[i]);
    }
  return n;
}

/*
 * Return true if P, which is assumed to be reduced with respect to the 
 * relations, lies in the base field. If P = 0 then false is returned.
 */

static bool
bad_member_reduced_nonzero_polynom_base_field (
    struct bap_polynom_mpz *P,
    struct bad_base_field *K)
{
  if (bap_is_numeric_polynom_mpz (P))
    return !bap_is_zero_polynom_mpz (P);
  else
    return bad_member_variable_base_field (bap_leader_polynom_mpz (P), K);
}

/*
 * texinfo: bad_member_nonzero_polynom_base_field
 * Return @code{true} if @var{P} is a nonzero element of @var{K}.
 * If the field @code{assume_reduced} of @var{K} is @code{true}, then the
 * polynomial @var{P} is supposed to be reduced with respect to 
 * the defining relations of @var{K}, thereby speeding up the membership test.
 */

BAD_DLL bool
bad_member_nonzero_polynom_base_field (
    struct bap_polynom_mpz *P,
    struct bad_base_field *K)
{
  struct bap_product_mpz R;
  struct ba0_mark M;
  ba0_int_p i;
  bool b;
  bool differential;

  if (bav_has_varmax_current_ordering ())
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  if (K->assume_reduced)
    return bad_member_reduced_nonzero_polynom_base_field (P, K);

  if (bap_is_independent_polynom_mpz (P))
    return !bap_is_zero_polynom_mpz (P);

  differential = bad_is_differential_base_field (K);

  if (K->relations.decision_system.size == 0
      || !bad_is_a_reducible_polynom_by_regchain (P, &K->relations,
          differential ? bad_full_reduction : bad_algebraic_reduction,
          bad_all_derivatives_to_reduce, (struct bav_rank *) 0,
          (ba0_int_p *) 0))
    return bad_member_reduced_nonzero_polynom_base_field (P, K);

  ba0_record (&M);
  bap_init_product_mpz (&R);
  bad_reduce_polynom_by_regchain (&R, (struct bap_product_mpz *) 0,
      (struct bav_tableof_term *) 0, P,
      &K->relations,
      differential ? bad_full_reduction : bad_algebraic_reduction,
      bad_all_derivatives_to_reduce);
  b = !bap_is_zero_product_mpz (&R);
  for (i = 0; b && i < R.size; i++)
    b = bad_member_reduced_nonzero_polynom_base_field (&R.tab[i].factor, K);
  ba0_restore (&M);

  return b;
}

/*
 * texinfo: bad_member_polynom_base_field
 * Return @code{true} if @var{P} is an element (possibly zero) of @var{K}.
 */

BAD_DLL bool
bad_member_polynom_base_field (
    struct bap_polynom_mpz *P,
    struct bad_base_field *K)
{
  struct bap_product_mpz R;
  struct ba0_mark M;
  ba0_int_p i;
  bool b;
  bool differential;

  if (bav_has_varmax_current_ordering ())
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  if (bap_is_independent_polynom_mpz (P))
    return true;

  if (bad_is_zero_regchain (&K->relations))
    return bad_member_reduced_nonzero_polynom_base_field (P, K);

  differential = bad_is_differential_base_field (K);

  ba0_record (&M);
  bap_init_product_mpz (&R);
  bad_reduce_polynom_by_regchain (&R, (struct bap_product_mpz *) 0,
      (struct bav_tableof_term *) 0, P,
      &K->relations,
      differential ? bad_full_reduction : bad_algebraic_reduction,
      bad_all_derivatives_to_reduce);
  b = true;
  for (i = 0; b && i < R.size; i++)
    b = bad_member_reduced_nonzero_polynom_base_field (&R.tab[i].factor, K);
  ba0_restore (&M);

  return b;
}

/*
 * texinfo: bad_member_product_base_field
 * Return @code{true} if @var{P} belongs to @var{K}, else @code{false}.
 */

BAD_DLL bool
bad_member_product_base_field (
    struct bap_product_mpz *P,
    struct bad_base_field *K)
{
  ba0_int_p i;
  bool b = true;

  if (bap_is_zero_product_mpz (P))
    return true;

  for (i = 0; i < P->size && b; i++)
    b = bad_member_polynom_base_field (&P->tab[i].factor, K);
  return b;
}

/*
 * texinfo: bad_remove_product_factors_base_field
 * Remove from the product @var{P} all factors which belong to @var{K}
 * and set to @math{1} the exponents of the remaining factors.
 * Set to @math{1} the numerical factor.
 * Assign the result to @var{R}.
 */

BAD_DLL void
bad_remove_product_factors_base_field (
    struct bap_product_mpz *R,
    struct bap_product_mpz *P,
    struct bad_base_field *K)
{
  ba0_int_p i;

  if (R != P)
    bap_set_product_mpz (R, P);

  if (!bap_is_zero_product_mpz (R))
    {
      i = 0;
      while (i < R->size)
        {
          if (bad_member_polynom_base_field (&R->tab[i].factor, K))
            {
              if (i < R->size - 1)
                BA0_SWAP (struct bap_power_mpz,
                    R->tab[i],
                    R->tab[R->size - 1]);
              R->size -= 1;
            }
          else
            {
              R->tab[i].exponent = 1;
              i += 1;
            }
        }
      ba0_mpz_set_si (R->num_factor, 1);
    }
}

/*
 * texinfo: bad_tag_product_factors_base_field
 * For each factor of @var{prod} which belongs to @var{K},
 * set the corresponding entry of @var{keep} to @code{false}.
 * Possibly swap factors of @var{prod} so that, eventually,
 * the @code{false} entries appear in the leftmost part of @var{keep}
 * and the @code{true} entries in the rightmost part.
 * The table @var{keep} must have the same size as @var{prod}.
 * See @code{baz_factor_easy_polynom_mpz}.
 */

BAD_DLL void
bad_tag_product_factors_base_field (
    struct bap_product_mpz *prod,
    struct ba0_tableof_bool *keep,
    struct bad_base_field *K)
{
  ba0_int_p i, j;

  i = 0;
  while (i < keep->size && !keep->tab[i])
    i += 1;
  j = i;
  while (j < keep->size)
    {
      if (bad_member_polynom_base_field (&prod->tab[j].factor, K))
        {
          if (j != i)
            BA0_SWAP (struct bap_power_mpz,
                prod->tab[i],
                prod->tab[j]);
          keep->tab[i] = false;
          i += 1;
        }
      j += 1;
    }
}

/*
 * texinfo: bad_set_base_field_relations_properties
 * If @var{relations} is empty, set all
 * its properties (except the differential and the coherence ones
 * if @var{differential} is false).
 * If it is nonempty, set the prime 
 * ideal property then call @code{bad_set_automatic_properties_attchain}.
 * The parameter @var{relations} is supposed to provide the
 * @code{relations} field of a base field.
 */

BAD_DLL void
bad_set_base_field_relations_properties (
    struct bad_regchain *relations,
    bool differential)
{
  if (bad_is_zero_regchain (relations))
    {
      bad_set_property_regchain (relations, bad_prime_ideal_property);
      if (differential)
        {
          bad_set_property_regchain (relations,
              bad_differential_ideal_property);
          bad_set_property_regchain (relations, bad_autoreduced_property);
          bad_set_property_regchain (relations, bad_primitive_property);
          bad_set_property_regchain (relations, bad_squarefree_property);
          bad_set_property_regchain (relations, bad_normalized_property);
          bad_set_property_regchain (relations, bad_coherence_property);
        }
      else
        {
          bad_clear_property_regchain (relations,
              bad_differential_ideal_property);
          bad_set_property_regchain (relations, bad_autoreduced_property);
          bad_set_property_regchain (relations, bad_primitive_property);
          bad_set_property_regchain (relations, bad_squarefree_property);
          bad_set_property_regchain (relations, bad_normalized_property);
          bad_clear_property_regchain (relations, bad_coherence_property);
        }
    }
  else
    {
      bad_set_property_regchain (relations, bad_prime_ideal_property);
      bad_set_automatic_properties_attchain (&relations->attrib);
    }
}

/*
 * texinfo: bad_scanf_base_field
 * The general parsing function for base fields.
 * It is called by @code{ba0_scanf/%base_field}.
 * The input string is expected to have the form:
 * @code{field ( [ differential = boolean ], 
 * [ generators = %t[%range_indexed_group] ], [ relations = %regchain ] )}.
 * The entries of the table of generators should be a subset of
 * the ones of the tables of blocks of orderings.
 * The table does not need to be exhaustive since
 * any variable which belongs to a block lower than the block
 * of any other base field element is automatically considered as 
 * a base field element.
 * The flag @code{differential} permits to force a base field
 * to be non differential even in the differential context i.e. when 
 * at least one derivation is defined.
 *
 * Keywords @code{basefield} and @code{base_field} may be used
 * instead of @code{field}.
 * Exception @code{BAD_ERRBAS} may be raised.
 */

BAD_DLL void *
bad_scanf_base_field (
    void *AA)
{
  struct bad_base_field *K;
  bool differential_is_set, differential;
  struct bad_regchain relations;
  struct ba0_tableof_range_indexed_group generators;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  if (ba0_type_token_analex () != ba0_string_token
      || (ba0_strcasecmp (ba0_value_token_analex (), "field") != 0
          && ba0_strcasecmp (ba0_value_token_analex (), "base_field") != 0
          && ba0_strcasecmp (ba0_value_token_analex (), "basefield") != 0))
    BA0_RAISE_PARSER_EXCEPTION (BAD_ERRBAS);
  ba0_get_token_analex ();
  if (!ba0_sign_token_analex ("("))
    BA0_RAISE_PARSER_EXCEPTION (BAD_ERRBAS);
  ba0_get_token_analex ();
/*
 * field ( 
 *              ^
 * differential_is_set = the differential flag is specified
 * differential        = the value of the differential flag (meaningful 
 *                       only if differential_is_set)
 */
  differential_is_set = false;
  if (ba0_type_token_analex () == ba0_string_token
      && ba0_strcasecmp (ba0_value_token_analex (), "differential") == 0)
    {
      differential_is_set = true;

      ba0_get_token_analex ();
      if (!ba0_sign_token_analex ("="))
        BA0_RAISE_PARSER_EXCEPTION (BAD_ERRBAS);
      ba0_get_token_analex ();
      if (ba0_type_token_analex () != ba0_string_token)
        BA0_RAISE_PARSER_EXCEPTION (BAD_ERRBAS);
      if (ba0_strcasecmp (ba0_value_token_analex (), "true") == 0)
        {
          if (bav_global.R.ders.size == 0)
            BA0_RAISE_EXCEPTION (BAD_ERRBFD);
          differential = true;
        }
      else if (ba0_strcasecmp (ba0_value_token_analex (), "false") == 0)
        differential = false;
      else
        BA0_RAISE_PARSER_EXCEPTION (BAD_ERRBAS);
      ba0_get_token_analex ();
      if (ba0_sign_token_analex (","))
        {
          ba0_get_token_analex ();
          if (ba0_sign_token_analex (")"))
            BA0_RAISE_PARSER_EXCEPTION (BAD_ERRBAS);
        }
    }
/*
 * generators = %t[%range_indexed_group] 
 */
  ba0_init_table ((struct ba0_table *) &generators);
  if (ba0_type_token_analex () == ba0_string_token
      && ba0_strcasecmp (ba0_value_token_analex (), "generators") == 0)
    {
      ba0_scanf ("generators = %t[%range_indexed_group]", &generators);
      ba0_get_token_analex ();
      if (ba0_sign_token_analex (","))
        {
          ba0_get_token_analex ();
          if (ba0_sign_token_analex (")"))
            BA0_RAISE_PARSER_EXCEPTION (BAD_ERRBAS);
        }
    }

  bad_init_regchain (&relations);
  if (ba0_type_token_analex () == ba0_string_token
      && ba0_strcasecmp (ba0_value_token_analex (), "relations") == 0)
    {
      ba0_scanf ("relations = %pretend_regchain", &relations);
      ba0_get_token_analex ();
    }

  if (!ba0_sign_token_analex (")"))
    BA0_RAISE_PARSER_EXCEPTION (BAD_ERRBAS);
/*
 * If a non empty regular chain is specified, 
 * - check consistency with (differential_is_set, differential)
 * - take its properties
 *
 * Otherwise, 
 * - use (differential_is_set, differential) if any
 * - set all properties to true
 */
  if (!bad_is_zero_regchain (&relations))
    {
      if (differential_is_set)
        if (differential != bad_has_property_regchain (&relations,
                bad_differential_ideal_property))
          BA0_RAISE_PARSER_EXCEPTION (BAD_ERRBAS);
    }

  if (!differential_is_set)
    differential = bav_global.R.ders.size > 0;

  bad_set_base_field_relations_properties (&relations, differential);

  ba0_pull_stack ();
  if (AA == (void *) 0)
    K = bad_new_base_field ();
  else
    K = (struct bad_base_field *) AA;

  bad_set_base_field_generators_and_relations (K, &generators, &relations,
      false);

  ba0_restore (&M);
  return K;
}

/*
 * texinfo: bad_printf_base_field
 * A printing function for base fields.
 * It is called by @code{ba0_printf/%base_field}.
 */

BAD_DLL void
bad_printf_base_field (
    void *AA)
{
  struct bad_base_field *K = (struct bad_base_field *) AA;
  struct ba0_tableof_range_indexed_group generators;
  struct ba0_mark M;
  bool differential;

  ba0_record (&M);
  ba0_init_table ((struct ba0_table *) &generators);
  bad_base_field_generators (&generators, K);

  differential = bad_is_differential_base_field (K);

  if (!bad_is_zero_regchain (&K->relations))
    ba0_printf
        ("field (differential = %s, generators = %t[%range_indexed_group], relations = %regchain)",
        differential ? "true" : "false", &generators, &K->relations);
  else
    ba0_printf
        ("field (differential = %s, generators = %t[%range_indexed_group])",
        differential ? "true" : "false", &generators);

  ba0_restore (&M);
}
