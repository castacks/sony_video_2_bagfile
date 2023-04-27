
import argparse
import cv2
import glob
import numpy as np
import os
import yaml

class PinholeModel(object):
    def __init__(self):
        super().__init__()
        
        self.K = np.eye(3, dtype=np.float32) # Intrinsics matrix.
        self.D = np.zeros(4, dtype=np.float32) # Distortion coefficients.
        self.shape = [0, 0] # Shape of the image, [H, W].

    def __str__(self):
        return \
            f'PinholeModel: \n'\
            f'K = \n'\
            f'{self.K}\n'\
            f'D = {self.D}\n'\
            f'shape = {self.shape}'
            
    def as_kalibr(self):
        kalibr_dict = {
            'cam0': {
                'camera_model': 'pinhole',
                'distortion_coeffs': self.D.tolist(),
                'distortion_model': 'radtan',
                'intrinsics': [ float(self.K[0, 0]), float(self.K[1, 1]) ] + self.K[0:2, 2].tolist(),
                'resolution': self.shape[::-1],
            } }
        return kalibr_dict

def write_yaml(fn: str, d: dict):
    with open(fn, 'w') as f:
        yaml.dump(d, f, default_flow_style=False)

def read_kalibr(fn):
    # Load the calibration result from the YAML file.
    with open(fn, 'r') as f:
        calib = yaml.load(f, Loader=yaml.FullLoader)
    
    calib = calib['cam0']
    
    assert calib['camera_model'] == 'pinhole', \
        f'calib["camera_model"] = {calib["camera_model"]}. '
        
    assert calib['distortion_model'] == 'radtan', \
        f'calib["distortion_model"] = {calib["distortion_model"]}. '
        
    pinhole_model = PinholeModel()
    pinhole_model.K[0, 0] = calib['intrinsics'][0]
    pinhole_model.K[1, 1] = calib['intrinsics'][1]
    pinhole_model.K[0, 2] = calib['intrinsics'][2]
    pinhole_model.K[1, 2] = calib['intrinsics'][3]
    
    pinhole_model.D = np.array( calib['distortion_coeffs'] ).astype(np.float32)

    pinhole_model.shape = [
        calib['resolution'][1],
        calib['resolution'][0] ]
    
    return pinhole_model

def get_new_shape_and_crop_column_range(ori_shape, new_height):
    ori_h, ori_w = ori_shape
    assert ori_h < ori_w, f'ori_h = {ori_h}, ori_w = {ori_w}. '
    assert ori_h > new_height, f'ori_h = {ori_h}, new_height = {new_height}. '
    
    new_width = int( new_height * ori_w / ori_h )
    crop_left = int( (new_width - new_height) / 2 )
    return [new_height, new_width], [ crop_left, crop_left + new_height ]

def calculate_new_camera_matrix_and_remap_grids(
    original_shape, 
    new_shape, 
    camera_matrix, 
    distortion_coeffs):
    
    new_cam_matrix, roi = cv2.getOptimalNewCameraMatrix(
        camera_matrix,
        distortion_coeffs,
        imageSize=( original_shape[1], original_shape[0] ),
        alpha=0.0,
        newImgSize=( new_shape[1], new_shape[0] ) )
    
    print(f'roi = {roi}. ')
    
    map0, map1 = cv2.initUndistortRectifyMap(
        camera_matrix,
        distortion_coeffs,
        R=None,
        newCameraMatrix=new_cam_matrix,
        size=( new_shape[1], new_shape[0] ),
        m1type=cv2.CV_32FC1)
    
    new_pinhole_model = PinholeModel()
    new_pinhole_model.K = new_cam_matrix
    new_pinhole_model.shape = new_shape
    
    return new_pinhole_model, map0, map1    

def find_files(d):
    files = sorted(glob.glob(os.path.join(d, 'frame_*.png'), recursive=False))
    assert len(files) > 0, f'No files found in {d}. '
    return files

def read_image(fn):
    img = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    assert img is not None, f'Cannot read {fn}. '
    return img

def handle_args():
    parser = argparse.ArgumentParser(
        description='Sample and crop the images inside a folder. ')
    
    parser.add_argument('indir', type=str, 
                        help='The input directory. ')
    
    parser.add_argument('outdir', type=str,
                        help='The output directory. ')
    
    parser.add_argument('calib_file', type=str, 
                        help='The calibration file in Kalibr format. ')
    
    parser.add_argument('--new_height', type=int, default='512', 
                         help='The new height. ')
    
    return parser.parse_args()

if __name__ == '__main__':
    args = handle_args()
    
    os.makedirs(args.outdir, exist_ok=True)
    
    # Prepare the mappings for cv2.remap.
    pinhole_model = read_kalibr(args.calib_file)
    print(f'Input camera model: \n{pinhole_model}')
    
    # Figure out the new shape of the camera model, and the crop size.
    new_shape, crop_col_range = get_new_shape_and_crop_column_range(
        pinhole_model.shape, args.new_height )
    
    print('')
    print(f'new_shape = {new_shape} \ncrop_col_range = {crop_col_range}. ')
    
    new_cam_model, map0, map1 = calculate_new_camera_matrix_and_remap_grids(
        pinhole_model.shape, new_shape, pinhole_model.K, pinhole_model.D )
    
    print('')
    print(f'new_cam_model = \n{new_cam_model}. ')
    
    in_images = find_files(args.indir)
    
    for fn in in_images:
        print(f'{fn}')
        
        img = read_image(fn)
        
        sampled = cv2.remap(
            img,
            map0, 
            map1,
            cv2.INTER_LINEAR)
        
        croppped = sampled[:, crop_col_range[0]:crop_col_range[1], ...]
        
        out_fn = os.path.join(args.outdir, os.path.basename(fn))
        cv2.imwrite(out_fn, croppped)
        
    # Save the final camera intrinsics for the cropped images.
    new_cam_model.K[0, 2] -= crop_col_range[0]
    new_cam_model.shape = [args.new_height, args.new_height]
    
    out_fn = os.path.join(args.outdir, 'calib.yaml')
    write_yaml(out_fn, new_cam_model.as_kalibr())
    
    print('')
    print(f'The camera intrinsics after cropping is \n{new_cam_model}')
    