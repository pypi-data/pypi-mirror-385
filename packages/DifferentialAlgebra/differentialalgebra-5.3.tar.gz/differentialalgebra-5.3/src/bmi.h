#if !defined (BMI_BALSA_H)
#   define BMI_BALSA_H 1

/*
 * BALSA is a fake MAPLE API, sufficient to make the regular bmi code work.
 * In the context of sagemath and sage, the functions implemented in
 *      BALSA are only called by the functions implemented in dapyx
 */

#   include <blad.h>

BEGIN_C_DECLS

enum bmi_balsa_typeof_object
{
  bmi_balsa_function_object,
  bmi_balsa_table_object,
  bmi_balsa_list_object,
  bmi_balsa_string_object,
  bmi_balsa_bool_object,
  bmi_balsa_integer_object,
  bmi_balsa_error_object
};

/*
 * Emulates the ALGEB defined in the MAPLE API.
 *
 * type provides the type of value.
 * type = bmi_balsa_function_object
 *      = bmi_balsa_list_object       -> value = struct bmi_balsa_list*
 * type = bmi_balsa_table_object      -> value = struct bmi_balsa_table*
 * type = bmi_balsa_string_object     -> value = char*
 * type = bmi_balsa_bool_object
 *      = bmi_balsa_integer_object    -> value = the pointer value
 *
 * dynamic = true -> the structure must be freed
 * nbref          -> a reference counter (meaningful if dynamic)
 */

struct bmi_balsa_object
{
  enum bmi_balsa_typeof_object type;
  void *value;
  bool dynamic;
  int nbref;
};

/*
 * The ALGEB 0 is allowed
 */

typedef struct bmi_balsa_object *ALGEB;

/*
 * Coded as arrays.
 * For a true list, tab [0] is the ALGEB 0
 * For a function, tab [0] is the function name
 */

struct bmi_balsa_list
{
  ba0_int_p alloc;
  ba0_int_p size;
  ALGEB *tab;
};

/*
 * As well differential rings as regular differential chains.
 * For differential rings, equations is the ALGEB 0.
 * The ALGEB type and notation are not dynamic.
 */

struct bmi_balsa_table
{
  ALGEB type;
  ALGEB notation;
  ALGEB ordering;
  ALGEB equations;
};

extern ALGEB bmi_balsa_default_sage_notation (
    void);
extern ALGEB bmi_balsa_default_sympy_notation (
    void);

extern ALGEB bmi_balsa_new_ALGEB (
    enum bmi_balsa_typeof_object type,
    void *value);
extern ALGEB bmi_balsa_new_string (
    char *);
extern ALGEB bmi_balsa_new_error (
    void);
extern ALGEB bmi_balsa_new_function (
    ALGEB,
    ba0_int_p);

extern void bmi_balsa_increment_nbref (
    ALGEB);
extern void bmi_balsa_decrement_nbref (
    ALGEB);
extern void bmi_balsa_clear_ALGEB (
    void *);
extern void bmi_balsa_printf_ALGEB (
    ALGEB);

/***********************************************************************
 * Faking MAPLE
 ***********************************************************************/

typedef void *MKernelVector;

/*
 * bmi_rtable
 */

#   define RTABLE_INTEGER32 0
#   define RTABLE_C 0
#   define UINTEGER32 char      /* do not worry */
typedef bool M_BOOL;
typedef ba0_int_p M_INT;

struct struct_RTableSettings
{
  int data_type;
  int order;
  bool read_only;
  int num_dimensions;
};

typedef struct struct_RTableSettings RTableSettings;

extern void RTableGetDefaults (
    MKernelVector,
    RTableSettings *);
extern void *RTableCreate (
    MKernelVector,
    RTableSettings *,
    ALGEB,
    M_INT *);
extern void *RTableDataBlock (
    MKernelVector,
    ALGEB);

extern void *MapleAlloc (
    MKernelVector,
    long);
extern void MapleGcAllow (
    MKernelVector,
    ALGEB);
extern void MapleDispose (
    MKernelVector,
    ALGEB);
extern void MapleGcProtect (
    MKernelVector,
    ALGEB);
extern void MapleCheckInterrupt (
    MKernelVector);

/*
 * bmi_memory
 */

#   define M_DECL
typedef void M_DECL bmi_balsa_error_proc (
    const char *,
    void *);
extern void MaplePushErrorProc (
    MKernelVector,
    bmi_balsa_error_proc *,
    void *);
extern void MaplePopErrorProc (
    MKernelVector);

/*
 * bmi_callback
 */

extern ALGEB ToMapleName (
    MKernelVector,
    char *,
    M_BOOL);
extern ALGEB ToMapleInteger (
    MKernelVector,
    ba0_int_p);
extern long MapleToInteger32 (
    MKernelVector,
    ALGEB);
extern ALGEB EvalMapleProc (
    MKernelVector,
    ALGEB,
    int,
    ...);
extern bool IsMapleString (
    MKernelVector,
    ALGEB);
extern bool IsMapleTable (
    MKernelVector,
    ALGEB);
extern bool IsMapleName (
    MKernelVector,
    ALGEB);
extern bool MapleToM_BOOL (
    MKernelVector,
    ALGEB);
extern char *MapleToString (
    MKernelVector,
    ALGEB);
extern ALGEB MapleTableSelect (
    MKernelVector,
    ALGEB,
    ALGEB);
extern void MapleRaiseError (
    MKernelVector,
    char *);

/*
 * bmi_blad_eval
 */

extern long MapleNumArgs (
    MKernelVector,
    ALGEB);

/*
 * exported
 */

extern ALGEB MapleListAlloc (
    MKernelVector,
    M_INT);
extern void MapleListAssign (
    MKernelVector,
    ALGEB,
    M_INT,
    ALGEB);
extern ALGEB ToMapleBoolean (
    MKernelVector,
    long);
extern ALGEB bmi_balsa_new_differential_ring (
    ALGEB);
extern ALGEB bmi_balsa_new_regchain (
    ALGEB);
extern ALGEB bmi_balsa_new_DLuple (
    ALGEB);

END_C_DECLS
#endif
#if !defined (BMI_DAPYX_H)
#   define BMI_DAPYX_H 1

/* #   include "bmi_balsa.h" */


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
