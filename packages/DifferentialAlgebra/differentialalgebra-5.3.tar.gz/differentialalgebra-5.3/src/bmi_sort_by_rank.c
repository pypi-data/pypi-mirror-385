#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_sort_by_rank.h"

/*************************************************************
 * SORT
 *************************************************************/

static int
bmi_compar_ascending_rank (
    const void *AA,
    const void *BB)
{
  struct bap_polynom_mpq *A = *(struct bap_polynom_mpq * *) AA;
  struct bap_polynom_mpq *B = *(struct bap_polynom_mpq * *) BB;
  struct bav_term T, U;
  struct ba0_mark M;
  int res;

  if (bap_is_zero_polynom_mpq (A))
    {
      if (bap_is_zero_polynom_mpq (B))
        return 0;
      else
        return -1;
    }
  else if (bap_is_zero_polynom_mpq (B))
    return 1;
  ba0_record (&M);
  bav_init_term (&T);
  bav_init_term (&U);
  bap_leading_term_polynom_mpq (&T, A);
  bap_leading_term_polynom_mpq (&U, B);
  if (bav_gt_term (&T, &U))
    res = 1;
  else if (bav_equal_term (&T, &U))
    res = 0;
  else
    res = -1;
  ba0_restore (&M);
  return res;
}

static int
bmi_compar_descending_rank (
    const void *AA,
    const void *BB)
{
  struct bap_polynom_mpq *A = *(struct bap_polynom_mpq * *) AA;
  struct bap_polynom_mpq *B = *(struct bap_polynom_mpq * *) BB;
  struct bav_term T, U;
  struct ba0_mark M;
  int res;

  if (bap_is_zero_polynom_mpq (A))
    {
      if (bap_is_zero_polynom_mpq (B))
        return 0;
      else
        return 1;
    }
  else if (bap_is_zero_polynom_mpq (B))
    return -1;
  ba0_record (&M);
  bav_init_term (&T);
  bav_init_term (&U);
  bap_leading_term_polynom_mpq (&T, A);
  bap_leading_term_polynom_mpq (&U, B);
  if (bav_lt_term (&T, &U))
    res = 1;
  else if (bav_equal_term (&T, &U))
    res = 0;
  else
    res = -1;
  ba0_restore (&M);
  return res;
}

/*
 * EXPORTED
 *
 * Sort (list(polynomial), ascending | descending, differential ring)
 */

ALGEB
bmi_sort_by_rank (
    struct bmi_callback *callback)
{
  struct bap_tableof_polynom_mpq T;
  char *eqns, *ord;
  int (
      *f) (
      const void *,
      const void *);

  if (bmi_nops (callback) != 3)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (3, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

  bmi_set_ordering (3, callback, __FILE__, __LINE__);

  eqns = bmi_string_op (1, callback);
  ord = bmi_string_op (2, callback);

  ba0_init_table ((struct ba0_table *) &T);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (eqns, "%t[%simplify_expanded_Aq]", &T);
#else
  ba0_sscanf2 (eqns, "%t[%simplify_Aq]", &T);
#endif

  if (strcmp (ord, BMI_IX_ascending) == 0)
    f = &bmi_compar_ascending_rank;
  else if (strcmp (ord, BMI_IX_descending) == 0)
    f = &bmi_compar_descending_rank;
  else
    {
      f = 0;                    /* to avoid a warning */
      BA0_RAISE_EXCEPTION (BMI_ERRMODE);
    }

  qsort (T.tab, (size_t) T.size, sizeof (struct bap_polynom_mpq *), f);

  {
    char *stres;
    ALGEB res;
#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
    stres = ba0_new_printf ("%t[%Aq]", &T);
    bmi_push_maple_gmp_allocators ();
#if ! defined (BMI_BALSA)
    res = EvalMapleStatement (callback->kv, stres);
#else
    res = bmi_balsa_new_string (stres);
#endif
    bmi_pull_maple_gmp_allocators ();
    return res;
  }
}
