#include<stdio.h>
#include<gmp.h>
#include"paillier.c"
int main(int argc, char** argv){
    paillier_pubkey_t* pubkey = paillier_pubkey_from_hex(argv[2]);
    paillier_prvkey_t* prikey = paillier_prvkey_from_hex(argv[3],pubkey);
    paillier_ciphertext_t* enc_res;
    enc_res = (paillier_ciphertext_t*) malloc(sizeof(paillier_ciphertext_t));
    mpz_init_set_str(enc_res->c, argv[1], 32);
    paillier_plaintext_t* dec_res = NULL;
    paillier_plaintext_t* dec_res1 = paillier_dec(dec_res,pubkey,prikey,enc_res);
    char* mpz_str = mpz_get_str(NULL,10,dec_res1->m);
    printf("%s", mpz_str);
    exit(0);
}

