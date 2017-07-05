
[//]: # (Image References)

[image1]: ./misc/rover_image.jpg
[image2]: ./calibration_images/example_rock1.jpg
[image3]: ./misc/warped.jpg 
[image4]: ./misc/threshed.jpg
[image5]: ./misc/obstacle_threshed.jpg
[image6]: ./misc/rock_threshed.jpg
[image7]: ./misc/best_run.jpg


Simulator Settings: 
* Resolution: 1280 x 800
* Graphics Quality: Good
* FPS: ~30

### Notebook Analysis

I used three separate functions to detect the navigable terrain `color_thresh()`), 
the obstacles (`obst_thresh()`) and the golden rocks (`rock_thresh()`).

In `rock_thresh()` I found that converting the image to the HSV color space and 
then dilating the binary image made it easier to locate the rocks. 

The color space and thresholds for each function are as follow:

`color_thresh()`: BGR - `[160, 160, 160]` to `[255, 255, 255]`

`obst_thresh()`: BGR - `[0, 0, 0]` to `[90, 90, 90]`

`rock_thresh()`: HSV - `[93, 173, 131]` to `[98, 255, 182]`

The rock calibration image

![alt text][image2]

The warped image

![alt text][image3]

Segmenting the navigable terrain using `color_thresh()`

![alt text][image4]

Segmenting the obstacles using `obst_thresh()`

![alt text][image5]

Segmenting the golden rocks using `rock_thresh()`

![alt text][image6]

#### 1. Mapping pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 

* First I transformed the image to using `perspect_transform()`
 
* Using the transformed the image I segmented it three times using `color_thresh()`, `obst_thresh()` and `rock_thresh()`

* With the segmented images I was able to convert the thresholded image pixel values to rover-centric coordinates using `rover_coords()`

* From the rover-centric coordinates I calculated the angle and distance of each pixel from the rover with the function `to_polar_coords()`

* Then I converted the rover-centric coordinates to world coordinates using `pix_to_world()`

* Using the world coordinates I was able to update the world map based on the rover's surroundings by setting the appropriate channel in `data.worldmap[]` equal to the corresponding world pixel values of either the detected navigable terrain,  obstacles or golden rocks


### Autonomous Navigation and Mapping
* `perception_step()` - My logic is as follows: Every time there is a new image, the image is transformed 
and three different thresholds are applied to it creating three separate channels. The three channels are 
used to determine where the obstacles, navigable terrain and the golden rocks are. Then the three channels 
are combined to be shown in the simulator. From the three individual channels the image pixel values are 
converted to rover-centric coordinates. The rover-centric pixel values are then converted to world 
coordinates. The world coordinates are then used to update the world map only if the pitch and roll of the 
rover are within 0.0 +/- 0.5 degrees. This is because when the rover isn't sitting flat the transformed 
image provides inaccurate data. Since the values returned to update the world map are used to determine 
percentage mapped and the fidelity of the mapping it is important to only update the map when the data is 
accurate. 

* `decision_step()` - In this function I have 5 modes. They are forward, stop, pickup, turn and home. 
  * **Forward**: Checks navigable angles to make sure they are over the minimum threshold, if they are then it
     checks the rover's speed. If the speed is less than the max velocity it accelerates otherwise it just 
     coasts. If the rover is in forward mode and its speed is stuck below 0.05 for more than a second then
      the rover changes its mode to turn. If the navigable angles is below the minimum threshold then the 
      enters stop mode.  
  * **Stop**: In this mode if the rover's speed isn't 0 then it brakes. If it is 0 then it sets its steering
  angle to -15 degrees and turns. I tried checking which way the average navigable angles were pointing but
  this caused it to get stuck in a corner turning back and forth.  
  * **Turn**: This mode is very similar to stop except it is called after the rover's speed is stuck at 0 when
  the rover is supposed to be moving.  
  * **Pickup**: This is a non-explicit mode that checks if there are any angles to the rocks. If there are the
  robot either stops or slows down as it navigates to the rock. In order to prevent over shooting the rock if 
  the robot is traveling fast it slams on the brakes and slowly moves to the rock.
  * **Home**: This mode is untested but is meant to navigate the rover back to its starting place while avoiding
  obstacles.

##### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

#####Accomplishments:
 1) Rover was able to successfully navigate around the world and pick up the rocks  
    1) Converting the image to HSV let me isolate the rock easier without false positives like I was getting using 
  the default BGR color-space.  
    1) By eroding the detected rock I was able to make it stand out more. This allowed me to wander in the middle
  of the path more and still make it to the rocks.  
 2) Added turn mode to get the rover unstuck when it drove into a rock. Detects when it is trying to go forward 
 but it not making any progress (velocity = 0). This mode makes the rover turn and try and go forward until it is
 successful.
 3) When my rover is going fast (velocity > 0.8) It slams on the brakes and then turns to the rock in order to
 prevent over shooting the rock
 
 My best run:
 
 ![alt text][image7]

#####Improvements: 
1) Making the rover hug the walls and follow a set distance off the walls would help increase net mapping as
well as fidelity. I also think it would help prevent rock overshooting. 
2) I think a better approach to getting unstuck should be taken but the simple system I implemented was good
enough for most cases.
3) To avoid going in circles I think the farthest X number of pixels should be ignored because in open areas 
it is easy to get stuck doing circles.
4) Sometimes the rover will approach a rock and it will be colliding with the wall trying to get close enough
to pick it up. A better approach could be to align the rover so the rock is within +/- 5 degrees from it so it
approaches the rock head on and never has this not close enough problem.

#####Comments:
* When trying to produce a run worthy of submitting I started noticing significant lag in the simulator to the
extent that the reported FPS went from ~40 down to ~20 but in reality the simulator was updating under 1 FPS. 



