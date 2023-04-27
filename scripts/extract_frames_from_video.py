
import argparse
import cv2
import numpy as np
import os

def extract_by_skipping_frames(output_folder, video_path, skip_frames=0):
    # Create the output folder.
    os.makedirs(output_folder, exist_ok=True)
    
    # Open the video file.
    cap = cv2.VideoCapture(video_path)
    
    # Loop over all the frames. 
    frame_count = 0
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print(f'cap.read() returned {ret}')
            print(f'Break here. ')
            break
        
        frame_count += 1
        if frame_count % (skip_frames + 1) != 1:
            continue
        
        frame_path = f"{output_folder}/frame_{frame_count:06d}.jpg"
        cv2.imwrite(frame_path, frame)
        print(f'{frame_path} written. ')
    
    cap.release()

def extract_total_frames(
    output_folder, 
    video_path, 
    total_frames=100, 
    skip_beginning=15,
    skip_endding=15):
    # Create the output folder.
    os.makedirs(output_folder, exist_ok=True)
    
    # Open the video file.
    cap = cv2.VideoCapture(video_path)
    
    # Get the total number of frames in the video
    ori_total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    assert ori_total_frames - skip_beginning - skip_endding > total_frames, \
        f'Not enough frames to extract from {video_path}. '\
        f'ori_total_frames = {ori_total_frames}. '
    
    # Get the integer index of the frames to extract.
    indices_to_be_extracted = \
        np.unique(
            np.floor(
                np.linspace(
                    skip_beginning, 
                    ori_total_frames - skip_endding, 
                    total_frames ) 
            ).astype(np.int32) 
        )
    
    assert len(indices_to_be_extracted) >= total_frames, \
        f'Not enough unique indices in {video_path}. '\
        f'ori_total_frames = {ori_total_frames}. '
    
    # Loop over all the frames. 
    frame_count = 0
    count = 0
    next_frame_index = indices_to_be_extracted[count]
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print(f'cap.read() returned {ret}')
            print(f'Break here. ')
            break
        
        if frame_count != next_frame_index:
            frame_count += 1
            continue
        
        frame_path = f"{output_folder}/frame_{frame_count:06d}.png"
        cv2.imwrite(frame_path, frame)
        print(f'{frame_path} written. ')
        
        count += 1
        
        if count == len(indices_to_be_extracted):
            print(f'{total_frames} reached. Stop here. ')
            break
        
        next_frame_index = indices_to_be_extracted[count]
        frame_count += 1
    
    cap.release()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract frames from a video file.')
    
    parser.add_argument('outdir', type=str, 
                        help='The output folder. ')
    parser.add_argument('videopath', type=str,
                        help='The input video file. ')
    parser.add_argument('--frame_mode', type=str, default='fixed-skip',
                        help=f'The mode for skipping frames. Choose from: fixed-skip '
                             f'and total-frames. ')
    parser.add_argument('--skip_frames', type=int, default=0,
                        help=f'The number of frames to skip when --frame-mode is '
                             f'"fixed-skip". ')
    parser.add_argument('--total_frames', type=int, default=0,
                        help=f'The number of total frames to extract when --frame-mode is '
                             f'"total-number". ')
    
    args = parser.parse_args()
    
    if args.frame_mode == 'fixed-skip':
        extract_by_skipping_frames( args.outdir, args.videopath, args.skip_frames )
    elif args.frame_mode == 'total-frames':
        extract_total_frames( args.outdir, args.videopath, args.total_frames )
    else:
        raise ValueError(f'Unknown frame mode: {args.frame_mode}. '
                         f'Choose from: fixed-skip and total-number ')
    
    print('Done. ')
