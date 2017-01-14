import sympy

from functools import wraps

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
            if(not is_error(e, y)): break
            xi = xi - y / df.subs([(x, xi)])

        return xi

    @staticmethod
    def cache(encoder=lambda arg: arg, decoder=lambda arg: arg):
        def decorator(f):
            cached = {}

            @wraps(f)
            def wrapper(self, *args):
                if args in cached: return encoder(cached[args])
                result = f(self, *args)
                cached[args] = decoder(result)
                return result

            return wrapper
        return decorator

    @staticmethod
    def non_elementary(default=None):
        def decorator(f):
            @wraps(f)
            def wrapper(self, *args):
                if self.is_elementary(): return default
                return f(self, *args)

            return wrapper
        return decorator

    @staticmethod
    def replace(old, new):
        def decorator(f):
            @wraps(f)
            def wrapper(self, arg):
                arg = arg.replace(old, new)
                return f(self, arg)
            return wrapper
        return decorator

    @staticmethod
    def encode_dagger(f):
        @wraps(f)
        @Util.replace('+', '*')
        def wrapper(*args):
            return f(*args)
        return wrapper

    @staticmethod
    def decode_dagger(f):
        @wraps(f)
        @Util.replace('*', '+')
        def wrapper(*args):
            return f(*args)
        return wrapper
