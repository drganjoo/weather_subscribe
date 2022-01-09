from functools import wraps

def logged(f):
    @wraps(f)
    def with_logging(*args, **kwargs):
        print('with_logging')
        return f(*args, **kwargs)

    print('logged deco called')
    return with_logging

def logged_param(route, *args):
    print(f'What is args {args}')
    f = args.pop()
    print(f'What is f {f}')

    @wraps(f)
    def with_logging(*args, **kwargs):
        print(f'logged_param -> with_logging, what is f {f} and what are args: {route}')
        return f(*args, **kwargs)

    print('logged_param deco called')
    return with_logging

@logged_param('/')
def check():
    """This is called doc string in python"""
    print('check has been called')

print('outside')
check()
print(f'check.__name__ name -> {check.__name__} and doc {check.__doc__}')
