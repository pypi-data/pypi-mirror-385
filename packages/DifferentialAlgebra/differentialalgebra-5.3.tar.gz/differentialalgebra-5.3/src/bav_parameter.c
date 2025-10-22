#include "bav_parameter.h"
#include "bav_differential_ring.h"
#include "bav_global.h"
#include "bav_variable.h"

/*
 * texinfo: bav_set_settings_parameter
 * Set to @var{Function_PFE} the corresponding settings variable.
 */

BAV_DLL void
bav_set_settings_parameter (
    char *Function_PFE)
{
  bav_initialized_global.parameter.Function_PFE = Function_PFE;
}

/*
 * texinfo: bav_get_settings_parameter
 * Assign to *@var{Function_PFE} the corresponding settings variable.
 * All arguments are allowed to be zero.
 */

BAV_DLL void
bav_get_settings_parameter (
    char * *Function_PFE)
{
  if (Function_PFE)
    *Function_PFE = bav_initialized_global.parameter.Function_PFE;
}

/*
 * texinfo: bav_init_parameter
 * Initialize @var{p}.
 */

BAV_DLL void
bav_init_parameter (
    struct bav_parameter *p)
{
  ba0_init_range_indexed_group (&p->rig);
  ba0_init_table ((struct ba0_table *) &p->dependencies);
}

/*
 * texinfo: bav_new_parameter
 * Allocate a new parameter, initialize it and return it.
 */

BAV_DLL struct bav_parameter *
bav_new_parameter (
    void)
{
  struct bav_parameter *p;
  p = (struct bav_parameter *) ba0_alloc (sizeof (struct bav_parameter));
  bav_init_parameter (p);
  return p;
}

/*
 * texinfo: bav_set_parameter
 * Assign @var{src} to @var{dst}.
 */

BAV_DLL void
bav_set_parameter (
    struct bav_parameter *dst,
    struct bav_parameter *src)
{
  if (dst != src)
    {
      ba0_set_range_indexed_group (&dst->rig, &src->rig);
      ba0_set_table ((struct ba0_table *) &dst->dependencies,
          (struct ba0_table *) &src->dependencies);
    }
}

/*
 * texinfo: bav_set_parameter_with_tableof_string
 * Assign @var{src} to @var{dst} without any string duplication.
 * Indeed, each string occurring in @var{src} is supposed to have a copy
 * in @var{T}, whose index is supposed to be registered in @var{D}.
 * Instead of duplicating strings, the copies are used.
 * Exception @code{BA0_ERRALG} is raised if some string
 * is not found in @var{D}.
 */

BAV_DLL void
bav_set_parameter_with_tableof_string (
    struct bav_parameter *dst,
    struct bav_parameter *src,
    struct ba0_dictionary_string *D,
    struct ba0_tableof_string *T)
{
  ba0_set_range_indexed_group_with_tableof_string (&dst->rig, &src->rig, D, T);
  ba0_set_table ((struct ba0_table *) &dst->dependencies,
      (struct ba0_table *) &src->dependencies);
}

/*
 * texinfo: bav_set_tableof_parameter_with_tableof_string
 * Assign @var{src} to @var{dst} without any string duplication
 * by calling @code{bav_set_parameter_with_tableof_string}.
 */

BAV_DLL void
bav_set_tableof_parameter_with_tableof_string (
    struct bav_tableof_parameter *dst,
    struct bav_tableof_parameter *src,
    struct ba0_dictionary_string *D,
    struct ba0_tableof_string *T)
{
  ba0_int_p i;

  ba0_realloc2_table ((struct ba0_table *) dst, src->size,
      (ba0_new_function *) & bav_new_parameter);
  for (i = 0; i < src->size; i++)
    bav_set_parameter_with_tableof_string (dst->tab[i], src->tab[i], D, T);
  dst->size = src->size;
}

/*
 * texinfo: bav_sizeof_parameter
 * Return the size needed to perform a copy of @var{p}.
 * If @var{code} is @code{ba0_embedded} then @var{p} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 * If @var{strings_not_copied} is @code{true} then the strings
 * occurring in @var{p} are supposed not to be copied.
 */

BAV_DLL unsigned ba0_int_p
bav_sizeof_parameter (
    struct bav_parameter *p,
    enum ba0_garbage_code code,
    bool strings_not_copied)
{
  unsigned ba0_int_p size;

  if (!strings_not_copied)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  if (code == ba0_isolated)
    size = ba0_allocated_size (sizeof (struct bav_parameter));
  else
    size = 0;

  size += ba0_sizeof_range_indexed_group (&p->rig, ba0_embedded,
      strings_not_copied);
  size +=
      ba0_sizeof_table ((struct ba0_table *) &p->dependencies, ba0_embedded);
  return size;
}

/*
 * texinfo: bav_sizeof_parameter
 * Return the size needed to perform a copy of @var{T}.
 * If @var{code} is @code{ba0_embedded} then @var{T} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 * If @var{strings_not_copied} is @code{true} then the strings
 * occurring in @var{T} are supposed not to be copied.
 */

BAV_DLL unsigned ba0_int_p
bav_sizeof_tableof_parameter (
    struct bav_tableof_parameter *T,
    enum ba0_garbage_code code,
    bool strings_not_copied)
{
  unsigned ba0_int_p size;
  ba0_int_p i;

  size = ba0_sizeof_table ((struct ba0_table *) T, code);
  for (i = 0; i < T->size; i++)
    size += bav_sizeof_parameter (T->tab[i], ba0_isolated, strings_not_copied);
  return size;
}

/*
 * texinfo: bav_is_a_parameter
 * Return @code{true} if @var{y} is a parameter, else @code{false}.
 * In the first case and if @var{p} is nonzero then *@var{p}
 * is assigned the address of the @code{struct bav_parameter} structure
 * associated to @var{y}.
 */

BAV_DLL bool
bav_is_a_parameter (
    struct bav_symbol *y,
    struct bav_parameter **p)
{
  if (y->type != bav_dependent_symbol || y->index_in_pars == BA0_NOT_AN_INDEX)
    return false;
  if (p != (struct bav_parameter **) 0)
    *p = bav_global.R.pars.pars.tab[y->index_in_pars];
  return true;
}

/*
 * texinfo: bav_annihilating_derivations_of_parameter
 * Assign to @var{T} all the derivations @var{x} such that
 * the derivative of @var{p} with respect to @var{x} is zero.
 */

BAV_DLL void
bav_annihilating_derivations_of_parameter (
    struct bav_tableof_symbol *T,
    struct bav_parameter *p)
{
  ba0_int_p i;

  ba0_reset_table ((struct ba0_table *) T);
  ba0_realloc_table ((struct ba0_table *) T, bav_global.R.ders.size);
  for (i = 0; i < bav_global.R.ders.size; i++)
    {
      ba0_int_p j = bav_global.R.ders.tab[i];
      if (!ba0_member_table ((void *) j, (struct ba0_table *) &p->dependencies))
        {
          struct bav_variable *v = bav_derivation_index_to_derivation (j);
          T->tab[T->size] = v->root;
          T->size += 1;
        }
    }
}

/*
 * texinfo: bav_is_constant_variable
 * Return @code{true} if @var{v} is a constant with respect to derivation 
 * @var{s} (or with respect to all derivations, if @var{s} is 
 * @code{BAV_NOT_A_SYMBOL}).
 */

BAV_DLL bool
bav_is_constant_variable (
    struct bav_variable *v,
    struct bav_symbol *s)
{
  struct bav_parameter *p;
  bool is_constant;

  if (s == BAV_NOT_A_SYMBOL)
    {
      if (bav_symbol_type_variable (v) == bav_independent_symbol)
        is_constant = false;
      else if (bav_is_a_parameter (v->root, &p))
        is_constant = p->dependencies.size == 0;
      else
        is_constant = false;
    }
  else
    {
      if (s->type != bav_independent_symbol)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      if (bav_symbol_type_variable (v) == bav_independent_symbol)
        is_constant = v->root != s;
      else if (bav_is_a_parameter (v->root, &p))
        {
          ba0_int_p j;

          is_constant = true;
          for (j = 0; is_constant && j < p->dependencies.size; j++)
            is_constant = p->dependencies.tab[j] != s->derivation_index;
        }
      else
        is_constant = false;
    }
  return is_constant;
}

/*
 * texinfo: bav_is_zero_derivative_of_parameter
 * Return @code{true} if @var{v} is a dependent variable and a derivative 
 * of some parameter which is supposed to simplify to zero.
 */

BAV_DLL bool
bav_is_zero_derivative_of_parameter (
    struct bav_variable *v)
{
  struct ba0_tableof_int_p *T;
  struct bav_symbol *y = v->root;
  ba0_int_p i;

  if (y->type != bav_dependent_symbol || y->index_in_pars == BA0_NOT_AN_INDEX)
    return false;

  T = &bav_global.R.pars.pars.tab[y->index_in_pars]->dependencies;

  for (i = 0; i < v->order.size; i++)
    if (v->order.tab[i] > 0)
      {
        if (!ba0_member_table ((void *) i, (struct ba0_table *) T))
          return true;
      }
  return false;
}

/*
 * texinfo: bav_scanf_parameter
 * The general parsing function for parameters.
 * It can be called via @code{ba0_scanf/%param}.
 * A parameter is either a symbol or a symbol followed by
 * a sequence of derivations, enclosed by parentheses.
 * The sequence of derivations provides the dependencies of the parameter.
 */

BAV_DLL void *
bav_scanf_parameter (
    void *z)
{
  struct bav_parameter p, *q;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_parameter (&p);
/*
 * We must not incorporate the trailing 'indexed string indices'
 * made of derivations into the range indexed group. This problem
 * may only arise in the case of a plain string range indexed group.
 * The trick, here, consists in using the symbol parser.
 */
  if (ba0_sign_token_analex ("("))
    ba0_scanf_range_indexed_group (&p.rig);
  else
    {
      struct bav_symbol *y = bav_scanf_symbol (0);
      ba0_set_range_indexed_group_string (&p.rig, y->ident);
    }
/*
 * Process now the trailing 'indexed string indices' made of derivations
 */
  ba0_get_token_analex ();
  if (ba0_sign_token_analex ("("))
    {
      struct bav_tableof_symbol T;
      struct ba0_tableof_int_p b;
      ba0_int_p i;

      ba0_init_table ((struct ba0_table *) &b);
      ba0_realloc_table ((struct ba0_table *) &b, bav_global.R.ders.size);
      for (i = 0; i < bav_global.R.ders.size; i++)
        b.tab[i] = false;
      b.size = bav_global.R.ders.size;

      ba0_init_table ((struct ba0_table *) &T);
      ba0_scanf ("%t(%y)", &T);

      for (i = 0; i < T.size; i++)
        {
          struct bav_symbol *d = T.tab[i];
          if (d->type != bav_independent_symbol || b.tab[d->derivation_index])
            BA0_RAISE_EXCEPTION (BAV_ERRPAR);
          else
            b.tab[d->derivation_index] = true;
        }

      ba0_realloc_table ((struct ba0_table *) &p.dependencies, T.size);
      for (i = 0; i < T.size; i++)
        p.dependencies.tab[i] = T.tab[i]->derivation_index;
      p.dependencies.size = T.size;
    }
  else
    ba0_unget_token_analex (1);

  ba0_pull_stack ();
  if (z == (void *) 0)
    q = bav_new_parameter ();
  else
    q = (struct bav_parameter *) z;

  bav_set_parameter (q, &p);
  ba0_restore (&M);
  return q;
}

/*
 * texinfo: bav_printf_parameter_dependencies
 * This subfunction of @code{bav_printf_parameter} prints
 * the dependencies of @var{p}.
 */

BAV_DLL void
bav_printf_parameter_dependencies (
    struct bav_parameter *p)
{
  if (p->dependencies.size > 0)
    {
      struct bav_variable *v;
      ba0_int_p i;

      ba0_put_char ('(');
      for (i = 0; i < p->dependencies.size; i++)
        {
          v = bav_derivation_index_to_derivation (p->dependencies.tab[i]);
          bav_printf_variable (v);
          if (i < p->dependencies.size - 1)
            ba0_put_char (',');
        }
      ba0_put_char (')');
    }
}

/*
 * texinfo: bav_printf_parameter
 * General printing function for parameters.
 * It can be called via @code{ba0_printf/%param}.
 */

BAV_DLL void
bav_printf_parameter (
    void *z)
{
  struct bav_parameter *p = (struct bav_parameter *) z;

  if (bav_initialized_global.parameter.Function_PFE == (char *) 0 ||
      p->dependencies.size == 0)
    ba0_printf_range_indexed_group (&p->rig);
  else
    {
      ba0_put_string (bav_initialized_global.parameter.Function_PFE);
      if (ba0_initialized_global.range_indexed_group.quote_PFE)
        ba0_put_char ('(');
      else
        ba0_put_string ("('");
      ba0_printf_range_indexed_group (&p->rig);
      if (ba0_initialized_global.range_indexed_group.quote_PFE)
        ba0_put_char (')');
      else
        ba0_put_string ("')");
    }
  bav_printf_parameter_dependencies (p);
}
