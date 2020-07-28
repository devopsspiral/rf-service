import inspect
from rf_runner import publisher


class PublisherFactory(object):

    @staticmethod
    def get(data):
        targetClass = getattr(publisher, data['type'])
        instance = targetClass(data)
        return instance

    @staticmethod
    def get_meta():
        result = {}
        for name, obj in inspect.getmembers(publisher):
            if inspect.isclass(obj) and 'Abstract' not in name \
                                    and 'Publisher' in name:
                result.update({name: obj.meta()})
        return result
