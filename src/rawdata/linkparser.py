import numpy as np
import math
from struct import unpack
#import pylab as pl

from functools import wraps
import functools
from collections import namedtuple
from typing import NamedTuple
from pprint import pprint


class decode:

	def __init__(self, pattern):

		fieldinfo = dict()

		# calculate bitmask and required shift for every character
		for i,x in enumerate(x for x in pattern if x not in ": "):
			p = 31-i # bit position
			if x not in fieldinfo:
				fieldinfo[x] = dict(mask=1<<p, shift=p)
			else:
				fieldinfo[x]['mask'] |= 1<<p
				fieldinfo[x]['shift'] = p

		# remember bits marked as '0' or '1' for validation of the dword
		zero_mask = fieldinfo.pop('0')['mask'] if '0' in fieldinfo else 0
		one_mask  = fieldinfo.pop('1')['mask'] if '1' in fieldinfo else 0
		self.validate_value = one_mask
		self.validate_mask = zero_mask | one_mask

		# create a named tuple based on the field names
		self.dtype = namedtuple("decoded_fields", fieldinfo.keys() )

		# flatten the fields info to a tuple for faster retrieval
		# the field name is not stritcly necessary, but might help to debug
		self.fields = tuple(
		  (k,fieldinfo[k]['mask'],fieldinfo[k]['shift']) for k in fieldinfo )


	def __call__(self,func):

		@wraps(func)
		def wrapper(ctx, dword):
			assert( (dword & self.validate_mask) == self.validate_value)
			return func(ctx,dword,self.decode(dword))

		return wrapper

	def decode(self,dword):
		return self.dtype(*[ (dword & x[1]) >> x[2] for x in self.fields ])

class describe:

	def __init__(self, fmt, level=3):
		self.format = fmt
		self.level = level
		self.loglevel = 3

	def __call__(self,func):

		@wraps(func)
		def wrapper(ctx,dword,fields=None):

			if fields is None:
				retval = func(ctx,dword)
				fielddata = {}

			else:
				retval = func(ctx,dword,fields)
				fielddata = fields._asdict()

			if retval is True or retval is None:
				retval = dict()

			if 'description' not in retval:
				retval['description'] = self.format.format(dword=dword, **fielddata, ctx=ctx)

			return retval

		return wrapper



ParsingContext = namedtuple('ParsingContext', [
  'major', 'minor', 'nhw', 'sm', 'stack', 'layer', 'side', #from HC0
  'ntb', 'bc_counter', 'pre_counter', 'pre_phase',
  'SIDE', 'HC', 'VER'
])


# ------------------------------------------------------------------------
# Generic dwords


@describe("... skip parsing ...", level=0)
def skip_until_eod(ctx, dword):
	pass

@describe("tracklet")
def parse_tracklet(state, dword):
	assert(dword != 0x10001000)

@describe("EOT")
def parse_eot(ctx, dword):
	assert(dword == 0x10001000)
	ctx.readlist.append([parse_eot, parse_hc0])

@describe("EOD")
def parse_eod(ctx, dword):
	assert(dword == 0x00000000)
	ctx.readlist.append([parse_eod])

# ------------------------------------------------------------------------
# Half-chamber headers

# @parsefct(compare=0x80000001, mask=0x80000003)
@decode("xmmm : mmmm : nnnn : nnnq : qqss : sssp : ppcc : ci01")
@describe("HC0 {ctx.HC} ver=0x{m:X}.{n:X} nw={q}")
def parse_hc0(ctx, dword, fields):

	ctx.major = fields.m  # (dword >> 24) & 0x7f
	ctx.minor = fields.n  # (dword >> 17) & 0x7f
	ctx.nhw   = fields.q  # (dword >> 14) & 0x7
	ctx.sm    = fields.s  # (dword >>  9) & 0x7
	ctx.layer = fields.p  # (dword >>  6) & 0x1f
	ctx.stack = fields.c  # (dword >>  3) & 0x3
	ctx.side  = fields.i  # (dword >>  2) & 0x1

	# An alternative to update the context - which one is easier to read?
	# (ctx.major,ctx.minor,ctx.nhw,ctx.sm,ctx.layer,ctx.stack,ctx.side) = fields

	side = 'A' if fields.i==0 else 'B'
	ctx.HC   = f"{fields.s:02}_{fields.c}_{fields.p}{side}"

	for i in range(ctx.nhw):
		ctx.readlist.append([parse_hc1, parse_hc2, parse_hc3])

	# ctx.readlist.append([skip_until_eod])
	ctx.readlist.append([parse_mcmhdr])

@decode("tttt : ttbb : bbbb : bbbb : bbbb : bbpp : pphh : hh01")
@describe("HC1 tb={t} bc={b} ptrg={p} phase={h}")
def parse_hc1(ctx, dword, fields):

	ctx.ntb         = fields.t  # (dword >> 26) & 0x3f
	ctx.bc_counter  = fields.b  # (dword >> 10) & 0xffff
	ctx.pre_counter = fields.p  # (dword >>  6) & 0xF
	ctx.pre_phase   = fields.h  # (dword >>  2) & 0xF


@decode("pgtc : nbaa : aaaa : xxxx : xxxx : xxxx : xx11 : 0001")
@describe("HC2 - filter settings")
def parse_hc2(self):
	pass

@decode("ssss : ssss : ssss : saaa : aaaa : aaaa : aa11 : 0101")
@describe("HC3 - svn version")
def parse_hc3(self):
	pass

# ------------------------------------------------------------------------
# MCM headers

@decode("1rrr : mmmm : eeee : eeee : eeee : eeee : eeee : 1100")
@describe("MCM {r}:{m:02} event {e}")
def parse_mcmhdr(ctx, dword, fields):

	if ctx.major & 0x20:
		# Zero suppression
		ctx.readlist.append([parse_adcmask])

	else:
		# No ZS -> read 21 channels, then expect next MCM header or EOD
		for i in range ( 21 * (ctx.ntb // 3) ):
			ctx.readlist.append([parse_adcdata])
		ctx.readlist.append([parse_mcmhdr, parse_eod])

@decode("nncc : cccm : mmmm : mmmm : mmmm : mmmm : mmmm : 1100")
@describe("MCM ADCMASK n={n} c={c} m={m:05x}")
def parse_adcmask(ctx, dword, fields):
	count = 0
	for ch in range(21):
		if fields.m & (1<<ch):
			count += 1
			# for tb in range ( ctx.ntb , 0, -3 ):
			for tb in range ( 0, ctx.ntb , 3 ):
				ctx.readlist.append([parse_adcdata(channel=ch, timebin=tb)])

	ctx.readlist.append([parse_mcmhdr, parse_eod])
	assert( count == (~fields.c & 0x1F) )



# ------------------------------------------------------------------------
# Raw data
class parse_adcdata:
	"""ADC data parser

	To parse ADC data, we need to know the channel number and the timebins
	in this dword. I don't think this data should be kept in the context.
	The parser for the MCM header / adcmask therefore stores it in the parser
	for the ADC data word. This parser therefore has to be a callable function.
	"""

	def __init__(self, channel, timebin):
		self.channel = channel
		self.timebin = timebin

	# @decode("xxxx:xxxx:xxyy:yyyy:yyyy:zzzz:zzzz:zzff")
	def __call__(self, ctx, dword):
		x = (dword & 0xFFC00000) >> 22
		y = (dword & 0x003FF000) >> 12
		z = (dword & 0x00000FFC) >>  2
		f = (dword & 0x00000003) >>  0

		desc = "ADCDATA   "
		desc += f"ch {self.channel:2} " if self.timebin==0 else " "*6
		desc += f"tb {self.timebin:2} (f={f})   {x:4}  {y:4}  {z:4}"

		return dict(description=desc)


# ------------------------------------------------------------------------
class LinkParser:

	end_of_tracklet = 0x10001000
	end_of_data     = 0x00000000


	#Defining the initial variables for class
	def __init__(self):
		pass

	def process(self,linkdata):
		'''
		Process the data from one optical link
        Parameter: linkdata = iterable list of uint32 data words
        '''

		ctx = ParsingContext
		ctx.readlist = [ list([parse_tracklet, parse_eot]) ]

		for i,dword in enumerate(linkdata):

			ctx.current_dword = i

			# if True:
			if False:
				for j,l in enumerate(ctx.readlist):
					print("*** " if i==j else "    ", end="")
					print( [ f.__name__ for f in ctx.readlist[j] ] )


			try:
				for fct in ctx.readlist[i]:

					# The function can raise an AssertionError to signal that
					# it does not understand the dword
					try:
						 result = fct(ctx,dword)

					except AssertionError as ex:
						continue


					# if result['description'].startswith("ch="): break
					# if result['description'].startswith("ADCMASK"): break

					# the function handled the dword -> we are done
					print(f"{ctx.current_dword:06x} {dword:08x}  ", end="")
					print(result['description'])

					break

			except IndexError:
				print()
				print("EXTRANEOUS DATA:")
				print("reached end of read list, but there is more data")
				break
