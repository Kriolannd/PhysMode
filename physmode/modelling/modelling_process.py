import time
from threading import Thread
from typing import Callable

from physmode.modelling.distortion import Distortion
from physmode.modelling.solver import Solver


# from distortion import Distortion
# from solver import Solver


class ModellingProcess(Thread):
    def __init__(self, solver_builder: Callable[[], Solver], distortion: Distortion):
        super().__init__()
        self.daemon = True

        self.distortion = distortion
        self.solver_builder = solver_builder
        self.solver = self.solver_builder()

        self.true_state = True
        self.apparent_state = True
        self.paused = True

        self.callbacks = []

    def set_trefr(self, trefr):
        if trefr:
            self.solver.set_trefr(float(trefr))

    def set_distortion_params(self, sigma, alpha):
        self.distortion.sigma = float(sigma) if sigma else self.distortion.sigma
        self.distortion.alpha = float(alpha) if alpha else self.distortion.alpha

    def switch(self):
        print(self.apparent_state)
        self.apparent_state = not self.apparent_state
        print(self.apparent_state)

        if self.distortion.change_switch():
            self.true_state = not self.true_state
            self.solver.do_switch()

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def _restart(self):
        self.solver = self.solver_builder()

        self.true_state = True
        self.apparent_state = True
        self.paused = True

    def toggle(self):
        self.paused = not self.paused

    def run(self):
        while True:
            try:
                for phys_calcs in self.solver.generate_calculations():
                    while self.paused: time.sleep(1)

                    results = {
                        "time": round(phys_calcs[0], 2),
                        "power": round(phys_calcs[2], 2),

                        "state": int(self.true_state),
                        "state_apparent": int(self.apparent_state),

                        "temp": round(phys_calcs[1], 2),
                        "temp_apparent": round(self.distortion.change_temp(phys_calcs[1]), 2),
                    }

                    for callback in self.callbacks:
                        callback(results)

            except ValueError:
                for callback in self.callbacks:
                    callback({"dead": True})

                self._restart()

    @staticmethod
    def build_from_file(f3_path):
        with open(f3_path, "r") as f3:
            line = f3.readline()
            vals = line.split(";")
            quant = float(vals[0])
            dt_required = float(vals[1])
            t_max = float(vals[2])
            t_min = float(vals[3])
            dt_go_min = float(vals[4])
            dt_go_max = float(vals[5])

        return ModellingProcess(
            lambda: Solver(quant=quant, dt_required=dt_required,
                           t_max=t_max, t_min=t_min,
                           dt_go_min=dt_go_min, dt_go_max=dt_go_max),
            Distortion(sigma=10, alpha=0)
        )


if __name__ == "__main__":
    mp = ModellingProcess.build_from_file("F3.txt")

    def log_values(values):
        with open("F4.txt", "a") as log:
            log.write(str(values) + "\n")

    # mp.add_callback(log_values)
    mp.add_callback(print)

    mp.start()
    mp.join()
