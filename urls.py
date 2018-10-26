# -*- coding: utf-8 -*-

from views import CBV

URLpattern = [
    (r"/CBV/(.*)/$", CBV.as_view(name='CBV')),  # 这个name可以用于endpoint功能开发
]

