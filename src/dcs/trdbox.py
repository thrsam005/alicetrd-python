
import click
import zmq

class TrdboxCommand:
    def __init__(self, connect):

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(connect)

    def exec(self, cmd):
        self.socket.send_string(cmd)
        return self.socket.recv_string()


@click.group()
@click.option('-c', '--connect', default='tcp://localhost:7766')
@click.pass_context
def trdbox(ctx, connect):
    ctx.obj = TrdboxCommand(connect)


@trdbox.command()
@click.argument('cmd', default=1)
@click.pass_context
def pretrigger(ctx, cmd):
    ctx.obj.exec(f"write 0x08 {cmd}")

@trdbox.command()
@click.argument('address', callback=lambda c,p,x: int(x,0))
@click.pass_context
def read(ctx, address):
    print(ctx.obj.exec(f"read {address}"))

@trdbox.command()
@click.argument('address', callback=lambda c,p,x: int(x,0))
@click.argument('data', callback=lambda c,p,x: int(x,0))
@click.pass_context
def write(ctx, address, data):
    ctx.obj.exec(f"write {address} {cmd}")
