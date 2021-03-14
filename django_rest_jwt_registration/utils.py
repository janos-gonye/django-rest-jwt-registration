import importlib


def import_elm_from_str(string):
    elements = string.split('.')
    module, elm = '.'.join(elements[:-1]), elements[-1]
    module = importlib.import_module(module)
    return getattr(module, elm)
