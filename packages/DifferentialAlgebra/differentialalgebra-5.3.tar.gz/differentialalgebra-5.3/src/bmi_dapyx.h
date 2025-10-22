#if !defined (BMI_DAPYX_H)
#   define BMI_DAPYX_H 1

#   include "bmi_balsa.h"


BEGIN_C_DECLS

/*
 * Interface between DifferentialAlgebra.pyx and BALSA
 * Used by both sagemath and sympy
 * The functions implemented in dapyx are the entry points of 
 *      DifferentialAlgebra.pyx
 */

/*
 * Type aliasing of ALGEB for legibility
 */

struct bmi_balsa_object_string
{
  enum bmi_balsa_typeof_object type;
  char *value;
  bool dynamic;
  int nbref;
};

typedef struct bmi_balsa_object_string *ALGEB_string;

/*
 * table
 */

struct bmi_balsa_object_table
{
  enum bmi_balsa_typeof_object type;
  struct bmi_balsa_table *value;
  bool dynamic;
  int nbref;
};

typedef struct bmi_balsa_object_table *ALGEB_table;

/*
 * list
 */

struct bmi_balsa_object_list
{
  enum bmi_balsa_typeof_object type;
  struct bmi_balsa_list *value;
  bool dynamic;
  int nbref;
};

typedef struct bmi_balsa_object_list *ALGEB_list;

/*
 * list of table
 */

struct bmi_balsa_listof_table
{
  ba0_int_p alloc;
  ba0_int_p size;
  ALGEB_table *tab;
};

struct bmi_balsa_object_listof_table
{
  enum bmi_balsa_typeof_object type;
  struct bmi_balsa_listof_table *value;
  bool dynamic;
  int nbref;
};

typedef struct bmi_balsa_object_listof_table *ALGEB_listof_table;

/*
 * list of list
 */

struct bmi_balsa_listof_list
{
  ba0_int_p alloc;
  ba0_int_p size;
  ALGEB_list *tab;
};

struct bmi_balsa_object_listof_list
{
  enum bmi_balsa_typeof_object type;
  struct bmi_balsa_listof_list *value;
  bool dynamic;
  int nbref;
};

typedef struct bmi_balsa_object_listof_list *ALGEB_listof_list;

/*
 * list of string
 */

struct bmi_balsa_listof_string
{
  ba0_int_p alloc;
  ba0_int_p size;
  ALGEB_string *tab;
};

struct bmi_balsa_object_listof_string
{
  enum bmi_balsa_typeof_object type;
  struct bmi_balsa_listof_string *value;
  bool dynamic;
  int nbref;
};

typedef struct bmi_balsa_object_listof_string *ALGEB_listof_string;

/*
 * Functions called from DifferentialAlgebra.pyx
 */

extern bool bmi_dapyx_is_error (
    void *);

extern char *bmi_dapyx_mesgerr (
    void *);

extern ALGEB bmi_dapyx_differential_ring (
    char *,
    char *,
    char *,
    char *);

extern ALGEB bmi_dapyx_pardi (
    ALGEB,
    char *,
    bool,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB bmi_dapyx_pretend_regular_differential_chain (
    char *,
    ALGEB,
    char *,
    bool,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_listof_list bmi_dapyx_DenefLipshitz (
    char *,
    char *,
    char *,
    ALGEB,
    char *,
    char *,
    char *,
    char *,
    char *,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_listof_list bmi_dapyx_DenefLipshitz_extend (
    char *,
    char *,
    ALGEB,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_DenefLipshitz_leading_polynomial (
    ALGEB,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_DenefLipshitz_series (
    char *,
    ALGEB,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_DenefLipshitz_constraints (
    ALGEB,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_list bmi_dapyx_RosenfeldGroebner (
    char *,
    char *,
    char *,
    char *,
    char *,
    ALGEB,
    char *,
    char *,
    bool,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_listof_string bmi_dapyx_process_equations (
    char *,
    ALGEB,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_attributes (
    ALGEB);

extern ALGEB_string bmi_dapyx_base_field_generators (
    char *,
    char *,
    ALGEB,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_coeffs (
    char *,
    char *,
    char *,
    char *,
    ALGEB,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_differential_prem (
    char *,
    char *,
    ALGEB,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_differential_prem2 (
    char *,
    char *,
    char *,
    ALGEB,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_differentiate (
    ALGEB,
    char *,
    bool,
    char *,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_equations (
    ALGEB,
    bool,
    bool,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_equations_with_criterion_DR (
    char *,
    ALGEB,
    bool,
    bool,
    char *,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_equations_with_criterion_RDC (
    ALGEB,
    bool,
    bool,
    char *,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_factor_derivative (
    char *,
    ALGEB,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_indets (
    char *,
    ALGEB,
    char *,
    char *,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_integrate (
    ALGEB,
    char *,
    char *,
    bool,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_is_constant (
    char *,
    char *,
    ALGEB,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_leading_coefficient (
    char *,
    ALGEB,
    bool,
    char *,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_leading_derivative (
    char *,
    ALGEB,
    bool,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_leading_rank (
    char *,
    ALGEB,
    bool,
    bool,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_normal_form (
    ALGEB,
    char *,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_number_of_equations (
    ALGEB);

extern ALGEB_string bmi_dapyx_preparation_equation (
    char *,
    ALGEB,
    char *,
    char *,
    ba0_int_p,
    char *,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_ranking (
    ALGEB);

extern ALGEB_string bmi_dapyx_prem (
    char *,
    ALGEB,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_resultant (
    char *,
    ALGEB,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_separant (
    char *,
    ALGEB,
    bool,
    char *,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_sort (
    char *,
    char *,
    ALGEB,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

extern ALGEB_string bmi_dapyx_tail (
    char *,
    ALGEB,
    bool,
    char *,
    char *,
    char *,
    ba0_int_p,
    ba0_int_p);

END_C_DECLS
#endif
