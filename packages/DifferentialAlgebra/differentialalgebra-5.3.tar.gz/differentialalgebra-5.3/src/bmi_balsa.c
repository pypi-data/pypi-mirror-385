#if HAVE_ASSERT_H
#   include <assert.h>
#else
#   define assert(condition) \
        if (!(condition)) \
          { \
            fprintf (stderr, "%s:%d: my_assert fails\n", __FILE__, __LINE__); \
            exit (1); \
          }
#endif

#include "bmi_balsa.h"
#include "bmi_indices.h"
#include "bmi_blad_eval.h"

/*
 * strdup is not available with -std=c99 - at least in string.h
 */

static char *
my_strdup (
    char *s)
{
  char *t = (char *) malloc (strlen (s) + 1);
  strcpy (t, s);
  return t;
}

static char *mesgerr;

/*
 * non-dynamic useful struct bmi_balsa_object
 */

static struct bmi_balsa_object op_name =
    { bmi_balsa_string_object, "op", false, 0 };
static struct bmi_balsa_object nops_name =
    { bmi_balsa_string_object, "nops", false, 0 };
static struct bmi_balsa_object ordering_name =
    { bmi_balsa_string_object, BMI_IX_ordering, false, 0 };
static struct bmi_balsa_object equations_name =
    { bmi_balsa_string_object, BMI_IX_equations, false, 0 };
static struct bmi_balsa_object notation_name =
    { bmi_balsa_string_object, BMI_IX_notation, false, 0 };
static struct bmi_balsa_object type_name =
    { bmi_balsa_string_object, BMI_IX_type, false, 0 };

static struct bmi_balsa_object jet_notation =
    { bmi_balsa_string_object, BMI_IX_jet, false, 0 };
static struct bmi_balsa_object D_notation =
    { bmi_balsa_string_object, BMI_IX_D, false, 0 };
static struct bmi_balsa_object Derivative_notation =
    { bmi_balsa_string_object, BMI_IX_Derivative, false, 0 };

static struct bmi_balsa_object dring =
    { bmi_balsa_string_object, BMI_IX_dring, false, 0 };
static struct bmi_balsa_object regchain =
    { bmi_balsa_string_object, BMI_IX_regchain, false, 0 };
static struct bmi_balsa_object DLuple =
    { bmi_balsa_string_object, BMI_IX_DLuple, false, 0 };

ALGEB
bmi_balsa_default_sage_notation (
    void)
{
  return &D_notation;
}

ALGEB
bmi_balsa_default_sympy_notation (
    void)
{
  return &Derivative_notation;
}

/*
 * Creates a new ALGEB and returns it
 */

ALGEB
bmi_balsa_new_ALGEB (
    enum bmi_balsa_typeof_object type,
    void *value)
{
  ALGEB res;

  res = (ALGEB) malloc (sizeof (struct bmi_balsa_object));
  assert (res != (ALGEB) 0);
  res->type = type;
  res->value = value;
  res->dynamic = true;
  res->nbref = 0;
  return res;
}

/*
 * Used in exported functions, to build a result.
 * Creates a new ALGEB of type string and returns it.
 */

ALGEB
bmi_balsa_new_string (
    char *s)
{
  char *t;

  t = my_strdup (s);
  return bmi_balsa_new_ALGEB (bmi_balsa_string_object, t);
}

/*
 * The error message actually is in mesgerr
 */

ALGEB
bmi_balsa_new_error (
    void)
{
  char *t;

  t = my_strdup (mesgerr);
  return bmi_balsa_new_ALGEB (bmi_balsa_error_object, t);
}

/*
 * Creates a new ALGEB of type function and returns it.
 */

ALGEB
bmi_balsa_new_function (
    ALGEB opzero,
    ba0_int_p nops)
{
  ALGEB F;

  F = MapleListAlloc (0, nops);
  MapleListAssign (0, F, 0, opzero);
  F->type = bmi_balsa_function_object;
  return F;
}

void
bmi_balsa_increment_nbref (
    ALGEB A)
{
  if (A && A->dynamic)
    A->nbref += 1;
}

void
bmi_balsa_decrement_nbref (
    ALGEB A)
{
  if (A && A->dynamic)
    A->nbref -= 1;
}

/*
 * The destructor of ALGEB. The bool careful is only present for debugging
 * purpose. If false, the function checks that everything gets actually freed.
 * 
 * The reference counter is decreased by the calling function.
 */

void
bmi_balsa_clear_ALGEB (
    void *A0)
{
  ALGEB A = (ALGEB) A0;
  struct bmi_balsa_list *L;
  struct bmi_balsa_table *T;
  ba0_int_p i;

  if (A != (ALGEB) 0 && A->dynamic)
    {
      assert (A->nbref >= 0);
      if (A->nbref == 0)
        {
          switch (A->type)
            {
            case bmi_balsa_function_object:
            case bmi_balsa_list_object:
              L = (struct bmi_balsa_list *) A->value;
              for (i = 0; i < L->size; i++)
                {
                  if (L->tab[i] && L->tab[i]->dynamic)
                    {
                      L->tab[i]->nbref -= 1;
                      bmi_balsa_clear_ALGEB (L->tab[i]);
                    }
                }
              free (L->tab);
              free (L);
              break;
            case bmi_balsa_string_object:
            case bmi_balsa_error_object:
              free ((char *) A->value);
              break;
            case bmi_balsa_table_object:
              T = (struct bmi_balsa_table *) A->value;
              free (T->ordering);
              free (T->equations);
              bmi_balsa_clear_ALGEB (T->notation);      /* jet0 notation */
              free (T);
              break;
            default:
              break;
            }
          free (A);
        }
    }
}

/*
 * Print a to the standard output. 
 *
 * For every ALGEB of type bmi_balsa_string_object, one looks for
 * its value in the environment.
 *
 * A mere place holder string is printed instead of tables.
 */

void
bmi_balsa_printf_ALGEB (
    ALGEB a)
{
  struct bmi_balsa_table *T;
  struct bmi_balsa_list *L;
  ba0_int_p i;

  if (a == (ALGEB) 0)
    return;

  switch (a->type)
    {
    case bmi_balsa_table_object:
      T = (struct bmi_balsa_table *) a->value;
      if (T->type == &dring)
        printf ("differential_ring");
      else if (T->type == &regchain)
        printf ("regular_differential_chain");
      else
        printf ("Denef_Lipshitz_uple");
      break;
    case bmi_balsa_function_object:
      L = (struct bmi_balsa_list *) a->value;
      bmi_balsa_printf_ALGEB (L->tab[0]);
      printf ("(");
      for (i = 1; i < L->size; i++)
        {
          if (i != 1)
            printf (", ");
          bmi_balsa_printf_ALGEB (L->tab[i]);
        }
      printf (")");
      break;
    case bmi_balsa_list_object:
      L = (struct bmi_balsa_list *) a->value;
      printf ("[");
      for (i = 1; i < L->size; i++)
        {
          if (i != 1)
            printf (", ");
          bmi_balsa_printf_ALGEB (L->tab[i]);
        }
      printf ("]");
      break;
    case bmi_balsa_bool_object:
      printf ((bool) a->value ? "true" : "false");
      break;
    case bmi_balsa_string_object:
      printf ("%s", (char *) a->value);
      break;
    case bmi_balsa_error_object:
      printf ("error %s", (char *) a->value);
      break;
    case bmi_balsa_integer_object:
      printf ("%ld", (long) a->value);
      break;
    }
}

/***********************************************************************
 * MAPLE fake functions
 *
 * The MKernelVector parameter is dummy.
 ***********************************************************************/

void
RTableGetDefaults (
    MKernelVector kv,
    RTableSettings *settings)
{
  kv = 0;
  settings = 0;
}

void *
RTableCreate (
    MKernelVector kv,
    RTableSettings *settings,
    ALGEB p,
    M_INT *bounds)
{
  kv = 0;
  settings = 0;
  bounds = 0;
  return p;
}

void *
RTableDataBlock (
    MKernelVector kv,
    ALGEB p)
{
  kv = 0;
  return p;
}

void *
MapleAlloc (
    MKernelVector kv,
    long size)
{
  void *res;

  kv = 0;
  res = (void *) malloc (size);
#if defined BALSA_DEBUG
  fprintf (stderr, "MapleAlloc: %lx (%ld)\n", (unsigned long int) res, size);
#endif
  return res;
}

void
MapleGcAllow (
    MKernelVector kv,
    ALGEB p)
{
  kv = 0;
  p = 0;
}

void
MapleDispose (
    MKernelVector kv,
    ALGEB p)
{
  kv = 0;
#if defined BALSA_DEBUG
  fprintf (stderr, "MapleDispose: %lx\n", (unsigned long int) p);
#endif
  free (p);
}

void
MapleGcProtect (
    MKernelVector kv,
    ALGEB p)
{
  kv = 0;
  p = 0;
}

void
MapleCheckInterrupt (
    MKernelVector kv)
{
  kv = 0;
}

static void *error_proc_data;
static bmi_balsa_error_proc *error_proc;

void
MaplePushErrorProc (
    MKernelVector kv,
    bmi_balsa_error_proc *err,
    void *data)
{
  kv = 0;
  error_proc = err;
  error_proc_data = data;
}

void
MaplePopErrorProc (
    MKernelVector kv)
{
  kv = 0;
}

/*
 * Comes from bmi_callback only.
 */

ALGEB
ToMapleName (
    MKernelVector kv,
    char *op,
    M_BOOL b)
{
  kv = 0;
  b = false;
  if (strcmp (op, "op") == 0)
    return &op_name;
  else if (strcmp (op, "nops") == 0)
    return &nops_name;
  else if (strcmp (op, BMI_IX_ordering) == 0)
    return &ordering_name;
  else if (strcmp (op, BMI_IX_equations) == 0)
    return &equations_name;
  else if (strcmp (op, BMI_IX_notation) == 0)
    return &notation_name;
  else
    {
      assert (strcmp (op, BMI_IX_type) == 0);
      return &type_name;
    }
}

/*
 * Comes from bmi_callback only, to encode k in « op (k, ...) ».
 * Used only as 4th parameter of EvalMapleProc.
 * Thus one does not need to create a struct bmi_balsa_object of type integer
 */

ALGEB
ToMapleInteger (
    MKernelVector kv,
    ba0_int_p k)
{
  kv = 0;
  return (void *) k;
}

/*
 * Used in conjunction with EvalMapleProc (nops) in bmi_callback, only.
 */

long
MapleToInteger32 (
    MKernelVector kv,
    ALGEB a)
{
  kv = 0;
  return (long) a;
}

ALGEB
EvalMapleProc (
    MKernelVector kv,
    ALGEB operator,
    int nargs,
    ...)
{
  struct bmi_balsa_list *list;
  ba0_int_p k;
  ALGEB res, operand;
  va_list arg;

  kv = 0;
  res = 0;

  va_start (arg, nargs);
  assert (operator-> type == bmi_balsa_string_object);
  if (operator == & op_name)
    {
      k = va_arg (arg, ba0_int_p);
      operand = va_arg (arg, ALGEB);
      if (k == 1 && operand->type == bmi_balsa_string_object)
        res = operand;
      else
        {
          assert (operand->type == bmi_balsa_list_object ||
              operand->type == bmi_balsa_function_object);
          list = (struct bmi_balsa_list *) operand->value;
          res = list->tab[k];
        }
    }
  else if (operator == & nops_name)
    {
      operand = va_arg (arg, ALGEB);
      assert (operand->type == bmi_balsa_list_object ||
          operand->type == bmi_balsa_function_object);
      list = (struct bmi_balsa_list *) operand->value;
/*
 * See above
 */
      res = (ALGEB) (list->size - 1);
    }
  va_end (arg);

  return res;
}

bool
IsMapleString (
    MKernelVector kv,
    ALGEB A)
{
  kv = 0;
  return A->type == bmi_balsa_string_object;
}

bool
IsMapleTable (
    MKernelVector kv,
    ALGEB A)
{
  kv = 0;
  return A->type == bmi_balsa_table_object;
}

bool
IsMapleName (
    MKernelVector kv,
    ALGEB A)
{
  kv = 0;
  return A->type == bmi_balsa_string_object;
}

bool
MapleToM_BOOL (
    MKernelVector kv,
    ALGEB A)
{
  bool b = true;

  kv = 0;
  if (A->type == bmi_balsa_string_object)
    {
      if (strcmp ((char *) A->value, "true") == 0)
        b = true;
      else if (strcmp ((char *) A->value, "false") == 0)
        b = false;
      else
        assert (false);
    }
  else if (A->type == bmi_balsa_bool_object)
    b = (bool) A->value;
  else
    assert (false);
  return b;
}

char *
MapleToString (
    MKernelVector kv,
    ALGEB A)
{
  kv = 0;
  assert (A->type == bmi_balsa_string_object);
  return (char *) A->value;
}

ALGEB
MapleTableSelect (
    MKernelVector kv,
    ALGEB table,
    ALGEB entry)
{
  ALGEB res;

  kv = 0;
  assert (table->type == bmi_balsa_table_object);
  if (entry == &type_name)
    res = ((struct bmi_balsa_table *) table->value)->type;
  else if (entry == &notation_name)
    res = ((struct bmi_balsa_table *) table->value)->notation;
  else if (entry == &ordering_name)
    res = ((struct bmi_balsa_table *) table->value)->ordering;
  else
    res = ((struct bmi_balsa_table *) table->value)->equations;
  return res;
}

/*
 * Quite a special function, with arglist being a null-terminated
 * array of ALGEB.
 */

long
MapleNumArgs (
    MKernelVector kv,
    ALGEB arglist)
{
  ALGEB *L;
  long num;

  kv = 0;
  L = (ALGEB *) arglist;
  num = 1;
  while (L[num] != (ALGEB) 0)
    num += 1;
  return num - 1;
}

/*
 * The error message comes from bmi_blad_eval.
 * It lies most of the time in bmi_mesgerr.
 * Otherwise, it is a conventional small error message.
 */

void
MapleRaiseError (
    MKernelVector kv,
    char *mesg)
{
  kv = 0;
  mesgerr = mesg;
}

/*
 * Used in exported functions, to build a result
 */

ALGEB
ToMapleBoolean (
    MKernelVector kv,
    long b)
{
  return bmi_balsa_new_ALGEB (bmi_balsa_bool_object, (ALGEB) b);
}

/*
 * Used in exported functions, to build a result.
 * Allocates one more ALGEB for null-terminating arrays (see MapleNumArgs)
 */

ALGEB
MapleListAlloc (
    MKernelVector kv,
    M_INT size)
{
  struct bmi_balsa_list *L;

  L = (struct bmi_balsa_list *) malloc (sizeof (struct bmi_balsa_list));
  assert (L != (struct bmi_balsa_list *) 0);
  L->tab = (ALGEB *) malloc ((size + 2) * sizeof (ALGEB));
  assert (L->tab != (ALGEB *) 0);
  memset (L->tab, 0, (size + 2) * sizeof (ALGEB));
  L->alloc = size + 2;
  L->size = size + 1;
  return bmi_balsa_new_ALGEB (bmi_balsa_list_object, L);
}

/*
 * list [index] := value
 */

void
MapleListAssign (
    MKernelVector kv,
    ALGEB list,
    M_INT index,
    ALGEB value)
{
  struct bmi_balsa_list *L;

  kv = 0;
  assert (list->type == bmi_balsa_list_object ||
      list->type == bmi_balsa_function_object);
  L = (struct bmi_balsa_list *) list->value;
  L->tab[index] = value;
  if (value && value->dynamic)
    value->nbref += 1;
}

/*
 * In DifferentialAlgebra, this is performed at the MAPLE level.
 * The behaviour is reproduced by looking at the output function
 */

static ALGEB
get_active_notation (
    void)
{
  ba0_printf_function *f;
  char *jet0_input_notation;

  bav_get_settings_variable (0, &f, &jet0_input_notation, 0, 0);

  if (f == &bav_printf_python_Derivative_variable)
    return &Derivative_notation;
  else if (f == &bav_printf_diff_variable)
    return &D_notation;
  else if (f == &bav_printf_jet_variable)
    return &jet_notation;
  else 
    {
      char str[BA0_BUFSIZE];
      ALGEB result;

      assert (f == &bav_printf_jet0_variable);

      sprintf (str, "jet(%s)", jet0_input_notation);
      result = bmi_balsa_new_string (str);
      return result;
    }
}

/*
 * In Maple/DifferentialAlgebra, tables are created at the MAPLE level
 */

static struct bmi_balsa_table *
new_table (
    ALGEB type,
    ALGEB ordering,
    ALGEB equations)
{
  struct bmi_balsa_table *T;

  T = (struct bmi_balsa_table *) malloc (sizeof (struct bmi_balsa_table));
  T->type = type;
  T->notation = get_active_notation ();
  T->ordering = ordering;
  T->equations = equations;
  return T;
}

ALGEB
bmi_balsa_new_differential_ring (
    ALGEB ordering)
{
  struct bmi_balsa_table *T;
  ALGEB O;

  T = new_table (&dring, ordering, (ALGEB) 0);
  O = bmi_balsa_new_ALGEB (bmi_balsa_table_object, T);
  return O;
}

ALGEB
bmi_balsa_new_regchain (
    ALGEB equations)
{
  struct bmi_balsa_table *T;
  ALGEB O;

  T = new_table (&regchain, (ALGEB) 0, equations);
  O = bmi_balsa_new_ALGEB (bmi_balsa_table_object, T);
  return O;
}

ALGEB
bmi_balsa_new_DLuple (
    ALGEB data)
{
  struct bmi_balsa_table *T;
  ALGEB O;

  T = new_table (&DLuple, (ALGEB) 0, data);
  O = bmi_balsa_new_ALGEB (bmi_balsa_table_object, T);
  return O;
}

