#include "bmi_blad_eval.h"
#include "bmi_memory.h"
#include "bmi_gmp.h"

/*
 * Hacked from MAPLE
 */

#define BMI_POINTER_TO_BINARY(p) ((ALGEB)((void**)(p)-1))
#define BMI_BINARY_DATA_BLOCK(a) ((void**)(a)+1)


static struct bmi_memory
{
/*
 * areas = a table containing the allocated cells of BLAD.
 *
 * This table and its elements are MAPLE BINARY DAGS, allocated
 * using MapleAlloc and, then, converted to BINARY DAGS by means
 * of BMI_POINTER_TO_BINARY.
 */
  ba0_int_p alloc;
  ba0_int_p size;
  ALGEB areas;
/*
 * For debugging purposes, a counter of calls to MaplePushErrorProc
 * MAPLE 13.
 */
  ba0_int_p maple_sp;

  MKernelVector kv;
  struct bmi_callback callback; /* The only existing callback structure */
} mem;

/*
 * The content of areas is Disposed.
 * Observe that MapleGcAllow applies to the BINARY, while,
 *              MapleDispose applies to the DATA_BLOCK.
 * To be called, rather than bmi_gc_allow_memory, when Maple raises
 * an "out of memory" exception.
 */

static void
bmi_gc_dispose_memory (
    void)
{
  ALGEB p_handle;
  void **p;
  long i;

  p_handle = mem.areas;
  p = BMI_BINARY_DATA_BLOCK (p_handle);
  for (i = 0; i < mem.size; i++)
    {
      ALGEB a = (ALGEB) BMI_BINARY_DATA_BLOCK (p[i]);
      MapleDispose (mem.kv, a);
    }
  if (p_handle)
    MapleDispose (mem.kv, (ALGEB) p);
}

#if defined (BMI_MAPLE)

/*
 * The content of areas is GcAllowed
 */

static void
bmi_gc_allow_memory (
    void)
{
  ALGEB p_handle;
  void **p;
  long i;

  p_handle = mem.areas;
  p = BMI_BINARY_DATA_BLOCK (p_handle);
  for (i = 0; i < mem.size; i++)
    MapleGcAllow (mem.kv, p[i]);
  if (p_handle)
    MapleGcAllow (mem.kv, p_handle);
}

#endif

#if defined (MAPLE11) || defined (MAPLE12)

/*
 * The content of areas is GcProtected
 */

static void
bmi_gc_protect_memory (
    void)
{
  ALGEB p_handle;
  void **p;
  long i;

  p_handle = mem.areas;
  p = BMI_BINARY_DATA_BLOCK (p_handle);
  for (i = 0; i < mem.size; i++)
    MapleGcProtect (mem.kv, p[i]);
  if (p_handle)
    MapleGcProtect (mem.kv, p_handle);
}

#endif

/*
 * BLAD ba0_malloc points to this one.
 * The allocated piece of memory is stored in areas.
 *
 * It can be called while the BLAD GMP allocators are not yet set.
 *
 * If there is no memory available, then MapleAlloc does not return
 * but raises an exception. The formerly allocated cells are given back 
 * to MAPLE by the function provided as a parameter to MaplePushErrorProc
 * i.e. bmi_error_proc. Of course, this does not work on MAPLE 11 and 12.
 */

static void *
bmi_malloc (
    size_t n)
{
  void **m, **p;
  ALGEB m_handle, p_handle;
  size_t new_n;
  MKernelVector kv = mem.kv;
/*
    fprintf (stderr, "bmi_malloc (%d)\n", n);

    bmi_check_blad_gmp_allocators (__FILE__, __LINE__);
    bmi_push_maple_gmp_allocators ();
 */
  if (mem.size == mem.alloc)
    {
      new_n = (size_t) (2 * mem.size + 1);
      m = (void **) MapleAlloc (kv, new_n * sizeof (void *));
      m_handle = BMI_POINTER_TO_BINARY (m);
      MapleGcProtect (kv, m_handle);
      if (mem.areas)
        {
          p_handle = mem.areas;
          p = BMI_BINARY_DATA_BLOCK (p_handle);
          memcpy (m, p, (size_t) (mem.size * sizeof (void *)));
#if defined (BMI_MAPLE)
          MapleGcAllow (kv, p_handle);
#else
          MapleDispose (kv, (ALGEB) p);
#endif
        }
      mem.areas = m_handle;
      mem.alloc = new_n;
    }
  p_handle = mem.areas;
  p = BMI_BINARY_DATA_BLOCK (p_handle);
  m = (void **) MapleAlloc (kv, n);
  m_handle = BMI_POINTER_TO_BINARY (m);
  MapleGcProtect (kv, m_handle);
  p[mem.size] = m_handle;
  mem.size += 1;
/*
    bmi_pull_maple_gmp_allocators ();
    bmi_check_blad_gmp_allocators (__FILE__, __LINE__);
 */
  return m;
}

/*
 * Do not Dispose. 
 */

static void
bmi_free (
    void *p)
{
  p = 0;                        /* to avoid a warning */
}

/*
 * This function is called every second by the BLAD libraries.
 * It checks if the user pressed control-C.
 *
 * On MAPLE 11, 12 the call to MapleCheckInterrupt does not return so that
 * - all the memory used by the BLAD library must be gc-allowed
 * - the GMP memory functions must be restored (to the MAPLE ones).
 *
 * On MAPLE 13, bmi_error_proc is called.
 */

static void
bmi_interrupt (
    void)
{
  bmi_check_blad_gmp_allocators (__FILE__, __LINE__);
  bmi_pull_blad_gmp_allocators ();

#if defined (MAPLE11) || defined (MAPLE12)
  bmi_gc_allow_callback (&mem.callback);
  bmi_gc_allow_memory ();
  MapleCheckInterrupt (mem.kv);
  bmi_gc_protect_memory ();
  bmi_gc_protect_callback (&mem.callback);
#else
  MapleCheckInterrupt (mem.kv);
#endif

  bmi_push_blad_gmp_allocators ();
  bmi_check_blad_gmp_allocators (__FILE__, __LINE__);
}

#if ! defined (MAPLE11) && ! defined (MAPLE12)

/*
 * MAPLE 13
 *
 * This function is called when the user strikes control-C or when
 * MapleAlloc raises an "out of memory" exception.
 */

static void M_DECL
bmi_error_proc (
    char *mesg,
    void *data)
{
#   if defined (MAPLE13)
/*
 * The following test provokes a recursive call to bmi_error_proc in MAPLE14
 */
  bmi_check_maple_gmp_allocators (__FILE__, __LINE__);
#   endif

  bmi_clear_callback (&mem.callback);
  bmi_gc_dispose_memory ();

  memset (&mem, 0, sizeof (struct bmi_memory));

  mesg = (char *) 0;
  data = (void *) 0;
}

#endif

/*
 * Constructor of mem.
 */

struct bmi_callback *
bmi_init_memory (
    MKernelVector kv)
{
  memset (&mem, 0, sizeof (struct bmi_memory));

  bmi_init_gmp_allocators_management (kv);

  mem.kv = kv;
  bmi_init_callback (&mem.callback, kv);
/*
 * Redirection of ba0_malloc and ba0_free.
 */
  ba0_set_settings_memory_functions (&bmi_malloc, &bmi_free);
/*
 * Redirection of the BLAD check interrupt function.
 */
  ba0_set_settings_interrupt (&bmi_interrupt, 1);

  mem.maple_sp = 0;
#if ! defined (MAPLE11) && ! defined (MAPLE12)
  MaplePushErrorProc (kv, (void (*)(const char *,
              void *)) &bmi_error_proc, (void *) 0);
  mem.maple_sp += 1;
#endif

  return &mem.callback;
}

/*
 * Destructor. Called when bmi_blad_eval exits.
 */

void
bmi_clear_memory (
    void)
{
#if ! defined (MAPLE11) && ! defined (MAPLE12)
  MaplePopErrorProc (mem.kv);
  mem.maple_sp -= 1;
#endif
  bmi_clear_callback (&mem.callback);

#if defined (BMI_MAPLE)
  bmi_gc_allow_memory ();
#else
  bmi_gc_dispose_memory ();
#endif
  memset (&mem, 0, sizeof (struct bmi_memory));
}

void
bmi_check_error_sp (
    void)
{
#if defined (BMI_MEMCHECK)
  if (mem.maple_sp != 0)
    {
      fprintf (stderr, "bmi fatal error: non empty error stack\n");
      exit (1);
    }
#endif
}
