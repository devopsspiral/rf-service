import inspect
from rf_runner import fetcher


class FetcherFactory(object):

    @staticmethod
    def get(data):
        targetClass = getattr(fetcher, data['type'])
        instance = targetClass(data)
        return instance

    @staticmethod
    def get_meta():
        result = {}
        for name, obj in inspect.getmembers(fetcher):
            if inspect.isclass(obj) and 'Abstract' not in name \
                                    and 'Fetcher' in name:
                result.update({name: obj.meta()})
        return result
