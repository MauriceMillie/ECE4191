// generated using template: cop_main.template---------------------------------------------
/******************************************************************************************
**
**  Module Name: cop_main.c
**  NOTE: Automatically generated file. DO NOT MODIFY!
**  Description:
**            Main file
**
******************************************************************************************/
// generated using template: arm/custom_include.template-----------------------------------


#ifdef __cplusplus
#include <limits>

extern "C" {
#endif

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <complex.h>
#include <time.h>
#include <stdarg.h>

// x86 libraries:
#include "../include/sp_functions_dev0.h"


#ifdef __cplusplus
}
#endif


// ----------------------------------------------------------------------------------------                // generated using template:generic_macros.template-----------------------------------------
/*********************** Macros (Inline Functions) Definitions ***************************/

// ----------------------------------------------------------------------------------------

#ifndef MAX
#define MAX(value, limit) (((value) > (limit)) ? (value) : (limit))
#endif
#ifndef MIN
#define MIN(value, limit) (((value) < (limit)) ? (value) : (limit))
#endif

// generated using template: VirtualHIL/custom_defines.template----------------------------

typedef unsigned char X_UnInt8;
typedef char X_Int8;
typedef signed short X_Int16;
typedef unsigned short X_UnInt16;
typedef int X_Int32;
typedef unsigned int X_UnInt32;
typedef unsigned int uint;
typedef double real;

// ----------------------------------------------------------------------------------------
// generated using template: custom_consts.template----------------------------------------

// arithmetic constants
#define C_SQRT_2                    1.4142135623730950488016887242097f
#define C_SQRT_3                    1.7320508075688772935274463415059f
#define C_PI                        3.1415926535897932384626433832795f
#define C_E                         2.7182818284590452353602874713527f
#define C_2PI                       6.283185307179586476925286766559f

//@cmp.def.start
//component defines

















































































#define SQRT_2OVER3 0.8164965809277260327324280249019f
#define SQRT3_OVER_2 0.8660254037844386467637231707529f
#define ONE_DIV_BY_SQRT_3 0.57735026918962576450914878f






















































































































//@cmp.def.end


//-----------------------------------------------------------------------------------------
// generated using template: common_variables.template-------------------------------------
// true global variables





// const variables

static const real _constant4__p_value = 0.0;

static const int _msr_632_671_i1_ia1__n_rd_as = 13107200;
static const unsigned int _msr_632_671_i1_ia1__p_addr = 58;
static const char* _msr_632_671_i1_ia1__p_sig_output = "True";

static const int _msr_632_671_i2_ia1__n_rd_as = 13107200;
static const unsigned int _msr_632_671_i2_ia1__p_addr = 59;
static const char* _msr_632_671_i2_ia1__p_sig_output = "True";

static const int _msr_632_671_i3_ia1__n_rd_as = 13107200;
static const unsigned int _msr_632_671_i3_ia1__p_addr = 60;
static const char* _msr_632_671_i3_ia1__p_sig_output = "True";

static const real _msr_632_671_ph_diff4__n_alpha[1] = {0.42361882287092434};
static const char _msr_632_671_ph_diff4__n_degrees = 1;
static const real _msr_632_671_ph_diff4__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _msr_632_671_ph_diff4__n_out_size = 1;
static const int _msr_632_671_ph_diff4__n_timeout[1] = {2778};


static const real _msr_632_671_ph_diff5__n_alpha[1] = {0.42361882287092434};
static const char _msr_632_671_ph_diff5__n_degrees = 1;
static const real _msr_632_671_ph_diff5__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _msr_632_671_ph_diff5__n_out_size = 1;
static const int _msr_632_671_ph_diff5__n_timeout[1] = {2778};


static const real _msr_632_671_ph_diff6__n_alpha[1] = {0.42361882287092434};
static const char _msr_632_671_ph_diff6__n_degrees = 1;
static const real _msr_632_671_ph_diff6__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _msr_632_671_ph_diff6__n_out_size = 1;
static const int _msr_632_671_ph_diff6__n_timeout[1] = {2778};


static const int _node_611_i3_ia1__n_rd_as = 13107200;
static const unsigned int _node_611_i3_ia1__p_addr = 61;
static const char* _node_611_i3_ia1__p_sig_output = "True";

static const real _node_611_ph_diff4__n_alpha[1] = {0.42361882287092434};
static const char _node_611_ph_diff4__n_degrees = 1;
static const real _node_611_ph_diff4__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_611_ph_diff4__n_out_size = 1;
static const int _node_611_ph_diff4__n_timeout[1] = {2778};


static const char _node_632_cpu_transition4_output__n_real_time = 1;
static const char _node_632_cpu_transition4_output__n_export_c = 0;
static const unsigned int _node_632_cpu_transition4_output__p_addr = 792723456;

static const char _node_632_cpu_transition5_output__n_real_time = 1;
static const char _node_632_cpu_transition5_output__n_export_c = 0;
static const unsigned int _node_632_cpu_transition5_output__p_addr = 792723460;

static const char _node_632_cpu_transition6_output__n_real_time = 1;
static const char _node_632_cpu_transition6_output__n_export_c = 0;
static const unsigned int _node_632_cpu_transition6_output__p_addr = 792723464;

static const int _node_632_i1_ia1__n_rd_as = 13107200;
static const unsigned int _node_632_i1_ia1__p_addr = 62;
static const char* _node_632_i1_ia1__p_sig_output = "True";

static const int _node_632_i2_ia1__n_rd_as = 13107200;
static const unsigned int _node_632_i2_ia1__p_addr = 63;
static const char* _node_632_i2_ia1__p_sig_output = "True";

static const int _node_632_i3_ia1__n_rd_as = 13107200;
static const unsigned int _node_632_i3_ia1__p_addr = 64;
static const char* _node_632_i3_ia1__p_sig_output = "True";

static const real _node_632_ph_diff4__n_alpha[1] = {0.42361882287092434};
static const char _node_632_ph_diff4__n_degrees = 1;
static const real _node_632_ph_diff4__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_632_ph_diff4__n_out_size = 1;
static const int _node_632_ph_diff4__n_timeout[1] = {2778};


static const real _node_632_ph_diff5__n_alpha[1] = {0.42361882287092434};
static const char _node_632_ph_diff5__n_degrees = 1;
static const real _node_632_ph_diff5__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_632_ph_diff5__n_out_size = 1;
static const int _node_632_ph_diff5__n_timeout[1] = {2778};


static const real _node_632_ph_diff6__n_alpha[1] = {0.42361882287092434};
static const char _node_632_ph_diff6__n_degrees = 1;
static const real _node_632_ph_diff6__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_632_ph_diff6__n_out_size = 1;
static const int _node_632_ph_diff6__n_timeout[1] = {2778};


static const int _node_633_i1_ia1__n_rd_as = 13107200;
static const unsigned int _node_633_i1_ia1__p_addr = 65;
static const char* _node_633_i1_ia1__p_sig_output = "True";

static const int _node_633_i2_ia1__n_rd_as = 13107200;
static const unsigned int _node_633_i2_ia1__p_addr = 66;
static const char* _node_633_i2_ia1__p_sig_output = "True";

static const int _node_633_i3_ia1__n_rd_as = 13107200;
static const unsigned int _node_633_i3_ia1__p_addr = 67;
static const char* _node_633_i3_ia1__p_sig_output = "True";

static const real _node_633_ph_diff4__n_alpha[1] = {0.42361882287092434};
static const char _node_633_ph_diff4__n_degrees = 1;
static const real _node_633_ph_diff4__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_633_ph_diff4__n_out_size = 1;
static const int _node_633_ph_diff4__n_timeout[1] = {2778};


static const real _node_633_ph_diff5__n_alpha[1] = {0.42361882287092434};
static const char _node_633_ph_diff5__n_degrees = 1;
static const real _node_633_ph_diff5__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_633_ph_diff5__n_out_size = 1;
static const int _node_633_ph_diff5__n_timeout[1] = {2778};


static const real _node_633_ph_diff6__n_alpha[1] = {0.42361882287092434};
static const char _node_633_ph_diff6__n_degrees = 1;
static const real _node_633_ph_diff6__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_633_ph_diff6__n_out_size = 1;
static const int _node_633_ph_diff6__n_timeout[1] = {2778};


static const int _node_634_i1_ia1__n_rd_as = 13107200;
static const unsigned int _node_634_i1_ia1__p_addr = 68;
static const char* _node_634_i1_ia1__p_sig_output = "True";

static const int _node_634_i2_ia1__n_rd_as = 13107200;
static const unsigned int _node_634_i2_ia1__p_addr = 69;
static const char* _node_634_i2_ia1__p_sig_output = "True";

static const int _node_634_i3_ia1__n_rd_as = 13107200;
static const unsigned int _node_634_i3_ia1__p_addr = 70;
static const char* _node_634_i3_ia1__p_sig_output = "True";

static const real _node_634_ph_diff4__n_alpha[1] = {0.42361882287092434};
static const char _node_634_ph_diff4__n_degrees = 1;
static const real _node_634_ph_diff4__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_634_ph_diff4__n_out_size = 1;
static const int _node_634_ph_diff4__n_timeout[1] = {2778};


static const real _node_634_ph_diff5__n_alpha[1] = {0.42361882287092434};
static const char _node_634_ph_diff5__n_degrees = 1;
static const real _node_634_ph_diff5__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_634_ph_diff5__n_out_size = 1;
static const int _node_634_ph_diff5__n_timeout[1] = {2778};


static const real _node_634_ph_diff6__n_alpha[1] = {0.42361882287092434};
static const char _node_634_ph_diff6__n_degrees = 1;
static const real _node_634_ph_diff6__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_634_ph_diff6__n_out_size = 1;
static const int _node_634_ph_diff6__n_timeout[1] = {2778};


static const int _node_645_i2_ia1__n_rd_as = 13107200;
static const unsigned int _node_645_i2_ia1__p_addr = 71;
static const char* _node_645_i2_ia1__p_sig_output = "True";

static const int _node_645_i3_ia1__n_rd_as = 13107200;
static const unsigned int _node_645_i3_ia1__p_addr = 72;
static const char* _node_645_i3_ia1__p_sig_output = "True";

static const real _node_645_ph_diff4__n_alpha[1] = {0.42361882287092434};
static const char _node_645_ph_diff4__n_degrees = 1;
static const real _node_645_ph_diff4__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_645_ph_diff4__n_out_size = 1;
static const int _node_645_ph_diff4__n_timeout[1] = {2778};


static const real _node_645_ph_diff6__n_alpha[1] = {0.42361882287092434};
static const char _node_645_ph_diff6__n_degrees = 1;
static const real _node_645_ph_diff6__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_645_ph_diff6__n_out_size = 1;
static const int _node_645_ph_diff6__n_timeout[1] = {2778};


static const int _node_646_i2_ia1__n_rd_as = 13107200;
static const unsigned int _node_646_i2_ia1__p_addr = 73;
static const char* _node_646_i2_ia1__p_sig_output = "True";

static const int _node_646_i3_ia1__n_rd_as = 13107200;
static const unsigned int _node_646_i3_ia1__p_addr = 74;
static const char* _node_646_i3_ia1__p_sig_output = "True";

static const real _node_646_ph_diff4__n_alpha[1] = {0.42361882287092434};
static const char _node_646_ph_diff4__n_degrees = 1;
static const real _node_646_ph_diff4__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_646_ph_diff4__n_out_size = 1;
static const int _node_646_ph_diff4__n_timeout[1] = {2778};


static const real _node_646_ph_diff6__n_alpha[1] = {0.42361882287092434};
static const char _node_646_ph_diff6__n_degrees = 1;
static const real _node_646_ph_diff6__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_646_ph_diff6__n_out_size = 1;
static const int _node_646_ph_diff6__n_timeout[1] = {2778};


static const int _node_652_i1_ia1__n_rd_as = 13107200;
static const unsigned int _node_652_i1_ia1__p_addr = 75;
static const char* _node_652_i1_ia1__p_sig_output = "True";

static const real _node_652_ph_diff5__n_alpha[1] = {0.42361882287092434};
static const char _node_652_ph_diff5__n_degrees = 1;
static const real _node_652_ph_diff5__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_652_ph_diff5__n_out_size = 1;
static const int _node_652_ph_diff5__n_timeout[1] = {2778};


static const int _node_671_i1_ia1__n_rd_as = 13107200;
static const unsigned int _node_671_i1_ia1__p_addr = 76;
static const char* _node_671_i1_ia1__p_sig_output = "True";

static const int _node_671_i2_ia1__n_rd_as = 13107200;
static const unsigned int _node_671_i2_ia1__p_addr = 77;
static const char* _node_671_i2_ia1__p_sig_output = "True";

static const int _node_671_i3_ia1__n_rd_as = 13107200;
static const unsigned int _node_671_i3_ia1__p_addr = 78;
static const char* _node_671_i3_ia1__p_sig_output = "True";

static const real _node_671_ph_diff4__n_alpha[1] = {0.42361882287092434};
static const char _node_671_ph_diff4__n_degrees = 1;
static const real _node_671_ph_diff4__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_671_ph_diff4__n_out_size = 1;
static const int _node_671_ph_diff4__n_timeout[1] = {2778};


static const real _node_671_ph_diff5__n_alpha[1] = {0.42361882287092434};
static const char _node_671_ph_diff5__n_degrees = 1;
static const real _node_671_ph_diff5__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_671_ph_diff5__n_out_size = 1;
static const int _node_671_ph_diff5__n_timeout[1] = {2778};


static const real _node_671_ph_diff6__n_alpha[1] = {0.42361882287092434};
static const char _node_671_ph_diff6__n_degrees = 1;
static const real _node_671_ph_diff6__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_671_ph_diff6__n_out_size = 1;
static const int _node_671_ph_diff6__n_timeout[1] = {2778};


static const int _node_675_i1_ia1__n_rd_as = 13107200;
static const unsigned int _node_675_i1_ia1__p_addr = 79;
static const char* _node_675_i1_ia1__p_sig_output = "True";

static const int _node_675_i2_ia1__n_rd_as = 13107200;
static const unsigned int _node_675_i2_ia1__p_addr = 80;
static const char* _node_675_i2_ia1__p_sig_output = "True";

static const int _node_675_i3_ia1__n_rd_as = 13107200;
static const unsigned int _node_675_i3_ia1__p_addr = 81;
static const char* _node_675_i3_ia1__p_sig_output = "True";

static const real _node_675_ph_diff4__n_alpha[1] = {0.42361882287092434};
static const char _node_675_ph_diff4__n_degrees = 1;
static const real _node_675_ph_diff4__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_675_ph_diff4__n_out_size = 1;
static const int _node_675_ph_diff4__n_timeout[1] = {2778};


static const real _node_675_ph_diff5__n_alpha[1] = {0.42361882287092434};
static const char _node_675_ph_diff5__n_degrees = 1;
static const real _node_675_ph_diff5__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_675_ph_diff5__n_out_size = 1;
static const int _node_675_ph_diff5__n_timeout[1] = {2778};


static const real _node_675_ph_diff6__n_alpha[1] = {0.42361882287092434};
static const char _node_675_ph_diff6__n_degrees = 1;
static const real _node_675_ph_diff6__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_675_ph_diff6__n_out_size = 1;
static const int _node_675_ph_diff6__n_timeout[1] = {2778};


static const int _node_680_i1_ia1__n_rd_as = 13107200;
static const unsigned int _node_680_i1_ia1__p_addr = 82;
static const char* _node_680_i1_ia1__p_sig_output = "True";

static const int _node_680_i2_ia1__n_rd_as = 13107200;
static const unsigned int _node_680_i2_ia1__p_addr = 83;
static const char* _node_680_i2_ia1__p_sig_output = "True";

static const int _node_680_i3_ia1__n_rd_as = 13107200;
static const unsigned int _node_680_i3_ia1__p_addr = 84;
static const char* _node_680_i3_ia1__p_sig_output = "True";

static const real _node_680_ph_diff4__n_alpha[1] = {0.42361882287092434};
static const char _node_680_ph_diff4__n_degrees = 1;
static const real _node_680_ph_diff4__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_680_ph_diff4__n_out_size = 1;
static const int _node_680_ph_diff4__n_timeout[1] = {2778};


static const real _node_680_ph_diff5__n_alpha[1] = {0.42361882287092434};
static const char _node_680_ph_diff5__n_degrees = 1;
static const real _node_680_ph_diff5__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_680_ph_diff5__n_out_size = 1;
static const int _node_680_ph_diff5__n_timeout[1] = {2778};


static const real _node_680_ph_diff6__n_alpha[1] = {0.42361882287092434};
static const char _node_680_ph_diff6__n_degrees = 1;
static const real _node_680_ph_diff6__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_680_ph_diff6__n_out_size = 1;
static const int _node_680_ph_diff6__n_timeout[1] = {2778};


static const int _node_684_i1_ia1__n_rd_as = 13107200;
static const unsigned int _node_684_i1_ia1__p_addr = 85;
static const char* _node_684_i1_ia1__p_sig_output = "True";

static const int _node_684_i3_ia1__n_rd_as = 13107200;
static const unsigned int _node_684_i3_ia1__p_addr = 86;
static const char* _node_684_i3_ia1__p_sig_output = "True";

static const real _node_684_ph_diff4__n_alpha[1] = {0.42361882287092434};
static const char _node_684_ph_diff4__n_degrees = 1;
static const real _node_684_ph_diff4__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_684_ph_diff4__n_out_size = 1;
static const int _node_684_ph_diff4__n_timeout[1] = {2778};


static const real _node_684_ph_diff5__n_alpha[1] = {0.42361882287092434};
static const char _node_684_ph_diff5__n_degrees = 1;
static const real _node_684_ph_diff5__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_684_ph_diff5__n_out_size = 1;
static const int _node_684_ph_diff5__n_timeout[1] = {2778};


static const int _node_692_i1_ia1__n_rd_as = 13107200;
static const unsigned int _node_692_i1_ia1__p_addr = 87;
static const char* _node_692_i1_ia1__p_sig_output = "True";

static const int _node_692_i2_ia1__n_rd_as = 13107200;
static const unsigned int _node_692_i2_ia1__p_addr = 88;
static const char* _node_692_i2_ia1__p_sig_output = "True";

static const int _node_692_i3_ia1__n_rd_as = 13107200;
static const unsigned int _node_692_i3_ia1__p_addr = 89;
static const char* _node_692_i3_ia1__p_sig_output = "True";

static const real _node_692_ph_diff4__n_alpha[1] = {0.42361882287092434};
static const char _node_692_ph_diff4__n_degrees = 1;
static const real _node_692_ph_diff4__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_692_ph_diff4__n_out_size = 1;
static const int _node_692_ph_diff4__n_timeout[1] = {2778};


static const real _node_692_ph_diff5__n_alpha[1] = {0.42361882287092434};
static const char _node_692_ph_diff5__n_degrees = 1;
static const real _node_692_ph_diff5__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_692_ph_diff5__n_out_size = 1;
static const int _node_692_ph_diff5__n_timeout[1] = {2778};


static const real _node_692_ph_diff6__n_alpha[1] = {0.42361882287092434};
static const char _node_692_ph_diff6__n_degrees = 1;
static const real _node_692_ph_diff6__n_one_minus_alpha[1] = {0.5763811771290757};
static const int _node_692_ph_diff6__n_out_size = 1;
static const int _node_692_ph_diff6__n_timeout[1] = {2778};


static const int _reference_v1_ref2_va1__n_rd_as = 13107200;
static const unsigned int _reference_v1_ref2_va1__p_addr = 41;
static const char* _reference_v1_ref2_va1__p_sig_output = "True";




static const int _msr_632_671_i3_phase__n_out_size = 1;
static const unsigned int _msr_632_671_i3_phase__p_addr = 16543;

static const int _msr_632_671_i1_phase__n_out_size = 1;
static const unsigned int _msr_632_671_i1_phase__p_addr = 16539;

static const int _msr_632_671_i2_phase__n_out_size = 1;
static const unsigned int _msr_632_671_i2_phase__p_addr = 16541;

static const int _node_611_i3_phase__n_out_size = 1;
static const unsigned int _node_611_i3_phase__p_addr = 16545;

static const int _node_632_i3_phase__n_out_size = 1;
static const unsigned int _node_632_i3_phase__p_addr = 16551;

static const int _node_632_i1_phase__n_out_size = 1;
static const unsigned int _node_632_i1_phase__p_addr = 16547;

static const int _node_632_i2_phase__n_out_size = 1;
static const unsigned int _node_632_i2_phase__p_addr = 16549;

static const int _node_633_i3_phase__n_out_size = 1;
static const unsigned int _node_633_i3_phase__p_addr = 16558;

static const int _node_633_i1_phase__n_out_size = 1;
static const unsigned int _node_633_i1_phase__p_addr = 16554;

static const int _node_633_i2_phase__n_out_size = 1;
static const unsigned int _node_633_i2_phase__p_addr = 16556;

static const int _node_634_i3_phase__n_out_size = 1;
static const unsigned int _node_634_i3_phase__p_addr = 16564;

static const int _node_634_i1_phase__n_out_size = 1;
static const unsigned int _node_634_i1_phase__p_addr = 16560;

static const int _node_634_i2_phase__n_out_size = 1;
static const unsigned int _node_634_i2_phase__p_addr = 16562;

static const int _node_645_i3_phase__n_out_size = 1;
static const unsigned int _node_645_i3_phase__p_addr = 16568;

static const int _node_645_i2_phase__n_out_size = 1;
static const unsigned int _node_645_i2_phase__p_addr = 16566;

static const int _node_646_i3_phase__n_out_size = 1;
static const unsigned int _node_646_i3_phase__p_addr = 16572;

static const int _node_646_i2_phase__n_out_size = 1;
static const unsigned int _node_646_i2_phase__p_addr = 16570;

static const int _node_652_i1_phase__n_out_size = 1;
static const unsigned int _node_652_i1_phase__p_addr = 16574;

static const int _node_671_i3_phase__n_out_size = 1;
static const unsigned int _node_671_i3_phase__p_addr = 16580;

static const int _node_671_i1_phase__n_out_size = 1;
static const unsigned int _node_671_i1_phase__p_addr = 16576;

static const int _node_671_i2_phase__n_out_size = 1;
static const unsigned int _node_671_i2_phase__p_addr = 16578;

static const int _node_675_i3_phase__n_out_size = 1;
static const unsigned int _node_675_i3_phase__p_addr = 16586;

static const int _node_675_i1_phase__n_out_size = 1;
static const unsigned int _node_675_i1_phase__p_addr = 16582;

static const int _node_675_i2_phase__n_out_size = 1;
static const unsigned int _node_675_i2_phase__p_addr = 16584;

static const int _node_680_i3_phase__n_out_size = 1;
static const unsigned int _node_680_i3_phase__p_addr = 16592;

static const int _node_680_i1_phase__n_out_size = 1;
static const unsigned int _node_680_i1_phase__p_addr = 16588;

static const int _node_680_i2_phase__n_out_size = 1;
static const unsigned int _node_680_i2_phase__p_addr = 16590;

static const int _node_684_i3_phase__n_out_size = 1;
static const unsigned int _node_684_i3_phase__p_addr = 16596;

static const int _node_684_i1_phase__n_out_size = 1;
static const unsigned int _node_684_i1_phase__p_addr = 16594;

static const int _node_692_i3_phase__n_out_size = 1;
static const unsigned int _node_692_i3_phase__p_addr = 16602;

static const int _node_692_i1_phase__n_out_size = 1;
static const unsigned int _node_692_i1_phase__p_addr = 16598;

static const int _node_692_i2_phase__n_out_size = 1;
static const unsigned int _node_692_i2_phase__p_addr = 16600;

static const char _node_611_cpu_transition1_input__n_real_time = 1;
static const char _node_611_cpu_transition1_input__n_export_c = 0;
static const unsigned int _node_611_cpu_transition1_input__p_addr = 792723688;

static const char _node_632_cpu_transition1_input__n_real_time = 1;
static const char _node_632_cpu_transition1_input__n_export_c = 0;
static const unsigned int _node_632_cpu_transition1_input__p_addr = 792723692;

static const char _node_632_cpu_transition2_input__n_real_time = 1;
static const char _node_632_cpu_transition2_input__n_export_c = 0;
static const unsigned int _node_632_cpu_transition2_input__p_addr = 792723696;

static const char _node_632_cpu_transition3_input__n_real_time = 1;
static const char _node_632_cpu_transition3_input__n_export_c = 0;
static const unsigned int _node_632_cpu_transition3_input__p_addr = 792723700;

static const char _node_633_cpu_transition1_input__n_real_time = 1;
static const char _node_633_cpu_transition1_input__n_export_c = 0;
static const unsigned int _node_633_cpu_transition1_input__p_addr = 792723704;

static const char _node_633_cpu_transition2_input__n_real_time = 1;
static const char _node_633_cpu_transition2_input__n_export_c = 0;
static const unsigned int _node_633_cpu_transition2_input__p_addr = 792723708;

static const char _node_633_cpu_transition3_input__n_real_time = 1;
static const char _node_633_cpu_transition3_input__n_export_c = 0;
static const unsigned int _node_633_cpu_transition3_input__p_addr = 792723712;

static const char _node_634_cpu_transition1_input__n_real_time = 1;
static const char _node_634_cpu_transition1_input__n_export_c = 0;
static const unsigned int _node_634_cpu_transition1_input__p_addr = 792723716;

static const char _node_634_cpu_transition2_input__n_real_time = 1;
static const char _node_634_cpu_transition2_input__n_export_c = 0;
static const unsigned int _node_634_cpu_transition2_input__p_addr = 792723720;

static const char _node_634_cpu_transition3_input__n_real_time = 1;
static const char _node_634_cpu_transition3_input__n_export_c = 0;
static const unsigned int _node_634_cpu_transition3_input__p_addr = 792723724;

static const char _node_645_cpu_transition1_input__n_real_time = 1;
static const char _node_645_cpu_transition1_input__n_export_c = 0;
static const unsigned int _node_645_cpu_transition1_input__p_addr = 792723728;

static const char _node_645_cpu_transition2_input__n_real_time = 1;
static const char _node_645_cpu_transition2_input__n_export_c = 0;
static const unsigned int _node_645_cpu_transition2_input__p_addr = 792723732;

static const char _node_646_cpu_transition1_input__n_real_time = 1;
static const char _node_646_cpu_transition1_input__n_export_c = 0;
static const unsigned int _node_646_cpu_transition1_input__p_addr = 792723736;

static const char _node_646_cpu_transition2_input__n_real_time = 1;
static const char _node_646_cpu_transition2_input__n_export_c = 0;
static const unsigned int _node_646_cpu_transition2_input__p_addr = 792723740;

static const char _node_652_cpu_transition1_input__n_real_time = 1;
static const char _node_652_cpu_transition1_input__n_export_c = 0;
static const unsigned int _node_652_cpu_transition1_input__p_addr = 792723744;

static const char _node_671_cpu_transition1_input__n_real_time = 1;
static const char _node_671_cpu_transition1_input__n_export_c = 0;
static const unsigned int _node_671_cpu_transition1_input__p_addr = 792723748;

static const char _node_671_cpu_transition2_input__n_real_time = 1;
static const char _node_671_cpu_transition2_input__n_export_c = 0;
static const unsigned int _node_671_cpu_transition2_input__p_addr = 792723752;

static const char _node_671_cpu_transition3_input__n_real_time = 1;
static const char _node_671_cpu_transition3_input__n_export_c = 0;
static const unsigned int _node_671_cpu_transition3_input__p_addr = 792723756;

static const char _node_675_cpu_transition1_input__n_real_time = 1;
static const char _node_675_cpu_transition1_input__n_export_c = 0;
static const unsigned int _node_675_cpu_transition1_input__p_addr = 792723760;

static const char _node_675_cpu_transition2_input__n_real_time = 1;
static const char _node_675_cpu_transition2_input__n_export_c = 0;
static const unsigned int _node_675_cpu_transition2_input__p_addr = 792723764;

static const char _node_675_cpu_transition3_input__n_real_time = 1;
static const char _node_675_cpu_transition3_input__n_export_c = 0;
static const unsigned int _node_675_cpu_transition3_input__p_addr = 792723768;

static const char _node_680_cpu_transition1_input__n_real_time = 1;
static const char _node_680_cpu_transition1_input__n_export_c = 0;
static const unsigned int _node_680_cpu_transition1_input__p_addr = 792723772;

static const char _node_680_cpu_transition2_input__n_real_time = 1;
static const char _node_680_cpu_transition2_input__n_export_c = 0;
static const unsigned int _node_680_cpu_transition2_input__p_addr = 792723776;

static const char _node_680_cpu_transition3_input__n_real_time = 1;
static const char _node_680_cpu_transition3_input__n_export_c = 0;
static const unsigned int _node_680_cpu_transition3_input__p_addr = 792723780;

static const char _node_684_cpu_transition1_input__n_real_time = 1;
static const char _node_684_cpu_transition1_input__n_export_c = 0;
static const unsigned int _node_684_cpu_transition1_input__p_addr = 792723784;

static const char _node_684_cpu_transition2_input__n_real_time = 1;
static const char _node_684_cpu_transition2_input__n_export_c = 0;
static const unsigned int _node_684_cpu_transition2_input__p_addr = 792723788;

static const char _node_692_cpu_transition1_input__n_real_time = 1;
static const char _node_692_cpu_transition1_input__n_export_c = 0;
static const unsigned int _node_692_cpu_transition1_input__p_addr = 792723792;

static const char _node_692_cpu_transition2_input__n_real_time = 1;
static const char _node_692_cpu_transition2_input__n_export_c = 0;
static const unsigned int _node_692_cpu_transition2_input__p_addr = 792723796;

static const char _node_692_cpu_transition3_input__n_real_time = 1;
static const char _node_692_cpu_transition3_input__n_export_c = 0;
static const unsigned int _node_692_cpu_transition3_input__p_addr = 792723800;

static const char* _s1_triple_s1_ideal_ctc_wrapper__n_ctrl_src_val = "Model";
static const char* _s1_triple_s1_ideal_ctc_wrapper__n_enable_fb_out_val = "False";
static const int _s1_triple_s1_ideal_ctc_wrapper__n_rd_ds = 16252928;
static const int _s1_triple_s1_ideal_ctc_wrapper__n_spc_baseaddr = 134217728;
static const int _s1_triple_s1_ideal_ctc_wrapper__n_spc_ct = 2359296;
static const int _s1_triple_s1_ideal_ctc_wrapper__n_spc_ct_sw_ctrl_val = 1152;
static const int _s1_triple_s1_ideal_ctc_wrapper__n_spc_do_baseaddr = 1024;
static const int _s1_triple_s1_ideal_ctc_wrapper__n_spc_do_mem_width = 15;
static const int _s1_triple_s1_ideal_ctc_wrapper__n_spc_off = 4194304;
static const int _s1_triple_s1_ideal_ctc_wrapper__p_ctc_nb = 0;
static const int _s1_triple_s1_ideal_ctc_wrapper__p_spc_nb = 0;

static const int _msr_632_671_i1_rms__n_out_size = 1;
static const unsigned int _msr_632_671_i1_rms__p_addr = 16540;

static const int _msr_632_671_i2_rms__n_out_size = 1;
static const unsigned int _msr_632_671_i2_rms__p_addr = 16542;

static const int _msr_632_671_i3_rms__n_out_size = 1;
static const unsigned int _msr_632_671_i3_rms__p_addr = 16544;

static const int _node_611_i3_rms__n_out_size = 1;
static const unsigned int _node_611_i3_rms__p_addr = 16546;

static const int _node_632_i1_rms__n_out_size = 1;
static const unsigned int _node_632_i1_rms__p_addr = 16548;

static const int _node_632_i2_rms__n_out_size = 1;
static const unsigned int _node_632_i2_rms__p_addr = 16550;

static const int _node_632_probe1__n_out_size = 1;
static const unsigned int _node_632_probe1__p_addr = 16553;

static const int _node_632_i3_rms__n_out_size = 1;
static const unsigned int _node_632_i3_rms__p_addr = 16552;

static const int _node_633_i1_rms__n_out_size = 1;
static const unsigned int _node_633_i1_rms__p_addr = 16555;

static const int _node_633_i2_rms__n_out_size = 1;
static const unsigned int _node_633_i2_rms__p_addr = 16557;

static const int _node_633_i3_rms__n_out_size = 1;
static const unsigned int _node_633_i3_rms__p_addr = 16559;

static const int _node_634_i1_rms__n_out_size = 1;
static const unsigned int _node_634_i1_rms__p_addr = 16561;

static const int _node_634_i2_rms__n_out_size = 1;
static const unsigned int _node_634_i2_rms__p_addr = 16563;

static const int _node_634_i3_rms__n_out_size = 1;
static const unsigned int _node_634_i3_rms__p_addr = 16565;

static const int _node_645_i2_rms__n_out_size = 1;
static const unsigned int _node_645_i2_rms__p_addr = 16567;

static const int _node_645_i3_rms__n_out_size = 1;
static const unsigned int _node_645_i3_rms__p_addr = 16569;

static const int _node_646_i2_rms__n_out_size = 1;
static const unsigned int _node_646_i2_rms__p_addr = 16571;

static const int _node_646_i3_rms__n_out_size = 1;
static const unsigned int _node_646_i3_rms__p_addr = 16573;

static const int _node_652_i1_rms__n_out_size = 1;
static const unsigned int _node_652_i1_rms__p_addr = 16575;

static const int _node_671_i1_rms__n_out_size = 1;
static const unsigned int _node_671_i1_rms__p_addr = 16577;

static const int _node_671_i2_rms__n_out_size = 1;
static const unsigned int _node_671_i2_rms__p_addr = 16579;

static const int _node_671_i3_rms__n_out_size = 1;
static const unsigned int _node_671_i3_rms__p_addr = 16581;

static const int _node_675_i1_rms__n_out_size = 1;
static const unsigned int _node_675_i1_rms__p_addr = 16583;

static const int _node_675_i2_rms__n_out_size = 1;
static const unsigned int _node_675_i2_rms__p_addr = 16585;

static const int _node_675_i3_rms__n_out_size = 1;
static const unsigned int _node_675_i3_rms__p_addr = 16587;

static const int _node_680_i1_rms__n_out_size = 1;
static const unsigned int _node_680_i1_rms__p_addr = 16589;

static const int _node_680_i2_rms__n_out_size = 1;
static const unsigned int _node_680_i2_rms__p_addr = 16591;

static const int _node_680_i3_rms__n_out_size = 1;
static const unsigned int _node_680_i3_rms__p_addr = 16593;

static const int _node_684_i1_rms__n_out_size = 1;
static const unsigned int _node_684_i1_rms__p_addr = 16595;

static const int _node_684_i3_rms__n_out_size = 1;
static const unsigned int _node_684_i3_rms__p_addr = 16597;

static const int _node_692_i1_rms__n_out_size = 1;
static const unsigned int _node_692_i1_rms__p_addr = 16599;

static const int _node_692_i2_rms__n_out_size = 1;
static const unsigned int _node_692_i2_rms__p_addr = 16601;

static const int _node_692_i3_rms__n_out_size = 1;
static const unsigned int _node_692_i3_rms__p_addr = 16603;


//@cmp.var.start
// variables
static real _constant4__out;
real _msr_632_671_i1_ia1__out;
real _msr_632_671_i2_ia1__out;
real _msr_632_671_i3_ia1__out;
static real _msr_632_671_ph_diff4__phase_diff;
static real _msr_632_671_ph_diff5__phase_diff;
static real _msr_632_671_ph_diff6__phase_diff;
real _node_611_i3_ia1__out;
static real _node_611_ph_diff4__phase_diff;
real _node_632_cpu_transition4_output__out;
real _node_632_cpu_transition5_output__out;
real _node_632_cpu_transition6_output__out;
real _node_632_i1_ia1__out;
real _node_632_i2_ia1__out;
real _node_632_i3_ia1__out;
static real _node_632_ph_diff4__phase_diff;
static real _node_632_ph_diff5__phase_diff;
static real _node_632_ph_diff6__phase_diff;
real _node_633_i1_ia1__out;
real _node_633_i2_ia1__out;
real _node_633_i3_ia1__out;
static real _node_633_ph_diff4__phase_diff;
static real _node_633_ph_diff5__phase_diff;
static real _node_633_ph_diff6__phase_diff;
real _node_634_i1_ia1__out;
real _node_634_i2_ia1__out;
real _node_634_i3_ia1__out;
static real _node_634_ph_diff4__phase_diff;
static real _node_634_ph_diff5__phase_diff;
static real _node_634_ph_diff6__phase_diff;
real _node_645_i2_ia1__out;
real _node_645_i3_ia1__out;
static real _node_645_ph_diff4__phase_diff;
static real _node_645_ph_diff6__phase_diff;
real _node_646_i2_ia1__out;
real _node_646_i3_ia1__out;
static real _node_646_ph_diff4__phase_diff;
static real _node_646_ph_diff6__phase_diff;
real _node_652_i1_ia1__out;
static real _node_652_ph_diff5__phase_diff;
real _node_671_i1_ia1__out;
real _node_671_i2_ia1__out;
real _node_671_i3_ia1__out;
static real _node_671_ph_diff4__phase_diff;
static real _node_671_ph_diff5__phase_diff;
static real _node_671_ph_diff6__phase_diff;
real _node_675_i1_ia1__out;
real _node_675_i2_ia1__out;
real _node_675_i3_ia1__out;
static real _node_675_ph_diff4__phase_diff;
static real _node_675_ph_diff5__phase_diff;
static real _node_675_ph_diff6__phase_diff;
real _node_680_i1_ia1__out;
real _node_680_i2_ia1__out;
real _node_680_i3_ia1__out;
static real _node_680_ph_diff4__phase_diff;
static real _node_680_ph_diff5__phase_diff;
static real _node_680_ph_diff6__phase_diff;
real _node_684_i1_ia1__out;
real _node_684_i3_ia1__out;
static real _node_684_ph_diff4__phase_diff;
static real _node_684_ph_diff5__phase_diff;
real _node_692_i1_ia1__out;
real _node_692_i2_ia1__out;
real _node_692_i3_ia1__out;
static real _node_692_ph_diff4__phase_diff;
static real _node_692_ph_diff5__phase_diff;
static real _node_692_ph_diff6__phase_diff;
real _reference_v1_ref2_va1__out;
double _switch_state__out;

double _msr_632_671_rms6__out;
X_UnInt32 _msr_632_671_rms6__zc;
double _msr_632_671_rms5__out;
X_UnInt32 _msr_632_671_rms5__zc;
double _msr_632_671_rms4__out;
X_UnInt32 _msr_632_671_rms4__zc;









double _node_611_rms4__out;
X_UnInt32 _node_611_rms4__zc;



double _node_632_rms6__out;
X_UnInt32 _node_632_rms6__zc;
double _node_632_rms5__out;
X_UnInt32 _node_632_rms5__zc;
double _node_632_power_meter1__Pdc;
double _node_632_power_meter1__Qdc;
double _node_632_power_meter1__P0dc;
double _node_632_power_meter1__Pac;
double _node_632_power_meter1__Qac;
double _node_632_power_meter1__P0ac;
double _node_632_power_meter1__apparent;
double _node_632_power_meter1__k_factor;
double _node_632_power_meter1__v_alpha;
double _node_632_power_meter1__v_beta;
double _node_632_power_meter1__i_alpha;
double _node_632_power_meter1__i_beta;
double _node_632_power_meter1__v_zero;
double _node_632_power_meter1__i_zero;
double _node_632_power_meter1__filter_1_output;
double _node_632_power_meter1__filter_1_outputQ;
double _node_632_power_meter1__filter_1_outputP0;
double _node_632_rms4__out;
X_UnInt32 _node_632_rms4__zc;









double _node_633_rms6__out;
X_UnInt32 _node_633_rms6__zc;
double _node_633_rms5__out;
X_UnInt32 _node_633_rms5__zc;
double _node_633_rms4__out;
X_UnInt32 _node_633_rms4__zc;









double _node_634_rms6__out;
X_UnInt32 _node_634_rms6__zc;
double _node_634_rms5__out;
X_UnInt32 _node_634_rms5__zc;
double _node_634_rms4__out;
X_UnInt32 _node_634_rms4__zc;









double _node_645_rms5__out;
X_UnInt32 _node_645_rms5__zc;
double _node_645_rms4__out;
X_UnInt32 _node_645_rms4__zc;






double _node_646_rms5__out;
X_UnInt32 _node_646_rms5__zc;
double _node_646_rms4__out;
X_UnInt32 _node_646_rms4__zc;






double _node_652_rms6__out;
X_UnInt32 _node_652_rms6__zc;



double _node_671_rms6__out;
X_UnInt32 _node_671_rms6__zc;
double _node_671_rms5__out;
X_UnInt32 _node_671_rms5__zc;
double _node_671_rms4__out;
X_UnInt32 _node_671_rms4__zc;









double _node_675_rms6__out;
X_UnInt32 _node_675_rms6__zc;
double _node_675_rms5__out;
X_UnInt32 _node_675_rms5__zc;
double _node_675_rms4__out;
X_UnInt32 _node_675_rms4__zc;









double _node_680_rms6__out;
X_UnInt32 _node_680_rms6__zc;
double _node_680_rms5__out;
X_UnInt32 _node_680_rms5__zc;
double _node_680_rms4__out;
X_UnInt32 _node_680_rms4__zc;









double _node_684_rms6__out;
X_UnInt32 _node_684_rms6__zc;
double _node_684_rms4__out;
X_UnInt32 _node_684_rms4__zc;






double _node_692_rms6__out;
X_UnInt32 _node_692_rms6__zc;
double _node_692_rms5__out;
X_UnInt32 _node_692_rms5__zc;
double _node_692_rms4__out;
X_UnInt32 _node_692_rms4__zc;










































































































































//@cmp.var.end

//@cmp.svar.start
// state variables












real _msr_632_671_ph_diff4__previous_correction_ref;
real _msr_632_671_ph_diff4__sample_cnt_ref;
real _msr_632_671_ph_diff4__previous_filtered_ref;
real _msr_632_671_ph_diff4__filtered_ref;
real _msr_632_671_ph_diff4__correction_ref;
char _msr_632_671_ph_diff4__zc_flag_ref;
real _msr_632_671_ph_diff4__phase_state;
real _msr_632_671_ph_diff4__correction_in;
real _msr_632_671_ph_diff4__previous_correction_in;
real _msr_632_671_ph_diff4__sample_cnt_in;
real _msr_632_671_ph_diff4__previous_filtered_in;
real _msr_632_671_ph_diff4__filtered_in;
char _msr_632_671_ph_diff4__no_zc_flag_in[1];
char _msr_632_671_ph_diff4__zc_flag_in[1];


real _msr_632_671_ph_diff5__previous_correction_ref;
real _msr_632_671_ph_diff5__sample_cnt_ref;
real _msr_632_671_ph_diff5__previous_filtered_ref;
real _msr_632_671_ph_diff5__filtered_ref;
real _msr_632_671_ph_diff5__correction_ref;
char _msr_632_671_ph_diff5__zc_flag_ref;
real _msr_632_671_ph_diff5__phase_state;
real _msr_632_671_ph_diff5__correction_in;
real _msr_632_671_ph_diff5__previous_correction_in;
real _msr_632_671_ph_diff5__sample_cnt_in;
real _msr_632_671_ph_diff5__previous_filtered_in;
real _msr_632_671_ph_diff5__filtered_in;
char _msr_632_671_ph_diff5__no_zc_flag_in[1];
char _msr_632_671_ph_diff5__zc_flag_in[1];


real _msr_632_671_ph_diff6__previous_correction_ref;
real _msr_632_671_ph_diff6__sample_cnt_ref;
real _msr_632_671_ph_diff6__previous_filtered_ref;
real _msr_632_671_ph_diff6__filtered_ref;
real _msr_632_671_ph_diff6__correction_ref;
char _msr_632_671_ph_diff6__zc_flag_ref;
real _msr_632_671_ph_diff6__phase_state;
real _msr_632_671_ph_diff6__correction_in;
real _msr_632_671_ph_diff6__previous_correction_in;
real _msr_632_671_ph_diff6__sample_cnt_in;
real _msr_632_671_ph_diff6__previous_filtered_in;
real _msr_632_671_ph_diff6__filtered_in;
char _msr_632_671_ph_diff6__no_zc_flag_in[1];
char _msr_632_671_ph_diff6__zc_flag_in[1];





real _node_611_ph_diff4__previous_correction_ref;
real _node_611_ph_diff4__sample_cnt_ref;
real _node_611_ph_diff4__previous_filtered_ref;
real _node_611_ph_diff4__filtered_ref;
real _node_611_ph_diff4__correction_ref;
char _node_611_ph_diff4__zc_flag_ref;
real _node_611_ph_diff4__phase_state;
real _node_611_ph_diff4__correction_in;
real _node_611_ph_diff4__previous_correction_in;
real _node_611_ph_diff4__sample_cnt_in;
real _node_611_ph_diff4__previous_filtered_in;
real _node_611_ph_diff4__filtered_in;
char _node_611_ph_diff4__no_zc_flag_in[1];
char _node_611_ph_diff4__zc_flag_in[1];




















real _node_632_ph_diff4__previous_correction_ref;
real _node_632_ph_diff4__sample_cnt_ref;
real _node_632_ph_diff4__previous_filtered_ref;
real _node_632_ph_diff4__filtered_ref;
real _node_632_ph_diff4__correction_ref;
char _node_632_ph_diff4__zc_flag_ref;
real _node_632_ph_diff4__phase_state;
real _node_632_ph_diff4__correction_in;
real _node_632_ph_diff4__previous_correction_in;
real _node_632_ph_diff4__sample_cnt_in;
real _node_632_ph_diff4__previous_filtered_in;
real _node_632_ph_diff4__filtered_in;
char _node_632_ph_diff4__no_zc_flag_in[1];
char _node_632_ph_diff4__zc_flag_in[1];


real _node_632_ph_diff5__previous_correction_ref;
real _node_632_ph_diff5__sample_cnt_ref;
real _node_632_ph_diff5__previous_filtered_ref;
real _node_632_ph_diff5__filtered_ref;
real _node_632_ph_diff5__correction_ref;
char _node_632_ph_diff5__zc_flag_ref;
real _node_632_ph_diff5__phase_state;
real _node_632_ph_diff5__correction_in;
real _node_632_ph_diff5__previous_correction_in;
real _node_632_ph_diff5__sample_cnt_in;
real _node_632_ph_diff5__previous_filtered_in;
real _node_632_ph_diff5__filtered_in;
char _node_632_ph_diff5__no_zc_flag_in[1];
char _node_632_ph_diff5__zc_flag_in[1];


real _node_632_ph_diff6__previous_correction_ref;
real _node_632_ph_diff6__sample_cnt_ref;
real _node_632_ph_diff6__previous_filtered_ref;
real _node_632_ph_diff6__filtered_ref;
real _node_632_ph_diff6__correction_ref;
char _node_632_ph_diff6__zc_flag_ref;
real _node_632_ph_diff6__phase_state;
real _node_632_ph_diff6__correction_in;
real _node_632_ph_diff6__previous_correction_in;
real _node_632_ph_diff6__sample_cnt_in;
real _node_632_ph_diff6__previous_filtered_in;
real _node_632_ph_diff6__filtered_in;
char _node_632_ph_diff6__no_zc_flag_in[1];
char _node_632_ph_diff6__zc_flag_in[1];











real _node_633_ph_diff4__previous_correction_ref;
real _node_633_ph_diff4__sample_cnt_ref;
real _node_633_ph_diff4__previous_filtered_ref;
real _node_633_ph_diff4__filtered_ref;
real _node_633_ph_diff4__correction_ref;
char _node_633_ph_diff4__zc_flag_ref;
real _node_633_ph_diff4__phase_state;
real _node_633_ph_diff4__correction_in;
real _node_633_ph_diff4__previous_correction_in;
real _node_633_ph_diff4__sample_cnt_in;
real _node_633_ph_diff4__previous_filtered_in;
real _node_633_ph_diff4__filtered_in;
char _node_633_ph_diff4__no_zc_flag_in[1];
char _node_633_ph_diff4__zc_flag_in[1];


real _node_633_ph_diff5__previous_correction_ref;
real _node_633_ph_diff5__sample_cnt_ref;
real _node_633_ph_diff5__previous_filtered_ref;
real _node_633_ph_diff5__filtered_ref;
real _node_633_ph_diff5__correction_ref;
char _node_633_ph_diff5__zc_flag_ref;
real _node_633_ph_diff5__phase_state;
real _node_633_ph_diff5__correction_in;
real _node_633_ph_diff5__previous_correction_in;
real _node_633_ph_diff5__sample_cnt_in;
real _node_633_ph_diff5__previous_filtered_in;
real _node_633_ph_diff5__filtered_in;
char _node_633_ph_diff5__no_zc_flag_in[1];
char _node_633_ph_diff5__zc_flag_in[1];


real _node_633_ph_diff6__previous_correction_ref;
real _node_633_ph_diff6__sample_cnt_ref;
real _node_633_ph_diff6__previous_filtered_ref;
real _node_633_ph_diff6__filtered_ref;
real _node_633_ph_diff6__correction_ref;
char _node_633_ph_diff6__zc_flag_ref;
real _node_633_ph_diff6__phase_state;
real _node_633_ph_diff6__correction_in;
real _node_633_ph_diff6__previous_correction_in;
real _node_633_ph_diff6__sample_cnt_in;
real _node_633_ph_diff6__previous_filtered_in;
real _node_633_ph_diff6__filtered_in;
char _node_633_ph_diff6__no_zc_flag_in[1];
char _node_633_ph_diff6__zc_flag_in[1];











real _node_634_ph_diff4__previous_correction_ref;
real _node_634_ph_diff4__sample_cnt_ref;
real _node_634_ph_diff4__previous_filtered_ref;
real _node_634_ph_diff4__filtered_ref;
real _node_634_ph_diff4__correction_ref;
char _node_634_ph_diff4__zc_flag_ref;
real _node_634_ph_diff4__phase_state;
real _node_634_ph_diff4__correction_in;
real _node_634_ph_diff4__previous_correction_in;
real _node_634_ph_diff4__sample_cnt_in;
real _node_634_ph_diff4__previous_filtered_in;
real _node_634_ph_diff4__filtered_in;
char _node_634_ph_diff4__no_zc_flag_in[1];
char _node_634_ph_diff4__zc_flag_in[1];


real _node_634_ph_diff5__previous_correction_ref;
real _node_634_ph_diff5__sample_cnt_ref;
real _node_634_ph_diff5__previous_filtered_ref;
real _node_634_ph_diff5__filtered_ref;
real _node_634_ph_diff5__correction_ref;
char _node_634_ph_diff5__zc_flag_ref;
real _node_634_ph_diff5__phase_state;
real _node_634_ph_diff5__correction_in;
real _node_634_ph_diff5__previous_correction_in;
real _node_634_ph_diff5__sample_cnt_in;
real _node_634_ph_diff5__previous_filtered_in;
real _node_634_ph_diff5__filtered_in;
char _node_634_ph_diff5__no_zc_flag_in[1];
char _node_634_ph_diff5__zc_flag_in[1];


real _node_634_ph_diff6__previous_correction_ref;
real _node_634_ph_diff6__sample_cnt_ref;
real _node_634_ph_diff6__previous_filtered_ref;
real _node_634_ph_diff6__filtered_ref;
real _node_634_ph_diff6__correction_ref;
char _node_634_ph_diff6__zc_flag_ref;
real _node_634_ph_diff6__phase_state;
real _node_634_ph_diff6__correction_in;
real _node_634_ph_diff6__previous_correction_in;
real _node_634_ph_diff6__sample_cnt_in;
real _node_634_ph_diff6__previous_filtered_in;
real _node_634_ph_diff6__filtered_in;
char _node_634_ph_diff6__no_zc_flag_in[1];
char _node_634_ph_diff6__zc_flag_in[1];








real _node_645_ph_diff4__previous_correction_ref;
real _node_645_ph_diff4__sample_cnt_ref;
real _node_645_ph_diff4__previous_filtered_ref;
real _node_645_ph_diff4__filtered_ref;
real _node_645_ph_diff4__correction_ref;
char _node_645_ph_diff4__zc_flag_ref;
real _node_645_ph_diff4__phase_state;
real _node_645_ph_diff4__correction_in;
real _node_645_ph_diff4__previous_correction_in;
real _node_645_ph_diff4__sample_cnt_in;
real _node_645_ph_diff4__previous_filtered_in;
real _node_645_ph_diff4__filtered_in;
char _node_645_ph_diff4__no_zc_flag_in[1];
char _node_645_ph_diff4__zc_flag_in[1];


real _node_645_ph_diff6__previous_correction_ref;
real _node_645_ph_diff6__sample_cnt_ref;
real _node_645_ph_diff6__previous_filtered_ref;
real _node_645_ph_diff6__filtered_ref;
real _node_645_ph_diff6__correction_ref;
char _node_645_ph_diff6__zc_flag_ref;
real _node_645_ph_diff6__phase_state;
real _node_645_ph_diff6__correction_in;
real _node_645_ph_diff6__previous_correction_in;
real _node_645_ph_diff6__sample_cnt_in;
real _node_645_ph_diff6__previous_filtered_in;
real _node_645_ph_diff6__filtered_in;
char _node_645_ph_diff6__no_zc_flag_in[1];
char _node_645_ph_diff6__zc_flag_in[1];








real _node_646_ph_diff4__previous_correction_ref;
real _node_646_ph_diff4__sample_cnt_ref;
real _node_646_ph_diff4__previous_filtered_ref;
real _node_646_ph_diff4__filtered_ref;
real _node_646_ph_diff4__correction_ref;
char _node_646_ph_diff4__zc_flag_ref;
real _node_646_ph_diff4__phase_state;
real _node_646_ph_diff4__correction_in;
real _node_646_ph_diff4__previous_correction_in;
real _node_646_ph_diff4__sample_cnt_in;
real _node_646_ph_diff4__previous_filtered_in;
real _node_646_ph_diff4__filtered_in;
char _node_646_ph_diff4__no_zc_flag_in[1];
char _node_646_ph_diff4__zc_flag_in[1];


real _node_646_ph_diff6__previous_correction_ref;
real _node_646_ph_diff6__sample_cnt_ref;
real _node_646_ph_diff6__previous_filtered_ref;
real _node_646_ph_diff6__filtered_ref;
real _node_646_ph_diff6__correction_ref;
char _node_646_ph_diff6__zc_flag_ref;
real _node_646_ph_diff6__phase_state;
real _node_646_ph_diff6__correction_in;
real _node_646_ph_diff6__previous_correction_in;
real _node_646_ph_diff6__sample_cnt_in;
real _node_646_ph_diff6__previous_filtered_in;
real _node_646_ph_diff6__filtered_in;
char _node_646_ph_diff6__no_zc_flag_in[1];
char _node_646_ph_diff6__zc_flag_in[1];





real _node_652_ph_diff5__previous_correction_ref;
real _node_652_ph_diff5__sample_cnt_ref;
real _node_652_ph_diff5__previous_filtered_ref;
real _node_652_ph_diff5__filtered_ref;
real _node_652_ph_diff5__correction_ref;
char _node_652_ph_diff5__zc_flag_ref;
real _node_652_ph_diff5__phase_state;
real _node_652_ph_diff5__correction_in;
real _node_652_ph_diff5__previous_correction_in;
real _node_652_ph_diff5__sample_cnt_in;
real _node_652_ph_diff5__previous_filtered_in;
real _node_652_ph_diff5__filtered_in;
char _node_652_ph_diff5__no_zc_flag_in[1];
char _node_652_ph_diff5__zc_flag_in[1];











real _node_671_ph_diff4__previous_correction_ref;
real _node_671_ph_diff4__sample_cnt_ref;
real _node_671_ph_diff4__previous_filtered_ref;
real _node_671_ph_diff4__filtered_ref;
real _node_671_ph_diff4__correction_ref;
char _node_671_ph_diff4__zc_flag_ref;
real _node_671_ph_diff4__phase_state;
real _node_671_ph_diff4__correction_in;
real _node_671_ph_diff4__previous_correction_in;
real _node_671_ph_diff4__sample_cnt_in;
real _node_671_ph_diff4__previous_filtered_in;
real _node_671_ph_diff4__filtered_in;
char _node_671_ph_diff4__no_zc_flag_in[1];
char _node_671_ph_diff4__zc_flag_in[1];


real _node_671_ph_diff5__previous_correction_ref;
real _node_671_ph_diff5__sample_cnt_ref;
real _node_671_ph_diff5__previous_filtered_ref;
real _node_671_ph_diff5__filtered_ref;
real _node_671_ph_diff5__correction_ref;
char _node_671_ph_diff5__zc_flag_ref;
real _node_671_ph_diff5__phase_state;
real _node_671_ph_diff5__correction_in;
real _node_671_ph_diff5__previous_correction_in;
real _node_671_ph_diff5__sample_cnt_in;
real _node_671_ph_diff5__previous_filtered_in;
real _node_671_ph_diff5__filtered_in;
char _node_671_ph_diff5__no_zc_flag_in[1];
char _node_671_ph_diff5__zc_flag_in[1];


real _node_671_ph_diff6__previous_correction_ref;
real _node_671_ph_diff6__sample_cnt_ref;
real _node_671_ph_diff6__previous_filtered_ref;
real _node_671_ph_diff6__filtered_ref;
real _node_671_ph_diff6__correction_ref;
char _node_671_ph_diff6__zc_flag_ref;
real _node_671_ph_diff6__phase_state;
real _node_671_ph_diff6__correction_in;
real _node_671_ph_diff6__previous_correction_in;
real _node_671_ph_diff6__sample_cnt_in;
real _node_671_ph_diff6__previous_filtered_in;
real _node_671_ph_diff6__filtered_in;
char _node_671_ph_diff6__no_zc_flag_in[1];
char _node_671_ph_diff6__zc_flag_in[1];











real _node_675_ph_diff4__previous_correction_ref;
real _node_675_ph_diff4__sample_cnt_ref;
real _node_675_ph_diff4__previous_filtered_ref;
real _node_675_ph_diff4__filtered_ref;
real _node_675_ph_diff4__correction_ref;
char _node_675_ph_diff4__zc_flag_ref;
real _node_675_ph_diff4__phase_state;
real _node_675_ph_diff4__correction_in;
real _node_675_ph_diff4__previous_correction_in;
real _node_675_ph_diff4__sample_cnt_in;
real _node_675_ph_diff4__previous_filtered_in;
real _node_675_ph_diff4__filtered_in;
char _node_675_ph_diff4__no_zc_flag_in[1];
char _node_675_ph_diff4__zc_flag_in[1];


real _node_675_ph_diff5__previous_correction_ref;
real _node_675_ph_diff5__sample_cnt_ref;
real _node_675_ph_diff5__previous_filtered_ref;
real _node_675_ph_diff5__filtered_ref;
real _node_675_ph_diff5__correction_ref;
char _node_675_ph_diff5__zc_flag_ref;
real _node_675_ph_diff5__phase_state;
real _node_675_ph_diff5__correction_in;
real _node_675_ph_diff5__previous_correction_in;
real _node_675_ph_diff5__sample_cnt_in;
real _node_675_ph_diff5__previous_filtered_in;
real _node_675_ph_diff5__filtered_in;
char _node_675_ph_diff5__no_zc_flag_in[1];
char _node_675_ph_diff5__zc_flag_in[1];


real _node_675_ph_diff6__previous_correction_ref;
real _node_675_ph_diff6__sample_cnt_ref;
real _node_675_ph_diff6__previous_filtered_ref;
real _node_675_ph_diff6__filtered_ref;
real _node_675_ph_diff6__correction_ref;
char _node_675_ph_diff6__zc_flag_ref;
real _node_675_ph_diff6__phase_state;
real _node_675_ph_diff6__correction_in;
real _node_675_ph_diff6__previous_correction_in;
real _node_675_ph_diff6__sample_cnt_in;
real _node_675_ph_diff6__previous_filtered_in;
real _node_675_ph_diff6__filtered_in;
char _node_675_ph_diff6__no_zc_flag_in[1];
char _node_675_ph_diff6__zc_flag_in[1];











real _node_680_ph_diff4__previous_correction_ref;
real _node_680_ph_diff4__sample_cnt_ref;
real _node_680_ph_diff4__previous_filtered_ref;
real _node_680_ph_diff4__filtered_ref;
real _node_680_ph_diff4__correction_ref;
char _node_680_ph_diff4__zc_flag_ref;
real _node_680_ph_diff4__phase_state;
real _node_680_ph_diff4__correction_in;
real _node_680_ph_diff4__previous_correction_in;
real _node_680_ph_diff4__sample_cnt_in;
real _node_680_ph_diff4__previous_filtered_in;
real _node_680_ph_diff4__filtered_in;
char _node_680_ph_diff4__no_zc_flag_in[1];
char _node_680_ph_diff4__zc_flag_in[1];


real _node_680_ph_diff5__previous_correction_ref;
real _node_680_ph_diff5__sample_cnt_ref;
real _node_680_ph_diff5__previous_filtered_ref;
real _node_680_ph_diff5__filtered_ref;
real _node_680_ph_diff5__correction_ref;
char _node_680_ph_diff5__zc_flag_ref;
real _node_680_ph_diff5__phase_state;
real _node_680_ph_diff5__correction_in;
real _node_680_ph_diff5__previous_correction_in;
real _node_680_ph_diff5__sample_cnt_in;
real _node_680_ph_diff5__previous_filtered_in;
real _node_680_ph_diff5__filtered_in;
char _node_680_ph_diff5__no_zc_flag_in[1];
char _node_680_ph_diff5__zc_flag_in[1];


real _node_680_ph_diff6__previous_correction_ref;
real _node_680_ph_diff6__sample_cnt_ref;
real _node_680_ph_diff6__previous_filtered_ref;
real _node_680_ph_diff6__filtered_ref;
real _node_680_ph_diff6__correction_ref;
char _node_680_ph_diff6__zc_flag_ref;
real _node_680_ph_diff6__phase_state;
real _node_680_ph_diff6__correction_in;
real _node_680_ph_diff6__previous_correction_in;
real _node_680_ph_diff6__sample_cnt_in;
real _node_680_ph_diff6__previous_filtered_in;
real _node_680_ph_diff6__filtered_in;
char _node_680_ph_diff6__no_zc_flag_in[1];
char _node_680_ph_diff6__zc_flag_in[1];








real _node_684_ph_diff4__previous_correction_ref;
real _node_684_ph_diff4__sample_cnt_ref;
real _node_684_ph_diff4__previous_filtered_ref;
real _node_684_ph_diff4__filtered_ref;
real _node_684_ph_diff4__correction_ref;
char _node_684_ph_diff4__zc_flag_ref;
real _node_684_ph_diff4__phase_state;
real _node_684_ph_diff4__correction_in;
real _node_684_ph_diff4__previous_correction_in;
real _node_684_ph_diff4__sample_cnt_in;
real _node_684_ph_diff4__previous_filtered_in;
real _node_684_ph_diff4__filtered_in;
char _node_684_ph_diff4__no_zc_flag_in[1];
char _node_684_ph_diff4__zc_flag_in[1];


real _node_684_ph_diff5__previous_correction_ref;
real _node_684_ph_diff5__sample_cnt_ref;
real _node_684_ph_diff5__previous_filtered_ref;
real _node_684_ph_diff5__filtered_ref;
real _node_684_ph_diff5__correction_ref;
char _node_684_ph_diff5__zc_flag_ref;
real _node_684_ph_diff5__phase_state;
real _node_684_ph_diff5__correction_in;
real _node_684_ph_diff5__previous_correction_in;
real _node_684_ph_diff5__sample_cnt_in;
real _node_684_ph_diff5__previous_filtered_in;
real _node_684_ph_diff5__filtered_in;
char _node_684_ph_diff5__no_zc_flag_in[1];
char _node_684_ph_diff5__zc_flag_in[1];











real _node_692_ph_diff4__previous_correction_ref;
real _node_692_ph_diff4__sample_cnt_ref;
real _node_692_ph_diff4__previous_filtered_ref;
real _node_692_ph_diff4__filtered_ref;
real _node_692_ph_diff4__correction_ref;
char _node_692_ph_diff4__zc_flag_ref;
real _node_692_ph_diff4__phase_state;
real _node_692_ph_diff4__correction_in;
real _node_692_ph_diff4__previous_correction_in;
real _node_692_ph_diff4__sample_cnt_in;
real _node_692_ph_diff4__previous_filtered_in;
real _node_692_ph_diff4__filtered_in;
char _node_692_ph_diff4__no_zc_flag_in[1];
char _node_692_ph_diff4__zc_flag_in[1];


real _node_692_ph_diff5__previous_correction_ref;
real _node_692_ph_diff5__sample_cnt_ref;
real _node_692_ph_diff5__previous_filtered_ref;
real _node_692_ph_diff5__filtered_ref;
real _node_692_ph_diff5__correction_ref;
char _node_692_ph_diff5__zc_flag_ref;
real _node_692_ph_diff5__phase_state;
real _node_692_ph_diff5__correction_in;
real _node_692_ph_diff5__previous_correction_in;
real _node_692_ph_diff5__sample_cnt_in;
real _node_692_ph_diff5__previous_filtered_in;
real _node_692_ph_diff5__filtered_in;
char _node_692_ph_diff5__no_zc_flag_in[1];
char _node_692_ph_diff5__zc_flag_in[1];


real _node_692_ph_diff6__previous_correction_ref;
real _node_692_ph_diff6__sample_cnt_ref;
real _node_692_ph_diff6__previous_filtered_ref;
real _node_692_ph_diff6__filtered_ref;
real _node_692_ph_diff6__correction_ref;
char _node_692_ph_diff6__zc_flag_ref;
real _node_692_ph_diff6__phase_state;
real _node_692_ph_diff6__correction_in;
real _node_692_ph_diff6__previous_correction_in;
real _node_692_ph_diff6__sample_cnt_in;
real _node_692_ph_diff6__previous_filtered_in;
real _node_692_ph_diff6__filtered_in;
char _node_692_ph_diff6__no_zc_flag_in[1];
char _node_692_ph_diff6__zc_flag_in[1];








double _msr_632_671_rms6__square_sum;
double _msr_632_671_rms6__sample_cnt;
double _msr_632_671_rms6__period_cnt;
double _msr_632_671_rms6__db_timer;
double _msr_632_671_rms6__previous_filtered_value;
double _msr_632_671_rms6__previous_correction;
double _msr_632_671_rms6__previous_value;
double _msr_632_671_rms6__correction;
double _msr_632_671_rms6__filtered_value;
double _msr_632_671_rms6__out_state;
double _msr_632_671_rms5__square_sum;
double _msr_632_671_rms5__sample_cnt;
double _msr_632_671_rms5__period_cnt;
double _msr_632_671_rms5__db_timer;
double _msr_632_671_rms5__previous_filtered_value;
double _msr_632_671_rms5__previous_correction;
double _msr_632_671_rms5__previous_value;
double _msr_632_671_rms5__correction;
double _msr_632_671_rms5__filtered_value;
double _msr_632_671_rms5__out_state;
double _msr_632_671_rms4__square_sum;
double _msr_632_671_rms4__sample_cnt;
double _msr_632_671_rms4__period_cnt;
double _msr_632_671_rms4__db_timer;
double _msr_632_671_rms4__previous_filtered_value;
double _msr_632_671_rms4__previous_correction;
double _msr_632_671_rms4__previous_value;
double _msr_632_671_rms4__correction;
double _msr_632_671_rms4__filtered_value;
double _msr_632_671_rms4__out_state;








double _node_611_rms4__square_sum;
double _node_611_rms4__sample_cnt;
double _node_611_rms4__period_cnt;
double _node_611_rms4__db_timer;
double _node_611_rms4__previous_filtered_value;
double _node_611_rms4__previous_correction;
double _node_611_rms4__previous_value;
double _node_611_rms4__correction;
double _node_611_rms4__filtered_value;
double _node_611_rms4__out_state;


double _node_632_rms6__square_sum;
double _node_632_rms6__sample_cnt;
double _node_632_rms6__period_cnt;
double _node_632_rms6__db_timer;
double _node_632_rms6__previous_filtered_value;
double _node_632_rms6__previous_correction;
double _node_632_rms6__previous_value;
double _node_632_rms6__correction;
double _node_632_rms6__filtered_value;
double _node_632_rms6__out_state;
double _node_632_rms5__square_sum;
double _node_632_rms5__sample_cnt;
double _node_632_rms5__period_cnt;
double _node_632_rms5__db_timer;
double _node_632_rms5__previous_filtered_value;
double _node_632_rms5__previous_correction;
double _node_632_rms5__previous_value;
double _node_632_rms5__correction;
double _node_632_rms5__filtered_value;
double _node_632_rms5__out_state;
double _node_632_power_meter1__filter_1_output_k_minus_1;
double _node_632_power_meter1__filter_1_input_k_minus_1;
double _node_632_power_meter1__filter_1_output_k_minus_1Q;
double _node_632_power_meter1__filter_1_input_k_minus_1Q;
double _node_632_power_meter1__filter_1_output_k_minus_1P0;
double _node_632_power_meter1__filter_1_input_k_minus_1P0;
double _node_632_rms4__square_sum;
double _node_632_rms4__sample_cnt;
double _node_632_rms4__period_cnt;
double _node_632_rms4__db_timer;
double _node_632_rms4__previous_filtered_value;
double _node_632_rms4__previous_correction;
double _node_632_rms4__previous_value;
double _node_632_rms4__correction;
double _node_632_rms4__filtered_value;
double _node_632_rms4__out_state;








double _node_633_rms6__square_sum;
double _node_633_rms6__sample_cnt;
double _node_633_rms6__period_cnt;
double _node_633_rms6__db_timer;
double _node_633_rms6__previous_filtered_value;
double _node_633_rms6__previous_correction;
double _node_633_rms6__previous_value;
double _node_633_rms6__correction;
double _node_633_rms6__filtered_value;
double _node_633_rms6__out_state;
double _node_633_rms5__square_sum;
double _node_633_rms5__sample_cnt;
double _node_633_rms5__period_cnt;
double _node_633_rms5__db_timer;
double _node_633_rms5__previous_filtered_value;
double _node_633_rms5__previous_correction;
double _node_633_rms5__previous_value;
double _node_633_rms5__correction;
double _node_633_rms5__filtered_value;
double _node_633_rms5__out_state;
double _node_633_rms4__square_sum;
double _node_633_rms4__sample_cnt;
double _node_633_rms4__period_cnt;
double _node_633_rms4__db_timer;
double _node_633_rms4__previous_filtered_value;
double _node_633_rms4__previous_correction;
double _node_633_rms4__previous_value;
double _node_633_rms4__correction;
double _node_633_rms4__filtered_value;
double _node_633_rms4__out_state;








double _node_634_rms6__square_sum;
double _node_634_rms6__sample_cnt;
double _node_634_rms6__period_cnt;
double _node_634_rms6__db_timer;
double _node_634_rms6__previous_filtered_value;
double _node_634_rms6__previous_correction;
double _node_634_rms6__previous_value;
double _node_634_rms6__correction;
double _node_634_rms6__filtered_value;
double _node_634_rms6__out_state;
double _node_634_rms5__square_sum;
double _node_634_rms5__sample_cnt;
double _node_634_rms5__period_cnt;
double _node_634_rms5__db_timer;
double _node_634_rms5__previous_filtered_value;
double _node_634_rms5__previous_correction;
double _node_634_rms5__previous_value;
double _node_634_rms5__correction;
double _node_634_rms5__filtered_value;
double _node_634_rms5__out_state;
double _node_634_rms4__square_sum;
double _node_634_rms4__sample_cnt;
double _node_634_rms4__period_cnt;
double _node_634_rms4__db_timer;
double _node_634_rms4__previous_filtered_value;
double _node_634_rms4__previous_correction;
double _node_634_rms4__previous_value;
double _node_634_rms4__correction;
double _node_634_rms4__filtered_value;
double _node_634_rms4__out_state;








double _node_645_rms5__square_sum;
double _node_645_rms5__sample_cnt;
double _node_645_rms5__period_cnt;
double _node_645_rms5__db_timer;
double _node_645_rms5__previous_filtered_value;
double _node_645_rms5__previous_correction;
double _node_645_rms5__previous_value;
double _node_645_rms5__correction;
double _node_645_rms5__filtered_value;
double _node_645_rms5__out_state;
double _node_645_rms4__square_sum;
double _node_645_rms4__sample_cnt;
double _node_645_rms4__period_cnt;
double _node_645_rms4__db_timer;
double _node_645_rms4__previous_filtered_value;
double _node_645_rms4__previous_correction;
double _node_645_rms4__previous_value;
double _node_645_rms4__correction;
double _node_645_rms4__filtered_value;
double _node_645_rms4__out_state;





double _node_646_rms5__square_sum;
double _node_646_rms5__sample_cnt;
double _node_646_rms5__period_cnt;
double _node_646_rms5__db_timer;
double _node_646_rms5__previous_filtered_value;
double _node_646_rms5__previous_correction;
double _node_646_rms5__previous_value;
double _node_646_rms5__correction;
double _node_646_rms5__filtered_value;
double _node_646_rms5__out_state;
double _node_646_rms4__square_sum;
double _node_646_rms4__sample_cnt;
double _node_646_rms4__period_cnt;
double _node_646_rms4__db_timer;
double _node_646_rms4__previous_filtered_value;
double _node_646_rms4__previous_correction;
double _node_646_rms4__previous_value;
double _node_646_rms4__correction;
double _node_646_rms4__filtered_value;
double _node_646_rms4__out_state;





double _node_652_rms6__square_sum;
double _node_652_rms6__sample_cnt;
double _node_652_rms6__period_cnt;
double _node_652_rms6__db_timer;
double _node_652_rms6__previous_filtered_value;
double _node_652_rms6__previous_correction;
double _node_652_rms6__previous_value;
double _node_652_rms6__correction;
double _node_652_rms6__filtered_value;
double _node_652_rms6__out_state;


double _node_671_rms6__square_sum;
double _node_671_rms6__sample_cnt;
double _node_671_rms6__period_cnt;
double _node_671_rms6__db_timer;
double _node_671_rms6__previous_filtered_value;
double _node_671_rms6__previous_correction;
double _node_671_rms6__previous_value;
double _node_671_rms6__correction;
double _node_671_rms6__filtered_value;
double _node_671_rms6__out_state;
double _node_671_rms5__square_sum;
double _node_671_rms5__sample_cnt;
double _node_671_rms5__period_cnt;
double _node_671_rms5__db_timer;
double _node_671_rms5__previous_filtered_value;
double _node_671_rms5__previous_correction;
double _node_671_rms5__previous_value;
double _node_671_rms5__correction;
double _node_671_rms5__filtered_value;
double _node_671_rms5__out_state;
double _node_671_rms4__square_sum;
double _node_671_rms4__sample_cnt;
double _node_671_rms4__period_cnt;
double _node_671_rms4__db_timer;
double _node_671_rms4__previous_filtered_value;
double _node_671_rms4__previous_correction;
double _node_671_rms4__previous_value;
double _node_671_rms4__correction;
double _node_671_rms4__filtered_value;
double _node_671_rms4__out_state;








double _node_675_rms6__square_sum;
double _node_675_rms6__sample_cnt;
double _node_675_rms6__period_cnt;
double _node_675_rms6__db_timer;
double _node_675_rms6__previous_filtered_value;
double _node_675_rms6__previous_correction;
double _node_675_rms6__previous_value;
double _node_675_rms6__correction;
double _node_675_rms6__filtered_value;
double _node_675_rms6__out_state;
double _node_675_rms5__square_sum;
double _node_675_rms5__sample_cnt;
double _node_675_rms5__period_cnt;
double _node_675_rms5__db_timer;
double _node_675_rms5__previous_filtered_value;
double _node_675_rms5__previous_correction;
double _node_675_rms5__previous_value;
double _node_675_rms5__correction;
double _node_675_rms5__filtered_value;
double _node_675_rms5__out_state;
double _node_675_rms4__square_sum;
double _node_675_rms4__sample_cnt;
double _node_675_rms4__period_cnt;
double _node_675_rms4__db_timer;
double _node_675_rms4__previous_filtered_value;
double _node_675_rms4__previous_correction;
double _node_675_rms4__previous_value;
double _node_675_rms4__correction;
double _node_675_rms4__filtered_value;
double _node_675_rms4__out_state;








double _node_680_rms6__square_sum;
double _node_680_rms6__sample_cnt;
double _node_680_rms6__period_cnt;
double _node_680_rms6__db_timer;
double _node_680_rms6__previous_filtered_value;
double _node_680_rms6__previous_correction;
double _node_680_rms6__previous_value;
double _node_680_rms6__correction;
double _node_680_rms6__filtered_value;
double _node_680_rms6__out_state;
double _node_680_rms5__square_sum;
double _node_680_rms5__sample_cnt;
double _node_680_rms5__period_cnt;
double _node_680_rms5__db_timer;
double _node_680_rms5__previous_filtered_value;
double _node_680_rms5__previous_correction;
double _node_680_rms5__previous_value;
double _node_680_rms5__correction;
double _node_680_rms5__filtered_value;
double _node_680_rms5__out_state;
double _node_680_rms4__square_sum;
double _node_680_rms4__sample_cnt;
double _node_680_rms4__period_cnt;
double _node_680_rms4__db_timer;
double _node_680_rms4__previous_filtered_value;
double _node_680_rms4__previous_correction;
double _node_680_rms4__previous_value;
double _node_680_rms4__correction;
double _node_680_rms4__filtered_value;
double _node_680_rms4__out_state;








double _node_684_rms6__square_sum;
double _node_684_rms6__sample_cnt;
double _node_684_rms6__period_cnt;
double _node_684_rms6__db_timer;
double _node_684_rms6__previous_filtered_value;
double _node_684_rms6__previous_correction;
double _node_684_rms6__previous_value;
double _node_684_rms6__correction;
double _node_684_rms6__filtered_value;
double _node_684_rms6__out_state;
double _node_684_rms4__square_sum;
double _node_684_rms4__sample_cnt;
double _node_684_rms4__period_cnt;
double _node_684_rms4__db_timer;
double _node_684_rms4__previous_filtered_value;
double _node_684_rms4__previous_correction;
double _node_684_rms4__previous_value;
double _node_684_rms4__correction;
double _node_684_rms4__filtered_value;
double _node_684_rms4__out_state;





double _node_692_rms6__square_sum;
double _node_692_rms6__sample_cnt;
double _node_692_rms6__period_cnt;
double _node_692_rms6__db_timer;
double _node_692_rms6__previous_filtered_value;
double _node_692_rms6__previous_correction;
double _node_692_rms6__previous_value;
double _node_692_rms6__correction;
double _node_692_rms6__filtered_value;
double _node_692_rms6__out_state;
double _node_692_rms5__square_sum;
double _node_692_rms5__sample_cnt;
double _node_692_rms5__period_cnt;
double _node_692_rms5__db_timer;
double _node_692_rms5__previous_filtered_value;
double _node_692_rms5__previous_correction;
double _node_692_rms5__previous_value;
double _node_692_rms5__correction;
double _node_692_rms5__filtered_value;
double _node_692_rms5__out_state;
double _node_692_rms4__square_sum;
double _node_692_rms4__sample_cnt;
double _node_692_rms4__period_cnt;
double _node_692_rms4__db_timer;
double _node_692_rms4__previous_filtered_value;
double _node_692_rms4__previous_correction;
double _node_692_rms4__previous_value;
double _node_692_rms4__correction;
double _node_692_rms4__filtered_value;
double _node_692_rms4__out_state;





































































































































































































//@cmp.svar.end

// IO shared variables

//
// Tunable parameters
//
static struct Tunable_params {
} __attribute__((__packed__)) tunable_params;

void *tunable_params_dev0_cpu0_ptr = &tunable_params;

// Dll function pointers
#if defined(_WIN64)
#else
// Define handles for loading dlls
#endif





// generated using template: \templates\virtual_hil\fmi_custom_logger_fncs.template---------------------------------
#include <stdarg.h>



//
// DMA buffers
//

































































































































































































































































































































































































































































































































































































































































































































































// generated using template: virtual_hil/custom_functions.template---------------------------------
void ReInit_user_sp_cpu0_dev0() {
#if DEBUG_MODE
    printf("\n\rReInitTimer");
#endif
    //@cmp.init.block.start
    {
        _msr_632_671_ph_diff4__previous_correction_ref = 0;
        _msr_632_671_ph_diff4__sample_cnt_ref = 0;
        _msr_632_671_ph_diff4__previous_filtered_ref = 0;
        _msr_632_671_ph_diff4__filtered_ref = 0;
        _msr_632_671_ph_diff4__correction_ref = 0;
        _msr_632_671_ph_diff4__zc_flag_ref = 0;
        _msr_632_671_ph_diff4__phase_state = 0;
        _msr_632_671_ph_diff4__correction_in = 0;
        _msr_632_671_ph_diff4__previous_correction_in = 0;
        _msr_632_671_ph_diff4__sample_cnt_in = 0;
        _msr_632_671_ph_diff4__previous_filtered_in = 0;
        _msr_632_671_ph_diff4__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _msr_632_671_ph_diff4__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _msr_632_671_ph_diff4__zc_flag_in[0] = 0;
        }
    }
    {
        _msr_632_671_ph_diff5__previous_correction_ref = 0;
        _msr_632_671_ph_diff5__sample_cnt_ref = 0;
        _msr_632_671_ph_diff5__previous_filtered_ref = 0;
        _msr_632_671_ph_diff5__filtered_ref = 0;
        _msr_632_671_ph_diff5__correction_ref = 0;
        _msr_632_671_ph_diff5__zc_flag_ref = 0;
        _msr_632_671_ph_diff5__phase_state = 0;
        _msr_632_671_ph_diff5__correction_in = 0;
        _msr_632_671_ph_diff5__previous_correction_in = 0;
        _msr_632_671_ph_diff5__sample_cnt_in = 0;
        _msr_632_671_ph_diff5__previous_filtered_in = 0;
        _msr_632_671_ph_diff5__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _msr_632_671_ph_diff5__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _msr_632_671_ph_diff5__zc_flag_in[0] = 0;
        }
    }
    {
        _msr_632_671_ph_diff6__previous_correction_ref = 0;
        _msr_632_671_ph_diff6__sample_cnt_ref = 0;
        _msr_632_671_ph_diff6__previous_filtered_ref = 0;
        _msr_632_671_ph_diff6__filtered_ref = 0;
        _msr_632_671_ph_diff6__correction_ref = 0;
        _msr_632_671_ph_diff6__zc_flag_ref = 0;
        _msr_632_671_ph_diff6__phase_state = 0;
        _msr_632_671_ph_diff6__correction_in = 0;
        _msr_632_671_ph_diff6__previous_correction_in = 0;
        _msr_632_671_ph_diff6__sample_cnt_in = 0;
        _msr_632_671_ph_diff6__previous_filtered_in = 0;
        _msr_632_671_ph_diff6__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _msr_632_671_ph_diff6__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _msr_632_671_ph_diff6__zc_flag_in[0] = 0;
        }
    }
    {
        _node_611_ph_diff4__previous_correction_ref = 0;
        _node_611_ph_diff4__sample_cnt_ref = 0;
        _node_611_ph_diff4__previous_filtered_ref = 0;
        _node_611_ph_diff4__filtered_ref = 0;
        _node_611_ph_diff4__correction_ref = 0;
        _node_611_ph_diff4__zc_flag_ref = 0;
        _node_611_ph_diff4__phase_state = 0;
        _node_611_ph_diff4__correction_in = 0;
        _node_611_ph_diff4__previous_correction_in = 0;
        _node_611_ph_diff4__sample_cnt_in = 0;
        _node_611_ph_diff4__previous_filtered_in = 0;
        _node_611_ph_diff4__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_611_ph_diff4__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_611_ph_diff4__zc_flag_in[0] = 0;
        }
    }
    {
        _node_632_ph_diff4__previous_correction_ref = 0;
        _node_632_ph_diff4__sample_cnt_ref = 0;
        _node_632_ph_diff4__previous_filtered_ref = 0;
        _node_632_ph_diff4__filtered_ref = 0;
        _node_632_ph_diff4__correction_ref = 0;
        _node_632_ph_diff4__zc_flag_ref = 0;
        _node_632_ph_diff4__phase_state = 0;
        _node_632_ph_diff4__correction_in = 0;
        _node_632_ph_diff4__previous_correction_in = 0;
        _node_632_ph_diff4__sample_cnt_in = 0;
        _node_632_ph_diff4__previous_filtered_in = 0;
        _node_632_ph_diff4__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_632_ph_diff4__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_632_ph_diff4__zc_flag_in[0] = 0;
        }
    }
    {
        _node_632_ph_diff5__previous_correction_ref = 0;
        _node_632_ph_diff5__sample_cnt_ref = 0;
        _node_632_ph_diff5__previous_filtered_ref = 0;
        _node_632_ph_diff5__filtered_ref = 0;
        _node_632_ph_diff5__correction_ref = 0;
        _node_632_ph_diff5__zc_flag_ref = 0;
        _node_632_ph_diff5__phase_state = 0;
        _node_632_ph_diff5__correction_in = 0;
        _node_632_ph_diff5__previous_correction_in = 0;
        _node_632_ph_diff5__sample_cnt_in = 0;
        _node_632_ph_diff5__previous_filtered_in = 0;
        _node_632_ph_diff5__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_632_ph_diff5__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_632_ph_diff5__zc_flag_in[0] = 0;
        }
    }
    {
        _node_632_ph_diff6__previous_correction_ref = 0;
        _node_632_ph_diff6__sample_cnt_ref = 0;
        _node_632_ph_diff6__previous_filtered_ref = 0;
        _node_632_ph_diff6__filtered_ref = 0;
        _node_632_ph_diff6__correction_ref = 0;
        _node_632_ph_diff6__zc_flag_ref = 0;
        _node_632_ph_diff6__phase_state = 0;
        _node_632_ph_diff6__correction_in = 0;
        _node_632_ph_diff6__previous_correction_in = 0;
        _node_632_ph_diff6__sample_cnt_in = 0;
        _node_632_ph_diff6__previous_filtered_in = 0;
        _node_632_ph_diff6__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_632_ph_diff6__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_632_ph_diff6__zc_flag_in[0] = 0;
        }
    }
    {
        _node_633_ph_diff4__previous_correction_ref = 0;
        _node_633_ph_diff4__sample_cnt_ref = 0;
        _node_633_ph_diff4__previous_filtered_ref = 0;
        _node_633_ph_diff4__filtered_ref = 0;
        _node_633_ph_diff4__correction_ref = 0;
        _node_633_ph_diff4__zc_flag_ref = 0;
        _node_633_ph_diff4__phase_state = 0;
        _node_633_ph_diff4__correction_in = 0;
        _node_633_ph_diff4__previous_correction_in = 0;
        _node_633_ph_diff4__sample_cnt_in = 0;
        _node_633_ph_diff4__previous_filtered_in = 0;
        _node_633_ph_diff4__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_633_ph_diff4__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_633_ph_diff4__zc_flag_in[0] = 0;
        }
    }
    {
        _node_633_ph_diff5__previous_correction_ref = 0;
        _node_633_ph_diff5__sample_cnt_ref = 0;
        _node_633_ph_diff5__previous_filtered_ref = 0;
        _node_633_ph_diff5__filtered_ref = 0;
        _node_633_ph_diff5__correction_ref = 0;
        _node_633_ph_diff5__zc_flag_ref = 0;
        _node_633_ph_diff5__phase_state = 0;
        _node_633_ph_diff5__correction_in = 0;
        _node_633_ph_diff5__previous_correction_in = 0;
        _node_633_ph_diff5__sample_cnt_in = 0;
        _node_633_ph_diff5__previous_filtered_in = 0;
        _node_633_ph_diff5__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_633_ph_diff5__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_633_ph_diff5__zc_flag_in[0] = 0;
        }
    }
    {
        _node_633_ph_diff6__previous_correction_ref = 0;
        _node_633_ph_diff6__sample_cnt_ref = 0;
        _node_633_ph_diff6__previous_filtered_ref = 0;
        _node_633_ph_diff6__filtered_ref = 0;
        _node_633_ph_diff6__correction_ref = 0;
        _node_633_ph_diff6__zc_flag_ref = 0;
        _node_633_ph_diff6__phase_state = 0;
        _node_633_ph_diff6__correction_in = 0;
        _node_633_ph_diff6__previous_correction_in = 0;
        _node_633_ph_diff6__sample_cnt_in = 0;
        _node_633_ph_diff6__previous_filtered_in = 0;
        _node_633_ph_diff6__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_633_ph_diff6__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_633_ph_diff6__zc_flag_in[0] = 0;
        }
    }
    {
        _node_634_ph_diff4__previous_correction_ref = 0;
        _node_634_ph_diff4__sample_cnt_ref = 0;
        _node_634_ph_diff4__previous_filtered_ref = 0;
        _node_634_ph_diff4__filtered_ref = 0;
        _node_634_ph_diff4__correction_ref = 0;
        _node_634_ph_diff4__zc_flag_ref = 0;
        _node_634_ph_diff4__phase_state = 0;
        _node_634_ph_diff4__correction_in = 0;
        _node_634_ph_diff4__previous_correction_in = 0;
        _node_634_ph_diff4__sample_cnt_in = 0;
        _node_634_ph_diff4__previous_filtered_in = 0;
        _node_634_ph_diff4__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_634_ph_diff4__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_634_ph_diff4__zc_flag_in[0] = 0;
        }
    }
    {
        _node_634_ph_diff5__previous_correction_ref = 0;
        _node_634_ph_diff5__sample_cnt_ref = 0;
        _node_634_ph_diff5__previous_filtered_ref = 0;
        _node_634_ph_diff5__filtered_ref = 0;
        _node_634_ph_diff5__correction_ref = 0;
        _node_634_ph_diff5__zc_flag_ref = 0;
        _node_634_ph_diff5__phase_state = 0;
        _node_634_ph_diff5__correction_in = 0;
        _node_634_ph_diff5__previous_correction_in = 0;
        _node_634_ph_diff5__sample_cnt_in = 0;
        _node_634_ph_diff5__previous_filtered_in = 0;
        _node_634_ph_diff5__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_634_ph_diff5__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_634_ph_diff5__zc_flag_in[0] = 0;
        }
    }
    {
        _node_634_ph_diff6__previous_correction_ref = 0;
        _node_634_ph_diff6__sample_cnt_ref = 0;
        _node_634_ph_diff6__previous_filtered_ref = 0;
        _node_634_ph_diff6__filtered_ref = 0;
        _node_634_ph_diff6__correction_ref = 0;
        _node_634_ph_diff6__zc_flag_ref = 0;
        _node_634_ph_diff6__phase_state = 0;
        _node_634_ph_diff6__correction_in = 0;
        _node_634_ph_diff6__previous_correction_in = 0;
        _node_634_ph_diff6__sample_cnt_in = 0;
        _node_634_ph_diff6__previous_filtered_in = 0;
        _node_634_ph_diff6__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_634_ph_diff6__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_634_ph_diff6__zc_flag_in[0] = 0;
        }
    }
    {
        _node_645_ph_diff4__previous_correction_ref = 0;
        _node_645_ph_diff4__sample_cnt_ref = 0;
        _node_645_ph_diff4__previous_filtered_ref = 0;
        _node_645_ph_diff4__filtered_ref = 0;
        _node_645_ph_diff4__correction_ref = 0;
        _node_645_ph_diff4__zc_flag_ref = 0;
        _node_645_ph_diff4__phase_state = 0;
        _node_645_ph_diff4__correction_in = 0;
        _node_645_ph_diff4__previous_correction_in = 0;
        _node_645_ph_diff4__sample_cnt_in = 0;
        _node_645_ph_diff4__previous_filtered_in = 0;
        _node_645_ph_diff4__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_645_ph_diff4__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_645_ph_diff4__zc_flag_in[0] = 0;
        }
    }
    {
        _node_645_ph_diff6__previous_correction_ref = 0;
        _node_645_ph_diff6__sample_cnt_ref = 0;
        _node_645_ph_diff6__previous_filtered_ref = 0;
        _node_645_ph_diff6__filtered_ref = 0;
        _node_645_ph_diff6__correction_ref = 0;
        _node_645_ph_diff6__zc_flag_ref = 0;
        _node_645_ph_diff6__phase_state = 0;
        _node_645_ph_diff6__correction_in = 0;
        _node_645_ph_diff6__previous_correction_in = 0;
        _node_645_ph_diff6__sample_cnt_in = 0;
        _node_645_ph_diff6__previous_filtered_in = 0;
        _node_645_ph_diff6__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_645_ph_diff6__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_645_ph_diff6__zc_flag_in[0] = 0;
        }
    }
    {
        _node_646_ph_diff4__previous_correction_ref = 0;
        _node_646_ph_diff4__sample_cnt_ref = 0;
        _node_646_ph_diff4__previous_filtered_ref = 0;
        _node_646_ph_diff4__filtered_ref = 0;
        _node_646_ph_diff4__correction_ref = 0;
        _node_646_ph_diff4__zc_flag_ref = 0;
        _node_646_ph_diff4__phase_state = 0;
        _node_646_ph_diff4__correction_in = 0;
        _node_646_ph_diff4__previous_correction_in = 0;
        _node_646_ph_diff4__sample_cnt_in = 0;
        _node_646_ph_diff4__previous_filtered_in = 0;
        _node_646_ph_diff4__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_646_ph_diff4__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_646_ph_diff4__zc_flag_in[0] = 0;
        }
    }
    {
        _node_646_ph_diff6__previous_correction_ref = 0;
        _node_646_ph_diff6__sample_cnt_ref = 0;
        _node_646_ph_diff6__previous_filtered_ref = 0;
        _node_646_ph_diff6__filtered_ref = 0;
        _node_646_ph_diff6__correction_ref = 0;
        _node_646_ph_diff6__zc_flag_ref = 0;
        _node_646_ph_diff6__phase_state = 0;
        _node_646_ph_diff6__correction_in = 0;
        _node_646_ph_diff6__previous_correction_in = 0;
        _node_646_ph_diff6__sample_cnt_in = 0;
        _node_646_ph_diff6__previous_filtered_in = 0;
        _node_646_ph_diff6__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_646_ph_diff6__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_646_ph_diff6__zc_flag_in[0] = 0;
        }
    }
    {
        _node_652_ph_diff5__previous_correction_ref = 0;
        _node_652_ph_diff5__sample_cnt_ref = 0;
        _node_652_ph_diff5__previous_filtered_ref = 0;
        _node_652_ph_diff5__filtered_ref = 0;
        _node_652_ph_diff5__correction_ref = 0;
        _node_652_ph_diff5__zc_flag_ref = 0;
        _node_652_ph_diff5__phase_state = 0;
        _node_652_ph_diff5__correction_in = 0;
        _node_652_ph_diff5__previous_correction_in = 0;
        _node_652_ph_diff5__sample_cnt_in = 0;
        _node_652_ph_diff5__previous_filtered_in = 0;
        _node_652_ph_diff5__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_652_ph_diff5__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_652_ph_diff5__zc_flag_in[0] = 0;
        }
    }
    {
        _node_671_ph_diff4__previous_correction_ref = 0;
        _node_671_ph_diff4__sample_cnt_ref = 0;
        _node_671_ph_diff4__previous_filtered_ref = 0;
        _node_671_ph_diff4__filtered_ref = 0;
        _node_671_ph_diff4__correction_ref = 0;
        _node_671_ph_diff4__zc_flag_ref = 0;
        _node_671_ph_diff4__phase_state = 0;
        _node_671_ph_diff4__correction_in = 0;
        _node_671_ph_diff4__previous_correction_in = 0;
        _node_671_ph_diff4__sample_cnt_in = 0;
        _node_671_ph_diff4__previous_filtered_in = 0;
        _node_671_ph_diff4__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_671_ph_diff4__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_671_ph_diff4__zc_flag_in[0] = 0;
        }
    }
    {
        _node_671_ph_diff5__previous_correction_ref = 0;
        _node_671_ph_diff5__sample_cnt_ref = 0;
        _node_671_ph_diff5__previous_filtered_ref = 0;
        _node_671_ph_diff5__filtered_ref = 0;
        _node_671_ph_diff5__correction_ref = 0;
        _node_671_ph_diff5__zc_flag_ref = 0;
        _node_671_ph_diff5__phase_state = 0;
        _node_671_ph_diff5__correction_in = 0;
        _node_671_ph_diff5__previous_correction_in = 0;
        _node_671_ph_diff5__sample_cnt_in = 0;
        _node_671_ph_diff5__previous_filtered_in = 0;
        _node_671_ph_diff5__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_671_ph_diff5__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_671_ph_diff5__zc_flag_in[0] = 0;
        }
    }
    {
        _node_671_ph_diff6__previous_correction_ref = 0;
        _node_671_ph_diff6__sample_cnt_ref = 0;
        _node_671_ph_diff6__previous_filtered_ref = 0;
        _node_671_ph_diff6__filtered_ref = 0;
        _node_671_ph_diff6__correction_ref = 0;
        _node_671_ph_diff6__zc_flag_ref = 0;
        _node_671_ph_diff6__phase_state = 0;
        _node_671_ph_diff6__correction_in = 0;
        _node_671_ph_diff6__previous_correction_in = 0;
        _node_671_ph_diff6__sample_cnt_in = 0;
        _node_671_ph_diff6__previous_filtered_in = 0;
        _node_671_ph_diff6__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_671_ph_diff6__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_671_ph_diff6__zc_flag_in[0] = 0;
        }
    }
    {
        _node_675_ph_diff4__previous_correction_ref = 0;
        _node_675_ph_diff4__sample_cnt_ref = 0;
        _node_675_ph_diff4__previous_filtered_ref = 0;
        _node_675_ph_diff4__filtered_ref = 0;
        _node_675_ph_diff4__correction_ref = 0;
        _node_675_ph_diff4__zc_flag_ref = 0;
        _node_675_ph_diff4__phase_state = 0;
        _node_675_ph_diff4__correction_in = 0;
        _node_675_ph_diff4__previous_correction_in = 0;
        _node_675_ph_diff4__sample_cnt_in = 0;
        _node_675_ph_diff4__previous_filtered_in = 0;
        _node_675_ph_diff4__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_675_ph_diff4__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_675_ph_diff4__zc_flag_in[0] = 0;
        }
    }
    {
        _node_675_ph_diff5__previous_correction_ref = 0;
        _node_675_ph_diff5__sample_cnt_ref = 0;
        _node_675_ph_diff5__previous_filtered_ref = 0;
        _node_675_ph_diff5__filtered_ref = 0;
        _node_675_ph_diff5__correction_ref = 0;
        _node_675_ph_diff5__zc_flag_ref = 0;
        _node_675_ph_diff5__phase_state = 0;
        _node_675_ph_diff5__correction_in = 0;
        _node_675_ph_diff5__previous_correction_in = 0;
        _node_675_ph_diff5__sample_cnt_in = 0;
        _node_675_ph_diff5__previous_filtered_in = 0;
        _node_675_ph_diff5__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_675_ph_diff5__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_675_ph_diff5__zc_flag_in[0] = 0;
        }
    }
    {
        _node_675_ph_diff6__previous_correction_ref = 0;
        _node_675_ph_diff6__sample_cnt_ref = 0;
        _node_675_ph_diff6__previous_filtered_ref = 0;
        _node_675_ph_diff6__filtered_ref = 0;
        _node_675_ph_diff6__correction_ref = 0;
        _node_675_ph_diff6__zc_flag_ref = 0;
        _node_675_ph_diff6__phase_state = 0;
        _node_675_ph_diff6__correction_in = 0;
        _node_675_ph_diff6__previous_correction_in = 0;
        _node_675_ph_diff6__sample_cnt_in = 0;
        _node_675_ph_diff6__previous_filtered_in = 0;
        _node_675_ph_diff6__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_675_ph_diff6__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_675_ph_diff6__zc_flag_in[0] = 0;
        }
    }
    {
        _node_680_ph_diff4__previous_correction_ref = 0;
        _node_680_ph_diff4__sample_cnt_ref = 0;
        _node_680_ph_diff4__previous_filtered_ref = 0;
        _node_680_ph_diff4__filtered_ref = 0;
        _node_680_ph_diff4__correction_ref = 0;
        _node_680_ph_diff4__zc_flag_ref = 0;
        _node_680_ph_diff4__phase_state = 0;
        _node_680_ph_diff4__correction_in = 0;
        _node_680_ph_diff4__previous_correction_in = 0;
        _node_680_ph_diff4__sample_cnt_in = 0;
        _node_680_ph_diff4__previous_filtered_in = 0;
        _node_680_ph_diff4__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_680_ph_diff4__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_680_ph_diff4__zc_flag_in[0] = 0;
        }
    }
    {
        _node_680_ph_diff5__previous_correction_ref = 0;
        _node_680_ph_diff5__sample_cnt_ref = 0;
        _node_680_ph_diff5__previous_filtered_ref = 0;
        _node_680_ph_diff5__filtered_ref = 0;
        _node_680_ph_diff5__correction_ref = 0;
        _node_680_ph_diff5__zc_flag_ref = 0;
        _node_680_ph_diff5__phase_state = 0;
        _node_680_ph_diff5__correction_in = 0;
        _node_680_ph_diff5__previous_correction_in = 0;
        _node_680_ph_diff5__sample_cnt_in = 0;
        _node_680_ph_diff5__previous_filtered_in = 0;
        _node_680_ph_diff5__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_680_ph_diff5__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_680_ph_diff5__zc_flag_in[0] = 0;
        }
    }
    {
        _node_680_ph_diff6__previous_correction_ref = 0;
        _node_680_ph_diff6__sample_cnt_ref = 0;
        _node_680_ph_diff6__previous_filtered_ref = 0;
        _node_680_ph_diff6__filtered_ref = 0;
        _node_680_ph_diff6__correction_ref = 0;
        _node_680_ph_diff6__zc_flag_ref = 0;
        _node_680_ph_diff6__phase_state = 0;
        _node_680_ph_diff6__correction_in = 0;
        _node_680_ph_diff6__previous_correction_in = 0;
        _node_680_ph_diff6__sample_cnt_in = 0;
        _node_680_ph_diff6__previous_filtered_in = 0;
        _node_680_ph_diff6__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_680_ph_diff6__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_680_ph_diff6__zc_flag_in[0] = 0;
        }
    }
    {
        _node_684_ph_diff4__previous_correction_ref = 0;
        _node_684_ph_diff4__sample_cnt_ref = 0;
        _node_684_ph_diff4__previous_filtered_ref = 0;
        _node_684_ph_diff4__filtered_ref = 0;
        _node_684_ph_diff4__correction_ref = 0;
        _node_684_ph_diff4__zc_flag_ref = 0;
        _node_684_ph_diff4__phase_state = 0;
        _node_684_ph_diff4__correction_in = 0;
        _node_684_ph_diff4__previous_correction_in = 0;
        _node_684_ph_diff4__sample_cnt_in = 0;
        _node_684_ph_diff4__previous_filtered_in = 0;
        _node_684_ph_diff4__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_684_ph_diff4__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_684_ph_diff4__zc_flag_in[0] = 0;
        }
    }
    {
        _node_684_ph_diff5__previous_correction_ref = 0;
        _node_684_ph_diff5__sample_cnt_ref = 0;
        _node_684_ph_diff5__previous_filtered_ref = 0;
        _node_684_ph_diff5__filtered_ref = 0;
        _node_684_ph_diff5__correction_ref = 0;
        _node_684_ph_diff5__zc_flag_ref = 0;
        _node_684_ph_diff5__phase_state = 0;
        _node_684_ph_diff5__correction_in = 0;
        _node_684_ph_diff5__previous_correction_in = 0;
        _node_684_ph_diff5__sample_cnt_in = 0;
        _node_684_ph_diff5__previous_filtered_in = 0;
        _node_684_ph_diff5__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_684_ph_diff5__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_684_ph_diff5__zc_flag_in[0] = 0;
        }
    }
    {
        _node_692_ph_diff4__previous_correction_ref = 0;
        _node_692_ph_diff4__sample_cnt_ref = 0;
        _node_692_ph_diff4__previous_filtered_ref = 0;
        _node_692_ph_diff4__filtered_ref = 0;
        _node_692_ph_diff4__correction_ref = 0;
        _node_692_ph_diff4__zc_flag_ref = 0;
        _node_692_ph_diff4__phase_state = 0;
        _node_692_ph_diff4__correction_in = 0;
        _node_692_ph_diff4__previous_correction_in = 0;
        _node_692_ph_diff4__sample_cnt_in = 0;
        _node_692_ph_diff4__previous_filtered_in = 0;
        _node_692_ph_diff4__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_692_ph_diff4__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_692_ph_diff4__zc_flag_in[0] = 0;
        }
    }
    {
        _node_692_ph_diff5__previous_correction_ref = 0;
        _node_692_ph_diff5__sample_cnt_ref = 0;
        _node_692_ph_diff5__previous_filtered_ref = 0;
        _node_692_ph_diff5__filtered_ref = 0;
        _node_692_ph_diff5__correction_ref = 0;
        _node_692_ph_diff5__zc_flag_ref = 0;
        _node_692_ph_diff5__phase_state = 0;
        _node_692_ph_diff5__correction_in = 0;
        _node_692_ph_diff5__previous_correction_in = 0;
        _node_692_ph_diff5__sample_cnt_in = 0;
        _node_692_ph_diff5__previous_filtered_in = 0;
        _node_692_ph_diff5__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_692_ph_diff5__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_692_ph_diff5__zc_flag_in[0] = 0;
        }
    }
    {
        _node_692_ph_diff6__previous_correction_ref = 0;
        _node_692_ph_diff6__sample_cnt_ref = 0;
        _node_692_ph_diff6__previous_filtered_ref = 0;
        _node_692_ph_diff6__filtered_ref = 0;
        _node_692_ph_diff6__correction_ref = 0;
        _node_692_ph_diff6__zc_flag_ref = 0;
        _node_692_ph_diff6__phase_state = 0;
        _node_692_ph_diff6__correction_in = 0;
        _node_692_ph_diff6__previous_correction_in = 0;
        _node_692_ph_diff6__sample_cnt_in = 0;
        _node_692_ph_diff6__previous_filtered_in = 0;
        _node_692_ph_diff6__filtered_in = 0;
        int t_tmp1;
        for(t_tmp1 = 0; t_tmp1 < 1; t_tmp1++) {
            _node_692_ph_diff6__no_zc_flag_in[0] = 0;
        }
        int t_tmp2;
        for(t_tmp2 = 0; t_tmp2 < 1; t_tmp2++) {
            _node_692_ph_diff6__zc_flag_in[0] = 0;
        }
    }
    _msr_632_671_rms6__square_sum = 0x0;
    _msr_632_671_rms6__sample_cnt = 0x0;
    _msr_632_671_rms6__period_cnt = 0x0;
    _msr_632_671_rms6__db_timer = 0x0;
    _msr_632_671_rms6__previous_filtered_value = 0x0;
    _msr_632_671_rms6__previous_correction = 0x0;
    _msr_632_671_rms6__correction = 0x0;
    _msr_632_671_rms6__previous_value = 0x0;
    _msr_632_671_rms6__out_state = 0x0;
    _msr_632_671_rms6__filtered_value = 0x0;
    _msr_632_671_rms6__db_timer = 0x0;
    _msr_632_671_rms5__square_sum = 0x0;
    _msr_632_671_rms5__sample_cnt = 0x0;
    _msr_632_671_rms5__period_cnt = 0x0;
    _msr_632_671_rms5__db_timer = 0x0;
    _msr_632_671_rms5__previous_filtered_value = 0x0;
    _msr_632_671_rms5__previous_correction = 0x0;
    _msr_632_671_rms5__correction = 0x0;
    _msr_632_671_rms5__previous_value = 0x0;
    _msr_632_671_rms5__out_state = 0x0;
    _msr_632_671_rms5__filtered_value = 0x0;
    _msr_632_671_rms5__db_timer = 0x0;
    _msr_632_671_rms4__square_sum = 0x0;
    _msr_632_671_rms4__sample_cnt = 0x0;
    _msr_632_671_rms4__period_cnt = 0x0;
    _msr_632_671_rms4__db_timer = 0x0;
    _msr_632_671_rms4__previous_filtered_value = 0x0;
    _msr_632_671_rms4__previous_correction = 0x0;
    _msr_632_671_rms4__correction = 0x0;
    _msr_632_671_rms4__previous_value = 0x0;
    _msr_632_671_rms4__out_state = 0x0;
    _msr_632_671_rms4__filtered_value = 0x0;
    _msr_632_671_rms4__db_timer = 0x0;
    {
        HIL_OutAO(0x409f, 0);
    }
    {
        HIL_OutAO(0x409b, 0);
    }
    {
        HIL_OutAO(0x409d, 0);
    }
    _node_611_rms4__square_sum = 0x0;
    _node_611_rms4__sample_cnt = 0x0;
    _node_611_rms4__period_cnt = 0x0;
    _node_611_rms4__db_timer = 0x0;
    _node_611_rms4__previous_filtered_value = 0x0;
    _node_611_rms4__previous_correction = 0x0;
    _node_611_rms4__correction = 0x0;
    _node_611_rms4__previous_value = 0x0;
    _node_611_rms4__out_state = 0x0;
    _node_611_rms4__filtered_value = 0x0;
    _node_611_rms4__db_timer = 0x0;
    {
        HIL_OutAO(0x40a1, 0);
    }
    _node_632_rms6__square_sum = 0x0;
    _node_632_rms6__sample_cnt = 0x0;
    _node_632_rms6__period_cnt = 0x0;
    _node_632_rms6__db_timer = 0x0;
    _node_632_rms6__previous_filtered_value = 0x0;
    _node_632_rms6__previous_correction = 0x0;
    _node_632_rms6__correction = 0x0;
    _node_632_rms6__previous_value = 0x0;
    _node_632_rms6__out_state = 0x0;
    _node_632_rms6__filtered_value = 0x0;
    _node_632_rms6__db_timer = 0x0;
    _node_632_rms5__square_sum = 0x0;
    _node_632_rms5__sample_cnt = 0x0;
    _node_632_rms5__period_cnt = 0x0;
    _node_632_rms5__db_timer = 0x0;
    _node_632_rms5__previous_filtered_value = 0x0;
    _node_632_rms5__previous_correction = 0x0;
    _node_632_rms5__correction = 0x0;
    _node_632_rms5__previous_value = 0x0;
    _node_632_rms5__out_state = 0x0;
    _node_632_rms5__filtered_value = 0x0;
    _node_632_rms5__db_timer = 0x0;
    _node_632_power_meter1__filter_1_output_k_minus_1 = 0.0;
    _node_632_power_meter1__filter_1_input_k_minus_1 = 0.0;
    _node_632_power_meter1__filter_1_output_k_minus_1Q = 0.0;
    _node_632_power_meter1__filter_1_input_k_minus_1Q = 0.0;
    _node_632_power_meter1__filter_1_output_k_minus_1P0 = 0.0;
    _node_632_power_meter1__filter_1_input_k_minus_1P0 = 0.0;
    _node_632_rms4__square_sum = 0x0;
    _node_632_rms4__sample_cnt = 0x0;
    _node_632_rms4__period_cnt = 0x0;
    _node_632_rms4__db_timer = 0x0;
    _node_632_rms4__previous_filtered_value = 0x0;
    _node_632_rms4__previous_correction = 0x0;
    _node_632_rms4__correction = 0x0;
    _node_632_rms4__previous_value = 0x0;
    _node_632_rms4__out_state = 0x0;
    _node_632_rms4__filtered_value = 0x0;
    _node_632_rms4__db_timer = 0x0;
    {
        HIL_OutAO(0x40a7, 0);
    }
    {
        HIL_OutAO(0x40a3, 0);
    }
    {
        HIL_OutAO(0x40a5, 0);
    }
    _node_633_rms6__square_sum = 0x0;
    _node_633_rms6__sample_cnt = 0x0;
    _node_633_rms6__period_cnt = 0x0;
    _node_633_rms6__db_timer = 0x0;
    _node_633_rms6__previous_filtered_value = 0x0;
    _node_633_rms6__previous_correction = 0x0;
    _node_633_rms6__correction = 0x0;
    _node_633_rms6__previous_value = 0x0;
    _node_633_rms6__out_state = 0x0;
    _node_633_rms6__filtered_value = 0x0;
    _node_633_rms6__db_timer = 0x0;
    _node_633_rms5__square_sum = 0x0;
    _node_633_rms5__sample_cnt = 0x0;
    _node_633_rms5__period_cnt = 0x0;
    _node_633_rms5__db_timer = 0x0;
    _node_633_rms5__previous_filtered_value = 0x0;
    _node_633_rms5__previous_correction = 0x0;
    _node_633_rms5__correction = 0x0;
    _node_633_rms5__previous_value = 0x0;
    _node_633_rms5__out_state = 0x0;
    _node_633_rms5__filtered_value = 0x0;
    _node_633_rms5__db_timer = 0x0;
    _node_633_rms4__square_sum = 0x0;
    _node_633_rms4__sample_cnt = 0x0;
    _node_633_rms4__period_cnt = 0x0;
    _node_633_rms4__db_timer = 0x0;
    _node_633_rms4__previous_filtered_value = 0x0;
    _node_633_rms4__previous_correction = 0x0;
    _node_633_rms4__correction = 0x0;
    _node_633_rms4__previous_value = 0x0;
    _node_633_rms4__out_state = 0x0;
    _node_633_rms4__filtered_value = 0x0;
    _node_633_rms4__db_timer = 0x0;
    {
        HIL_OutAO(0x40ae, 0);
    }
    {
        HIL_OutAO(0x40aa, 0);
    }
    {
        HIL_OutAO(0x40ac, 0);
    }
    _node_634_rms6__square_sum = 0x0;
    _node_634_rms6__sample_cnt = 0x0;
    _node_634_rms6__period_cnt = 0x0;
    _node_634_rms6__db_timer = 0x0;
    _node_634_rms6__previous_filtered_value = 0x0;
    _node_634_rms6__previous_correction = 0x0;
    _node_634_rms6__correction = 0x0;
    _node_634_rms6__previous_value = 0x0;
    _node_634_rms6__out_state = 0x0;
    _node_634_rms6__filtered_value = 0x0;
    _node_634_rms6__db_timer = 0x0;
    _node_634_rms5__square_sum = 0x0;
    _node_634_rms5__sample_cnt = 0x0;
    _node_634_rms5__period_cnt = 0x0;
    _node_634_rms5__db_timer = 0x0;
    _node_634_rms5__previous_filtered_value = 0x0;
    _node_634_rms5__previous_correction = 0x0;
    _node_634_rms5__correction = 0x0;
    _node_634_rms5__previous_value = 0x0;
    _node_634_rms5__out_state = 0x0;
    _node_634_rms5__filtered_value = 0x0;
    _node_634_rms5__db_timer = 0x0;
    _node_634_rms4__square_sum = 0x0;
    _node_634_rms4__sample_cnt = 0x0;
    _node_634_rms4__period_cnt = 0x0;
    _node_634_rms4__db_timer = 0x0;
    _node_634_rms4__previous_filtered_value = 0x0;
    _node_634_rms4__previous_correction = 0x0;
    _node_634_rms4__correction = 0x0;
    _node_634_rms4__previous_value = 0x0;
    _node_634_rms4__out_state = 0x0;
    _node_634_rms4__filtered_value = 0x0;
    _node_634_rms4__db_timer = 0x0;
    {
        HIL_OutAO(0x40b4, 0);
    }
    {
        HIL_OutAO(0x40b0, 0);
    }
    {
        HIL_OutAO(0x40b2, 0);
    }
    _node_645_rms5__square_sum = 0x0;
    _node_645_rms5__sample_cnt = 0x0;
    _node_645_rms5__period_cnt = 0x0;
    _node_645_rms5__db_timer = 0x0;
    _node_645_rms5__previous_filtered_value = 0x0;
    _node_645_rms5__previous_correction = 0x0;
    _node_645_rms5__correction = 0x0;
    _node_645_rms5__previous_value = 0x0;
    _node_645_rms5__out_state = 0x0;
    _node_645_rms5__filtered_value = 0x0;
    _node_645_rms5__db_timer = 0x0;
    _node_645_rms4__square_sum = 0x0;
    _node_645_rms4__sample_cnt = 0x0;
    _node_645_rms4__period_cnt = 0x0;
    _node_645_rms4__db_timer = 0x0;
    _node_645_rms4__previous_filtered_value = 0x0;
    _node_645_rms4__previous_correction = 0x0;
    _node_645_rms4__correction = 0x0;
    _node_645_rms4__previous_value = 0x0;
    _node_645_rms4__out_state = 0x0;
    _node_645_rms4__filtered_value = 0x0;
    _node_645_rms4__db_timer = 0x0;
    {
        HIL_OutAO(0x40b8, 0);
    }
    {
        HIL_OutAO(0x40b6, 0);
    }
    _node_646_rms5__square_sum = 0x0;
    _node_646_rms5__sample_cnt = 0x0;
    _node_646_rms5__period_cnt = 0x0;
    _node_646_rms5__db_timer = 0x0;
    _node_646_rms5__previous_filtered_value = 0x0;
    _node_646_rms5__previous_correction = 0x0;
    _node_646_rms5__correction = 0x0;
    _node_646_rms5__previous_value = 0x0;
    _node_646_rms5__out_state = 0x0;
    _node_646_rms5__filtered_value = 0x0;
    _node_646_rms5__db_timer = 0x0;
    _node_646_rms4__square_sum = 0x0;
    _node_646_rms4__sample_cnt = 0x0;
    _node_646_rms4__period_cnt = 0x0;
    _node_646_rms4__db_timer = 0x0;
    _node_646_rms4__previous_filtered_value = 0x0;
    _node_646_rms4__previous_correction = 0x0;
    _node_646_rms4__correction = 0x0;
    _node_646_rms4__previous_value = 0x0;
    _node_646_rms4__out_state = 0x0;
    _node_646_rms4__filtered_value = 0x0;
    _node_646_rms4__db_timer = 0x0;
    {
        HIL_OutAO(0x40bc, 0);
    }
    {
        HIL_OutAO(0x40ba, 0);
    }
    _node_652_rms6__square_sum = 0x0;
    _node_652_rms6__sample_cnt = 0x0;
    _node_652_rms6__period_cnt = 0x0;
    _node_652_rms6__db_timer = 0x0;
    _node_652_rms6__previous_filtered_value = 0x0;
    _node_652_rms6__previous_correction = 0x0;
    _node_652_rms6__correction = 0x0;
    _node_652_rms6__previous_value = 0x0;
    _node_652_rms6__out_state = 0x0;
    _node_652_rms6__filtered_value = 0x0;
    _node_652_rms6__db_timer = 0x0;
    {
        HIL_OutAO(0x40be, 0);
    }
    _node_671_rms6__square_sum = 0x0;
    _node_671_rms6__sample_cnt = 0x0;
    _node_671_rms6__period_cnt = 0x0;
    _node_671_rms6__db_timer = 0x0;
    _node_671_rms6__previous_filtered_value = 0x0;
    _node_671_rms6__previous_correction = 0x0;
    _node_671_rms6__correction = 0x0;
    _node_671_rms6__previous_value = 0x0;
    _node_671_rms6__out_state = 0x0;
    _node_671_rms6__filtered_value = 0x0;
    _node_671_rms6__db_timer = 0x0;
    _node_671_rms5__square_sum = 0x0;
    _node_671_rms5__sample_cnt = 0x0;
    _node_671_rms5__period_cnt = 0x0;
    _node_671_rms5__db_timer = 0x0;
    _node_671_rms5__previous_filtered_value = 0x0;
    _node_671_rms5__previous_correction = 0x0;
    _node_671_rms5__correction = 0x0;
    _node_671_rms5__previous_value = 0x0;
    _node_671_rms5__out_state = 0x0;
    _node_671_rms5__filtered_value = 0x0;
    _node_671_rms5__db_timer = 0x0;
    _node_671_rms4__square_sum = 0x0;
    _node_671_rms4__sample_cnt = 0x0;
    _node_671_rms4__period_cnt = 0x0;
    _node_671_rms4__db_timer = 0x0;
    _node_671_rms4__previous_filtered_value = 0x0;
    _node_671_rms4__previous_correction = 0x0;
    _node_671_rms4__correction = 0x0;
    _node_671_rms4__previous_value = 0x0;
    _node_671_rms4__out_state = 0x0;
    _node_671_rms4__filtered_value = 0x0;
    _node_671_rms4__db_timer = 0x0;
    {
        HIL_OutAO(0x40c4, 0);
    }
    {
        HIL_OutAO(0x40c0, 0);
    }
    {
        HIL_OutAO(0x40c2, 0);
    }
    _node_675_rms6__square_sum = 0x0;
    _node_675_rms6__sample_cnt = 0x0;
    _node_675_rms6__period_cnt = 0x0;
    _node_675_rms6__db_timer = 0x0;
    _node_675_rms6__previous_filtered_value = 0x0;
    _node_675_rms6__previous_correction = 0x0;
    _node_675_rms6__correction = 0x0;
    _node_675_rms6__previous_value = 0x0;
    _node_675_rms6__out_state = 0x0;
    _node_675_rms6__filtered_value = 0x0;
    _node_675_rms6__db_timer = 0x0;
    _node_675_rms5__square_sum = 0x0;
    _node_675_rms5__sample_cnt = 0x0;
    _node_675_rms5__period_cnt = 0x0;
    _node_675_rms5__db_timer = 0x0;
    _node_675_rms5__previous_filtered_value = 0x0;
    _node_675_rms5__previous_correction = 0x0;
    _node_675_rms5__correction = 0x0;
    _node_675_rms5__previous_value = 0x0;
    _node_675_rms5__out_state = 0x0;
    _node_675_rms5__filtered_value = 0x0;
    _node_675_rms5__db_timer = 0x0;
    _node_675_rms4__square_sum = 0x0;
    _node_675_rms4__sample_cnt = 0x0;
    _node_675_rms4__period_cnt = 0x0;
    _node_675_rms4__db_timer = 0x0;
    _node_675_rms4__previous_filtered_value = 0x0;
    _node_675_rms4__previous_correction = 0x0;
    _node_675_rms4__correction = 0x0;
    _node_675_rms4__previous_value = 0x0;
    _node_675_rms4__out_state = 0x0;
    _node_675_rms4__filtered_value = 0x0;
    _node_675_rms4__db_timer = 0x0;
    {
        HIL_OutAO(0x40ca, 0);
    }
    {
        HIL_OutAO(0x40c6, 0);
    }
    {
        HIL_OutAO(0x40c8, 0);
    }
    _node_680_rms6__square_sum = 0x0;
    _node_680_rms6__sample_cnt = 0x0;
    _node_680_rms6__period_cnt = 0x0;
    _node_680_rms6__db_timer = 0x0;
    _node_680_rms6__previous_filtered_value = 0x0;
    _node_680_rms6__previous_correction = 0x0;
    _node_680_rms6__correction = 0x0;
    _node_680_rms6__previous_value = 0x0;
    _node_680_rms6__out_state = 0x0;
    _node_680_rms6__filtered_value = 0x0;
    _node_680_rms6__db_timer = 0x0;
    _node_680_rms5__square_sum = 0x0;
    _node_680_rms5__sample_cnt = 0x0;
    _node_680_rms5__period_cnt = 0x0;
    _node_680_rms5__db_timer = 0x0;
    _node_680_rms5__previous_filtered_value = 0x0;
    _node_680_rms5__previous_correction = 0x0;
    _node_680_rms5__correction = 0x0;
    _node_680_rms5__previous_value = 0x0;
    _node_680_rms5__out_state = 0x0;
    _node_680_rms5__filtered_value = 0x0;
    _node_680_rms5__db_timer = 0x0;
    _node_680_rms4__square_sum = 0x0;
    _node_680_rms4__sample_cnt = 0x0;
    _node_680_rms4__period_cnt = 0x0;
    _node_680_rms4__db_timer = 0x0;
    _node_680_rms4__previous_filtered_value = 0x0;
    _node_680_rms4__previous_correction = 0x0;
    _node_680_rms4__correction = 0x0;
    _node_680_rms4__previous_value = 0x0;
    _node_680_rms4__out_state = 0x0;
    _node_680_rms4__filtered_value = 0x0;
    _node_680_rms4__db_timer = 0x0;
    {
        HIL_OutAO(0x40d0, 0);
    }
    {
        HIL_OutAO(0x40cc, 0);
    }
    {
        HIL_OutAO(0x40ce, 0);
    }
    _node_684_rms6__square_sum = 0x0;
    _node_684_rms6__sample_cnt = 0x0;
    _node_684_rms6__period_cnt = 0x0;
    _node_684_rms6__db_timer = 0x0;
    _node_684_rms6__previous_filtered_value = 0x0;
    _node_684_rms6__previous_correction = 0x0;
    _node_684_rms6__correction = 0x0;
    _node_684_rms6__previous_value = 0x0;
    _node_684_rms6__out_state = 0x0;
    _node_684_rms6__filtered_value = 0x0;
    _node_684_rms6__db_timer = 0x0;
    _node_684_rms4__square_sum = 0x0;
    _node_684_rms4__sample_cnt = 0x0;
    _node_684_rms4__period_cnt = 0x0;
    _node_684_rms4__db_timer = 0x0;
    _node_684_rms4__previous_filtered_value = 0x0;
    _node_684_rms4__previous_correction = 0x0;
    _node_684_rms4__correction = 0x0;
    _node_684_rms4__previous_value = 0x0;
    _node_684_rms4__out_state = 0x0;
    _node_684_rms4__filtered_value = 0x0;
    _node_684_rms4__db_timer = 0x0;
    {
        HIL_OutAO(0x40d4, 0);
    }
    {
        HIL_OutAO(0x40d2, 0);
    }
    _node_692_rms6__square_sum = 0x0;
    _node_692_rms6__sample_cnt = 0x0;
    _node_692_rms6__period_cnt = 0x0;
    _node_692_rms6__db_timer = 0x0;
    _node_692_rms6__previous_filtered_value = 0x0;
    _node_692_rms6__previous_correction = 0x0;
    _node_692_rms6__correction = 0x0;
    _node_692_rms6__previous_value = 0x0;
    _node_692_rms6__out_state = 0x0;
    _node_692_rms6__filtered_value = 0x0;
    _node_692_rms6__db_timer = 0x0;
    _node_692_rms5__square_sum = 0x0;
    _node_692_rms5__sample_cnt = 0x0;
    _node_692_rms5__period_cnt = 0x0;
    _node_692_rms5__db_timer = 0x0;
    _node_692_rms5__previous_filtered_value = 0x0;
    _node_692_rms5__previous_correction = 0x0;
    _node_692_rms5__correction = 0x0;
    _node_692_rms5__previous_value = 0x0;
    _node_692_rms5__out_state = 0x0;
    _node_692_rms5__filtered_value = 0x0;
    _node_692_rms5__db_timer = 0x0;
    _node_692_rms4__square_sum = 0x0;
    _node_692_rms4__sample_cnt = 0x0;
    _node_692_rms4__period_cnt = 0x0;
    _node_692_rms4__db_timer = 0x0;
    _node_692_rms4__previous_filtered_value = 0x0;
    _node_692_rms4__previous_correction = 0x0;
    _node_692_rms4__correction = 0x0;
    _node_692_rms4__previous_value = 0x0;
    _node_692_rms4__out_state = 0x0;
    _node_692_rms4__filtered_value = 0x0;
    _node_692_rms4__db_timer = 0x0;
    {
        HIL_OutAO(0x40da, 0);
    }
    {
        HIL_OutAO(0x40d6, 0);
    }
    {
        HIL_OutAO(0x40d8, 0);
    }
    {
        XIo_OutFloat(0x2f4000e8, 0);
    }
    {
        XIo_OutFloat(0x2f4000ec, 0);
    }
    {
        XIo_OutFloat(0x2f4000f0, 0);
    }
    {
        XIo_OutFloat(0x2f4000f4, 0);
    }
    {
        XIo_OutFloat(0x2f4000f8, 0);
    }
    {
        XIo_OutFloat(0x2f4000fc, 0);
    }
    {
        XIo_OutFloat(0x2f400100, 0);
    }
    {
        XIo_OutFloat(0x2f400104, 0);
    }
    {
        XIo_OutFloat(0x2f400108, 0);
    }
    {
        XIo_OutFloat(0x2f40010c, 0);
    }
    {
        XIo_OutFloat(0x2f400110, 0);
    }
    {
        XIo_OutFloat(0x2f400114, 0);
    }
    {
        XIo_OutFloat(0x2f400118, 0);
    }
    {
        XIo_OutFloat(0x2f40011c, 0);
    }
    {
        XIo_OutFloat(0x2f400120, 0);
    }
    {
        XIo_OutFloat(0x2f400124, 0);
    }
    {
        XIo_OutFloat(0x2f400128, 0);
    }
    {
        XIo_OutFloat(0x2f40012c, 0);
    }
    {
        XIo_OutFloat(0x2f400130, 0);
    }
    {
        XIo_OutFloat(0x2f400134, 0);
    }
    {
        XIo_OutFloat(0x2f400138, 0);
    }
    {
        XIo_OutFloat(0x2f40013c, 0);
    }
    {
        XIo_OutFloat(0x2f400140, 0);
    }
    {
        XIo_OutFloat(0x2f400144, 0);
    }
    {
        XIo_OutFloat(0x2f400148, 0);
    }
    {
        XIo_OutFloat(0x2f40014c, 0);
    }
    {
        XIo_OutFloat(0x2f400150, 0);
    }
    {
        XIo_OutFloat(0x2f400154, 0);
    }
    {
        XIo_OutFloat(0x2f400158, 0);
    }
    {
        HIL_OutAO(0x409c, 0);
    }
    {
        HIL_OutAO(0x409e, 0);
    }
    {
        HIL_OutAO(0x40a0, 0);
    }
    {
        HIL_OutAO(0x40a2, 0);
    }
    {
        HIL_OutAO(0x40a4, 0);
    }
    {
        HIL_OutAO(0x40a6, 0);
    }
    {
        HIL_OutAO(0x40a9, 0);
    }
    {
        HIL_OutAO(0x40a8, 0);
    }
    {
        HIL_OutAO(0x40ab, 0);
    }
    {
        HIL_OutAO(0x40ad, 0);
    }
    {
        HIL_OutAO(0x40af, 0);
    }
    {
        HIL_OutAO(0x40b1, 0);
    }
    {
        HIL_OutAO(0x40b3, 0);
    }
    {
        HIL_OutAO(0x40b5, 0);
    }
    {
        HIL_OutAO(0x40b7, 0);
    }
    {
        HIL_OutAO(0x40b9, 0);
    }
    {
        HIL_OutAO(0x40bb, 0);
    }
    {
        HIL_OutAO(0x40bd, 0);
    }
    {
        HIL_OutAO(0x40bf, 0);
    }
    {
        HIL_OutAO(0x40c1, 0);
    }
    {
        HIL_OutAO(0x40c3, 0);
    }
    {
        HIL_OutAO(0x40c5, 0);
    }
    {
        HIL_OutAO(0x40c7, 0);
    }
    {
        HIL_OutAO(0x40c9, 0);
    }
    {
        HIL_OutAO(0x40cb, 0);
    }
    {
        HIL_OutAO(0x40cd, 0);
    }
    {
        HIL_OutAO(0x40cf, 0);
    }
    {
        HIL_OutAO(0x40d1, 0);
    }
    {
        HIL_OutAO(0x40d3, 0);
    }
    {
        HIL_OutAO(0x40d5, 0);
    }
    {
        HIL_OutAO(0x40d7, 0);
    }
    {
        HIL_OutAO(0x40d9, 0);
    }
    {
        HIL_OutAO(0x40db, 0);
    }
    //@cmp.init.block.end
}


// Dll function pointers and dll reload function
#if defined(_WIN64)
// Define method for reloading dll functions
void ReloadDllFunctions_user_sp_cpu0_dev0(void) {
    // Load each library and setup function pointers
}

void FreeDllFunctions_user_sp_cpu0_dev0(void) {
}

#else
// Define method for reloading dll functions
void ReloadDllFunctions_user_sp_cpu0_dev0(void) {
    // Load each library and setup function pointers
}

void FreeDllFunctions_user_sp_cpu0_dev0(void) {
}
#endif

void load_fmi_libraries_user_sp_cpu0_dev0(void) {
#if defined(_WIN64)
#else
#endif
}


void ReInit_sp_scope_user_sp_cpu0_dev0() {
    // initialise SP Scope buffer pointer
}


// generated using template: virtual_hil/common_timer_counter_handler.template-------------------------

/*****************************************************************************************/
/**
* This function is the handler which performs processing for the timer counter.
* It is called from an interrupt context such that the amount of processing
* performed should be minimized.  It is called when the timer counter expires
* if interrupts are enabled.
*
*
* @param    None
*
* @return   None
*
* @note     None
*
*****************************************************************************************/

void TimerCounterHandler_0_user_sp_cpu0_dev0() {
#if DEBUG_MODE
    printf("\n\rTimerCounterHandler_0");
#endif
    //////////////////////////////////////////////////////////////////////////
    // Output block
    //////////////////////////////////////////////////////////////////////////
    //@cmp.out.block.start
    // Generated from the component: Constant4
    {
        _constant4__out = _constant4__p_value;
    }
    // Generated from the component: Termination1
    {
    }
//@cmp.out.block.end
    //////////////////////////////////////////////////////////////////////////
    // Update block
    //////////////////////////////////////////////////////////////////////////
    //@cmp.update.block.start
    // Generated from the component: Constant4
    // Generated from the component: Termination1
    //@cmp.update.block.end
}
void TimerCounterHandler_1_user_sp_cpu0_dev0() {
#if DEBUG_MODE
    printf("\n\rTimerCounterHandler_1");
#endif
    //////////////////////////////////////////////////////////////////////////
    // Output block
    //////////////////////////////////////////////////////////////////////////
    //@cmp.out.block.start
    // Generated from the component: MSR 632-671.I1.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc8003a);
        _msr_632_671_i1_ia1__out = tac_tmp1;
    }
    // Generated from the component: MSR 632-671.I2.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc8003b);
        _msr_632_671_i2_ia1__out = tac_tmp1;
    }
    // Generated from the component: MSR 632-671.I3.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc8003c);
        _msr_632_671_i3_ia1__out = tac_tmp1;
    }
    // Generated from the component: MSR 632-671.ph_diff4
    {
        if(_msr_632_671_ph_diff4__n_degrees) {
            _msr_632_671_ph_diff4__phase_diff = _msr_632_671_ph_diff4__phase_state;
        }
        else {
            _msr_632_671_ph_diff4__phase_diff = ((_msr_632_671_ph_diff4__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: MSR 632-671.ph_diff5
    {
        if(_msr_632_671_ph_diff5__n_degrees) {
            _msr_632_671_ph_diff5__phase_diff = _msr_632_671_ph_diff5__phase_state;
        }
        else {
            _msr_632_671_ph_diff5__phase_diff = ((_msr_632_671_ph_diff5__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: MSR 632-671.ph_diff6
    {
        if(_msr_632_671_ph_diff6__n_degrees) {
            _msr_632_671_ph_diff6__phase_diff = _msr_632_671_ph_diff6__phase_state;
        }
        else {
            _msr_632_671_ph_diff6__phase_diff = ((_msr_632_671_ph_diff6__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 611.I3.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc8003d);
        _node_611_i3_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 611.ph_diff4
    {
        if(_node_611_ph_diff4__n_degrees) {
            _node_611_ph_diff4__phase_diff = _node_611_ph_diff4__phase_state;
        }
        else {
            _node_611_ph_diff4__phase_diff = ((_node_611_ph_diff4__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 632.CPU Transition4.Output
    {
        real tac_tmp1;
        tac_tmp1 = XIo_InFloat(0x2f400000);
        _node_632_cpu_transition4_output__out = tac_tmp1;
    }
    // Generated from the component: Node 632.CPU Transition5.Output
    {
        real tac_tmp1;
        tac_tmp1 = XIo_InFloat(0x2f400004);
        _node_632_cpu_transition5_output__out = tac_tmp1;
    }
    // Generated from the component: Node 632.CPU Transition6.Output
    {
        real tac_tmp1;
        tac_tmp1 = XIo_InFloat(0x2f400008);
        _node_632_cpu_transition6_output__out = tac_tmp1;
    }
    // Generated from the component: Node 632.I1.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc8003e);
        _node_632_i1_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 632.I2.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc8003f);
        _node_632_i2_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 632.I3.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80040);
        _node_632_i3_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 632.ph_diff4
    {
        if(_node_632_ph_diff4__n_degrees) {
            _node_632_ph_diff4__phase_diff = _node_632_ph_diff4__phase_state;
        }
        else {
            _node_632_ph_diff4__phase_diff = ((_node_632_ph_diff4__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 632.ph_diff5
    {
        if(_node_632_ph_diff5__n_degrees) {
            _node_632_ph_diff5__phase_diff = _node_632_ph_diff5__phase_state;
        }
        else {
            _node_632_ph_diff5__phase_diff = ((_node_632_ph_diff5__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 632.ph_diff6
    {
        if(_node_632_ph_diff6__n_degrees) {
            _node_632_ph_diff6__phase_diff = _node_632_ph_diff6__phase_state;
        }
        else {
            _node_632_ph_diff6__phase_diff = ((_node_632_ph_diff6__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 633.I1.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80041);
        _node_633_i1_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 633.I2.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80042);
        _node_633_i2_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 633.I3.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80043);
        _node_633_i3_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 633.ph_diff4
    {
        if(_node_633_ph_diff4__n_degrees) {
            _node_633_ph_diff4__phase_diff = _node_633_ph_diff4__phase_state;
        }
        else {
            _node_633_ph_diff4__phase_diff = ((_node_633_ph_diff4__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 633.ph_diff5
    {
        if(_node_633_ph_diff5__n_degrees) {
            _node_633_ph_diff5__phase_diff = _node_633_ph_diff5__phase_state;
        }
        else {
            _node_633_ph_diff5__phase_diff = ((_node_633_ph_diff5__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 633.ph_diff6
    {
        if(_node_633_ph_diff6__n_degrees) {
            _node_633_ph_diff6__phase_diff = _node_633_ph_diff6__phase_state;
        }
        else {
            _node_633_ph_diff6__phase_diff = ((_node_633_ph_diff6__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 634.I1.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80044);
        _node_634_i1_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 634.I2.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80045);
        _node_634_i2_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 634.I3.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80046);
        _node_634_i3_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 634.ph_diff4
    {
        if(_node_634_ph_diff4__n_degrees) {
            _node_634_ph_diff4__phase_diff = _node_634_ph_diff4__phase_state;
        }
        else {
            _node_634_ph_diff4__phase_diff = ((_node_634_ph_diff4__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 634.ph_diff5
    {
        if(_node_634_ph_diff5__n_degrees) {
            _node_634_ph_diff5__phase_diff = _node_634_ph_diff5__phase_state;
        }
        else {
            _node_634_ph_diff5__phase_diff = ((_node_634_ph_diff5__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 634.ph_diff6
    {
        if(_node_634_ph_diff6__n_degrees) {
            _node_634_ph_diff6__phase_diff = _node_634_ph_diff6__phase_state;
        }
        else {
            _node_634_ph_diff6__phase_diff = ((_node_634_ph_diff6__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 645.I2.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80047);
        _node_645_i2_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 645.I3.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80048);
        _node_645_i3_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 645.ph_diff4
    {
        if(_node_645_ph_diff4__n_degrees) {
            _node_645_ph_diff4__phase_diff = _node_645_ph_diff4__phase_state;
        }
        else {
            _node_645_ph_diff4__phase_diff = ((_node_645_ph_diff4__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 645.ph_diff6
    {
        if(_node_645_ph_diff6__n_degrees) {
            _node_645_ph_diff6__phase_diff = _node_645_ph_diff6__phase_state;
        }
        else {
            _node_645_ph_diff6__phase_diff = ((_node_645_ph_diff6__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 646.I2.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80049);
        _node_646_i2_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 646.I3.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc8004a);
        _node_646_i3_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 646.ph_diff4
    {
        if(_node_646_ph_diff4__n_degrees) {
            _node_646_ph_diff4__phase_diff = _node_646_ph_diff4__phase_state;
        }
        else {
            _node_646_ph_diff4__phase_diff = ((_node_646_ph_diff4__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 646.ph_diff6
    {
        if(_node_646_ph_diff6__n_degrees) {
            _node_646_ph_diff6__phase_diff = _node_646_ph_diff6__phase_state;
        }
        else {
            _node_646_ph_diff6__phase_diff = ((_node_646_ph_diff6__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 652.I1.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc8004b);
        _node_652_i1_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 652.ph_diff5
    {
        if(_node_652_ph_diff5__n_degrees) {
            _node_652_ph_diff5__phase_diff = _node_652_ph_diff5__phase_state;
        }
        else {
            _node_652_ph_diff5__phase_diff = ((_node_652_ph_diff5__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 671.I1.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc8004c);
        _node_671_i1_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 671.I2.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc8004d);
        _node_671_i2_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 671.I3.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc8004e);
        _node_671_i3_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 671.ph_diff4
    {
        if(_node_671_ph_diff4__n_degrees) {
            _node_671_ph_diff4__phase_diff = _node_671_ph_diff4__phase_state;
        }
        else {
            _node_671_ph_diff4__phase_diff = ((_node_671_ph_diff4__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 671.ph_diff5
    {
        if(_node_671_ph_diff5__n_degrees) {
            _node_671_ph_diff5__phase_diff = _node_671_ph_diff5__phase_state;
        }
        else {
            _node_671_ph_diff5__phase_diff = ((_node_671_ph_diff5__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 671.ph_diff6
    {
        if(_node_671_ph_diff6__n_degrees) {
            _node_671_ph_diff6__phase_diff = _node_671_ph_diff6__phase_state;
        }
        else {
            _node_671_ph_diff6__phase_diff = ((_node_671_ph_diff6__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 675.I1.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc8004f);
        _node_675_i1_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 675.I2.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80050);
        _node_675_i2_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 675.I3.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80051);
        _node_675_i3_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 675.ph_diff4
    {
        if(_node_675_ph_diff4__n_degrees) {
            _node_675_ph_diff4__phase_diff = _node_675_ph_diff4__phase_state;
        }
        else {
            _node_675_ph_diff4__phase_diff = ((_node_675_ph_diff4__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 675.ph_diff5
    {
        if(_node_675_ph_diff5__n_degrees) {
            _node_675_ph_diff5__phase_diff = _node_675_ph_diff5__phase_state;
        }
        else {
            _node_675_ph_diff5__phase_diff = ((_node_675_ph_diff5__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 675.ph_diff6
    {
        if(_node_675_ph_diff6__n_degrees) {
            _node_675_ph_diff6__phase_diff = _node_675_ph_diff6__phase_state;
        }
        else {
            _node_675_ph_diff6__phase_diff = ((_node_675_ph_diff6__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 680.I1.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80052);
        _node_680_i1_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 680.I2.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80053);
        _node_680_i2_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 680.I3.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80054);
        _node_680_i3_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 680.ph_diff4
    {
        if(_node_680_ph_diff4__n_degrees) {
            _node_680_ph_diff4__phase_diff = _node_680_ph_diff4__phase_state;
        }
        else {
            _node_680_ph_diff4__phase_diff = ((_node_680_ph_diff4__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 680.ph_diff5
    {
        if(_node_680_ph_diff5__n_degrees) {
            _node_680_ph_diff5__phase_diff = _node_680_ph_diff5__phase_state;
        }
        else {
            _node_680_ph_diff5__phase_diff = ((_node_680_ph_diff5__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 680.ph_diff6
    {
        if(_node_680_ph_diff6__n_degrees) {
            _node_680_ph_diff6__phase_diff = _node_680_ph_diff6__phase_state;
        }
        else {
            _node_680_ph_diff6__phase_diff = ((_node_680_ph_diff6__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 684.I1.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80055);
        _node_684_i1_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 684.I3.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80056);
        _node_684_i3_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 684.ph_diff4
    {
        if(_node_684_ph_diff4__n_degrees) {
            _node_684_ph_diff4__phase_diff = _node_684_ph_diff4__phase_state;
        }
        else {
            _node_684_ph_diff4__phase_diff = ((_node_684_ph_diff4__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 684.ph_diff5
    {
        if(_node_684_ph_diff5__n_degrees) {
            _node_684_ph_diff5__phase_diff = _node_684_ph_diff5__phase_state;
        }
        else {
            _node_684_ph_diff5__phase_diff = ((_node_684_ph_diff5__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 692.I1.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80057);
        _node_692_i1_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 692.I2.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80058);
        _node_692_i2_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 692.I3.Ia1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80059);
        _node_692_i3_ia1__out = tac_tmp1;
    }
    // Generated from the component: Node 692.ph_diff4
    {
        if(_node_692_ph_diff4__n_degrees) {
            _node_692_ph_diff4__phase_diff = _node_692_ph_diff4__phase_state;
        }
        else {
            _node_692_ph_diff4__phase_diff = ((_node_692_ph_diff4__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 692.ph_diff5
    {
        if(_node_692_ph_diff5__n_degrees) {
            _node_692_ph_diff5__phase_diff = _node_692_ph_diff5__phase_state;
        }
        else {
            _node_692_ph_diff5__phase_diff = ((_node_692_ph_diff5__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Node 692.ph_diff6
    {
        if(_node_692_ph_diff6__n_degrees) {
            _node_692_ph_diff6__phase_diff = _node_692_ph_diff6__phase_state;
        }
        else {
            _node_692_ph_diff6__phase_diff = ((_node_692_ph_diff6__phase_state * M_PI) / 180);
        }
    }
    // Generated from the component: Reference.V1_REF2.Va1
    {
        real tac_tmp1;
        tac_tmp1 = HIL_InFloat(0xc80029);
        _reference_v1_ref2_va1__out = tac_tmp1;
    }
    // Generated from the component: switch state
    _switch_state__out = XIo_InFloat(0x2f80009c);
    // Generated from the component: MSR 632-671.RMS6
    _msr_632_671_rms6__previous_filtered_value = _msr_632_671_rms6__filtered_value;
    if (0)
        _msr_632_671_rms6__filtered_value = _msr_632_671_rms6__previous_filtered_value * 1 + _msr_632_671_i1_ia1__out * 1;
    else
        _msr_632_671_rms6__filtered_value = _msr_632_671_rms6__previous_filtered_value * 0.1 + _msr_632_671_i1_ia1__out * 0.9;
    _msr_632_671_rms6__db_timer += 0.00018;
    if( (_msr_632_671_rms6__filtered_value >= 0.0) && (_msr_632_671_rms6__previous_filtered_value < 0.0) && (_msr_632_671_rms6__db_timer >= 0.0) ) {
        _msr_632_671_rms6__zc = 1;
        _msr_632_671_rms6__db_timer = 0;
    } else
        _msr_632_671_rms6__zc = 0;
    _msr_632_671_rms6__out = _msr_632_671_rms6__out_state;
    // Generated from the component: MSR 632-671.RMS5
    _msr_632_671_rms5__previous_filtered_value = _msr_632_671_rms5__filtered_value;
    if (0)
        _msr_632_671_rms5__filtered_value = _msr_632_671_rms5__previous_filtered_value * 1 + _msr_632_671_i2_ia1__out * 1;
    else
        _msr_632_671_rms5__filtered_value = _msr_632_671_rms5__previous_filtered_value * 0.1 + _msr_632_671_i2_ia1__out * 0.9;
    _msr_632_671_rms5__db_timer += 0.00018;
    if( (_msr_632_671_rms5__filtered_value >= 0.0) && (_msr_632_671_rms5__previous_filtered_value < 0.0) && (_msr_632_671_rms5__db_timer >= 0.0) ) {
        _msr_632_671_rms5__zc = 1;
        _msr_632_671_rms5__db_timer = 0;
    } else
        _msr_632_671_rms5__zc = 0;
    _msr_632_671_rms5__out = _msr_632_671_rms5__out_state;
    // Generated from the component: MSR 632-671.RMS4
    _msr_632_671_rms4__previous_filtered_value = _msr_632_671_rms4__filtered_value;
    if (0)
        _msr_632_671_rms4__filtered_value = _msr_632_671_rms4__previous_filtered_value * 1 + _msr_632_671_i3_ia1__out * 1;
    else
        _msr_632_671_rms4__filtered_value = _msr_632_671_rms4__previous_filtered_value * 0.1 + _msr_632_671_i3_ia1__out * 0.9;
    _msr_632_671_rms4__db_timer += 0.00018;
    if( (_msr_632_671_rms4__filtered_value >= 0.0) && (_msr_632_671_rms4__previous_filtered_value < 0.0) && (_msr_632_671_rms4__db_timer >= 0.0) ) {
        _msr_632_671_rms4__zc = 1;
        _msr_632_671_rms4__db_timer = 0;
    } else
        _msr_632_671_rms4__zc = 0;
    _msr_632_671_rms4__out = _msr_632_671_rms4__out_state;
    // Generated from the component: MSR 632-671.I3_phase
    {
        HIL_OutAO(0x409f, _msr_632_671_ph_diff4__phase_diff);
    }
    // Generated from the component: MSR 632-671.I1_phase
    {
        HIL_OutAO(0x409b, _msr_632_671_ph_diff5__phase_diff);
    }
    // Generated from the component: MSR 632-671.I2_phase
    {
        HIL_OutAO(0x409d, _msr_632_671_ph_diff6__phase_diff);
    }
    // Generated from the component: Node 611.RMS4
    _node_611_rms4__previous_filtered_value = _node_611_rms4__filtered_value;
    if (0)
        _node_611_rms4__filtered_value = _node_611_rms4__previous_filtered_value * 1 + _node_611_i3_ia1__out * 1;
    else
        _node_611_rms4__filtered_value = _node_611_rms4__previous_filtered_value * 0.1 + _node_611_i3_ia1__out * 0.9;
    _node_611_rms4__db_timer += 0.00018;
    if( (_node_611_rms4__filtered_value >= 0.0) && (_node_611_rms4__previous_filtered_value < 0.0) && (_node_611_rms4__db_timer >= 0.0) ) {
        _node_611_rms4__zc = 1;
        _node_611_rms4__db_timer = 0;
    } else
        _node_611_rms4__zc = 0;
    _node_611_rms4__out = _node_611_rms4__out_state;
    // Generated from the component: Node 611.I3_phase
    {
        HIL_OutAO(0x40a1, _node_611_ph_diff4__phase_diff);
    }
    // Generated from the component: Node 632.RMS6
    _node_632_rms6__previous_filtered_value = _node_632_rms6__filtered_value;
    if (0)
        _node_632_rms6__filtered_value = _node_632_rms6__previous_filtered_value * 1 + _node_632_i1_ia1__out * 1;
    else
        _node_632_rms6__filtered_value = _node_632_rms6__previous_filtered_value * 0.1 + _node_632_i1_ia1__out * 0.9;
    _node_632_rms6__db_timer += 0.00018;
    if( (_node_632_rms6__filtered_value >= 0.0) && (_node_632_rms6__previous_filtered_value < 0.0) && (_node_632_rms6__db_timer >= 0.0) ) {
        _node_632_rms6__zc = 1;
        _node_632_rms6__db_timer = 0;
    } else
        _node_632_rms6__zc = 0;
    _node_632_rms6__out = _node_632_rms6__out_state;
    // Generated from the component: Node 632.RMS5
    _node_632_rms5__previous_filtered_value = _node_632_rms5__filtered_value;
    if (0)
        _node_632_rms5__filtered_value = _node_632_rms5__previous_filtered_value * 1 + _node_632_i2_ia1__out * 1;
    else
        _node_632_rms5__filtered_value = _node_632_rms5__previous_filtered_value * 0.1 + _node_632_i2_ia1__out * 0.9;
    _node_632_rms5__db_timer += 0.00018;
    if( (_node_632_rms5__filtered_value >= 0.0) && (_node_632_rms5__previous_filtered_value < 0.0) && (_node_632_rms5__db_timer >= 0.0) ) {
        _node_632_rms5__zc = 1;
        _node_632_rms5__db_timer = 0;
    } else
        _node_632_rms5__zc = 0;
    _node_632_rms5__out = _node_632_rms5__out_state;
    // Generated from the component: Node 632.Power Meter1
    _node_632_power_meter1__v_alpha = SQRT_2OVER3 * ( _node_632_cpu_transition4_output__out - 0.5f * _node_632_cpu_transition5_output__out - 0.5f * _node_632_cpu_transition6_output__out);
    _node_632_power_meter1__v_beta = SQRT_2OVER3 * (SQRT3_OVER_2 * _node_632_cpu_transition5_output__out - SQRT3_OVER_2 * _node_632_cpu_transition6_output__out);
    _node_632_power_meter1__i_alpha = SQRT_2OVER3 * ( _node_632_i1_ia1__out - 0.5f * _node_632_i2_ia1__out - 0.5f * _node_632_i3_ia1__out);
    _node_632_power_meter1__i_beta = SQRT_2OVER3 * (SQRT3_OVER_2 * _node_632_i2_ia1__out - SQRT3_OVER_2 * _node_632_i3_ia1__out);
    _node_632_power_meter1__v_zero = ONE_DIV_BY_SQRT_3 * (_node_632_cpu_transition4_output__out + _node_632_cpu_transition5_output__out + _node_632_cpu_transition6_output__out);
    _node_632_power_meter1__i_zero = ONE_DIV_BY_SQRT_3 * (_node_632_i1_ia1__out + _node_632_i2_ia1__out + _node_632_i3_ia1__out);
    _node_632_power_meter1__Pac = _node_632_power_meter1__v_alpha * _node_632_power_meter1__i_alpha + _node_632_power_meter1__v_beta * _node_632_power_meter1__i_beta;
    _node_632_power_meter1__Qac = _node_632_power_meter1__v_beta * _node_632_power_meter1__i_alpha - _node_632_power_meter1__v_alpha * _node_632_power_meter1__i_beta;
    _node_632_power_meter1__P0ac = _node_632_power_meter1__v_zero * _node_632_power_meter1__i_zero;
    _node_632_power_meter1__filter_1_output = 0.016681603591600154 * (_node_632_power_meter1__Pac + _node_632_power_meter1__filter_1_input_k_minus_1) - (-0.9666367928167997) * _node_632_power_meter1__filter_1_output_k_minus_1;
    _node_632_power_meter1__filter_1_outputQ = 0.016681603591600154 * (_node_632_power_meter1__Qac + _node_632_power_meter1__filter_1_input_k_minus_1Q) - (-0.9666367928167997) * _node_632_power_meter1__filter_1_output_k_minus_1Q;
    _node_632_power_meter1__filter_1_outputP0 = 0.016681603591600154 * (_node_632_power_meter1__P0ac + _node_632_power_meter1__filter_1_input_k_minus_1P0) - (-0.9666367928167997) * _node_632_power_meter1__filter_1_output_k_minus_1P0;
    _node_632_power_meter1__filter_1_input_k_minus_1 = _node_632_power_meter1__Pac;
    _node_632_power_meter1__filter_1_output_k_minus_1 = _node_632_power_meter1__filter_1_output;
    _node_632_power_meter1__filter_1_input_k_minus_1Q = _node_632_power_meter1__Qac;;
    _node_632_power_meter1__filter_1_output_k_minus_1Q = _node_632_power_meter1__filter_1_outputQ;
    _node_632_power_meter1__filter_1_input_k_minus_1P0 = _node_632_power_meter1__P0ac;
    _node_632_power_meter1__filter_1_output_k_minus_1P0 = _node_632_power_meter1__filter_1_outputP0;
    _node_632_power_meter1__Pdc = _node_632_power_meter1__filter_1_output;
    _node_632_power_meter1__Qdc = _node_632_power_meter1__filter_1_outputQ;
    _node_632_power_meter1__P0dc = _node_632_power_meter1__filter_1_outputP0;
    _node_632_power_meter1__apparent = sqrt(pow(_node_632_power_meter1__Pdc, 2) + pow(_node_632_power_meter1__Qdc, 2));
    if (_node_632_power_meter1__apparent > 0)
        _node_632_power_meter1__k_factor = _node_632_power_meter1__Pdc / _node_632_power_meter1__apparent;
    else
        _node_632_power_meter1__k_factor = 0;
    // Generated from the component: Node 632.RMS4
    _node_632_rms4__previous_filtered_value = _node_632_rms4__filtered_value;
    if (0)
        _node_632_rms4__filtered_value = _node_632_rms4__previous_filtered_value * 1 + _node_632_i3_ia1__out * 1;
    else
        _node_632_rms4__filtered_value = _node_632_rms4__previous_filtered_value * 0.1 + _node_632_i3_ia1__out * 0.9;
    _node_632_rms4__db_timer += 0.00018;
    if( (_node_632_rms4__filtered_value >= 0.0) && (_node_632_rms4__previous_filtered_value < 0.0) && (_node_632_rms4__db_timer >= 0.0) ) {
        _node_632_rms4__zc = 1;
        _node_632_rms4__db_timer = 0;
    } else
        _node_632_rms4__zc = 0;
    _node_632_rms4__out = _node_632_rms4__out_state;
    // Generated from the component: Node 632.I3_phase
    {
        HIL_OutAO(0x40a7, _node_632_ph_diff4__phase_diff);
    }
    // Generated from the component: Node 632.I1_phase
    {
        HIL_OutAO(0x40a3, _node_632_ph_diff5__phase_diff);
    }
    // Generated from the component: Node 632.I2_phase
    {
        HIL_OutAO(0x40a5, _node_632_ph_diff6__phase_diff);
    }
    // Generated from the component: Node 633.RMS6
    _node_633_rms6__previous_filtered_value = _node_633_rms6__filtered_value;
    if (0)
        _node_633_rms6__filtered_value = _node_633_rms6__previous_filtered_value * 1 + _node_633_i1_ia1__out * 1;
    else
        _node_633_rms6__filtered_value = _node_633_rms6__previous_filtered_value * 0.1 + _node_633_i1_ia1__out * 0.9;
    _node_633_rms6__db_timer += 0.00018;
    if( (_node_633_rms6__filtered_value >= 0.0) && (_node_633_rms6__previous_filtered_value < 0.0) && (_node_633_rms6__db_timer >= 0.0) ) {
        _node_633_rms6__zc = 1;
        _node_633_rms6__db_timer = 0;
    } else
        _node_633_rms6__zc = 0;
    _node_633_rms6__out = _node_633_rms6__out_state;
    // Generated from the component: Node 633.RMS5
    _node_633_rms5__previous_filtered_value = _node_633_rms5__filtered_value;
    if (0)
        _node_633_rms5__filtered_value = _node_633_rms5__previous_filtered_value * 1 + _node_633_i2_ia1__out * 1;
    else
        _node_633_rms5__filtered_value = _node_633_rms5__previous_filtered_value * 0.1 + _node_633_i2_ia1__out * 0.9;
    _node_633_rms5__db_timer += 0.00018;
    if( (_node_633_rms5__filtered_value >= 0.0) && (_node_633_rms5__previous_filtered_value < 0.0) && (_node_633_rms5__db_timer >= 0.0) ) {
        _node_633_rms5__zc = 1;
        _node_633_rms5__db_timer = 0;
    } else
        _node_633_rms5__zc = 0;
    _node_633_rms5__out = _node_633_rms5__out_state;
    // Generated from the component: Node 633.RMS4
    _node_633_rms4__previous_filtered_value = _node_633_rms4__filtered_value;
    if (0)
        _node_633_rms4__filtered_value = _node_633_rms4__previous_filtered_value * 1 + _node_633_i3_ia1__out * 1;
    else
        _node_633_rms4__filtered_value = _node_633_rms4__previous_filtered_value * 0.1 + _node_633_i3_ia1__out * 0.9;
    _node_633_rms4__db_timer += 0.00018;
    if( (_node_633_rms4__filtered_value >= 0.0) && (_node_633_rms4__previous_filtered_value < 0.0) && (_node_633_rms4__db_timer >= 0.0) ) {
        _node_633_rms4__zc = 1;
        _node_633_rms4__db_timer = 0;
    } else
        _node_633_rms4__zc = 0;
    _node_633_rms4__out = _node_633_rms4__out_state;
    // Generated from the component: Node 633.I3_phase
    {
        HIL_OutAO(0x40ae, _node_633_ph_diff4__phase_diff);
    }
    // Generated from the component: Node 633.I1_phase
    {
        HIL_OutAO(0x40aa, _node_633_ph_diff5__phase_diff);
    }
    // Generated from the component: Node 633.I2_phase
    {
        HIL_OutAO(0x40ac, _node_633_ph_diff6__phase_diff);
    }
    // Generated from the component: Node 634.RMS6
    _node_634_rms6__previous_filtered_value = _node_634_rms6__filtered_value;
    if (0)
        _node_634_rms6__filtered_value = _node_634_rms6__previous_filtered_value * 1 + _node_634_i1_ia1__out * 1;
    else
        _node_634_rms6__filtered_value = _node_634_rms6__previous_filtered_value * 0.1 + _node_634_i1_ia1__out * 0.9;
    _node_634_rms6__db_timer += 0.00018;
    if( (_node_634_rms6__filtered_value >= 0.0) && (_node_634_rms6__previous_filtered_value < 0.0) && (_node_634_rms6__db_timer >= 0.0) ) {
        _node_634_rms6__zc = 1;
        _node_634_rms6__db_timer = 0;
    } else
        _node_634_rms6__zc = 0;
    _node_634_rms6__out = _node_634_rms6__out_state;
    // Generated from the component: Node 634.RMS5
    _node_634_rms5__previous_filtered_value = _node_634_rms5__filtered_value;
    if (0)
        _node_634_rms5__filtered_value = _node_634_rms5__previous_filtered_value * 1 + _node_634_i2_ia1__out * 1;
    else
        _node_634_rms5__filtered_value = _node_634_rms5__previous_filtered_value * 0.1 + _node_634_i2_ia1__out * 0.9;
    _node_634_rms5__db_timer += 0.00018;
    if( (_node_634_rms5__filtered_value >= 0.0) && (_node_634_rms5__previous_filtered_value < 0.0) && (_node_634_rms5__db_timer >= 0.0) ) {
        _node_634_rms5__zc = 1;
        _node_634_rms5__db_timer = 0;
    } else
        _node_634_rms5__zc = 0;
    _node_634_rms5__out = _node_634_rms5__out_state;
    // Generated from the component: Node 634.RMS4
    _node_634_rms4__previous_filtered_value = _node_634_rms4__filtered_value;
    if (0)
        _node_634_rms4__filtered_value = _node_634_rms4__previous_filtered_value * 1 + _node_634_i3_ia1__out * 1;
    else
        _node_634_rms4__filtered_value = _node_634_rms4__previous_filtered_value * 0.1 + _node_634_i3_ia1__out * 0.9;
    _node_634_rms4__db_timer += 0.00018;
    if( (_node_634_rms4__filtered_value >= 0.0) && (_node_634_rms4__previous_filtered_value < 0.0) && (_node_634_rms4__db_timer >= 0.0) ) {
        _node_634_rms4__zc = 1;
        _node_634_rms4__db_timer = 0;
    } else
        _node_634_rms4__zc = 0;
    _node_634_rms4__out = _node_634_rms4__out_state;
    // Generated from the component: Node 634.I3_phase
    {
        HIL_OutAO(0x40b4, _node_634_ph_diff4__phase_diff);
    }
    // Generated from the component: Node 634.I1_phase
    {
        HIL_OutAO(0x40b0, _node_634_ph_diff5__phase_diff);
    }
    // Generated from the component: Node 634.I2_phase
    {
        HIL_OutAO(0x40b2, _node_634_ph_diff6__phase_diff);
    }
    // Generated from the component: Node 645.RMS5
    _node_645_rms5__previous_filtered_value = _node_645_rms5__filtered_value;
    if (0)
        _node_645_rms5__filtered_value = _node_645_rms5__previous_filtered_value * 1 + _node_645_i2_ia1__out * 1;
    else
        _node_645_rms5__filtered_value = _node_645_rms5__previous_filtered_value * 0.1 + _node_645_i2_ia1__out * 0.9;
    _node_645_rms5__db_timer += 0.00018;
    if( (_node_645_rms5__filtered_value >= 0.0) && (_node_645_rms5__previous_filtered_value < 0.0) && (_node_645_rms5__db_timer >= 0.0) ) {
        _node_645_rms5__zc = 1;
        _node_645_rms5__db_timer = 0;
    } else
        _node_645_rms5__zc = 0;
    _node_645_rms5__out = _node_645_rms5__out_state;
    // Generated from the component: Node 645.RMS4
    _node_645_rms4__previous_filtered_value = _node_645_rms4__filtered_value;
    if (0)
        _node_645_rms4__filtered_value = _node_645_rms4__previous_filtered_value * 1 + _node_645_i3_ia1__out * 1;
    else
        _node_645_rms4__filtered_value = _node_645_rms4__previous_filtered_value * 0.1 + _node_645_i3_ia1__out * 0.9;
    _node_645_rms4__db_timer += 0.00018;
    if( (_node_645_rms4__filtered_value >= 0.0) && (_node_645_rms4__previous_filtered_value < 0.0) && (_node_645_rms4__db_timer >= 0.0) ) {
        _node_645_rms4__zc = 1;
        _node_645_rms4__db_timer = 0;
    } else
        _node_645_rms4__zc = 0;
    _node_645_rms4__out = _node_645_rms4__out_state;
    // Generated from the component: Node 645.I3_phase
    {
        HIL_OutAO(0x40b8, _node_645_ph_diff4__phase_diff);
    }
    // Generated from the component: Node 645.I2_phase
    {
        HIL_OutAO(0x40b6, _node_645_ph_diff6__phase_diff);
    }
    // Generated from the component: Node 646.RMS5
    _node_646_rms5__previous_filtered_value = _node_646_rms5__filtered_value;
    if (0)
        _node_646_rms5__filtered_value = _node_646_rms5__previous_filtered_value * 1 + _node_646_i2_ia1__out * 1;
    else
        _node_646_rms5__filtered_value = _node_646_rms5__previous_filtered_value * 0.1 + _node_646_i2_ia1__out * 0.9;
    _node_646_rms5__db_timer += 0.00018;
    if( (_node_646_rms5__filtered_value >= 0.0) && (_node_646_rms5__previous_filtered_value < 0.0) && (_node_646_rms5__db_timer >= 0.0) ) {
        _node_646_rms5__zc = 1;
        _node_646_rms5__db_timer = 0;
    } else
        _node_646_rms5__zc = 0;
    _node_646_rms5__out = _node_646_rms5__out_state;
    // Generated from the component: Node 646.RMS4
    _node_646_rms4__previous_filtered_value = _node_646_rms4__filtered_value;
    if (0)
        _node_646_rms4__filtered_value = _node_646_rms4__previous_filtered_value * 1 + _node_646_i3_ia1__out * 1;
    else
        _node_646_rms4__filtered_value = _node_646_rms4__previous_filtered_value * 0.1 + _node_646_i3_ia1__out * 0.9;
    _node_646_rms4__db_timer += 0.00018;
    if( (_node_646_rms4__filtered_value >= 0.0) && (_node_646_rms4__previous_filtered_value < 0.0) && (_node_646_rms4__db_timer >= 0.0) ) {
        _node_646_rms4__zc = 1;
        _node_646_rms4__db_timer = 0;
    } else
        _node_646_rms4__zc = 0;
    _node_646_rms4__out = _node_646_rms4__out_state;
    // Generated from the component: Node 646.I3_phase
    {
        HIL_OutAO(0x40bc, _node_646_ph_diff4__phase_diff);
    }
    // Generated from the component: Node 646.I2_phase
    {
        HIL_OutAO(0x40ba, _node_646_ph_diff6__phase_diff);
    }
    // Generated from the component: Node 652.RMS6
    _node_652_rms6__previous_filtered_value = _node_652_rms6__filtered_value;
    if (0)
        _node_652_rms6__filtered_value = _node_652_rms6__previous_filtered_value * 1 + _node_652_i1_ia1__out * 1;
    else
        _node_652_rms6__filtered_value = _node_652_rms6__previous_filtered_value * 0.1 + _node_652_i1_ia1__out * 0.9;
    _node_652_rms6__db_timer += 0.00018;
    if( (_node_652_rms6__filtered_value >= 0.0) && (_node_652_rms6__previous_filtered_value < 0.0) && (_node_652_rms6__db_timer >= 0.0) ) {
        _node_652_rms6__zc = 1;
        _node_652_rms6__db_timer = 0;
    } else
        _node_652_rms6__zc = 0;
    _node_652_rms6__out = _node_652_rms6__out_state;
    // Generated from the component: Node 652.I1_phase
    {
        HIL_OutAO(0x40be, _node_652_ph_diff5__phase_diff);
    }
    // Generated from the component: Node 671.RMS6
    _node_671_rms6__previous_filtered_value = _node_671_rms6__filtered_value;
    if (0)
        _node_671_rms6__filtered_value = _node_671_rms6__previous_filtered_value * 1 + _node_671_i1_ia1__out * 1;
    else
        _node_671_rms6__filtered_value = _node_671_rms6__previous_filtered_value * 0.1 + _node_671_i1_ia1__out * 0.9;
    _node_671_rms6__db_timer += 0.00018;
    if( (_node_671_rms6__filtered_value >= 0.0) && (_node_671_rms6__previous_filtered_value < 0.0) && (_node_671_rms6__db_timer >= 0.0) ) {
        _node_671_rms6__zc = 1;
        _node_671_rms6__db_timer = 0;
    } else
        _node_671_rms6__zc = 0;
    _node_671_rms6__out = _node_671_rms6__out_state;
    // Generated from the component: Node 671.RMS5
    _node_671_rms5__previous_filtered_value = _node_671_rms5__filtered_value;
    if (0)
        _node_671_rms5__filtered_value = _node_671_rms5__previous_filtered_value * 1 + _node_671_i2_ia1__out * 1;
    else
        _node_671_rms5__filtered_value = _node_671_rms5__previous_filtered_value * 0.1 + _node_671_i2_ia1__out * 0.9;
    _node_671_rms5__db_timer += 0.00018;
    if( (_node_671_rms5__filtered_value >= 0.0) && (_node_671_rms5__previous_filtered_value < 0.0) && (_node_671_rms5__db_timer >= 0.0) ) {
        _node_671_rms5__zc = 1;
        _node_671_rms5__db_timer = 0;
    } else
        _node_671_rms5__zc = 0;
    _node_671_rms5__out = _node_671_rms5__out_state;
    // Generated from the component: Node 671.RMS4
    _node_671_rms4__previous_filtered_value = _node_671_rms4__filtered_value;
    if (0)
        _node_671_rms4__filtered_value = _node_671_rms4__previous_filtered_value * 1 + _node_671_i3_ia1__out * 1;
    else
        _node_671_rms4__filtered_value = _node_671_rms4__previous_filtered_value * 0.1 + _node_671_i3_ia1__out * 0.9;
    _node_671_rms4__db_timer += 0.00018;
    if( (_node_671_rms4__filtered_value >= 0.0) && (_node_671_rms4__previous_filtered_value < 0.0) && (_node_671_rms4__db_timer >= 0.0) ) {
        _node_671_rms4__zc = 1;
        _node_671_rms4__db_timer = 0;
    } else
        _node_671_rms4__zc = 0;
    _node_671_rms4__out = _node_671_rms4__out_state;
    // Generated from the component: Node 671.I3_phase
    {
        HIL_OutAO(0x40c4, _node_671_ph_diff4__phase_diff);
    }
    // Generated from the component: Node 671.I1_phase
    {
        HIL_OutAO(0x40c0, _node_671_ph_diff5__phase_diff);
    }
    // Generated from the component: Node 671.I2_phase
    {
        HIL_OutAO(0x40c2, _node_671_ph_diff6__phase_diff);
    }
    // Generated from the component: Node 675.RMS6
    _node_675_rms6__previous_filtered_value = _node_675_rms6__filtered_value;
    if (0)
        _node_675_rms6__filtered_value = _node_675_rms6__previous_filtered_value * 1 + _node_675_i1_ia1__out * 1;
    else
        _node_675_rms6__filtered_value = _node_675_rms6__previous_filtered_value * 0.1 + _node_675_i1_ia1__out * 0.9;
    _node_675_rms6__db_timer += 0.00018;
    if( (_node_675_rms6__filtered_value >= 0.0) && (_node_675_rms6__previous_filtered_value < 0.0) && (_node_675_rms6__db_timer >= 0.0) ) {
        _node_675_rms6__zc = 1;
        _node_675_rms6__db_timer = 0;
    } else
        _node_675_rms6__zc = 0;
    _node_675_rms6__out = _node_675_rms6__out_state;
    // Generated from the component: Node 675.RMS5
    _node_675_rms5__previous_filtered_value = _node_675_rms5__filtered_value;
    if (0)
        _node_675_rms5__filtered_value = _node_675_rms5__previous_filtered_value * 1 + _node_675_i2_ia1__out * 1;
    else
        _node_675_rms5__filtered_value = _node_675_rms5__previous_filtered_value * 0.1 + _node_675_i2_ia1__out * 0.9;
    _node_675_rms5__db_timer += 0.00018;
    if( (_node_675_rms5__filtered_value >= 0.0) && (_node_675_rms5__previous_filtered_value < 0.0) && (_node_675_rms5__db_timer >= 0.0) ) {
        _node_675_rms5__zc = 1;
        _node_675_rms5__db_timer = 0;
    } else
        _node_675_rms5__zc = 0;
    _node_675_rms5__out = _node_675_rms5__out_state;
    // Generated from the component: Node 675.RMS4
    _node_675_rms4__previous_filtered_value = _node_675_rms4__filtered_value;
    if (0)
        _node_675_rms4__filtered_value = _node_675_rms4__previous_filtered_value * 1 + _node_675_i3_ia1__out * 1;
    else
        _node_675_rms4__filtered_value = _node_675_rms4__previous_filtered_value * 0.1 + _node_675_i3_ia1__out * 0.9;
    _node_675_rms4__db_timer += 0.00018;
    if( (_node_675_rms4__filtered_value >= 0.0) && (_node_675_rms4__previous_filtered_value < 0.0) && (_node_675_rms4__db_timer >= 0.0) ) {
        _node_675_rms4__zc = 1;
        _node_675_rms4__db_timer = 0;
    } else
        _node_675_rms4__zc = 0;
    _node_675_rms4__out = _node_675_rms4__out_state;
    // Generated from the component: Node 675.I3_phase
    {
        HIL_OutAO(0x40ca, _node_675_ph_diff4__phase_diff);
    }
    // Generated from the component: Node 675.I1_phase
    {
        HIL_OutAO(0x40c6, _node_675_ph_diff5__phase_diff);
    }
    // Generated from the component: Node 675.I2_phase
    {
        HIL_OutAO(0x40c8, _node_675_ph_diff6__phase_diff);
    }
    // Generated from the component: Node 680.RMS6
    _node_680_rms6__previous_filtered_value = _node_680_rms6__filtered_value;
    if (0)
        _node_680_rms6__filtered_value = _node_680_rms6__previous_filtered_value * 1 + _node_680_i1_ia1__out * 1;
    else
        _node_680_rms6__filtered_value = _node_680_rms6__previous_filtered_value * 0.1 + _node_680_i1_ia1__out * 0.9;
    _node_680_rms6__db_timer += 0.00018;
    if( (_node_680_rms6__filtered_value >= 0.0) && (_node_680_rms6__previous_filtered_value < 0.0) && (_node_680_rms6__db_timer >= 0.0) ) {
        _node_680_rms6__zc = 1;
        _node_680_rms6__db_timer = 0;
    } else
        _node_680_rms6__zc = 0;
    _node_680_rms6__out = _node_680_rms6__out_state;
    // Generated from the component: Node 680.RMS5
    _node_680_rms5__previous_filtered_value = _node_680_rms5__filtered_value;
    if (0)
        _node_680_rms5__filtered_value = _node_680_rms5__previous_filtered_value * 1 + _node_680_i2_ia1__out * 1;
    else
        _node_680_rms5__filtered_value = _node_680_rms5__previous_filtered_value * 0.1 + _node_680_i2_ia1__out * 0.9;
    _node_680_rms5__db_timer += 0.00018;
    if( (_node_680_rms5__filtered_value >= 0.0) && (_node_680_rms5__previous_filtered_value < 0.0) && (_node_680_rms5__db_timer >= 0.0) ) {
        _node_680_rms5__zc = 1;
        _node_680_rms5__db_timer = 0;
    } else
        _node_680_rms5__zc = 0;
    _node_680_rms5__out = _node_680_rms5__out_state;
    // Generated from the component: Node 680.RMS4
    _node_680_rms4__previous_filtered_value = _node_680_rms4__filtered_value;
    if (0)
        _node_680_rms4__filtered_value = _node_680_rms4__previous_filtered_value * 1 + _node_680_i3_ia1__out * 1;
    else
        _node_680_rms4__filtered_value = _node_680_rms4__previous_filtered_value * 0.1 + _node_680_i3_ia1__out * 0.9;
    _node_680_rms4__db_timer += 0.00018;
    if( (_node_680_rms4__filtered_value >= 0.0) && (_node_680_rms4__previous_filtered_value < 0.0) && (_node_680_rms4__db_timer >= 0.0) ) {
        _node_680_rms4__zc = 1;
        _node_680_rms4__db_timer = 0;
    } else
        _node_680_rms4__zc = 0;
    _node_680_rms4__out = _node_680_rms4__out_state;
    // Generated from the component: Node 680.I3_phase
    {
        HIL_OutAO(0x40d0, _node_680_ph_diff4__phase_diff);
    }
    // Generated from the component: Node 680.I1_phase
    {
        HIL_OutAO(0x40cc, _node_680_ph_diff5__phase_diff);
    }
    // Generated from the component: Node 680.I2_phase
    {
        HIL_OutAO(0x40ce, _node_680_ph_diff6__phase_diff);
    }
    // Generated from the component: Node 684.RMS6
    _node_684_rms6__previous_filtered_value = _node_684_rms6__filtered_value;
    if (0)
        _node_684_rms6__filtered_value = _node_684_rms6__previous_filtered_value * 1 + _node_684_i1_ia1__out * 1;
    else
        _node_684_rms6__filtered_value = _node_684_rms6__previous_filtered_value * 0.1 + _node_684_i1_ia1__out * 0.9;
    _node_684_rms6__db_timer += 0.00018;
    if( (_node_684_rms6__filtered_value >= 0.0) && (_node_684_rms6__previous_filtered_value < 0.0) && (_node_684_rms6__db_timer >= 0.0) ) {
        _node_684_rms6__zc = 1;
        _node_684_rms6__db_timer = 0;
    } else
        _node_684_rms6__zc = 0;
    _node_684_rms6__out = _node_684_rms6__out_state;
    // Generated from the component: Node 684.RMS4
    _node_684_rms4__previous_filtered_value = _node_684_rms4__filtered_value;
    if (0)
        _node_684_rms4__filtered_value = _node_684_rms4__previous_filtered_value * 1 + _node_684_i3_ia1__out * 1;
    else
        _node_684_rms4__filtered_value = _node_684_rms4__previous_filtered_value * 0.1 + _node_684_i3_ia1__out * 0.9;
    _node_684_rms4__db_timer += 0.00018;
    if( (_node_684_rms4__filtered_value >= 0.0) && (_node_684_rms4__previous_filtered_value < 0.0) && (_node_684_rms4__db_timer >= 0.0) ) {
        _node_684_rms4__zc = 1;
        _node_684_rms4__db_timer = 0;
    } else
        _node_684_rms4__zc = 0;
    _node_684_rms4__out = _node_684_rms4__out_state;
    // Generated from the component: Node 684.I3_phase
    {
        HIL_OutAO(0x40d4, _node_684_ph_diff4__phase_diff);
    }
    // Generated from the component: Node 684.I1_phase
    {
        HIL_OutAO(0x40d2, _node_684_ph_diff5__phase_diff);
    }
    // Generated from the component: Node 692.RMS6
    _node_692_rms6__previous_filtered_value = _node_692_rms6__filtered_value;
    if (0)
        _node_692_rms6__filtered_value = _node_692_rms6__previous_filtered_value * 1 + _node_692_i1_ia1__out * 1;
    else
        _node_692_rms6__filtered_value = _node_692_rms6__previous_filtered_value * 0.1 + _node_692_i1_ia1__out * 0.9;
    _node_692_rms6__db_timer += 0.00018;
    if( (_node_692_rms6__filtered_value >= 0.0) && (_node_692_rms6__previous_filtered_value < 0.0) && (_node_692_rms6__db_timer >= 0.0) ) {
        _node_692_rms6__zc = 1;
        _node_692_rms6__db_timer = 0;
    } else
        _node_692_rms6__zc = 0;
    _node_692_rms6__out = _node_692_rms6__out_state;
    // Generated from the component: Node 692.RMS5
    _node_692_rms5__previous_filtered_value = _node_692_rms5__filtered_value;
    if (0)
        _node_692_rms5__filtered_value = _node_692_rms5__previous_filtered_value * 1 + _node_692_i2_ia1__out * 1;
    else
        _node_692_rms5__filtered_value = _node_692_rms5__previous_filtered_value * 0.1 + _node_692_i2_ia1__out * 0.9;
    _node_692_rms5__db_timer += 0.00018;
    if( (_node_692_rms5__filtered_value >= 0.0) && (_node_692_rms5__previous_filtered_value < 0.0) && (_node_692_rms5__db_timer >= 0.0) ) {
        _node_692_rms5__zc = 1;
        _node_692_rms5__db_timer = 0;
    } else
        _node_692_rms5__zc = 0;
    _node_692_rms5__out = _node_692_rms5__out_state;
    // Generated from the component: Node 692.RMS4
    _node_692_rms4__previous_filtered_value = _node_692_rms4__filtered_value;
    if (0)
        _node_692_rms4__filtered_value = _node_692_rms4__previous_filtered_value * 1 + _node_692_i3_ia1__out * 1;
    else
        _node_692_rms4__filtered_value = _node_692_rms4__previous_filtered_value * 0.1 + _node_692_i3_ia1__out * 0.9;
    _node_692_rms4__db_timer += 0.00018;
    if( (_node_692_rms4__filtered_value >= 0.0) && (_node_692_rms4__previous_filtered_value < 0.0) && (_node_692_rms4__db_timer >= 0.0) ) {
        _node_692_rms4__zc = 1;
        _node_692_rms4__db_timer = 0;
    } else
        _node_692_rms4__zc = 0;
    _node_692_rms4__out = _node_692_rms4__out_state;
    // Generated from the component: Node 692.I3_phase
    {
        HIL_OutAO(0x40da, _node_692_ph_diff4__phase_diff);
    }
    // Generated from the component: Node 692.I1_phase
    {
        HIL_OutAO(0x40d6, _node_692_ph_diff5__phase_diff);
    }
    // Generated from the component: Node 692.I2_phase
    {
        HIL_OutAO(0x40d8, _node_692_ph_diff6__phase_diff);
    }
    // Generated from the component: Node 611.CPU Transition1.Input
    {
        XIo_OutFloat(0x2f4000e8, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 632.CPU Transition1.Input
    {
        XIo_OutFloat(0x2f4000ec, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 632.CPU Transition2.Input
    {
        XIo_OutFloat(0x2f4000f0, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 632.CPU Transition3.Input
    {
        XIo_OutFloat(0x2f4000f4, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 633.CPU Transition1.Input
    {
        XIo_OutFloat(0x2f4000f8, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 633.CPU Transition2.Input
    {
        XIo_OutFloat(0x2f4000fc, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 633.CPU Transition3.Input
    {
        XIo_OutFloat(0x2f400100, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 634.CPU Transition1.Input
    {
        XIo_OutFloat(0x2f400104, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 634.CPU Transition2.Input
    {
        XIo_OutFloat(0x2f400108, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 634.CPU Transition3.Input
    {
        XIo_OutFloat(0x2f40010c, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 645.CPU Transition1.Input
    {
        XIo_OutFloat(0x2f400110, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 645.CPU Transition2.Input
    {
        XIo_OutFloat(0x2f400114, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 646.CPU Transition1.Input
    {
        XIo_OutFloat(0x2f400118, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 646.CPU Transition2.Input
    {
        XIo_OutFloat(0x2f40011c, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 652.CPU Transition1.Input
    {
        XIo_OutFloat(0x2f400120, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 671.CPU Transition1.Input
    {
        XIo_OutFloat(0x2f400124, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 671.CPU Transition2.Input
    {
        XIo_OutFloat(0x2f400128, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 671.CPU Transition3.Input
    {
        XIo_OutFloat(0x2f40012c, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 675.CPU Transition1.Input
    {
        XIo_OutFloat(0x2f400130, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 675.CPU Transition2.Input
    {
        XIo_OutFloat(0x2f400134, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 675.CPU Transition3.Input
    {
        XIo_OutFloat(0x2f400138, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 680.CPU Transition1.Input
    {
        XIo_OutFloat(0x2f40013c, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 680.CPU Transition2.Input
    {
        XIo_OutFloat(0x2f400140, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 680.CPU Transition3.Input
    {
        XIo_OutFloat(0x2f400144, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 684.CPU Transition1.Input
    {
        XIo_OutFloat(0x2f400148, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 684.CPU Transition2.Input
    {
        XIo_OutFloat(0x2f40014c, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 692.CPU Transition1.Input
    {
        XIo_OutFloat(0x2f400150, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 692.CPU Transition2.Input
    {
        XIo_OutFloat(0x2f400154, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: Node 692.CPU Transition3.Input
    {
        XIo_OutFloat(0x2f400158, _reference_v1_ref2_va1__out);
    }
    // Generated from the component: S1.Triple S1 ideal.CTC_Wrapper
    {
        {
            if((_switch_state__out == 0)) {
                HIL_OutInt32(0x8240480, 0);
            }
            else {
                HIL_OutInt32(0x8240480, 1);
            }
        }
    }
    // Generated from the component: MSR 632-671.I1_rms
    {
        HIL_OutAO(0x409c, _msr_632_671_rms6__out);
    }
    // Generated from the component: MSR 632-671.I2_rms
    {
        HIL_OutAO(0x409e, _msr_632_671_rms5__out);
    }
    // Generated from the component: MSR 632-671.I3_rms
    {
        HIL_OutAO(0x40a0, _msr_632_671_rms4__out);
    }
    // Generated from the component: Node 611.I3_rms
    {
        HIL_OutAO(0x40a2, _node_611_rms4__out);
    }
    // Generated from the component: Node 632.I1_rms
    {
        HIL_OutAO(0x40a4, _node_632_rms6__out);
    }
    // Generated from the component: Node 632.I2_rms
    {
        HIL_OutAO(0x40a6, _node_632_rms5__out);
    }
    // Generated from the component: Node 632.Probe1
    {
        HIL_OutAO(0x40a9, _node_632_power_meter1__Pdc);
    }
    // Generated from the component: Node 632.I3_rms
    {
        HIL_OutAO(0x40a8, _node_632_rms4__out);
    }
    // Generated from the component: Node 633.I1_rms
    {
        HIL_OutAO(0x40ab, _node_633_rms6__out);
    }
    // Generated from the component: Node 633.I2_rms
    {
        HIL_OutAO(0x40ad, _node_633_rms5__out);
    }
    // Generated from the component: Node 633.I3_rms
    {
        HIL_OutAO(0x40af, _node_633_rms4__out);
    }
    // Generated from the component: Node 634.I1_rms
    {
        HIL_OutAO(0x40b1, _node_634_rms6__out);
    }
    // Generated from the component: Node 634.I2_rms
    {
        HIL_OutAO(0x40b3, _node_634_rms5__out);
    }
    // Generated from the component: Node 634.I3_rms
    {
        HIL_OutAO(0x40b5, _node_634_rms4__out);
    }
    // Generated from the component: Node 645.I2_rms
    {
        HIL_OutAO(0x40b7, _node_645_rms5__out);
    }
    // Generated from the component: Node 645.I3_rms
    {
        HIL_OutAO(0x40b9, _node_645_rms4__out);
    }
    // Generated from the component: Node 646.I2_rms
    {
        HIL_OutAO(0x40bb, _node_646_rms5__out);
    }
    // Generated from the component: Node 646.I3_rms
    {
        HIL_OutAO(0x40bd, _node_646_rms4__out);
    }
    // Generated from the component: Node 652.I1_rms
    {
        HIL_OutAO(0x40bf, _node_652_rms6__out);
    }
    // Generated from the component: Node 671.I1_rms
    {
        HIL_OutAO(0x40c1, _node_671_rms6__out);
    }
    // Generated from the component: Node 671.I2_rms
    {
        HIL_OutAO(0x40c3, _node_671_rms5__out);
    }
    // Generated from the component: Node 671.I3_rms
    {
        HIL_OutAO(0x40c5, _node_671_rms4__out);
    }
    // Generated from the component: Node 675.I1_rms
    {
        HIL_OutAO(0x40c7, _node_675_rms6__out);
    }
    // Generated from the component: Node 675.I2_rms
    {
        HIL_OutAO(0x40c9, _node_675_rms5__out);
    }
    // Generated from the component: Node 675.I3_rms
    {
        HIL_OutAO(0x40cb, _node_675_rms4__out);
    }
    // Generated from the component: Node 680.I1_rms
    {
        HIL_OutAO(0x40cd, _node_680_rms6__out);
    }
    // Generated from the component: Node 680.I2_rms
    {
        HIL_OutAO(0x40cf, _node_680_rms5__out);
    }
    // Generated from the component: Node 680.I3_rms
    {
        HIL_OutAO(0x40d1, _node_680_rms4__out);
    }
    // Generated from the component: Node 684.I1_rms
    {
        HIL_OutAO(0x40d3, _node_684_rms6__out);
    }
    // Generated from the component: Node 684.I3_rms
    {
        HIL_OutAO(0x40d5, _node_684_rms4__out);
    }
    // Generated from the component: Node 692.I1_rms
    {
        HIL_OutAO(0x40d7, _node_692_rms6__out);
    }
    // Generated from the component: Node 692.I2_rms
    {
        HIL_OutAO(0x40d9, _node_692_rms5__out);
    }
    // Generated from the component: Node 692.I3_rms
    {
        HIL_OutAO(0x40db, _node_692_rms4__out);
    }
//@cmp.out.block.end
    //////////////////////////////////////////////////////////////////////////
    // Update block
    //////////////////////////////////////////////////////////////////////////
    //@cmp.update.block.start
    // Generated from the component: MSR 632-671.I1.Ia1
    // Generated from the component: MSR 632-671.I2.Ia1
    // Generated from the component: MSR 632-671.I3.Ia1
    // Generated from the component: MSR 632-671.ph_diff4
    {
        _msr_632_671_ph_diff4__sample_cnt_ref += 1.0;
        _msr_632_671_ph_diff4__previous_filtered_ref = _msr_632_671_ph_diff4__filtered_ref;
        _msr_632_671_ph_diff4__filtered_ref = ((_msr_632_671_ph_diff4__previous_filtered_ref * _msr_632_671_ph_diff4__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _msr_632_671_ph_diff4__n_alpha[0]));
        if((_msr_632_671_ph_diff4__sample_cnt_ref >= _msr_632_671_ph_diff4__n_timeout[0])) {
            _msr_632_671_ph_diff4__zc_flag_ref = 0;
            _msr_632_671_ph_diff4__sample_cnt_ref = 0;
            _msr_632_671_ph_diff4__previous_correction_ref = 0;
            _msr_632_671_ph_diff4__phase_state = 0;
        }
        else {
            if(((_msr_632_671_ph_diff4__filtered_ref >= 0) && (_msr_632_671_ph_diff4__previous_filtered_ref < 0))) {
                _msr_632_671_ph_diff4__zc_flag_ref = 1;
            }
            else {
                _msr_632_671_ph_diff4__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _msr_632_671_ph_diff4__n_out_size; tmp1 += 1) {
            _msr_632_671_ph_diff4__sample_cnt_in += 1;
            _msr_632_671_ph_diff4__previous_filtered_in = _msr_632_671_ph_diff4__filtered_in;
            _msr_632_671_ph_diff4__filtered_in = ((_msr_632_671_ph_diff4__previous_filtered_in * _msr_632_671_ph_diff4__n_one_minus_alpha[0]) + (_msr_632_671_i3_ia1__out * _msr_632_671_ph_diff4__n_alpha[0]));
            if((_msr_632_671_ph_diff4__sample_cnt_in >= _msr_632_671_ph_diff4__n_timeout[0])) {
                _msr_632_671_ph_diff4__zc_flag_in[0] = 0;
                _msr_632_671_ph_diff4__no_zc_flag_in[0] = 1;
                _msr_632_671_ph_diff4__sample_cnt_in = 0;
                _msr_632_671_ph_diff4__previous_correction_in = 0;
                _msr_632_671_ph_diff4__phase_state = 0;
            }
            else {
                if(((_msr_632_671_ph_diff4__filtered_in >= 0) && (_msr_632_671_ph_diff4__previous_filtered_in < 0))) {
                    _msr_632_671_ph_diff4__zc_flag_in[0] = 1;
                    _msr_632_671_ph_diff4__no_zc_flag_in[0] = 0;
                }
                else {
                    _msr_632_671_ph_diff4__zc_flag_in[0] = 0;
                }
            }
        }
        if(_msr_632_671_ph_diff4__zc_flag_ref) {
            _msr_632_671_ph_diff4__correction_ref = ((- _msr_632_671_ph_diff4__previous_filtered_ref) / ((_msr_632_671_ph_diff4__filtered_ref - _msr_632_671_ph_diff4__previous_filtered_ref)));
            _msr_632_671_ph_diff4__sample_cnt_ref += ((_msr_632_671_ph_diff4__correction_ref - _msr_632_671_ph_diff4__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _msr_632_671_ph_diff4__n_out_size; tmp2 += 1) {
                if((fabs(_msr_632_671_ph_diff4__sample_cnt_ref) > 1e-06)) {
                    if((!_msr_632_671_ph_diff4__no_zc_flag_in[0])) {
                        _msr_632_671_ph_diff4__phase_state = ((360 * (((_msr_632_671_ph_diff4__sample_cnt_in + _msr_632_671_ph_diff4__correction_ref) - _msr_632_671_ph_diff4__previous_correction_in))) / _msr_632_671_ph_diff4__sample_cnt_ref);
                    }
                }
                if((fabs(_msr_632_671_ph_diff4__phase_state) > 360)) {
                    _msr_632_671_ph_diff4__phase_state = fmod(_msr_632_671_ph_diff4__phase_state, 360);
                }
                if((_msr_632_671_ph_diff4__phase_state < (- 180))) {
                    _msr_632_671_ph_diff4__phase_state += 360;
                }
                if((_msr_632_671_ph_diff4__phase_state > 180)) {
                    _msr_632_671_ph_diff4__phase_state -= 360;
                }
            }
            _msr_632_671_ph_diff4__sample_cnt_ref = 0;
            _msr_632_671_ph_diff4__previous_correction_ref = _msr_632_671_ph_diff4__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _msr_632_671_ph_diff4__n_out_size; tmp3 += 1) {
            if(_msr_632_671_ph_diff4__zc_flag_in[0]) {
                _msr_632_671_ph_diff4__correction_in = ((- _msr_632_671_ph_diff4__previous_filtered_in) / ((_msr_632_671_ph_diff4__filtered_in - _msr_632_671_ph_diff4__previous_filtered_in)));
                _msr_632_671_ph_diff4__sample_cnt_in = 0;
                _msr_632_671_ph_diff4__previous_correction_in = _msr_632_671_ph_diff4__correction_in;
            }
        }
    }
    // Generated from the component: MSR 632-671.ph_diff5
    {
        _msr_632_671_ph_diff5__sample_cnt_ref += 1.0;
        _msr_632_671_ph_diff5__previous_filtered_ref = _msr_632_671_ph_diff5__filtered_ref;
        _msr_632_671_ph_diff5__filtered_ref = ((_msr_632_671_ph_diff5__previous_filtered_ref * _msr_632_671_ph_diff5__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _msr_632_671_ph_diff5__n_alpha[0]));
        if((_msr_632_671_ph_diff5__sample_cnt_ref >= _msr_632_671_ph_diff5__n_timeout[0])) {
            _msr_632_671_ph_diff5__zc_flag_ref = 0;
            _msr_632_671_ph_diff5__sample_cnt_ref = 0;
            _msr_632_671_ph_diff5__previous_correction_ref = 0;
            _msr_632_671_ph_diff5__phase_state = 0;
        }
        else {
            if(((_msr_632_671_ph_diff5__filtered_ref >= 0) && (_msr_632_671_ph_diff5__previous_filtered_ref < 0))) {
                _msr_632_671_ph_diff5__zc_flag_ref = 1;
            }
            else {
                _msr_632_671_ph_diff5__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _msr_632_671_ph_diff5__n_out_size; tmp1 += 1) {
            _msr_632_671_ph_diff5__sample_cnt_in += 1;
            _msr_632_671_ph_diff5__previous_filtered_in = _msr_632_671_ph_diff5__filtered_in;
            _msr_632_671_ph_diff5__filtered_in = ((_msr_632_671_ph_diff5__previous_filtered_in * _msr_632_671_ph_diff5__n_one_minus_alpha[0]) + (_msr_632_671_i1_ia1__out * _msr_632_671_ph_diff5__n_alpha[0]));
            if((_msr_632_671_ph_diff5__sample_cnt_in >= _msr_632_671_ph_diff5__n_timeout[0])) {
                _msr_632_671_ph_diff5__zc_flag_in[0] = 0;
                _msr_632_671_ph_diff5__no_zc_flag_in[0] = 1;
                _msr_632_671_ph_diff5__sample_cnt_in = 0;
                _msr_632_671_ph_diff5__previous_correction_in = 0;
                _msr_632_671_ph_diff5__phase_state = 0;
            }
            else {
                if(((_msr_632_671_ph_diff5__filtered_in >= 0) && (_msr_632_671_ph_diff5__previous_filtered_in < 0))) {
                    _msr_632_671_ph_diff5__zc_flag_in[0] = 1;
                    _msr_632_671_ph_diff5__no_zc_flag_in[0] = 0;
                }
                else {
                    _msr_632_671_ph_diff5__zc_flag_in[0] = 0;
                }
            }
        }
        if(_msr_632_671_ph_diff5__zc_flag_ref) {
            _msr_632_671_ph_diff5__correction_ref = ((- _msr_632_671_ph_diff5__previous_filtered_ref) / ((_msr_632_671_ph_diff5__filtered_ref - _msr_632_671_ph_diff5__previous_filtered_ref)));
            _msr_632_671_ph_diff5__sample_cnt_ref += ((_msr_632_671_ph_diff5__correction_ref - _msr_632_671_ph_diff5__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _msr_632_671_ph_diff5__n_out_size; tmp2 += 1) {
                if((fabs(_msr_632_671_ph_diff5__sample_cnt_ref) > 1e-06)) {
                    if((!_msr_632_671_ph_diff5__no_zc_flag_in[0])) {
                        _msr_632_671_ph_diff5__phase_state = ((360 * (((_msr_632_671_ph_diff5__sample_cnt_in + _msr_632_671_ph_diff5__correction_ref) - _msr_632_671_ph_diff5__previous_correction_in))) / _msr_632_671_ph_diff5__sample_cnt_ref);
                    }
                }
                if((fabs(_msr_632_671_ph_diff5__phase_state) > 360)) {
                    _msr_632_671_ph_diff5__phase_state = fmod(_msr_632_671_ph_diff5__phase_state, 360);
                }
                if((_msr_632_671_ph_diff5__phase_state < (- 180))) {
                    _msr_632_671_ph_diff5__phase_state += 360;
                }
                if((_msr_632_671_ph_diff5__phase_state > 180)) {
                    _msr_632_671_ph_diff5__phase_state -= 360;
                }
            }
            _msr_632_671_ph_diff5__sample_cnt_ref = 0;
            _msr_632_671_ph_diff5__previous_correction_ref = _msr_632_671_ph_diff5__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _msr_632_671_ph_diff5__n_out_size; tmp3 += 1) {
            if(_msr_632_671_ph_diff5__zc_flag_in[0]) {
                _msr_632_671_ph_diff5__correction_in = ((- _msr_632_671_ph_diff5__previous_filtered_in) / ((_msr_632_671_ph_diff5__filtered_in - _msr_632_671_ph_diff5__previous_filtered_in)));
                _msr_632_671_ph_diff5__sample_cnt_in = 0;
                _msr_632_671_ph_diff5__previous_correction_in = _msr_632_671_ph_diff5__correction_in;
            }
        }
    }
    // Generated from the component: MSR 632-671.ph_diff6
    {
        _msr_632_671_ph_diff6__sample_cnt_ref += 1.0;
        _msr_632_671_ph_diff6__previous_filtered_ref = _msr_632_671_ph_diff6__filtered_ref;
        _msr_632_671_ph_diff6__filtered_ref = ((_msr_632_671_ph_diff6__previous_filtered_ref * _msr_632_671_ph_diff6__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _msr_632_671_ph_diff6__n_alpha[0]));
        if((_msr_632_671_ph_diff6__sample_cnt_ref >= _msr_632_671_ph_diff6__n_timeout[0])) {
            _msr_632_671_ph_diff6__zc_flag_ref = 0;
            _msr_632_671_ph_diff6__sample_cnt_ref = 0;
            _msr_632_671_ph_diff6__previous_correction_ref = 0;
            _msr_632_671_ph_diff6__phase_state = 0;
        }
        else {
            if(((_msr_632_671_ph_diff6__filtered_ref >= 0) && (_msr_632_671_ph_diff6__previous_filtered_ref < 0))) {
                _msr_632_671_ph_diff6__zc_flag_ref = 1;
            }
            else {
                _msr_632_671_ph_diff6__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _msr_632_671_ph_diff6__n_out_size; tmp1 += 1) {
            _msr_632_671_ph_diff6__sample_cnt_in += 1;
            _msr_632_671_ph_diff6__previous_filtered_in = _msr_632_671_ph_diff6__filtered_in;
            _msr_632_671_ph_diff6__filtered_in = ((_msr_632_671_ph_diff6__previous_filtered_in * _msr_632_671_ph_diff6__n_one_minus_alpha[0]) + (_msr_632_671_i2_ia1__out * _msr_632_671_ph_diff6__n_alpha[0]));
            if((_msr_632_671_ph_diff6__sample_cnt_in >= _msr_632_671_ph_diff6__n_timeout[0])) {
                _msr_632_671_ph_diff6__zc_flag_in[0] = 0;
                _msr_632_671_ph_diff6__no_zc_flag_in[0] = 1;
                _msr_632_671_ph_diff6__sample_cnt_in = 0;
                _msr_632_671_ph_diff6__previous_correction_in = 0;
                _msr_632_671_ph_diff6__phase_state = 0;
            }
            else {
                if(((_msr_632_671_ph_diff6__filtered_in >= 0) && (_msr_632_671_ph_diff6__previous_filtered_in < 0))) {
                    _msr_632_671_ph_diff6__zc_flag_in[0] = 1;
                    _msr_632_671_ph_diff6__no_zc_flag_in[0] = 0;
                }
                else {
                    _msr_632_671_ph_diff6__zc_flag_in[0] = 0;
                }
            }
        }
        if(_msr_632_671_ph_diff6__zc_flag_ref) {
            _msr_632_671_ph_diff6__correction_ref = ((- _msr_632_671_ph_diff6__previous_filtered_ref) / ((_msr_632_671_ph_diff6__filtered_ref - _msr_632_671_ph_diff6__previous_filtered_ref)));
            _msr_632_671_ph_diff6__sample_cnt_ref += ((_msr_632_671_ph_diff6__correction_ref - _msr_632_671_ph_diff6__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _msr_632_671_ph_diff6__n_out_size; tmp2 += 1) {
                if((fabs(_msr_632_671_ph_diff6__sample_cnt_ref) > 1e-06)) {
                    if((!_msr_632_671_ph_diff6__no_zc_flag_in[0])) {
                        _msr_632_671_ph_diff6__phase_state = ((360 * (((_msr_632_671_ph_diff6__sample_cnt_in + _msr_632_671_ph_diff6__correction_ref) - _msr_632_671_ph_diff6__previous_correction_in))) / _msr_632_671_ph_diff6__sample_cnt_ref);
                    }
                }
                if((fabs(_msr_632_671_ph_diff6__phase_state) > 360)) {
                    _msr_632_671_ph_diff6__phase_state = fmod(_msr_632_671_ph_diff6__phase_state, 360);
                }
                if((_msr_632_671_ph_diff6__phase_state < (- 180))) {
                    _msr_632_671_ph_diff6__phase_state += 360;
                }
                if((_msr_632_671_ph_diff6__phase_state > 180)) {
                    _msr_632_671_ph_diff6__phase_state -= 360;
                }
            }
            _msr_632_671_ph_diff6__sample_cnt_ref = 0;
            _msr_632_671_ph_diff6__previous_correction_ref = _msr_632_671_ph_diff6__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _msr_632_671_ph_diff6__n_out_size; tmp3 += 1) {
            if(_msr_632_671_ph_diff6__zc_flag_in[0]) {
                _msr_632_671_ph_diff6__correction_in = ((- _msr_632_671_ph_diff6__previous_filtered_in) / ((_msr_632_671_ph_diff6__filtered_in - _msr_632_671_ph_diff6__previous_filtered_in)));
                _msr_632_671_ph_diff6__sample_cnt_in = 0;
                _msr_632_671_ph_diff6__previous_correction_in = _msr_632_671_ph_diff6__correction_in;
            }
        }
    }
    // Generated from the component: Node 611.I3.Ia1
    // Generated from the component: Node 611.ph_diff4
    {
        _node_611_ph_diff4__sample_cnt_ref += 1.0;
        _node_611_ph_diff4__previous_filtered_ref = _node_611_ph_diff4__filtered_ref;
        _node_611_ph_diff4__filtered_ref = ((_node_611_ph_diff4__previous_filtered_ref * _node_611_ph_diff4__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_611_ph_diff4__n_alpha[0]));
        if((_node_611_ph_diff4__sample_cnt_ref >= _node_611_ph_diff4__n_timeout[0])) {
            _node_611_ph_diff4__zc_flag_ref = 0;
            _node_611_ph_diff4__sample_cnt_ref = 0;
            _node_611_ph_diff4__previous_correction_ref = 0;
            _node_611_ph_diff4__phase_state = 0;
        }
        else {
            if(((_node_611_ph_diff4__filtered_ref >= 0) && (_node_611_ph_diff4__previous_filtered_ref < 0))) {
                _node_611_ph_diff4__zc_flag_ref = 1;
            }
            else {
                _node_611_ph_diff4__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_611_ph_diff4__n_out_size; tmp1 += 1) {
            _node_611_ph_diff4__sample_cnt_in += 1;
            _node_611_ph_diff4__previous_filtered_in = _node_611_ph_diff4__filtered_in;
            _node_611_ph_diff4__filtered_in = ((_node_611_ph_diff4__previous_filtered_in * _node_611_ph_diff4__n_one_minus_alpha[0]) + (_node_611_i3_ia1__out * _node_611_ph_diff4__n_alpha[0]));
            if((_node_611_ph_diff4__sample_cnt_in >= _node_611_ph_diff4__n_timeout[0])) {
                _node_611_ph_diff4__zc_flag_in[0] = 0;
                _node_611_ph_diff4__no_zc_flag_in[0] = 1;
                _node_611_ph_diff4__sample_cnt_in = 0;
                _node_611_ph_diff4__previous_correction_in = 0;
                _node_611_ph_diff4__phase_state = 0;
            }
            else {
                if(((_node_611_ph_diff4__filtered_in >= 0) && (_node_611_ph_diff4__previous_filtered_in < 0))) {
                    _node_611_ph_diff4__zc_flag_in[0] = 1;
                    _node_611_ph_diff4__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_611_ph_diff4__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_611_ph_diff4__zc_flag_ref) {
            _node_611_ph_diff4__correction_ref = ((- _node_611_ph_diff4__previous_filtered_ref) / ((_node_611_ph_diff4__filtered_ref - _node_611_ph_diff4__previous_filtered_ref)));
            _node_611_ph_diff4__sample_cnt_ref += ((_node_611_ph_diff4__correction_ref - _node_611_ph_diff4__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_611_ph_diff4__n_out_size; tmp2 += 1) {
                if((fabs(_node_611_ph_diff4__sample_cnt_ref) > 1e-06)) {
                    if((!_node_611_ph_diff4__no_zc_flag_in[0])) {
                        _node_611_ph_diff4__phase_state = ((360 * (((_node_611_ph_diff4__sample_cnt_in + _node_611_ph_diff4__correction_ref) - _node_611_ph_diff4__previous_correction_in))) / _node_611_ph_diff4__sample_cnt_ref);
                    }
                }
                if((fabs(_node_611_ph_diff4__phase_state) > 360)) {
                    _node_611_ph_diff4__phase_state = fmod(_node_611_ph_diff4__phase_state, 360);
                }
                if((_node_611_ph_diff4__phase_state < (- 180))) {
                    _node_611_ph_diff4__phase_state += 360;
                }
                if((_node_611_ph_diff4__phase_state > 180)) {
                    _node_611_ph_diff4__phase_state -= 360;
                }
            }
            _node_611_ph_diff4__sample_cnt_ref = 0;
            _node_611_ph_diff4__previous_correction_ref = _node_611_ph_diff4__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_611_ph_diff4__n_out_size; tmp3 += 1) {
            if(_node_611_ph_diff4__zc_flag_in[0]) {
                _node_611_ph_diff4__correction_in = ((- _node_611_ph_diff4__previous_filtered_in) / ((_node_611_ph_diff4__filtered_in - _node_611_ph_diff4__previous_filtered_in)));
                _node_611_ph_diff4__sample_cnt_in = 0;
                _node_611_ph_diff4__previous_correction_in = _node_611_ph_diff4__correction_in;
            }
        }
    }
    // Generated from the component: Node 632.CPU Transition4.Output
    // Generated from the component: Node 632.CPU Transition5.Output
    // Generated from the component: Node 632.CPU Transition6.Output
    // Generated from the component: Node 632.I1.Ia1
    // Generated from the component: Node 632.I2.Ia1
    // Generated from the component: Node 632.I3.Ia1
    // Generated from the component: Node 632.ph_diff4
    {
        _node_632_ph_diff4__sample_cnt_ref += 1.0;
        _node_632_ph_diff4__previous_filtered_ref = _node_632_ph_diff4__filtered_ref;
        _node_632_ph_diff4__filtered_ref = ((_node_632_ph_diff4__previous_filtered_ref * _node_632_ph_diff4__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_632_ph_diff4__n_alpha[0]));
        if((_node_632_ph_diff4__sample_cnt_ref >= _node_632_ph_diff4__n_timeout[0])) {
            _node_632_ph_diff4__zc_flag_ref = 0;
            _node_632_ph_diff4__sample_cnt_ref = 0;
            _node_632_ph_diff4__previous_correction_ref = 0;
            _node_632_ph_diff4__phase_state = 0;
        }
        else {
            if(((_node_632_ph_diff4__filtered_ref >= 0) && (_node_632_ph_diff4__previous_filtered_ref < 0))) {
                _node_632_ph_diff4__zc_flag_ref = 1;
            }
            else {
                _node_632_ph_diff4__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_632_ph_diff4__n_out_size; tmp1 += 1) {
            _node_632_ph_diff4__sample_cnt_in += 1;
            _node_632_ph_diff4__previous_filtered_in = _node_632_ph_diff4__filtered_in;
            _node_632_ph_diff4__filtered_in = ((_node_632_ph_diff4__previous_filtered_in * _node_632_ph_diff4__n_one_minus_alpha[0]) + (_node_632_i3_ia1__out * _node_632_ph_diff4__n_alpha[0]));
            if((_node_632_ph_diff4__sample_cnt_in >= _node_632_ph_diff4__n_timeout[0])) {
                _node_632_ph_diff4__zc_flag_in[0] = 0;
                _node_632_ph_diff4__no_zc_flag_in[0] = 1;
                _node_632_ph_diff4__sample_cnt_in = 0;
                _node_632_ph_diff4__previous_correction_in = 0;
                _node_632_ph_diff4__phase_state = 0;
            }
            else {
                if(((_node_632_ph_diff4__filtered_in >= 0) && (_node_632_ph_diff4__previous_filtered_in < 0))) {
                    _node_632_ph_diff4__zc_flag_in[0] = 1;
                    _node_632_ph_diff4__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_632_ph_diff4__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_632_ph_diff4__zc_flag_ref) {
            _node_632_ph_diff4__correction_ref = ((- _node_632_ph_diff4__previous_filtered_ref) / ((_node_632_ph_diff4__filtered_ref - _node_632_ph_diff4__previous_filtered_ref)));
            _node_632_ph_diff4__sample_cnt_ref += ((_node_632_ph_diff4__correction_ref - _node_632_ph_diff4__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_632_ph_diff4__n_out_size; tmp2 += 1) {
                if((fabs(_node_632_ph_diff4__sample_cnt_ref) > 1e-06)) {
                    if((!_node_632_ph_diff4__no_zc_flag_in[0])) {
                        _node_632_ph_diff4__phase_state = ((360 * (((_node_632_ph_diff4__sample_cnt_in + _node_632_ph_diff4__correction_ref) - _node_632_ph_diff4__previous_correction_in))) / _node_632_ph_diff4__sample_cnt_ref);
                    }
                }
                if((fabs(_node_632_ph_diff4__phase_state) > 360)) {
                    _node_632_ph_diff4__phase_state = fmod(_node_632_ph_diff4__phase_state, 360);
                }
                if((_node_632_ph_diff4__phase_state < (- 180))) {
                    _node_632_ph_diff4__phase_state += 360;
                }
                if((_node_632_ph_diff4__phase_state > 180)) {
                    _node_632_ph_diff4__phase_state -= 360;
                }
            }
            _node_632_ph_diff4__sample_cnt_ref = 0;
            _node_632_ph_diff4__previous_correction_ref = _node_632_ph_diff4__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_632_ph_diff4__n_out_size; tmp3 += 1) {
            if(_node_632_ph_diff4__zc_flag_in[0]) {
                _node_632_ph_diff4__correction_in = ((- _node_632_ph_diff4__previous_filtered_in) / ((_node_632_ph_diff4__filtered_in - _node_632_ph_diff4__previous_filtered_in)));
                _node_632_ph_diff4__sample_cnt_in = 0;
                _node_632_ph_diff4__previous_correction_in = _node_632_ph_diff4__correction_in;
            }
        }
    }
    // Generated from the component: Node 632.ph_diff5
    {
        _node_632_ph_diff5__sample_cnt_ref += 1.0;
        _node_632_ph_diff5__previous_filtered_ref = _node_632_ph_diff5__filtered_ref;
        _node_632_ph_diff5__filtered_ref = ((_node_632_ph_diff5__previous_filtered_ref * _node_632_ph_diff5__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_632_ph_diff5__n_alpha[0]));
        if((_node_632_ph_diff5__sample_cnt_ref >= _node_632_ph_diff5__n_timeout[0])) {
            _node_632_ph_diff5__zc_flag_ref = 0;
            _node_632_ph_diff5__sample_cnt_ref = 0;
            _node_632_ph_diff5__previous_correction_ref = 0;
            _node_632_ph_diff5__phase_state = 0;
        }
        else {
            if(((_node_632_ph_diff5__filtered_ref >= 0) && (_node_632_ph_diff5__previous_filtered_ref < 0))) {
                _node_632_ph_diff5__zc_flag_ref = 1;
            }
            else {
                _node_632_ph_diff5__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_632_ph_diff5__n_out_size; tmp1 += 1) {
            _node_632_ph_diff5__sample_cnt_in += 1;
            _node_632_ph_diff5__previous_filtered_in = _node_632_ph_diff5__filtered_in;
            _node_632_ph_diff5__filtered_in = ((_node_632_ph_diff5__previous_filtered_in * _node_632_ph_diff5__n_one_minus_alpha[0]) + (_node_632_i1_ia1__out * _node_632_ph_diff5__n_alpha[0]));
            if((_node_632_ph_diff5__sample_cnt_in >= _node_632_ph_diff5__n_timeout[0])) {
                _node_632_ph_diff5__zc_flag_in[0] = 0;
                _node_632_ph_diff5__no_zc_flag_in[0] = 1;
                _node_632_ph_diff5__sample_cnt_in = 0;
                _node_632_ph_diff5__previous_correction_in = 0;
                _node_632_ph_diff5__phase_state = 0;
            }
            else {
                if(((_node_632_ph_diff5__filtered_in >= 0) && (_node_632_ph_diff5__previous_filtered_in < 0))) {
                    _node_632_ph_diff5__zc_flag_in[0] = 1;
                    _node_632_ph_diff5__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_632_ph_diff5__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_632_ph_diff5__zc_flag_ref) {
            _node_632_ph_diff5__correction_ref = ((- _node_632_ph_diff5__previous_filtered_ref) / ((_node_632_ph_diff5__filtered_ref - _node_632_ph_diff5__previous_filtered_ref)));
            _node_632_ph_diff5__sample_cnt_ref += ((_node_632_ph_diff5__correction_ref - _node_632_ph_diff5__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_632_ph_diff5__n_out_size; tmp2 += 1) {
                if((fabs(_node_632_ph_diff5__sample_cnt_ref) > 1e-06)) {
                    if((!_node_632_ph_diff5__no_zc_flag_in[0])) {
                        _node_632_ph_diff5__phase_state = ((360 * (((_node_632_ph_diff5__sample_cnt_in + _node_632_ph_diff5__correction_ref) - _node_632_ph_diff5__previous_correction_in))) / _node_632_ph_diff5__sample_cnt_ref);
                    }
                }
                if((fabs(_node_632_ph_diff5__phase_state) > 360)) {
                    _node_632_ph_diff5__phase_state = fmod(_node_632_ph_diff5__phase_state, 360);
                }
                if((_node_632_ph_diff5__phase_state < (- 180))) {
                    _node_632_ph_diff5__phase_state += 360;
                }
                if((_node_632_ph_diff5__phase_state > 180)) {
                    _node_632_ph_diff5__phase_state -= 360;
                }
            }
            _node_632_ph_diff5__sample_cnt_ref = 0;
            _node_632_ph_diff5__previous_correction_ref = _node_632_ph_diff5__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_632_ph_diff5__n_out_size; tmp3 += 1) {
            if(_node_632_ph_diff5__zc_flag_in[0]) {
                _node_632_ph_diff5__correction_in = ((- _node_632_ph_diff5__previous_filtered_in) / ((_node_632_ph_diff5__filtered_in - _node_632_ph_diff5__previous_filtered_in)));
                _node_632_ph_diff5__sample_cnt_in = 0;
                _node_632_ph_diff5__previous_correction_in = _node_632_ph_diff5__correction_in;
            }
        }
    }
    // Generated from the component: Node 632.ph_diff6
    {
        _node_632_ph_diff6__sample_cnt_ref += 1.0;
        _node_632_ph_diff6__previous_filtered_ref = _node_632_ph_diff6__filtered_ref;
        _node_632_ph_diff6__filtered_ref = ((_node_632_ph_diff6__previous_filtered_ref * _node_632_ph_diff6__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_632_ph_diff6__n_alpha[0]));
        if((_node_632_ph_diff6__sample_cnt_ref >= _node_632_ph_diff6__n_timeout[0])) {
            _node_632_ph_diff6__zc_flag_ref = 0;
            _node_632_ph_diff6__sample_cnt_ref = 0;
            _node_632_ph_diff6__previous_correction_ref = 0;
            _node_632_ph_diff6__phase_state = 0;
        }
        else {
            if(((_node_632_ph_diff6__filtered_ref >= 0) && (_node_632_ph_diff6__previous_filtered_ref < 0))) {
                _node_632_ph_diff6__zc_flag_ref = 1;
            }
            else {
                _node_632_ph_diff6__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_632_ph_diff6__n_out_size; tmp1 += 1) {
            _node_632_ph_diff6__sample_cnt_in += 1;
            _node_632_ph_diff6__previous_filtered_in = _node_632_ph_diff6__filtered_in;
            _node_632_ph_diff6__filtered_in = ((_node_632_ph_diff6__previous_filtered_in * _node_632_ph_diff6__n_one_minus_alpha[0]) + (_node_632_i2_ia1__out * _node_632_ph_diff6__n_alpha[0]));
            if((_node_632_ph_diff6__sample_cnt_in >= _node_632_ph_diff6__n_timeout[0])) {
                _node_632_ph_diff6__zc_flag_in[0] = 0;
                _node_632_ph_diff6__no_zc_flag_in[0] = 1;
                _node_632_ph_diff6__sample_cnt_in = 0;
                _node_632_ph_diff6__previous_correction_in = 0;
                _node_632_ph_diff6__phase_state = 0;
            }
            else {
                if(((_node_632_ph_diff6__filtered_in >= 0) && (_node_632_ph_diff6__previous_filtered_in < 0))) {
                    _node_632_ph_diff6__zc_flag_in[0] = 1;
                    _node_632_ph_diff6__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_632_ph_diff6__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_632_ph_diff6__zc_flag_ref) {
            _node_632_ph_diff6__correction_ref = ((- _node_632_ph_diff6__previous_filtered_ref) / ((_node_632_ph_diff6__filtered_ref - _node_632_ph_diff6__previous_filtered_ref)));
            _node_632_ph_diff6__sample_cnt_ref += ((_node_632_ph_diff6__correction_ref - _node_632_ph_diff6__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_632_ph_diff6__n_out_size; tmp2 += 1) {
                if((fabs(_node_632_ph_diff6__sample_cnt_ref) > 1e-06)) {
                    if((!_node_632_ph_diff6__no_zc_flag_in[0])) {
                        _node_632_ph_diff6__phase_state = ((360 * (((_node_632_ph_diff6__sample_cnt_in + _node_632_ph_diff6__correction_ref) - _node_632_ph_diff6__previous_correction_in))) / _node_632_ph_diff6__sample_cnt_ref);
                    }
                }
                if((fabs(_node_632_ph_diff6__phase_state) > 360)) {
                    _node_632_ph_diff6__phase_state = fmod(_node_632_ph_diff6__phase_state, 360);
                }
                if((_node_632_ph_diff6__phase_state < (- 180))) {
                    _node_632_ph_diff6__phase_state += 360;
                }
                if((_node_632_ph_diff6__phase_state > 180)) {
                    _node_632_ph_diff6__phase_state -= 360;
                }
            }
            _node_632_ph_diff6__sample_cnt_ref = 0;
            _node_632_ph_diff6__previous_correction_ref = _node_632_ph_diff6__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_632_ph_diff6__n_out_size; tmp3 += 1) {
            if(_node_632_ph_diff6__zc_flag_in[0]) {
                _node_632_ph_diff6__correction_in = ((- _node_632_ph_diff6__previous_filtered_in) / ((_node_632_ph_diff6__filtered_in - _node_632_ph_diff6__previous_filtered_in)));
                _node_632_ph_diff6__sample_cnt_in = 0;
                _node_632_ph_diff6__previous_correction_in = _node_632_ph_diff6__correction_in;
            }
        }
    }
    // Generated from the component: Node 633.I1.Ia1
    // Generated from the component: Node 633.I2.Ia1
    // Generated from the component: Node 633.I3.Ia1
    // Generated from the component: Node 633.ph_diff4
    {
        _node_633_ph_diff4__sample_cnt_ref += 1.0;
        _node_633_ph_diff4__previous_filtered_ref = _node_633_ph_diff4__filtered_ref;
        _node_633_ph_diff4__filtered_ref = ((_node_633_ph_diff4__previous_filtered_ref * _node_633_ph_diff4__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_633_ph_diff4__n_alpha[0]));
        if((_node_633_ph_diff4__sample_cnt_ref >= _node_633_ph_diff4__n_timeout[0])) {
            _node_633_ph_diff4__zc_flag_ref = 0;
            _node_633_ph_diff4__sample_cnt_ref = 0;
            _node_633_ph_diff4__previous_correction_ref = 0;
            _node_633_ph_diff4__phase_state = 0;
        }
        else {
            if(((_node_633_ph_diff4__filtered_ref >= 0) && (_node_633_ph_diff4__previous_filtered_ref < 0))) {
                _node_633_ph_diff4__zc_flag_ref = 1;
            }
            else {
                _node_633_ph_diff4__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_633_ph_diff4__n_out_size; tmp1 += 1) {
            _node_633_ph_diff4__sample_cnt_in += 1;
            _node_633_ph_diff4__previous_filtered_in = _node_633_ph_diff4__filtered_in;
            _node_633_ph_diff4__filtered_in = ((_node_633_ph_diff4__previous_filtered_in * _node_633_ph_diff4__n_one_minus_alpha[0]) + (_node_633_i3_ia1__out * _node_633_ph_diff4__n_alpha[0]));
            if((_node_633_ph_diff4__sample_cnt_in >= _node_633_ph_diff4__n_timeout[0])) {
                _node_633_ph_diff4__zc_flag_in[0] = 0;
                _node_633_ph_diff4__no_zc_flag_in[0] = 1;
                _node_633_ph_diff4__sample_cnt_in = 0;
                _node_633_ph_diff4__previous_correction_in = 0;
                _node_633_ph_diff4__phase_state = 0;
            }
            else {
                if(((_node_633_ph_diff4__filtered_in >= 0) && (_node_633_ph_diff4__previous_filtered_in < 0))) {
                    _node_633_ph_diff4__zc_flag_in[0] = 1;
                    _node_633_ph_diff4__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_633_ph_diff4__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_633_ph_diff4__zc_flag_ref) {
            _node_633_ph_diff4__correction_ref = ((- _node_633_ph_diff4__previous_filtered_ref) / ((_node_633_ph_diff4__filtered_ref - _node_633_ph_diff4__previous_filtered_ref)));
            _node_633_ph_diff4__sample_cnt_ref += ((_node_633_ph_diff4__correction_ref - _node_633_ph_diff4__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_633_ph_diff4__n_out_size; tmp2 += 1) {
                if((fabs(_node_633_ph_diff4__sample_cnt_ref) > 1e-06)) {
                    if((!_node_633_ph_diff4__no_zc_flag_in[0])) {
                        _node_633_ph_diff4__phase_state = ((360 * (((_node_633_ph_diff4__sample_cnt_in + _node_633_ph_diff4__correction_ref) - _node_633_ph_diff4__previous_correction_in))) / _node_633_ph_diff4__sample_cnt_ref);
                    }
                }
                if((fabs(_node_633_ph_diff4__phase_state) > 360)) {
                    _node_633_ph_diff4__phase_state = fmod(_node_633_ph_diff4__phase_state, 360);
                }
                if((_node_633_ph_diff4__phase_state < (- 180))) {
                    _node_633_ph_diff4__phase_state += 360;
                }
                if((_node_633_ph_diff4__phase_state > 180)) {
                    _node_633_ph_diff4__phase_state -= 360;
                }
            }
            _node_633_ph_diff4__sample_cnt_ref = 0;
            _node_633_ph_diff4__previous_correction_ref = _node_633_ph_diff4__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_633_ph_diff4__n_out_size; tmp3 += 1) {
            if(_node_633_ph_diff4__zc_flag_in[0]) {
                _node_633_ph_diff4__correction_in = ((- _node_633_ph_diff4__previous_filtered_in) / ((_node_633_ph_diff4__filtered_in - _node_633_ph_diff4__previous_filtered_in)));
                _node_633_ph_diff4__sample_cnt_in = 0;
                _node_633_ph_diff4__previous_correction_in = _node_633_ph_diff4__correction_in;
            }
        }
    }
    // Generated from the component: Node 633.ph_diff5
    {
        _node_633_ph_diff5__sample_cnt_ref += 1.0;
        _node_633_ph_diff5__previous_filtered_ref = _node_633_ph_diff5__filtered_ref;
        _node_633_ph_diff5__filtered_ref = ((_node_633_ph_diff5__previous_filtered_ref * _node_633_ph_diff5__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_633_ph_diff5__n_alpha[0]));
        if((_node_633_ph_diff5__sample_cnt_ref >= _node_633_ph_diff5__n_timeout[0])) {
            _node_633_ph_diff5__zc_flag_ref = 0;
            _node_633_ph_diff5__sample_cnt_ref = 0;
            _node_633_ph_diff5__previous_correction_ref = 0;
            _node_633_ph_diff5__phase_state = 0;
        }
        else {
            if(((_node_633_ph_diff5__filtered_ref >= 0) && (_node_633_ph_diff5__previous_filtered_ref < 0))) {
                _node_633_ph_diff5__zc_flag_ref = 1;
            }
            else {
                _node_633_ph_diff5__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_633_ph_diff5__n_out_size; tmp1 += 1) {
            _node_633_ph_diff5__sample_cnt_in += 1;
            _node_633_ph_diff5__previous_filtered_in = _node_633_ph_diff5__filtered_in;
            _node_633_ph_diff5__filtered_in = ((_node_633_ph_diff5__previous_filtered_in * _node_633_ph_diff5__n_one_minus_alpha[0]) + (_node_633_i1_ia1__out * _node_633_ph_diff5__n_alpha[0]));
            if((_node_633_ph_diff5__sample_cnt_in >= _node_633_ph_diff5__n_timeout[0])) {
                _node_633_ph_diff5__zc_flag_in[0] = 0;
                _node_633_ph_diff5__no_zc_flag_in[0] = 1;
                _node_633_ph_diff5__sample_cnt_in = 0;
                _node_633_ph_diff5__previous_correction_in = 0;
                _node_633_ph_diff5__phase_state = 0;
            }
            else {
                if(((_node_633_ph_diff5__filtered_in >= 0) && (_node_633_ph_diff5__previous_filtered_in < 0))) {
                    _node_633_ph_diff5__zc_flag_in[0] = 1;
                    _node_633_ph_diff5__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_633_ph_diff5__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_633_ph_diff5__zc_flag_ref) {
            _node_633_ph_diff5__correction_ref = ((- _node_633_ph_diff5__previous_filtered_ref) / ((_node_633_ph_diff5__filtered_ref - _node_633_ph_diff5__previous_filtered_ref)));
            _node_633_ph_diff5__sample_cnt_ref += ((_node_633_ph_diff5__correction_ref - _node_633_ph_diff5__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_633_ph_diff5__n_out_size; tmp2 += 1) {
                if((fabs(_node_633_ph_diff5__sample_cnt_ref) > 1e-06)) {
                    if((!_node_633_ph_diff5__no_zc_flag_in[0])) {
                        _node_633_ph_diff5__phase_state = ((360 * (((_node_633_ph_diff5__sample_cnt_in + _node_633_ph_diff5__correction_ref) - _node_633_ph_diff5__previous_correction_in))) / _node_633_ph_diff5__sample_cnt_ref);
                    }
                }
                if((fabs(_node_633_ph_diff5__phase_state) > 360)) {
                    _node_633_ph_diff5__phase_state = fmod(_node_633_ph_diff5__phase_state, 360);
                }
                if((_node_633_ph_diff5__phase_state < (- 180))) {
                    _node_633_ph_diff5__phase_state += 360;
                }
                if((_node_633_ph_diff5__phase_state > 180)) {
                    _node_633_ph_diff5__phase_state -= 360;
                }
            }
            _node_633_ph_diff5__sample_cnt_ref = 0;
            _node_633_ph_diff5__previous_correction_ref = _node_633_ph_diff5__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_633_ph_diff5__n_out_size; tmp3 += 1) {
            if(_node_633_ph_diff5__zc_flag_in[0]) {
                _node_633_ph_diff5__correction_in = ((- _node_633_ph_diff5__previous_filtered_in) / ((_node_633_ph_diff5__filtered_in - _node_633_ph_diff5__previous_filtered_in)));
                _node_633_ph_diff5__sample_cnt_in = 0;
                _node_633_ph_diff5__previous_correction_in = _node_633_ph_diff5__correction_in;
            }
        }
    }
    // Generated from the component: Node 633.ph_diff6
    {
        _node_633_ph_diff6__sample_cnt_ref += 1.0;
        _node_633_ph_diff6__previous_filtered_ref = _node_633_ph_diff6__filtered_ref;
        _node_633_ph_diff6__filtered_ref = ((_node_633_ph_diff6__previous_filtered_ref * _node_633_ph_diff6__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_633_ph_diff6__n_alpha[0]));
        if((_node_633_ph_diff6__sample_cnt_ref >= _node_633_ph_diff6__n_timeout[0])) {
            _node_633_ph_diff6__zc_flag_ref = 0;
            _node_633_ph_diff6__sample_cnt_ref = 0;
            _node_633_ph_diff6__previous_correction_ref = 0;
            _node_633_ph_diff6__phase_state = 0;
        }
        else {
            if(((_node_633_ph_diff6__filtered_ref >= 0) && (_node_633_ph_diff6__previous_filtered_ref < 0))) {
                _node_633_ph_diff6__zc_flag_ref = 1;
            }
            else {
                _node_633_ph_diff6__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_633_ph_diff6__n_out_size; tmp1 += 1) {
            _node_633_ph_diff6__sample_cnt_in += 1;
            _node_633_ph_diff6__previous_filtered_in = _node_633_ph_diff6__filtered_in;
            _node_633_ph_diff6__filtered_in = ((_node_633_ph_diff6__previous_filtered_in * _node_633_ph_diff6__n_one_minus_alpha[0]) + (_node_633_i2_ia1__out * _node_633_ph_diff6__n_alpha[0]));
            if((_node_633_ph_diff6__sample_cnt_in >= _node_633_ph_diff6__n_timeout[0])) {
                _node_633_ph_diff6__zc_flag_in[0] = 0;
                _node_633_ph_diff6__no_zc_flag_in[0] = 1;
                _node_633_ph_diff6__sample_cnt_in = 0;
                _node_633_ph_diff6__previous_correction_in = 0;
                _node_633_ph_diff6__phase_state = 0;
            }
            else {
                if(((_node_633_ph_diff6__filtered_in >= 0) && (_node_633_ph_diff6__previous_filtered_in < 0))) {
                    _node_633_ph_diff6__zc_flag_in[0] = 1;
                    _node_633_ph_diff6__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_633_ph_diff6__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_633_ph_diff6__zc_flag_ref) {
            _node_633_ph_diff6__correction_ref = ((- _node_633_ph_diff6__previous_filtered_ref) / ((_node_633_ph_diff6__filtered_ref - _node_633_ph_diff6__previous_filtered_ref)));
            _node_633_ph_diff6__sample_cnt_ref += ((_node_633_ph_diff6__correction_ref - _node_633_ph_diff6__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_633_ph_diff6__n_out_size; tmp2 += 1) {
                if((fabs(_node_633_ph_diff6__sample_cnt_ref) > 1e-06)) {
                    if((!_node_633_ph_diff6__no_zc_flag_in[0])) {
                        _node_633_ph_diff6__phase_state = ((360 * (((_node_633_ph_diff6__sample_cnt_in + _node_633_ph_diff6__correction_ref) - _node_633_ph_diff6__previous_correction_in))) / _node_633_ph_diff6__sample_cnt_ref);
                    }
                }
                if((fabs(_node_633_ph_diff6__phase_state) > 360)) {
                    _node_633_ph_diff6__phase_state = fmod(_node_633_ph_diff6__phase_state, 360);
                }
                if((_node_633_ph_diff6__phase_state < (- 180))) {
                    _node_633_ph_diff6__phase_state += 360;
                }
                if((_node_633_ph_diff6__phase_state > 180)) {
                    _node_633_ph_diff6__phase_state -= 360;
                }
            }
            _node_633_ph_diff6__sample_cnt_ref = 0;
            _node_633_ph_diff6__previous_correction_ref = _node_633_ph_diff6__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_633_ph_diff6__n_out_size; tmp3 += 1) {
            if(_node_633_ph_diff6__zc_flag_in[0]) {
                _node_633_ph_diff6__correction_in = ((- _node_633_ph_diff6__previous_filtered_in) / ((_node_633_ph_diff6__filtered_in - _node_633_ph_diff6__previous_filtered_in)));
                _node_633_ph_diff6__sample_cnt_in = 0;
                _node_633_ph_diff6__previous_correction_in = _node_633_ph_diff6__correction_in;
            }
        }
    }
    // Generated from the component: Node 634.I1.Ia1
    // Generated from the component: Node 634.I2.Ia1
    // Generated from the component: Node 634.I3.Ia1
    // Generated from the component: Node 634.ph_diff4
    {
        _node_634_ph_diff4__sample_cnt_ref += 1.0;
        _node_634_ph_diff4__previous_filtered_ref = _node_634_ph_diff4__filtered_ref;
        _node_634_ph_diff4__filtered_ref = ((_node_634_ph_diff4__previous_filtered_ref * _node_634_ph_diff4__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_634_ph_diff4__n_alpha[0]));
        if((_node_634_ph_diff4__sample_cnt_ref >= _node_634_ph_diff4__n_timeout[0])) {
            _node_634_ph_diff4__zc_flag_ref = 0;
            _node_634_ph_diff4__sample_cnt_ref = 0;
            _node_634_ph_diff4__previous_correction_ref = 0;
            _node_634_ph_diff4__phase_state = 0;
        }
        else {
            if(((_node_634_ph_diff4__filtered_ref >= 0) && (_node_634_ph_diff4__previous_filtered_ref < 0))) {
                _node_634_ph_diff4__zc_flag_ref = 1;
            }
            else {
                _node_634_ph_diff4__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_634_ph_diff4__n_out_size; tmp1 += 1) {
            _node_634_ph_diff4__sample_cnt_in += 1;
            _node_634_ph_diff4__previous_filtered_in = _node_634_ph_diff4__filtered_in;
            _node_634_ph_diff4__filtered_in = ((_node_634_ph_diff4__previous_filtered_in * _node_634_ph_diff4__n_one_minus_alpha[0]) + (_node_634_i3_ia1__out * _node_634_ph_diff4__n_alpha[0]));
            if((_node_634_ph_diff4__sample_cnt_in >= _node_634_ph_diff4__n_timeout[0])) {
                _node_634_ph_diff4__zc_flag_in[0] = 0;
                _node_634_ph_diff4__no_zc_flag_in[0] = 1;
                _node_634_ph_diff4__sample_cnt_in = 0;
                _node_634_ph_diff4__previous_correction_in = 0;
                _node_634_ph_diff4__phase_state = 0;
            }
            else {
                if(((_node_634_ph_diff4__filtered_in >= 0) && (_node_634_ph_diff4__previous_filtered_in < 0))) {
                    _node_634_ph_diff4__zc_flag_in[0] = 1;
                    _node_634_ph_diff4__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_634_ph_diff4__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_634_ph_diff4__zc_flag_ref) {
            _node_634_ph_diff4__correction_ref = ((- _node_634_ph_diff4__previous_filtered_ref) / ((_node_634_ph_diff4__filtered_ref - _node_634_ph_diff4__previous_filtered_ref)));
            _node_634_ph_diff4__sample_cnt_ref += ((_node_634_ph_diff4__correction_ref - _node_634_ph_diff4__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_634_ph_diff4__n_out_size; tmp2 += 1) {
                if((fabs(_node_634_ph_diff4__sample_cnt_ref) > 1e-06)) {
                    if((!_node_634_ph_diff4__no_zc_flag_in[0])) {
                        _node_634_ph_diff4__phase_state = ((360 * (((_node_634_ph_diff4__sample_cnt_in + _node_634_ph_diff4__correction_ref) - _node_634_ph_diff4__previous_correction_in))) / _node_634_ph_diff4__sample_cnt_ref);
                    }
                }
                if((fabs(_node_634_ph_diff4__phase_state) > 360)) {
                    _node_634_ph_diff4__phase_state = fmod(_node_634_ph_diff4__phase_state, 360);
                }
                if((_node_634_ph_diff4__phase_state < (- 180))) {
                    _node_634_ph_diff4__phase_state += 360;
                }
                if((_node_634_ph_diff4__phase_state > 180)) {
                    _node_634_ph_diff4__phase_state -= 360;
                }
            }
            _node_634_ph_diff4__sample_cnt_ref = 0;
            _node_634_ph_diff4__previous_correction_ref = _node_634_ph_diff4__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_634_ph_diff4__n_out_size; tmp3 += 1) {
            if(_node_634_ph_diff4__zc_flag_in[0]) {
                _node_634_ph_diff4__correction_in = ((- _node_634_ph_diff4__previous_filtered_in) / ((_node_634_ph_diff4__filtered_in - _node_634_ph_diff4__previous_filtered_in)));
                _node_634_ph_diff4__sample_cnt_in = 0;
                _node_634_ph_diff4__previous_correction_in = _node_634_ph_diff4__correction_in;
            }
        }
    }
    // Generated from the component: Node 634.ph_diff5
    {
        _node_634_ph_diff5__sample_cnt_ref += 1.0;
        _node_634_ph_diff5__previous_filtered_ref = _node_634_ph_diff5__filtered_ref;
        _node_634_ph_diff5__filtered_ref = ((_node_634_ph_diff5__previous_filtered_ref * _node_634_ph_diff5__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_634_ph_diff5__n_alpha[0]));
        if((_node_634_ph_diff5__sample_cnt_ref >= _node_634_ph_diff5__n_timeout[0])) {
            _node_634_ph_diff5__zc_flag_ref = 0;
            _node_634_ph_diff5__sample_cnt_ref = 0;
            _node_634_ph_diff5__previous_correction_ref = 0;
            _node_634_ph_diff5__phase_state = 0;
        }
        else {
            if(((_node_634_ph_diff5__filtered_ref >= 0) && (_node_634_ph_diff5__previous_filtered_ref < 0))) {
                _node_634_ph_diff5__zc_flag_ref = 1;
            }
            else {
                _node_634_ph_diff5__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_634_ph_diff5__n_out_size; tmp1 += 1) {
            _node_634_ph_diff5__sample_cnt_in += 1;
            _node_634_ph_diff5__previous_filtered_in = _node_634_ph_diff5__filtered_in;
            _node_634_ph_diff5__filtered_in = ((_node_634_ph_diff5__previous_filtered_in * _node_634_ph_diff5__n_one_minus_alpha[0]) + (_node_634_i1_ia1__out * _node_634_ph_diff5__n_alpha[0]));
            if((_node_634_ph_diff5__sample_cnt_in >= _node_634_ph_diff5__n_timeout[0])) {
                _node_634_ph_diff5__zc_flag_in[0] = 0;
                _node_634_ph_diff5__no_zc_flag_in[0] = 1;
                _node_634_ph_diff5__sample_cnt_in = 0;
                _node_634_ph_diff5__previous_correction_in = 0;
                _node_634_ph_diff5__phase_state = 0;
            }
            else {
                if(((_node_634_ph_diff5__filtered_in >= 0) && (_node_634_ph_diff5__previous_filtered_in < 0))) {
                    _node_634_ph_diff5__zc_flag_in[0] = 1;
                    _node_634_ph_diff5__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_634_ph_diff5__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_634_ph_diff5__zc_flag_ref) {
            _node_634_ph_diff5__correction_ref = ((- _node_634_ph_diff5__previous_filtered_ref) / ((_node_634_ph_diff5__filtered_ref - _node_634_ph_diff5__previous_filtered_ref)));
            _node_634_ph_diff5__sample_cnt_ref += ((_node_634_ph_diff5__correction_ref - _node_634_ph_diff5__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_634_ph_diff5__n_out_size; tmp2 += 1) {
                if((fabs(_node_634_ph_diff5__sample_cnt_ref) > 1e-06)) {
                    if((!_node_634_ph_diff5__no_zc_flag_in[0])) {
                        _node_634_ph_diff5__phase_state = ((360 * (((_node_634_ph_diff5__sample_cnt_in + _node_634_ph_diff5__correction_ref) - _node_634_ph_diff5__previous_correction_in))) / _node_634_ph_diff5__sample_cnt_ref);
                    }
                }
                if((fabs(_node_634_ph_diff5__phase_state) > 360)) {
                    _node_634_ph_diff5__phase_state = fmod(_node_634_ph_diff5__phase_state, 360);
                }
                if((_node_634_ph_diff5__phase_state < (- 180))) {
                    _node_634_ph_diff5__phase_state += 360;
                }
                if((_node_634_ph_diff5__phase_state > 180)) {
                    _node_634_ph_diff5__phase_state -= 360;
                }
            }
            _node_634_ph_diff5__sample_cnt_ref = 0;
            _node_634_ph_diff5__previous_correction_ref = _node_634_ph_diff5__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_634_ph_diff5__n_out_size; tmp3 += 1) {
            if(_node_634_ph_diff5__zc_flag_in[0]) {
                _node_634_ph_diff5__correction_in = ((- _node_634_ph_diff5__previous_filtered_in) / ((_node_634_ph_diff5__filtered_in - _node_634_ph_diff5__previous_filtered_in)));
                _node_634_ph_diff5__sample_cnt_in = 0;
                _node_634_ph_diff5__previous_correction_in = _node_634_ph_diff5__correction_in;
            }
        }
    }
    // Generated from the component: Node 634.ph_diff6
    {
        _node_634_ph_diff6__sample_cnt_ref += 1.0;
        _node_634_ph_diff6__previous_filtered_ref = _node_634_ph_diff6__filtered_ref;
        _node_634_ph_diff6__filtered_ref = ((_node_634_ph_diff6__previous_filtered_ref * _node_634_ph_diff6__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_634_ph_diff6__n_alpha[0]));
        if((_node_634_ph_diff6__sample_cnt_ref >= _node_634_ph_diff6__n_timeout[0])) {
            _node_634_ph_diff6__zc_flag_ref = 0;
            _node_634_ph_diff6__sample_cnt_ref = 0;
            _node_634_ph_diff6__previous_correction_ref = 0;
            _node_634_ph_diff6__phase_state = 0;
        }
        else {
            if(((_node_634_ph_diff6__filtered_ref >= 0) && (_node_634_ph_diff6__previous_filtered_ref < 0))) {
                _node_634_ph_diff6__zc_flag_ref = 1;
            }
            else {
                _node_634_ph_diff6__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_634_ph_diff6__n_out_size; tmp1 += 1) {
            _node_634_ph_diff6__sample_cnt_in += 1;
            _node_634_ph_diff6__previous_filtered_in = _node_634_ph_diff6__filtered_in;
            _node_634_ph_diff6__filtered_in = ((_node_634_ph_diff6__previous_filtered_in * _node_634_ph_diff6__n_one_minus_alpha[0]) + (_node_634_i2_ia1__out * _node_634_ph_diff6__n_alpha[0]));
            if((_node_634_ph_diff6__sample_cnt_in >= _node_634_ph_diff6__n_timeout[0])) {
                _node_634_ph_diff6__zc_flag_in[0] = 0;
                _node_634_ph_diff6__no_zc_flag_in[0] = 1;
                _node_634_ph_diff6__sample_cnt_in = 0;
                _node_634_ph_diff6__previous_correction_in = 0;
                _node_634_ph_diff6__phase_state = 0;
            }
            else {
                if(((_node_634_ph_diff6__filtered_in >= 0) && (_node_634_ph_diff6__previous_filtered_in < 0))) {
                    _node_634_ph_diff6__zc_flag_in[0] = 1;
                    _node_634_ph_diff6__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_634_ph_diff6__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_634_ph_diff6__zc_flag_ref) {
            _node_634_ph_diff6__correction_ref = ((- _node_634_ph_diff6__previous_filtered_ref) / ((_node_634_ph_diff6__filtered_ref - _node_634_ph_diff6__previous_filtered_ref)));
            _node_634_ph_diff6__sample_cnt_ref += ((_node_634_ph_diff6__correction_ref - _node_634_ph_diff6__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_634_ph_diff6__n_out_size; tmp2 += 1) {
                if((fabs(_node_634_ph_diff6__sample_cnt_ref) > 1e-06)) {
                    if((!_node_634_ph_diff6__no_zc_flag_in[0])) {
                        _node_634_ph_diff6__phase_state = ((360 * (((_node_634_ph_diff6__sample_cnt_in + _node_634_ph_diff6__correction_ref) - _node_634_ph_diff6__previous_correction_in))) / _node_634_ph_diff6__sample_cnt_ref);
                    }
                }
                if((fabs(_node_634_ph_diff6__phase_state) > 360)) {
                    _node_634_ph_diff6__phase_state = fmod(_node_634_ph_diff6__phase_state, 360);
                }
                if((_node_634_ph_diff6__phase_state < (- 180))) {
                    _node_634_ph_diff6__phase_state += 360;
                }
                if((_node_634_ph_diff6__phase_state > 180)) {
                    _node_634_ph_diff6__phase_state -= 360;
                }
            }
            _node_634_ph_diff6__sample_cnt_ref = 0;
            _node_634_ph_diff6__previous_correction_ref = _node_634_ph_diff6__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_634_ph_diff6__n_out_size; tmp3 += 1) {
            if(_node_634_ph_diff6__zc_flag_in[0]) {
                _node_634_ph_diff6__correction_in = ((- _node_634_ph_diff6__previous_filtered_in) / ((_node_634_ph_diff6__filtered_in - _node_634_ph_diff6__previous_filtered_in)));
                _node_634_ph_diff6__sample_cnt_in = 0;
                _node_634_ph_diff6__previous_correction_in = _node_634_ph_diff6__correction_in;
            }
        }
    }
    // Generated from the component: Node 645.I2.Ia1
    // Generated from the component: Node 645.I3.Ia1
    // Generated from the component: Node 645.ph_diff4
    {
        _node_645_ph_diff4__sample_cnt_ref += 1.0;
        _node_645_ph_diff4__previous_filtered_ref = _node_645_ph_diff4__filtered_ref;
        _node_645_ph_diff4__filtered_ref = ((_node_645_ph_diff4__previous_filtered_ref * _node_645_ph_diff4__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_645_ph_diff4__n_alpha[0]));
        if((_node_645_ph_diff4__sample_cnt_ref >= _node_645_ph_diff4__n_timeout[0])) {
            _node_645_ph_diff4__zc_flag_ref = 0;
            _node_645_ph_diff4__sample_cnt_ref = 0;
            _node_645_ph_diff4__previous_correction_ref = 0;
            _node_645_ph_diff4__phase_state = 0;
        }
        else {
            if(((_node_645_ph_diff4__filtered_ref >= 0) && (_node_645_ph_diff4__previous_filtered_ref < 0))) {
                _node_645_ph_diff4__zc_flag_ref = 1;
            }
            else {
                _node_645_ph_diff4__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_645_ph_diff4__n_out_size; tmp1 += 1) {
            _node_645_ph_diff4__sample_cnt_in += 1;
            _node_645_ph_diff4__previous_filtered_in = _node_645_ph_diff4__filtered_in;
            _node_645_ph_diff4__filtered_in = ((_node_645_ph_diff4__previous_filtered_in * _node_645_ph_diff4__n_one_minus_alpha[0]) + (_node_645_i3_ia1__out * _node_645_ph_diff4__n_alpha[0]));
            if((_node_645_ph_diff4__sample_cnt_in >= _node_645_ph_diff4__n_timeout[0])) {
                _node_645_ph_diff4__zc_flag_in[0] = 0;
                _node_645_ph_diff4__no_zc_flag_in[0] = 1;
                _node_645_ph_diff4__sample_cnt_in = 0;
                _node_645_ph_diff4__previous_correction_in = 0;
                _node_645_ph_diff4__phase_state = 0;
            }
            else {
                if(((_node_645_ph_diff4__filtered_in >= 0) && (_node_645_ph_diff4__previous_filtered_in < 0))) {
                    _node_645_ph_diff4__zc_flag_in[0] = 1;
                    _node_645_ph_diff4__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_645_ph_diff4__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_645_ph_diff4__zc_flag_ref) {
            _node_645_ph_diff4__correction_ref = ((- _node_645_ph_diff4__previous_filtered_ref) / ((_node_645_ph_diff4__filtered_ref - _node_645_ph_diff4__previous_filtered_ref)));
            _node_645_ph_diff4__sample_cnt_ref += ((_node_645_ph_diff4__correction_ref - _node_645_ph_diff4__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_645_ph_diff4__n_out_size; tmp2 += 1) {
                if((fabs(_node_645_ph_diff4__sample_cnt_ref) > 1e-06)) {
                    if((!_node_645_ph_diff4__no_zc_flag_in[0])) {
                        _node_645_ph_diff4__phase_state = ((360 * (((_node_645_ph_diff4__sample_cnt_in + _node_645_ph_diff4__correction_ref) - _node_645_ph_diff4__previous_correction_in))) / _node_645_ph_diff4__sample_cnt_ref);
                    }
                }
                if((fabs(_node_645_ph_diff4__phase_state) > 360)) {
                    _node_645_ph_diff4__phase_state = fmod(_node_645_ph_diff4__phase_state, 360);
                }
                if((_node_645_ph_diff4__phase_state < (- 180))) {
                    _node_645_ph_diff4__phase_state += 360;
                }
                if((_node_645_ph_diff4__phase_state > 180)) {
                    _node_645_ph_diff4__phase_state -= 360;
                }
            }
            _node_645_ph_diff4__sample_cnt_ref = 0;
            _node_645_ph_diff4__previous_correction_ref = _node_645_ph_diff4__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_645_ph_diff4__n_out_size; tmp3 += 1) {
            if(_node_645_ph_diff4__zc_flag_in[0]) {
                _node_645_ph_diff4__correction_in = ((- _node_645_ph_diff4__previous_filtered_in) / ((_node_645_ph_diff4__filtered_in - _node_645_ph_diff4__previous_filtered_in)));
                _node_645_ph_diff4__sample_cnt_in = 0;
                _node_645_ph_diff4__previous_correction_in = _node_645_ph_diff4__correction_in;
            }
        }
    }
    // Generated from the component: Node 645.ph_diff6
    {
        _node_645_ph_diff6__sample_cnt_ref += 1.0;
        _node_645_ph_diff6__previous_filtered_ref = _node_645_ph_diff6__filtered_ref;
        _node_645_ph_diff6__filtered_ref = ((_node_645_ph_diff6__previous_filtered_ref * _node_645_ph_diff6__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_645_ph_diff6__n_alpha[0]));
        if((_node_645_ph_diff6__sample_cnt_ref >= _node_645_ph_diff6__n_timeout[0])) {
            _node_645_ph_diff6__zc_flag_ref = 0;
            _node_645_ph_diff6__sample_cnt_ref = 0;
            _node_645_ph_diff6__previous_correction_ref = 0;
            _node_645_ph_diff6__phase_state = 0;
        }
        else {
            if(((_node_645_ph_diff6__filtered_ref >= 0) && (_node_645_ph_diff6__previous_filtered_ref < 0))) {
                _node_645_ph_diff6__zc_flag_ref = 1;
            }
            else {
                _node_645_ph_diff6__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_645_ph_diff6__n_out_size; tmp1 += 1) {
            _node_645_ph_diff6__sample_cnt_in += 1;
            _node_645_ph_diff6__previous_filtered_in = _node_645_ph_diff6__filtered_in;
            _node_645_ph_diff6__filtered_in = ((_node_645_ph_diff6__previous_filtered_in * _node_645_ph_diff6__n_one_minus_alpha[0]) + (_node_645_i2_ia1__out * _node_645_ph_diff6__n_alpha[0]));
            if((_node_645_ph_diff6__sample_cnt_in >= _node_645_ph_diff6__n_timeout[0])) {
                _node_645_ph_diff6__zc_flag_in[0] = 0;
                _node_645_ph_diff6__no_zc_flag_in[0] = 1;
                _node_645_ph_diff6__sample_cnt_in = 0;
                _node_645_ph_diff6__previous_correction_in = 0;
                _node_645_ph_diff6__phase_state = 0;
            }
            else {
                if(((_node_645_ph_diff6__filtered_in >= 0) && (_node_645_ph_diff6__previous_filtered_in < 0))) {
                    _node_645_ph_diff6__zc_flag_in[0] = 1;
                    _node_645_ph_diff6__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_645_ph_diff6__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_645_ph_diff6__zc_flag_ref) {
            _node_645_ph_diff6__correction_ref = ((- _node_645_ph_diff6__previous_filtered_ref) / ((_node_645_ph_diff6__filtered_ref - _node_645_ph_diff6__previous_filtered_ref)));
            _node_645_ph_diff6__sample_cnt_ref += ((_node_645_ph_diff6__correction_ref - _node_645_ph_diff6__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_645_ph_diff6__n_out_size; tmp2 += 1) {
                if((fabs(_node_645_ph_diff6__sample_cnt_ref) > 1e-06)) {
                    if((!_node_645_ph_diff6__no_zc_flag_in[0])) {
                        _node_645_ph_diff6__phase_state = ((360 * (((_node_645_ph_diff6__sample_cnt_in + _node_645_ph_diff6__correction_ref) - _node_645_ph_diff6__previous_correction_in))) / _node_645_ph_diff6__sample_cnt_ref);
                    }
                }
                if((fabs(_node_645_ph_diff6__phase_state) > 360)) {
                    _node_645_ph_diff6__phase_state = fmod(_node_645_ph_diff6__phase_state, 360);
                }
                if((_node_645_ph_diff6__phase_state < (- 180))) {
                    _node_645_ph_diff6__phase_state += 360;
                }
                if((_node_645_ph_diff6__phase_state > 180)) {
                    _node_645_ph_diff6__phase_state -= 360;
                }
            }
            _node_645_ph_diff6__sample_cnt_ref = 0;
            _node_645_ph_diff6__previous_correction_ref = _node_645_ph_diff6__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_645_ph_diff6__n_out_size; tmp3 += 1) {
            if(_node_645_ph_diff6__zc_flag_in[0]) {
                _node_645_ph_diff6__correction_in = ((- _node_645_ph_diff6__previous_filtered_in) / ((_node_645_ph_diff6__filtered_in - _node_645_ph_diff6__previous_filtered_in)));
                _node_645_ph_diff6__sample_cnt_in = 0;
                _node_645_ph_diff6__previous_correction_in = _node_645_ph_diff6__correction_in;
            }
        }
    }
    // Generated from the component: Node 646.I2.Ia1
    // Generated from the component: Node 646.I3.Ia1
    // Generated from the component: Node 646.ph_diff4
    {
        _node_646_ph_diff4__sample_cnt_ref += 1.0;
        _node_646_ph_diff4__previous_filtered_ref = _node_646_ph_diff4__filtered_ref;
        _node_646_ph_diff4__filtered_ref = ((_node_646_ph_diff4__previous_filtered_ref * _node_646_ph_diff4__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_646_ph_diff4__n_alpha[0]));
        if((_node_646_ph_diff4__sample_cnt_ref >= _node_646_ph_diff4__n_timeout[0])) {
            _node_646_ph_diff4__zc_flag_ref = 0;
            _node_646_ph_diff4__sample_cnt_ref = 0;
            _node_646_ph_diff4__previous_correction_ref = 0;
            _node_646_ph_diff4__phase_state = 0;
        }
        else {
            if(((_node_646_ph_diff4__filtered_ref >= 0) && (_node_646_ph_diff4__previous_filtered_ref < 0))) {
                _node_646_ph_diff4__zc_flag_ref = 1;
            }
            else {
                _node_646_ph_diff4__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_646_ph_diff4__n_out_size; tmp1 += 1) {
            _node_646_ph_diff4__sample_cnt_in += 1;
            _node_646_ph_diff4__previous_filtered_in = _node_646_ph_diff4__filtered_in;
            _node_646_ph_diff4__filtered_in = ((_node_646_ph_diff4__previous_filtered_in * _node_646_ph_diff4__n_one_minus_alpha[0]) + (_node_646_i3_ia1__out * _node_646_ph_diff4__n_alpha[0]));
            if((_node_646_ph_diff4__sample_cnt_in >= _node_646_ph_diff4__n_timeout[0])) {
                _node_646_ph_diff4__zc_flag_in[0] = 0;
                _node_646_ph_diff4__no_zc_flag_in[0] = 1;
                _node_646_ph_diff4__sample_cnt_in = 0;
                _node_646_ph_diff4__previous_correction_in = 0;
                _node_646_ph_diff4__phase_state = 0;
            }
            else {
                if(((_node_646_ph_diff4__filtered_in >= 0) && (_node_646_ph_diff4__previous_filtered_in < 0))) {
                    _node_646_ph_diff4__zc_flag_in[0] = 1;
                    _node_646_ph_diff4__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_646_ph_diff4__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_646_ph_diff4__zc_flag_ref) {
            _node_646_ph_diff4__correction_ref = ((- _node_646_ph_diff4__previous_filtered_ref) / ((_node_646_ph_diff4__filtered_ref - _node_646_ph_diff4__previous_filtered_ref)));
            _node_646_ph_diff4__sample_cnt_ref += ((_node_646_ph_diff4__correction_ref - _node_646_ph_diff4__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_646_ph_diff4__n_out_size; tmp2 += 1) {
                if((fabs(_node_646_ph_diff4__sample_cnt_ref) > 1e-06)) {
                    if((!_node_646_ph_diff4__no_zc_flag_in[0])) {
                        _node_646_ph_diff4__phase_state = ((360 * (((_node_646_ph_diff4__sample_cnt_in + _node_646_ph_diff4__correction_ref) - _node_646_ph_diff4__previous_correction_in))) / _node_646_ph_diff4__sample_cnt_ref);
                    }
                }
                if((fabs(_node_646_ph_diff4__phase_state) > 360)) {
                    _node_646_ph_diff4__phase_state = fmod(_node_646_ph_diff4__phase_state, 360);
                }
                if((_node_646_ph_diff4__phase_state < (- 180))) {
                    _node_646_ph_diff4__phase_state += 360;
                }
                if((_node_646_ph_diff4__phase_state > 180)) {
                    _node_646_ph_diff4__phase_state -= 360;
                }
            }
            _node_646_ph_diff4__sample_cnt_ref = 0;
            _node_646_ph_diff4__previous_correction_ref = _node_646_ph_diff4__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_646_ph_diff4__n_out_size; tmp3 += 1) {
            if(_node_646_ph_diff4__zc_flag_in[0]) {
                _node_646_ph_diff4__correction_in = ((- _node_646_ph_diff4__previous_filtered_in) / ((_node_646_ph_diff4__filtered_in - _node_646_ph_diff4__previous_filtered_in)));
                _node_646_ph_diff4__sample_cnt_in = 0;
                _node_646_ph_diff4__previous_correction_in = _node_646_ph_diff4__correction_in;
            }
        }
    }
    // Generated from the component: Node 646.ph_diff6
    {
        _node_646_ph_diff6__sample_cnt_ref += 1.0;
        _node_646_ph_diff6__previous_filtered_ref = _node_646_ph_diff6__filtered_ref;
        _node_646_ph_diff6__filtered_ref = ((_node_646_ph_diff6__previous_filtered_ref * _node_646_ph_diff6__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_646_ph_diff6__n_alpha[0]));
        if((_node_646_ph_diff6__sample_cnt_ref >= _node_646_ph_diff6__n_timeout[0])) {
            _node_646_ph_diff6__zc_flag_ref = 0;
            _node_646_ph_diff6__sample_cnt_ref = 0;
            _node_646_ph_diff6__previous_correction_ref = 0;
            _node_646_ph_diff6__phase_state = 0;
        }
        else {
            if(((_node_646_ph_diff6__filtered_ref >= 0) && (_node_646_ph_diff6__previous_filtered_ref < 0))) {
                _node_646_ph_diff6__zc_flag_ref = 1;
            }
            else {
                _node_646_ph_diff6__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_646_ph_diff6__n_out_size; tmp1 += 1) {
            _node_646_ph_diff6__sample_cnt_in += 1;
            _node_646_ph_diff6__previous_filtered_in = _node_646_ph_diff6__filtered_in;
            _node_646_ph_diff6__filtered_in = ((_node_646_ph_diff6__previous_filtered_in * _node_646_ph_diff6__n_one_minus_alpha[0]) + (_node_646_i2_ia1__out * _node_646_ph_diff6__n_alpha[0]));
            if((_node_646_ph_diff6__sample_cnt_in >= _node_646_ph_diff6__n_timeout[0])) {
                _node_646_ph_diff6__zc_flag_in[0] = 0;
                _node_646_ph_diff6__no_zc_flag_in[0] = 1;
                _node_646_ph_diff6__sample_cnt_in = 0;
                _node_646_ph_diff6__previous_correction_in = 0;
                _node_646_ph_diff6__phase_state = 0;
            }
            else {
                if(((_node_646_ph_diff6__filtered_in >= 0) && (_node_646_ph_diff6__previous_filtered_in < 0))) {
                    _node_646_ph_diff6__zc_flag_in[0] = 1;
                    _node_646_ph_diff6__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_646_ph_diff6__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_646_ph_diff6__zc_flag_ref) {
            _node_646_ph_diff6__correction_ref = ((- _node_646_ph_diff6__previous_filtered_ref) / ((_node_646_ph_diff6__filtered_ref - _node_646_ph_diff6__previous_filtered_ref)));
            _node_646_ph_diff6__sample_cnt_ref += ((_node_646_ph_diff6__correction_ref - _node_646_ph_diff6__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_646_ph_diff6__n_out_size; tmp2 += 1) {
                if((fabs(_node_646_ph_diff6__sample_cnt_ref) > 1e-06)) {
                    if((!_node_646_ph_diff6__no_zc_flag_in[0])) {
                        _node_646_ph_diff6__phase_state = ((360 * (((_node_646_ph_diff6__sample_cnt_in + _node_646_ph_diff6__correction_ref) - _node_646_ph_diff6__previous_correction_in))) / _node_646_ph_diff6__sample_cnt_ref);
                    }
                }
                if((fabs(_node_646_ph_diff6__phase_state) > 360)) {
                    _node_646_ph_diff6__phase_state = fmod(_node_646_ph_diff6__phase_state, 360);
                }
                if((_node_646_ph_diff6__phase_state < (- 180))) {
                    _node_646_ph_diff6__phase_state += 360;
                }
                if((_node_646_ph_diff6__phase_state > 180)) {
                    _node_646_ph_diff6__phase_state -= 360;
                }
            }
            _node_646_ph_diff6__sample_cnt_ref = 0;
            _node_646_ph_diff6__previous_correction_ref = _node_646_ph_diff6__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_646_ph_diff6__n_out_size; tmp3 += 1) {
            if(_node_646_ph_diff6__zc_flag_in[0]) {
                _node_646_ph_diff6__correction_in = ((- _node_646_ph_diff6__previous_filtered_in) / ((_node_646_ph_diff6__filtered_in - _node_646_ph_diff6__previous_filtered_in)));
                _node_646_ph_diff6__sample_cnt_in = 0;
                _node_646_ph_diff6__previous_correction_in = _node_646_ph_diff6__correction_in;
            }
        }
    }
    // Generated from the component: Node 652.I1.Ia1
    // Generated from the component: Node 652.ph_diff5
    {
        _node_652_ph_diff5__sample_cnt_ref += 1.0;
        _node_652_ph_diff5__previous_filtered_ref = _node_652_ph_diff5__filtered_ref;
        _node_652_ph_diff5__filtered_ref = ((_node_652_ph_diff5__previous_filtered_ref * _node_652_ph_diff5__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_652_ph_diff5__n_alpha[0]));
        if((_node_652_ph_diff5__sample_cnt_ref >= _node_652_ph_diff5__n_timeout[0])) {
            _node_652_ph_diff5__zc_flag_ref = 0;
            _node_652_ph_diff5__sample_cnt_ref = 0;
            _node_652_ph_diff5__previous_correction_ref = 0;
            _node_652_ph_diff5__phase_state = 0;
        }
        else {
            if(((_node_652_ph_diff5__filtered_ref >= 0) && (_node_652_ph_diff5__previous_filtered_ref < 0))) {
                _node_652_ph_diff5__zc_flag_ref = 1;
            }
            else {
                _node_652_ph_diff5__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_652_ph_diff5__n_out_size; tmp1 += 1) {
            _node_652_ph_diff5__sample_cnt_in += 1;
            _node_652_ph_diff5__previous_filtered_in = _node_652_ph_diff5__filtered_in;
            _node_652_ph_diff5__filtered_in = ((_node_652_ph_diff5__previous_filtered_in * _node_652_ph_diff5__n_one_minus_alpha[0]) + (_node_652_i1_ia1__out * _node_652_ph_diff5__n_alpha[0]));
            if((_node_652_ph_diff5__sample_cnt_in >= _node_652_ph_diff5__n_timeout[0])) {
                _node_652_ph_diff5__zc_flag_in[0] = 0;
                _node_652_ph_diff5__no_zc_flag_in[0] = 1;
                _node_652_ph_diff5__sample_cnt_in = 0;
                _node_652_ph_diff5__previous_correction_in = 0;
                _node_652_ph_diff5__phase_state = 0;
            }
            else {
                if(((_node_652_ph_diff5__filtered_in >= 0) && (_node_652_ph_diff5__previous_filtered_in < 0))) {
                    _node_652_ph_diff5__zc_flag_in[0] = 1;
                    _node_652_ph_diff5__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_652_ph_diff5__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_652_ph_diff5__zc_flag_ref) {
            _node_652_ph_diff5__correction_ref = ((- _node_652_ph_diff5__previous_filtered_ref) / ((_node_652_ph_diff5__filtered_ref - _node_652_ph_diff5__previous_filtered_ref)));
            _node_652_ph_diff5__sample_cnt_ref += ((_node_652_ph_diff5__correction_ref - _node_652_ph_diff5__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_652_ph_diff5__n_out_size; tmp2 += 1) {
                if((fabs(_node_652_ph_diff5__sample_cnt_ref) > 1e-06)) {
                    if((!_node_652_ph_diff5__no_zc_flag_in[0])) {
                        _node_652_ph_diff5__phase_state = ((360 * (((_node_652_ph_diff5__sample_cnt_in + _node_652_ph_diff5__correction_ref) - _node_652_ph_diff5__previous_correction_in))) / _node_652_ph_diff5__sample_cnt_ref);
                    }
                }
                if((fabs(_node_652_ph_diff5__phase_state) > 360)) {
                    _node_652_ph_diff5__phase_state = fmod(_node_652_ph_diff5__phase_state, 360);
                }
                if((_node_652_ph_diff5__phase_state < (- 180))) {
                    _node_652_ph_diff5__phase_state += 360;
                }
                if((_node_652_ph_diff5__phase_state > 180)) {
                    _node_652_ph_diff5__phase_state -= 360;
                }
            }
            _node_652_ph_diff5__sample_cnt_ref = 0;
            _node_652_ph_diff5__previous_correction_ref = _node_652_ph_diff5__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_652_ph_diff5__n_out_size; tmp3 += 1) {
            if(_node_652_ph_diff5__zc_flag_in[0]) {
                _node_652_ph_diff5__correction_in = ((- _node_652_ph_diff5__previous_filtered_in) / ((_node_652_ph_diff5__filtered_in - _node_652_ph_diff5__previous_filtered_in)));
                _node_652_ph_diff5__sample_cnt_in = 0;
                _node_652_ph_diff5__previous_correction_in = _node_652_ph_diff5__correction_in;
            }
        }
    }
    // Generated from the component: Node 671.I1.Ia1
    // Generated from the component: Node 671.I2.Ia1
    // Generated from the component: Node 671.I3.Ia1
    // Generated from the component: Node 671.ph_diff4
    {
        _node_671_ph_diff4__sample_cnt_ref += 1.0;
        _node_671_ph_diff4__previous_filtered_ref = _node_671_ph_diff4__filtered_ref;
        _node_671_ph_diff4__filtered_ref = ((_node_671_ph_diff4__previous_filtered_ref * _node_671_ph_diff4__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_671_ph_diff4__n_alpha[0]));
        if((_node_671_ph_diff4__sample_cnt_ref >= _node_671_ph_diff4__n_timeout[0])) {
            _node_671_ph_diff4__zc_flag_ref = 0;
            _node_671_ph_diff4__sample_cnt_ref = 0;
            _node_671_ph_diff4__previous_correction_ref = 0;
            _node_671_ph_diff4__phase_state = 0;
        }
        else {
            if(((_node_671_ph_diff4__filtered_ref >= 0) && (_node_671_ph_diff4__previous_filtered_ref < 0))) {
                _node_671_ph_diff4__zc_flag_ref = 1;
            }
            else {
                _node_671_ph_diff4__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_671_ph_diff4__n_out_size; tmp1 += 1) {
            _node_671_ph_diff4__sample_cnt_in += 1;
            _node_671_ph_diff4__previous_filtered_in = _node_671_ph_diff4__filtered_in;
            _node_671_ph_diff4__filtered_in = ((_node_671_ph_diff4__previous_filtered_in * _node_671_ph_diff4__n_one_minus_alpha[0]) + (_node_671_i3_ia1__out * _node_671_ph_diff4__n_alpha[0]));
            if((_node_671_ph_diff4__sample_cnt_in >= _node_671_ph_diff4__n_timeout[0])) {
                _node_671_ph_diff4__zc_flag_in[0] = 0;
                _node_671_ph_diff4__no_zc_flag_in[0] = 1;
                _node_671_ph_diff4__sample_cnt_in = 0;
                _node_671_ph_diff4__previous_correction_in = 0;
                _node_671_ph_diff4__phase_state = 0;
            }
            else {
                if(((_node_671_ph_diff4__filtered_in >= 0) && (_node_671_ph_diff4__previous_filtered_in < 0))) {
                    _node_671_ph_diff4__zc_flag_in[0] = 1;
                    _node_671_ph_diff4__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_671_ph_diff4__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_671_ph_diff4__zc_flag_ref) {
            _node_671_ph_diff4__correction_ref = ((- _node_671_ph_diff4__previous_filtered_ref) / ((_node_671_ph_diff4__filtered_ref - _node_671_ph_diff4__previous_filtered_ref)));
            _node_671_ph_diff4__sample_cnt_ref += ((_node_671_ph_diff4__correction_ref - _node_671_ph_diff4__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_671_ph_diff4__n_out_size; tmp2 += 1) {
                if((fabs(_node_671_ph_diff4__sample_cnt_ref) > 1e-06)) {
                    if((!_node_671_ph_diff4__no_zc_flag_in[0])) {
                        _node_671_ph_diff4__phase_state = ((360 * (((_node_671_ph_diff4__sample_cnt_in + _node_671_ph_diff4__correction_ref) - _node_671_ph_diff4__previous_correction_in))) / _node_671_ph_diff4__sample_cnt_ref);
                    }
                }
                if((fabs(_node_671_ph_diff4__phase_state) > 360)) {
                    _node_671_ph_diff4__phase_state = fmod(_node_671_ph_diff4__phase_state, 360);
                }
                if((_node_671_ph_diff4__phase_state < (- 180))) {
                    _node_671_ph_diff4__phase_state += 360;
                }
                if((_node_671_ph_diff4__phase_state > 180)) {
                    _node_671_ph_diff4__phase_state -= 360;
                }
            }
            _node_671_ph_diff4__sample_cnt_ref = 0;
            _node_671_ph_diff4__previous_correction_ref = _node_671_ph_diff4__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_671_ph_diff4__n_out_size; tmp3 += 1) {
            if(_node_671_ph_diff4__zc_flag_in[0]) {
                _node_671_ph_diff4__correction_in = ((- _node_671_ph_diff4__previous_filtered_in) / ((_node_671_ph_diff4__filtered_in - _node_671_ph_diff4__previous_filtered_in)));
                _node_671_ph_diff4__sample_cnt_in = 0;
                _node_671_ph_diff4__previous_correction_in = _node_671_ph_diff4__correction_in;
            }
        }
    }
    // Generated from the component: Node 671.ph_diff5
    {
        _node_671_ph_diff5__sample_cnt_ref += 1.0;
        _node_671_ph_diff5__previous_filtered_ref = _node_671_ph_diff5__filtered_ref;
        _node_671_ph_diff5__filtered_ref = ((_node_671_ph_diff5__previous_filtered_ref * _node_671_ph_diff5__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_671_ph_diff5__n_alpha[0]));
        if((_node_671_ph_diff5__sample_cnt_ref >= _node_671_ph_diff5__n_timeout[0])) {
            _node_671_ph_diff5__zc_flag_ref = 0;
            _node_671_ph_diff5__sample_cnt_ref = 0;
            _node_671_ph_diff5__previous_correction_ref = 0;
            _node_671_ph_diff5__phase_state = 0;
        }
        else {
            if(((_node_671_ph_diff5__filtered_ref >= 0) && (_node_671_ph_diff5__previous_filtered_ref < 0))) {
                _node_671_ph_diff5__zc_flag_ref = 1;
            }
            else {
                _node_671_ph_diff5__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_671_ph_diff5__n_out_size; tmp1 += 1) {
            _node_671_ph_diff5__sample_cnt_in += 1;
            _node_671_ph_diff5__previous_filtered_in = _node_671_ph_diff5__filtered_in;
            _node_671_ph_diff5__filtered_in = ((_node_671_ph_diff5__previous_filtered_in * _node_671_ph_diff5__n_one_minus_alpha[0]) + (_node_671_i1_ia1__out * _node_671_ph_diff5__n_alpha[0]));
            if((_node_671_ph_diff5__sample_cnt_in >= _node_671_ph_diff5__n_timeout[0])) {
                _node_671_ph_diff5__zc_flag_in[0] = 0;
                _node_671_ph_diff5__no_zc_flag_in[0] = 1;
                _node_671_ph_diff5__sample_cnt_in = 0;
                _node_671_ph_diff5__previous_correction_in = 0;
                _node_671_ph_diff5__phase_state = 0;
            }
            else {
                if(((_node_671_ph_diff5__filtered_in >= 0) && (_node_671_ph_diff5__previous_filtered_in < 0))) {
                    _node_671_ph_diff5__zc_flag_in[0] = 1;
                    _node_671_ph_diff5__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_671_ph_diff5__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_671_ph_diff5__zc_flag_ref) {
            _node_671_ph_diff5__correction_ref = ((- _node_671_ph_diff5__previous_filtered_ref) / ((_node_671_ph_diff5__filtered_ref - _node_671_ph_diff5__previous_filtered_ref)));
            _node_671_ph_diff5__sample_cnt_ref += ((_node_671_ph_diff5__correction_ref - _node_671_ph_diff5__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_671_ph_diff5__n_out_size; tmp2 += 1) {
                if((fabs(_node_671_ph_diff5__sample_cnt_ref) > 1e-06)) {
                    if((!_node_671_ph_diff5__no_zc_flag_in[0])) {
                        _node_671_ph_diff5__phase_state = ((360 * (((_node_671_ph_diff5__sample_cnt_in + _node_671_ph_diff5__correction_ref) - _node_671_ph_diff5__previous_correction_in))) / _node_671_ph_diff5__sample_cnt_ref);
                    }
                }
                if((fabs(_node_671_ph_diff5__phase_state) > 360)) {
                    _node_671_ph_diff5__phase_state = fmod(_node_671_ph_diff5__phase_state, 360);
                }
                if((_node_671_ph_diff5__phase_state < (- 180))) {
                    _node_671_ph_diff5__phase_state += 360;
                }
                if((_node_671_ph_diff5__phase_state > 180)) {
                    _node_671_ph_diff5__phase_state -= 360;
                }
            }
            _node_671_ph_diff5__sample_cnt_ref = 0;
            _node_671_ph_diff5__previous_correction_ref = _node_671_ph_diff5__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_671_ph_diff5__n_out_size; tmp3 += 1) {
            if(_node_671_ph_diff5__zc_flag_in[0]) {
                _node_671_ph_diff5__correction_in = ((- _node_671_ph_diff5__previous_filtered_in) / ((_node_671_ph_diff5__filtered_in - _node_671_ph_diff5__previous_filtered_in)));
                _node_671_ph_diff5__sample_cnt_in = 0;
                _node_671_ph_diff5__previous_correction_in = _node_671_ph_diff5__correction_in;
            }
        }
    }
    // Generated from the component: Node 671.ph_diff6
    {
        _node_671_ph_diff6__sample_cnt_ref += 1.0;
        _node_671_ph_diff6__previous_filtered_ref = _node_671_ph_diff6__filtered_ref;
        _node_671_ph_diff6__filtered_ref = ((_node_671_ph_diff6__previous_filtered_ref * _node_671_ph_diff6__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_671_ph_diff6__n_alpha[0]));
        if((_node_671_ph_diff6__sample_cnt_ref >= _node_671_ph_diff6__n_timeout[0])) {
            _node_671_ph_diff6__zc_flag_ref = 0;
            _node_671_ph_diff6__sample_cnt_ref = 0;
            _node_671_ph_diff6__previous_correction_ref = 0;
            _node_671_ph_diff6__phase_state = 0;
        }
        else {
            if(((_node_671_ph_diff6__filtered_ref >= 0) && (_node_671_ph_diff6__previous_filtered_ref < 0))) {
                _node_671_ph_diff6__zc_flag_ref = 1;
            }
            else {
                _node_671_ph_diff6__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_671_ph_diff6__n_out_size; tmp1 += 1) {
            _node_671_ph_diff6__sample_cnt_in += 1;
            _node_671_ph_diff6__previous_filtered_in = _node_671_ph_diff6__filtered_in;
            _node_671_ph_diff6__filtered_in = ((_node_671_ph_diff6__previous_filtered_in * _node_671_ph_diff6__n_one_minus_alpha[0]) + (_node_671_i2_ia1__out * _node_671_ph_diff6__n_alpha[0]));
            if((_node_671_ph_diff6__sample_cnt_in >= _node_671_ph_diff6__n_timeout[0])) {
                _node_671_ph_diff6__zc_flag_in[0] = 0;
                _node_671_ph_diff6__no_zc_flag_in[0] = 1;
                _node_671_ph_diff6__sample_cnt_in = 0;
                _node_671_ph_diff6__previous_correction_in = 0;
                _node_671_ph_diff6__phase_state = 0;
            }
            else {
                if(((_node_671_ph_diff6__filtered_in >= 0) && (_node_671_ph_diff6__previous_filtered_in < 0))) {
                    _node_671_ph_diff6__zc_flag_in[0] = 1;
                    _node_671_ph_diff6__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_671_ph_diff6__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_671_ph_diff6__zc_flag_ref) {
            _node_671_ph_diff6__correction_ref = ((- _node_671_ph_diff6__previous_filtered_ref) / ((_node_671_ph_diff6__filtered_ref - _node_671_ph_diff6__previous_filtered_ref)));
            _node_671_ph_diff6__sample_cnt_ref += ((_node_671_ph_diff6__correction_ref - _node_671_ph_diff6__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_671_ph_diff6__n_out_size; tmp2 += 1) {
                if((fabs(_node_671_ph_diff6__sample_cnt_ref) > 1e-06)) {
                    if((!_node_671_ph_diff6__no_zc_flag_in[0])) {
                        _node_671_ph_diff6__phase_state = ((360 * (((_node_671_ph_diff6__sample_cnt_in + _node_671_ph_diff6__correction_ref) - _node_671_ph_diff6__previous_correction_in))) / _node_671_ph_diff6__sample_cnt_ref);
                    }
                }
                if((fabs(_node_671_ph_diff6__phase_state) > 360)) {
                    _node_671_ph_diff6__phase_state = fmod(_node_671_ph_diff6__phase_state, 360);
                }
                if((_node_671_ph_diff6__phase_state < (- 180))) {
                    _node_671_ph_diff6__phase_state += 360;
                }
                if((_node_671_ph_diff6__phase_state > 180)) {
                    _node_671_ph_diff6__phase_state -= 360;
                }
            }
            _node_671_ph_diff6__sample_cnt_ref = 0;
            _node_671_ph_diff6__previous_correction_ref = _node_671_ph_diff6__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_671_ph_diff6__n_out_size; tmp3 += 1) {
            if(_node_671_ph_diff6__zc_flag_in[0]) {
                _node_671_ph_diff6__correction_in = ((- _node_671_ph_diff6__previous_filtered_in) / ((_node_671_ph_diff6__filtered_in - _node_671_ph_diff6__previous_filtered_in)));
                _node_671_ph_diff6__sample_cnt_in = 0;
                _node_671_ph_diff6__previous_correction_in = _node_671_ph_diff6__correction_in;
            }
        }
    }
    // Generated from the component: Node 675.I1.Ia1
    // Generated from the component: Node 675.I2.Ia1
    // Generated from the component: Node 675.I3.Ia1
    // Generated from the component: Node 675.ph_diff4
    {
        _node_675_ph_diff4__sample_cnt_ref += 1.0;
        _node_675_ph_diff4__previous_filtered_ref = _node_675_ph_diff4__filtered_ref;
        _node_675_ph_diff4__filtered_ref = ((_node_675_ph_diff4__previous_filtered_ref * _node_675_ph_diff4__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_675_ph_diff4__n_alpha[0]));
        if((_node_675_ph_diff4__sample_cnt_ref >= _node_675_ph_diff4__n_timeout[0])) {
            _node_675_ph_diff4__zc_flag_ref = 0;
            _node_675_ph_diff4__sample_cnt_ref = 0;
            _node_675_ph_diff4__previous_correction_ref = 0;
            _node_675_ph_diff4__phase_state = 0;
        }
        else {
            if(((_node_675_ph_diff4__filtered_ref >= 0) && (_node_675_ph_diff4__previous_filtered_ref < 0))) {
                _node_675_ph_diff4__zc_flag_ref = 1;
            }
            else {
                _node_675_ph_diff4__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_675_ph_diff4__n_out_size; tmp1 += 1) {
            _node_675_ph_diff4__sample_cnt_in += 1;
            _node_675_ph_diff4__previous_filtered_in = _node_675_ph_diff4__filtered_in;
            _node_675_ph_diff4__filtered_in = ((_node_675_ph_diff4__previous_filtered_in * _node_675_ph_diff4__n_one_minus_alpha[0]) + (_node_675_i3_ia1__out * _node_675_ph_diff4__n_alpha[0]));
            if((_node_675_ph_diff4__sample_cnt_in >= _node_675_ph_diff4__n_timeout[0])) {
                _node_675_ph_diff4__zc_flag_in[0] = 0;
                _node_675_ph_diff4__no_zc_flag_in[0] = 1;
                _node_675_ph_diff4__sample_cnt_in = 0;
                _node_675_ph_diff4__previous_correction_in = 0;
                _node_675_ph_diff4__phase_state = 0;
            }
            else {
                if(((_node_675_ph_diff4__filtered_in >= 0) && (_node_675_ph_diff4__previous_filtered_in < 0))) {
                    _node_675_ph_diff4__zc_flag_in[0] = 1;
                    _node_675_ph_diff4__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_675_ph_diff4__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_675_ph_diff4__zc_flag_ref) {
            _node_675_ph_diff4__correction_ref = ((- _node_675_ph_diff4__previous_filtered_ref) / ((_node_675_ph_diff4__filtered_ref - _node_675_ph_diff4__previous_filtered_ref)));
            _node_675_ph_diff4__sample_cnt_ref += ((_node_675_ph_diff4__correction_ref - _node_675_ph_diff4__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_675_ph_diff4__n_out_size; tmp2 += 1) {
                if((fabs(_node_675_ph_diff4__sample_cnt_ref) > 1e-06)) {
                    if((!_node_675_ph_diff4__no_zc_flag_in[0])) {
                        _node_675_ph_diff4__phase_state = ((360 * (((_node_675_ph_diff4__sample_cnt_in + _node_675_ph_diff4__correction_ref) - _node_675_ph_diff4__previous_correction_in))) / _node_675_ph_diff4__sample_cnt_ref);
                    }
                }
                if((fabs(_node_675_ph_diff4__phase_state) > 360)) {
                    _node_675_ph_diff4__phase_state = fmod(_node_675_ph_diff4__phase_state, 360);
                }
                if((_node_675_ph_diff4__phase_state < (- 180))) {
                    _node_675_ph_diff4__phase_state += 360;
                }
                if((_node_675_ph_diff4__phase_state > 180)) {
                    _node_675_ph_diff4__phase_state -= 360;
                }
            }
            _node_675_ph_diff4__sample_cnt_ref = 0;
            _node_675_ph_diff4__previous_correction_ref = _node_675_ph_diff4__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_675_ph_diff4__n_out_size; tmp3 += 1) {
            if(_node_675_ph_diff4__zc_flag_in[0]) {
                _node_675_ph_diff4__correction_in = ((- _node_675_ph_diff4__previous_filtered_in) / ((_node_675_ph_diff4__filtered_in - _node_675_ph_diff4__previous_filtered_in)));
                _node_675_ph_diff4__sample_cnt_in = 0;
                _node_675_ph_diff4__previous_correction_in = _node_675_ph_diff4__correction_in;
            }
        }
    }
    // Generated from the component: Node 675.ph_diff5
    {
        _node_675_ph_diff5__sample_cnt_ref += 1.0;
        _node_675_ph_diff5__previous_filtered_ref = _node_675_ph_diff5__filtered_ref;
        _node_675_ph_diff5__filtered_ref = ((_node_675_ph_diff5__previous_filtered_ref * _node_675_ph_diff5__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_675_ph_diff5__n_alpha[0]));
        if((_node_675_ph_diff5__sample_cnt_ref >= _node_675_ph_diff5__n_timeout[0])) {
            _node_675_ph_diff5__zc_flag_ref = 0;
            _node_675_ph_diff5__sample_cnt_ref = 0;
            _node_675_ph_diff5__previous_correction_ref = 0;
            _node_675_ph_diff5__phase_state = 0;
        }
        else {
            if(((_node_675_ph_diff5__filtered_ref >= 0) && (_node_675_ph_diff5__previous_filtered_ref < 0))) {
                _node_675_ph_diff5__zc_flag_ref = 1;
            }
            else {
                _node_675_ph_diff5__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_675_ph_diff5__n_out_size; tmp1 += 1) {
            _node_675_ph_diff5__sample_cnt_in += 1;
            _node_675_ph_diff5__previous_filtered_in = _node_675_ph_diff5__filtered_in;
            _node_675_ph_diff5__filtered_in = ((_node_675_ph_diff5__previous_filtered_in * _node_675_ph_diff5__n_one_minus_alpha[0]) + (_node_675_i1_ia1__out * _node_675_ph_diff5__n_alpha[0]));
            if((_node_675_ph_diff5__sample_cnt_in >= _node_675_ph_diff5__n_timeout[0])) {
                _node_675_ph_diff5__zc_flag_in[0] = 0;
                _node_675_ph_diff5__no_zc_flag_in[0] = 1;
                _node_675_ph_diff5__sample_cnt_in = 0;
                _node_675_ph_diff5__previous_correction_in = 0;
                _node_675_ph_diff5__phase_state = 0;
            }
            else {
                if(((_node_675_ph_diff5__filtered_in >= 0) && (_node_675_ph_diff5__previous_filtered_in < 0))) {
                    _node_675_ph_diff5__zc_flag_in[0] = 1;
                    _node_675_ph_diff5__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_675_ph_diff5__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_675_ph_diff5__zc_flag_ref) {
            _node_675_ph_diff5__correction_ref = ((- _node_675_ph_diff5__previous_filtered_ref) / ((_node_675_ph_diff5__filtered_ref - _node_675_ph_diff5__previous_filtered_ref)));
            _node_675_ph_diff5__sample_cnt_ref += ((_node_675_ph_diff5__correction_ref - _node_675_ph_diff5__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_675_ph_diff5__n_out_size; tmp2 += 1) {
                if((fabs(_node_675_ph_diff5__sample_cnt_ref) > 1e-06)) {
                    if((!_node_675_ph_diff5__no_zc_flag_in[0])) {
                        _node_675_ph_diff5__phase_state = ((360 * (((_node_675_ph_diff5__sample_cnt_in + _node_675_ph_diff5__correction_ref) - _node_675_ph_diff5__previous_correction_in))) / _node_675_ph_diff5__sample_cnt_ref);
                    }
                }
                if((fabs(_node_675_ph_diff5__phase_state) > 360)) {
                    _node_675_ph_diff5__phase_state = fmod(_node_675_ph_diff5__phase_state, 360);
                }
                if((_node_675_ph_diff5__phase_state < (- 180))) {
                    _node_675_ph_diff5__phase_state += 360;
                }
                if((_node_675_ph_diff5__phase_state > 180)) {
                    _node_675_ph_diff5__phase_state -= 360;
                }
            }
            _node_675_ph_diff5__sample_cnt_ref = 0;
            _node_675_ph_diff5__previous_correction_ref = _node_675_ph_diff5__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_675_ph_diff5__n_out_size; tmp3 += 1) {
            if(_node_675_ph_diff5__zc_flag_in[0]) {
                _node_675_ph_diff5__correction_in = ((- _node_675_ph_diff5__previous_filtered_in) / ((_node_675_ph_diff5__filtered_in - _node_675_ph_diff5__previous_filtered_in)));
                _node_675_ph_diff5__sample_cnt_in = 0;
                _node_675_ph_diff5__previous_correction_in = _node_675_ph_diff5__correction_in;
            }
        }
    }
    // Generated from the component: Node 675.ph_diff6
    {
        _node_675_ph_diff6__sample_cnt_ref += 1.0;
        _node_675_ph_diff6__previous_filtered_ref = _node_675_ph_diff6__filtered_ref;
        _node_675_ph_diff6__filtered_ref = ((_node_675_ph_diff6__previous_filtered_ref * _node_675_ph_diff6__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_675_ph_diff6__n_alpha[0]));
        if((_node_675_ph_diff6__sample_cnt_ref >= _node_675_ph_diff6__n_timeout[0])) {
            _node_675_ph_diff6__zc_flag_ref = 0;
            _node_675_ph_diff6__sample_cnt_ref = 0;
            _node_675_ph_diff6__previous_correction_ref = 0;
            _node_675_ph_diff6__phase_state = 0;
        }
        else {
            if(((_node_675_ph_diff6__filtered_ref >= 0) && (_node_675_ph_diff6__previous_filtered_ref < 0))) {
                _node_675_ph_diff6__zc_flag_ref = 1;
            }
            else {
                _node_675_ph_diff6__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_675_ph_diff6__n_out_size; tmp1 += 1) {
            _node_675_ph_diff6__sample_cnt_in += 1;
            _node_675_ph_diff6__previous_filtered_in = _node_675_ph_diff6__filtered_in;
            _node_675_ph_diff6__filtered_in = ((_node_675_ph_diff6__previous_filtered_in * _node_675_ph_diff6__n_one_minus_alpha[0]) + (_node_675_i2_ia1__out * _node_675_ph_diff6__n_alpha[0]));
            if((_node_675_ph_diff6__sample_cnt_in >= _node_675_ph_diff6__n_timeout[0])) {
                _node_675_ph_diff6__zc_flag_in[0] = 0;
                _node_675_ph_diff6__no_zc_flag_in[0] = 1;
                _node_675_ph_diff6__sample_cnt_in = 0;
                _node_675_ph_diff6__previous_correction_in = 0;
                _node_675_ph_diff6__phase_state = 0;
            }
            else {
                if(((_node_675_ph_diff6__filtered_in >= 0) && (_node_675_ph_diff6__previous_filtered_in < 0))) {
                    _node_675_ph_diff6__zc_flag_in[0] = 1;
                    _node_675_ph_diff6__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_675_ph_diff6__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_675_ph_diff6__zc_flag_ref) {
            _node_675_ph_diff6__correction_ref = ((- _node_675_ph_diff6__previous_filtered_ref) / ((_node_675_ph_diff6__filtered_ref - _node_675_ph_diff6__previous_filtered_ref)));
            _node_675_ph_diff6__sample_cnt_ref += ((_node_675_ph_diff6__correction_ref - _node_675_ph_diff6__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_675_ph_diff6__n_out_size; tmp2 += 1) {
                if((fabs(_node_675_ph_diff6__sample_cnt_ref) > 1e-06)) {
                    if((!_node_675_ph_diff6__no_zc_flag_in[0])) {
                        _node_675_ph_diff6__phase_state = ((360 * (((_node_675_ph_diff6__sample_cnt_in + _node_675_ph_diff6__correction_ref) - _node_675_ph_diff6__previous_correction_in))) / _node_675_ph_diff6__sample_cnt_ref);
                    }
                }
                if((fabs(_node_675_ph_diff6__phase_state) > 360)) {
                    _node_675_ph_diff6__phase_state = fmod(_node_675_ph_diff6__phase_state, 360);
                }
                if((_node_675_ph_diff6__phase_state < (- 180))) {
                    _node_675_ph_diff6__phase_state += 360;
                }
                if((_node_675_ph_diff6__phase_state > 180)) {
                    _node_675_ph_diff6__phase_state -= 360;
                }
            }
            _node_675_ph_diff6__sample_cnt_ref = 0;
            _node_675_ph_diff6__previous_correction_ref = _node_675_ph_diff6__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_675_ph_diff6__n_out_size; tmp3 += 1) {
            if(_node_675_ph_diff6__zc_flag_in[0]) {
                _node_675_ph_diff6__correction_in = ((- _node_675_ph_diff6__previous_filtered_in) / ((_node_675_ph_diff6__filtered_in - _node_675_ph_diff6__previous_filtered_in)));
                _node_675_ph_diff6__sample_cnt_in = 0;
                _node_675_ph_diff6__previous_correction_in = _node_675_ph_diff6__correction_in;
            }
        }
    }
    // Generated from the component: Node 680.I1.Ia1
    // Generated from the component: Node 680.I2.Ia1
    // Generated from the component: Node 680.I3.Ia1
    // Generated from the component: Node 680.ph_diff4
    {
        _node_680_ph_diff4__sample_cnt_ref += 1.0;
        _node_680_ph_diff4__previous_filtered_ref = _node_680_ph_diff4__filtered_ref;
        _node_680_ph_diff4__filtered_ref = ((_node_680_ph_diff4__previous_filtered_ref * _node_680_ph_diff4__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_680_ph_diff4__n_alpha[0]));
        if((_node_680_ph_diff4__sample_cnt_ref >= _node_680_ph_diff4__n_timeout[0])) {
            _node_680_ph_diff4__zc_flag_ref = 0;
            _node_680_ph_diff4__sample_cnt_ref = 0;
            _node_680_ph_diff4__previous_correction_ref = 0;
            _node_680_ph_diff4__phase_state = 0;
        }
        else {
            if(((_node_680_ph_diff4__filtered_ref >= 0) && (_node_680_ph_diff4__previous_filtered_ref < 0))) {
                _node_680_ph_diff4__zc_flag_ref = 1;
            }
            else {
                _node_680_ph_diff4__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_680_ph_diff4__n_out_size; tmp1 += 1) {
            _node_680_ph_diff4__sample_cnt_in += 1;
            _node_680_ph_diff4__previous_filtered_in = _node_680_ph_diff4__filtered_in;
            _node_680_ph_diff4__filtered_in = ((_node_680_ph_diff4__previous_filtered_in * _node_680_ph_diff4__n_one_minus_alpha[0]) + (_node_680_i3_ia1__out * _node_680_ph_diff4__n_alpha[0]));
            if((_node_680_ph_diff4__sample_cnt_in >= _node_680_ph_diff4__n_timeout[0])) {
                _node_680_ph_diff4__zc_flag_in[0] = 0;
                _node_680_ph_diff4__no_zc_flag_in[0] = 1;
                _node_680_ph_diff4__sample_cnt_in = 0;
                _node_680_ph_diff4__previous_correction_in = 0;
                _node_680_ph_diff4__phase_state = 0;
            }
            else {
                if(((_node_680_ph_diff4__filtered_in >= 0) && (_node_680_ph_diff4__previous_filtered_in < 0))) {
                    _node_680_ph_diff4__zc_flag_in[0] = 1;
                    _node_680_ph_diff4__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_680_ph_diff4__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_680_ph_diff4__zc_flag_ref) {
            _node_680_ph_diff4__correction_ref = ((- _node_680_ph_diff4__previous_filtered_ref) / ((_node_680_ph_diff4__filtered_ref - _node_680_ph_diff4__previous_filtered_ref)));
            _node_680_ph_diff4__sample_cnt_ref += ((_node_680_ph_diff4__correction_ref - _node_680_ph_diff4__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_680_ph_diff4__n_out_size; tmp2 += 1) {
                if((fabs(_node_680_ph_diff4__sample_cnt_ref) > 1e-06)) {
                    if((!_node_680_ph_diff4__no_zc_flag_in[0])) {
                        _node_680_ph_diff4__phase_state = ((360 * (((_node_680_ph_diff4__sample_cnt_in + _node_680_ph_diff4__correction_ref) - _node_680_ph_diff4__previous_correction_in))) / _node_680_ph_diff4__sample_cnt_ref);
                    }
                }
                if((fabs(_node_680_ph_diff4__phase_state) > 360)) {
                    _node_680_ph_diff4__phase_state = fmod(_node_680_ph_diff4__phase_state, 360);
                }
                if((_node_680_ph_diff4__phase_state < (- 180))) {
                    _node_680_ph_diff4__phase_state += 360;
                }
                if((_node_680_ph_diff4__phase_state > 180)) {
                    _node_680_ph_diff4__phase_state -= 360;
                }
            }
            _node_680_ph_diff4__sample_cnt_ref = 0;
            _node_680_ph_diff4__previous_correction_ref = _node_680_ph_diff4__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_680_ph_diff4__n_out_size; tmp3 += 1) {
            if(_node_680_ph_diff4__zc_flag_in[0]) {
                _node_680_ph_diff4__correction_in = ((- _node_680_ph_diff4__previous_filtered_in) / ((_node_680_ph_diff4__filtered_in - _node_680_ph_diff4__previous_filtered_in)));
                _node_680_ph_diff4__sample_cnt_in = 0;
                _node_680_ph_diff4__previous_correction_in = _node_680_ph_diff4__correction_in;
            }
        }
    }
    // Generated from the component: Node 680.ph_diff5
    {
        _node_680_ph_diff5__sample_cnt_ref += 1.0;
        _node_680_ph_diff5__previous_filtered_ref = _node_680_ph_diff5__filtered_ref;
        _node_680_ph_diff5__filtered_ref = ((_node_680_ph_diff5__previous_filtered_ref * _node_680_ph_diff5__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_680_ph_diff5__n_alpha[0]));
        if((_node_680_ph_diff5__sample_cnt_ref >= _node_680_ph_diff5__n_timeout[0])) {
            _node_680_ph_diff5__zc_flag_ref = 0;
            _node_680_ph_diff5__sample_cnt_ref = 0;
            _node_680_ph_diff5__previous_correction_ref = 0;
            _node_680_ph_diff5__phase_state = 0;
        }
        else {
            if(((_node_680_ph_diff5__filtered_ref >= 0) && (_node_680_ph_diff5__previous_filtered_ref < 0))) {
                _node_680_ph_diff5__zc_flag_ref = 1;
            }
            else {
                _node_680_ph_diff5__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_680_ph_diff5__n_out_size; tmp1 += 1) {
            _node_680_ph_diff5__sample_cnt_in += 1;
            _node_680_ph_diff5__previous_filtered_in = _node_680_ph_diff5__filtered_in;
            _node_680_ph_diff5__filtered_in = ((_node_680_ph_diff5__previous_filtered_in * _node_680_ph_diff5__n_one_minus_alpha[0]) + (_node_680_i1_ia1__out * _node_680_ph_diff5__n_alpha[0]));
            if((_node_680_ph_diff5__sample_cnt_in >= _node_680_ph_diff5__n_timeout[0])) {
                _node_680_ph_diff5__zc_flag_in[0] = 0;
                _node_680_ph_diff5__no_zc_flag_in[0] = 1;
                _node_680_ph_diff5__sample_cnt_in = 0;
                _node_680_ph_diff5__previous_correction_in = 0;
                _node_680_ph_diff5__phase_state = 0;
            }
            else {
                if(((_node_680_ph_diff5__filtered_in >= 0) && (_node_680_ph_diff5__previous_filtered_in < 0))) {
                    _node_680_ph_diff5__zc_flag_in[0] = 1;
                    _node_680_ph_diff5__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_680_ph_diff5__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_680_ph_diff5__zc_flag_ref) {
            _node_680_ph_diff5__correction_ref = ((- _node_680_ph_diff5__previous_filtered_ref) / ((_node_680_ph_diff5__filtered_ref - _node_680_ph_diff5__previous_filtered_ref)));
            _node_680_ph_diff5__sample_cnt_ref += ((_node_680_ph_diff5__correction_ref - _node_680_ph_diff5__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_680_ph_diff5__n_out_size; tmp2 += 1) {
                if((fabs(_node_680_ph_diff5__sample_cnt_ref) > 1e-06)) {
                    if((!_node_680_ph_diff5__no_zc_flag_in[0])) {
                        _node_680_ph_diff5__phase_state = ((360 * (((_node_680_ph_diff5__sample_cnt_in + _node_680_ph_diff5__correction_ref) - _node_680_ph_diff5__previous_correction_in))) / _node_680_ph_diff5__sample_cnt_ref);
                    }
                }
                if((fabs(_node_680_ph_diff5__phase_state) > 360)) {
                    _node_680_ph_diff5__phase_state = fmod(_node_680_ph_diff5__phase_state, 360);
                }
                if((_node_680_ph_diff5__phase_state < (- 180))) {
                    _node_680_ph_diff5__phase_state += 360;
                }
                if((_node_680_ph_diff5__phase_state > 180)) {
                    _node_680_ph_diff5__phase_state -= 360;
                }
            }
            _node_680_ph_diff5__sample_cnt_ref = 0;
            _node_680_ph_diff5__previous_correction_ref = _node_680_ph_diff5__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_680_ph_diff5__n_out_size; tmp3 += 1) {
            if(_node_680_ph_diff5__zc_flag_in[0]) {
                _node_680_ph_diff5__correction_in = ((- _node_680_ph_diff5__previous_filtered_in) / ((_node_680_ph_diff5__filtered_in - _node_680_ph_diff5__previous_filtered_in)));
                _node_680_ph_diff5__sample_cnt_in = 0;
                _node_680_ph_diff5__previous_correction_in = _node_680_ph_diff5__correction_in;
            }
        }
    }
    // Generated from the component: Node 680.ph_diff6
    {
        _node_680_ph_diff6__sample_cnt_ref += 1.0;
        _node_680_ph_diff6__previous_filtered_ref = _node_680_ph_diff6__filtered_ref;
        _node_680_ph_diff6__filtered_ref = ((_node_680_ph_diff6__previous_filtered_ref * _node_680_ph_diff6__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_680_ph_diff6__n_alpha[0]));
        if((_node_680_ph_diff6__sample_cnt_ref >= _node_680_ph_diff6__n_timeout[0])) {
            _node_680_ph_diff6__zc_flag_ref = 0;
            _node_680_ph_diff6__sample_cnt_ref = 0;
            _node_680_ph_diff6__previous_correction_ref = 0;
            _node_680_ph_diff6__phase_state = 0;
        }
        else {
            if(((_node_680_ph_diff6__filtered_ref >= 0) && (_node_680_ph_diff6__previous_filtered_ref < 0))) {
                _node_680_ph_diff6__zc_flag_ref = 1;
            }
            else {
                _node_680_ph_diff6__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_680_ph_diff6__n_out_size; tmp1 += 1) {
            _node_680_ph_diff6__sample_cnt_in += 1;
            _node_680_ph_diff6__previous_filtered_in = _node_680_ph_diff6__filtered_in;
            _node_680_ph_diff6__filtered_in = ((_node_680_ph_diff6__previous_filtered_in * _node_680_ph_diff6__n_one_minus_alpha[0]) + (_node_680_i2_ia1__out * _node_680_ph_diff6__n_alpha[0]));
            if((_node_680_ph_diff6__sample_cnt_in >= _node_680_ph_diff6__n_timeout[0])) {
                _node_680_ph_diff6__zc_flag_in[0] = 0;
                _node_680_ph_diff6__no_zc_flag_in[0] = 1;
                _node_680_ph_diff6__sample_cnt_in = 0;
                _node_680_ph_diff6__previous_correction_in = 0;
                _node_680_ph_diff6__phase_state = 0;
            }
            else {
                if(((_node_680_ph_diff6__filtered_in >= 0) && (_node_680_ph_diff6__previous_filtered_in < 0))) {
                    _node_680_ph_diff6__zc_flag_in[0] = 1;
                    _node_680_ph_diff6__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_680_ph_diff6__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_680_ph_diff6__zc_flag_ref) {
            _node_680_ph_diff6__correction_ref = ((- _node_680_ph_diff6__previous_filtered_ref) / ((_node_680_ph_diff6__filtered_ref - _node_680_ph_diff6__previous_filtered_ref)));
            _node_680_ph_diff6__sample_cnt_ref += ((_node_680_ph_diff6__correction_ref - _node_680_ph_diff6__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_680_ph_diff6__n_out_size; tmp2 += 1) {
                if((fabs(_node_680_ph_diff6__sample_cnt_ref) > 1e-06)) {
                    if((!_node_680_ph_diff6__no_zc_flag_in[0])) {
                        _node_680_ph_diff6__phase_state = ((360 * (((_node_680_ph_diff6__sample_cnt_in + _node_680_ph_diff6__correction_ref) - _node_680_ph_diff6__previous_correction_in))) / _node_680_ph_diff6__sample_cnt_ref);
                    }
                }
                if((fabs(_node_680_ph_diff6__phase_state) > 360)) {
                    _node_680_ph_diff6__phase_state = fmod(_node_680_ph_diff6__phase_state, 360);
                }
                if((_node_680_ph_diff6__phase_state < (- 180))) {
                    _node_680_ph_diff6__phase_state += 360;
                }
                if((_node_680_ph_diff6__phase_state > 180)) {
                    _node_680_ph_diff6__phase_state -= 360;
                }
            }
            _node_680_ph_diff6__sample_cnt_ref = 0;
            _node_680_ph_diff6__previous_correction_ref = _node_680_ph_diff6__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_680_ph_diff6__n_out_size; tmp3 += 1) {
            if(_node_680_ph_diff6__zc_flag_in[0]) {
                _node_680_ph_diff6__correction_in = ((- _node_680_ph_diff6__previous_filtered_in) / ((_node_680_ph_diff6__filtered_in - _node_680_ph_diff6__previous_filtered_in)));
                _node_680_ph_diff6__sample_cnt_in = 0;
                _node_680_ph_diff6__previous_correction_in = _node_680_ph_diff6__correction_in;
            }
        }
    }
    // Generated from the component: Node 684.I1.Ia1
    // Generated from the component: Node 684.I3.Ia1
    // Generated from the component: Node 684.ph_diff4
    {
        _node_684_ph_diff4__sample_cnt_ref += 1.0;
        _node_684_ph_diff4__previous_filtered_ref = _node_684_ph_diff4__filtered_ref;
        _node_684_ph_diff4__filtered_ref = ((_node_684_ph_diff4__previous_filtered_ref * _node_684_ph_diff4__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_684_ph_diff4__n_alpha[0]));
        if((_node_684_ph_diff4__sample_cnt_ref >= _node_684_ph_diff4__n_timeout[0])) {
            _node_684_ph_diff4__zc_flag_ref = 0;
            _node_684_ph_diff4__sample_cnt_ref = 0;
            _node_684_ph_diff4__previous_correction_ref = 0;
            _node_684_ph_diff4__phase_state = 0;
        }
        else {
            if(((_node_684_ph_diff4__filtered_ref >= 0) && (_node_684_ph_diff4__previous_filtered_ref < 0))) {
                _node_684_ph_diff4__zc_flag_ref = 1;
            }
            else {
                _node_684_ph_diff4__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_684_ph_diff4__n_out_size; tmp1 += 1) {
            _node_684_ph_diff4__sample_cnt_in += 1;
            _node_684_ph_diff4__previous_filtered_in = _node_684_ph_diff4__filtered_in;
            _node_684_ph_diff4__filtered_in = ((_node_684_ph_diff4__previous_filtered_in * _node_684_ph_diff4__n_one_minus_alpha[0]) + (_node_684_i3_ia1__out * _node_684_ph_diff4__n_alpha[0]));
            if((_node_684_ph_diff4__sample_cnt_in >= _node_684_ph_diff4__n_timeout[0])) {
                _node_684_ph_diff4__zc_flag_in[0] = 0;
                _node_684_ph_diff4__no_zc_flag_in[0] = 1;
                _node_684_ph_diff4__sample_cnt_in = 0;
                _node_684_ph_diff4__previous_correction_in = 0;
                _node_684_ph_diff4__phase_state = 0;
            }
            else {
                if(((_node_684_ph_diff4__filtered_in >= 0) && (_node_684_ph_diff4__previous_filtered_in < 0))) {
                    _node_684_ph_diff4__zc_flag_in[0] = 1;
                    _node_684_ph_diff4__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_684_ph_diff4__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_684_ph_diff4__zc_flag_ref) {
            _node_684_ph_diff4__correction_ref = ((- _node_684_ph_diff4__previous_filtered_ref) / ((_node_684_ph_diff4__filtered_ref - _node_684_ph_diff4__previous_filtered_ref)));
            _node_684_ph_diff4__sample_cnt_ref += ((_node_684_ph_diff4__correction_ref - _node_684_ph_diff4__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_684_ph_diff4__n_out_size; tmp2 += 1) {
                if((fabs(_node_684_ph_diff4__sample_cnt_ref) > 1e-06)) {
                    if((!_node_684_ph_diff4__no_zc_flag_in[0])) {
                        _node_684_ph_diff4__phase_state = ((360 * (((_node_684_ph_diff4__sample_cnt_in + _node_684_ph_diff4__correction_ref) - _node_684_ph_diff4__previous_correction_in))) / _node_684_ph_diff4__sample_cnt_ref);
                    }
                }
                if((fabs(_node_684_ph_diff4__phase_state) > 360)) {
                    _node_684_ph_diff4__phase_state = fmod(_node_684_ph_diff4__phase_state, 360);
                }
                if((_node_684_ph_diff4__phase_state < (- 180))) {
                    _node_684_ph_diff4__phase_state += 360;
                }
                if((_node_684_ph_diff4__phase_state > 180)) {
                    _node_684_ph_diff4__phase_state -= 360;
                }
            }
            _node_684_ph_diff4__sample_cnt_ref = 0;
            _node_684_ph_diff4__previous_correction_ref = _node_684_ph_diff4__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_684_ph_diff4__n_out_size; tmp3 += 1) {
            if(_node_684_ph_diff4__zc_flag_in[0]) {
                _node_684_ph_diff4__correction_in = ((- _node_684_ph_diff4__previous_filtered_in) / ((_node_684_ph_diff4__filtered_in - _node_684_ph_diff4__previous_filtered_in)));
                _node_684_ph_diff4__sample_cnt_in = 0;
                _node_684_ph_diff4__previous_correction_in = _node_684_ph_diff4__correction_in;
            }
        }
    }
    // Generated from the component: Node 684.ph_diff5
    {
        _node_684_ph_diff5__sample_cnt_ref += 1.0;
        _node_684_ph_diff5__previous_filtered_ref = _node_684_ph_diff5__filtered_ref;
        _node_684_ph_diff5__filtered_ref = ((_node_684_ph_diff5__previous_filtered_ref * _node_684_ph_diff5__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_684_ph_diff5__n_alpha[0]));
        if((_node_684_ph_diff5__sample_cnt_ref >= _node_684_ph_diff5__n_timeout[0])) {
            _node_684_ph_diff5__zc_flag_ref = 0;
            _node_684_ph_diff5__sample_cnt_ref = 0;
            _node_684_ph_diff5__previous_correction_ref = 0;
            _node_684_ph_diff5__phase_state = 0;
        }
        else {
            if(((_node_684_ph_diff5__filtered_ref >= 0) && (_node_684_ph_diff5__previous_filtered_ref < 0))) {
                _node_684_ph_diff5__zc_flag_ref = 1;
            }
            else {
                _node_684_ph_diff5__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_684_ph_diff5__n_out_size; tmp1 += 1) {
            _node_684_ph_diff5__sample_cnt_in += 1;
            _node_684_ph_diff5__previous_filtered_in = _node_684_ph_diff5__filtered_in;
            _node_684_ph_diff5__filtered_in = ((_node_684_ph_diff5__previous_filtered_in * _node_684_ph_diff5__n_one_minus_alpha[0]) + (_node_684_i1_ia1__out * _node_684_ph_diff5__n_alpha[0]));
            if((_node_684_ph_diff5__sample_cnt_in >= _node_684_ph_diff5__n_timeout[0])) {
                _node_684_ph_diff5__zc_flag_in[0] = 0;
                _node_684_ph_diff5__no_zc_flag_in[0] = 1;
                _node_684_ph_diff5__sample_cnt_in = 0;
                _node_684_ph_diff5__previous_correction_in = 0;
                _node_684_ph_diff5__phase_state = 0;
            }
            else {
                if(((_node_684_ph_diff5__filtered_in >= 0) && (_node_684_ph_diff5__previous_filtered_in < 0))) {
                    _node_684_ph_diff5__zc_flag_in[0] = 1;
                    _node_684_ph_diff5__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_684_ph_diff5__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_684_ph_diff5__zc_flag_ref) {
            _node_684_ph_diff5__correction_ref = ((- _node_684_ph_diff5__previous_filtered_ref) / ((_node_684_ph_diff5__filtered_ref - _node_684_ph_diff5__previous_filtered_ref)));
            _node_684_ph_diff5__sample_cnt_ref += ((_node_684_ph_diff5__correction_ref - _node_684_ph_diff5__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_684_ph_diff5__n_out_size; tmp2 += 1) {
                if((fabs(_node_684_ph_diff5__sample_cnt_ref) > 1e-06)) {
                    if((!_node_684_ph_diff5__no_zc_flag_in[0])) {
                        _node_684_ph_diff5__phase_state = ((360 * (((_node_684_ph_diff5__sample_cnt_in + _node_684_ph_diff5__correction_ref) - _node_684_ph_diff5__previous_correction_in))) / _node_684_ph_diff5__sample_cnt_ref);
                    }
                }
                if((fabs(_node_684_ph_diff5__phase_state) > 360)) {
                    _node_684_ph_diff5__phase_state = fmod(_node_684_ph_diff5__phase_state, 360);
                }
                if((_node_684_ph_diff5__phase_state < (- 180))) {
                    _node_684_ph_diff5__phase_state += 360;
                }
                if((_node_684_ph_diff5__phase_state > 180)) {
                    _node_684_ph_diff5__phase_state -= 360;
                }
            }
            _node_684_ph_diff5__sample_cnt_ref = 0;
            _node_684_ph_diff5__previous_correction_ref = _node_684_ph_diff5__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_684_ph_diff5__n_out_size; tmp3 += 1) {
            if(_node_684_ph_diff5__zc_flag_in[0]) {
                _node_684_ph_diff5__correction_in = ((- _node_684_ph_diff5__previous_filtered_in) / ((_node_684_ph_diff5__filtered_in - _node_684_ph_diff5__previous_filtered_in)));
                _node_684_ph_diff5__sample_cnt_in = 0;
                _node_684_ph_diff5__previous_correction_in = _node_684_ph_diff5__correction_in;
            }
        }
    }
    // Generated from the component: Node 692.I1.Ia1
    // Generated from the component: Node 692.I2.Ia1
    // Generated from the component: Node 692.I3.Ia1
    // Generated from the component: Node 692.ph_diff4
    {
        _node_692_ph_diff4__sample_cnt_ref += 1.0;
        _node_692_ph_diff4__previous_filtered_ref = _node_692_ph_diff4__filtered_ref;
        _node_692_ph_diff4__filtered_ref = ((_node_692_ph_diff4__previous_filtered_ref * _node_692_ph_diff4__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_692_ph_diff4__n_alpha[0]));
        if((_node_692_ph_diff4__sample_cnt_ref >= _node_692_ph_diff4__n_timeout[0])) {
            _node_692_ph_diff4__zc_flag_ref = 0;
            _node_692_ph_diff4__sample_cnt_ref = 0;
            _node_692_ph_diff4__previous_correction_ref = 0;
            _node_692_ph_diff4__phase_state = 0;
        }
        else {
            if(((_node_692_ph_diff4__filtered_ref >= 0) && (_node_692_ph_diff4__previous_filtered_ref < 0))) {
                _node_692_ph_diff4__zc_flag_ref = 1;
            }
            else {
                _node_692_ph_diff4__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_692_ph_diff4__n_out_size; tmp1 += 1) {
            _node_692_ph_diff4__sample_cnt_in += 1;
            _node_692_ph_diff4__previous_filtered_in = _node_692_ph_diff4__filtered_in;
            _node_692_ph_diff4__filtered_in = ((_node_692_ph_diff4__previous_filtered_in * _node_692_ph_diff4__n_one_minus_alpha[0]) + (_node_692_i3_ia1__out * _node_692_ph_diff4__n_alpha[0]));
            if((_node_692_ph_diff4__sample_cnt_in >= _node_692_ph_diff4__n_timeout[0])) {
                _node_692_ph_diff4__zc_flag_in[0] = 0;
                _node_692_ph_diff4__no_zc_flag_in[0] = 1;
                _node_692_ph_diff4__sample_cnt_in = 0;
                _node_692_ph_diff4__previous_correction_in = 0;
                _node_692_ph_diff4__phase_state = 0;
            }
            else {
                if(((_node_692_ph_diff4__filtered_in >= 0) && (_node_692_ph_diff4__previous_filtered_in < 0))) {
                    _node_692_ph_diff4__zc_flag_in[0] = 1;
                    _node_692_ph_diff4__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_692_ph_diff4__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_692_ph_diff4__zc_flag_ref) {
            _node_692_ph_diff4__correction_ref = ((- _node_692_ph_diff4__previous_filtered_ref) / ((_node_692_ph_diff4__filtered_ref - _node_692_ph_diff4__previous_filtered_ref)));
            _node_692_ph_diff4__sample_cnt_ref += ((_node_692_ph_diff4__correction_ref - _node_692_ph_diff4__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_692_ph_diff4__n_out_size; tmp2 += 1) {
                if((fabs(_node_692_ph_diff4__sample_cnt_ref) > 1e-06)) {
                    if((!_node_692_ph_diff4__no_zc_flag_in[0])) {
                        _node_692_ph_diff4__phase_state = ((360 * (((_node_692_ph_diff4__sample_cnt_in + _node_692_ph_diff4__correction_ref) - _node_692_ph_diff4__previous_correction_in))) / _node_692_ph_diff4__sample_cnt_ref);
                    }
                }
                if((fabs(_node_692_ph_diff4__phase_state) > 360)) {
                    _node_692_ph_diff4__phase_state = fmod(_node_692_ph_diff4__phase_state, 360);
                }
                if((_node_692_ph_diff4__phase_state < (- 180))) {
                    _node_692_ph_diff4__phase_state += 360;
                }
                if((_node_692_ph_diff4__phase_state > 180)) {
                    _node_692_ph_diff4__phase_state -= 360;
                }
            }
            _node_692_ph_diff4__sample_cnt_ref = 0;
            _node_692_ph_diff4__previous_correction_ref = _node_692_ph_diff4__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_692_ph_diff4__n_out_size; tmp3 += 1) {
            if(_node_692_ph_diff4__zc_flag_in[0]) {
                _node_692_ph_diff4__correction_in = ((- _node_692_ph_diff4__previous_filtered_in) / ((_node_692_ph_diff4__filtered_in - _node_692_ph_diff4__previous_filtered_in)));
                _node_692_ph_diff4__sample_cnt_in = 0;
                _node_692_ph_diff4__previous_correction_in = _node_692_ph_diff4__correction_in;
            }
        }
    }
    // Generated from the component: Node 692.ph_diff5
    {
        _node_692_ph_diff5__sample_cnt_ref += 1.0;
        _node_692_ph_diff5__previous_filtered_ref = _node_692_ph_diff5__filtered_ref;
        _node_692_ph_diff5__filtered_ref = ((_node_692_ph_diff5__previous_filtered_ref * _node_692_ph_diff5__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_692_ph_diff5__n_alpha[0]));
        if((_node_692_ph_diff5__sample_cnt_ref >= _node_692_ph_diff5__n_timeout[0])) {
            _node_692_ph_diff5__zc_flag_ref = 0;
            _node_692_ph_diff5__sample_cnt_ref = 0;
            _node_692_ph_diff5__previous_correction_ref = 0;
            _node_692_ph_diff5__phase_state = 0;
        }
        else {
            if(((_node_692_ph_diff5__filtered_ref >= 0) && (_node_692_ph_diff5__previous_filtered_ref < 0))) {
                _node_692_ph_diff5__zc_flag_ref = 1;
            }
            else {
                _node_692_ph_diff5__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_692_ph_diff5__n_out_size; tmp1 += 1) {
            _node_692_ph_diff5__sample_cnt_in += 1;
            _node_692_ph_diff5__previous_filtered_in = _node_692_ph_diff5__filtered_in;
            _node_692_ph_diff5__filtered_in = ((_node_692_ph_diff5__previous_filtered_in * _node_692_ph_diff5__n_one_minus_alpha[0]) + (_node_692_i1_ia1__out * _node_692_ph_diff5__n_alpha[0]));
            if((_node_692_ph_diff5__sample_cnt_in >= _node_692_ph_diff5__n_timeout[0])) {
                _node_692_ph_diff5__zc_flag_in[0] = 0;
                _node_692_ph_diff5__no_zc_flag_in[0] = 1;
                _node_692_ph_diff5__sample_cnt_in = 0;
                _node_692_ph_diff5__previous_correction_in = 0;
                _node_692_ph_diff5__phase_state = 0;
            }
            else {
                if(((_node_692_ph_diff5__filtered_in >= 0) && (_node_692_ph_diff5__previous_filtered_in < 0))) {
                    _node_692_ph_diff5__zc_flag_in[0] = 1;
                    _node_692_ph_diff5__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_692_ph_diff5__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_692_ph_diff5__zc_flag_ref) {
            _node_692_ph_diff5__correction_ref = ((- _node_692_ph_diff5__previous_filtered_ref) / ((_node_692_ph_diff5__filtered_ref - _node_692_ph_diff5__previous_filtered_ref)));
            _node_692_ph_diff5__sample_cnt_ref += ((_node_692_ph_diff5__correction_ref - _node_692_ph_diff5__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_692_ph_diff5__n_out_size; tmp2 += 1) {
                if((fabs(_node_692_ph_diff5__sample_cnt_ref) > 1e-06)) {
                    if((!_node_692_ph_diff5__no_zc_flag_in[0])) {
                        _node_692_ph_diff5__phase_state = ((360 * (((_node_692_ph_diff5__sample_cnt_in + _node_692_ph_diff5__correction_ref) - _node_692_ph_diff5__previous_correction_in))) / _node_692_ph_diff5__sample_cnt_ref);
                    }
                }
                if((fabs(_node_692_ph_diff5__phase_state) > 360)) {
                    _node_692_ph_diff5__phase_state = fmod(_node_692_ph_diff5__phase_state, 360);
                }
                if((_node_692_ph_diff5__phase_state < (- 180))) {
                    _node_692_ph_diff5__phase_state += 360;
                }
                if((_node_692_ph_diff5__phase_state > 180)) {
                    _node_692_ph_diff5__phase_state -= 360;
                }
            }
            _node_692_ph_diff5__sample_cnt_ref = 0;
            _node_692_ph_diff5__previous_correction_ref = _node_692_ph_diff5__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_692_ph_diff5__n_out_size; tmp3 += 1) {
            if(_node_692_ph_diff5__zc_flag_in[0]) {
                _node_692_ph_diff5__correction_in = ((- _node_692_ph_diff5__previous_filtered_in) / ((_node_692_ph_diff5__filtered_in - _node_692_ph_diff5__previous_filtered_in)));
                _node_692_ph_diff5__sample_cnt_in = 0;
                _node_692_ph_diff5__previous_correction_in = _node_692_ph_diff5__correction_in;
            }
        }
    }
    // Generated from the component: Node 692.ph_diff6
    {
        _node_692_ph_diff6__sample_cnt_ref += 1.0;
        _node_692_ph_diff6__previous_filtered_ref = _node_692_ph_diff6__filtered_ref;
        _node_692_ph_diff6__filtered_ref = ((_node_692_ph_diff6__previous_filtered_ref * _node_692_ph_diff6__n_one_minus_alpha[0]) + (_reference_v1_ref2_va1__out * _node_692_ph_diff6__n_alpha[0]));
        if((_node_692_ph_diff6__sample_cnt_ref >= _node_692_ph_diff6__n_timeout[0])) {
            _node_692_ph_diff6__zc_flag_ref = 0;
            _node_692_ph_diff6__sample_cnt_ref = 0;
            _node_692_ph_diff6__previous_correction_ref = 0;
            _node_692_ph_diff6__phase_state = 0;
        }
        else {
            if(((_node_692_ph_diff6__filtered_ref >= 0) && (_node_692_ph_diff6__previous_filtered_ref < 0))) {
                _node_692_ph_diff6__zc_flag_ref = 1;
            }
            else {
                _node_692_ph_diff6__zc_flag_ref = 0;
            }
        }
        int tmp1;
        for(tmp1 = 0; tmp1 < _node_692_ph_diff6__n_out_size; tmp1 += 1) {
            _node_692_ph_diff6__sample_cnt_in += 1;
            _node_692_ph_diff6__previous_filtered_in = _node_692_ph_diff6__filtered_in;
            _node_692_ph_diff6__filtered_in = ((_node_692_ph_diff6__previous_filtered_in * _node_692_ph_diff6__n_one_minus_alpha[0]) + (_node_692_i2_ia1__out * _node_692_ph_diff6__n_alpha[0]));
            if((_node_692_ph_diff6__sample_cnt_in >= _node_692_ph_diff6__n_timeout[0])) {
                _node_692_ph_diff6__zc_flag_in[0] = 0;
                _node_692_ph_diff6__no_zc_flag_in[0] = 1;
                _node_692_ph_diff6__sample_cnt_in = 0;
                _node_692_ph_diff6__previous_correction_in = 0;
                _node_692_ph_diff6__phase_state = 0;
            }
            else {
                if(((_node_692_ph_diff6__filtered_in >= 0) && (_node_692_ph_diff6__previous_filtered_in < 0))) {
                    _node_692_ph_diff6__zc_flag_in[0] = 1;
                    _node_692_ph_diff6__no_zc_flag_in[0] = 0;
                }
                else {
                    _node_692_ph_diff6__zc_flag_in[0] = 0;
                }
            }
        }
        if(_node_692_ph_diff6__zc_flag_ref) {
            _node_692_ph_diff6__correction_ref = ((- _node_692_ph_diff6__previous_filtered_ref) / ((_node_692_ph_diff6__filtered_ref - _node_692_ph_diff6__previous_filtered_ref)));
            _node_692_ph_diff6__sample_cnt_ref += ((_node_692_ph_diff6__correction_ref - _node_692_ph_diff6__previous_correction_ref));
            int tmp2;
            for(tmp2 = 0; tmp2 < _node_692_ph_diff6__n_out_size; tmp2 += 1) {
                if((fabs(_node_692_ph_diff6__sample_cnt_ref) > 1e-06)) {
                    if((!_node_692_ph_diff6__no_zc_flag_in[0])) {
                        _node_692_ph_diff6__phase_state = ((360 * (((_node_692_ph_diff6__sample_cnt_in + _node_692_ph_diff6__correction_ref) - _node_692_ph_diff6__previous_correction_in))) / _node_692_ph_diff6__sample_cnt_ref);
                    }
                }
                if((fabs(_node_692_ph_diff6__phase_state) > 360)) {
                    _node_692_ph_diff6__phase_state = fmod(_node_692_ph_diff6__phase_state, 360);
                }
                if((_node_692_ph_diff6__phase_state < (- 180))) {
                    _node_692_ph_diff6__phase_state += 360;
                }
                if((_node_692_ph_diff6__phase_state > 180)) {
                    _node_692_ph_diff6__phase_state -= 360;
                }
            }
            _node_692_ph_diff6__sample_cnt_ref = 0;
            _node_692_ph_diff6__previous_correction_ref = _node_692_ph_diff6__correction_ref;
        }
        int tmp3;
        for(tmp3 = 0; tmp3 < _node_692_ph_diff6__n_out_size; tmp3 += 1) {
            if(_node_692_ph_diff6__zc_flag_in[0]) {
                _node_692_ph_diff6__correction_in = ((- _node_692_ph_diff6__previous_filtered_in) / ((_node_692_ph_diff6__filtered_in - _node_692_ph_diff6__previous_filtered_in)));
                _node_692_ph_diff6__sample_cnt_in = 0;
                _node_692_ph_diff6__previous_correction_in = _node_692_ph_diff6__correction_in;
            }
        }
    }
    // Generated from the component: Reference.V1_REF2.Va1
    // Generated from the component: MSR 632-671.RMS6
    if( _msr_632_671_rms6__zc ) {
        if (_msr_632_671_i1_ia1__out != _msr_632_671_rms6__previous_value)
            _msr_632_671_rms6__correction = - _msr_632_671_rms6__previous_value / (_msr_632_671_i1_ia1__out - _msr_632_671_rms6__previous_value);
        if (_msr_632_671_rms6__correction < 0)
            _msr_632_671_rms6__correction = 0;
        else
            _msr_632_671_rms6__correction = 0;
        _msr_632_671_rms6__sample_cnt += _msr_632_671_rms6__correction - _msr_632_671_rms6__previous_correction;
        _msr_632_671_rms6__out_state = sqrt(_msr_632_671_rms6__square_sum / _msr_632_671_rms6__sample_cnt);
        _msr_632_671_rms6__sample_cnt = 0;
        _msr_632_671_rms6__previous_correction = _msr_632_671_rms6__correction;
        _msr_632_671_rms6__square_sum = 0;
    } else if ( _msr_632_671_rms6__sample_cnt >= 2778 ) {
        _msr_632_671_rms6__out_state = sqrt(_msr_632_671_rms6__square_sum / _msr_632_671_rms6__sample_cnt);
        _msr_632_671_rms6__sample_cnt = 0;
        _msr_632_671_rms6__square_sum = 0;
    }
    _msr_632_671_rms6__previous_value = _msr_632_671_i1_ia1__out;
    _msr_632_671_rms6__square_sum += _msr_632_671_i1_ia1__out * _msr_632_671_i1_ia1__out;
    _msr_632_671_rms6__sample_cnt ++;
    // Generated from the component: MSR 632-671.RMS5
    if( _msr_632_671_rms5__zc ) {
        if (_msr_632_671_i2_ia1__out != _msr_632_671_rms5__previous_value)
            _msr_632_671_rms5__correction = - _msr_632_671_rms5__previous_value / (_msr_632_671_i2_ia1__out - _msr_632_671_rms5__previous_value);
        if (_msr_632_671_rms5__correction < 0)
            _msr_632_671_rms5__correction = 0;
        else
            _msr_632_671_rms5__correction = 0;
        _msr_632_671_rms5__sample_cnt += _msr_632_671_rms5__correction - _msr_632_671_rms5__previous_correction;
        _msr_632_671_rms5__out_state = sqrt(_msr_632_671_rms5__square_sum / _msr_632_671_rms5__sample_cnt);
        _msr_632_671_rms5__sample_cnt = 0;
        _msr_632_671_rms5__previous_correction = _msr_632_671_rms5__correction;
        _msr_632_671_rms5__square_sum = 0;
    } else if ( _msr_632_671_rms5__sample_cnt >= 2778 ) {
        _msr_632_671_rms5__out_state = sqrt(_msr_632_671_rms5__square_sum / _msr_632_671_rms5__sample_cnt);
        _msr_632_671_rms5__sample_cnt = 0;
        _msr_632_671_rms5__square_sum = 0;
    }
    _msr_632_671_rms5__previous_value = _msr_632_671_i2_ia1__out;
    _msr_632_671_rms5__square_sum += _msr_632_671_i2_ia1__out * _msr_632_671_i2_ia1__out;
    _msr_632_671_rms5__sample_cnt ++;
    // Generated from the component: MSR 632-671.RMS4
    if( _msr_632_671_rms4__zc ) {
        if (_msr_632_671_i3_ia1__out != _msr_632_671_rms4__previous_value)
            _msr_632_671_rms4__correction = - _msr_632_671_rms4__previous_value / (_msr_632_671_i3_ia1__out - _msr_632_671_rms4__previous_value);
        if (_msr_632_671_rms4__correction < 0)
            _msr_632_671_rms4__correction = 0;
        else
            _msr_632_671_rms4__correction = 0;
        _msr_632_671_rms4__sample_cnt += _msr_632_671_rms4__correction - _msr_632_671_rms4__previous_correction;
        _msr_632_671_rms4__out_state = sqrt(_msr_632_671_rms4__square_sum / _msr_632_671_rms4__sample_cnt);
        _msr_632_671_rms4__sample_cnt = 0;
        _msr_632_671_rms4__previous_correction = _msr_632_671_rms4__correction;
        _msr_632_671_rms4__square_sum = 0;
    } else if ( _msr_632_671_rms4__sample_cnt >= 2778 ) {
        _msr_632_671_rms4__out_state = sqrt(_msr_632_671_rms4__square_sum / _msr_632_671_rms4__sample_cnt);
        _msr_632_671_rms4__sample_cnt = 0;
        _msr_632_671_rms4__square_sum = 0;
    }
    _msr_632_671_rms4__previous_value = _msr_632_671_i3_ia1__out;
    _msr_632_671_rms4__square_sum += _msr_632_671_i3_ia1__out * _msr_632_671_i3_ia1__out;
    _msr_632_671_rms4__sample_cnt ++;
    // Generated from the component: MSR 632-671.I3_phase
    // Generated from the component: MSR 632-671.I1_phase
    // Generated from the component: MSR 632-671.I2_phase
    // Generated from the component: Node 611.RMS4
    if( _node_611_rms4__zc ) {
        if (_node_611_i3_ia1__out != _node_611_rms4__previous_value)
            _node_611_rms4__correction = - _node_611_rms4__previous_value / (_node_611_i3_ia1__out - _node_611_rms4__previous_value);
        if (_node_611_rms4__correction < 0)
            _node_611_rms4__correction = 0;
        else
            _node_611_rms4__correction = 0;
        _node_611_rms4__sample_cnt += _node_611_rms4__correction - _node_611_rms4__previous_correction;
        _node_611_rms4__out_state = sqrt(_node_611_rms4__square_sum / _node_611_rms4__sample_cnt);
        _node_611_rms4__sample_cnt = 0;
        _node_611_rms4__previous_correction = _node_611_rms4__correction;
        _node_611_rms4__square_sum = 0;
    } else if ( _node_611_rms4__sample_cnt >= 2778 ) {
        _node_611_rms4__out_state = sqrt(_node_611_rms4__square_sum / _node_611_rms4__sample_cnt);
        _node_611_rms4__sample_cnt = 0;
        _node_611_rms4__square_sum = 0;
    }
    _node_611_rms4__previous_value = _node_611_i3_ia1__out;
    _node_611_rms4__square_sum += _node_611_i3_ia1__out * _node_611_i3_ia1__out;
    _node_611_rms4__sample_cnt ++;
    // Generated from the component: Node 611.I3_phase
    // Generated from the component: Node 632.RMS6
    if( _node_632_rms6__zc ) {
        if (_node_632_i1_ia1__out != _node_632_rms6__previous_value)
            _node_632_rms6__correction = - _node_632_rms6__previous_value / (_node_632_i1_ia1__out - _node_632_rms6__previous_value);
        if (_node_632_rms6__correction < 0)
            _node_632_rms6__correction = 0;
        else
            _node_632_rms6__correction = 0;
        _node_632_rms6__sample_cnt += _node_632_rms6__correction - _node_632_rms6__previous_correction;
        _node_632_rms6__out_state = sqrt(_node_632_rms6__square_sum / _node_632_rms6__sample_cnt);
        _node_632_rms6__sample_cnt = 0;
        _node_632_rms6__previous_correction = _node_632_rms6__correction;
        _node_632_rms6__square_sum = 0;
    } else if ( _node_632_rms6__sample_cnt >= 2778 ) {
        _node_632_rms6__out_state = sqrt(_node_632_rms6__square_sum / _node_632_rms6__sample_cnt);
        _node_632_rms6__sample_cnt = 0;
        _node_632_rms6__square_sum = 0;
    }
    _node_632_rms6__previous_value = _node_632_i1_ia1__out;
    _node_632_rms6__square_sum += _node_632_i1_ia1__out * _node_632_i1_ia1__out;
    _node_632_rms6__sample_cnt ++;
    // Generated from the component: Node 632.RMS5
    if( _node_632_rms5__zc ) {
        if (_node_632_i2_ia1__out != _node_632_rms5__previous_value)
            _node_632_rms5__correction = - _node_632_rms5__previous_value / (_node_632_i2_ia1__out - _node_632_rms5__previous_value);
        if (_node_632_rms5__correction < 0)
            _node_632_rms5__correction = 0;
        else
            _node_632_rms5__correction = 0;
        _node_632_rms5__sample_cnt += _node_632_rms5__correction - _node_632_rms5__previous_correction;
        _node_632_rms5__out_state = sqrt(_node_632_rms5__square_sum / _node_632_rms5__sample_cnt);
        _node_632_rms5__sample_cnt = 0;
        _node_632_rms5__previous_correction = _node_632_rms5__correction;
        _node_632_rms5__square_sum = 0;
    } else if ( _node_632_rms5__sample_cnt >= 2778 ) {
        _node_632_rms5__out_state = sqrt(_node_632_rms5__square_sum / _node_632_rms5__sample_cnt);
        _node_632_rms5__sample_cnt = 0;
        _node_632_rms5__square_sum = 0;
    }
    _node_632_rms5__previous_value = _node_632_i2_ia1__out;
    _node_632_rms5__square_sum += _node_632_i2_ia1__out * _node_632_i2_ia1__out;
    _node_632_rms5__sample_cnt ++;
    // Generated from the component: Node 632.RMS4
    if( _node_632_rms4__zc ) {
        if (_node_632_i3_ia1__out != _node_632_rms4__previous_value)
            _node_632_rms4__correction = - _node_632_rms4__previous_value / (_node_632_i3_ia1__out - _node_632_rms4__previous_value);
        if (_node_632_rms4__correction < 0)
            _node_632_rms4__correction = 0;
        else
            _node_632_rms4__correction = 0;
        _node_632_rms4__sample_cnt += _node_632_rms4__correction - _node_632_rms4__previous_correction;
        _node_632_rms4__out_state = sqrt(_node_632_rms4__square_sum / _node_632_rms4__sample_cnt);
        _node_632_rms4__sample_cnt = 0;
        _node_632_rms4__previous_correction = _node_632_rms4__correction;
        _node_632_rms4__square_sum = 0;
    } else if ( _node_632_rms4__sample_cnt >= 2778 ) {
        _node_632_rms4__out_state = sqrt(_node_632_rms4__square_sum / _node_632_rms4__sample_cnt);
        _node_632_rms4__sample_cnt = 0;
        _node_632_rms4__square_sum = 0;
    }
    _node_632_rms4__previous_value = _node_632_i3_ia1__out;
    _node_632_rms4__square_sum += _node_632_i3_ia1__out * _node_632_i3_ia1__out;
    _node_632_rms4__sample_cnt ++;
    // Generated from the component: Node 632.I3_phase
    // Generated from the component: Node 632.I1_phase
    // Generated from the component: Node 632.I2_phase
    // Generated from the component: Node 633.RMS6
    if( _node_633_rms6__zc ) {
        if (_node_633_i1_ia1__out != _node_633_rms6__previous_value)
            _node_633_rms6__correction = - _node_633_rms6__previous_value / (_node_633_i1_ia1__out - _node_633_rms6__previous_value);
        if (_node_633_rms6__correction < 0)
            _node_633_rms6__correction = 0;
        else
            _node_633_rms6__correction = 0;
        _node_633_rms6__sample_cnt += _node_633_rms6__correction - _node_633_rms6__previous_correction;
        _node_633_rms6__out_state = sqrt(_node_633_rms6__square_sum / _node_633_rms6__sample_cnt);
        _node_633_rms6__sample_cnt = 0;
        _node_633_rms6__previous_correction = _node_633_rms6__correction;
        _node_633_rms6__square_sum = 0;
    } else if ( _node_633_rms6__sample_cnt >= 2778 ) {
        _node_633_rms6__out_state = sqrt(_node_633_rms6__square_sum / _node_633_rms6__sample_cnt);
        _node_633_rms6__sample_cnt = 0;
        _node_633_rms6__square_sum = 0;
    }
    _node_633_rms6__previous_value = _node_633_i1_ia1__out;
    _node_633_rms6__square_sum += _node_633_i1_ia1__out * _node_633_i1_ia1__out;
    _node_633_rms6__sample_cnt ++;
    // Generated from the component: Node 633.RMS5
    if( _node_633_rms5__zc ) {
        if (_node_633_i2_ia1__out != _node_633_rms5__previous_value)
            _node_633_rms5__correction = - _node_633_rms5__previous_value / (_node_633_i2_ia1__out - _node_633_rms5__previous_value);
        if (_node_633_rms5__correction < 0)
            _node_633_rms5__correction = 0;
        else
            _node_633_rms5__correction = 0;
        _node_633_rms5__sample_cnt += _node_633_rms5__correction - _node_633_rms5__previous_correction;
        _node_633_rms5__out_state = sqrt(_node_633_rms5__square_sum / _node_633_rms5__sample_cnt);
        _node_633_rms5__sample_cnt = 0;
        _node_633_rms5__previous_correction = _node_633_rms5__correction;
        _node_633_rms5__square_sum = 0;
    } else if ( _node_633_rms5__sample_cnt >= 2778 ) {
        _node_633_rms5__out_state = sqrt(_node_633_rms5__square_sum / _node_633_rms5__sample_cnt);
        _node_633_rms5__sample_cnt = 0;
        _node_633_rms5__square_sum = 0;
    }
    _node_633_rms5__previous_value = _node_633_i2_ia1__out;
    _node_633_rms5__square_sum += _node_633_i2_ia1__out * _node_633_i2_ia1__out;
    _node_633_rms5__sample_cnt ++;
    // Generated from the component: Node 633.RMS4
    if( _node_633_rms4__zc ) {
        if (_node_633_i3_ia1__out != _node_633_rms4__previous_value)
            _node_633_rms4__correction = - _node_633_rms4__previous_value / (_node_633_i3_ia1__out - _node_633_rms4__previous_value);
        if (_node_633_rms4__correction < 0)
            _node_633_rms4__correction = 0;
        else
            _node_633_rms4__correction = 0;
        _node_633_rms4__sample_cnt += _node_633_rms4__correction - _node_633_rms4__previous_correction;
        _node_633_rms4__out_state = sqrt(_node_633_rms4__square_sum / _node_633_rms4__sample_cnt);
        _node_633_rms4__sample_cnt = 0;
        _node_633_rms4__previous_correction = _node_633_rms4__correction;
        _node_633_rms4__square_sum = 0;
    } else if ( _node_633_rms4__sample_cnt >= 2778 ) {
        _node_633_rms4__out_state = sqrt(_node_633_rms4__square_sum / _node_633_rms4__sample_cnt);
        _node_633_rms4__sample_cnt = 0;
        _node_633_rms4__square_sum = 0;
    }
    _node_633_rms4__previous_value = _node_633_i3_ia1__out;
    _node_633_rms4__square_sum += _node_633_i3_ia1__out * _node_633_i3_ia1__out;
    _node_633_rms4__sample_cnt ++;
    // Generated from the component: Node 633.I3_phase
    // Generated from the component: Node 633.I1_phase
    // Generated from the component: Node 633.I2_phase
    // Generated from the component: Node 634.RMS6
    if( _node_634_rms6__zc ) {
        if (_node_634_i1_ia1__out != _node_634_rms6__previous_value)
            _node_634_rms6__correction = - _node_634_rms6__previous_value / (_node_634_i1_ia1__out - _node_634_rms6__previous_value);
        if (_node_634_rms6__correction < 0)
            _node_634_rms6__correction = 0;
        else
            _node_634_rms6__correction = 0;
        _node_634_rms6__sample_cnt += _node_634_rms6__correction - _node_634_rms6__previous_correction;
        _node_634_rms6__out_state = sqrt(_node_634_rms6__square_sum / _node_634_rms6__sample_cnt);
        _node_634_rms6__sample_cnt = 0;
        _node_634_rms6__previous_correction = _node_634_rms6__correction;
        _node_634_rms6__square_sum = 0;
    } else if ( _node_634_rms6__sample_cnt >= 2778 ) {
        _node_634_rms6__out_state = sqrt(_node_634_rms6__square_sum / _node_634_rms6__sample_cnt);
        _node_634_rms6__sample_cnt = 0;
        _node_634_rms6__square_sum = 0;
    }
    _node_634_rms6__previous_value = _node_634_i1_ia1__out;
    _node_634_rms6__square_sum += _node_634_i1_ia1__out * _node_634_i1_ia1__out;
    _node_634_rms6__sample_cnt ++;
    // Generated from the component: Node 634.RMS5
    if( _node_634_rms5__zc ) {
        if (_node_634_i2_ia1__out != _node_634_rms5__previous_value)
            _node_634_rms5__correction = - _node_634_rms5__previous_value / (_node_634_i2_ia1__out - _node_634_rms5__previous_value);
        if (_node_634_rms5__correction < 0)
            _node_634_rms5__correction = 0;
        else
            _node_634_rms5__correction = 0;
        _node_634_rms5__sample_cnt += _node_634_rms5__correction - _node_634_rms5__previous_correction;
        _node_634_rms5__out_state = sqrt(_node_634_rms5__square_sum / _node_634_rms5__sample_cnt);
        _node_634_rms5__sample_cnt = 0;
        _node_634_rms5__previous_correction = _node_634_rms5__correction;
        _node_634_rms5__square_sum = 0;
    } else if ( _node_634_rms5__sample_cnt >= 2778 ) {
        _node_634_rms5__out_state = sqrt(_node_634_rms5__square_sum / _node_634_rms5__sample_cnt);
        _node_634_rms5__sample_cnt = 0;
        _node_634_rms5__square_sum = 0;
    }
    _node_634_rms5__previous_value = _node_634_i2_ia1__out;
    _node_634_rms5__square_sum += _node_634_i2_ia1__out * _node_634_i2_ia1__out;
    _node_634_rms5__sample_cnt ++;
    // Generated from the component: Node 634.RMS4
    if( _node_634_rms4__zc ) {
        if (_node_634_i3_ia1__out != _node_634_rms4__previous_value)
            _node_634_rms4__correction = - _node_634_rms4__previous_value / (_node_634_i3_ia1__out - _node_634_rms4__previous_value);
        if (_node_634_rms4__correction < 0)
            _node_634_rms4__correction = 0;
        else
            _node_634_rms4__correction = 0;
        _node_634_rms4__sample_cnt += _node_634_rms4__correction - _node_634_rms4__previous_correction;
        _node_634_rms4__out_state = sqrt(_node_634_rms4__square_sum / _node_634_rms4__sample_cnt);
        _node_634_rms4__sample_cnt = 0;
        _node_634_rms4__previous_correction = _node_634_rms4__correction;
        _node_634_rms4__square_sum = 0;
    } else if ( _node_634_rms4__sample_cnt >= 2778 ) {
        _node_634_rms4__out_state = sqrt(_node_634_rms4__square_sum / _node_634_rms4__sample_cnt);
        _node_634_rms4__sample_cnt = 0;
        _node_634_rms4__square_sum = 0;
    }
    _node_634_rms4__previous_value = _node_634_i3_ia1__out;
    _node_634_rms4__square_sum += _node_634_i3_ia1__out * _node_634_i3_ia1__out;
    _node_634_rms4__sample_cnt ++;
    // Generated from the component: Node 634.I3_phase
    // Generated from the component: Node 634.I1_phase
    // Generated from the component: Node 634.I2_phase
    // Generated from the component: Node 645.RMS5
    if( _node_645_rms5__zc ) {
        if (_node_645_i2_ia1__out != _node_645_rms5__previous_value)
            _node_645_rms5__correction = - _node_645_rms5__previous_value / (_node_645_i2_ia1__out - _node_645_rms5__previous_value);
        if (_node_645_rms5__correction < 0)
            _node_645_rms5__correction = 0;
        else
            _node_645_rms5__correction = 0;
        _node_645_rms5__sample_cnt += _node_645_rms5__correction - _node_645_rms5__previous_correction;
        _node_645_rms5__out_state = sqrt(_node_645_rms5__square_sum / _node_645_rms5__sample_cnt);
        _node_645_rms5__sample_cnt = 0;
        _node_645_rms5__previous_correction = _node_645_rms5__correction;
        _node_645_rms5__square_sum = 0;
    } else if ( _node_645_rms5__sample_cnt >= 2778 ) {
        _node_645_rms5__out_state = sqrt(_node_645_rms5__square_sum / _node_645_rms5__sample_cnt);
        _node_645_rms5__sample_cnt = 0;
        _node_645_rms5__square_sum = 0;
    }
    _node_645_rms5__previous_value = _node_645_i2_ia1__out;
    _node_645_rms5__square_sum += _node_645_i2_ia1__out * _node_645_i2_ia1__out;
    _node_645_rms5__sample_cnt ++;
    // Generated from the component: Node 645.RMS4
    if( _node_645_rms4__zc ) {
        if (_node_645_i3_ia1__out != _node_645_rms4__previous_value)
            _node_645_rms4__correction = - _node_645_rms4__previous_value / (_node_645_i3_ia1__out - _node_645_rms4__previous_value);
        if (_node_645_rms4__correction < 0)
            _node_645_rms4__correction = 0;
        else
            _node_645_rms4__correction = 0;
        _node_645_rms4__sample_cnt += _node_645_rms4__correction - _node_645_rms4__previous_correction;
        _node_645_rms4__out_state = sqrt(_node_645_rms4__square_sum / _node_645_rms4__sample_cnt);
        _node_645_rms4__sample_cnt = 0;
        _node_645_rms4__previous_correction = _node_645_rms4__correction;
        _node_645_rms4__square_sum = 0;
    } else if ( _node_645_rms4__sample_cnt >= 2778 ) {
        _node_645_rms4__out_state = sqrt(_node_645_rms4__square_sum / _node_645_rms4__sample_cnt);
        _node_645_rms4__sample_cnt = 0;
        _node_645_rms4__square_sum = 0;
    }
    _node_645_rms4__previous_value = _node_645_i3_ia1__out;
    _node_645_rms4__square_sum += _node_645_i3_ia1__out * _node_645_i3_ia1__out;
    _node_645_rms4__sample_cnt ++;
    // Generated from the component: Node 645.I3_phase
    // Generated from the component: Node 645.I2_phase
    // Generated from the component: Node 646.RMS5
    if( _node_646_rms5__zc ) {
        if (_node_646_i2_ia1__out != _node_646_rms5__previous_value)
            _node_646_rms5__correction = - _node_646_rms5__previous_value / (_node_646_i2_ia1__out - _node_646_rms5__previous_value);
        if (_node_646_rms5__correction < 0)
            _node_646_rms5__correction = 0;
        else
            _node_646_rms5__correction = 0;
        _node_646_rms5__sample_cnt += _node_646_rms5__correction - _node_646_rms5__previous_correction;
        _node_646_rms5__out_state = sqrt(_node_646_rms5__square_sum / _node_646_rms5__sample_cnt);
        _node_646_rms5__sample_cnt = 0;
        _node_646_rms5__previous_correction = _node_646_rms5__correction;
        _node_646_rms5__square_sum = 0;
    } else if ( _node_646_rms5__sample_cnt >= 2778 ) {
        _node_646_rms5__out_state = sqrt(_node_646_rms5__square_sum / _node_646_rms5__sample_cnt);
        _node_646_rms5__sample_cnt = 0;
        _node_646_rms5__square_sum = 0;
    }
    _node_646_rms5__previous_value = _node_646_i2_ia1__out;
    _node_646_rms5__square_sum += _node_646_i2_ia1__out * _node_646_i2_ia1__out;
    _node_646_rms5__sample_cnt ++;
    // Generated from the component: Node 646.RMS4
    if( _node_646_rms4__zc ) {
        if (_node_646_i3_ia1__out != _node_646_rms4__previous_value)
            _node_646_rms4__correction = - _node_646_rms4__previous_value / (_node_646_i3_ia1__out - _node_646_rms4__previous_value);
        if (_node_646_rms4__correction < 0)
            _node_646_rms4__correction = 0;
        else
            _node_646_rms4__correction = 0;
        _node_646_rms4__sample_cnt += _node_646_rms4__correction - _node_646_rms4__previous_correction;
        _node_646_rms4__out_state = sqrt(_node_646_rms4__square_sum / _node_646_rms4__sample_cnt);
        _node_646_rms4__sample_cnt = 0;
        _node_646_rms4__previous_correction = _node_646_rms4__correction;
        _node_646_rms4__square_sum = 0;
    } else if ( _node_646_rms4__sample_cnt >= 2778 ) {
        _node_646_rms4__out_state = sqrt(_node_646_rms4__square_sum / _node_646_rms4__sample_cnt);
        _node_646_rms4__sample_cnt = 0;
        _node_646_rms4__square_sum = 0;
    }
    _node_646_rms4__previous_value = _node_646_i3_ia1__out;
    _node_646_rms4__square_sum += _node_646_i3_ia1__out * _node_646_i3_ia1__out;
    _node_646_rms4__sample_cnt ++;
    // Generated from the component: Node 646.I3_phase
    // Generated from the component: Node 646.I2_phase
    // Generated from the component: Node 652.RMS6
    if( _node_652_rms6__zc ) {
        if (_node_652_i1_ia1__out != _node_652_rms6__previous_value)
            _node_652_rms6__correction = - _node_652_rms6__previous_value / (_node_652_i1_ia1__out - _node_652_rms6__previous_value);
        if (_node_652_rms6__correction < 0)
            _node_652_rms6__correction = 0;
        else
            _node_652_rms6__correction = 0;
        _node_652_rms6__sample_cnt += _node_652_rms6__correction - _node_652_rms6__previous_correction;
        _node_652_rms6__out_state = sqrt(_node_652_rms6__square_sum / _node_652_rms6__sample_cnt);
        _node_652_rms6__sample_cnt = 0;
        _node_652_rms6__previous_correction = _node_652_rms6__correction;
        _node_652_rms6__square_sum = 0;
    } else if ( _node_652_rms6__sample_cnt >= 2778 ) {
        _node_652_rms6__out_state = sqrt(_node_652_rms6__square_sum / _node_652_rms6__sample_cnt);
        _node_652_rms6__sample_cnt = 0;
        _node_652_rms6__square_sum = 0;
    }
    _node_652_rms6__previous_value = _node_652_i1_ia1__out;
    _node_652_rms6__square_sum += _node_652_i1_ia1__out * _node_652_i1_ia1__out;
    _node_652_rms6__sample_cnt ++;
    // Generated from the component: Node 652.I1_phase
    // Generated from the component: Node 671.RMS6
    if( _node_671_rms6__zc ) {
        if (_node_671_i1_ia1__out != _node_671_rms6__previous_value)
            _node_671_rms6__correction = - _node_671_rms6__previous_value / (_node_671_i1_ia1__out - _node_671_rms6__previous_value);
        if (_node_671_rms6__correction < 0)
            _node_671_rms6__correction = 0;
        else
            _node_671_rms6__correction = 0;
        _node_671_rms6__sample_cnt += _node_671_rms6__correction - _node_671_rms6__previous_correction;
        _node_671_rms6__out_state = sqrt(_node_671_rms6__square_sum / _node_671_rms6__sample_cnt);
        _node_671_rms6__sample_cnt = 0;
        _node_671_rms6__previous_correction = _node_671_rms6__correction;
        _node_671_rms6__square_sum = 0;
    } else if ( _node_671_rms6__sample_cnt >= 2778 ) {
        _node_671_rms6__out_state = sqrt(_node_671_rms6__square_sum / _node_671_rms6__sample_cnt);
        _node_671_rms6__sample_cnt = 0;
        _node_671_rms6__square_sum = 0;
    }
    _node_671_rms6__previous_value = _node_671_i1_ia1__out;
    _node_671_rms6__square_sum += _node_671_i1_ia1__out * _node_671_i1_ia1__out;
    _node_671_rms6__sample_cnt ++;
    // Generated from the component: Node 671.RMS5
    if( _node_671_rms5__zc ) {
        if (_node_671_i2_ia1__out != _node_671_rms5__previous_value)
            _node_671_rms5__correction = - _node_671_rms5__previous_value / (_node_671_i2_ia1__out - _node_671_rms5__previous_value);
        if (_node_671_rms5__correction < 0)
            _node_671_rms5__correction = 0;
        else
            _node_671_rms5__correction = 0;
        _node_671_rms5__sample_cnt += _node_671_rms5__correction - _node_671_rms5__previous_correction;
        _node_671_rms5__out_state = sqrt(_node_671_rms5__square_sum / _node_671_rms5__sample_cnt);
        _node_671_rms5__sample_cnt = 0;
        _node_671_rms5__previous_correction = _node_671_rms5__correction;
        _node_671_rms5__square_sum = 0;
    } else if ( _node_671_rms5__sample_cnt >= 2778 ) {
        _node_671_rms5__out_state = sqrt(_node_671_rms5__square_sum / _node_671_rms5__sample_cnt);
        _node_671_rms5__sample_cnt = 0;
        _node_671_rms5__square_sum = 0;
    }
    _node_671_rms5__previous_value = _node_671_i2_ia1__out;
    _node_671_rms5__square_sum += _node_671_i2_ia1__out * _node_671_i2_ia1__out;
    _node_671_rms5__sample_cnt ++;
    // Generated from the component: Node 671.RMS4
    if( _node_671_rms4__zc ) {
        if (_node_671_i3_ia1__out != _node_671_rms4__previous_value)
            _node_671_rms4__correction = - _node_671_rms4__previous_value / (_node_671_i3_ia1__out - _node_671_rms4__previous_value);
        if (_node_671_rms4__correction < 0)
            _node_671_rms4__correction = 0;
        else
            _node_671_rms4__correction = 0;
        _node_671_rms4__sample_cnt += _node_671_rms4__correction - _node_671_rms4__previous_correction;
        _node_671_rms4__out_state = sqrt(_node_671_rms4__square_sum / _node_671_rms4__sample_cnt);
        _node_671_rms4__sample_cnt = 0;
        _node_671_rms4__previous_correction = _node_671_rms4__correction;
        _node_671_rms4__square_sum = 0;
    } else if ( _node_671_rms4__sample_cnt >= 2778 ) {
        _node_671_rms4__out_state = sqrt(_node_671_rms4__square_sum / _node_671_rms4__sample_cnt);
        _node_671_rms4__sample_cnt = 0;
        _node_671_rms4__square_sum = 0;
    }
    _node_671_rms4__previous_value = _node_671_i3_ia1__out;
    _node_671_rms4__square_sum += _node_671_i3_ia1__out * _node_671_i3_ia1__out;
    _node_671_rms4__sample_cnt ++;
    // Generated from the component: Node 671.I3_phase
    // Generated from the component: Node 671.I1_phase
    // Generated from the component: Node 671.I2_phase
    // Generated from the component: Node 675.RMS6
    if( _node_675_rms6__zc ) {
        if (_node_675_i1_ia1__out != _node_675_rms6__previous_value)
            _node_675_rms6__correction = - _node_675_rms6__previous_value / (_node_675_i1_ia1__out - _node_675_rms6__previous_value);
        if (_node_675_rms6__correction < 0)
            _node_675_rms6__correction = 0;
        else
            _node_675_rms6__correction = 0;
        _node_675_rms6__sample_cnt += _node_675_rms6__correction - _node_675_rms6__previous_correction;
        _node_675_rms6__out_state = sqrt(_node_675_rms6__square_sum / _node_675_rms6__sample_cnt);
        _node_675_rms6__sample_cnt = 0;
        _node_675_rms6__previous_correction = _node_675_rms6__correction;
        _node_675_rms6__square_sum = 0;
    } else if ( _node_675_rms6__sample_cnt >= 2778 ) {
        _node_675_rms6__out_state = sqrt(_node_675_rms6__square_sum / _node_675_rms6__sample_cnt);
        _node_675_rms6__sample_cnt = 0;
        _node_675_rms6__square_sum = 0;
    }
    _node_675_rms6__previous_value = _node_675_i1_ia1__out;
    _node_675_rms6__square_sum += _node_675_i1_ia1__out * _node_675_i1_ia1__out;
    _node_675_rms6__sample_cnt ++;
    // Generated from the component: Node 675.RMS5
    if( _node_675_rms5__zc ) {
        if (_node_675_i2_ia1__out != _node_675_rms5__previous_value)
            _node_675_rms5__correction = - _node_675_rms5__previous_value / (_node_675_i2_ia1__out - _node_675_rms5__previous_value);
        if (_node_675_rms5__correction < 0)
            _node_675_rms5__correction = 0;
        else
            _node_675_rms5__correction = 0;
        _node_675_rms5__sample_cnt += _node_675_rms5__correction - _node_675_rms5__previous_correction;
        _node_675_rms5__out_state = sqrt(_node_675_rms5__square_sum / _node_675_rms5__sample_cnt);
        _node_675_rms5__sample_cnt = 0;
        _node_675_rms5__previous_correction = _node_675_rms5__correction;
        _node_675_rms5__square_sum = 0;
    } else if ( _node_675_rms5__sample_cnt >= 2778 ) {
        _node_675_rms5__out_state = sqrt(_node_675_rms5__square_sum / _node_675_rms5__sample_cnt);
        _node_675_rms5__sample_cnt = 0;
        _node_675_rms5__square_sum = 0;
    }
    _node_675_rms5__previous_value = _node_675_i2_ia1__out;
    _node_675_rms5__square_sum += _node_675_i2_ia1__out * _node_675_i2_ia1__out;
    _node_675_rms5__sample_cnt ++;
    // Generated from the component: Node 675.RMS4
    if( _node_675_rms4__zc ) {
        if (_node_675_i3_ia1__out != _node_675_rms4__previous_value)
            _node_675_rms4__correction = - _node_675_rms4__previous_value / (_node_675_i3_ia1__out - _node_675_rms4__previous_value);
        if (_node_675_rms4__correction < 0)
            _node_675_rms4__correction = 0;
        else
            _node_675_rms4__correction = 0;
        _node_675_rms4__sample_cnt += _node_675_rms4__correction - _node_675_rms4__previous_correction;
        _node_675_rms4__out_state = sqrt(_node_675_rms4__square_sum / _node_675_rms4__sample_cnt);
        _node_675_rms4__sample_cnt = 0;
        _node_675_rms4__previous_correction = _node_675_rms4__correction;
        _node_675_rms4__square_sum = 0;
    } else if ( _node_675_rms4__sample_cnt >= 2778 ) {
        _node_675_rms4__out_state = sqrt(_node_675_rms4__square_sum / _node_675_rms4__sample_cnt);
        _node_675_rms4__sample_cnt = 0;
        _node_675_rms4__square_sum = 0;
    }
    _node_675_rms4__previous_value = _node_675_i3_ia1__out;
    _node_675_rms4__square_sum += _node_675_i3_ia1__out * _node_675_i3_ia1__out;
    _node_675_rms4__sample_cnt ++;
    // Generated from the component: Node 675.I3_phase
    // Generated from the component: Node 675.I1_phase
    // Generated from the component: Node 675.I2_phase
    // Generated from the component: Node 680.RMS6
    if( _node_680_rms6__zc ) {
        if (_node_680_i1_ia1__out != _node_680_rms6__previous_value)
            _node_680_rms6__correction = - _node_680_rms6__previous_value / (_node_680_i1_ia1__out - _node_680_rms6__previous_value);
        if (_node_680_rms6__correction < 0)
            _node_680_rms6__correction = 0;
        else
            _node_680_rms6__correction = 0;
        _node_680_rms6__sample_cnt += _node_680_rms6__correction - _node_680_rms6__previous_correction;
        _node_680_rms6__out_state = sqrt(_node_680_rms6__square_sum / _node_680_rms6__sample_cnt);
        _node_680_rms6__sample_cnt = 0;
        _node_680_rms6__previous_correction = _node_680_rms6__correction;
        _node_680_rms6__square_sum = 0;
    } else if ( _node_680_rms6__sample_cnt >= 2778 ) {
        _node_680_rms6__out_state = sqrt(_node_680_rms6__square_sum / _node_680_rms6__sample_cnt);
        _node_680_rms6__sample_cnt = 0;
        _node_680_rms6__square_sum = 0;
    }
    _node_680_rms6__previous_value = _node_680_i1_ia1__out;
    _node_680_rms6__square_sum += _node_680_i1_ia1__out * _node_680_i1_ia1__out;
    _node_680_rms6__sample_cnt ++;
    // Generated from the component: Node 680.RMS5
    if( _node_680_rms5__zc ) {
        if (_node_680_i2_ia1__out != _node_680_rms5__previous_value)
            _node_680_rms5__correction = - _node_680_rms5__previous_value / (_node_680_i2_ia1__out - _node_680_rms5__previous_value);
        if (_node_680_rms5__correction < 0)
            _node_680_rms5__correction = 0;
        else
            _node_680_rms5__correction = 0;
        _node_680_rms5__sample_cnt += _node_680_rms5__correction - _node_680_rms5__previous_correction;
        _node_680_rms5__out_state = sqrt(_node_680_rms5__square_sum / _node_680_rms5__sample_cnt);
        _node_680_rms5__sample_cnt = 0;
        _node_680_rms5__previous_correction = _node_680_rms5__correction;
        _node_680_rms5__square_sum = 0;
    } else if ( _node_680_rms5__sample_cnt >= 2778 ) {
        _node_680_rms5__out_state = sqrt(_node_680_rms5__square_sum / _node_680_rms5__sample_cnt);
        _node_680_rms5__sample_cnt = 0;
        _node_680_rms5__square_sum = 0;
    }
    _node_680_rms5__previous_value = _node_680_i2_ia1__out;
    _node_680_rms5__square_sum += _node_680_i2_ia1__out * _node_680_i2_ia1__out;
    _node_680_rms5__sample_cnt ++;
    // Generated from the component: Node 680.RMS4
    if( _node_680_rms4__zc ) {
        if (_node_680_i3_ia1__out != _node_680_rms4__previous_value)
            _node_680_rms4__correction = - _node_680_rms4__previous_value / (_node_680_i3_ia1__out - _node_680_rms4__previous_value);
        if (_node_680_rms4__correction < 0)
            _node_680_rms4__correction = 0;
        else
            _node_680_rms4__correction = 0;
        _node_680_rms4__sample_cnt += _node_680_rms4__correction - _node_680_rms4__previous_correction;
        _node_680_rms4__out_state = sqrt(_node_680_rms4__square_sum / _node_680_rms4__sample_cnt);
        _node_680_rms4__sample_cnt = 0;
        _node_680_rms4__previous_correction = _node_680_rms4__correction;
        _node_680_rms4__square_sum = 0;
    } else if ( _node_680_rms4__sample_cnt >= 2778 ) {
        _node_680_rms4__out_state = sqrt(_node_680_rms4__square_sum / _node_680_rms4__sample_cnt);
        _node_680_rms4__sample_cnt = 0;
        _node_680_rms4__square_sum = 0;
    }
    _node_680_rms4__previous_value = _node_680_i3_ia1__out;
    _node_680_rms4__square_sum += _node_680_i3_ia1__out * _node_680_i3_ia1__out;
    _node_680_rms4__sample_cnt ++;
    // Generated from the component: Node 680.I3_phase
    // Generated from the component: Node 680.I1_phase
    // Generated from the component: Node 680.I2_phase
    // Generated from the component: Node 684.RMS6
    if( _node_684_rms6__zc ) {
        if (_node_684_i1_ia1__out != _node_684_rms6__previous_value)
            _node_684_rms6__correction = - _node_684_rms6__previous_value / (_node_684_i1_ia1__out - _node_684_rms6__previous_value);
        if (_node_684_rms6__correction < 0)
            _node_684_rms6__correction = 0;
        else
            _node_684_rms6__correction = 0;
        _node_684_rms6__sample_cnt += _node_684_rms6__correction - _node_684_rms6__previous_correction;
        _node_684_rms6__out_state = sqrt(_node_684_rms6__square_sum / _node_684_rms6__sample_cnt);
        _node_684_rms6__sample_cnt = 0;
        _node_684_rms6__previous_correction = _node_684_rms6__correction;
        _node_684_rms6__square_sum = 0;
    } else if ( _node_684_rms6__sample_cnt >= 2778 ) {
        _node_684_rms6__out_state = sqrt(_node_684_rms6__square_sum / _node_684_rms6__sample_cnt);
        _node_684_rms6__sample_cnt = 0;
        _node_684_rms6__square_sum = 0;
    }
    _node_684_rms6__previous_value = _node_684_i1_ia1__out;
    _node_684_rms6__square_sum += _node_684_i1_ia1__out * _node_684_i1_ia1__out;
    _node_684_rms6__sample_cnt ++;
    // Generated from the component: Node 684.RMS4
    if( _node_684_rms4__zc ) {
        if (_node_684_i3_ia1__out != _node_684_rms4__previous_value)
            _node_684_rms4__correction = - _node_684_rms4__previous_value / (_node_684_i3_ia1__out - _node_684_rms4__previous_value);
        if (_node_684_rms4__correction < 0)
            _node_684_rms4__correction = 0;
        else
            _node_684_rms4__correction = 0;
        _node_684_rms4__sample_cnt += _node_684_rms4__correction - _node_684_rms4__previous_correction;
        _node_684_rms4__out_state = sqrt(_node_684_rms4__square_sum / _node_684_rms4__sample_cnt);
        _node_684_rms4__sample_cnt = 0;
        _node_684_rms4__previous_correction = _node_684_rms4__correction;
        _node_684_rms4__square_sum = 0;
    } else if ( _node_684_rms4__sample_cnt >= 2778 ) {
        _node_684_rms4__out_state = sqrt(_node_684_rms4__square_sum / _node_684_rms4__sample_cnt);
        _node_684_rms4__sample_cnt = 0;
        _node_684_rms4__square_sum = 0;
    }
    _node_684_rms4__previous_value = _node_684_i3_ia1__out;
    _node_684_rms4__square_sum += _node_684_i3_ia1__out * _node_684_i3_ia1__out;
    _node_684_rms4__sample_cnt ++;
    // Generated from the component: Node 684.I3_phase
    // Generated from the component: Node 684.I1_phase
    // Generated from the component: Node 692.RMS6
    if( _node_692_rms6__zc ) {
        if (_node_692_i1_ia1__out != _node_692_rms6__previous_value)
            _node_692_rms6__correction = - _node_692_rms6__previous_value / (_node_692_i1_ia1__out - _node_692_rms6__previous_value);
        if (_node_692_rms6__correction < 0)
            _node_692_rms6__correction = 0;
        else
            _node_692_rms6__correction = 0;
        _node_692_rms6__sample_cnt += _node_692_rms6__correction - _node_692_rms6__previous_correction;
        _node_692_rms6__out_state = sqrt(_node_692_rms6__square_sum / _node_692_rms6__sample_cnt);
        _node_692_rms6__sample_cnt = 0;
        _node_692_rms6__previous_correction = _node_692_rms6__correction;
        _node_692_rms6__square_sum = 0;
    } else if ( _node_692_rms6__sample_cnt >= 2778 ) {
        _node_692_rms6__out_state = sqrt(_node_692_rms6__square_sum / _node_692_rms6__sample_cnt);
        _node_692_rms6__sample_cnt = 0;
        _node_692_rms6__square_sum = 0;
    }
    _node_692_rms6__previous_value = _node_692_i1_ia1__out;
    _node_692_rms6__square_sum += _node_692_i1_ia1__out * _node_692_i1_ia1__out;
    _node_692_rms6__sample_cnt ++;
    // Generated from the component: Node 692.RMS5
    if( _node_692_rms5__zc ) {
        if (_node_692_i2_ia1__out != _node_692_rms5__previous_value)
            _node_692_rms5__correction = - _node_692_rms5__previous_value / (_node_692_i2_ia1__out - _node_692_rms5__previous_value);
        if (_node_692_rms5__correction < 0)
            _node_692_rms5__correction = 0;
        else
            _node_692_rms5__correction = 0;
        _node_692_rms5__sample_cnt += _node_692_rms5__correction - _node_692_rms5__previous_correction;
        _node_692_rms5__out_state = sqrt(_node_692_rms5__square_sum / _node_692_rms5__sample_cnt);
        _node_692_rms5__sample_cnt = 0;
        _node_692_rms5__previous_correction = _node_692_rms5__correction;
        _node_692_rms5__square_sum = 0;
    } else if ( _node_692_rms5__sample_cnt >= 2778 ) {
        _node_692_rms5__out_state = sqrt(_node_692_rms5__square_sum / _node_692_rms5__sample_cnt);
        _node_692_rms5__sample_cnt = 0;
        _node_692_rms5__square_sum = 0;
    }
    _node_692_rms5__previous_value = _node_692_i2_ia1__out;
    _node_692_rms5__square_sum += _node_692_i2_ia1__out * _node_692_i2_ia1__out;
    _node_692_rms5__sample_cnt ++;
    // Generated from the component: Node 692.RMS4
    if( _node_692_rms4__zc ) {
        if (_node_692_i3_ia1__out != _node_692_rms4__previous_value)
            _node_692_rms4__correction = - _node_692_rms4__previous_value / (_node_692_i3_ia1__out - _node_692_rms4__previous_value);
        if (_node_692_rms4__correction < 0)
            _node_692_rms4__correction = 0;
        else
            _node_692_rms4__correction = 0;
        _node_692_rms4__sample_cnt += _node_692_rms4__correction - _node_692_rms4__previous_correction;
        _node_692_rms4__out_state = sqrt(_node_692_rms4__square_sum / _node_692_rms4__sample_cnt);
        _node_692_rms4__sample_cnt = 0;
        _node_692_rms4__previous_correction = _node_692_rms4__correction;
        _node_692_rms4__square_sum = 0;
    } else if ( _node_692_rms4__sample_cnt >= 2778 ) {
        _node_692_rms4__out_state = sqrt(_node_692_rms4__square_sum / _node_692_rms4__sample_cnt);
        _node_692_rms4__sample_cnt = 0;
        _node_692_rms4__square_sum = 0;
    }
    _node_692_rms4__previous_value = _node_692_i3_ia1__out;
    _node_692_rms4__square_sum += _node_692_i3_ia1__out * _node_692_i3_ia1__out;
    _node_692_rms4__sample_cnt ++;
    // Generated from the component: Node 692.I3_phase
    // Generated from the component: Node 692.I1_phase
    // Generated from the component: Node 692.I2_phase
    // Generated from the component: Node 611.CPU Transition1.Input
    // Generated from the component: Node 632.CPU Transition1.Input
    // Generated from the component: Node 632.CPU Transition2.Input
    // Generated from the component: Node 632.CPU Transition3.Input
    // Generated from the component: Node 633.CPU Transition1.Input
    // Generated from the component: Node 633.CPU Transition2.Input
    // Generated from the component: Node 633.CPU Transition3.Input
    // Generated from the component: Node 634.CPU Transition1.Input
    // Generated from the component: Node 634.CPU Transition2.Input
    // Generated from the component: Node 634.CPU Transition3.Input
    // Generated from the component: Node 645.CPU Transition1.Input
    // Generated from the component: Node 645.CPU Transition2.Input
    // Generated from the component: Node 646.CPU Transition1.Input
    // Generated from the component: Node 646.CPU Transition2.Input
    // Generated from the component: Node 652.CPU Transition1.Input
    // Generated from the component: Node 671.CPU Transition1.Input
    // Generated from the component: Node 671.CPU Transition2.Input
    // Generated from the component: Node 671.CPU Transition3.Input
    // Generated from the component: Node 675.CPU Transition1.Input
    // Generated from the component: Node 675.CPU Transition2.Input
    // Generated from the component: Node 675.CPU Transition3.Input
    // Generated from the component: Node 680.CPU Transition1.Input
    // Generated from the component: Node 680.CPU Transition2.Input
    // Generated from the component: Node 680.CPU Transition3.Input
    // Generated from the component: Node 684.CPU Transition1.Input
    // Generated from the component: Node 684.CPU Transition2.Input
    // Generated from the component: Node 692.CPU Transition1.Input
    // Generated from the component: Node 692.CPU Transition2.Input
    // Generated from the component: Node 692.CPU Transition3.Input
    // Generated from the component: S1.Triple S1 ideal.CTC_Wrapper
    // Generated from the component: MSR 632-671.I1_rms
    // Generated from the component: MSR 632-671.I2_rms
    // Generated from the component: MSR 632-671.I3_rms
    // Generated from the component: Node 611.I3_rms
    // Generated from the component: Node 632.I1_rms
    // Generated from the component: Node 632.I2_rms
    // Generated from the component: Node 632.Probe1
    // Generated from the component: Node 632.I3_rms
    // Generated from the component: Node 633.I1_rms
    // Generated from the component: Node 633.I2_rms
    // Generated from the component: Node 633.I3_rms
    // Generated from the component: Node 634.I1_rms
    // Generated from the component: Node 634.I2_rms
    // Generated from the component: Node 634.I3_rms
    // Generated from the component: Node 645.I2_rms
    // Generated from the component: Node 645.I3_rms
    // Generated from the component: Node 646.I2_rms
    // Generated from the component: Node 646.I3_rms
    // Generated from the component: Node 652.I1_rms
    // Generated from the component: Node 671.I1_rms
    // Generated from the component: Node 671.I2_rms
    // Generated from the component: Node 671.I3_rms
    // Generated from the component: Node 675.I1_rms
    // Generated from the component: Node 675.I2_rms
    // Generated from the component: Node 675.I3_rms
    // Generated from the component: Node 680.I1_rms
    // Generated from the component: Node 680.I2_rms
    // Generated from the component: Node 680.I3_rms
    // Generated from the component: Node 684.I1_rms
    // Generated from the component: Node 684.I3_rms
    // Generated from the component: Node 692.I1_rms
    // Generated from the component: Node 692.I2_rms
    // Generated from the component: Node 692.I3_rms
    //@cmp.update.block.end
}
// ----------------------------------------------------------------------------------------
//-----------------------------------------------------------------------------------------