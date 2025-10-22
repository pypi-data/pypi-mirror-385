#include "bad_attchain.h"

/*
 * texinfo: bad_init_attchain
 * Set the field @code{ordering} to the current ordering.
 * Clear the field @code{property} of @var{A}.
 */

BAD_DLL void
bad_init_attchain (
    struct bad_attchain *A)
{
  bad_reset_attchain (A);
}

/*
 * texinfo: bad_reset_attchain
 * Set the field @code{ordering} to the current ordering.
 * Clear the field @code{property} of @var{A}.
 */

BAD_DLL void
bad_reset_attchain (
    struct bad_attchain *A)
{
  A->ordering = bav_current_ordering ();
  A->property = 0;
}

/*
 * texinfo: bad_equal_attchain
 * Return @code{true} if @var{A} is equal to @var{B}, 
 * @code{false} otherwise.
 */

BAD_DLL bool
bad_equal_attchain (
    struct bad_attchain *A,
    struct bad_attchain *B)
{
  return A->ordering == B->ordering && A->property == B->property;
}

/*
 * texinfo: bad_set_attchain
 * Assign @var{B} to @var{A}.
 */

BAD_DLL void
bad_set_attchain (
    struct bad_attchain *A,
    struct bad_attchain *B)
{
  *A = *B;
}

/*
 * texinfo: bad_intersect_attchain
 * Intersect the attributes of @var{A} and those of @var{B}.
 * The result is in @var{A}.
 * This function is used to compute the attributes of the intersection of two
 * regular chains (see @code{struct bad_intersectof_regchain *}). 
 * Exception @code{BAD_ERRIAC} is raised if @var{A} and @var{B}
 * have different orderings or are not both differential or not both non 
 * differential.
 * The prime ideal property of @var{A} is cleared.
 * The other properties are intersected.
 */

BAD_DLL void
bad_intersect_attchain (
    struct bad_attchain *A,
    struct bad_attchain *B)
{
  if (A->ordering != B->ordering)
    BA0_RAISE_EXCEPTION (BAD_ERRIAC);
  if (bad_has_property_attchain (A,
          bad_differential_ideal_property) != bad_has_property_attchain (B,
          bad_differential_ideal_property))
    BA0_RAISE_EXCEPTION (BAD_ERRIAC);
  A->property &= B->property;
  bad_clear_property_attchain (A, bad_prime_ideal_property);
}

/*
 * texinfo: bad_set_automatic_properties_attchain
 * Set some properties of @var{A} by applying the following rules.
 * If @dfn{differential} is set then @dfn{squarefree} is set.
 * If @dfn{prime} is set then @dfn{squarefree} is set.
 * If @dfn{normalized} is set then @dfn{autoreduced} and
 *     @dfn{primitive} are set.
 */

BAD_DLL void
bad_set_automatic_properties_attchain (
    struct bad_attchain *A)
{
  if (bad_has_property_attchain (A, bad_differential_ideal_property))
    bad_set_property_attchain (A, bad_squarefree_property);

  if (bad_has_property_attchain (A, bad_prime_ideal_property))
    bad_set_property_attchain (A, bad_squarefree_property);

  if (bad_has_property_attchain (A, bad_normalized_property))
    {
      bad_set_property_attchain (A, bad_autoreduced_property);
      bad_set_property_attchain (A, bad_primitive_property);
    }
}

/*
 * texinfo: bad_set_properties_attchain
 * The list @var{P} contain a list of property identifiers.
 * Set the corresponding properties in @var{A}.
 * Exception @code{BAD_ERRNAC} is raised in the case of a non
 * recognized property.
 */

BAD_DLL void
bad_set_properties_attchain (
    struct bad_attchain *A,
    struct ba0_tableof_string *P)
{
  enum bad_property_attchain prop;
  ba0_int_p i;

  A->property = 0;

  for (i = 0; i < P->size; i++)
    {
      if (bad_is_a_property_attchain (P->tab[i], &prop))
        bad_set_property_attchain (A, prop);
      else
        BA0_RAISE_EXCEPTION (BAD_ERRNAC);
    }
}

/*
 * texinfo: bad_set_property_attchain
 * Set the property @var{p} of @var{A}.
 */

BAD_DLL void
bad_set_property_attchain (
    struct bad_attchain *A,
    enum bad_property_attchain p)
{
  A->property |= (ba0_int_p) (1 << (int) p);
}

/*
 * texinfo: bad_clear_property_attchain
 * Clear the property @var{p} of @var{A}.
 */

BAD_DLL void
bad_clear_property_attchain (
    struct bad_attchain *A,
    enum bad_property_attchain p)
{
  A->property &= -1 - (1 << (int) p);
}

/*
 * Readonly static structures
 */

static struct
{
  char *ident;
  enum bad_property_attchain prop;
} properties[] = {
  {"differential", bad_differential_ideal_property},
  {"prime", bad_prime_ideal_property},
  {"autoreduced", bad_autoreduced_property},
  {"primitive", bad_primitive_property},
  {"squarefree", bad_squarefree_property},
  {"coherent", bad_coherence_property},
  {"normalized", bad_normalized_property}
};

/*
 * texinfo: bad_is_a_property_attchain
 * Return @code{true} if @var{s} is the identifier of a property,
 * @code{false} otherwise. Valid values for @var{s} are @code{autoreduced},
 * @code{primitive}, @code{squarefree}, @code{coherent} and @code{normalized}.
 */

BAD_DLL bool
bad_is_a_property_attchain (
    char *s,
    enum bad_property_attchain *p)
{
  ba0_int_p i, n;

  n = sizeof (properties) / sizeof (*properties);
  for (i = 0; i < n; i++)
    {
      if (ba0_strcasecmp (s, properties[i].ident) == 0)
        {
          if (p != (enum bad_property_attchain *) 0)
            *p = properties[i].prop;
          return true;
        }
    }
  return false;
}

/*
 * texinfo: bad_properties_attchain
 * Append to @var{T} a list of identifiers describing the 
 * properties which are set in @var{C}.
 */

BAD_DLL void
bad_properties_attchain (
    struct ba0_tableof_string *T,
    struct bad_attchain *C)
{
  ba0_int_p i, n;

  n = sizeof (properties) / sizeof (*properties);
  ba0_realloc_table ((struct ba0_table *) T, T->size + n);
  for (i = 0; i < n; i++)
    {
      if (bad_has_property_attchain (C, properties[i].prop))
        T->tab[T->size++] = properties[i].ident;
    }
}

/*
 * texinfo: bad_has_property_attchain
 * Return @code{true} if the property @var{p} is set in @var{A},
 * @code{false} otherwise.
 */

BAD_DLL bool
bad_has_property_attchain (
    struct bad_attchain *A,
    enum bad_property_attchain p)
{
  return (A->property & (ba0_int_p) (1 << (int) p)) != 0;
}

/*
 * texinfo: bad_defines_a_prime_ideal_attchain
 * Return @code{true} if the prime ideal property is set in @var{C},
 * @code{false} otherwise.
 */

BAD_DLL bool
bad_defines_a_prime_ideal_attchain (
    struct bad_attchain *C)
{
  return bad_has_property_attchain (C, bad_prime_ideal_property);
}

/*
 * texinfo: bad_defines_a_differential_ideal_attchain
 * Return @code{true} if the differential ideal property is set in @var{C},
 * @code{false} otherwise.
 */

BAD_DLL bool
bad_defines_a_differential_ideal_attchain (
    struct bad_attchain *C)
{
  return bad_has_property_attchain (C, bad_differential_ideal_property);
}
