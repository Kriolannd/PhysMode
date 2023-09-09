import random


class Distortion:
    def __init__(self, sigma=0, alpha=0):
        self.sigma = sigma
        self.alpha = alpha

    def change_temp(self, temp):
        return random.gauss(temp, self.sigma)

    def change_switch(self):
        return random.random() > self.alpha
