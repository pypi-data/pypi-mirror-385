#include "bmi_gmp.h"
#include "bmi_blad_eval.h"

#if ! defined (MAPLE11) && ! defined (MAPLE12)
#   undef BMI_DO_PUSH_MAPLE
#endif

static struct
{
  MKernelVector kv;
/*
 * MAPLE 11 and 12.
 * Implements a stack of GMP allocators.
 *
 * saved_alloc, saved_realloc, saved_free are the allocators
 * values when the stack is empty (can be maple or blad).
 *
 * sp is the stack pointer (the only needed information since
 * one only pushes maple allocators).
 */
  void *(
      *saved_alloc) (
      size_t);
  void *(
      *saved_realloc) (
      void *,
      size_t,
      size_t);
  void (
      *saved_free) (
      void *,
      size_t);
  ba0_int_p sp;
/*
 * For debugging purposes, a counter of calls to MaplePushGMPAllocators
 * MAPLE 13.
 */
  ba0_int_p maple_sp;
/*
 * The values of the MAPLE GMP allocators.
 * MAPLE 11, 12 and 13
 */
  void *(
      *maple_alloc) (
      size_t);
  void *(
      *maple_realloc) (
      void *,
      size_t,
      size_t);
  void (
      *maple_free) (
      void *,
      size_t);
} gmp;

/*
 * On Windows, BLAD is compiled with the __cdecl convention while 
 * MaplePushGMPAllocators expects the GMP_DECL convention.
 *
 * The following functions solve this problem.
 */

#if defined (_MSC_VER) && ! defined (MAPLE11) && ! defined (MAPLE12)

static void *GMP_DECL
bmi_ba0_gmp_alloc (
    size_t n)
{
  return ba0_gmp_alloc (n);
}

static void *GMP_DECL
bmi_ba0_gmp_realloc (
    void *old,
    size_t n,
    size_t m)
{
  return ba0_gmp_realloc (old, n, m);
}

static void GMP_DECL
bmi_ba0_gmp_free (
    void *old,
    size_t n)
{
  ba0_gmp_free (old, n);
}

#endif

/*
 * This function is called
 * - from bad_restart with alloc = the_BLAD_gmp_allocator
 * - from bad_terminate with alloc = the_MAPLE_gmp_allocator
 *
 * MAPLE 11, 12:
 *   just mp_set_memory_functions the allocators
 *
 * MAPLE 13: 
 *   In the first case, we MaplePush the allocator. In the second case
 *   we MaplePop it.
 */

static void
bmi_mp_set_memory_function (
    void *(*alloc) (size_t),
    void *(*realloc) (void *,
        size_t,
        size_t),
    void (*free) (void *,
        size_t))
{
#if ! defined (MAPLE11) && ! defined (MAPLE12) && ! defined (BMI_BALSA)
/*
    mytest (gmp.kv);
*/
  if (alloc == &ba0_gmp_alloc)
    {
      gmp.maple_sp += 1;
#   if defined (_MSC_VER)
      MaplePushGMPAllocators (gmp.kv, &bmi_ba0_gmp_alloc,
          &bmi_ba0_gmp_realloc, &bmi_ba0_gmp_free);
#   else
      MaplePushGMPAllocators (gmp.kv, alloc, realloc, free);
#   endif
      bmi_check_blad_gmp_allocators (__FILE__, __LINE__);
    }
  else
    {
      MaplePopGMPAllocators (gmp.kv);
      bmi_check_maple_gmp_allocators (__FILE__, __LINE__);
      gmp.maple_sp -= 1;
#   if defined BMI_MEMCHECK
      if (gmp.maple_sp < 0)
        {
          fprintf (stderr, "bmi fatal error: MAPLE stack underflow\n");
          exit (1);
        }
#   endif
    }
#else
  ba0_mp_set_memory_functions (alloc, realloc, free);
#endif
}

void
bmi_check_blad_gmp_allocators (
    char *f,
    int l)
{
#if defined (BMI_MEMCHECK)
#   if defined (MAPLE11) || defined (MAPLE12) || defined (BMI_BALSA)
  void *(
      *blad_alloc) (
      size_t);
  void *(
      *blad_realloc) (
      void *,
      size_t,
      size_t);
  void (
      *blad_free) (
      void *,
      size_t);

  ba0_mp_get_memory_functions (&blad_alloc, &blad_realloc, &blad_free);

  if (gmp.sp != 0 || blad_alloc != &ba0_gmp_alloc)
    {
      fprintf (stderr, "bmi fatal error: BLAD gmp allocators expected\n");
      fprintf (stderr, "file %s, line %d\n", f, l);
      fprintf (stderr, "actual = %lx, blad = %lx, maple = %lx\n",
          (unsigned long) blad_alloc,
          (unsigned long) &ba0_gmp_alloc, (unsigned long) gmp.maple_alloc);
      fprintf (stderr, "gmp.sp = %ld\n", (long int) gmp.sp);
      exit (1);
    }
#   else
  ba0_mpz_t x;

  ba0_global.gmp.gmp_alloc_function_called = false;
  ba0_mpz_init_set_ui (x, 1);

  if (gmp.sp != 0 || ba0_global.gmp.gmp_alloc_function_called == false)
    {
      fprintf (stderr, "bmi fatal error: BLAD gmp allocators expected\n");
      fprintf (stderr, "file %s, line %d\n", f, l);
      fprintf (stderr, "gmp.sp = %d\n", (int) gmp.sp);
      exit (1);
    }

  ba0_mpz_clear (x);
#   endif
#endif
  f = (char *) 0;
  l = 0;
}

void
bmi_check_maple_gmp_allocators (
    char *f,
    int l)
{
#if defined (BMI_MEMCHECK)
#   if defined (MAPLE11) || defined (MAPLE12) || defined (BMI_BALSA)
  void *(
      *maple_alloc) (
      size_t);
  void *(
      *maple_realloc) (
      void *,
      size_t,
      size_t);
  void (
      *maple_free) (
      void *,
      size_t);

  ba0_mp_get_memory_functions (&maple_alloc, &maple_realloc, &maple_free);

  if (maple_alloc != gmp.maple_alloc)
    {
      fprintf (stderr, "bmi fatal error: MAPLE gmp allocators expected\n");
      fprintf (stderr, "file %s, line %d\n", f, l);
      exit (1);
    }
#   else
  ba0_mpz_t x;

  ba0_global.gmp.gmp_alloc_function_called = false;
  ba0_mpz_init_set_ui (x, 1);

  if (ba0_global.gmp.gmp_alloc_function_called)
    {
      fprintf (stderr, "bmi fatal error: MAPLE gmp allocators expected\n");
      fprintf (stderr, "file %s, line %d\n", f, l);
      exit (1);
    }

  ba0_mpz_clear (x);
#   endif
#endif
  f = (char *) 0;
  l = 0;
}

void
bmi_check_gmp_sp (
    void)
{
#if defined (BMI_MEMCHECK)
  if (gmp.sp != 0 || gmp.maple_sp != 0)
    {
      fprintf (stderr, "bmi fatal error: non empty GMP stacks\n");
      exit (1);
    }
#endif
}

/*
 * Must be called before restarting BLAD
 */

void
bmi_init_gmp_allocators_management (
    MKernelVector kv)
{
  char *Integer_PFE;

  gmp.kv = kv;
  ba0_get_settings_gmp (0, &Integer_PFE);
  ba0_set_settings_gmp (&bmi_mp_set_memory_function, Integer_PFE);
  ba0_mp_get_memory_functions
      (&gmp.maple_alloc, &gmp.maple_realloc, &gmp.maple_free);
  gmp.sp = 0;
  gmp.maple_sp = 0;
}

/*
 * Implementation of a stack of gmp_allocators.
 * The only pushed allocators are those of MAPLE.
 * Thus one only needs to implement the stack pointer ... with no stack.
 */

void
bmi_push_maple_gmp_allocators (
    void)
{
#if defined (MAPLE11) || defined (MAPLE12) || defined (BMI_BALSA)
  if (gmp.sp == 0)
    {
      ba0_mp_get_memory_functions
          (&gmp.saved_alloc, &gmp.saved_realloc, &gmp.saved_free);
      ba0_mp_set_memory_functions
          (gmp.maple_alloc, gmp.maple_realloc, gmp.maple_free);
    }
#else
  if (gmp.sp == 0)
    {
      gmp.maple_sp += 1;
#   if defined (BMI_DO_PUSH_MAPLE)
      MaplePushGMPAllocators
          (gmp.kv, gmp.maple_alloc, gmp.maple_realloc, gmp.maple_free);
#   endif
    }
#endif
  gmp.sp += 1;
}

void
bmi_pull_maple_gmp_allocators (
    void)
{
  gmp.sp -= 1;
#if defined (BMI_MEMCHECK)
  if (gmp.sp < 0)
    {
      fprintf (stderr, "bmi fatal error: GMP stack underflow\n");
      exit (1);
    }
#endif
#if defined (MAPLE11) || defined (MAPLE12) || defined (BMI_BALSA)
  if (gmp.sp == 0)
    ba0_mp_set_memory_functions
        (gmp.saved_alloc, gmp.saved_realloc, gmp.saved_free);
#else
  if (gmp.sp == 0)
    {
#   if defined (BMI_DO_PUSH_MAPLE)
      MaplePopGMPAllocators (gmp.kv);
#   endif
      gmp.maple_sp -= 1;
#   if defined (BMI_MEMCHECK)
      if (gmp.maple_sp < 0)
        {
          fprintf (stderr, "bmi fatal error: MAPLE stack underflow\n");
          exit (1);
        }
#   endif
    }
#endif
}

/*
 * The next functions are only called by bmi_interrupt.
 */

void
bmi_push_blad_gmp_allocators (
    void)
{
#if defined (MAPLE11) || defined (MAPLE12) || defined (BMI_BALSA)
  ba0_mp_set_memory_functions (&ba0_gmp_alloc, &ba0_gmp_realloc, &ba0_gmp_free);
#else
  gmp.maple_sp += 1;
#   if defined (_MSC_VER)
  MaplePushGMPAllocators
      (gmp.kv, &bmi_ba0_gmp_alloc, &bmi_ba0_gmp_realloc, &bmi_ba0_gmp_free);
#   else
  MaplePushGMPAllocators
      (gmp.kv, &ba0_gmp_alloc, &ba0_gmp_realloc, &ba0_gmp_free);
#   endif
#endif
}

void
bmi_pull_blad_gmp_allocators (
    void)
{
#if defined (MAPLE11) || defined (MAPLE12) || defined (BMI_BALSA)
  ba0_mp_set_memory_functions
      (gmp.maple_alloc, gmp.maple_realloc, gmp.maple_free);
#else
  MaplePopGMPAllocators (gmp.kv);
  gmp.maple_sp -= 1;
#   if defined (BMI_MEMCHECK)
  if (gmp.maple_sp < 0)
    {
      fprintf (stderr, "bmi fatal error: MAPLE stack underflow\n");
      exit (1);
    }
#   endif
#endif
}
