#include "blad.h"
#include "bmi_gmp.h"
#include "bmi_rtable.h"

/***********************************************************************
 * Management of data stored in MAPLE rtables
 *
 * First creation of rtables
 ***********************************************************************/

/*
 * Create an empty rtable with data block of size bytes
 */

static ALGEB
bmi_empty_rtable (
    MKernelVector kv,
    ba0_int_p size)
{
  RTableSettings bmi_table_settings;
  void *cell;
  M_INT bmi_bounds[2];
  ALGEB res;

  bmi_push_maple_gmp_allocators ();

  cell = MapleAlloc (kv, (long) size);

  RTableGetDefaults (kv, &bmi_table_settings);
  bmi_table_settings.data_type = RTABLE_INTEGER32;
  bmi_table_settings.order = RTABLE_C;
  bmi_table_settings.read_only = true;
  bmi_table_settings.num_dimensions = 1;
  bmi_bounds[0] = 0;
  bmi_bounds[1] = (M_INT) (size / sizeof (UINTEGER32) - 1);
  res = RTableCreate (kv, &bmi_table_settings, cell, bmi_bounds);

  bmi_pull_maple_gmp_allocators ();

  return res;
}

/*
 * Create a rtable involving
 *
 * A struct ba0_table * T of 2 elements.
 * T[0] = a struct bav_differential_ring * 
 * T[1] used to be for parameters
 */

ALGEB
bmi_rtable_differential_ring (
    MKernelVector kv,
    char *f,
    int l)
{
  struct ba0_stack H;
  struct ba0_table *T;
  ba0_int_p size;
  void *res, *cell;
/*
 * Though actually not important here
 */
  bmi_check_blad_gmp_allocators (f, l);

  T = ba0_new_table ();
  ba0_realloc_table (T, 2);
  T->size = 2;

  size = ba0_sizeof_table (T, ba0_isolated);
  size += bav_sizeof_differential_ring (&bav_global.R, ba0_isolated);

  res = bmi_empty_rtable (kv, size);

  cell = RTableDataBlock (kv, (ALGEB) res);
  ba0_init_one_cell_stack (&H, "maple", cell, size);
  ba0_push_stack (&H);

  T = ba0_new_table ();
  ba0_realloc_table (T, 2);
  T->size = 2;

  T->tab[0] = bav_new_differential_ring ();
  bav_R_set_differential_ring ((struct bav_differential_ring *) T->tab[0],
      &bav_global.R);

  ba0_pull_stack ();
  ba0_clear_one_cell_stack (&H);

  return res;
}

/*
 * Create a rtable involving
 *
 * A struct ba0_table * T of 3 elements
 * T[0] = a struct bav_differential_ring *
 * T[1] used to be for parameters
 * T[2] = a struct bad_regchain *
 */

ALGEB
bmi_rtable_regchain (
    MKernelVector kv,
    struct bad_regchain *C,
    char *f,
    int l)
{
  struct ba0_stack H;
  struct ba0_table *T;
  ba0_int_p size;
  void *res, *cell;

  bmi_check_blad_gmp_allocators (f, l);

  T = ba0_new_table ();
  ba0_realloc_table (T, 3);
  T->size = 3;
/*
  {
    struct ba0_mark M, A, B;
    struct ba0_stack *H;
    ba0_int_p size, other_size;
    struct bav_differential_ring *R;
    size = bav_sizeof_differential_ring (&bav_global.R, ba0_isolated);
    ba0_record (&M);
    H = ba0_current_stack ();
    ba0_alloc (H->free.memory_left);
    ba0_record (&A);
    R = bav_new_differential_ring ();
    bav_R_set_differential_ring (R, &bav_global.R);
    ba0_record (&B);
    other_size = ba0_range_mark (&A, &B);
    if (size != other_size)
      BA0_RAISE_EXCEPTION (BA0_ERRALG);
    ba0_restore (&M);
  }
 */
  size = ba0_sizeof_table (T, ba0_isolated);
  size += bav_sizeof_differential_ring (&bav_global.R, ba0_isolated);
  size += bad_sizeof_regchain (C, ba0_isolated);

  res = bmi_empty_rtable (kv, size + 0);
  cell = RTableDataBlock (kv, (ALGEB) res);

  ba0_init_one_cell_stack (&H, "maple", cell, size + 0);
  ba0_push_stack (&H);

  T = ba0_new_table ();
  ba0_realloc_table (T, 3);
  T->size = 3;
/*
 * FIX ME.
 * Temporarily, the number of allocated bytes exceeds the size of the data
 */
  T->tab[2] = bad_new_regchain ();
  bad_set_regchain ((struct bad_regchain *) T->tab[2], C);

  T->tab[0] = bav_new_differential_ring ();
  bav_R_set_differential_ring ((struct bav_differential_ring *) T->tab[0],
      &bav_global.R);

  bad_switch_ring_regchain
      ((struct bad_regchain *) T->tab[2],
      (struct bav_differential_ring *) T->tab[0]);

  ba0_pull_stack ();

  ba0_clear_one_cell_stack (&H);

  return res;
}

/*
 * Create a rtable involving
 *
 * A struct ba0_table * T of 2 elements
 * T[0] = a struct bav_differential_ring *
 * T[1] = a struct bas_DLuple *
 */

ALGEB
bmi_rtable_DLuple (
    MKernelVector kv,
    struct bas_DLuple *DL,
    char *f, 
    int l)
{
  struct ba0_stack H;
  struct ba0_table *T;
  ba0_int_p size;
  void *res, *cell;

  bmi_check_blad_gmp_allocators (f, l);

  T = ba0_new_table ();
  ba0_realloc_table (T, 2);
  T->size = 2;

  size = ba0_sizeof_table (T, ba0_isolated);
  size += bav_sizeof_differential_ring (&bav_global.R, ba0_isolated);
  size += bas_sizeof_DLuple (DL, ba0_isolated);

  res = bmi_empty_rtable (kv, size + 0);
  cell = RTableDataBlock (kv, (ALGEB) res);

  ba0_init_one_cell_stack (&H, "maple", cell, size + 0);
  ba0_push_stack (&H);

  T = ba0_new_table ();
  ba0_realloc_table (T, 2);
  T->size = 2;
/*
 * FIX ME.
 * Temporarily, the number of allocated bytes exceeds the size of the data
 */
  T->tab[1] = bas_new_DLuple ();
  bas_set_DLuple ((struct bas_DLuple *) T->tab[1], DL);

  T->tab[0] = bav_new_differential_ring ();
  bav_R_set_differential_ring ((struct bav_differential_ring *) T->tab[0],
      &bav_global.R);

  bas_switch_ring_DLuple
      ((struct bas_DLuple *) T->tab[1],
      (struct bav_differential_ring *) T->tab[0]);

  ba0_pull_stack ();

  ba0_clear_one_cell_stack (&H);

  return res;
}

/***********************************************************************
 * Management of data stored in MAPLE rtables
 *
 * Second extracting information from rtables
 ***********************************************************************/

/*
 * op (k, callback) is a MAPLE table.
 * This tables may either be a DifferentialRing or a RegularChain.
 *
 * Extracts a rtable from this table (entry Ordering/Equations)
 * This rtable was created by bmi_rtable_ordering or bmi_rtable_regchain
 *
 * Load the struct bav_differential_ring * and the struct bav_tableof_parameter * that
 * it contains. The current ordering is returned.
 */

bav_Iordering
bmi_set_ordering (
    long k,
    struct bmi_callback *callback,
    char *f,
    int l)
{
  struct bav_differential_ring *R;
//  struct bav_tableof_parameter *P;
  bav_Iordering r;
  struct ba0_table *T;
  ALGEB rtable;

  bmi_check_blad_gmp_allocators (f, l);

  if (bmi_is_regchain_op (k, callback))
    rtable = bmi_table_equations_op (k, callback);
  else
    rtable = bmi_table_ordering_op (k, callback);

  bmi_push_maple_gmp_allocators ();
  T = (struct ba0_table *) RTableDataBlock (callback->kv, rtable);
  bmi_pull_maple_gmp_allocators ();

  R = (struct bav_differential_ring *) T->tab[0];
//  P = (struct bav_tableof_parameter *) T->tab[1];
  ba0_push_stack (&ba0_global.stack.quiet);
  bav_R_set_differential_ring (&bav_global.R, R);
  ba0_pull_stack ();
  r = bav_current_ordering ();
  return r;
}

/*
 * op (k, callback) is a MAPLE table.
 * It is a RegularChain.
 *
 * Extracts a rtable from this table (entry Equations)
 * This rtable was created by bmi_rtable_regchain
 *
 * Load the struct bav_differential_ring *
 * and the  struct bad_regchain * 
 * that it contains. 
 *
 * The current ordering is returned.
 */

bav_Iordering
bmi_set_ordering_and_regchain (
    struct bad_regchain *C,
    long k,
    struct bmi_callback *callback,
    char *f,
    int l)
{
  struct bav_differential_ring *R;
  struct bad_regchain *D;
  bav_Iordering r;
  struct ba0_table *T;
  ALGEB rtable;

  bmi_check_blad_gmp_allocators (f, l);

  rtable = bmi_table_equations_op (k, callback);

  bmi_push_maple_gmp_allocators ();
  T = (struct ba0_table *) RTableDataBlock (callback->kv, rtable);
  bmi_pull_maple_gmp_allocators ();

  R = (struct bav_differential_ring *) T->tab[0];
  D = (struct bad_regchain *) T->tab[2];

  ba0_push_stack (&ba0_global.stack.quiet);
  bav_R_set_differential_ring (&bav_global.R, R);
  ba0_pull_stack ();
  r = bav_current_ordering ();
  bad_init_regchain (C);
  bad_set_regchain (C, D);
  bad_switch_ring_regchain (C, &bav_global.R);
  return r;
}

/*
 * op (k, callback) is a MAPLE table.
 * It is a DenefLipshitzUple
 *
 * Extracts a rtable from this table 
 * This rtable was created by bmi_rtable_DLuple
 *
 * Load the struct bav_differential_ring *
 * and the  struct bas_DLuple * 
 * that it contains. 
 *
 * The current ordering is returned.
 */

bav_Iordering
bmi_set_ordering_and_DLuple (
    struct bas_DLuple *DL,
    long k,
    struct bmi_callback *callback,
    char *f,
    int l)
{
  struct bav_differential_ring *R;
  struct bas_DLuple *DM;
  bav_Iordering r;
  struct ba0_table *T;
  ALGEB rtable;

  bmi_check_blad_gmp_allocators (f, l);

  rtable = bmi_table_equations_op (k, callback);

  bmi_push_maple_gmp_allocators ();
  T = (struct ba0_table *) RTableDataBlock (callback->kv, rtable);
  bmi_pull_maple_gmp_allocators ();

  R = (struct bav_differential_ring *) T->tab[0];
  DM = (struct bas_DLuple *) T->tab[1];

  ba0_push_stack (&ba0_global.stack.quiet);
  bav_R_set_differential_ring (&bav_global.R, R);
  ba0_pull_stack ();
  r = bav_current_ordering ();
  bas_init_DLuple (DL);
  bas_set_DLuple (DL, DM);
  bas_switch_ring_DLuple (DL, &bav_global.R);
  return r;
}

/*
 * op (k, callback) ... op (nops (callback), callback) are MAPLE tables.
 * They are RegularChain.
 *
 * Extracts the rtables from these tables (entries Equations)
 * These rtables were created by bmi_rtable_regchain
 *
 * Load the struct bav_differential_ring * 
 * from the first rtable.
 *
 * Load the struct bad_regchain *(s) from each rtable.
 *
 * The current ordering is returned.
 */

bav_Iordering
bmi_set_ordering_and_intersectof_regchain (
    struct bad_intersectof_regchain *tabC,
    long k,
    struct bmi_callback *callback,
    char *f,
    int l)
{
  struct bav_differential_ring *R;
  struct bad_regchain *D;
  bav_Iordering r;
  struct ba0_table *T;
  ALGEB rtable;
  ba0_int_p i, nops;

  bmi_check_blad_gmp_allocators (f, l);

  rtable = bmi_table_equations_op (k, callback);

  bmi_push_maple_gmp_allocators ();
  T = (struct ba0_table *) RTableDataBlock (callback->kv, rtable);
  bmi_pull_maple_gmp_allocators ();
/*
 * The differential ring
 */
  R = (struct bav_differential_ring *) T->tab[0];

  ba0_push_stack (&ba0_global.stack.quiet);
  bav_R_set_differential_ring (&bav_global.R, R);
  ba0_pull_stack ();

  r = bav_current_ordering ();
/*
 * The regular chains
 */
  nops = bmi_nops (callback);

  bad_init_intersectof_regchain (tabC);
  bad_realloc_intersectof_regchain (tabC, nops - k + 1);

  for (i = k; i <= nops; i++)
    {
      rtable = bmi_table_equations_op (i, callback);

      bmi_push_maple_gmp_allocators ();
      T = (struct ba0_table *) RTableDataBlock (callback->kv, rtable);
      bmi_pull_maple_gmp_allocators ();

      D = (struct bad_regchain *) T->tab[2];
      bad_set_regchain (tabC->inter.tab[tabC->inter.size], D);
      bad_switch_ring_regchain (tabC->inter.tab[tabC->inter.size],
          &bav_global.R);
      tabC->inter.size += 1;
    }

  bad_set_attchain (&tabC->attrib, &tabC->inter.tab[0]->attrib);
  return r;
}
