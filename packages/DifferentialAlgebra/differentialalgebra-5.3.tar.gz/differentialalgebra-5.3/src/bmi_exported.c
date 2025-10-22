#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"

#include "bmi_all_derivatives.h"
#include "bmi_attributes.h"
#include "bmi_base_field_generators.h"
#include "bmi_belongs_to.h"
#include "bmi_coeffs.h"
#include "bmi_delta_polynomial.h"
#include "bmi_Denef_Lipshitz.h"
#include "bmi_Denef_Lipshitz_constraints.h"
#include "bmi_Denef_Lipshitz_leading_polynomial.h"
#include "bmi_Denef_Lipshitz_series.h"
#include "bmi_differential_prem.h"
#include "bmi_differential_ring.h"
#include "bmi_differentiate.h"
#include "bmi_equations.h"
#include "bmi_factor_derivative.h"
#include "bmi_field_element.h"
#include "bmi_frozen_symbols.h"
#include "bmi_indets.h"
#include "bmi_is_constant.h"
#include "bmi_is_orthonomic.h"
#include "bmi_is_reduced.h"
#include "bmi_leading_coefficient.h"
#include "bmi_leading_derivative.h"
#include "bmi_leading_rank.h"
#include "bmi_min_rank_element.h"
#include "bmi_max_rank_element.h"
#include "bmi_normal_form.h"
#include "bmi_normal_form_ext.h"
#include "bmi_number_of_equations.h"
#include "bmi_ranking.h"
#include "bmi_rat_bilge.h"
#include "bmi_parameters.h"
#include "bmi_pardi.h"
#include "bmi_prem.h"
#include "bmi_preparation_equation.h"
#include "bmi_pretend_regchain.h"
#include "bmi_process_equations.h"
#include "bmi_process_expansion_point.h"
#include "bmi_reduced_form.h"
#include "bmi_resultant.h"
#include "bmi_Rosenfeld_Groebner.h"
#include "bmi_separant.h"
#include "bmi_sort_by_rank.h"
#include "bmi_tail.h"

struct bmi_exported_pair
{
  char *name;
    ALGEB (
      *pointer) (
      struct bmi_callback *);
};

/*
 * The table associates a bmi function to each method of
 * the Maple DifferentialAlgebra package
 *
 * Entries are sought using bsearch so that the table must
 * be sorted by increasing order
 */

static struct bmi_exported_pair bmi_exported_table[] = {
  {"AllDerivatives", &bmi_all_derivatives},
  {"Attributes", &bmi_attributes},
  {"BaseFieldGenerators", &bmi_base_field_generators},
  {"BelongsTo", &bmi_belongs_to},
  {"Coeffs", &bmi_coeffs},
  {"DeltaPolynomial", &bmi_delta_polynomial},
  {"DenefLipshitz", &bmi_Denef_Lipshitz},
  {"DenefLipshitzConstraints", &bmi_Denef_Lipshitz_constraints},
  {"DenefLipshitzLeadingPolynomial", &bmi_Denef_Lipshitz_leading_polynomial},
  {"DenefLipshitzSeries", &bmi_Denef_Lipshitz_series},
  {"DifferentialPrem", &bmi_differential_prem},
  {"DifferentialRing", &bmi_differential_ring},
  {"Differentiate", &bmi_differentiate},
  {"Equations", &bmi_equations},
  {"EquationsWithCriterion", &bmi_equations_with_criterion},
  {"FactorDerivative", &bmi_factor_derivative},
  {"FieldElement", &bmi_field_element},
  {"FrozenSymbols", &bmi_frozen_symbols},
  {"Indets", &bmi_indets},
  {"IsConstant", &bmi_is_constant},
  {"IsOrthonomic", &bmi_is_orthonomic},
  {"IsReduced", &bmi_is_reduced},
  {"LeadingCoefficient", &bmi_leading_coefficient},
  {"LeadingDerivative", &bmi_leading_derivative},
  {"LeadingRank", &bmi_leading_rank},
  {"LeadingRankListForm", &bmi_leading_rank_list_form},
  {"MaxRankElement", &bmi_max_rank_element},
  {"MinRankElement", &bmi_min_rank_element},
  {"NormalForm", &bmi_normal_form},
  {"NormalFormHandlingExceptions",
      &bmi_normal_form_handling_exceptions},
  {"NumberOfEquations", &bmi_number_of_equations},
  {"Parameters", &bmi_parameters},
  {"Pardi", &bmi_pardi},
  {"Prem", &bmi_prem},
  {"PreparationEquation", &bmi_preparation_equation},
  {"PretendRegularDifferentialChain", &bmi_pretend_regchain},
  {"ProcessEquations", &bmi_process_equations},
  {"ProcessExpansionPoint", &bmi_process_expansion_point},
  {"Ranking", &bmi_ranking},
  {"RatBilge", &bmi_rat_bilge},
  {"ReducedForm", &bmi_reduced_form},
  {"Resultant", &bmi_resultant},
  {"RewriteRules", &bmi_rewrite_rules},
  {"RewriteRulesWithCriterion", &bmi_rewrite_rules_with_criterion},
  {"RosenfeldGroebner", &bmi_Rosenfeld_Groebner},
  {"Separant", &bmi_separant},
  {"SortByRank", &bmi_sort_by_rank},
  {"Tail", &bmi_tail}
};

#define NARGS(t) (sizeof(t)/sizeof(*(t)))

/*
 * For bsearch
 */

static int
bmi_compare_identifier (
    const void *_name,
    const void *_pair)
{
  char *name = (char *) _name;
  struct bmi_exported_pair *pair = (struct bmi_exported_pair *) _pair;

  return strcmp (name, pair->name);
}

static struct bmi_exported_pair *
get_bmi_exported_pair (
    char *name)
{
  struct bmi_exported_pair *pair;

  pair = (struct bmi_exported_pair *) bsearch
      (name, bmi_exported_table, NARGS (bmi_exported_table),
      sizeof (struct bmi_exported_pair), &bmi_compare_identifier);
  return pair;
}

/*
 * This variable is involved in an error which arises at debugging stage only
 * It is thus harmless.
 */

#define BMIBUFSZ 256
static char bmi_exported_mesgerr[BMIBUFSZ];

ALGEB
bmi_call_exported (
    char *name,
    struct bmi_callback *callback)
{
  struct bmi_exported_pair *pair;
  ALGEB res;

  pair = get_bmi_exported_pair (name);
  if (pair == (struct bmi_exported_pair *) 0)
/*
 * This should not happen error
 */
    {
      strcpy (bmi_exported_mesgerr, BMI_ERRFUN);
      strcat (bmi_exported_mesgerr, ": ");
      strncat (bmi_exported_mesgerr, name,
          BMIBUFSZ - strlen (bmi_exported_mesgerr) - 5);
      BA0_RAISE_EXCEPTION (bmi_exported_mesgerr);
    }
/*
    fprintf (stderr, "bmi_call_exported: %s\n", pair->name);
*/
  res = (*pair->pointer) (callback);
  MapleGcProtect (callback->kv, res);
/*
    fprintf (stderr, "bmi_call_exported: out\n");
*/
  return res;
}
