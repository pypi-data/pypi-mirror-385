import argparse
import sys
import os
import json
from .storage import *
from .reader import *

def main():
    parser = argparse.ArgumentParser(
                    prog='scan-your-trash',
                    description='Tool to help with downloading and extracting Scan Your Trash samples',
                    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    sync_parser = subparsers.add_parser('sync', help='Download samples from storage to disk')
    sync_parser.add_argument('bucket_name')
    sync_parser.add_argument('destination')
    sync_parser.add_argument('--endpoint', default="https://landfill.scantrash.de")

    unpack_parser = subparsers.add_parser('unpack', help='Unpack a sample into pngs per frame')
    unpack_parser.add_argument('filename')
    unpack_parser.add_argument('destination', default=".")

    arguments = parser.parse_args(sys.argv[1:])
    if arguments.command == 'sync':
        for file in fetch_samples(arguments.bucket_name, destination = arguments.destination, endpoint = arguments.endpoint):
            print('.', end='', flush=True)

        print()
        return

    if arguments.command == 'unpack':
        with Reader(arguments.filename) as reader:
            metadata = reader.get_metadata()
            keywords = metadata.get('com.apple.quicktime.keywords', '').split(':')
            sample_type = 'unknown'
            if len(keywords) == 2 and keywords[0] == 'Trash with recycling code':
                sample_type = keywords[1].strip()
                if sample_type == '':
                    sample_type = 'unknown'
            
            prefix = os.path.join(arguments.destination, f"{os.path.basename(arguments.filename)}.type_{sample_type}")

            with open(f"{prefix}.meta.json", 'w') as f:
                json.dump(metadata, f)

            recycling_logo_image = reader.get_recycling_logo()
            if recycling_logo_image != None:
                recycling_logo_image.save(f"{prefix}.recycling_logo.png")
            for timestamp, main_frame, depth_frame, saliency_frame, object_mask, frame_meta in reader.get_samples():
                frame_prefix = f"{prefix}.frame_{str(timestamp).zfill(5)}"
                main_frame.save(f"{frame_prefix}.color.png")
                if depth_frame != None:
                    depth_frame.save(f"{frame_prefix}.depth.png")
                saliency_frame.save(f"{frame_prefix}.saliency.png")
                object_mask.save(f"{frame_prefix}.mask.png")
                
                with open(f"{frame_prefix}.frame_meta.json", 'w') as f:
                    json.dump(frame_meta, f)

                print('.', end='', flush=True)
            print()
            return
