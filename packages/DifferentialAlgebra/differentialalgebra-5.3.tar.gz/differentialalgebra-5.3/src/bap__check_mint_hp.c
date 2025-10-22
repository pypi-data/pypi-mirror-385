#include "bap_polynom_mint_hp.h"
#include "bap__check_mint_hp.h"

#define BAD_FLAG_mint_hp

BAP_DLL void
bap__check_ordering_mint_hp (
    struct bap_polynom_mint_hp *A)
{
#if defined (BA0_HEAVY_DEBUG)
  ba0_int_p i;

  for (i = 1; i < A->total_rank.size; i++)
    if (bav_variable_number (A->total_rank.rg[i - 1].var) <=
        bav_variable_number (A->total_rank.rg[i].var))
      BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (A->clot != (struct bap_clot_mint_hp *) 0
      && ba0_which_stack (A->clot) == (struct ba0_stack *) 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
#else
  A = (struct bap_polynom_mint_hp *) 0;
#endif
}

#if defined (BA0_HEAVY_DEBUG)
static void
bap__check_compatible_ordering_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B)
{
  bap__check_ordering_mint_hp (A);
  bap__check_ordering_mint_hp (B);
}
#endif

BAP_DLL void
bap__check_compatible_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B)
{
#if defined (BA0_HEAVY_DEBUG)
  bap__check_compatible_ordering_mint_hp (A, B);
#else
  A = (struct bap_polynom_mint_hp *) 0;
  B = (struct bap_polynom_mint_hp *) 0;
#endif
}

#undef BAD_FLAG_mint_hp
