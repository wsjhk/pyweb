# -*- coding: utf-8 -*-

class View(object):
    methods = None

    decorators = ()

    @classmethod
    def as_view(cls, name, *class_args, **class_kwargs):
        def view(*args, **kwargs):
            self = view.view_class(*class_args, **class_kwargs) # 反射机制
            return self.dispatch_request(*args, **kwargs)

        if cls.decorators:
            view.__name__ = name
            view.__module__ = cls.__module__
            for decorator in cls.decorators:
                view = decorator(view)

        view.view_class = cls
        view.__name__ = name
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.methods = cls.methods
        return view

    def dispatch_request(self, *args, **kwargs):
        request = args[0]
        meth = getattr(self, request.method.lower(), None)
        assert meth is not None, 'Unimplemented method'
        return meth(*args, **kwargs)


class CBV(View):
    methods = None

    decorators = ()

    def get(self, request, name):
        method = request.method
        return "<h1>CBV {method}, {name}!</h1>".format(method = method, name = name)

    def post(self, request, name):
        method = request.method
        return "<h1>CBV {method}, {name}!</h1>".format(method = method, name = name)

    
    
    
    
