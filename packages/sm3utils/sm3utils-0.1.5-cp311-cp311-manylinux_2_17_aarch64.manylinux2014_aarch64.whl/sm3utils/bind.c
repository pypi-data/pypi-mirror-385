
#include "sm3.h"

char pysm3_init_docs[] = "sm3 init context";
char pysm3_update_docs[] = "sm3 update";
char pysm3_final_docs[] = "sm3 final";
char pysm3_free_docs[] = "sm3 free context";
char pysm3_copy_docs[] = "sm3 copy context";

PyMethodDef _sm3_funcs[] = {
	{	"pysm3_init",
		(PyCFunction)pysm3_init,
		METH_NOARGS,
		pysm3_init_docs},
	{	"pysm3_update",
		(PyCFunction)pysm3_update,
		METH_VARARGS,
		pysm3_update_docs},
	{	"pysm3_final",
		(PyCFunction)pysm3_final,
		METH_VARARGS,
		pysm3_final_docs},
    {	"pysm3_free",
		(PyCFunction)pysm3_free,
		METH_VARARGS,
		pysm3_free_docs},
    {	"pysm3_copy",
		(PyCFunction)pysm3_copy,
		METH_VARARGS,
		pysm3_copy_docs},
	{	NULL}
};

char _sm3_docs[] = "sm3 hash utils";
char _sm3_name[] = "_sm3";

#if PY_MAJOR_VERSION >= 3

PyModuleDef _sm3_mod = {
	PyModuleDef_HEAD_INIT,
	_sm3_name,
	_sm3_docs,
	-1,
	_sm3_funcs,
	NULL,
	NULL,
	NULL,
	NULL
};

PyMODINIT_FUNC PyInit__sm3(void) {
	return PyModule_Create(&_sm3_mod);
}

#else

void init_sm3(void) {
	Py_InitModule3(_sm3_name, _sm3_funcs, _sm3_docs);
}

#endif
