#include "ba0_global.h"

BA0_DLL struct ba0_global ba0_global;

BA0_DLL struct ba0_initialized_global ba0_initialized_global = {
/*
 * common
 */
  {ba0_init_level, (void (*)(void)) 0, (time_t) 1, false},
/*
 * malloc
 */
  {false},
/*
 * stack
 */
  {BA0_SIZE_CELL_MAIN_STACK, BA0_SIZE_CELL_QUIET_STACK,
        BA0_SIZE_CELL_ANALEX_STACK, BA0_NB_CELLS_PER_STACK,
      BA0_SIZE_STACK_OF_STACK, &malloc, &free},
/*
 * gmp
 */
#if defined (BA0_USE_GMP)
  {&mp_set_memory_functions, (char *) 0},
#else
  {&bam_mp_set_memory_functions, (char *) 0},
#endif
/*
 * analex
 */
  {BA0_NBTOKENS, BA0_QUOTES},
/*
 * value
 */
  {BA0_POINT_OPER},
/*
 * range_indexed_group
 */
  {BA0_RANGE_INDEXED_GROUP_OPER, BA0_RANGE_INDEXED_GROUP_INFINITY, false, false}
};
