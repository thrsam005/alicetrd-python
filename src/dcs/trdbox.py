
import click
import zmq

@click.group()
@click.option('-c', '--connect', default='tcp://localhost:7766')
@click.pass_context
def trdbox(ctx, connect):
    ctx.ensure_object(dict)

    ctx.obj['context'] = zmq.Context()
    ctx.obj['socket'] = ctx.obj['context'].socket(zmq.REQ)
    ctx.obj['socket'].connect(connect)


@trdbox.command()
@click.argument('cmd', default=1)
@click.pass_context
def pretrigger(ctx, cmd):
    socket = ctx.obj['socket']

    socket.send_string(f"write 0x08 {cmd}")
    reply = socket.recv_string()
    print(reply)

@trdbox.command()
@click.argument('address', callback=lambda c,p,x: int(x,0))
@click.pass_context
def read(ctx, address):
    socket = ctx.obj['socket']

    socket.send_string(f"read {address}")
    reply = socket.recv_string()
    print(reply)

@trdbox.command()
@click.argument('address', callback=lambda c,p,x: int(x,0))
@click.argument('data', callback=lambda c,p,x: int(x,0))
@click.pass_context
def write(ctx, address, data):
    socket = ctx.obj['socket']

    socket.send_string(f"write {address} {data}")
    reply = socket.recv_string()
    print(reply)
