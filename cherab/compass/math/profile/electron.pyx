from cherab.core.math.function cimport Function1D

from libc.math cimport exp

cdef class ModifiedTanhGaussian(Function1D):
    """
    Profile function used at the COMPASS tokamak for electron temperature and density profiles. Pedestal part
    is described by a modified hyperbolic tanges. The core part is a Normal-like shape with power as a parameter.
    Based on [1]_.


    :param ped_height: Pedestal height
    :param ped_sol: Scrapeoff layer position
    :param ped_width: Width of the pedestal
    :param ped_pos: Position of the pedestal
    :param ped_slope: Slope of the pedestal
    :param core_height: Value of the profile at the magnetic axis
    :param core_width: Width or shape of the curvature of the core profile part
    :param core_exp: Exponential parameter of the bell-shaped core profile


    [1]Stefanikova, E., Peterka, M., Bohm, P., Bilkova, P., Aftanas, M., Sos, M., Urban, J., Hron, M. and Panek, R.,
     2016. Fitting of the Thomson scattering density and temperature profiles on the COMPASS tokamak.
    Review of Scientific Instruments, 87(11), p.11E536.
    """
    
    def __init__(self, ped_height, ped_sol, ped_width, ped_pos, ped_slope, core_height, core_width, core_exp):
        super().__init__()

        self.ped_height = ped_height
        self.ped_sol = ped_sol
        self.ped_width = ped_width
        self.ped_pos = ped_pos
        self.ped_slope = ped_slope
        self.core_height = core_height
        self.core_width = core_width
        self.core_exp = core_exp

    @property
    def ped_height(self):
        return self._ped_height

    @ped_height.setter
    def ped_height(self, value):
        self._ped_height = value

    @property
    def ped_sol(self):
        return self._ped_sol

    @ped_sol.setter
    def ped_sol(self, value):
        self._ped_sol = value

    
    @property
    def ped_width(self):
        return self._ped_width

    @ped_width.setter
    def ped_width(self, value):
        self._ped_width = value

    @property
    def ped_pos(self):
        return self._ped_pos

    @ped_pos.setter
    def ped_pos(self, value):
        self._ped_pos = value

    @property
    def ped_slope(self):
        return self._ped_slope

    @ped_slope.setter
    def ped_slope(self, value):
        self._ped_slope = value

    @property
    def core_height(self):
        return self._core_height

    @core_height.setter
    def core_height(self, value):
        self._core_height = value


    @property
    def core_width(self):
        return self._core_width

    @core_width.setter
    def core_width(self, value):
        self._core_width = value

    @property
    def core_exp(self):
        return self._core_exp

    @core_exp.setter
    def core_exp(self, value):
        self._core_exp = value

    cdef double evaluate(self, double x) except? -1e999:
        """
        Evaluate the function for x
        :param x: Independent variable
        :return: Profile value
        """
        cdef:
            double core, ped

        core = self.core(x)
        ped = self.pedestal(x)

        return ped + (self._core_height - ped) * core


    cdef double pedestal(self, double x):
        """
        Pedestal part of the profile.
        :param x: Independent variable
        :return: Value of pedestal part of profile
        """
        cdef:
            double mtanh

        mtanh = self.mtanh(x)

        return 0.5 * (self._ped_height - self._ped_sol) * (mtanh + 1)

    cdef double mtanh(self, double x):
        """
        Modified hyperbolic tangens used in pedestal shape description
        :param x: Independent variable
        :return: 
        """
        cdef:
            double xped
            
        xped = (self._ped_pos - x ) / (2 * self._ped_width) # Independent variable for modified hyp. tangens
        return ((1 + self._ped_slope * xped) * exp(xped) - exp(-1 * xped)) / (exp(xped) + exp(-1 * xped))


    cdef double core(self, double x):
        """
        Core part of the profile described by a Normal-like distribution.
        :param x: Independent variable
        :return: Core part of the profile
        """
        cdef:
            double exponent

        exponent = -(x / self._core_width) ** self._core_exp
        return exp(exponent)

