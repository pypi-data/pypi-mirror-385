#include "bap_polynom_mpzm.h"
#include "bap_add_polynom_mpzm.h"
#include "bap_mul_polynom_mpzm.h"
#include "bap_creator_mpzm.h"
#include "bap_itermon_mpzm.h"
#include "bap_geobucket_mpzm.h"
#include "bap_diff_polynom_mpzm.h"

#define BAD_FLAG_mpzm

/*
 * texinfo: bap_is_constant_polynom_mpzm
 * Return @code{true} if the derivative of @var{A} with respect to 
 * @var{s} is zero, else @code{false}. 
 * If @var{s} is zero, then return @code{true} if 
 * the derivatives of @var{A} with respect to 
 * all independent variables are zero, else @code{false}.
 */

BAP_DLL bool
bap_is_constant_polynom_mpzm (
    struct bap_polynom_mpzm *A,
    struct bav_symbol *s)
{
  struct bav_variable *w;
  ba0_int_p i;
  bool is_constant;

  is_constant = true;
  for (i = 0; i < A->total_rank.size && is_constant; i++)
    {
      w = A->total_rank.rg[i].var;
      is_constant = bav_is_constant_variable (w, s);
    }
  return is_constant;
}

/*
 * texinfo: bap_is_polynomial_with_constant_coefficients_mpzm
 * Return @code{true} if @var{A} is a polynomial in @var{v}
 * with coefficients constants with respect to derivation @var{x}.
 */

BAP_DLL bool
bap_is_polynomial_with_constant_coefficients_mpzm (
    struct bap_polynom_mpzm *A,
    struct bav_variable *v,
    struct bav_symbol *x)
{
  bool b = true;
  ba0_int_p i;

  if (x->type != bav_independent_symbol)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  for (i = 0; b && i < A->total_rank.size; i++)
    {
      struct bav_variable *w = A->total_rank.rg[i].var;
      if (w != v)
        b = bav_is_constant_variable (w, x);
    }

  return b;
}

/*
 * texinfo: bap_is_independent_polynom_mpzm
 * Return @code{true} if @var{A} does not depend on dependent variables 
 * (i.e. does not depend on derivatives, unless they are parameters)
 * else return @code{false}.
 */

BAP_DLL bool
bap_is_independent_polynom_mpzm (
    struct bap_polynom_mpzm *A)
{
  struct bav_variable *w;
//  struct bav_symbol *y;
  bool is_independent;
//  ba0_int_p i, k;
  ba0_int_p i;

  is_independent = true;
  for (i = 0; is_independent && i < A->total_rank.size; i++)
    {
      w = A->total_rank.rg[i].var;
      is_independent = bav_symbol_type_variable (w) == bav_independent_symbol;
    }
  return is_independent;
}

static void diff_monome_mpzm (
    struct bap_polynom_mpzm *,
    struct bav_term *,
    struct bap_itermon_mpzm *,
    struct bav_symbol *);

/*
 * texinfo: bap_diff_polynom_mpzm
 * Assign to @var{R} the polynomial obtained by differentiating @var{A}
 * with respect to @var{s}. 
 * Rewrite to zero any monomial involving a zero derivative of a parameter.
 */

BAP_DLL void
bap_diff_polynom_mpzm (
    struct bap_polynom_mpzm *R,
    struct bap_polynom_mpzm *A,
    struct bav_symbol *s)
{
  struct bap_itermon_mpzm iter;
  struct bap_geobucket_mpzm geo;
  struct bap_polynom_mpzm R1;
  struct bav_term rgtot;
  struct ba0_mark M;

  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&rgtot);
  bav_set_term (&rgtot, &A->total_rank);
  bav_diff_term (&rgtot, &rgtot, s);

  bap_init_geobucket_mpzm (&geo);
  bap_init_polynom_mpzm (&R1);
  bap_begin_itermon_mpzm (&iter, A);
  while (!bap_outof_itermon_mpzm (&iter))
    {
      diff_monome_mpzm (&R1, &rgtot, &iter, s);
      bap_add_geobucket_mpzm (&geo, &R1);
      bap_next_itermon_mpzm (&iter);
    }
  ba0_pull_stack ();
  bap_set_polynom_geobucket_mpzm (R, &geo);
  ba0_restore (&M);
}

/*
   It is assumed that the ordering is such that a derivative is lower than
   its proper derivatives. This is a property of ordering but some functions
   alter orderings for their own purposes.
*/

static void
diff_monome_mpzm (
    struct bap_polynom_mpzm *R,
    struct bav_term *rgtot,
    struct bap_itermon_mpzm *iter,
    struct bav_symbol *s)
{
  struct bap_creator_mpzm crea;
  struct bav_term T, U;
  bav_Inumber num_der;
  bav_Inumber num_v, num_w, num_k = 0;
  bav_Idegree d;
  struct bav_variable *v, *w;
  enum bav_typeof_symbol type_v;
  ba0_mpzm_t c;
  ba0_int_p j, k, n, m;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  v = bav_symbol_to_variable (s);
  num_der = bav_variable_number (v);

  bav_init_term (&T);
  bav_init_term (&U);
  ba0_mpzm_init (c);

  bap_term_itermon_mpzm (&T, iter);
  bav_realloc_term (&U, T.size + 1);
  ba0_pull_stack ();

  bap_begin_creator_mpzm (&crea, R, rgtot, bap_approx_total_rank, T.size);
/*
   The monomial may be zero
*/
  for (j = 0; j < T.size; j++)
    {
      if (bav_is_zero_derivative_of_parameter (T.rg[j].var))
        goto fin;
    }
/*
   It is non zero
*/
  for (j = 0; j < T.size; j++)
    {
      v = T.rg[j].var;
      type_v = bav_symbol_type_variable (v);
      num_v = bav_variable_number (v);
      d = T.rg[j].deg;
/*
   v^d is the current rank of the term. Let's differentiate it.
*/
      if (type_v == bav_dependent_symbol)
        {
          w = bav_diff_variable (v, s);
/*
   w may be zero.
*/
          if (bav_is_zero_derivative_of_parameter (w))
            continue;
/*
   It is non zero
*/
          num_w = bav_variable_number (w);
/* 
   Look for the index k at which the derivative w of v must be inserted.
*/
          for (k = j - 1;; k--)
            {
              if (k < 0)
                break;
              num_k = bav_variable_number (T.rg[k].var);
              if (num_w <= num_k)
                break;
            }
/*
   Building the differentiated term.
*/
          n = 0;
          m = 0;
          if (k < 0)
            {
              U.size = T.size + 1;
              U.rg[n].var = w;
              U.rg[n++].deg = 1;
            }
          else
            {
              while (m < k)
                U.rg[n++] = T.rg[m++];
              if (num_w == num_k)
                {
                  U.size = T.size;
                  U.rg[n].var = T.rg[m].var;
                  U.rg[n++].deg = T.rg[m++].deg + 1;
                }
              else
                {
                  U.size = T.size + 1;
                  U.rg[n++] = T.rg[m++];
                  U.rg[n].var = w;
                  U.rg[n++].deg = 1;
                }
            }
          while (m < j)
            U.rg[n++] = T.rg[m++];
          if (d > 1)
            {
              U.rg[n].var = T.rg[m].var;
              U.rg[n++].deg = T.rg[m++].deg - 1;
            }
          else
            {
              U.size--;
              m++;
            }
          while (m < T.size)
            U.rg[n++] = T.rg[m++];
          if (d > 1)
            {
              ba0_push_another_stack ();
              ba0_mpzm_mul_ui (c, *bap_coeff_itermon_mpzm (iter),
                  (unsigned long int) d);
              ba0_pull_stack ();
              bap_write_creator_mpzm (&crea, &U, c);
            }
          else
            bap_write_creator_mpzm (&crea, &U,
                *bap_coeff_itermon_mpzm (iter));
        }
      else if (type_v == bav_independent_symbol)
        {
          if (v->root == s)
            {
/*
   Building the differentiated term.
*/
              n = 0;
              m = 0;
              while (m < j)
                U.rg[n++] = T.rg[m++];
              if (d > 1)
                {
                  U.size = T.size;
                  U.rg[n].var = T.rg[m].var;
                  U.rg[n++].deg = T.rg[m++].deg - 1;
                }
              else
                {
                  U.size = T.size - 1;
                  m++;
                }
              while (m < T.size)
                U.rg[n++] = T.rg[m++];
              if (d > 1)
                {
                  ba0_push_another_stack ();
                  ba0_mpzm_mul_ui (c, *bap_coeff_itermon_mpzm (iter),
                      (unsigned long int) d);
                  ba0_pull_stack ();
                  bap_write_creator_mpzm (&crea, &U, c);
                }
              else
                bap_write_creator_mpzm (&crea, &U,
                    *bap_coeff_itermon_mpzm (iter));
            }
          else if (num_v < num_der)
            break;
        }
      else
        break;
    }
fin:
  ba0_restore (&M);
  bap_close_creator_mpzm (&crea);
}

/*
 * texinfo: bap_diff2_polynom_mpzm
 * Assign to @var{R} the polynomial obtained by differentiating @var{A}
 * with respect to @var{theta}. Rewrite to zero any monomial involving 
 * a zero derivative of a parameter.
 * The term @var{theta} encodes a derivation operator: every variable
 * should correspond to a derivation. 
 */

BAP_DLL void
bap_diff2_polynom_mpzm (
    struct bap_polynom_mpzm *R,
    struct bap_polynom_mpzm *A,
    struct bav_term *T)
{
  bav_Idegree d;
  ba0_int_p i;
  bool first;

  if (bav_is_one_term (T))
    {
      if (R != A)
        bap_set_polynom_mpzm (R, A);
    }
  else
    {
      first = true;
      for (i = 0; i < T->size; i++)
        {
          for (d = 0; d < T->rg[i].deg; d++)
            {
              bap_diff_polynom_mpzm (R, first ? A : R, T->rg[i].var->root);
              first = false;
            }
        }
    }
}

/*
 * texinfo: bap_involved_derivations_polynom_mpzm
 * Append to @var{T} the derivations involved in the derivatives @var{P}
 * depends on. The independent variables occurring in @var{P} are not
 * taken into account.
 */

BAP_DLL void
bap_involved_derivations_polynom_mpzm (
    struct bav_tableof_variable *T,
    struct bap_polynom_mpzm *P)
{
  struct bav_variable *v, *x;
  ba0_int_p i, j;

  for (i = 0; i < P->total_rank.size; i++)
    {
      v = P->total_rank.rg[i].var;
      if (bav_symbol_type_variable (v) == bav_dependent_symbol)
        {
          for (j = 0; j < bav_global.R.ders.size; j++)
            {
              if (v->order.tab[j] > 0)
                {
                  x = bav_derivation_index_to_derivation (j);
                  if (!ba0_member_table (x, (struct ba0_table *) T))
                    {
                      ba0_realloc_table ((struct ba0_table *) T,
                          bav_global.R.ders.size);
                      T->tab[T->size] = x;
                      T->size += 1;
                    }
                }
            }
        }
    }
}

/*
 * texinfo: bap_involved_parameters_polynom_mpzm
 * Append to @var{T} the parameters occurring in @var{P}.
 * Every parameter already present in @var{T} is supposed to be
 * registered in the dictionary @var{dict}.
 */

BAP_DLL void
bap_involved_parameters_polynom_mpzm (
    struct bav_dictionary_symbol *dict,
    struct bav_tableof_symbol *T,
    struct bap_polynom_mpzm *P)
{
  struct bav_symbol *y;
  ba0_int_p i;

  for (i = 0; i < P->total_rank.size; i++)
    {
      y = P->total_rank.rg[i].var->root;
      if (bav_is_a_parameter (y, (struct bav_parameter **) 0))
        {
          if (bav_get_dictionary_symbol (dict, T, y) == BA0_NOT_AN_INDEX)
            {
              if (T->size == T->alloc)
                {
                  ba0_int_p new_alloc = 2 * T->alloc + 1;
                  ba0_realloc_table ((struct ba0_table *) T, new_alloc);
                }
              bav_add_dictionary_symbol (dict, T, y, T->size);
              T->tab[T->size] = y;
              T->size += 1;
            }
        }
    }
}

#undef BAD_FLAG_mpzm
