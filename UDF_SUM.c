#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "gmp.h"
#include "paillier.c"
#include <my_global.h>
#include <my_sys.h>
#include <mysql.h>
#define BASE 32

static pthread_mutex_t LOCK_hostname;
static char* PUBLIC_KEY = "a4778d390098957740d4c69b6ba06f35";

my_bool SUM_HE_init(UDF_INIT *initid, UDF_ARGS *args, char *message);
void SUM_HE_deinit(UDF_INIT *initid);
char *SUM_HE(UDF_INIT *initid, UDF_ARGS *args,
             char *result, unsigned long *length,
             char *is_null, char *error);
void SUM_HE_clear(UDF_INIT *initid, char *is_null, 
                  char *error);
void SUM_HE_add(UDF_INIT *initid, UDF_ARGS *args,
                char *is_null, char *error);

my_bool SUM_HE_init(UDF_INIT *initid, UDF_ARGS *args, char *message){
    char* i = (char*) malloc(100*sizeof(char));
    initid->ptr = i;
    initid->maybe_null=1;
    // check the arguments format
    if (args->arg_count != 1){
        strcpy(message,"SUM_HE() requires one arguments");
        return 1;
    }
    
    if (args->arg_type[0] != STRING_RESULT){
        strcpy(message,"SUM_HE() requires an string");
        return 1;
    }
    return 0;
}

void SUM_HE_deinit(UDF_INIT *initid){
    free(initid->ptr);
}

char *SUM_HE(UDF_INIT *initid, UDF_ARGS *args,
             char *result, unsigned long *length,
             char *is_null, char *error){
    *length = strlen(initid->ptr);
    return initid->ptr;
}

void SUM_HE_clear(UDF_INIT *initid, char *is_null, char *error){
    paillier_ciphertext_t* enc_zero = paillier_create_enc_zero();
    initid->ptr = mpz_get_str(NULL, BASE, enc_zero->c);
}

void SUM_HE_add(UDF_INIT *initid, UDF_ARGS *args, char *is_null, char *error){
    paillier_pubkey_t* pubkey = paillier_pubkey_from_hex(PUBLIC_KEY);
    paillier_ciphertext_t* ct0;
    paillier_ciphertext_t* ct1;
    paillier_ciphertext_t* sum;
    ct0 = (paillier_ciphertext_t*) malloc(sizeof(paillier_ciphertext_t)); 
    ct1  = (paillier_ciphertext_t*) malloc(sizeof(paillier_ciphertext_t));
    sum = (paillier_ciphertext_t*) malloc(sizeof(paillier_ciphertext_t));
    mpz_init_set_str(ct0->c, initid->ptr, BASE);
    mpz_init_set_str(ct1->c, args->args[0], BASE);
    mpz_init(sum->c);
    paillier_mul(pubkey, sum, ct0, ct1);
    initid->ptr = mpz_get_str(NULL, BASE, sum->c);
}
