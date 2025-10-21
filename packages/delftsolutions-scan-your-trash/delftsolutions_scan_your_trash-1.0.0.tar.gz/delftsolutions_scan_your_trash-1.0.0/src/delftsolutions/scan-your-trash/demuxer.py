import json
import numpy
import collections
import struct

class Demuxer:
    def __init__(self, container):
        self.container = container
        self.stream_buffers = []
        self.available_frames = collections.deque()
    
    def add_stream(self, stream):
        self.stream_buffers.append(StreamBuffer(stream))

    def add_packet(self, packet):
        for buffer in self.stream_buffers:
            if buffer.stream != packet.stream:
                continue
            buffer.add_packet(packet)

        min_next_presentation = 100000000
        min_last_emitted = 100000000

        for buffer in self.stream_buffers:
            next_presentation = buffer.next_presentation_timestamp()
            if next_presentation < min_next_presentation:
                min_next_presentation = next_presentation

            if buffer.last_presentation_timestamp < min_last_emitted:
                min_last_emitted = buffer.last_presentation_timestamp

        if min_next_presentation <= min_last_emitted:
            return

        frame = {}
        for buffer in self.stream_buffers:
            if buffer.next_presentation_timestamp() == min_next_presentation:
                frame[buffer.stream] = buffer.read()

        self.available_frames.append((min_next_presentation, frame))

    def has_frame(self):
        return len(self.available_frames) > 0

    def get_frame(self):
        if len(self.available_frames) == 0:
            return None
        return self.available_frames.popleft()

    @classmethod
    def parse_metadata(self, packet, meta_defs):
        buffer = bytes(packet)
        offset = 0
        result = []

        while offset < len(buffer):
            packet_length = int.from_bytes(buffer[offset:(offset + 4)], byteorder='big')
            metadata_type = int.from_bytes(buffer[(offset + 4):(offset + 4 + 4)], byteorder='big')
            packet = buffer[(offset + 4 + 4):(offset + packet_length)]
            offset += packet_length

            if metadata_type in meta_defs:
                identifier, metadata_parser = meta_defs[metadata_type]
                
                if metadata_parser == "json":
                    result.append((identifier, json.loads(packet.decode('utf-8'))))
                    continue
                
                if metadata_parser == "float32":
                    parsed = struct.unpack('>f', packet)[0]
                    result.append((identifier, parsed))
                    continue

            result.append((f"<unknown: {metadata_type}>", packet))

        return result

    @classmethod
    def demux_container(self, container, streams, meta_defs):
        demuxer = Demuxer(container)
        for stream in streams:
            demuxer.add_stream(stream)

        for packet in container.demux(streams):
            demuxer.add_packet(packet)

            if demuxer.has_frame():
                frame_timestamp, decodable_frame = demuxer.get_frame()

                available_streams = decodable_frame.keys()
                for stream in available_streams:
                    if stream.type == 'video':
                        decodable_frame[stream] = decodable_frame[stream].decode()
                    if stream.type == 'data':
                        if stream in meta_defs:
                            decodable_frame[stream] = self.parse_metadata(decodable_frame[stream], meta_defs[stream])
                        else:
                            decodable_frame[stream] = self.parse_metadata(decodable_frame[stream], {})
                
                yield (frame_timestamp, decodable_frame)

