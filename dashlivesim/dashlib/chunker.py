from repack_poc.ewmedia.mp4 import mp4
from repack_poc.ewmedia.esf.boxes import *

import pdb


def decode_fragment(data):
    """
    :param data: CMAF Fragment 
    :return: Sample generator
    """
    root = mp4(data)
    moof = root.find('moof')
    tfhd = moof.find('traf.tfhd')
    tfdt = moof.find('traf.tfdt')
    trun = moof.find('traf.trun')

    base_data_offset = tfhd.base_data_offset if tfhd.has_base_data_offset else moof.offset
    data_offset = trun.data_offset if trun.has_data_offset else 0
    base_media_decode_time = tfdt.decode_time

    t0, t1 = base_media_decode_time, base_media_decode_time
    begin, end = 0, 0
    for entry in map(trun.sample_entry, range(trun.sample_count)):
        duration = entry['duration'] if trun.has_sample_duration else tfhd.default_sample_duration
        size = entry['size'] if trun.has_sample_size else tfhd.default_sample_size
        flags = int(entry['flags'], 0) if trun.has_sample_flags else tfhd.default_sample_flags
        time_offset = entry['time_offset'] if trun.has_sample_composition_time_offset else 0
        begin, end = end, end + size
        data = root.raw_data[base_data_offset+data_offset:][begin:end]
        t0, t1 = t1, t1 + duration
        yield Sample(data, t0, duration, flags & 0x2000000, time_offset)


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
    if part:
        yield part


def encode_chunked(seqno, track_id, samples, duration):
    for chunk_samples in partition(samples, duration):
        yield create_moof(seqno, track_id, chunk_samples, None)
        yield create_mdat(chunk_samples)


def chunk(data, duration):
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

    boxes = encode_chunked(seqno, track_id, decode_fragment(data), duration)
    for moof, mdat in zip(boxes, boxes):
        yield moof.serialize()+mdat.serialize()
