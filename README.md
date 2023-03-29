
# Capture a video

## Using the Canon camera

- Select the full manual mode to gain access to exposure control.
- Use low exposure time to reduce motion blur.
- Select 29Hz frame rate instead of 25Hz to reduce lighting flickering while in the office area.
- Use the 18mm focal length.
- Use the regional focus mode.
- Use FHD resolution.

# Extract image frames from the video

Extracting image frames does not require ROS support, can be done locally as long as we have OpenCV support.

```bash
cd <sony_video_2_bagfile>/script/
python3 extract_frames_from_video.py \
    <output folder> \
    <input video filename> \
    --skip_frames 14
```

# Assemble image frames to a bagfile

Do something like

```bash
roslaunch sony_video_2_bagfile assmeble_frames.launch \
    image_folder:=<folder of the images> \
    out_bag_fn:=<full path of the output filename>
```

