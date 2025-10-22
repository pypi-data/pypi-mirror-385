#include "bmi_callback.h"
#include "bmi_indices.h"
#include "bmi_gmp.h"

void
bmi_init_callback (
    struct bmi_callback *callback,
    MKernelVector kv)
{
  bmi_push_maple_gmp_allocators ();

  callback->kv = kv;
/*
 * Those names do not need to be protected.
 */
  callback->op = ToMapleName (kv, "op", (M_BOOL) true);
  callback->nops = ToMapleName (kv, "nops", (M_BOOL) true);
/*
 * The indices of the regchains. Those ones do need to be protected.
 */
  callback->ordering = ToMapleName (kv, BMI_IX_ordering, (M_BOOL) true);
  MapleGcProtect (callback->kv, callback->ordering);
  callback->equations = ToMapleName (kv, BMI_IX_equations, (M_BOOL) true);
  MapleGcProtect (callback->kv, callback->equations);
  callback->notation = ToMapleName (kv, BMI_IX_notation, (M_BOOL) true);
  MapleGcProtect (callback->kv, callback->notation);
  callback->type = ToMapleName (kv, BMI_IX_type, (M_BOOL) true);
  MapleGcProtect (callback->kv, callback->type);

  bmi_pull_maple_gmp_allocators ();

  callback->arg = (ALGEB) 0;
}

/*
 * Called from bmi_clear_callback
 * Called from bmi_interrupt if MAPLE11 || MAPLE12
 * ==> static function
 */

void
bmi_gc_allow_callback (
    struct bmi_callback *callback)
{
  MapleGcAllow (callback->kv, callback->ordering);
  MapleGcAllow (callback->kv, callback->equations);
  MapleGcAllow (callback->kv, callback->notation);
  MapleGcAllow (callback->kv, callback->type);
}

/*
 * Called from bmi_interrupt if MAPLE11 || MAPLE12
 * ==> to be removed
 */

void
bmi_gc_protect_callback (
    struct bmi_callback *callback)
{
  MapleGcProtect (callback->kv, callback->ordering);
  MapleGcProtect (callback->kv, callback->equations);
  MapleGcProtect (callback->kv, callback->notation);
  MapleGcProtect (callback->kv, callback->type);
}

/*
 * Destructor
 */

void
bmi_clear_callback (
    struct bmi_callback *callback)
{
  bmi_gc_allow_callback (callback);
  memset (callback, 0, sizeof (struct bmi_callback));
}

/*
 * This function sets the ALGEB over which the callback functions apply.
 */

void
bmi_set_callback_ALGEB (
    struct bmi_callback *callback,
    ALGEB arg)
{
  callback->arg = arg;
}

/*
 * The MAPLE nops function
 */

long
bmi_nops (
    struct bmi_callback *callback)
{
  ALGEB a;
  long result;

  bmi_push_maple_gmp_allocators ();
  a = EvalMapleProc (callback->kv, callback->nops, 1, callback->arg);
  MapleGcProtect (callback->kv, a);
  result = (long) MapleToInteger32 (callback->kv, a);
  MapleGcAllow (callback->kv, a);
  bmi_pull_maple_gmp_allocators ();
  return result;
}

/*
 * Returns true if op (k, callback) can be processed by MapleToString.
 * Actually, returns true if op (k, callback) is a string or a name.
 */

bool
bmi_is_string_op (
    long k,
    struct bmi_callback *callback)
{
  ALGEB a, b;
  bool result;

  bmi_push_maple_gmp_allocators ();
  b = ToMapleInteger (callback->kv, k);
  MapleGcProtect (callback->kv, b);
  a = EvalMapleProc (callback->kv, callback->op, 2, b, callback->arg);
/*
 * No need to protect since it should already be
 */
  result = IsMapleString (callback->kv, a) || IsMapleName (callback->kv, a);
  MapleGcAllow (callback->kv, b);
  bmi_pull_maple_gmp_allocators ();
  return result;
}

/*
 * Returns true if op (k, callback) is a table.
 */

bool
bmi_is_table_op (
    long k,
    struct bmi_callback *callback)
{
  ALGEB a, b;
  bool result;

  bmi_push_maple_gmp_allocators ();
  b = ToMapleInteger (callback->kv, k);
  MapleGcProtect (callback->kv, b);
  a = EvalMapleProc (callback->kv, callback->op, 2, b, callback->arg);
/*
 * No need to protect since it should already be.
 */
  result = (bool) IsMapleTable (callback->kv, a);
  MapleGcAllow (callback->kv, b);
  bmi_pull_maple_gmp_allocators ();
  return result;
}

/*
 * Returns true if op (k, callback) is a regchain.
 */

bool
bmi_is_regchain_op (
    long k,
    struct bmi_callback *callback)
{
  return bmi_is_table_op (k, callback) &&
      strcmp (bmi_table_type_op (k, callback), BMI_IX_regchain) == 0;
}

/*
 * Returns true if op (k, callback) is a dring.
 */

bool
bmi_is_dring_op (
    long k,
    struct bmi_callback *callback)
{
  return bmi_is_table_op (k, callback) &&
      strcmp (bmi_table_type_op (k, callback), BMI_IX_dring) == 0;
}

bool
bmi_bool_op (
    long k,
    struct bmi_callback *callback)
{
  ALGEB a, b;
  bool result;

  bmi_push_maple_gmp_allocators ();
  b = ToMapleInteger (callback->kv, k);
  MapleGcProtect (callback->kv, b);
  a = EvalMapleProc (callback->kv, callback->op, 2, b, callback->arg);
/*
 * No need to protect since it should already be.
 */
  result = (bool) MapleToM_BOOL (callback->kv, a);
  MapleGcAllow (callback->kv, b);
  bmi_pull_maple_gmp_allocators ();
  return result;
}

/*
 * It is assumed that op (k, callback) is a string.
 * Returns this operand as a C string.
 */

char *
bmi_string_op (
    long k,
    struct bmi_callback *callback)
{
  ALGEB a, b;
  char *result;

  bmi_push_maple_gmp_allocators ();
  b = ToMapleInteger (callback->kv, k);
  MapleGcProtect (callback->kv, b);
  a = EvalMapleProc (callback->kv, callback->op, 2, b, callback->arg);
/*
 * No need to protect a since it should already be.
 * I assume that string is part of a and is thus also protected.
 */
  result = MapleToString (callback->kv, a);
  MapleGcAllow (callback->kv, b);
  bmi_pull_maple_gmp_allocators ();
  return result;
}

/*
 * It is assumed that op (k, operand) is a table.
 * Converts the field entry of this table into a string and returns it.
 */

static char *
bmi_table_string_entry_op (
    long k,
    ALGEB Entry,
    struct bmi_callback *callback)
{
  ALGEB b, table, value;
  char *result;

  bmi_push_maple_gmp_allocators ();
  b = ToMapleInteger (callback->kv, k);
  MapleGcProtect (callback->kv, b);
  table = EvalMapleProc (callback->kv, callback->op, 2, b, callback->arg);
  value = MapleTableSelect (callback->kv, table, Entry);
/*
 * No need to protect table and value since they should already be.
 */
  result = MapleToString (callback->kv, value);
  MapleGcAllow (callback->kv, b);
  bmi_pull_maple_gmp_allocators ();
  return result;
}

/*
 * It is assumed that op (k, operand) is a table.
 * Returns the field entry of this table.
 */

static ALGEB
bmi_table_rtable_entry_op (
    long k,
    ALGEB Entry,
    struct bmi_callback *callback)
{
  ALGEB b, table;
  ALGEB result;

  bmi_push_maple_gmp_allocators ();
  b = ToMapleInteger (callback->kv, k);
  MapleGcProtect (callback->kv, b);
  table = EvalMapleProc (callback->kv, callback->op, 2, b, callback->arg);
  result = MapleTableSelect (callback->kv, table, Entry);
/*
 * No need to protect table and result since they should already be.
 */
  MapleGcAllow (callback->kv, b);
  bmi_pull_maple_gmp_allocators ();
  return result;
}

/*
 * It is assumed that op (k, callback) is a table.
 * Return the field Ordering of this table.
 */

char *
bmi_table_type_op (
    long k,
    struct bmi_callback *callback)
{
  return bmi_table_string_entry_op (k, callback->type, callback);
}

/*
 * It is assumed that op (k, callback) is a table.
 * Return the field Ordering of this table.
 */

ALGEB
bmi_table_ordering_op (
    long k,
    struct bmi_callback *callback)
{
  return bmi_table_rtable_entry_op (k, callback->ordering, callback);
}

/*
 * It is assumed that op (k, callback) is a table.
 * Return the field Equations of this table.
 */

ALGEB
bmi_table_equations_op (
    long k,
    struct bmi_callback *callback)
{
  return bmi_table_rtable_entry_op (k, callback->equations, callback);
}

/*
 * It is assumed that op (k, callback) is a table.
 * Return the field Notation of this table.
 */

char *
bmi_table_notation_op (
    long k,
    struct bmi_callback *callback)
{
  return bmi_table_string_entry_op (k, callback->notation, callback);
}
