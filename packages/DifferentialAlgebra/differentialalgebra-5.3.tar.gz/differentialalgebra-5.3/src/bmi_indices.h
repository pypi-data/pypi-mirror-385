/*
 * This file is processed by the Makefile to produce bmi_indices.h
 * See sedcmds/indices.sed
 */

/*
 * Cell sizes
 */

#define BMI_IX_small		"small"
#define BMI_IX_large		"large"

/*
 * The entries of the tables and the related keywords
 * BMI_IX_Derivative and BMI_IX_jet0 are for sympy only
 * BMI_jet_LENGTH is the length of the 'jet' prefix of 'jet0'
 * It is implicitly used in the code that the jet0 notation starts with
 *  BMI_IX_jet
 */

#define BMI_IX_equations	"Equations"
#define BMI_IX_ordering		"Ranking"
#define BMI_IX_notation		"Notation"
#define BMI_IX_jet		"jet"
#define BMI_jet_LENGTH  3
#define BMI_IX_tjet		"tjet"
#define BMI_IX_jet0 	"jet0"
#define BMI_IX_diff		"diff"
#define BMI_IX_udif		"Diff"
#define BMI_IX_D                "D"
#define BMI_IX_Derivative   "Derivative"
#define BMI_IX_undefined	"undefined"
#define BMI_IX_type		"Type"
#define BMI_IX_regchain		"RegularDifferentialChain"
#define BMI_IX_dring		"DifferentialRing"
#define BMI_IX_DLuple		"DenefLipshitzUple"

/*
 * For sort
 */

#define BMI_IX_ascending	"ascending"
#define BMI_IX_descending	"descending"

/*
 * Criteria of Equations
 */

#define BMI_IX_leader		"leader"
#define BMI_IX_order		"order"
#define BMI_IX_rank		"rank"

#define BMI_IX_eq		"equal"
#define BMI_IX_ne		"different"
#define BMI_IX_gt		"greater"
#define BMI_IX_ge		"greatereq"
#define BMI_IX_lt		"less"
#define BMI_IX_le		"lesseq"

#define BMI_IX_identical	"identical"
#define BMI_IX_deriv		"derivative"
#define BMI_IX_proper		"proper"

/*
 * Selections of Indets
 */

#define BMI_IX_depvars		"depvars"
#define BMI_IX_indepvars	"indepvars"
#define BMI_IX_derivs		"derivatives"
#define BMI_IX_allvars		"allvars"
#define BMI_IX_params		"parameters"
#define BMI_IX_constants        "constants"

/*
 * Types of reduction
 */

#define BMI_IX_fully            "full"
#define BMI_IX_partially        "partial"
#define BMI_IX_algebraically	"algebraic"

/*
 * singsol
 */

#define BMI_IX_all		"all"
#define BMI_IX_none		"none"
#define BMI_IX_essential	"essential"

/*
 * dimlbin
 */

#define BMI_IX_nocase		"nocase"
#define BMI_IX_safecase		"safecase"
#define BMI_IX_odecase		"odecase"
#define BMI_IX_pdecase		"pdecase"

/*
 * Denef Lipshitz beta control
 */

#define BMI_IX_single       "single"
#define BMI_IX_vector       "vector"
