import sympy

class Util:
    @staticmethod
    def combination(n, k):
        k = min(k, n - k)
        result = type(n)(1)

        for i in range(1, k + 1):
            result *= n
            result /= i
            n -= 1

        return result

    # SymPyオブジェクト
    # f: 関数
    # x: 対象変数
    # e: 許容誤差
    @staticmethod
    def newton_raphson_method(f, x, e, is_error=lambda e, y: abs(y) > e):
        df = sympy.diff(f, x)
        xi = 1.0

        while(True):
            y = f.subs([(x, xi)])
            if(not is_error(e, y)):
                break
            xi = xi - y / df.subs([(x, xi)])

        return xi
