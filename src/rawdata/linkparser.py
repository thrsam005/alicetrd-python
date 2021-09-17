import numpy as np
import math
from struct import unpack
#import pylab as pl

from functools import wraps
import functools
# from collections import namedtuple
from typing import NamedTuple


# class datafmt_error(Exception):
#
# 	def __init__(self, text):
# 		self.text = text
#
# 	def __str__(self):
# 		return "data format error: "+self.text
#

class parsefct:

	def __init__(self, compare=None, mask=0xFFFFFFFF, next=None, fmt=None, **kwargs):
		self.compare = compare
		self.mask = mask
		self.expect_next = next
		self.fmt = fmt
		# self.__name__ = self.func.__name__

	def __call__(self, func):

		# The actual function that will be called
		def wrapper(ctx,dword):
			if (dword & self.mask) != self.compare:
				return False
			retval = func(ctx,dword)
			if retval is None:
				retval = True

			if retval:

				if self.fmt is not None:
					print(self.fmt.format(**ctx.asdict(ctx)))

				if self.expect_next is not None:
					ctx.expect_next = self.expect_next
			return retval

		# set a readable name (mostly for debugging)
		wrapper.__name__ = func.__name__

		# Replace the dummy function `parsefct.myself`
		#
		# This is necessary, because the function is not yet known when the
		# decorator arguments are called.
		if self.expect_next is not None:
			for i,x in enumerate(self.expect_next):
				if x == parsefct.myself:
					self.expect_next[i] = wrapper

		return wrapper


	def myself():
		'''Function to be used as a placeholder in next'''
		pass

class ParsingContext:

	# major : int
	# minor : int
	# nhw   : int
	# sm    : int
	# layer : int
	# stack : int
	# side  : int
	# expect_next : list

	def __init__(self, *args):
		self.expect_next = args

	def asdict(self):

		side_str = 'A' if self.side==0 else 'B'
		hc_str = f"{self.sm:02}_{self.stack}_{self.layer}{side_str}"
		ver_str = f"0x{self.major:02X}.{self.minor:02X}"

		return dict(major=self.major, minor=self.minor, nhw=self.nhw,
		  sm=self.sm, layer=self.layer, stack=self.stack, side=self.side,
		  ntb = self.ntb, bc_counter=self.bc_counter,
		  pre_counter=self.pre_counter, pre_phase=self.pre_phase,
		  side_str=side_str, hc_str=hc_str, ver_str=ver_str
		)

	def hcid(self):
		side = 'A' if self.side==0 else 'B'
		return f"{self.sm:02}_{self.stack}_{self.layer}{side}"


	def ver_str(self):
		return f"0x{self.major:02X}.{self.minor:02X}"




def skip_until_eod(ctx, dword):
	if dword == 0x00000000:
		print(f"EOD")
		ctx.expect_next = [ skip_until_eod ]
		# state.expect_next = [ parse_eod ]
		return True
	else:
		print(f"... skip parsing ...")
		ctx.expect_next = [ skip_until_eod ]
		return True


def parse_tracklet(state, dword):
	if dword == 0x10001000:
		return False
	else:
		print("tracklet")
		return True

# def hcid(ctx):
# 	side = 'A' if self.side==0 else 'B'
# 	return f"{self.sm:02}_{self.stack}_{self.layer}{side}"


@parsefct(compare=0x80000001, mask=0x80000003)
# fmt="HC0 {hc_str} ver={ver_str} nw={nhw}")
def parse_hc0(ctx, dword):

	ctx.major = (dword >> 24) & 0x7f
	ctx.minor = (dword >> 17) & 0x7f
	ctx.nhw   = (dword >> 14) & 0x7
	ctx.sm    = (dword >>  9) & 0x7
	ctx.layer = (dword >>  6) & 0x1f
	ctx.stack = (dword >>  3) & 0x3
	ctx.side  = (dword >>  2) & 0x1

	print(f"HC0 {ctx.hcid(ctx)} ver={ctx.ver_str(ctx)} nw={ctx.nhw}")

	if ctx.nhw >= 1:
		ctx.expect_next = [ parse_hc1 ]
	else:
		ctx.expect_next = [ parse_mcm_h0 ]
	return True


@parsefct(compare=0x10001000, next=[parsefct.myself, parse_hc0])
def parse_eot(ctx, dword):
	print(f"EOT")
	# ctx.expect_next = [parse_eot, parse_hc0]


@parsefct(compare=0x00000001, mask=0x00000003,
fmt="HC2 tb={ntb} bc={bc_counter} pre={pre_counter} phase={pre_phase}")
def parse_hc1(ctx, dword):

	ctx.ntb         = (dword >> 26) & 0x3f
	ctx.bc_counter  = (dword >> 10) & 0xffff
	ctx.pre_counter = (dword >>  6) & 0xF
	ctx.pre_phase   = (dword >>  2) & 0xF

	if ctx.nhw >= 2:
		ctx.expect_next = [ parse_hc2 ]
	else:
		# self.expect_next = [ self.parse_mcm_h0 ]
		ctx.expect_next = [ skip_until_eod ]
	return True


#
# def parse_hc2(self):
# 	if (self.x & 0x0000003F) != 0x00000031:
# 		return False
# 	print(f"HC2 filter settings")
# 	if self.nhw >= 3:
# 		self.expect_next = [ self.parse_hc3 ]
# 	else:
# 		# self.expect_next = [ self.parse_mcm_h0 ]
# 		self.expect_next = [ self.skip_until_eod ]
# 	return True
#
# def parse_hc3(self):
# 	if (self.x & 0x0000003F) != 0x00000035:
# 		return False
# 	print(f"HC2 svn revision")
# 	# self.expect_next = [ self.parse_mcm_h0 ]
# 	self.expect_next = [ self.skip_until_eod ]
# 	return True


class LinkParser:

	end_of_tracklet = 0x10001000
	end_of_data     = 0x00000000


	#Defining the initial variables for class
	def __init__(self):
		pass
		# self.data=np.zeros((16,144,30))
        # self.clean_data=np.zeros((16,144,30))

        # self.HC_header=0
        # self.HC1_header=0
        # self.ntb=30
        # self.MCM_header=0
		#
        # self.line=-1
        # self.sfp=0
		#
        # self.debug = 0



			#
			#         #print('HC1_header: ',self.HC1_header)
			#
			#         self.ntb=(int(hex(self.HC1_header)[0:10],0)>>26)&0x3F
			#         for i in range(1,hw):
			#             check=self.get_dword(dic)
			#
			#
			#     if hw >= 2:
			#         hc2 = self.get_dword(dic)
			#
			#     if hw >= 3:
			#         hc3 = self.get_dword(dic)
			#
			#     if self.debug > 5:
			#         print ( "HC %02d_%d_%d%s: fmt %d.%d - %d TBs - %d %d hdr words" %
			#                 (self.sm,self.stack,self.layer,self.sidestr,
			#                  self.major,self.minor,
			#                  self.ntb, self.nhw, hw) )
			#
			#
			#
			#
			# def extract_mcm_data(self,dic):
			#
			#     '''
			#     Parameter:rdr = Rawreader variable
			#
			#     Extracts MCM header and all the mcm data that follows under the header
			#     '''
			#
			#     mcmhdr = self.get_dword(dic)
			#     self.MCM_header=mcmhdr
			#
			#     if self.debug >= 7:
			#         print(f'MCM header @ line {self.line}: 0x{mcmhdr:08X}')
			#
			#     self.robpos   = (mcmhdr >> 28) & 0x7
			#     self.mcmpos   = (mcmhdr >> 24) & 0xF
			#     self.mcmevent = (mcmhdr >> 4) & 0xFFFFF
			#
			#     if self.major & (1<<5):
			#         # self.adcmask = self.get_dword(dic)
			#         self.adcmask = (self.get_dword(dic) >> 4) & 0x01FFFFF
			#     else:
			#         self.adcmask = 0x01FFFFF
			#
			#     if self.debug >= 7:
			#         print(f'MCM {self.robpos}:{self.mcmpos:02d} '+
			#               f'ADCmask=0x{self.adcmask:08X}   event #{self.mcmevent}')
			#
			#
			#     #Cycle throught 21 channels per mcm
			#     for ch in range(0,21):
			#
			#         if (self.adcmask & (1<<ch)) == 0:
			#             continue
			#
			#         if self.debug >= 8:
			#             print ("  reading ADC %d (0x%08x)" % (ch, (1<<(ch+4))))
			#
			#         #Cycle through number of words (timebin) associated with the mcm
			#         for i in range(0,adcarray.N_words(self.ntb)):
			#
			#             dword=self.get_dword(dic)
			#             tb=i*3
			#
			#
			#             if ch>=0 and ch < 18:
			#             #Extract and save data in 3D array
			#                 self.parse_adcword(dword,tb,ch)


	def process(self,linkdata):
		'''
		Process the data from one optical link
        Parameter: linkdata = iterable list of uint32 data words
        '''

		ctx = ParsingContext
		ctx.expect_next = [ parse_tracklet, parse_eot ]

		for i,dword in enumerate(linkdata):

			# print( [ f.__name__ for f in ctx.expect_next ] )

			print(f"{i:06x} {dword:08x}  ", end="")

			for fct in ctx.expect_next:
				if fct(ctx, dword):
					break
			else:
				print("NO MATCH")
				expc="???"


	# def parse_tracklet():





#         for sfp in [0,1]:
#             self.sfp=sfp
#             self.line=-1
#
#             if dic['datablocks'][self.sfp]['raw'].size == 0:
#                 continue
#
#             # Skip tracklets
#             c=0
#             while c!=2:
#                 line=self.get_dword(dic)
#                 # print(hex(line))
#
#                 if line == adcarray.end_of_tracklet:
#                     c+=1
#
#
#             #Read HC_header:
#             self.read_hc_header(dic)
#
#
#             #Cycle through MCM data in data stream
#             while self.peek_dword(dic) != adcarray.end_of_data:
#                 self.extract_mcm_data(dic)
#
#
#             # Read all end of data markers
#             while self.line < dic['datablocks'][self.sfp]['raw'].size-1:
#                 if self.get_dword(dic) != adcarray.end_of_data:
#                     raise datafmt_error(f'data after end-of-data marker in SFP {self.sfp} line {self.line} of {maxline}')
#
#         return
#
#
# 	#Takes dword and reads information into a 3D cube
#     def parse_adcword(self,dword,tb,ch):
#         '''
#         Extract information from dword, and read it into the 3D data cube
#         Parameters:
#                 dword=MCM_data dword
#                 tb=time_bin the dword is associated with
#                 ch=channel from where the data comes from
#         writes: self.data 3D cube
#         '''
#         #Find position
#         col,row = adcarray.conv(self.robpos,self.mcmpos,ch)
#
#         #from dword, write into self.data
#         self.data[row][col][tb+2]=(dword>>22)& 0x3ff
#         self.data[row][col][tb+1]=(dword>>12)& 0x3ff
#         self.data[row][col][tb]=(dword>>2)& 0x3ff
#
#
#
#
#
#     # def get_adc(self,row,col,ch,tb):
# 	#
#     #     '''
#     #     Works on a 12x144xtb 3D data cube:
# 	#
#     #             row: dimension 0-11 (y-direction of adc)
#     #             col: dimension 0-7 (x-direction of adc)
#     #             ch: channel number of adc
#     #             tb:  # of timebin
# 	#
#     #     returns value in data cube
#     #     '''
# 	#
#     #     return self.data[row][col*18+ch][tb]
#
#
#     # #Extract position form pos(sel)
#     #     def pos_ex(self):
#     #
#     #         '''
#     #         Extracts read_out_board and adc position from mcm_header
#     #         returns: read_out_board,MCM_position
#     #         '''
#     #
#     #         ROB=(int(hex(self.MCM_header),0)>>28) & 0x7
#     #         MCMpos=(int(hex(self.MCM_header),0)>>24) & 0xF
#     #
#     #         return ROB,MCMpos
#
#
# #
# #     #X-coordinate
# #     def xc(self,ROB,MCMpos):
# #
# #         '''
# #         Parameters: ROB = read_out_board
# #                 MCMpos = MCM_position
# #
# #         Returns x-coordinate of position on the trd board
# #         '''
# #
# #         return 7-(4*(ROB%2) + MCMpos%4)
# #
# # #Y-coordinate
# #     def yc(self,ROB,MCMpos):
# #
# #         '''
# #         Parameters: ROB = read_out_board
# #                 MCMpos = MCM_position
# #
# #         Returns y-coordinate of position on the trd board
# #         '''
# #
# #         return 4*(math.floor(ROB/2)) + math.floor(MCMpos/4)
#
#
#     #Covert Readout board and ADC to X/Y-pos
#     def conv(rob,mcm,ch):
#         '''
#         Converts read_out_board and mcm to x and y positions
#         Parameters:
#                     rob = Readout board
#                     mcm = MCM position on ROB
#                     ch  = channel within MCM
#
#         returns: x,y position
#         '''
#
#         mcmcol = 7-(4*(rob%2) + mcm%4)
#         row = 4*(math.floor(rob/2)) + math.floor(mcm/4)
#         col = 18*mcmcol + ch - 1
#
#         return col,row
#
# # #Find position on board
# #     def pos(self):
# #         '''
# #         Finds x,y position from MCM_header
# #         returns x,y coordinates
# #         '''
# #         ROB,MCMpos = self.pos_ex()
# #         #x,y = self.conv(ROB,MCMpos)
# #         #print("%02d:%02d -> %02d/%03d     MCM hdr: %08x" % (ROB,MCMpos,x,y,self.MCM_header))
# #         return self.conv(ROB,MCMpos)
#
# #Find Number of words from Number of timebins
#     def N_words(Nt):
#         '''
#         Calculates the number of dwords, given the number of time_bins
#         Parameter: Nt = Number of time_bins
#         '''
#         return math.floor((Nt-1)/3) + 1
#
#
#
#
#     def reset(self):
#         '''
#         Resets initial varaiables associated with the adcarray data
#         '''
#
#         self.data=np.zeros((16,144,30))
#
#         self.HC_header=0
#         self.HC1_header=0
#         self.ntb=0
#         self.MCM_header=0
