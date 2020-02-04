from .fetcher import fetcher_factory
from .executor import Executor
from .publisher import publisher_factory


class Runner(object):
    def __init__(self, data):
        self.data = data

    def run(self):
        with fetcher_factory(self.data['fetcher']) as f:
            f.update()
            e = Executor(f.get_context())
            self.data['publisher']['context'] = f.get_context()
            p = publisher_factory(self.data['publisher'])
            p.publish(e.execute())
