
import numpy
import re
from datetime import datetime
from typing import NamedTuple

class event_t(NamedTuple):
    timestamp: datetime
    subevents: tuple

class subevent_t(NamedTuple):
    # timestamp: datetime
    equipment_type: int
    equipment_id: int
    payload: numpy.ndarray


class o32reader:
    """Reader class for files in the .o32 format.

    The class can be used as an iterator over events in the file."""

    #Initial state variables:
    def __init__(self,file_name):

        self.filename = file_name

        self.line_number=0
        self.linebuf = None

        # self.HC_header=0

        # self.ev_timestamp = None

        # self.n_subevents = 0
        #
        # self.blk_sfp = None
        # self.blk_size = None
        # self.blk_unread = 0

    def __iter__(self):
        self.infile=open(self.filename, 'r')
        return self

    #Create dictionary
    def __next__(self):

        header = self.read_event_header()

        subevents = tuple([self.read_subevent() for i in range(header['data blocks'])])

        return event_t(header['time stamp'], subevents)


    def read_event_header(self):

        hdr = dict()

        line = self.read_line()
        if not line:
            raise StopIteration

        if line != '# EVENT':
            print(line)
            raise Exception('file format', 'invalid file format')

        # Extract header version number (should always be 1.0)
        m = re.search('# *format version: *(.*)', self.read_line())
        hdr['version'] = m.group(1)

        # The header version determines the names and order of the fields
        # in the header
        if hdr['version'] == '1.0':
            hdrfields = ('time stamp', 'data blocks')

        else:
            raise Exception('file format', 'unknown format version')


        for h in hdrfields:

            if h == 'time stamp':
                m = re.search('# *time stamp: *(.*)', self.read_line())

                hdr['time stamp'] = datetime.strptime( m.group(1),
                                                           '%Y-%m-%dT%H:%M:%S.%f')

            elif h == 'data blocks':
                m = re.search('# *data blocks: *(.*)', self.read_line())
                hdr['data blocks'] = int(m.group(1))

            else:
                raise Exception('FATAL', 'unknown header field')

        print(hdr)
        return hdr


    def read_subevent(self):

        subevent = dict()

        if self.read_line() != '## DATA SEGMENT':
            raise Exception('file format', 'invalid file format')

        m = re.match('## *sfp: *(.*)', self.read_line())
        equipment_type = 0x10
        equipment_id = int(m.group(1))

        m = re.search('## *size: *(.*)', self.read_line())
        payload_size = int(m.group(1))

        payload = numpy.zeros(payload_size, dtype=numpy.uint32)
        for i in range(payload_size):
            payload[i] = numpy.uint32(int(self.read_line(),0))

        return subevent_t(equipment_type, equipment_id, payload)



    def read_line(self):
        if self.linebuf is not None:
            tmp = self.linebuf
            self.linebuf = None
            return tmp
        else:
            self.line_number+=1
            self.lastline = self.infile.readline().rstrip()
            return self.lastline
