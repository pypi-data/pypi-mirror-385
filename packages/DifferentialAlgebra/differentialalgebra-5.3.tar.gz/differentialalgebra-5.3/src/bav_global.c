#include "bav_global.h"
#include "bav_symbol.h"
#include "bav_variable.h"
#include "bav_rank.h"

BAV_DLL struct bav_global bav_global;

BAV_DLL struct bav_initialized_global bav_initialized_global = {
/*
 * common
 */
  {&bav_unknown_default},
/*
 * symbol
 */
  {&bav_scanf_default_symbol, &bav_printf_default_symbol, (char *) 0},
/*
 * parameter
 */
  {(char *) 0},
/*
 * variable
 */
  {&bav_scanf_jet_variable, &bav_printf_jet_variable,
      BAV_JET0_INPUT_STRING, BAV_JET0_OUTPUT_STRING, BAV_TEMP_STRING},
/*
 * rank
 */
  {&bav_printf_default_rank},
/*
 * ordering
 */
  {"ordering"}
};
