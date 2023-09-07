from cherab.core.math.function cimport Function1D

cdef class ModifiedTanhGaussian(Function1D):

    cdef:
        double _ped_height, _ped_sol, _ped_width, _ped_pos, _ped_slope, _core_height, _core_width, _core_exp

    cdef double evaluate(self, double x) except? -1e999

    cdef double pedestal(self, double x)

    cdef double mtanh(self, double x)

    cdef double core(self, double x)
