#include<stdio.h>
#include<gmp.h>
#include"paillier.c"
int main(int argc, char** argv){
    paillier_pubkey_t* pubkey = paillier_pubkey_from_hex(argv[2]);
    paillier_prvkey_t* prikey = paillier_prvkey_from_hex(argv[3],pubkey);
    unsigned long int ui = strtoul(argv[1], NULL, 10);
    paillier_plaintext_t* pt = paillier_plaintext_from_ui(ui);
    paillier_ciphertext_t* enc_res = NULL;
    paillier_ciphertext_t* enc_res1 = paillier_enc(enc_res,pubkey,pt,paillier_get_rand_devurandom);
    char* mpz_str = mpz_get_str(NULL,32,enc_res1->c);
    printf("%s",mpz_str);
    exit(0);
}
