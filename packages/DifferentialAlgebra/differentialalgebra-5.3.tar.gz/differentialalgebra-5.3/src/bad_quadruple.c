#include "bad_quench_regchain.h"
#include "bad_reduction.h"
#include "bad_regularize.h"
#include "bad_quadruple.h"
#include "bad_splitting_tree.h"
#include "bad_global.h"
#include "bad_stats.h"

/*
 * texinfo: bad_init_quadruple
 * Initialize @var{G}.
 */

BAD_DLL void
bad_init_quadruple (
    struct bad_quadruple *G)
{
  bad_init_regchain (&G->A);
  G->D = (struct bad_listof_critical_pair *) 0;
  G->P = G->S = (struct bap_listof_polynom_mpz *) 0;
}

/*
 * texinfo: bad_new_quadruple
 * Allocate a new quadruple, initialize it and return it.
 */

BAD_DLL struct bad_quadruple *
bad_new_quadruple (
    void)
{
  struct bad_quadruple *G;

  G = (struct bad_quadruple *) ba0_alloc (sizeof (struct bad_quadruple));
  bad_init_quadruple (G);
  return G;
}

/*
 * texinfo: bad_set_number_quadruple
 * Set the number of @var{G} to @var{number}.
 */

BAD_DLL void
bad_set_number_quadruple (
    struct bad_quadruple *G,
    ba0_int_p number)
{
  bad_set_number_regchain (&G->A, number);
}

/*
 * texinfo: bad_set_next_number_quadruple
 * Set the number of @var{G} to the next number obtained from @var{tree}.
 */

BAD_DLL void
bad_set_next_number_quadruple (
    struct bad_quadruple *G,
    struct bad_splitting_tree *tree)
{
  ba0_int_p n = bad_next_number_splitting_tree (tree);
  bad_set_number_quadruple (G, n);
}

/*
 * texinfo: bad_get_number_quadruple
 * Return the number of @var{G}.
 */

BAD_DLL ba0_int_p
bad_get_number_quadruple (
    struct bad_quadruple *G)
{
  return bad_get_number_regchain (&G->A);
}

/*
 * texinfo: bad_mark_indets_quadruple
 * Append to @var{vars} the variables occurring in @var{Q} which
 * are not already present in @var{vars}.
 * Every element of @var{vars} is supposed to be registered in
 * the dictionary @var{dict}.
 */

BAD_DLL void
bad_mark_indets_quadruple (
    struct bav_dictionary_variable *dict,
    struct bav_tableof_variable *vars,
    struct bad_quadruple *Q)
{
  struct bad_listof_critical_pair *L;

  bad_mark_indets_regchain (dict, vars, &Q->A);
  for (L = Q->D; L != (struct bad_listof_critical_pair *) 0; L = L->next)
    {
      bap_mark_indets_polynom_mpz (dict, vars, &L->value->p);
      bap_mark_indets_polynom_mpz (dict, vars, &L->value->q);
    }
  bap_mark_indets_listof_polynom_mpz (dict, vars, Q->P);
  bap_mark_indets_listof_polynom_mpz (dict, vars, Q->S);
}

/*
 * texinfo: bad_set_quadruple
 * Assign @var{Q} to @var{P}.
 */

BAD_DLL void
bad_set_quadruple (
    struct bad_quadruple *P,
    struct bad_quadruple *Q)
{
  if (P != Q)
    {
      bad_set_regchain (&P->A, &Q->A);
      P->D =
          (struct bad_listof_critical_pair *) ba0_copy ("%l[%critical_pair]",
          Q->D);
      P->P = (struct bap_listof_polynom_mpz *) ba0_copy ("%l[%Az]", Q->P);
      P->S = (struct bap_listof_polynom_mpz *) ba0_copy ("%l[%Az]", Q->S);
    }
}

/*
 * Variant of bad_set_quadruple where the regular chain is given separately
 */

static void
bad_set2_quadruple (
    struct bad_quadruple *P,
    struct bad_quadruple *Q,
    struct bad_regchain *A)
{
  if (P != Q)
    {
      bad_set_regchain (&P->A, A);
      P->D =
          (struct bad_listof_critical_pair *) ba0_copy ("%l[%critical_pair]",
          Q->D);
      P->P = (struct bap_listof_polynom_mpz *) ba0_copy ("%l[%Az]", Q->P);
      P->S = (struct bap_listof_polynom_mpz *) ba0_copy ("%l[%Az]", Q->S);
    }
  else
    bad_set_regchain (&P->A, A);
}

/*
 * texinfo: bad_insert_in_S_quadruple
 * Assign @var{Q} to @var{P}.
 * Then insert @var{poly} in the field @code{S} of @var{P}.
 */

BAD_DLL void
bad_insert_in_S_quadruple (
    struct bad_quadruple *P,
    struct bad_quadruple *Q,
    struct bap_polynom_mpz *poly)
{
  if (P != Q)
    {
      bad_set_regchain (&P->A, &Q->A);
      P->D =
          (struct bad_listof_critical_pair *) ba0_copy ("%l[%critical_pair]",
          Q->D);
      P->P = (struct bap_listof_polynom_mpz *) ba0_copy ("%l[%Az]", Q->P);
      P->S = (struct bap_listof_polynom_mpz *) ba0_copy ("%l[%Az]", Q->S);
    }
  P->S = bad_insert_in_listof_polynom_mpz (poly, P->S);
}

/*
 * texinfo: bad_insert_in_P_quadruple
 * Assign @var{Q} to @var{P}.
 * Then insert @var{poly} in the field @code{P} of @var{P}.
 */

BAD_DLL void
bad_insert_in_P_quadruple (
    struct bad_quadruple *P,
    struct bad_quadruple *Q,
    struct bap_polynom_mpz *poly)
{
  if (P != Q)
    {
      bad_set_regchain (&P->A, &Q->A);
      P->D =
          (struct bad_listof_critical_pair *) ba0_copy ("%l[%critical_pair]",
          Q->D);
      P->P = (struct bap_listof_polynom_mpz *) ba0_copy ("%l[%Az]", Q->P);
      P->S = (struct bap_listof_polynom_mpz *) ba0_copy ("%l[%Az]", Q->S);
    }
  P->P = bad_insert_in_listof_polynom_mpz (poly, P->P);
}

/*
 * texinfo: bad_scanf_quadruple
 * The parsing function for quadruples.
 * It is called by @code{ba0_scanf/%quadruple}.
 * The expected format is @code{quadruple %d (regular chain, D = list of critical pairs, P = list of polynomials, S = list of polynomials)}.
 * The quadruple number may be omitted.
 */

BAD_DLL void *
bad_scanf_quadruple (
    void *A)
{
  struct bad_quadruple *G;

  if (A == (void *) 0)
    G = bad_new_quadruple ();
  else
    G = (struct bad_quadruple *) A;

  if (ba0_type_token_analex () != ba0_string_token &&
      strcmp (ba0_value_token_analex (), "quadruple") != 0)
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

  ba0_get_token_analex ();
  if (ba0_type_token_analex () == ba0_integer_token)
    {
      ba0_int_p n;

      ba0_scanf
          ("%d (%regchain, D = %l[%critical_pair], P = %l[%Az], S = %l[%Az])",
          &n, &G->A, &G->D, &G->P, &G->S);
      bad_set_number_quadruple (G, n);
    }
  else
    ba0_scanf
        ("(%regchain, D = %l[%critical_pair], P = %l[%Az], S = %l[%Az])",
        &G->A, &G->D, &G->P, &G->S);

  return G;
}

/*
 * texinfo: bad_printf_quadruple
 * The printing function for quadruples.
 * It is called by @code{ba0_printf/%quadruple}.
 */

BAD_DLL void
bad_printf_quadruple (
    void *A)
{
  struct bad_quadruple *G = (struct bad_quadruple *) A;

  ba0_printf
      ("quadruple %d (%regchain,\nD = %l[\n%critical_pair],\nP = %l[%Az],\nS = %l[%Az]\n)",
      bad_get_number_quadruple (G), &G->A, G->D, G->P, G->S);
}

/*
 * Readonly static data
 */

static char _struct_quadruple[] = "struct bad_quadruple";

BAD_DLL ba0_int_p
bad_garbage1_quadruple (
    void *A,
    enum ba0_garbage_code code)
{
  struct bad_quadruple *G = (struct bad_quadruple *) A;
  ba0_int_p n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (G, sizeof (struct bad_quadruple), _struct_quadruple);

  n += bad_garbage1_regchain (&G->A, ba0_embedded);
  n += ba0_garbage1 ("%l[%critical_pair]", G->D, ba0_isolated);
  n += ba0_garbage1 ("%l[%Az]", G->P, ba0_isolated);
  n += ba0_garbage1 ("%l[%Az]", G->S, ba0_isolated);

  return n;
}

BAD_DLL void *
bad_garbage2_quadruple (
    void *A,
    enum ba0_garbage_code code)
{
  struct bad_quadruple *G;

  if (code == ba0_isolated)
    G = (struct bad_quadruple *) ba0_new_addr_gc_info (A, _struct_quadruple);
  else
    G = (struct bad_quadruple *) A;

  bad_garbage2_regchain (&G->A, ba0_embedded);
  G->D = ba0_garbage2 ("%l[%critical_pair]", G->D, ba0_isolated);
  G->P = ba0_garbage2 ("%l[%Az]", G->P, ba0_isolated);
  G->S = ba0_garbage2 ("%l[%Az]", G->S, ba0_isolated);

  return G;
}

BAD_DLL void *
bad_copy_quadruple (
    void *A)
{
  struct bad_quadruple *G;

  G = bad_new_quadruple ();
  bad_set_quadruple (G, (struct bad_quadruple *) A);
  return G;
}

/*
 * texinfo: bad_insert_in_listof_polynom_mpz
 * Insert a copy of @var{p} in @var{L}. In place function.
 * The list @var{L} is assumed to be the component @var{P} or @var{S} of
 * some quadruple. If @var{p} is already present in @var{L}, it is
 * not duplicated.  The systematic use of this function keeps lists sorted.
 */

BAD_DLL struct bap_listof_polynom_mpz *
bad_insert_in_listof_polynom_mpz (
    struct bap_polynom_mpz *p,
    struct bap_listof_polynom_mpz *L)
{
  struct bap_listof_polynom_mpz *R, *cour, *prec, *cons;
  ba0_int_p nbmon_p, nbmon_c;
  bool forget, found;

  nbmon_p = bap_nbmon_polynom_mpz (p);

  found = false;
  forget = false;

  prec = (struct bap_listof_polynom_mpz *) 0;
  cour = L;
  while (cour != (struct bap_listof_polynom_mpz *) 0 && !found && !forget)
    {
      nbmon_c = bap_nbmon_polynom_mpz (cour->value);
      if (nbmon_p < nbmon_c)
        found = true;
      else if (nbmon_p == nbmon_c)
        {
          if (bap_lt_rank_polynom_mpz (p, cour->value))
            found = true;
          else if (bap_equal_polynom_mpz (p, cour->value))
            forget = true;
        }
      if (!found && !forget)
        {
          prec = cour;
          cour = cour->next;
        }
    }
/*
 * forget = true means that p is already present. Just forget it.
 * Otherwise, a new cons should be inserted in front of cour.
 */
  if (!forget)
    {
      cons =
          (struct bap_listof_polynom_mpz *) ba0_alloc (sizeof (struct
              bap_listof_polynom_mpz));
      cons->next = cour;
      cons->value = (struct bap_polynom_mpz *) bap_copy_polynom_mpz (p);
/*
 * Insertion at the beginning of the list ?
 */
      if (prec == (struct bap_listof_polynom_mpz *) 0)
        R = cons;
      else
        {
          prec->next = cons;
          R = L;
        }
    }
  else
    R = L;
  return R;
}

/*
 * texinfo: bad_delete_from_listof_polynom_mpz
 * Remove @var{p} from the list @var{L}.
 * The argument @var{deletion} is set to @code{true} if @var{p} was present
 * in @var{L}, else it is set to @code{false}. It may be the zero pointer.
 */

BAD_DLL struct bap_listof_polynom_mpz *
bad_delete_from_listof_polynom_mpz (
    struct bap_polynom_mpz *p,
    struct bap_listof_polynom_mpz *L,
    bool *deletion)
{
  struct bap_listof_polynom_mpz *prec, *cour, *R;
  bool found;

  found = false;

  prec = (struct bap_listof_polynom_mpz *) 0;
  cour = L;
  while (cour != (struct bap_listof_polynom_mpz *) 0 && !found)
    {
      found = bap_equal_polynom_mpz (p, cour->value);
      if (!found)
        {
          prec = cour;
          cour = cour->next;
        }
    }
/*
 * found = p is equal to cour->value
 */
  if (!found)
    {
      if (deletion)
        *deletion = false;
      R = L;
    }
  else
    {
      if (deletion)
        *deletion = true;
/*
 * Deletion of the first element ?
 */
      if (prec == (struct bap_listof_polynom_mpz *) 0)
        R = L->next;
      else
        {
          prec->next = cour->next;
          R = L;
        }
    }
  return R;
}

/*
 * texinfo: bad_preprocess_equation_quadruple
 * Simplify @var{A} using the inequations of @var{G}
 * by means of gcd computations. 
 * Factors of @var{A} which belong to the base field @var{K} or which
 * divide some inequation of @var{G} are discarded.
 * This simplification process may exhibit a factorization of some 
 * inequation of @var{G}. Any such factorization is
 * recorded as an entry in @var{ineqs} and @var{factored_ineqs}. 
 * Factors of inequations which cannot vanish are also discarded: 
 * the nonzero elements of the base field @var{K}.
 * If nonzero, the argument @var{discarded_branch} is set to @code{true}
 * if at least one factor which is not a base field element
 * is discarded.
 */

BAD_DLL void
bad_preprocess_equation_quadruple (
    struct bap_product_mpz *A,
    struct bap_tableof_polynom_mpz *ineqs,
    struct bap_tableof_product_mpz *factored_ineqs,
    bool *discarded_branch,
    struct bad_quadruple *G,
    struct bad_base_field *K)
{
  struct bap_product_mpz prod, prod_gcd;
  struct bap_tableof_polynom_mpz polys;
  struct bap_listof_polynom_mpz *S;
  struct bap_polynom_mpz gcd, cof;
  struct ba0_mark M;
  ba0_int_p i, length;
  bool discarded, removed, already_stored;

  ba0_reset_table ((struct ba0_table *) ineqs);
  ba0_reset_table ((struct ba0_table *) factored_ineqs);

  if (bap_is_numeric_product_mpz (A))
    {
      if (!bap_is_zero_product_mpz (A))
        ba0_mpz_set_si (A->num_factor, 1);
      return;
    }

  length = ba0_length_list ((struct ba0_list *) G->S);
  ba0_realloc_table ((struct ba0_table *) ineqs, length);
  ba0_realloc2_table ((struct ba0_table *) factored_ineqs, length,
      (ba0_new_function *) & bap_new_product_mpz);

  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_product_mpz (&prod);
  bap_set_product_mpz (&prod, A);

  ba0_mpz_set_si (prod.num_factor, 1);

  ba0_init_table ((struct ba0_table *) &polys);
  ba0_realloc_table ((struct ba0_table *) &polys, 2);

  bap_init_product_mpz (&prod_gcd);
  bap_init_polynom_mpz (&gcd);
  bap_init_polynom_mpz (&cof);

  discarded = false;

  i = 0;
  while (i < prod.size)
    {
/*
 * removed = the ith component of the product is removed (it corresponds
 *           to a polynomial which cannot vanish).
 */
      if (bad_member_nonzero_polynom_base_field (&prod.tab[i].factor, K))
        {
          if (i != prod.size - 1)
            BA0_SWAP (struct bap_polynom_mpz,
                prod.tab[i].factor,
                prod.tab[prod.size - 1].factor);
          prod.size -= 1;
          removed = true;
        }
      else
        {
          removed = false;
          S = G->S;
          already_stored = false;
          while (!removed && S != (struct bap_listof_polynom_mpz *) 0)
            {
              polys.tab[0] = &prod.tab[i].factor;
              polys.tab[1] = S->value;
              polys.size = 2;
              baz_gcd_tableof_polynom_mpz (&prod_gcd, &polys, false);
              if (!bap_is_numeric_product_mpz (&prod_gcd))
                {
                  discarded = true;
/*
 * Non-trivial gcd between the ith component and the current inequation.
 * Factor the gcd out. May lead to a component that should be removed.
 */
                  bap_expand_product_mpz (&gcd, &prod_gcd);
                  bap_exquo_polynom_mpz (&prod.tab[i].factor,
                      &prod.tab[i].factor, &gcd);
                  removed =
                      bad_member_nonzero_polynom_base_field (&prod.tab[i].
                      factor, K);
                  if (!already_stored && (prod_gcd.size > 1
                          || !bap_equal_polynom_mpz (S->value, &gcd)))
                    {
/*
 * The non-trivial gcd is also a non-trivial factor of the current inequation.
 * Simplify the inequation.
 */
                      bap_exquo_polynom_mpz (&cof, S->value, &gcd);

                      ba0_pull_stack ();

                      ineqs->tab[ineqs->size] = S->value;
                      bap_mul_product_polynom_mpz (factored_ineqs->tab
                          [factored_ineqs->size], &prod_gcd, &cof, 1);

                      ineqs->size += 1;
                      factored_ineqs->size += 1;

                      ba0_push_another_stack ();
                      already_stored = true;
                    }
                }
              else
                {
                  S = S->next;
                  already_stored = false;
                }
            }
        }
/*
      else
        removed = false;
 */

      if (!removed)
        {
          prod.tab[i].exponent = 1;
          i += 1;
        }
    }

  ba0_pull_stack ();
  bap_set_product_mpz (A, &prod);
  if (discarded_branch)
    *discarded_branch = discarded;
  ba0_restore (&M);
}

/*
 * texinfo: bad_report_simplification_of_inequations_quadruple
 * Replace in the field @code{S} of each quadruple of @var{tabG}
 * any occurrence of any polynomial of @var{ineqs} by its factors,
 * given in @var{factored_ineqs}. These factors are supposed to
 * be processed by @code{bad_preprocess_equation_quadruple}.
 */

BAD_DLL void
bad_report_simplification_of_inequations_quadruple (
    struct bad_tableof_quadruple *tabG,
    struct bap_tableof_polynom_mpz *ineqs,
    struct bap_tableof_product_mpz *factored_ineqs)
{
  struct bad_quadruple *G;
  struct bap_product_mpz *prod;
  struct bap_polynom_mpz *p;
  ba0_int_p i, j, k;
  bool found;

  if (ineqs->size != factored_ineqs->size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  for (k = 0; k < ineqs->size; k++)
    {
      p = ineqs->tab[k];
      prod = factored_ineqs->tab[k];
      for (i = 0; i < tabG->size; i++)
        {
          G = tabG->tab[i];
          G->S = bad_delete_from_listof_polynom_mpz (p, G->S, &found);
          if (found)
            {
              for (j = 0; j < prod->size; j++)
                G->S =
                    bad_insert_in_listof_polynom_mpz (&prod->tab[j].factor,
                    G->S);
            }
        }
    }
}

/*
 * texinfo: bad_split_on_factors_of_equations_quadruple
 * Generate in @var{tabG} the quadruples obtained from the top quadruple
 * @var{G} of @var{tabG}, covering the cases where @var{prod} and @var{uctum} 
 * both vanish. 
 *
 * To each factor of @var{prod}, there exists a corresponding entry 
 * of @var{keep}. The factors of @var{prod} whose corresponding entry
 * in @var{keep} is @code{false} are not considered.
 *
 * Denote @math{a_1 \cdots a_n} the considered factors of @var{prod}
 *
 * If @var{uctum} is not @code{BAP_NOT_A_POLYNOMIAL_mpz} then @math{n}
 * new quadruples @math{Q_i} equal to
 * @math{G, a_i = 0, a_1 \cdots a_{i-1} \neq 0, @var{uctum} = 0}.
 * Moreover, the quadruple @var{G} is augmented with 
 * @math{a_1 \cdots a_n \neq 0}.
 *
 * If @var{uctum} is @code{BAP_NOT_A_POLYNOMIAL_mpz} then @math{n-1}
 * new quadruples @math{Q_i} equal to
 * @math{G, a_i = 0, a_1 \cdots a_{i-1} \neq 0} are generated.
 * Moreover, the quadruple @var{G} is augmented with
 * @math{a_1 \cdots a_{n-1} \neq 0}.
 *
 * In quadruples, new equations are stored in the field @code{P}.
 * New inequations are stored in the field @code{S}.
 *
 * The argument @var{tree} is used to assign a @emph{number} to each 
 * new quadruple @math{Q_i}. These numbers are equal to @math{i} plus
 * some offset.
 * The number of @var{G} is not modified.
 */

BAD_DLL void
bad_split_on_factors_of_equations_quadruple (
    struct bad_tableof_quadruple *tabG,
    struct bad_splitting_tree *tree,
    struct bap_product_mpz *prod,
    struct ba0_tableof_bool *keep,
    struct bap_polynom_mpz *uctum)
{
  struct bad_quadruple *G, *H;
  struct bap_polynom_mpz *p;
  ba0_int_p g, h, i, n;

  if (bap_is_zero_product_mpz (prod) || keep->size != prod->size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  g = tabG->size - 1;
  G = tabG->tab[g];

  ba0_realloc2_table ((struct ba0_table *) tabG, tabG->size + prod->size,
      (ba0_new_function *) & bad_new_quadruple);
/*
 * if uctum is specified then we are splitting cases on some initial
 * or separant and a quadruple with all factors nonzero must be generated ;
 * otherwise, just do not take into account the last factor of prod
 */
  n = uctum != (struct bap_polynom_mpz *) 0 ? prod->size : prod->size - 1;
  for (i = 0; i < n; i++)
    {
      struct bav_variable *v;
/*
 * create a new quadruple H and fill it with G + "p = 0" [+ "uctum = 0"]
 * then add "p != 0" to G
 */
      if (keep->tab[i])
        {
          p = &prod->tab[i].factor;
          v = bap_leader_polynom_mpz (p);
          h = tabG->size;
          H = tabG->tab[h];
          bad_set_next_number_quadruple (H, tree);
          bad_insert_in_P_quadruple (H, G, p);
          if (uctum != (struct bap_polynom_mpz *) 0 &&
              !bap_is_zero_polynom_mpz (uctum))
            bad_insert_in_P_quadruple (H, H, uctum);
          tabG->size += 1;
          bad_insert_in_S_quadruple (G, G, p);
        }
    }
/*
 * move again G at the end of tabG
 */
  ba0_move_to_tail_table ((struct ba0_table *) tabG, (struct ba0_table *) tabG,
      g);
}

/*
 * texinfo: bad_simplify_and_store_in_P_quadruple
 * Store in the @code{P} field of @var{G} the polynomial @var{p}
 * after the simplifications performed by
 * @code{bad_preprocess_equation_quadruple}.
 * Return @code{false} if @var{p} is proved to be nonzero so that
 * @var{G} becomes inconsistent else return @code{false}.
 * If nonzero, the argument @var{discarded_branch} is set to @code{true}
 * if at least one factor which is not a base field element
 * is discarded.
 */

BAD_DLL bool
bad_simplify_and_store_in_P_quadruple (
    struct bad_quadruple *G,
    bool *discarded_branch,
    struct bap_polynom_mpz *p,
    struct bad_base_field *K)
{
  struct bap_tableof_polynom_mpz ineqs;
  struct bap_tableof_product_mpz factored_ineqs;
  struct bap_product_mpz prod;
  struct bap_polynom_mpz *q;
  struct ba0_mark M;

  if (bap_is_zero_polynom_mpz (p))
    return true;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_init_table ((struct ba0_table *) &ineqs);
  ba0_init_table ((struct ba0_table *) &factored_ineqs);
  bap_init_product_mpz (&prod);
  bap_set_product_polynom_mpz (&prod, p, 1);
  bad_preprocess_equation_quadruple (&prod, &ineqs, &factored_ineqs,
      discarded_branch, G, K);

  ba0_pull_stack ();

  q = bap_new_polynom_mpz ();
  bap_expand_product_mpz (q, &prod);

  ba0_restore (&M);
/*
 * Nonzero factors of prod are removed by bad_simplify_relation_mod_quadruple
 * Might be useful for some bad_nonzero functions and when all factors
 * of prod are nonzero.
 *
 */
  if (bad_member_nonzero_polynom_base_field (q, K))
    return false;
  else
    {
      G->P = bad_insert_in_listof_polynom_mpz (p, G->P);
      return true;
    }
}

/*
 * texinfo: bad_simplify_and_store_in_S_quadruple
 * Store in the @code{S} field of @var{G} the polynomial @var{p}
 * after the simplifications performed by 
 * @code{bad_preprocess_equation_quadruple}.
 * Return @code{false} if @var{p} is proved to be zero so that
 * @var{G} becomes inconsistent else return @code{false}.
 * If nonzero, the argument @var{discarded_branch} is set to @code{true}
 * if at least one factor which is not a base field element
 * is discarded.
 */

BAD_DLL bool
bad_simplify_and_store_in_S_quadruple (
    struct bad_quadruple *G,
    bool *discarded_branch,
    struct bap_polynom_mpz *p,
    struct bad_base_field *K)
{
  struct bap_tableof_polynom_mpz ineqs;
  struct bap_tableof_product_mpz factored_ineqs;
  struct bap_product_mpz prod;
  ba0_int_p i;
  bool consistent;
  struct ba0_mark M;

  if (bap_is_zero_polynom_mpz (p))
    return false;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_init_table ((struct ba0_table *) &ineqs);
  ba0_init_table ((struct ba0_table *) &factored_ineqs);
  bap_init_product_mpz (&prod);
  bap_set_product_polynom_mpz (&prod, p, 1);
  bad_preprocess_equation_quadruple (&prod, &ineqs, &factored_ineqs,
      discarded_branch, G, K);

  consistent = true;
  for (i = 0; i < prod.size && consistent; i++)
    {
      if (!bad_member_nonzero_polynom_base_field (&prod.tab[i].factor, K))
        {
          ba0_pull_stack ();
          G->S = bad_insert_in_listof_polynom_mpz (&prod.tab[i].factor, G->S);
          ba0_push_another_stack ();
        }
      else if (bap_is_zero_polynom_mpz (p))
        consistent = false;
    }

  ba0_pull_stack ();
  ba0_restore (&M);

  return consistent;
}

/***********************************************************************
 * PICK AND REMOVE FROM QUADRUPLE
 **********************************************************************/

/*
 * Picks a polynomial from G->P and stores it in p.
 */

static void
bad_pick_from_P_quadruple (
    struct bap_polynom_mpz *p,
    struct bad_quadruple *G,
    struct bad_critical_pair * *pair)
{
  if (G->P == (struct bap_listof_polynom_mpz *) 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  bap_set_polynom_mpz (p, G->P->value);
  G->P = G->P->next;
  if (pair)
    *pair = (struct bad_critical_pair *) 0;
}

/*
 * Picks a pair from G->D. The picked pair is stored in *pair.
 * The Delta-polynomial is stored in p.
 */

static void
bad_pick_from_D_quadruple (
    struct bap_polynom_mpz *p,
    struct bad_quadruple *G,
    struct bad_critical_pair * *pair)
{
  if (G->D == (struct bad_listof_critical_pair *) 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  bad_delta_polynom_critical_pair (p, G->D->value);
  if (pair)
    *pair = G->D->value;
  G->D = G->D->next;
}

/*
 * Picks elements of P first
 */

static void
bad_pick_and_remove_quadruple_P_first (
    struct bap_polynom_mpz *p,
    struct bad_quadruple *G,
    struct bad_critical_pair * *pair)
{
  if (G->P != (struct bap_listof_polynom_mpz *) 0)
    bad_pick_from_P_quadruple (p, G, pair);
  else
    bad_pick_from_D_quadruple (p, G, pair);
}

/*
 * Between a polynomial p and a critical pair {f, g}, picks
 * the one of lower "leader" (the leader of {f, g} being the 
 * lcd of the leaders of f and g).
 */

static void
bad_pick_and_remove_quadruple_lower_leader_first (
    struct bap_polynom_mpz *p,
    struct bad_quadruple *G,
    struct bad_critical_pair * *pair)
{
  struct bav_variable *u, *v;

  if (G->P == (struct bap_listof_polynom_mpz *) 0)
    bad_pick_from_D_quadruple (p, G, pair);
  else if (G->D == (struct bad_listof_critical_pair *) 0)
    bad_pick_from_P_quadruple (p, G, pair);
  else
    {
      u = bap_leader_polynom_mpz (G->P->value);
      v = bav_lcd_variable (bap_leader_polynom_mpz (&G->D->value->p),
          bap_leader_polynom_mpz (&G->D->value->q));
      if (bav_variable_number (u) < bav_variable_number (v))
        bad_pick_from_P_quadruple (p, G, pair);
      else
        bad_pick_from_D_quadruple (p, G, pair);
    }
}

/*
 * texinfo: bad_pick_and_remove_quadruple
 * It is assumed that one of the components @var{P} or @var{D} of the quadruple 
 * is non empty. Assign to @var{p} the first element of @var{P} or the 
 * @math{\Delta}-polynomial defined by the first critical pair of @var{D}.
 * The choice is defined by @var{strategy}.
 * The picked element is removed from the list.
 * If @var{p} is picked from @var{P} then zero is assigned
 * to @var{pair} else the picked pair is assigned to @var{pair}.
 * The pointer @var{pair} is allowed to be zero.
 */

BAD_DLL void
bad_pick_and_remove_quadruple (
    struct bap_polynom_mpz *p,
    struct bad_quadruple *G,
    struct bad_critical_pair * *pair,
    struct bad_selection_strategy *S)
{
  switch (S->strategy)
    {
    case bad_equation_first_selection_strategy:
      bad_pick_and_remove_quadruple_P_first (p, G, pair);
      break;
    case bad_lower_leader_first_selection_strategy:
      bad_pick_and_remove_quadruple_lower_leader_first (p, G, pair);
      break;
    }
}

/*
 * texinfo: bad_reg_characteristic_quadruple
 * Denote @math{I} the unit ideal if @var{ideal} is zero and the ideal
 * defined by @var{ideal} otherwise.
 * It is assumed that 
 *      @math{G = \langle A,\, \emptyset,\, \emptyset,\, S \rangle}, that 
 *      @math{A = 0,\ S \neq 0} is a regular differential system and that
 *      @math{[A] : S^\infty \subset I}.
 * This function stores in @var{tabC} a list of regular differential chains
 *      @math{A_1, \ldots, A_t} such that
 * @math{[A] : S^\infty \subset [A_1] :{H_{A_1}}^\infty 
 *                  \cap \cdots \cap [A_t] : {H_{A_t}}^\infty \subset I}.
 * In the case @math{I} is prime the function only returns one
 * regular chain. If moreover @math{I} is a minimal prime of
 * @math{[C] : {H_C}^\infty} then the returned regular chain is a 
 * characteristic set of @math{I}. 
 * Polynomials are supposed to have coefficients in @var{K}.
 */

BAD_DLL void
bad_reg_characteristic_quadruple (
    struct bad_intersectof_regchain *tabC,
    struct bad_quadruple *G,
    struct bad_regchain *ideal,
    struct bad_base_field *K)
{
  ba0_realloc2_table ((struct ba0_table *) &tabC->inter, tabC->inter.size + 1,
      (ba0_new_function *) & bad_new_regchain);
  tabC->inter.size++;
  bad_set_regchain (tabC->inter.tab[tabC->inter.size - 1], &G->A);
  bad_reg_characteristic_regchain (tabC, G->S, ideal, K);
}

/***************************************************************************
 COMPLETE
 ***************************************************************************/

static void bad_insert_in_regchain (
    struct bad_regchain *,
    struct bap_polynom_mpz *,
    ba0_int_p *,
    ba0_int_p *);

static void bad_insert_parameter_defined_critical_pairs_in_D (
    struct bad_quadruple *,
    struct bap_polynom_mpz *,
    struct bad_selection_strategy *);

static void bad_insert_new_critical_pairs_in_D (
    struct bad_quadruple *,
    ba0_int_p,
    struct bap_polynom_mpz *,
    struct bad_selection_strategy *);

static bool bad_partially_reduce_S (
    struct bad_quadruple *,
    struct bav_tableof_term *,
    struct bad_base_field *);

/*
 * texinfo: bad_complete_quadruple
 * Denote @math{G = \langle A,\, D,\, P,\, S \rangle} the last element 
 * of @var{tabG}.
 * 
 * In the nondifferential context, store @var{r} in @math{A} and 
 * possibly a critical pair in @math{D} if @math{A} contains an
 * element with the same leader as @var{r}.
 * 
 * In the differential context,
 * it is assumed that @math{r} is partially reduced with respect to @math{A}.
 * The function stores @math{r} in @math{A}.
 * Some critical pairs are generated and stored in @math{D}.
 * This list is sorted according to @var{strategy}.
 * The elements of @math{S} are reduced partially with respect to @math{A}.
 * 
 * Both contexts.
 * 
 * The quenching operation, applied on @math{A} may split @math{A} in finitely
 * many different regular chains. In this case, the quadruple @math{G} is
 * split into the same number of quadruples.
 * The resulting quadruples are stored in @var{tabG}, at indices greater
 * than or equal to that of @math{G} (the functions reuses the input 
 * quadruple @math{G}).
 * 
 * The parameter @var{ideal} is provided to the quenching operation
 * and permits to avoid some splittings: if an element of @math{A} factors as
 * @math{f_1\,f_2 = 0} then the branch @math{f_i = 0} is generated only 
 * if @math{f_i} is zero or a zero divisor modulo @var{ideal}.
 * 
 * The initial and the separants of @math{r} are not stored in @math{S}.
 * Polynomials are supposed to have coefficients in @var{K}.
 *
 * If nonzero, the argument @var{discarded_branch} is set to @code{true}
 * if at least one branch of the splitting tree is discarded because
 * of the presence of inequations. This may happen either in the quenching
 * process and in the partial reduction process of the inequations.
 */

BAD_DLL void
bad_complete_quadruple (
    struct bad_tableof_quadruple *tabG,
    struct bav_tableof_term *theta,
    bool *discarded_branch,
    struct bad_splitting_tree *tree,
    struct bap_polynom_mpz *r,
    struct bad_regchain *ideal,
    struct bad_base_field *K,
    struct bad_selection_strategy *strategy)
{
  struct bad_quadruple *G;
  struct bad_intersectof_regchain *tabC;
  struct bad_quench_map map;
  struct bav_tableof_term *phi, *psi;
  struct bav_parameter *p;
  struct bav_variable *v;
  ba0_int_p j, k, l;
  bool first_loop, differential_ideal;
  bool discarded_by_quench, discarded_by_partial_reduction;
  struct ba0_mark M;

  G = tabG->tab[tabG->size - 1];
  differential_ideal = bad_defines_a_differential_ideal_regchain (&G->A);
  v = bap_leader_polynom_mpz (r);
/* 
 * A copy of r is inserted at index j in A (= G->A).
 * A [A->size .. l-1] = the polynomials thrown away from A due to 
 *      the insertion of r, in order to keep it differentially triangular
 */
  bad_insert_in_regchain (&G->A, r, &k, &l);
/*
 * The triangular set A is transformed into finitely many regular chains
 */
  tabC = bad_new_intersectof_regchain ();
  ba0_realloc_table ((struct ba0_table *) &tabC->inter, 1);
  tabC->inter.tab[0] = &G->A;
  tabC->inter.size = 1;

  ba0_push_another_stack ();
  ba0_record (&M);
  bad_init_from_complete_quench_map (&map, k, &G->A);
  ba0_pull_stack ();

  if (theta != (struct bav_tableof_term *) 0)
    {
      phi = (struct bav_tableof_term *) ba0_new_table ();
      psi = (struct bav_tableof_term *) ba0_new_table ();
    }
  else
    {
      phi = (struct bav_tableof_term *) 0;
      psi = (struct bav_tableof_term *) 0;
    }

  bad_quench_and_handle_exceptions_regchain (tabC, &map, phi,
      &discarded_by_quench, ideal, K);

  ba0_realloc2_table ((struct ba0_table *) tabG,
      tabG->size + tabC->inter.size - 1,
      (ba0_new_function *) & bad_new_quadruple);

  discarded_by_partial_reduction = false;
  first_loop = true;
  tabG->size -= 1;
  for (j = 0; j < tabC->inter.size; j++)
    {
      struct bad_quadruple *H;
      if (first_loop)
        {
          H = G;
          first_loop = false;
        }
      else
        H = bad_new_quadruple ();

      bad_set2_quadruple (H, G, tabC->inter.tab[j]);
      bad_set_next_number_quadruple (H, tree);

      tabG->tab[tabG->size] = H;
      tabG->size += 1;

      if (!differential_ideal)
        {
/*
 * Algebraic case - at most one thrown away polynomial
 */
          if (l != H->A.decision_system.size)
            {
              struct bad_critical_pair *pair;

              pair =
                  bad_new_critical_pair_polynom_mpz (H->A.decision_system.
                  tab[k], G->A.decision_system.tab[l - 1]);

              H->D =
                  (struct bad_listof_critical_pair *)
                  ba0_insert2_list (pair, (struct ba0_list *) G->D,
                  (ba0_cmp2_function *) & bad_is_a_simpler_critical_pair,
                  strategy);
            }
        }
      else
        {
/*
 * In the differential case, 
 *    o the list D of critical pairs is updated,
 *    o the elements of S are partially reduced with respect to r
 *
 * Observe that r = H->decision_system.tab [k] may have been
 *      modified by the quenching process
 *
 * There are two types of modifications to the list of critical pairs
 *    o the ones due to the parameter defining equations if the
 *      leader of r is a parameter (or a derivative of a parameter)
 *    o the other ones for which the ordinary case is separated from the
 *      partial one 
 */
          if (bav_is_a_parameter (v->root, &p))
            {
              if (bav_is_zero_derivative_of_parameter (v))
                BA0_RAISE_EXCEPTION (BA0_ERRALG);
              bad_insert_parameter_defined_critical_pairs_in_D (H,
                  H->A.decision_system.tab[k], strategy);
            }

          if (bav_global.R.ders.size == 1)
            {
/*
 * Ordinary case - at most one thrown away differential polynomial
 */
              if (l != H->A.decision_system.size)
                {
                  struct bad_critical_pair *pair;

                  pair =
                      bad_new_critical_pair_polynom_mpz (H->A.decision_system.
                      tab[k], G->A.decision_system.tab[l - 1]);

                  H->D =
                      (struct bad_listof_critical_pair *)
                      ba0_insert2_list (pair, (struct ba0_list *) G->D,
                      (ba0_cmp2_function *) & bad_is_a_simpler_critical_pair,
                      strategy);
                }
            }
          else
/*
 * Partial case
 */
            bad_insert_new_critical_pairs_in_D (H, l,
                H->A.decision_system.tab[k], strategy);

          if (!bad_partially_reduce_S (H, psi, K))
            {
/*
 * The only way the partial reduction process may remove a branch
 * is by detecting the reduction to zero of an inequation
 */
              discarded_by_partial_reduction = true;
              tabG->size -= 1;
            }
          else
            bad_set_next_number_quadruple (H, tree);
        }
    }

  ba0_restore (&M);

  if (theta != (struct bav_tableof_term *) 0)
    bav_lcm_tableof_term (theta, phi, psi);

  if (discarded_branch)
    *discarded_branch = discarded_by_quench || discarded_by_partial_reduction;
}

/*
 *    Insert r in A.
 *    The index of r in A is stored in *k.
 * 
 *    In the differential case, some polynomials may be thrown away
 * from A (the ones the leader of which is a derivative of the leader
 * of r). 
 *    These polynomials, which may be needed by the calling function,
 * are stored at the end of A (at indices > A->decision_system.size).
 * The first index after the last of these polynomials is stored in *l.
 * 
 *    At the end we therefore have
 * 
 *                      +------------------+-------------------+
 * A->decision_system   | kept pols.  r    | thrown away pols  |
 *                      +------------------+-------------------+
 *                                    ^     ^                   ^
 *                                    *k    size                *l
 * 
 *    Quenching is not called so that the resulting A is not yet a
 * regular chain.
 */

static void
bad_insert_in_regchain (
    struct bad_regchain *A,
    struct bap_polynom_mpz *r,
    ba0_int_p *k,
    ba0_int_p *l)
{
  struct bav_variable *u, *ui = BAV_NOT_A_VARIABLE;
  ba0_int_p i, old_size, new_size;
  bool loop, differential_ideal;
  ba0_mpz_t *lc;

  u = bap_leader_polynom_mpz (r);

  if (u->root->type != bav_dependent_symbol
      && u->root->type != bav_temporary_symbol)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  differential_ideal = bad_defines_a_differential_ideal_regchain (A);
  old_size = A->decision_system.size;
/*
 * Look for an index i such that r must be inserted in A at index i
 * Remove from A every differential polynomial whose leader is a
 *  derivative of the leader of r
 * If an element of A has the same leader as r, it is removed also
 */
  i = A->decision_system.size - 1;
  loop = true;
  while (i >= 0 && loop)
    {
      ui = bap_leader_polynom_mpz (A->decision_system.tab[i]);
      if (u == ui || (differential_ideal && bav_is_proper_derivative (ui, u)))
        {
          ba0_delete_table ((struct ba0_table *) &A->decision_system, i);
          i -= 1;
        }
      else if (bav_variable_number (u) > bav_variable_number (ui))
        loop = false;
      else
        i -= 1;
    }
/*
 * We exit with i = -1 or u > ui
 * In both cases, increase i
 */
  i += 1;
  new_size = A->decision_system.size;

#if defined (BA0_MEMCHECK)
  if (i <= new_size - 1)
    {
      ui = bap_leader_polynom_mpz (A->decision_system.tab[i]);
      if (bav_variable_number (u) >= bav_variable_number (ui))
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
    }
  if (i > 0)
    {
      ui = bap_leader_polynom_mpz (A->decision_system.tab[i - 1]);
      if (bav_variable_number (u) <= bav_variable_number (ui))
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
    }
#endif

  if (k != (ba0_int_p *) 0)
    *k = i;
  A->decision_system.size = old_size;
  bad_realloc_regchain (A, A->decision_system.size + 1);
  A->decision_system.size += 1;
/*
 *                      +-------------------+-------------------+---+
 * A->decision_system   | ......... | . | . | thrown away pols  | ? |
 *                      +-------------------+-------------------+---+
 *                                    ^      ^                    ^
 *                                    i   new_size             old_size
 */
  ba0_move_from_tail_table ((struct ba0_table *) &A->decision_system,
      (struct ba0_table *) &A->decision_system, i);
  bap_set_polynom_mpz (A->decision_system.tab[i], r);
  A->decision_system.size = new_size + 1;
  if (l != (ba0_int_p *) 0)
    *l = old_size + 1;
/*
 *                      +-----------------------+-------------------+
 * A->decision_system   | ......... | r | ..... | thrown away pols  |
 *                      +-----------------------+-------------------+
 *                                    ^          ^                    ^
 *                                    i       A->size                *l
 *
 * The following should be useless
 */
  lc = bap_numeric_initial_polynom_mpz (A->decision_system.tab[i]);
  if (ba0_mpz_sgn (*lc) < 0)
    bap_neg_polynom_mpz (A->decision_system.tab[i], A->decision_system.tab[i]);
}

/*
 * This function is called in the differential case only.
 * It is called when the leader of r has a symbol which is a parameter.
 * It inserts in D the critical pairs generated by r and the implicit
 *      parameter defining equations
 */

static void
bad_insert_parameter_defined_critical_pairs_in_D (
    struct bad_quadruple *G,
    struct bap_polynom_mpz *r,
    struct bad_selection_strategy *strategy)
{
  struct bad_critical_pair *pair;
  struct bap_polynom_mpz poly;
  struct bav_parameter *p;
  struct bav_tableof_symbol T;
  struct bav_variable *u, *v;
  struct ba0_mark M;
  ba0_int_p i;

  u = bap_leader_polynom_mpz (r);
  if (!bav_is_a_parameter (u->root, &p))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_init_table ((struct ba0_table *) &T);
  bav_annihilating_derivations_of_parameter (&T, p);

  bap_init_polynom_mpz (&poly);

  for (i = 0; i < T.size; i++)
    {
      v = bav_diff_variable (u, T.tab[i]);
      bap_set_polynom_variable_mpz (&poly, v, 1);

      ba0_pull_stack ();

      pair = bad_new_critical_pair_polynom_mpz (&poly, r);
      G->D = (struct bad_listof_critical_pair *) ba0_cons_list (pair,
          (struct ba0_list *) G->D);

      ba0_push_another_stack ();
    }

  ba0_pull_stack ();
  ba0_restore (&M);

  G->D =
      (struct bad_listof_critical_pair *) ba0_sort2_list ((struct ba0_list *)
      G->D, (ba0_cmp2_function *) & bad_is_a_simpler_critical_pair, strategy);
}

/*
 * This function is called in the partial case only.
 * It inserts in D the critical pairs generated by the insertion of r in A.
 *
 * The thrown away elements of A (with which critical pairs have to be formed)
 * are located in A [A->size .. l-1].
 */

static void
bad_insert_new_critical_pairs_in_D (
    struct bad_quadruple *G,
    ba0_int_p l,
    struct bap_polynom_mpz *r,
    struct bad_selection_strategy *strategy)
{
  struct bad_listof_critical_pair *cour;
  struct bad_critical_pair *pair;
  struct bav_rank rkp, rkq;
  struct bav_variable *u, *v;
  ba0_int_p i;
/*
 * Throw away non reduction critical pairs which involve one of
 *    the thrown away polynomials.
 *
 * remove = true if the pair is a triangular pair involving one of 
 * the thrown away elements.
 */
  cour = G->D;
  while (cour != (struct bad_listof_critical_pair *) 0)
    {
      pair = cour->value;
      if (!bad_is_a_reduction_critical_pair (pair, (struct bav_variable **) 0))
        {
          rkp = bap_rank_polynom_mpz (&pair->p);
          rkq = bap_rank_polynom_mpz (&pair->q);
          if (!bad_is_rank_of_regchain (&rkp, &G->A, (ba0_int_p *) 0)
              || !bad_is_rank_of_regchain (&rkq, &G->A, (ba0_int_p *) 0))
            pair->tag = bad_rejected_easy_critical_pair;
        }
      cour = cour->next;
    }
/*
 * Generate all the new critical pairs between r and the former elements of A
 */
  u = bap_leader_polynom_mpz (r);
  for (i = 0; i < l; i++)
    {
      v = bap_leader_polynom_mpz (G->A.decision_system.tab[i]);
      if (u->root == v->root)
        {
          pair =
              bad_new_critical_pair_polynom_mpz (r,
              G->A.decision_system.tab[i]);
          G->D =
              (struct bad_listof_critical_pair *) ba0_cons_list (pair,
              (struct ba0_list *) G->D);
        }
    }
/*
 * The list of critical pairs is now sorted by increasing order.
 * The simplest pairs to process occur at the beginning of the list
 *
 * The tagged pairs have a penalty.
 */
  G->D =
      (struct bad_listof_critical_pair *) ba0_sort2_list ((struct ba0_list *)
      G->D, (ba0_cmp2_function *) & bad_is_a_simpler_critical_pair, strategy);
}

/*
 * Reduce S partially with respect to A.
 * Return false if some element of S simplifies to zero.
 *
 * If nonzero, theta is assigned the lcm of the table of terms 
 * returned by the partial reduction algorithm.
 *
 * Subfunction of bad_complete_quadruple
 */

static bool
bad_partially_reduce_S (
    struct bad_quadruple *G,
    struct bav_tableof_term *theta,
    struct bad_base_field *K)
{
  bool *discarded_branch = 0;
  struct bap_listof_polynom_mpz *prec, *cour, *rmov;
  struct bap_product_mpz prod;
  struct bav_tableof_term *phi, *psi;
  ba0_int_p i;
  bool consistent;
  struct ba0_mark M;
/*
 * One first removes from S all the non partially reduced elements.
 * These discarded elements are stored in the list rmov.
 */
  prec = (struct bap_listof_polynom_mpz *) 0;
  cour = G->S;
  rmov = (struct bap_listof_polynom_mpz *) 0;
  while (cour != (struct bap_listof_polynom_mpz *) 0)
    {
      if (bad_is_a_partially_reduced_polynom_wrt_regchain (cour->value, &G->A))
        {
          prec = cour;
          cour = cour->next;
        }
      else
        {
          if (prec == (struct bap_listof_polynom_mpz *) 0)
            G->S = cour->next;
          else
            prec->next = cour->next;
          cour->next = rmov;
          rmov = cour;
          if (prec == (struct bap_listof_polynom_mpz *) 0)
            cour = G->S;
          else
            cour = prec->next;
        }
    }
/*
 * One then reduces each element of rmov partially with respect to A
 * and stores the factors of the so obtained products in S.
 */
  ba0_push_another_stack ();
  ba0_record (&M);

  if (theta)
    {
      phi = (struct bav_tableof_term *) ba0_new_table ();
      psi = (struct bav_tableof_term *) ba0_new_table ();
      bad_reset_theta (psi, &G->A);
    }
  else
    {
      phi = (struct bav_tableof_term *) 0;
      psi = (struct bav_tableof_term *) 0;
    }

  bap_init_product_mpz (&prod);

  consistent = true;
  while (rmov != (struct bap_listof_polynom_mpz *) 0 && consistent)
    {
      bad_reduce_polynom_by_regchain (&prod, (struct bap_product_mpz *) 0,
          phi, rmov->value, &G->A,
          bad_partial_reduction, bad_all_derivatives_to_reduce);
      if (theta)
        bav_lcm_tableof_term (psi, psi, phi);
      consistent = !bap_is_zero_product_mpz (&prod);

      ba0_pull_stack ();
/*
 * There is no need handling discarded_branch.
 * Either the branch is consistent and it is not discarded or it is not
 *  and it is discarded. All the information is thus in consistent.
 */
      for (i = 0; i < prod.size && consistent; i++)
        consistent =
            bad_simplify_and_store_in_S_quadruple (G, discarded_branch,
            &prod.tab[i].factor, K);

      ba0_push_another_stack ();
      rmov = rmov->next;
    }

  ba0_pull_stack ();

  if (theta)
    bav_set_tableof_term (theta, psi);

  ba0_restore (&M);

  return consistent;
}

/*
 * texinfo: bad_extend_quadruple_regchain
 * Extend the field @code{A} of @var{Q} with @var{C}
 * (see @code{bad_extend_regchain}). 
 * Insert the initials of @var{C} in the field @code{S} of @var{Q}.
 * Insert the separants also if the field @code{A} of @var{Q}
 * holds the squarefree property.
 */

BAD_DLL void
bad_extend_quadruple_regchain (
    struct bad_quadruple *Q,
    struct bad_regchain *C,
    struct bad_base_field *K)
{
  bool *discarded_branch = 0;
  struct bap_polynom_mpz init, sep;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_push_another_stack ();
  ba0_record (&M);
  bap_init_readonly_polynom_mpz (&init);
  bap_init_polynom_mpz (&sep);
  ba0_pull_stack ();

  bad_extend_regchain (&Q->A, C);
  for (i = 0; i < C->decision_system.size; i++)
    {
      ba0_push_another_stack ();
      bap_initial_polynom_mpz (&init, C->decision_system.tab[i]);
      ba0_pull_stack ();
/*
 * There is no need handling discarded branches since the function
 *  is not supposed to fail (otherwise an exception is raised)
 */
      if (!bad_member_polynom_base_field (&init, K))
        bad_simplify_and_store_in_S_quadruple (Q, discarded_branch, &init, K);

      if (bad_has_property_regchain (&Q->A, bad_squarefree_property)
          && bap_leading_degree_polynom_mpz (C->decision_system.tab[i]) > 1)
        {
          ba0_push_another_stack ();
          bap_separant_polynom_mpz (&sep, C->decision_system.tab[i]);
          ba0_pull_stack ();

          bad_simplify_and_store_in_S_quadruple (Q, discarded_branch, &sep, K);
        }
    }

  ba0_restore (&M);
}
