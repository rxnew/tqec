class Util:
    @staticmethod
    def combination(n, k):
        k = min(k, n - k)
        result = type(n)(0)
        for i in range(1, k + 1):
            result *= n
            result /= i
            n -= 1
        return result
