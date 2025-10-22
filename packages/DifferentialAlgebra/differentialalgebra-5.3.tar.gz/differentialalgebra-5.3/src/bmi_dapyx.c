#include <assert.h>
#include "bmi_dapyx.h"
#include "bmi_indices.h"
#include "bmi_blad_eval.h"

#define DOPRINT
#undef DOPRINT

#define isnull(eqns) (eqns[0] == '\0')

static struct bmi_balsa_object zero =
    { bmi_balsa_string_object, "0", false, 0 };
static struct bmi_balsa_object small =
    { bmi_balsa_string_object, BMI_IX_small, false, 0 };
static struct bmi_balsa_object large =
    { bmi_balsa_string_object, BMI_IX_large, false, 0 };
static struct bmi_balsa_object vrai =
    { bmi_balsa_string_object, "true", false, 0 };
static struct bmi_balsa_object faux =
    { bmi_balsa_string_object, "false", false, 0 };
static struct bmi_balsa_object bool_vrai =
    { bmi_balsa_bool_object, (void *) true, false, 0 };
static struct bmi_balsa_object bool_faux =
    { bmi_balsa_bool_object, (void *) false, false, 0 };

bool
bmi_dapyx_is_error (
    void *A0)
{
  ALGEB A = (ALGEB) A0;
  return A->type == bmi_balsa_error_object;
}

char *
bmi_dapyx_mesgerr (
    void *A0)
{
  ALGEB A = (ALGEB) A0;
  assert (A->type == bmi_balsa_error_object);
  return (char *) A->value;
}

static ALGEB
fix_notation (
    char *notation,
    ALGEB table)
{
  if (strcmp (notation, BMI_IX_undefined) != 0)
    return bmi_balsa_new_string (notation);
  else
    return ((struct bmi_balsa_table *) table->value)->notation;
}

/*
 * F is freed since it is embedded in L
 */

static ALGEB
eval (
    ALGEB F,
    ALGEB notin,
    ALGEB notout,
    ba0_int_p timeout,
    ba0_int_p memout,
    ALGEB cellsize)
{
  ALGEB L, R, *arglist;
  char buffer[32];

  L = MapleListAlloc (0, 6);
  MapleListAssign (0, L, 1, F);
  MapleListAssign (0, L, 2, notin);
  MapleListAssign (0, L, 3, notout);
  if (timeout == 0)
    MapleListAssign (0, L, 4, &zero);
  else
    {
      sprintf (buffer, "%ld", timeout);
      MapleListAssign (0, L, 4, bmi_balsa_new_string (buffer));
    }
  if (memout == 0)
    MapleListAssign (0, L, 5, &zero);
  else
    {
      sprintf (buffer, "%ld", memout);
      MapleListAssign (0, L, 5, bmi_balsa_new_string (buffer));
    }
  MapleListAssign (0, L, 6, cellsize);

  arglist = ((struct bmi_balsa_list *) L->value)->tab;
#if defined (DO_PRINT)
  printf ("before eval\n");
#endif
  R = bmi_blad_eval_python (0, (ALGEB) arglist);
#if defined (DO_PRINT)
  printf ("after eval\n");
#endif
  bmi_balsa_clear_ALGEB (L);
  if (R == NULL)
    R = bmi_balsa_new_error ();
  return R;
}

ALGEB
bmi_dapyx_differential_ring (
    char *derivations,
    char *blocks,
    char *parameters,
    char *notation)
{
  ALGEB A, F;
  static struct bmi_balsa_object DifferentialRing =
      { bmi_balsa_string_object, "DifferentialRing", false, 0 };

  F = bmi_balsa_new_function (&DifferentialRing, 3);
  A = bmi_balsa_new_string (derivations);
  MapleListAssign (0, F, 1, A);
  A = bmi_balsa_new_string (blocks);
  MapleListAssign (0, F, 2, A);
  A = bmi_balsa_new_string (parameters);
  MapleListAssign (0, F, 3, A);

  if (strcmp (notation, "undefined") == 0)
    A = bmi_balsa_default_sympy_notation ();
  else
    A = bmi_balsa_new_string (notation);

  return eval (F, A, A, 0, 0, &small);
}

ALGEB_string
bmi_dapyx_ranking (
    ALGEB DRing)
{
  ALGEB F;
  static struct bmi_balsa_object Ranking =
      { bmi_balsa_string_object, "Ranking", false, 0 };

  F = bmi_balsa_new_function (&Ranking, 1);
  MapleListAssign (0, F, 1, DRing);
  return (ALGEB_string) eval
      (F,
      bmi_balsa_default_sympy_notation (),
      bmi_balsa_default_sympy_notation (), 0, 0, &small);
}

ALGEB_string
bmi_dapyx_attributes (
    ALGEB DRing)
{
  ALGEB F;
  static struct bmi_balsa_object Attributes =
      { bmi_balsa_string_object, "Attributes", false, 0 };

  F = bmi_balsa_new_function (&Attributes, 1);
  MapleListAssign (0, F, 1, DRing);
  return (ALGEB_string) eval
      (F,
      bmi_balsa_default_sympy_notation (),
      bmi_balsa_default_sympy_notation (), 0, 0, &small);
}

ALGEB_string
bmi_dapyx_base_field_generators (
    char *generators,
    char *relations,
    ALGEB DRing,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object BaseFieldGenerators =
      { bmi_balsa_string_object, "BaseFieldGenerators", false, 0 };

  F = bmi_balsa_new_function (&BaseFieldGenerators, 3);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (generators));
  MapleListAssign (0, F, 2, bmi_balsa_new_string (relations));
  MapleListAssign (0, F, 3, DRing);
  return (ALGEB_string) eval
      (F,
      fix_notation (notin, DRing),
      fix_notation (notout, DRing), timeout, memout, &small);
}

ALGEB_string
bmi_dapyx_indets (
    char *eqns,
    ALGEB DRing,
    char *selection,
    char *fullset_or_var,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object Indets =
      { bmi_balsa_string_object, "Indets", false, 0 };

  F = bmi_balsa_new_function (&Indets, 4);
  MapleListAssign (0, F, 1,
      isnull (eqns) ? DRing : bmi_balsa_new_string (eqns));
  MapleListAssign (0, F, 2, bmi_balsa_new_string (selection));
  MapleListAssign (0, F, 3, bmi_balsa_new_string (fullset_or_var));
  MapleListAssign (0, F, 4, DRing);
  return (ALGEB_string) eval
      (F,
      fix_notation (notin, DRing),
      fix_notation (notout, DRing), timeout, memout, &small);
}

ALGEB_string
bmi_dapyx_differential_prem (
    char *eqn,
    char *mode,
    ALGEB regchain,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object DifferentialPrem =
      { bmi_balsa_string_object, "DifferentialPrem", false, 0 };

  F = bmi_balsa_new_function (&DifferentialPrem, 3);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (eqn));
  MapleListAssign (0, F, 2, bmi_balsa_new_string (mode));
  MapleListAssign (0, F, 3, regchain);
  return (ALGEB_string) eval
      (F,
      fix_notation (notin, regchain),
      fix_notation (notout, regchain), timeout, memout, &large);
}

ALGEB_string
bmi_dapyx_differential_prem2 (
    char *eqn,
    char *redset,
    char *mode,
    ALGEB DRing,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object DifferentialPrem =
      { bmi_balsa_string_object, "DifferentialPrem", false, 0 };

  F = bmi_balsa_new_function (&DifferentialPrem, 4);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (eqn));
  MapleListAssign (0, F, 2, bmi_balsa_new_string (mode));
  MapleListAssign (0, F, 3, bmi_balsa_new_string (redset));
  MapleListAssign (0, F, 4, DRing);
  return (ALGEB_string) eval
      (F,
      fix_notation (notin, DRing),
      fix_notation (notout, DRing), timeout, memout, &large);
}

ALGEB
bmi_dapyx_pretend_regular_differential_chain (
    char *equations,
    ALGEB DRing,
    char *attributes,
    bool pretend,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object PretendRegularDifferentialChain =
      { bmi_balsa_string_object, "PretendRegularDifferentialChain",
    false, 0
  };

  F = bmi_balsa_new_function (&PretendRegularDifferentialChain, 4);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (equations));
  MapleListAssign (0, F, 2, bmi_balsa_new_string (attributes));
  MapleListAssign (0, F, 3, pretend ? &vrai : &faux);
  MapleListAssign (0, F, 4, DRing);
  return eval
      (F,
      fix_notation (notin, DRing),
      fix_notation (notout, DRing), timeout, memout, &large);
}

ALGEB_listof_string
bmi_dapyx_process_equations (
    char *equations,
    ALGEB DRing,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object ProcessEquations =
      { bmi_balsa_string_object, "ProcessEquations", false, 0 };
  F = bmi_balsa_new_function (&ProcessEquations, 2);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (equations));
  MapleListAssign (0, F, 2, DRing);
  return (ALGEB_listof_string) eval
      (F,
      fix_notation (notin, DRing),
      fix_notation (notout, DRing), timeout, memout, &small);
}

ALGEB_string
bmi_dapyx_factor_derivative (
    char *derv,
    ALGEB DRing,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object FactorDerivative =
      { bmi_balsa_string_object, "FactorDerivative", false, 0 };

  F = bmi_balsa_new_function (&FactorDerivative, 2);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (derv));
  MapleListAssign (0, F, 2, DRing);

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, DRing),
      fix_notation (notout, DRing), timeout, memout, &small);
}

ALGEB_string
bmi_dapyx_is_constant (
    char *eqn,
    char *derv,
    ALGEB DRing,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object IsConstant =
      { bmi_balsa_string_object, "IsConstant", false, 0 };

  F = bmi_balsa_new_function (&IsConstant, 3);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (eqn));
  MapleListAssign (0, F, 2, bmi_balsa_new_string (derv));
  MapleListAssign (0, F, 3, DRing);

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, DRing),
      fix_notation (notout, DRing), timeout, memout, &small);
}

ALGEB_string
bmi_dapyx_leading_derivative (
    char *eqns,
    ALGEB regchain,
    bool fullset,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object LeadingDerivative =
      { bmi_balsa_string_object, "LeadingDerivative", false, 0 };

  F = bmi_balsa_new_function (&LeadingDerivative, 3);
  MapleListAssign (0, F, 1,
      isnull (eqns) ? regchain : bmi_balsa_new_string (eqns));
  MapleListAssign (0, F, 2, fullset ? &vrai : &faux);
  MapleListAssign (0, F, 3, regchain);

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, regchain),
      fix_notation (notout, regchain), timeout, memout, &large);
}

ALGEB_string
bmi_dapyx_leading_rank (
    char *eqns,
    ALGEB regchain,
    bool fullset,
    bool listform,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB A, F;
  static struct bmi_balsa_object LeadingRank =
      { bmi_balsa_string_object, "LeadingRank", false, 0 };
  static struct bmi_balsa_object LeadingRankListForm =
      { bmi_balsa_string_object, "LeadingRankListForm", false, 0 };

  if (listform)
    A = &LeadingRankListForm;
  else
    A = &LeadingRank;
  F = bmi_balsa_new_function (A, 3);
  MapleListAssign (0, F, 1,
      isnull (eqns) ? regchain : bmi_balsa_new_string (eqns));
  MapleListAssign (0, F, 2, fullset ? &vrai : &faux);
  MapleListAssign (0, F, 3, regchain);

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, regchain),
      fix_notation (notout, regchain), timeout, memout, &large);
}

ALGEB_string
bmi_dapyx_leading_coefficient (
    char *eqns,
    ALGEB regchain,
    bool fullset,
    char *variable,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object LeadingCoefficient =
      { bmi_balsa_string_object, "LeadingCoefficient", false, 0 };

  F = bmi_balsa_new_function (&LeadingCoefficient, 4);
  MapleListAssign (0, F, 1,
      isnull (eqns) ? regchain : bmi_balsa_new_string (eqns));
  MapleListAssign (0, F, 2, fullset ? &vrai : &faux);
  MapleListAssign (0, F, 3, bmi_balsa_new_string (variable));
  MapleListAssign (0, F, 4, regchain);

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, regchain),
      fix_notation (notout, regchain), timeout, memout, &large);
}

ALGEB_string
bmi_dapyx_tail (
    char *eqns,
    ALGEB regchain,
    bool fullset,
    char *variable,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object Tail =
      { bmi_balsa_string_object, "Tail", false, 0 };

  F = bmi_balsa_new_function (&Tail, 4);
  MapleListAssign (0, F, 1,
      isnull (eqns) ? regchain : bmi_balsa_new_string (eqns));
  MapleListAssign (0, F, 2, fullset ? &vrai : &faux);
  MapleListAssign (0, F, 3, bmi_balsa_new_string (variable));
  MapleListAssign (0, F, 4, regchain);

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, regchain),
      fix_notation (notout, regchain), timeout, memout, &large);
}

ALGEB_string
bmi_dapyx_separant (
    char *eqns,
    ALGEB regchain,
    bool fullset,
    char *variable,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object Separant =
      { bmi_balsa_string_object, "Separant", false, 0 };

  F = bmi_balsa_new_function (&Separant, 4);
  MapleListAssign (0, F, 1,
      isnull (eqns) ? regchain : bmi_balsa_new_string (eqns));
  MapleListAssign (0, F, 2, fullset ? &vrai : &faux);
  MapleListAssign (0, F, 3, bmi_balsa_new_string (variable));
  MapleListAssign (0, F, 4, regchain);

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, regchain),
      fix_notation (notout, regchain), timeout, memout, &large);
}

ALGEB_string
bmi_dapyx_normal_form (
    ALGEB regchain,
    char *eqns,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object NormalForm =
      { bmi_balsa_string_object, "NormalForm", false, 0 };

  F = bmi_balsa_new_function (&NormalForm, 2);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (eqns));
  MapleListAssign (0, F, 2, regchain);

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, regchain),
      fix_notation (notout, regchain), timeout, memout, &large);
}

ALGEB_string
bmi_dapyx_differentiate (
    ALGEB DRing,
    char *eqns,
    bool fullset,
    char *lders,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object Differentiate =
      { bmi_balsa_string_object, "Differentiate", false, 0 };

  F = bmi_balsa_new_function (&Differentiate, 4);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (eqns));
  MapleListAssign (0, F, 2, fullset ? &vrai : &faux);
  MapleListAssign (0, F, 3, bmi_balsa_new_string (lders));
  MapleListAssign (0, F, 4, DRing);

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, DRing),
      fix_notation (notout, DRing), timeout, memout, &large);
}

ALGEB_string
bmi_dapyx_integrate (
    ALGEB DRing,
    char *eqns,
    char *var,
    bool iterated,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object RatBilge =
      { bmi_balsa_string_object, "RatBilge", false, 0 };

  F = bmi_balsa_new_function (&RatBilge, 4);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (eqns));
  MapleListAssign (0, F, 2, bmi_balsa_new_string (var));
  MapleListAssign (0, F, 3, iterated ? &vrai : &faux);
  MapleListAssign (0, F, 4, DRing);

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, DRing),
      fix_notation (notout, DRing), timeout, memout, &large);
}

ALGEB_string
bmi_dapyx_coeffs (
    char *streqns,
    char *strvar,
    char *strgens,
    char *strrels,
    ALGEB DRing,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object Coeffs =
      { bmi_balsa_string_object, "Coeffs", false, 0 };
/*
 * There are two forms, for compatibility reasons with MAPLE
 * To do: pass the "collected" bool as last argument
 */
  if (strvar[0] != '\0')
    {
      F = bmi_balsa_new_function (&Coeffs, 3);
      MapleListAssign (0, F, 1, bmi_balsa_new_string (streqns));
      MapleListAssign (0, F, 2, bmi_balsa_new_string (strvar));
      MapleListAssign (0, F, 3, DRing);
    }
  else
    {
      F = bmi_balsa_new_function (&Coeffs, 4);
      MapleListAssign (0, F, 1, bmi_balsa_new_string (streqns));
      MapleListAssign (0, F, 2, bmi_balsa_new_string (strgens));
      MapleListAssign (0, F, 3, bmi_balsa_new_string (strrels));
      MapleListAssign (0, F, 4, DRing);
    }

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, DRing),
      fix_notation (notout, DRing), timeout, memout, &large);
}

ALGEB_string
bmi_dapyx_equations (
    ALGEB regchain,
    bool fullset,
    bool solved,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB A, F;
  static struct bmi_balsa_object Equations =
      { bmi_balsa_string_object, "Equations", false, 0 };
  static struct bmi_balsa_object RewriteRules =
      { bmi_balsa_string_object, "RewriteRules", false, 0 };

  if (solved)
    A = &RewriteRules;
  else
    A = &Equations;
  F = bmi_balsa_new_function (A, 2);
  MapleListAssign (0, F, 1, regchain);
  MapleListAssign (0, F, 2, fullset ? &vrai : &faux);

  A = eval
      (F,
      fix_notation (notin, regchain),
      fix_notation (notout, regchain), timeout, memout, &large);
#if defined (DOPRINT)
  printf ("[%s]\n", (char *) A->value);
#endif
  return (ALGEB_string) A;
}

ALGEB_string
bmi_dapyx_equations_with_criterion_RDC (
    ALGEB regchain,
    bool fullset,
    bool solved,
    char *criterion,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB A, F;
  static struct bmi_balsa_object Equations =
      { bmi_balsa_string_object, "EquationsWithCriterion", false, 0 };
  static struct bmi_balsa_object RewriteRules =
      { bmi_balsa_string_object, "RewriteRulesWithCriterion", false,
    0
  };

  if (solved)
    A = &RewriteRules;
  else
    A = &Equations;
  F = bmi_balsa_new_function (A, 4);
  MapleListAssign (0, F, 1, regchain);
  MapleListAssign (0, F, 2, bmi_balsa_new_string (criterion));
  MapleListAssign (0, F, 3, fullset ? &vrai : &faux);
  MapleListAssign (0, F, 4, regchain);

  A = eval
      (F,
      fix_notation (notin, regchain),
      fix_notation (notout, regchain), timeout, memout, &large);
#if defined (DOPRINT)
  printf ("[%s]\n", (char *) A->value);
#endif
  return (ALGEB_string) A;
}

ALGEB_string
bmi_dapyx_equations_with_criterion_DR (
    char *equations,
    ALGEB DRing,
    bool fullset,
    bool solved,
    char *criterion,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB A, F;
  static struct bmi_balsa_object Equations =
      { bmi_balsa_string_object, "EquationsWithCriterion", false, 0 };
  static struct bmi_balsa_object RewriteRules =
      { bmi_balsa_string_object, "RewriteRulesWithCriterion", false,
    0
  };

  if (solved)
    A = &RewriteRules;
  else
    A = &Equations;
  F = bmi_balsa_new_function (A, 4);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (equations));
  MapleListAssign (0, F, 2, bmi_balsa_new_string (criterion));
  MapleListAssign (0, F, 3, fullset ? &vrai : &faux);
  MapleListAssign (0, F, 4, DRing);

  A = eval
      (F,
      fix_notation (notin, DRing),
      fix_notation (notout, DRing), timeout, memout, &large);
#if defined (DOPRINT)
  printf ("[%s]\n", (char *) A->value);
#endif
  return (ALGEB_string) A;
}

ALGEB_string
bmi_dapyx_prem (
    char *eqns,
    ALGEB regchain,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object Prem =
      { bmi_balsa_string_object, "Prem", false, 0 };

  F = bmi_balsa_new_function (&Prem, 2);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (eqns));
  MapleListAssign (0, F, 2, regchain);

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, regchain),
      fix_notation (notout, regchain), timeout, memout, &small);
}

ALGEB_string
bmi_dapyx_resultant (
    char *eqns,
    ALGEB regchain,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object Resultant =
      { bmi_balsa_string_object, "Resultant", false, 0 };

  F = bmi_balsa_new_function (&Resultant, 2);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (eqns));
  MapleListAssign (0, F, 2, regchain);

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, regchain),
      fix_notation (notout, regchain), timeout, memout, &small);
}

ALGEB_string
bmi_dapyx_sort (
    char *eqns,
    char *mode,
    ALGEB DRing,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object SortByRank =
      { bmi_balsa_string_object, "SortByRank", false, 0 };

  F = bmi_balsa_new_function (&SortByRank, 3);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (eqns));
  MapleListAssign (0, F, 2, bmi_balsa_new_string (mode));
  MapleListAssign (0, F, 3, DRing);

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, DRing),
      fix_notation (notout, DRing), timeout, memout, &small);
}

ALGEB_string
bmi_dapyx_number_of_equations (
    ALGEB regchain)
{
  ALGEB F;
  static struct bmi_balsa_object NumberOfEquations =
      { bmi_balsa_string_object, "NumberOfEquations", false, 0 };

  F = bmi_balsa_new_function (&NumberOfEquations, 1);
  MapleListAssign (0, F, 1, regchain);
  return (ALGEB_string) eval
      (F,
      bmi_balsa_default_sympy_notation (),
      bmi_balsa_default_sympy_notation (), 0, 0, &small);
}

ALGEB_string
bmi_dapyx_preparation_equation (
    char *eqns,
    ALGEB regchain,
    char *generators,
    char *relations,
    ba0_int_p congruence,
    char *zstring,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object PreparationEquation =
      { bmi_balsa_string_object, "PreparationEquation", false, 0 };

  F = bmi_balsa_new_function (&PreparationEquation, 6);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (eqns));
  MapleListAssign (0, F, 2, regchain);
  MapleListAssign (0, F, 3, bmi_balsa_new_string (generators));
  MapleListAssign (0, F, 4, bmi_balsa_new_string (relations));
  MapleListAssign (0, F, 5, congruence ? &bool_vrai : &bool_faux);
  MapleListAssign (0, F, 6, bmi_balsa_new_string (zstring));

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, regchain),
      fix_notation (notout, regchain), timeout, memout, &small);
}

ALGEB_listof_list
bmi_dapyx_DenefLipshitz (
    char *equations,
    char *inequations,
    char *properties,
    ALGEB DRing,
    char *Y,
    char *Ybar,
    char *q,
    char *x,
    char *beta_control,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object DenefLipshitz =
      { bmi_balsa_string_object, "DenefLipshitz", false, 0 };

  F = bmi_balsa_new_function (&DenefLipshitz, 9);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (equations));
  MapleListAssign (0, F, 2, bmi_balsa_new_string (inequations));
  MapleListAssign (0, F, 3, bmi_balsa_new_string (properties));
  MapleListAssign (0, F, 4, DRing);
  MapleListAssign (0, F, 5, bmi_balsa_new_string (Y));
  MapleListAssign (0, F, 6, bmi_balsa_new_string (Ybar));
  MapleListAssign (0, F, 7, bmi_balsa_new_string (q));
  MapleListAssign (0, F, 8, bmi_balsa_new_string (x));
  MapleListAssign (0, F, 9, bmi_balsa_new_string (beta_control));

  return (ALGEB_listof_list) eval
      (F,
      fix_notation (notin, DRing),
      fix_notation (notout, DRing), timeout, memout, &large);
}

ALGEB_listof_list
bmi_dapyx_DenefLipshitz_extend (
    char *equations,
    char *inequations,
    ALGEB DLuple,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object DenefLipshitz =
      { bmi_balsa_string_object, "DenefLipshitz", false, 0 };

  F = bmi_balsa_new_function (&DenefLipshitz, 3);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (equations));
  MapleListAssign (0, F, 2, bmi_balsa_new_string (inequations));
  MapleListAssign (0, F, 3, DLuple);

  return (ALGEB_listof_list) eval
      (F,
      fix_notation (notin, DLuple),
      fix_notation (notout, DLuple), timeout, memout, &large);
}

ALGEB_string
bmi_dapyx_DenefLipshitz_leading_polynomial (
    ALGEB DLuple,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object DenefLipshitz =
      { bmi_balsa_string_object, "DenefLipshitzLeadingPolynomial", false, 0 };

  F = bmi_balsa_new_function (&DenefLipshitz, 1);
  MapleListAssign (0, F, 1, DLuple);

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, DLuple),
      fix_notation (notout, DLuple), timeout, memout, &small);
}

ALGEB_string
bmi_dapyx_DenefLipshitz_series (
    char *vars,
    ALGEB DLuple,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object DenefLipshitz =
      { bmi_balsa_string_object, "DenefLipshitzSeries", false, 0 };

  F = bmi_balsa_new_function (&DenefLipshitz, 2);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (vars));
  MapleListAssign (0, F, 2, DLuple);

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, DLuple),
      fix_notation (notout, DLuple), timeout, memout, &large);
}

ALGEB_string
bmi_dapyx_DenefLipshitz_constraints (
    ALGEB DLuple,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object DenefLipshitz =
      { bmi_balsa_string_object, "DenefLipshitzConstraints", false, 0 };

  F = bmi_balsa_new_function (&DenefLipshitz, 1);
  MapleListAssign (0, F, 1, DLuple);

  return (ALGEB_string) eval
      (F,
      fix_notation (notin, DLuple),
      fix_notation (notout, DLuple), timeout, memout, &large);
}

ALGEB_list
bmi_dapyx_RosenfeldGroebner (
    char *equations,
    char *inequations,
    char *generators,
    char *relations,
    char *attributes,
    ALGEB DRing_or_regchain,
    char *singsol,
    char *dimlb,
    bool called_from_RG,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object RosenfeldGroebner =
      { bmi_balsa_string_object, "RosenfeldGroebner", false, 0 };

  F = bmi_balsa_new_function (&RosenfeldGroebner, 9);
  MapleListAssign (0, F, 1, bmi_balsa_new_string (equations));
  MapleListAssign (0, F, 2, bmi_balsa_new_string (inequations));
  MapleListAssign (0, F, 3, bmi_balsa_new_string (generators));
  MapleListAssign (0, F, 4, bmi_balsa_new_string (relations));
  MapleListAssign (0, F, 5, bmi_balsa_new_string (attributes));
  MapleListAssign (0, F, 6, DRing_or_regchain);
  MapleListAssign (0, F, 7, bmi_balsa_new_string (singsol));
  MapleListAssign (0, F, 8, bmi_balsa_new_string (dimlb));
  MapleListAssign (0, F, 9, called_from_RG ? &bool_vrai : &bool_faux);

  return (ALGEB_list) eval
      (F,
      fix_notation (notin, DRing_or_regchain),
      fix_notation (notout, DRing_or_regchain), timeout, memout, &large);
}

ALGEB
bmi_dapyx_pardi (
    ALGEB regchain,
    char *target_ranking,
    bool prime,
    char *notin,
    char *notout,
    ba0_int_p timeout,
    ba0_int_p memout)
{
  ALGEB F;
  static struct bmi_balsa_object Pardi =
      { bmi_balsa_string_object, "Pardi", false, 0 };

#if defined (DOPRINT)
  printf ("Enter PARDI\n");
#endif
  F = bmi_balsa_new_function (&Pardi, 3);
  MapleListAssign (0, F, 1, regchain);
  MapleListAssign (0, F, 2, bmi_balsa_new_string (target_ranking));
  MapleListAssign (0, F, 3, prime ? &vrai : &faux);
#if defined (DOPRINT)
  printf ("before eval\n");
#endif
  F = eval
      (F,
      fix_notation (notin, regchain),
      fix_notation (notout, regchain), timeout, memout, &large);
#if defined (DOPRINT)
  printf ("Exit PARDI\n");
#endif
  return F;
}
