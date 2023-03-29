
import argparse
import cv2
import os

def extract_frames(output_folder, video_path, skip_frames=0):
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
    
    cap.release()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract frames from a video file.')
    
    parser.add_argument('output_folder', type=str, 
                        help='The output folder. ')
    parser.add_argument('video_path', type=str,
                        help='The input video file. ')
    parser.add_argument('--skip_frames', type=int, default=0,
                        help='The number of frames to skip. ')
    
    args = parser.parse_args()
    
    extract_frames( args.output_folder, args.video_path, args.skip_frames )
    
    print('Done. ')
