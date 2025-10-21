import collections

class StreamBuffer:
    def __init__(self, stream):
        self.stream = stream
        self.queue = collections.deque()
        self.last_presentation_timestamp = -1

    def add_packet(self, packet):
        if packet.dts == None:
            return
        self.queue.append((packet.pts, packet))

    def next_presentation_timestamp(self):
        if len(self.queue) == 0:
            return self.last_presentation_timestamp

        return self.queue[0][0]
    
    def read(self):
        if len(self.queue) == 0:
            raise ValueError("No packet available")
        
        timestamp, result = self.queue.popleft()
        self.last_presentation_timestamp = timestamp
        return result


