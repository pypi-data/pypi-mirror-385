

from twisted.internet import reactor
from ebs.linuxnode.core.basenode import BaseIoTNode
from ebs.linuxnode.core import config
from ebs.linuxnode.exim.mixin import LocalEximMixin


class ExampleNode(LocalEximMixin, BaseIoTNode):
    def start(self):
        self.install()
        super(ExampleNode, self).start()
        reactor.callLater(60, self.stop)
        reactor.run()

    def stop(self):
        super(ExampleNode, self).stop()
        reactor.stop()


def main():
    nodeconfig = config.IoTNodeConfig('iotnode-exim')
    config.current_config = nodeconfig

    node = ExampleNode(reactor=reactor)
    node.start()


if __name__ == '__main__':
    main()
