from time import sleep


class Solver:
    def __init__(self, dt_go_max=10, dt_go_min=10, dt_required=1000, t_min=700, t_max=1400, t0=300, time0=0,
                 t_refr0=300, p0=0, p_max=80000, quant=1, c=700, m=10):
        self.j = 10
        self.i = 0
        self.c = c
        self.m = m
        self.quant = quant
        self.h = quant / self.j
        self.p_max = p_max
        self.p_current = p0
        self.p_next = p0
        self.t_refr_current = t_refr0
        self.t_refr_next = t_refr0
        self.t_current = t0
        self.t_next = t0
        self.time_current = time0
        self.time_next = time0
        self.t_max = t_max
        self.t_min = t_min
        self.dt_required = dt_required
        self.dt_go_min = dt_go_min
        self.dt_go_max = dt_go_max
        self.coeff = p_max / (c * m * 1700)
        self.change_p = p0
        self.change_time = time0
        self.switch = True
        self.detect_in = False
        self.time_in = 0
        self.out = [t0, ]
        self.times = [time0, ]
        self.ps = [p0, ]

    def _calculate_one_point(self):
        self.t_next = (1 / (1 + (self.coeff * self.h) / 2)) * \
                      (self.t_current + (self.h / 2) * (((self.p_current + self.p_next) /
                                                         (self.c * self.m)) - self.coeff * (self.t_current -
                                                                                            self.t_refr_current - self.t_refr_next)))
        self.t_refr_current = self.t_refr_next

    def _rise_power_and_go_constant(self):
        if self.change_p + (
                (self.p_max - self.change_p) * (self.time_next - self.change_time) / self.dt_go_max) <= self.p_max:
            self.p_next = self.change_p + (
                        (self.p_max - self.change_p) * (self.time_next - self.change_time) / self.dt_go_max)
        else:
            self.p_next = self.p_max

    def _fall_power_and_go_zero(self):
        if self.change_p * (1 - ((self.time_next - self.change_time) / self.dt_go_min)) > 0:
            self.p_next = self.change_p * (1 - ((self.time_next - self.change_time) / self.dt_go_min))
        else:
            self.p_next = 0

    def _check_in_limits(self):
        if self.t_next > self.t_max or self.t_next < self.t_min:
            return False
        else:
            return True

    def do_switch(self):
        self.change_p = self.p_current
        self.change_time = self.time_current
        self.switch = not self.switch

    def set_trefr(self, trefr):
        self.t_refr_next = trefr

    def calc(self):
        self.time_current = self.time_next
        self.time_next = self.time_current + self.h

        if self.switch:
            self.p_current = self.p_next
            self._rise_power_and_go_constant()
        else:
            self.p_current = self.p_next
            self._fall_power_and_go_zero()

        self.t_current = self.t_next
        self._calculate_one_point()

        if self.t_next > self.t_min >= self.t_current:
            self.detect_in = True
            self.time_in = self.t_next

        if self.detect_in:
            if not self._check_in_limits():  # and ((self.t_next - self.time_in) < self.dt_required or (self.t_next - self.time_in) > self.dt_required * 1.1):
                raise (ValueError("Браковано"))

            if (self.t_next - self.time_in) > self.dt_required * 1.1:
                self.detect_in = False

        self.i += 1

        self.out.append(self.t_next)
        self.times.append(self.time_next)
        self.ps.append(self.p_next)

    def generate_calculations(self):
        while True:
            self.calc()
            if self.i % self.j == 0:
                yield self.times[-1], self.out[-1], self.ps[-1]
            sleep(self.h)
