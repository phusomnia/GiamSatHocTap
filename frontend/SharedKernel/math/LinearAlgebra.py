import math
import numpy as np

class Vector:
    def __init__(self, values):
        self.values = values
        ...
    
    # GETTER / SETTER
    def get_vector(self):
        return self.values

    def add(self, other: "Vector"):
        result = []

        for i in range(len(self.values)):
            result.append(
                self.values[i] + other.values[i]
            )

        print(f"[DEBUG] - Add: {self.values} + {other.values} = {result}")
        return Vector(result)

    def dot(self, other):
        result = []

        for i in range(len(self.values)):
            result.append(self.values[i] * other.values)

        print(f"[DEBUG] - DOT product: np.sum({self.values} * {other.values}) = {result}")
        return result

    def norm(self):
        
        total = 0

        for v in self.values:
            total += v * v

        result = math.sqrt

        print(f"[DEBUG] - norm: math.sqrt(np.sum({self.values} ** 2)) = {result}")
        return result

    def cosine_similarity(self, other: "Vector"):
        dot_product = self.dot(other)
        norm_self = self.norm()
        norm_other = other.norm()
        
        result = dot_product / (norm_self * norm_other)

        print(f"[DEBUG] - cosine_similarity: {dot_product} / ({norm_self} * {norm_other}) = {result}")
        return result

    def mahattan_distance(self, a, b):
        total = 0

        for i in range(len(a)):
            total += abs(a[i] - b[i])

        return total

    def euclidean_distance(self, a, b):
        total = 0 

        for i in range(len(a)):
            total += abs((a[i] - b[i]) ** 2)

        
        return math.sqrt(total)

class Matrix:
    def __init__(self, data):
        self.data = data

    def get_matrix(self):
        return self.data

    def transpose(self):
        rows = len(self.data)
        cols = len(self.data[0])

        result = []

        for j in range(cols):
            row = []
            for i in range(rows):
                row.append(
                    self.data[i][j]
                )
            result.append(row)

        return Matrix(result)

    def multiply(self, other):
        rows_A = len(self.data)
        cols_A = len(self.data[0])

        rows_B = len(other)
        cols_B = len(other[0])

        result = []

        for i in range(rows_A):
            row = []
            for j in range(cols_B):
                value = 0
                for k in range(cols_A):
                    value += (
                        self.data[i][k]
                        *
                        other.data[k][j]
                    )
                row.append(value)
            result.append(row)

        return Matrix(result)

class Determinant:
    def _get_minor(self):
        ...        
    
    def compute(self, matrix):
        n = len(matrix)

        if any(len(row) != n for row in matrix):
            raise ValueError("Ma trận phải là ma trận vuông!")

        # Trường hợp cơ sở 1: Ma trận cấp 1x1
        if n == 1:
            return matrix[0][0]

        if n == 2:
            return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

        det = 0
        
        for j in range(n):
            sign = (-1) ** j

vec1 = Vector([1, 2])
vec2 = Vector([1, 2])
# vec1.get_vector()
vec1.add(vec2).get_vector()
# print(f"Cosine similarity: {vec1.cosine_similarity(vec2)}")

ma1 = Matrix([
    [1, 2], 
    [3, 4]
])
ma2 = Matrix([
    [5, 6],
    [7, 8]
])
print(ma1.transpose().get_matrix())

det = Determinant()
det.compute([[1, 2], [2, 3]])
