
# Capture a video

## Using the Canon camera

- Select the full manual mode to gain access to exposure control.
- Use low exposure time to reduce motion blur.
- Select 29Hz frame rate instead of 25Hz to reduce lighting flickering while in the office area.
- Use the 18mm focal length.
- Use the regional focus mode.
- Use FHD resolution.

# Extract image frames from the video

# Assemble image frames to a bagfile

Do something like

```bash
roslaunch sony_video_2_bagfile assmeble_frames.launch \
    image_folder:=/home/yaoyuh/Playground/sony/calib_canon/extracted_frames \
    out_bag_fn:=/home/yaoyuh/Playground/sony/calib_canon/assembled_bagfile/cannon_20230328.bag
```

