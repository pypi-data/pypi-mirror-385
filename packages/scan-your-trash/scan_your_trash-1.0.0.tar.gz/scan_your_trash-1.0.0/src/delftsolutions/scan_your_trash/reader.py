#!/usr/bin/env python3

import av
import json
import math
import PIL.Image
import numpy
import io
import collections
from .demuxer import *

class Reader:
    def __init__(self, file):
        self._fileref = file
        self._container_mgr = None
        self._container = None
        self._recycling_logo = None

    def __enter__(self):
        if self._container != None:
            raise ValueError("Sample is opened twice, this is not supported.")

        self._container_mgr = av.open(self._fileref, format='mov')
        self._container = self._container_mgr.__enter__()

        self.get_recycling_logo()
        return self

    def __exit__(self, *args):
        if self._container == None:
            raise ValueError("Sample is already closed")
        
        self._container = None
        return self._container_mgr.__exit__(*args)
    
    def get_recycling_logo(self):
        if self._container == None:
            raise ValueError("Unable to get samples from unopened reader")

        if self._recycling_logo != None:
            return self._recycling_logo

        image_streams = []
        for stream in self._container.streams:
            if stream.type == 'video' and stream.codec.name == 'mjpeg':
                image_streams.append(stream)

        if len(image_streams) < 2:
            return None

        for frame in self._container.decode(image_streams[1]):
            self._recycling_logo = frame.to_image()
            return self._recycling_logo
    
        return None


    @classmethod
    def compute_mask(self, frame, saliency_frame, frame_meta):
        if "targetPosition.camera_space" not in frame_meta:
            return None

        main_size = (frame.width, frame.height)
        saliency_pixels = numpy.asarray(saliency_frame) / 255.0
        saliency_size = saliency_pixels.shape[0:2]
        saliency_pixel_size = (main_size[0] / saliency_size[0], main_size[1] / saliency_size[1])
        target_pos = frame_meta["targetPosition.camera_space"]
        target_y = saliency_size[1] * (target_pos["y"] + 1) / 2.0
        target_x = saliency_size[0] * (target_pos["x"] + 1) / 2.0
        round_target_x = int(round(target_x))
        round_target_y = int(round(target_y))

        small_mask = numpy.zeros((saliency_size[0], saliency_size[1], 3))

        circle_width = min(frame.width, frame.height) * 0.3 / -target_pos["z"]
        circle_feather = 0.3

        fill_queue = []

        start_point_x = round_target_x
        start_point_y = round_target_y
        connected_threshold = 0.1

        if saliency_pixels[round_target_y][round_target_x][0] < connected_threshold:
            # Search for starting point close by if the computed starting point is uninteresting
            best_pixel = 100000000
            for y in range(-6, 7):
                dest_y = round_target_y + y
                if dest_y >= saliency_size[1] or dest_y < 0:
                    continue
                for x in range(-6, 7):
                    dest_x = round_target_x + x
                    if dest_x >= saliency_size[0] or dest_y < 0:
                        continue

                    pixel_value = saliency_pixels[dest_y][dest_x][0]
                    if pixel_value < connected_threshold:
                        continue
                    
                    score = (math.sqrt(x*x + y*y) + 1) / ((pixel_value + 0.0001) ** 2)
                    if score < best_pixel:
                        best_pixel = score
                        start_point_x = dest_x
                        start_point_y = dest_y


        small_mask[start_point_y][start_point_x][2] += 0.333
        small_mask[round_target_y][round_target_x][2] += 0.666

        small_mask[:,:,1] = saliency_pixels[:,:,0]

        visited = set()
        fill_queue.append((start_point_x, start_point_y))

        while len(fill_queue) > 0:
            coord = fill_queue.pop()
            if coord in visited:
                continue
            x = coord[0]
            y = coord[1]

            if x < 0 or x >= saliency_size[0]:
                continue
            if y < 0 or y >= saliency_size[0]:
                continue

            visited.add(coord)

            pixel_distance_x = saliency_pixel_size[0] * abs(x - target_x)
            pixel_distance_y = saliency_pixel_size[1] * abs(y - target_y)
            pixel_distance = math.sqrt(pixel_distance_x * pixel_distance_x + pixel_distance_y * pixel_distance_y)

            circle_amount = 1.0 - min(1.0, max(0.0, (pixel_distance - circle_width) / (circle_width * circle_feather)))

            result = saliency_pixels[y][x][0] * circle_amount
            small_mask[y][x][0] = result

            if result >= connected_threshold:
                fill_queue.append((x - 1, y))
                fill_queue.append((x + 1, y))
                fill_queue.append((x, y - 1))
                fill_queue.append((x, y + 1))

        return PIL.Image.fromarray((small_mask * 255.0).astype(numpy.uint8)).resize(main_size, resample=PIL.Image.NEAREST)
    
    def get_metadata(self):
        if self._container == None:
            raise ValueError("Unable to get metadata from unopened reader")

        return self._container.metadata


    def get_samples(self, compute_mask = True):
        if self._container == None:
            raise ValueError("Unable to get samples from unopened reader")

        container = self._container

        main_stream = None
        depth_stream = None
        saliency_stream = None
        for stream in container.streams.video:
            if stream.codec.name == 'png':
                continue

            if stream.codec.name == 'prores':
                main_stream = stream
                continue

            if stream.codec.name == 'mjpeg':
                if stream.width >= 1920 and main_stream == None:
                    main_stream = stream

            if stream.codec.name == 'hevc':
                # Not very robust but can't think of a better way
                if stream.width == 68:
                    saliency_stream = stream
                else:
                    if stream.width >= 1920:
                        main_stream = stream
                    else:
                        depth_stream = stream

        realtime_datastream = container.streams.data[0]
        analysed_datastream = container.streams.data[1]
        metadata_defs = {
            #[(1, b'{"x":0.65620893239974976,"y":0.31595063209533691,"z":-0.54826480150222778}\x00\x00\x00R'), (2, b'{"x":0.32552766799926758,"y":-0.05249331146478653,"z":0.31045728921890259}\x00\x00\x00O'), (3, b'{"x":-1.268170952796936,"y":3.0191268920898438,"z":-1.7532858848571777}\x00\x00\x00\x0c'), (4, b'\x00\x00\x00\x00\x00\x00\x00\x0c'), (5, b'@\xd8z\xe1\x00\x00\x00\x0c'), (6, b';\xd7\x946\x00\x00\x00\x0c'), (7, b'?\xd4\xf5\xe8\x00\x00\x00\x0c'), (8, b'\x00\x00\x00\x00\x00\x00\x00\x0c'), (9, b'@\xe8\x14\xb6\x00\x00\x00\x0c'), (10, b'@\xae\xe75\x00\x00\x010'), (11, b'{"matrix4x4":[[-0.9548676609992981,-0.054085470736026764,-0.29206544160842896,0.39867055416107178],[-0.29479146003723145,0.29307848215103149,0.90950691699981689,-0.17101562023162842],[0.036406967788934708,0.95455735921859741,-0.29579511284828186,0.13008816540241241],[0,0,0,0.99999988079071045]]}')]
            realtime_datastream: {
                1: ("targetPosition.camera_space", "json"),
                2: ("camera.euler_rotation", "json"),
                3: ("camera.position", "json"),
                4: ("camera.exposure_bias", "float32"),
                5: ("camera.focal_length", "float32"),
                6: ("camera.exposure_time", "float32"),
                7: ("camera.aperture_value", "float32"),
                8: ("camera.white_balance", "float32"),
                9: ("camera.shutter_speed", "float32"),
                10: ("camera.brightness", "float32"),
                11: ("camera.view_matrix", "json"),
            },
            #[(2, b'{"boundingBox":{"right":0.7694083424803202,"top":0.2406140706541795,"left":0.80745554490850213,"bottom":0.28271773914964027},"text":"privr y","confidence":0.30000001192092896}\x00\x00\x00\xb8'), (2, b'{"boundingBox":{"right":0.77819767464012102,"top":0.30284237866665475,"left":0.79738372036626137,"bottom":0.34315245421461482},"text":"Aultan","confidence":0.30000001192092896}\x00\x00\x00\xc6'), (2, b'{"boundingBox":{"right":0.67360876894997945,"top":0.31953059881881118,"left":0.7698770810863117,"bottom":0.39723334715277747},"text":"(till us chit it pla)","confidence":0.30000001192092896}\x00\x00\x00\xbf'), (2, b'{"boundingBox":{"right":0.54298023306814991,"top":0.058284112390403098,"left":0.5590735398082749,"bottom":0.15561713743968331},"text":"it code neges","confidence":0.30000001192092896}\x00\x00\x00\xa8'), (2, b'{"boundingBox":{"right":0.61927935210170115,"top":0.23591252542507946,"left":0.62027668194648389,"bottom":0.13092039005927547},"text":"PROVISOR","confidence":1}\x00\x00\x00\xb6'), (2, b'{"boundingBox":{"right":0.40880415863941244,"top":0.61246743139997351,"left":0.44417639600386349,"bottom":0.61895418546418024},"text":"ntos","confidence":0.30000001192092896}\x00\x00\x00G'), (3, b'{"classification":"structure","confidence":0.79961663484573364}')]}
            analysed_datastream: {
                1: ("barcode", "json"),
                2: ("text_element", "json"),
                3: ("classification", "json"),
            }
        }
        
        if main_stream == None:
            raise ValueError("Given sample does not contain a main stream.")
        

        for timestamp, frame in Demuxer.demux_container(container, [x for x in [main_stream, depth_stream, saliency_stream, realtime_datastream, analysed_datastream] if x is not None], metadata_defs):
            frame_meta = {}
            if realtime_datastream != None and realtime_datastream in frame:
                for identifier, value in frame[realtime_datastream]:
                    frame_meta[identifier] = value
            
            if analysed_datastream != None and analysed_datastream in frame:
                for identifier, value in frame[analysed_datastream]:
                    if identifier == "classification":
                        frame_meta[identifier] = value
                    else:
                        if identifier not in frame_meta:
                            frame_meta[identifier] = []
                        frame_meta[identifier].append(value)

            main_frame = None
            if main_stream != None and main_stream in frame:
                main_frame = frame[main_stream][0].to_image()
            depth_frame = None
            if depth_stream != None and depth_stream in frame:
                depth_frame = frame[depth_stream][0].to_image()
            saliency_frame = None
            if saliency_stream != None and saliency_stream in frame:
                saliency_frame = frame[saliency_stream][0].to_image()

            object_mask = None
            if compute_mask and main_frame != None and saliency_frame != None:
                object_mask = self.compute_mask(main_frame, saliency_frame, frame_meta)

            if main_frame == None:
                continue

            yield (timestamp, main_frame, depth_frame, saliency_frame, object_mask, frame_meta)


