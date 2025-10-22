#include "bav_differential_ring.h"
#include "bav_term_ordering.h"
#include "bav_global.h"

static enum ba0_compare_code
compare_term_lex (
    struct bav_term *T,
    struct bav_term *U)
{
  enum ba0_compare_code code = ba0_eq;
  ba0_int_p i, m = BA0_MIN (T->size, U->size);
  bav_Inumber num_t, num_u;

  for (i = 0; code == ba0_eq && i < m; i++)
    {
      if (T->rg[i].var != U->rg[i].var)
        {
          num_t = bav_variable_number (T->rg[i].var);
          num_u = bav_variable_number (U->rg[i].var);
          if (num_t < num_u)
            code = ba0_lt;
          else
            code = ba0_gt;
        }
      else if (T->rg[i].deg < U->rg[i].deg)
        code = ba0_lt;
      else if (T->rg[i].deg > U->rg[i].deg)
        code = ba0_gt;
    }
  if (code == ba0_eq)
    {
      if (T->size < U->size)
        code = ba0_lt;
      else if (T->size > U->size)
        code = ba0_gt;
    }
  return code;
}

static enum ba0_compare_code
compare_term_grlex (
    struct bav_term *T,
    struct bav_term *U)
{
  bav_Idegree degT, degU;

  degT = bav_total_degree_term (T);
  degU = bav_total_degree_term (U);
  if (degT < degU)
    return ba0_lt;
  else if (degT > degU)
    return ba0_gt;
  else
    return compare_term_lex (T, U);
}

static enum ba0_compare_code
compare_term_degrevlex (
    struct bav_term *T,
    struct bav_term *U)
{
  bav_Idegree degT, degU;

  degT = bav_total_degree_term (T);
  degU = bav_total_degree_term (U);
  if (degT < degU)
    return ba0_lt;
  else if (degT > degU)
    return ba0_gt;
  else
    {
      enum ba0_compare_code code;
      bav_Inumber num_t, num_u;
      ba0_int_p i, j;

      for (code = ba0_eq, i = T->size - 1, j = U->size - 1;
          code == ba0_eq && i >= 0 && j >= 0; i--, j--)
        {
          if (T->rg[i].var != U->rg[j].var)
            {
              num_t = bav_variable_number (T->rg[i].var);
              num_u = bav_variable_number (U->rg[j].var);
              if (num_t < num_u)
                code = ba0_lt;
              else
                code = ba0_gt;
            }
          else if (T->rg[i].deg < U->rg[j].deg)
            code = ba0_gt;
          else if (T->rg[i].deg > U->rg[j].deg)
            code = ba0_lt;
        }
/*
   Should not happen since the total degrees are identical
*/
      if (code == ba0_eq && (i >= 0 || j >= 0))
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      return code;
    }
}


static enum ba0_compare_code
compare_stripped_term_lex (
    struct bav_term *T,
    struct bav_term *U,
    bav_Inumber last_numero)
{
  ba0_int_p i;
  bav_Inumber num_t, num_u;

  for (i = 0;; i++)
    {
      if (i >= T->size)
        {
          if (i < U->size)
            {
              num_u = bav_variable_number (U->rg[i].var);
              return num_u >= last_numero ? ba0_lt : ba0_eq;
            }
          else
            return ba0_eq;
        }
      else if (i >= U->size)
        {
          num_t = bav_variable_number (T->rg[i].var);
          return num_t >= last_numero ? ba0_gt : ba0_eq;
        }
      num_t = bav_variable_number (T->rg[i].var);
      num_u = bav_variable_number (U->rg[i].var);
      if (num_t < last_numero)
        return num_u >= last_numero ? ba0_lt : ba0_eq;
      else if (num_u < last_numero)
        return ba0_gt;
      else if (num_t < num_u)
        return ba0_lt;
      else if (num_t > num_u)
        return ba0_gt;
      else if (T->rg[i].deg < U->rg[i].deg)
        return ba0_lt;
      else if (T->rg[i].deg > U->rg[i].deg)
        return ba0_gt;
    }
}

static enum ba0_compare_code
compare_stripped_term_grlex (
    struct bav_term *T,
    struct bav_term *U,
    bav_Inumber last_numero)
{
  struct bav_term TT, UU;
  struct ba0_mark M;
  enum ba0_compare_code code;

  ba0_record (&M);
  bav_init_term (&TT);
  bav_strip_term (&TT, T, last_numero);
  bav_init_term (&UU);
  bav_strip_term (&UU, U, last_numero);

  code = compare_term_grlex (&TT, &UU);
  ba0_restore (&M);
  return code;
}

static enum ba0_compare_code
compare_stripped_term_degrevlex (
    struct bav_term *T,
    struct bav_term *U,
    bav_Inumber last_numero)
{
  struct bav_term TT, UU;
  struct ba0_mark M;
  enum ba0_compare_code code;

  ba0_record (&M);
  bav_init_term (&TT);
  bav_strip_term (&TT, T, last_numero);
  bav_init_term (&UU);
  bav_strip_term (&UU, U, last_numero);

  code = compare_term_degrevlex (&TT, &UU);
  ba0_restore (&M);
  return code;
}

#define compare_term		bav_global.term_ordering.compare
#define compare_stripped_term	bav_global.term_ordering.compare_stripped

/*
 * texinfo: bav_compare_term
 * Return @code{ba0_lt} if @math{T < U}, @code{ba0_eq} if @math{T = U}
 * and @code{ba0_gt} if @math{T > U} w.r.t. the current term ordering.
 */

BAV_DLL enum ba0_compare_code
bav_compare_term (
    struct bav_term *T,
    struct bav_term *U)
{
  return (*compare_term) (T, U);
}

/*
 * texinfo: bav_compare_stripped_term
 * Variant of the above function such that only variable whose number
 * (w.r.t. the current ordering on variables) is greater than
 * @var{last_number} are taken into account.
 */

BAV_DLL enum ba0_compare_code
bav_compare_stripped_term (
    struct bav_term *T,
    struct bav_term *U,
    bav_Inumber last_number)
{
  return (*compare_stripped_term) (T, U, last_number);
}

/*
 * texinfo: bav_set_term_ordering
 * Set the current term ordering to @var{ordering} which must
 * be one of the strings @code{"lex"}, @code{"grlex"} and @code{"degrevlex"}.
 */

BAV_DLL void
bav_set_term_ordering (
    char *ordering)
{
  if (ba0_strcasecmp (ordering, "lex") == 0)
    {
      compare_term = &compare_term_lex;
      compare_stripped_term = &compare_stripped_term_lex;
    }
  else if (ba0_strcasecmp (ordering, "grlex") == 0)
    {
      compare_term = &compare_term_grlex;
      compare_stripped_term = &compare_stripped_term_grlex;
    }
  else if (ba0_strcasecmp (ordering, "degrevlex") == 0)
    {
      compare_term = &compare_term_degrevlex;
      compare_stripped_term = &compare_stripped_term_degrevlex;
    }
  else
    BA0_RAISE_EXCEPTION (BAV_ERRBOR);
}
