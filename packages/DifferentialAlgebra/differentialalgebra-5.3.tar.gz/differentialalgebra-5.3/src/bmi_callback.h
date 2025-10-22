#if !defined (BMI_CALLBACK_H)
#   define BMI_CALLBACK_H 1

#   include "bmi_common.h"

BEGIN_C_DECLS

/*
 * A callback is a structure which involves a MAPLE ALGEB and, over which,
 * it is possible to apply some MAPLE commands. 
 * 
 * To speed up the process, some MAPLE names, used to formulate the
 * MAPLE commands are stored in the structure. Beware to the fact that 
 * some of these names need to be protected from the MAPLE gc. Thus,
 * they get protected when the structure is initialized and unprotected
 * when the structure is cleared. However, since these MAPLE names are
 * unique, clearing one struct callback unprotects the MAPLE names stored
 * in any other struct callback (bug). Starting from bmi-2.2, one manages to
 * get only one struct callback created.
 */

struct bmi_callback
{
  MKernelVector kv;
  ALGEB arg;                    /* The ALGEB functions apply to */
  ALGEB op;                     /* MAPLE keywords. They do not need to be protected */
  ALGEB nops;
  ALGEB ordering;               /* Indices in MAPLE tables. They need to be protected */
  ALGEB equations;
  ALGEB notation;
  ALGEB type;
};

extern void bmi_init_callback (
    struct bmi_callback *,
    MKernelVector);

extern void bmi_gc_allow_callback (
    struct bmi_callback *);
extern void bmi_gc_protect_callback (
    struct bmi_callback *);
extern void bmi_clear_callback (
    struct bmi_callback *);

extern void bmi_set_callback_ALGEB (
    struct bmi_callback *,
    ALGEB);

extern long bmi_nops (
    struct bmi_callback *);

extern bool bmi_is_string_op (
    long,
    struct bmi_callback *);
extern bool bmi_is_table_op (
    long,
    struct bmi_callback *);
extern bool bmi_is_dring_op (
    long,
    struct bmi_callback *);
extern bool bmi_is_regchain_op (
    long,
    struct bmi_callback *);

extern bool bmi_bool_op (
    long,
    struct bmi_callback *);
extern char *bmi_string_op (
    long,
    struct bmi_callback *);
extern char *bmi_table_type_op (
    long,
    struct bmi_callback *);
extern char *bmi_table_notation_op (
    long,
    struct bmi_callback *);
extern ALGEB bmi_table_ordering_op (
    long,
    struct bmi_callback *);
extern ALGEB bmi_table_equations_op (
    long,
    struct bmi_callback *);

END_C_DECLS
#endif /*! BMI_CALLBACK_H */
