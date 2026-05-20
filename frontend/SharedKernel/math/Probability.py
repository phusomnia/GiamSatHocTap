import random
import math

class Bernoulli: 
    def __init__(self, p) -> None:
        self.validate(p)
        self.p = p
        ...

    def validate(self, p):
        if p < 0 or p > 1:
            raise ValueError("sigma > 0")

    def pmf(self, x):
        if x == 1: 
            return self.p
        if x == 0: 
            return 1 - self.p
        else: 
            return 0

    def mean(self):
        return self.p

    def variance(self):
        return self.p * (1 - self.p)

    def sample(self):
        r = random.random()
        if r < self.p:
            return 1
        return 0

class Gaussian:
    """
    sigma: 
        - ky hieu 𝜎
        - do lech chuan
    mean:
        - ky hieu 𝜇
        - trung binh 
    """

    def __init__(self, mu: int, sigma: int) -> None:
        if sigma <= 0:
            raise ValueError("sigma phai lon hon 0")
        
        self.mu = mu
        self.sigma = sigma
        ...

    def PDF(self, x: int):
        cofficient = 1 / (self.sigma * math.sqrt(2 * math.pi))

        exponent = math.exp(
            -((x - self.mu) ** 2) / (2 * self.sigma ** 2)
        )

        return cofficient * exponent

    def sample_BoxMuller(self):
        u1 = random.random()
        u2 = random.random()

        z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)

        return self.mu + self.sigma * z

# b = Bernoulli(0.7)
# print("P(X=1) =", b.pmf(1))
# print("P(X=0) =", b.pmf(0))

# print("Mean =", b.mean())
# print("Variance =", b.variance())

# Example usage (commented out to avoid side effects when importing)
# b = Bernoulli(0.7)
# for _ in range(10):
#     print(b.sample(), end=" ")

# g = Gaussian(0, 1)
# print("PDF at x=0 =", g.PDF(0))
# print("\nRandom Gaussian samples:")
# for _ in range(10):
#     print(round(g.sample_BoxMuller(), 4))