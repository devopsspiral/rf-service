import inspect
from rf_runner import fetcher


class FetcherFactory(object):

    def __init__(self):
        self.fetchers = []

    def get(self, data):
        targetClass = getattr(fetcher, data['type'])
        instance = targetClass(data)
        return instance

    def get_meta(self):
        result = {}
        for name, obj in inspect.getmembers(fetcher):
            if inspect.isclass(obj) and 'Abstract' not in name \
                                    and 'Fetcher' in name:
                result.update({name: obj.meta()})
        return result
