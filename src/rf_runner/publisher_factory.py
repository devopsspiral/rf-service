import inspect
from rf_runner import publisher


class PublisherFactory(object):

    def __init__(self):
        self.publishers = []

    def get(self, data):
        targetClass = getattr(publisher, data['type'])
        instance = targetClass(data)
        return instance

    def get_meta(self):
        result = {}
        for name, obj in inspect.getmembers(publisher):
            if inspect.isclass(obj) and 'Abstract' not in name \
                                    and 'Publisher' in name:
                result.update({name: obj.meta()})
        return result
