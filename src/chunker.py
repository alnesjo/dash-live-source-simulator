from repack_poc.ewmedia.mp4 import mp4
from repack_poc.ewmedia.esf.boxes import *


def decode_fragment(data):
    """
    :param data: CMAF Fragment 
    :return: Sample generator
    """
    root = mp4(data)
    moof = root.find('moof')
    tfhd = moof.find('traf.tfhd')
    trun = moof.find('traf.trun')

    base_data_offset = tfhd.base_data_offset if tfhd.has_base_data_offset else moof.offset
    data_offset = trun.data_offset if trun.has_data_offset else 0

    t0, t1 = 0, 0
    begin, end = 0, 0
    for i in range(trun.sample_count):
        entry = trun.sample_entry(i)
        begin, end = end, end + entry['size']
        data = root.raw_data[base_data_offset+data_offset:][begin:end]
        duration = entry['duration']
        t0, t1 = t1, t1 + duration
        time_offset = entry['time_offset']
        sync = int(entry['flags'],0) & 0x2000000
        yield Sample(data, t0, duration, sync, time_offset)


def partition(samples, duration):
    d0, d1 = 0, duration
    part = []
    for sample in samples:
        if d0 >= d1:
            d1 += duration
            yield part
            part = []
        d0 += sample.duration
        part.append(sample)


def encode_chunked(seqno, track_id, samples, duration):
    for chunk_samples in partition(samples, duration):
        yield create_moof(seqno, track_id, chunk_samples, None)
        yield create_mdat(samples)


def chunk(data, duration=MOVIE_TIMESCALE):
    """
    :param data: CMAF Fragment
    :param duration: Target chunk duration
    :return: Chunked CMAF Segment
    """
    root = mp4(data)
    mfhd = root.find('moof.mfhd')
    tfhd = root.find('moof.traf.tfhd')

    seqno = mfhd.seqno
    track_id = tfhd.track_id

    return BoxSequence(create_styp(),
                       *encode_chunked(seqno,
                                       track_id,
                                       decode_fragment(data),
                                       duration))


def chunk_file(input,output,duration):
    data = open(input, 'rb').read()
    chunked = chunk(data, duration)
    open(output, 'wb').write(chunked)
