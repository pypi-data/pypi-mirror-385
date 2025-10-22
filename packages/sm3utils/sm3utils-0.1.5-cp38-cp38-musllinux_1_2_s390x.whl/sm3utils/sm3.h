#ifndef LIBSM3_SM3_H
#define LIBSM3_SM3_H

#include <sys/types.h>
#include <stdint.h>
#include <string.h>

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define SM3_DIGEST_LENGTH	32
#define SM3_BLOCK_SIZE		64
#ifdef CPU_BIGENDIAN
    #define cpu_to_be16(v) (v)
    #define cpu_to_be32(v) (v)
    #define be16_to_cpu(v) (v)
    #define be32_to_cpu(v) (v)
#else
    #define cpu_to_be16(v) (((v)<< 8) | ((v)>>8))
    #define cpu_to_be32(v) (((v)>>24) | (((v)>>8)&0xff00) | (((v)<<8)&0xff0000) | ((v)<<24))
    #define be16_to_cpu(v) cpu_to_be16(v)
    #define be32_to_cpu(v) cpu_to_be32(v)
#endif

#ifdef __cplusplus
extern "C" {
#endif


typedef struct {
	uint32_t digest[8];
	int nblocks;
	unsigned char block[64];
	int num;
} sm3_ctx_t;

void sm3_init(sm3_ctx_t *ctx);
void sm3_update(sm3_ctx_t *ctx, const unsigned char* data, size_t data_len);
void sm3_final(sm3_ctx_t *ctx, unsigned char digest[SM3_DIGEST_LENGTH]);
void sm3_compress(uint32_t digest[8], const unsigned char block[SM3_BLOCK_SIZE]);

PyObject * pysm3_init(PyObject *);
PyObject * pysm3_update(PyObject *, PyObject *);
PyObject * pysm3_final(PyObject *, PyObject *);
PyObject * pysm3_free(PyObject *, PyObject *);
PyObject * pysm3_copy(PyObject *, PyObject *);

#ifdef __cplusplus
}
#endif

#endif