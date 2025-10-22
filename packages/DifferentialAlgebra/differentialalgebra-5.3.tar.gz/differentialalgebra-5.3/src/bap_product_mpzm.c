#include "bap_mul_polynom_mpzm.h"
#include "bap_parse_polynom_mpzm.h"
#include "bap_product_mpzm.h"

#define BAD_FLAG_mpzm

/*
 * texinfo: bap_init_power_mpzm
 * Initialize @var{P} to @math{1^1}.
 */

BAP_DLL void
bap_init_power_mpzm (
    struct bap_power_mpzm *P)
{
  bap_init_polynom_one_mpzm (&P->factor);
  P->exponent = 1;
}

/*
 * texinfo: bap_new_power_mpzm
 * Allocate a new power, initialize it and return it.
 */

BAP_DLL struct bap_power_mpzm *
bap_new_power_mpzm (
    void)
{
  struct bap_power_mpzm *P;

  P = (struct bap_power_mpzm *) ba0_alloc (sizeof (struct bap_power_mpzm));
  bap_init_power_mpzm (P);
  return P;
}

/*
 * texinfo: bap_set_power_mpzm
 * Assign @var{Q} to @var{P}.
 */

BAP_DLL void
bap_set_power_mpzm (
    struct bap_power_mpzm *P,
    struct bap_power_mpzm *Q)
{
  bap_set_polynom_mpzm (&P->factor, &Q->factor);
  P->exponent = Q->exponent;
}

/*
 * texinfo: bap_set_power_polynom_mpzm
 * Assign @math{A^k} to @var{P}.
 */

BAP_DLL void
bap_set_power_polynom_mpzm (
    struct bap_power_mpzm *P,
    struct bap_polynom_mpzm *A,
    bav_Idegree k)
{
  bap_set_polynom_mpzm (&P->factor, A);
  P->exponent = k;
}

/*
 * texinfo: bap_pow_power_mpzm
 * Assign @math{Q^k} to @var{P}.
 */

BAP_DLL void
bap_pow_power_mpzm (
    struct bap_power_mpzm *P,
    struct bap_power_mpzm *Q,
    bav_Idegree k)
{
  if (P != Q)
    bap_set_polynom_mpzm (&P->factor, &Q->factor);
  P->exponent = Q->exponent * k;
}

static void *
bap_scanf_power_mpzm (
    void *A)
{
  struct bap_power_mpzm *P = (struct bap_power_mpzm *) A;
  bool exponent;

  if (A == (void *) 0)
    P = bap_new_power_mpzm ();
  bap_scanf_atomic_polynom_mpzm (&P->factor);
  ba0_get_token_analex ();

  exponent = false;
  if (ba0_sign_token_analex ("^"))
    exponent = true;
  else if (ba0_sign_token_analex ("*"))
    {
      ba0_get_token_analex ();
      if (ba0_sign_token_analex ("*"))
        exponent = true;
      else
        ba0_unget_token_analex (1);
    }

  if (exponent)
    {
      ba0_get_token_analex ();
      if (ba0_type_token_analex () != ba0_integer_token)
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
      P->exponent = (bav_Idegree) atoi (ba0_value_token_analex ());
      if (P->exponent <= 0)
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
    }
  else
    {
      ba0_unget_token_analex (1);
      P->exponent = 1;
    }
  return P;
}

/*
 * PRODUCTS
 */

static bool bap_has_non_trivial_factors_product_mpzm (
    struct bap_product_mpzm *,
    ba0_int_p);

/*
 * texinfo: bap_init_product_mpzm
 * Initialize @var{prod} to one.
 */

BAP_DLL void
bap_init_product_mpzm (
    struct bap_product_mpzm *prod)
{
  ba0_mpzm_init_set_ui (prod->num_factor, 1);
  prod->alloc = 0;
  prod->size = 0;
  prod->tab = (struct bap_power_mpzm *) 0;
}

/* Initializes {\tt prod} to $0$.  */

/*
 * texinfo: bap_init_product_zero_mpzm
 * Initialize @var{prod} to zero.
 */

BAP_DLL void
bap_init_product_zero_mpzm (
    struct bap_product_mpzm *prod)
{
  ba0_mpzm_init_set_ui (prod->num_factor, 0);
  prod->alloc = 0;
  prod->size = 0;
  prod->tab = (struct bap_power_mpzm *) 0;
}

/*
 * texinfo: bap_realloc_product_mpzm
 * Reallocate @var{prod} if needed so that it can receive a product of at
 * least @var{n} powers. The already existing powers are kept.
 */

BAP_DLL void
bap_realloc_product_mpzm (
    struct bap_product_mpzm *prod,
    ba0_int_p n)
{
  struct bap_power_mpzm *newtab;
  ba0_int_p i;

  if (n > prod->alloc)
    {
      newtab =
          (struct bap_power_mpzm *) ba0_alloc (sizeof (struct bap_power_mpzm)
          * n);
      memcpy (newtab, prod->tab, prod->size * sizeof (struct bap_power_mpzm));
      for (i = prod->size; i < n; i++)
        bap_init_power_mpzm (&newtab[i]);
      prod->alloc = n;
      prod->tab = newtab;
    }
}

/*
 * texinfo: bap_new_product_mpzm
 * Allocate a new product, initialize it and return it.
 */

BAP_DLL struct bap_product_mpzm *
bap_new_product_mpzm (
    void)
{
  struct bap_product_mpzm *P;

  P = (struct bap_product_mpzm *) ba0_alloc (sizeof (struct
          bap_product_mpzm));
  bap_init_product_mpzm (P);
  return P;
}

/*
 * texinfo: bap_new_product_zero_mpzm
 * Return the product zero.
 */

BAP_DLL struct bap_product_mpzm *
bap_new_product_zero_mpzm (
    void)
{
  struct bap_product_mpzm *P;

  P = (struct bap_product_mpzm *) ba0_alloc (sizeof (struct
          bap_product_mpzm));
  bap_init_product_zero_mpzm (P);
  return P;
}

/*
 * texinfo: bap_set_product_one_mpzm
 * Assign @math{1} to @var{P}.
 */

BAP_DLL void
bap_set_product_one_mpzm (
    struct bap_product_mpzm *P)
{
  ba0_mpzm_set_si (P->num_factor, 1);
  P->size = 0;
}

/*
 * texinfo: bap_set_product_zero_mpzm
 * Assign @math{0} to @var{P}.
 */

BAP_DLL void
bap_set_product_zero_mpzm (
    struct bap_product_mpzm *P)
{
  ba0_mpzm_set_si (P->num_factor, 0);
  P->size = 0;
}

/*
 * texinfo: bap_set_product_numeric_mpzm
 * Assign @var{c} to @var{P}.
 */

BAP_DLL void
bap_set_product_numeric_mpzm (
    struct bap_product_mpzm *P,
    ba0_mpzm_t c)
{
  P->size = 0;
  ba0_mpzm_set (P->num_factor, c);
}

/*
 * texinfo: bap_set_product_polynom_mpzm
 * Assign @math{A^d} to @var{P}.
 */

BAP_DLL void
bap_set_product_polynom_mpzm (
    struct bap_product_mpzm *P,
    struct bap_polynom_mpzm *A,
    bav_Idegree d)
{
  if (bap_is_zero_polynom_mpzm (A))
    bap_set_product_zero_mpzm (P);
  else if (d == 0)
    bap_set_product_one_mpzm (P);
  else if (bap_is_numeric_polynom_mpzm (A))
    {
      struct ba0_mark M;
      ba0_mpzm_t c;

      ba0_push_another_stack ();
      ba0_record (&M);
      ba0_mpzm_init (c);
      ba0_mpzm_pow_ui (c, *bap_numeric_initial_polynom_mpzm (A), d);
      ba0_pull_stack ();
      bap_set_product_numeric_mpzm (P, c);
      ba0_restore (&M);
    }
  else
    {
      bap_set_product_one_mpzm (P);
      bap_realloc_product_mpzm (P, 1);
      bap_set_polynom_mpzm (&P->tab[0].factor, A);
      P->tab[0].exponent = d;
      P->size = 1;
    }
}

/* Returns true if $P$ is the empty product.  */

static bool bap_has_non_trivial_factors_product_mpzm (
    struct bap_product_mpzm *,
    ba0_int_p);

/*
 * texinfo: bap_is_one_product_mpzm
 * Return @code{true} if @var{P} is equal to @math{1}.
 */

BAP_DLL bool
bap_is_one_product_mpzm (
    struct bap_product_mpzm *P)
{
  return (!bap_has_non_trivial_factors_product_mpzm (P, 0))
      && ba0_mpzm_is_one (P->num_factor);
}

/*
 * texinfo: bap_is_zero_product_mpzm
 * Return @code{true} if @var{P} is equel to @math{0}.
 */

BAP_DLL bool
bap_is_zero_product_mpzm (
    struct bap_product_mpzm *P)
{
  return ba0_mpzm_is_zero (P->num_factor);
}

/*
 * texinfo: bap_is_numeric_product_mpzm
 * Return @code{true} if @var{P} is a numerical coefficient
 * (the function actually only tests if all exponents are equal to @math{0}).
 */

BAP_DLL bool
bap_is_numeric_product_mpzm (
    struct bap_product_mpzm *P)
{
  return bap_is_zero_product_mpzm (P) ||
      !bap_has_non_trivial_factors_product_mpzm (P, 0);
}

/*
 * texinfo: bap_leader_product_mpzm
 * Return the maximum of the leaders of the factors of @var{P}.
 * Exception @code{BAP_ERRCST} is raised if @var{P} is numeric.
 */

BAP_DLL struct bav_variable *
bap_leader_product_mpzm (
    struct bap_product_mpzm *P)
{
  struct bav_variable *v, *w;
  ba0_int_p nv, nw, i;

  if (bap_is_numeric_product_mpzm (P))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  i = 0;
  while (i < P->size && P->tab[i].exponent == 0)
    i += 1;
  v = bap_leader_polynom_mpzm (&P->tab[i].factor);
  nv = bav_variable_number (v);
  i += 1;
  while (i < P->size)
    {
      if (P->tab[i].exponent > 0)
        {
          w = bap_leader_polynom_mpzm (&P->tab[i].factor);
          nw = bav_variable_number (w);
          if (nw > nv)
            {
              v = w;
              nv = nw;
            }
        }
      i += 1;
    }
  return v;
}
        
/*
 * texinfo: bap_set_product_mpzm
 * Assign @var{Q} to @var{P}.
 * Do not copy the powers whose exponents are zero.
 */

BAP_DLL void
bap_set_product_mpzm (
    struct bap_product_mpzm *P,
    struct bap_product_mpzm *Q)
{
  ba0_int_p p, q;

  if (P != Q)
    {
      P->size = 0;
      bap_realloc_product_mpzm (P, Q->size);
      ba0_mpzm_set (P->num_factor, Q->num_factor);
      p = 0;
      for (q = 0; q < Q->size; q++)
        {
          if (Q->tab[q].exponent > 0)
            {
              bap_set_polynom_mpzm (&P->tab[p].factor, &Q->tab[q].factor);
              P->tab[p].exponent = Q->tab[q].exponent;
              p++;
            }
        }
      P->size = p;
    }
}

/*
 * texinfo: bap_exponent_product_mpzm
 * If @var{A} is one of the factors of @var{prod}, return its exponent.
 * Return @math{0} otherwise.
 */

BAP_DLL bav_Idegree
bap_exponent_product_mpzm (
    struct bap_product_mpzm *prod,
    struct bap_polynom_mpzm *A)
{
  ba0_int_p i;

  for (i = 0; i < prod->size; i++)
    if (bap_equal_polynom_mpzm (&prod->tab[i].factor, A))
      return prod->tab[i].exponent;
  return 0;
}

/*
 * texinfo: bap_sort_product_mpzm
 * Apply @code{bap_sort_polynom_mpzm} over all the factors of @var{Q}.
 * The result is stored in @var{P} in readonly mode.
 */

BAP_DLL void
bap_sort_product_mpzm (
    struct bap_product_mpzm *P,
    struct bap_product_mpzm *Q)
{
  ba0_int_p i;

  if (P == Q)
    for (i = 0; i < Q->size; i++)
      bap_sort_polynom_mpzm (&P->tab[i].factor, &Q->tab[i].factor);
  else
    {
      bap_set_product_numeric_mpzm (P, Q->num_factor);
      bap_realloc_product_mpzm (P, Q->size);
      for (i = 0; i < Q->size; i++)
        {
          bap_sort_polynom_mpzm (&P->tab[i].factor, &Q->tab[i].factor);
          P->tab[i].exponent = Q->tab[i].exponent;
        }
      P->size = Q->size;
    }
}

/*
 * texinfo: bap_physort_product_mpzm
 * Apply @code{bap_physort_polynom_mpzm} over all the factors of @var{P}.
 */

BAP_DLL void
bap_physort_product_mpzm (
    struct bap_product_mpzm *P)
{
  ba0_int_p i;

  for (i = 0; i < P->size; i++)
    bap_physort_polynom_mpzm (&P->tab[i].factor);
}

/*
 * texinfo: bap_expand_product_mpzm
 * Assign to @var{R} the expansion of @var{prod}.
 */

BAP_DLL void
bap_expand_product_mpzm (
    struct bap_polynom_mpzm *R,
    struct bap_product_mpzm *prod)
{
  struct bap_polynom_mpzm *P, *Q;
  struct bav_rank rg;
  ba0_int_p i, j;
  struct ba0_mark M;

  i = 0;
  while (i < prod->size && prod->tab[i].exponent == 0)
    i++;
  j = i + 1;
  while (j < prod->size && prod->tab[j].exponent == 0)
    j++;

  if (i == prod->size)
    {
      rg = bav_constant_rank ();
      bap_set_polynom_crk_mpzm (R, prod->num_factor, &rg);
    }
  else if (j == prod->size)
    {
      if (prod->tab[i].exponent > 1)
        {
          if (ba0_mpzm_is_one (prod->num_factor))
            bap_pow_polynom_mpzm (R, &prod->tab[i].factor,
                prod->tab[i].exponent);
          else
            {
              ba0_push_another_stack ();
              ba0_record (&M);
              P = bap_new_polynom_mpzm ();
              bap_pow_polynom_mpzm (P, &prod->tab[i].factor,
                  prod->tab[i].exponent);
              ba0_pull_stack ();
              bap_mul_polynom_numeric_mpzm (R, P, prod->num_factor);
              ba0_restore (&M);
            }
        }
      else if (ba0_mpzm_is_one (prod->num_factor))
        bap_set_polynom_mpzm (R, &prod->tab[i].factor);
      else
        bap_mul_polynom_numeric_mpzm (R, &prod->tab[i].factor,
            prod->num_factor);
    }
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);

      P = bap_new_polynom_mpzm ();
      Q = bap_new_polynom_mpzm ();
      bap_pow_polynom_mpzm (P, &prod->tab[i].factor, prod->tab[i].exponent);
      do
        {
          if (prod->tab[j].exponent > 1)
            {
              bap_pow_polynom_mpzm (Q, &prod->tab[j].factor,
                  prod->tab[j].exponent);
              bap_mul_polynom_mpzm (P, P, Q);
            }
          else
            bap_mul_polynom_mpzm (P, P, &prod->tab[j].factor);
          do
            j++;
          while (j < prod->size && prod->tab[j].exponent == 0);
        }
      while (j < prod->size);
      if (!ba0_mpzm_is_one (prod->num_factor))
        bap_mul_polynom_numeric_mpzm (P, P, prod->num_factor);
      ba0_pull_stack ();
      bap_set_polynom_mpzm (R, P);
      ba0_restore (&M);
    }
}

/*
 * texinfo: bap_mul_product_polynom_mpzm
 * Assign to @var{res} the product @math{@emph{prod}\,A^k}.
 */

BAP_DLL void
bap_mul_product_polynom_mpzm (
    struct bap_product_mpzm *res,
    struct bap_product_mpzm *prod,
    struct bap_polynom_mpzm *A,
    bav_Idegree k)
{
  ba0_int_p i;

  if (bap_is_zero_polynom_mpzm (A))
    bap_set_product_zero_mpzm (res);
  else
    {
      if (res != prod)
        {
          res->size = 0;
          bap_realloc_product_mpzm (res, prod->size + 1);
          bap_set_product_mpzm (res, prod);
        }

      if (bap_is_numeric_polynom_mpzm (A))
        {
          ba0_mpzm_t p;
          struct ba0_mark M;

          ba0_push_another_stack ();
          ba0_record (&M);
          ba0_mpzm_init (p);
          ba0_mpzm_pow_ui (p, *bap_numeric_initial_polynom_mpzm (A), k);
          ba0_pull_stack ();
          ba0_mpzm_mul (res->num_factor, res->num_factor, p);
          ba0_restore (&M);
        }
      else if (k > 0)
        {
          i = 0;
          while (i < res->size
              && !bap_equal_polynom_mpzm (&res->tab[i].factor, A))
            i++;
          if (i < res->size)
            res->tab[i].exponent += k;
          else
            {
              bap_realloc_product_mpzm (res, res->size + 1);
              bap_set_polynom_mpzm (&res->tab[i].factor, A);
              res->tab[i].exponent = k;
              res->size += 1;
            }
        }
    }
}

/*
 * texinfo: bap_neg_product_mpzm
 * Assign to @var{R} the product @math{- A}.
 */

BAP_DLL void
bap_neg_product_mpzm (
    struct bap_product_mpzm *R,
    struct bap_product_mpzm *A)
{
  if (R == A)
    ba0_mpzm_neg (R->num_factor, R->num_factor);
  else
    {
      bap_set_product_mpzm (R, A);
      ba0_mpzm_neg (R->num_factor, R->num_factor);
    }
}

/*
 * texinfo: bap_mul_product_numeric_mpzm
 * Assign to @var{R} the product @math{A\,c}.
 */

BAP_DLL void
bap_mul_product_numeric_mpzm (
    struct bap_product_mpzm *R,
    struct bap_product_mpzm *A,
    ba0_mpzm_t c)
{
  if (ba0_mpzm_is_zero (c) || bap_is_zero_product_mpzm (A))
    bap_set_product_zero_mpzm (R);
  if (R != A)
    bap_set_product_mpzm (R, A);
  ba0_mpzm_mul (R->num_factor, R->num_factor, c);
  if (ba0_mpzm_is_zero (R->num_factor))
    bap_set_product_zero_mpzm (R);
}

/*
 * texinfo: bap_mul_product_term_mpzm
 * Assign to @var{R} the product @math{@emph{prod}\,T}.
 */

BAP_DLL void
bap_mul_product_term_mpzm (
    struct bap_product_mpzm *res,
    struct bap_product_mpzm *prod,
    struct bav_term *T)
{
  ba0_int_p i, j, nb_alloc, *tab;
  bool found;
  struct ba0_mark M;

  if (bav_is_one_term (T))
    {
      bap_set_product_mpzm (res, prod);
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M);
  tab = (ba0_int_p *) ba0_alloc (sizeof (ba0_int_p) * T->size);
  ba0_pull_stack ();

  nb_alloc = 0;
  for (i = 0; i < T->size; i++)
    {
      found = false;
      for (j = 0; !found && j < prod->size; j++)
        {
          struct bav_rank rg;

          rg = bap_rank_polynom_mpzm (&prod->tab[j].factor);
          if (bap_nbmon_polynom_mpzm (&prod->tab[j].factor) == 1
              && rg.var == T->rg[i].var && rg.deg == 1)
            {
              tab[i] = j;
              found = true;
            }
        }
      if (!found)
        {
          tab[i] = -1;
          nb_alloc++;
        }
    }

  if (res != prod)
    {
      res->size = 0;
      bap_realloc_product_mpzm (res, prod->size + nb_alloc);
      bap_set_product_mpzm (res, prod);
    }
  else
    bap_realloc_product_mpzm (res, res->size + nb_alloc);

  for (i = 0; i < T->size; i++)
    {
      if (tab[i] >= 0)
        res->tab[tab[i]].exponent += T->rg[i].deg;
      else
        {
          bap_set_polynom_variable_mpzm (&res->tab[res->size].factor,
              T->rg[i].var, 1);
          res->tab[res->size].exponent = T->rg[i].deg;
          res->size++;
        }
    }
  ba0_restore (&M);
}

/*
 * texinfo: bap_mul_product_mpzm
 * Assign to @var{R} the product @math{P\,Q}.
 */

BAP_DLL void
bap_mul_product_mpzm (
    struct bap_product_mpzm *R,
    struct bap_product_mpzm *P,
    struct bap_product_mpzm *Q)
{
  ba0_int_p i;

  if (bap_is_zero_product_mpzm (P) || bap_is_zero_product_mpzm (Q))
    {
      bap_set_product_zero_mpzm (R);
      return;
    }

  bap_realloc_product_mpzm (R, P->size + Q->size);

  if (R == Q)
    {
      BA0_SWAP (struct bap_product_mpzm *,
          P,
          Q);
    }

  if (R != P)
    bap_set_product_mpzm (R, P);

  ba0_mpzm_mul (R->num_factor, R->num_factor, Q->num_factor);
  for (i = 0; i < Q->size; i++)
    bap_mul_product_polynom_mpzm (R, R, &Q->tab[i].factor, Q->tab[i].exponent);
}

/*
 * texinfo: bap_pow_product_mpzm
 * Assign to @var{P} the product @math{Q^k}.
 */

BAP_DLL void
bap_pow_product_mpzm (
    struct bap_product_mpzm *P,
    struct bap_product_mpzm *Q,
    bav_Idegree k)
{
  ba0_int_p j;

  if (bap_is_zero_product_mpzm (Q))
    bap_set_product_zero_mpzm (P);
  else if (k == 0)
    bap_set_product_one_mpzm (P);
  else
    {
      bap_set_product_mpzm (P, Q);
      ba0_mpzm_pow_ui (P->num_factor, P->num_factor, k);
      for (j = 0; j < P->size; j++)
        P->tab[j].exponent *= k;
    }
}

#if defined (ba0_mpzm_div)

/*
 * texinfo: bap_exquo_product_polynom_mpzm
 * Assign to @var{res} the product @math{@emph{prod}/A^k}.
 * The polynomial @var{A} must be one of the factors of the product and
 * the division must be exact.
 * May raise exception @code{BAV_EXEXQO}.
 */

BAP_DLL void
bap_exquo_product_polynom_mpzm (
    struct bap_product_mpzm *res,
    struct bap_product_mpzm *prod,
    struct bap_polynom_mpzm *A,
    bav_Idegree k)
{
  ba0_mpzm_t p;
  ba0_int_p i;
  struct ba0_mark M;

  if (bap_is_zero_polynom_mpzm (A))
    BA0_RAISE_EXCEPTION (BAP_ERRNUL);

  if (res != prod)
    bap_set_product_mpzm (res, prod);

  if (bap_is_numeric_polynom_mpzm (A))
    {
      ba0_push_another_stack ();
      ba0_record (&M);
      ba0_mpzm_init (p);
      ba0_mpzm_pow_ui (p, *bap_numeric_initial_polynom_mpzm (A), k);
      ba0_pull_stack ();

      ba0_mpzm_div (res->num_factor, res->num_factor, p);

      ba0_restore (&M);
    }
  else if (k > 0)
    {
      i = 0;
      while (i < res->size && !bap_equal_polynom_mpzm (A, &res->tab[i].factor))
        i++;

      if (i == res->size || res->tab[i].exponent < k)
        BA0_RAISE_EXCEPTION (BAV_EXEXQO);

      if (res->tab[i].exponent > k)
        res->tab[i].exponent -= k;
      else if (i == res->size - 1)
        res->size -= 1;
      else
        {
          BA0_SWAP (struct bap_power_mpzm,
              res->tab[i],
              res->tab[res->size - 1]);
          res->size -= 1;
        }
    }
}
#endif

/*
 * Readonly static data
 */

static char _struct_product[] = "struct bap_product_mpzm";
#if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm)
static char _struct_product_num[] =
    "struct bap_product_mpzm *->num_factor._mp_d";
#else
#   if defined (BAD_FLAG_mpq)
static char _struct_product_num_num[] =
    "struct bap_product_mpzm *->num_factor._mp_num._mp_d";
static char _struct_product_num_den[] =
    "struct bap_product_mpzm *->num_factor._mp_den._mp_d";
#   endif
#endif
static char _struct_product_tab[] = "struct bap_product_mpzm *->tab";

BAP_DLL ba0_int_p
bap_garbage1_product_mpzm (
    void *AA,
    enum ba0_garbage_code code)
{
  struct bap_product_mpzm *A = (struct bap_product_mpzm *) AA;
  ba0_int_p i, n = 0;
  ba0__mpz_struct *p;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (A, sizeof (struct bap_product_mpzm),
        _struct_product);

#if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm)
  p = A->num_factor;
  n += ba0_new_gc_info (p->_mp_d, p->_mp_alloc * sizeof (ba0_mp_limb_t),
      _struct_product_num);
#else
#   if defined (BAD_FLAG_mpq)
  p = &A->num_factor[0]._mp_num;
  n += ba0_new_gc_info (p->_mp_d, p->_mp_alloc * sizeof (ba0_mp_limb_t),
      _struct_product_num_num);
  p = &A->num_factor[0]._mp_den;
  n += ba0_new_gc_info (p->_mp_d, p->_mp_alloc * sizeof (ba0_mp_limb_t),
      _struct_product_num_den);
#   else
  p = (ba0__mpz_struct *) 0;
#   endif
#endif

  n += ba0_new_gc_info (A->tab, A->alloc * sizeof (struct bap_power_mpzm),
      _struct_product_tab);
  for (i = 0; i < A->alloc; i++)
    n += bap_garbage1_polynom_mpzm (&A->tab[i].factor, ba0_embedded);

  return n;
}

BAP_DLL void *
bap_garbage2_product_mpzm (
    void *AA,
    enum ba0_garbage_code code)
{
  struct bap_product_mpzm *A;
  ba0_int_p i;
  ba0__mpz_struct *p;

  if (code == ba0_isolated)
    A = (struct bap_product_mpzm *) ba0_new_addr_gc_info (AA, _struct_product);
  else
    A = (struct bap_product_mpzm *) AA;

#if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm)
  p = A->num_factor;
  p->_mp_d =
      (ba0_mp_limb_t *) ba0_new_addr_gc_info (p->_mp_d, _struct_product_num);
#elif defined (BAD_FLAG_mpq)
  p = &A->num_factor[0]._mp_num;
  p->_mp_d =
      (ba0_mp_limb_t *) ba0_new_addr_gc_info (p->_mp_d,
      _struct_product_num_num);
  p = &A->num_factor[0]._mp_den;
  p->_mp_d =
      (ba0_mp_limb_t *) ba0_new_addr_gc_info (p->_mp_d,
      _struct_product_num_den);
#else
  p = (ba0__mpz_struct *) 0;
#endif

  A->tab =
      (struct bap_power_mpzm *) ba0_new_addr_gc_info (A->tab,
      _struct_product_tab);
  for (i = 0; i < A->alloc; i++)
    bap_garbage2_polynom_mpzm (&A->tab[i].factor, ba0_embedded);

  return A;
}

BAP_DLL void *
bap_copy_product_mpzm (
    void *A)
{
  struct bap_product_mpzm *B;

  B = bap_new_product_mpzm ();
  bap_set_product_mpzm (B, (struct bap_product_mpzm *) A);
  return B;
}

/*
 * texinfo: bap_scanf_product_mpzm
 * The general parsing function for products.
 * It is called by @code{ba0_scanf/%Pzm}.
 */

BAP_DLL void *
bap_scanf_product_mpzm (
    void *A)
{
  struct bap_product_mpzm *prod = (struct bap_product_mpzm *) A;
  struct bap_power_mpzm *P;
  struct ba0_list *L;
  ba0_int_p i;
  bool negatif = false;
  bool nul = false;
  struct ba0_mark M;

  if (prod == (struct bap_product_mpzm *) 0)
    prod = bap_new_product_mpzm ();
  else
    bap_set_product_one_mpzm (prod);

  ba0_push_another_stack ();
  ba0_record (&M);

  if (ba0_sign_token_analex ("-"))
    {
      negatif = true;
      ba0_get_token_analex ();
    }

  L = (struct ba0_list *) 0;
  P = bap_scanf_power_mpzm ((void *) 0);
  if (bap_is_zero_polynom_mpzm (&P->factor))
    nul = true;
  L = ba0_cons_list (P, L);
  ba0_get_token_analex ();
  while (ba0_sign_token_analex ("*"))
    {
      ba0_get_token_analex ();
      P = bap_scanf_power_mpzm ((void *) 0);
      if (bap_is_zero_polynom_mpzm (&P->factor))
        nul = true;
      L = ba0_cons_list (P, L);
      ba0_get_token_analex ();
    }
#if defined (BAD_FLAG_mpq)
  if (ba0_sign_token_analex ("/"))
    {
      ba0_mpq_t denom;

      ba0_get_token_analex ();
      ba0_mpq_init (denom);
      ba0_mpz_init_set_si (ba0_mpq_numref (denom), 1);
      ba0_scanf_mpz (ba0_mpq_denref (denom));
      if (ba0_mpz_sgn (ba0_mpq_denref (denom)) == 0)
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRIVZ);
      ba0_get_token_analex ();
      ba0_pull_stack ();
      ba0_mpq_mul (prod->num_factor, prod->num_factor, denom);
      ba0_push_another_stack ();
    }
#endif
  ba0_unget_token_analex (1);
  L = ba0_reverse_list (L);
  ba0_pull_stack ();

/*
   Affecte L a prod.
*/
  if (nul)
    bap_set_product_zero_mpzm (prod);
  else
    {
      bap_realloc_product_mpzm (prod, ba0_length_list (L));
      i = 0;
      while (L != (struct ba0_list *) 0)
        {
          P = (struct bap_power_mpzm *) L->value;
          if (bap_is_numeric_polynom_mpzm (&P->factor))
            {
              ba0_mpzm_t *lc = bap_numeric_initial_polynom_mpzm (&P->factor);
              bav_Idegree e;
              for (e = 0; e < P->exponent; e++)
                ba0_mpzm_mul (prod->num_factor, prod->num_factor, *lc);
            }
          else
            bap_set_power_mpzm (&prod->tab[i++], P);
          L = L->next;
        }
      prod->size = i;
      if (negatif)
        ba0_mpzm_neg (prod->num_factor, prod->num_factor);
    }

  ba0_restore (&M);
  return prod;
}

/*
 * texinfo: bap_printf_product_mpzm
 * The general printing function for products.
 * It is called by @code{ba0_printf/%Pzm}.
 */

BAP_DLL void
bap_printf_product_mpzm (
    void *A)
{
  struct bap_product_mpzm *P = (struct bap_product_mpzm *) A;
  ba0_mpzm_t bunk, *lc;
  ba0_int_p i;
  struct ba0_mark M;
  ba0_printf_function *print_rank;

  if (bap_is_zero_product_mpzm (P))
    {
      ba0_put_char ('0');
      return;
    }

  bav_get_settings_rank (&print_rank);

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpzm_init (bunk);

  if (ba0_mpzm_is_negative (P->num_factor))
    {
      ba0_put_string ("- ");
      ba0_mpzm_neg (bunk, P->num_factor);
    }
  else
    ba0_mpzm_set (bunk, P->num_factor);

  if (!ba0_mpzm_is_one (bunk))
    {
#if defined (BAD_FLAG_mint_hp)
      ba0_printf ("%zm", &bunk);
#else
      ba0_printf ("%zm", bunk);
#endif
      if (bap_has_non_trivial_factors_product_mpzm (P, 0))
        {
          if (ba0_global.common.LaTeX)
            ba0_put_string ("\\,");
          else
            ba0_put_char ('*');
        }
    }
  else if (!bap_has_non_trivial_factors_product_mpzm (P, 0))
    {
#if defined (BAD_FLAG_mint_hp)
      ba0_printf ("%zm", &bunk);
#else
      ba0_printf ("%zm", bunk);
#endif
    }

  for (i = 0; i < P->size; i++)
    {
      if (P->tab[i].exponent == 0)
        continue;
      lc = bap_numeric_initial_polynom_mpzm (&P->tab[i].factor);
      if (bap_nbmon_polynom_mpzm (&P->tab[i].factor) > 1
          || !ba0_mpzm_is_one (*lc))
        {
          ba0_put_char ('(');
          bap_printf_polynom_mpzm (&P->tab[i].factor);
          ba0_put_char (')');
        }
      else
        bap_printf_polynom_mpzm (&P->tab[i].factor);
/*
 * Reproduce the behaviour of ranks in terms of '**' and '^'
 */
      if (P->tab[i].exponent > 1)
        {
          if (print_rank == &bav_printf_stars_rank)
            ba0_put_string ("**");
          else
            ba0_put_char ('^');
          ba0_put_int_p (P->tab[i].exponent);
        }
      if (bap_has_non_trivial_factors_product_mpzm (P, i + 1))
        {
          if (ba0_global.common.LaTeX)
            ba0_put_string ("\\,");
          else
            ba0_put_char ('*');
        }
    }

  ba0_pull_stack ();
  ba0_restore (&M);
}

/*
   Return true if P has at least one non trivial factor in the
	range P->tab [i .. P->size - 1].

   P is assumed to be nonzero
 */

static bool
bap_has_non_trivial_factors_product_mpzm (
    struct bap_product_mpzm *P,
    ba0_int_p i)
{
  ba0_int_p j;
  bool found;

  found = false;
  for (j = i; j < P->size && !found; j++)
    found = P->tab[i].exponent > 0;
  return found;
}

#undef BAD_FLAG_mpzm
