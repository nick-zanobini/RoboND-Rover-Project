import numpy as np
import cv2


def color_thresh(img, lower_path=np.array([159, 159, 159]), upper_path=np.array([255, 255, 255])):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:, :, 0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = ((img[:, :, 0] > lower_path[0]) & (img[:, :, 0] <= upper_path[0])) \
        & ((img[:, :, 1] > lower_path[1]) & (img[:, :, 1] <= upper_path[1])) \
        & ((img[:, :, 2] > lower_path[2]) & (img[:, :, 2] <= upper_path[2]))
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select


def rock_thresh(img, lower_rock=np.array([93, 173, 131]), upper_rock=np.array([98, 255, 182])):
    # Create an array of zeros same xy size as img, but single channel
    rock_select = np.zeros_like(img[:, :, 0])
    # Convert BGR to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Threshold the HSV image to get only yellow colors
    between_thresh = (((hsv[:, :, 0] > lower_rock[0]) & (hsv[:, :, 0] <= upper_rock[0])) &
                      ((hsv[:, :, 1] > lower_rock[1]) & (hsv[:, :, 1] <= upper_rock[1])) &
                      ((hsv[:, :, 2] > lower_rock[2]) & (hsv[:, :, 2] <= upper_rock[2])))
    # Index the array of zeros with the boolean array and set to 1
    rock_select[between_thresh] = 1
    # kernel of 5x5 size
    kernel = np.ones((5, 5), np.uint8)
    # Dilate the image to get a bigger and easier to locate target
    rock_select = cv2.dilate(rock_select, kernel, iterations=3)
    # Return the binary image
    return rock_select


def obst_thresh(img, lower_obst=np.array([0, 0, 0]), upper_obst=np.array([140, 140, 140])):
    # Create an array of zeros same xy size as img, but single channel
    obst_select = np.zeros_like(img[:, :, 0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    below_thresh = ((img[:, :, 0] > lower_obst[0]) & (img[:, :, 0] <= upper_obst[0])) \
        & ((img[:, :, 1] > lower_obst[1]) & (img[:, :, 1] <= upper_obst[1])) \
        & ((img[:, :, 2] > lower_obst[2]) & (img[:, :, 2] <= upper_obst[2]))
    # Index the array of zeros with the boolean array and set to 1
    obst_select[below_thresh] = 1
    # Return the binary image
    return obst_select


def rover_coords(binary_img):
    # Define a function to convert to rover-centric coordinates
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the
    # center bottom of the image.
    x_pixel = np.absolute(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[0]).astype(np.float)
    return x_pixel, y_pixel


def to_polar_coords(x_pixel, y_pixel):
    # Define a function to convert to radial coords in rover space
    # Convert (x_pixel, y_pixel) to (distance, angle)
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel ** 2 + y_pixel ** 2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles


def rotate_pix(xpix, ypix, yaw):
    # Define a function to apply a rotation to pixel positions\
    # Convert yaw to radians
    # Apply a rotation
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = xpix * np.cos(yaw_rad) - ypix * np.sin(yaw_rad)
    ypix_rotated = xpix * np.sin(yaw_rad) + ypix * np.cos(yaw_rad)
    # Return the result
    return xpix_rotated, ypix_rotated


def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale):
    # Define a function to perform a translation
    # Apply a scaling and a translation
    # Assume a scale factor of 10 between world space pixels and rover space pixels
    # Perform translation and convert to integer since pixel values can't be float
    xpix_translated = np.int_(xpos + (xpix_rot / scale))
    ypix_translated = np.int_(ypos + (ypix_rot / scale))
    # Return the result
    return xpix_translated, ypix_translated


def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Define a function to apply rotation and translation (and clipping)
    # Once you define the two functions above this function should work
    # Apply rotation

    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)

    # Return the result
    return x_pix_world, y_pix_world


def perspect_transform(img, src, dst):
    # Define a function to perform a perspective transform
    m = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, m, (img.shape[1], img.shape[0]))  # keep same size as input image

    return warped


def perception_step(Rover):
    # Apply the above functions in succession and update the Rover state accordingly
    # Perform perception steps to update Rover()
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    dst_size = 10
    bottom_offset = 6
    source = np.float32([[14, 140], [301, 140], [200, 96], [118, 96]])
    destination = np.float32([[Rover.img.shape[1] / 2 - dst_size, Rover.img.shape[0] - bottom_offset],
                              [Rover.img.shape[1] / 2 + dst_size, Rover.img.shape[0] - bottom_offset],
                              [Rover.img.shape[1] / 2 + dst_size, Rover.img.shape[0] - 2 * dst_size - bottom_offset],
                              [Rover.img.shape[1] / 2 - dst_size, Rover.img.shape[0] - 2 * dst_size - bottom_offset],
                              ])

    # 2) Apply perspective transform
    warped = perspect_transform(Rover.img, source, destination)

    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    threshed = color_thresh(warped)
    rock_threshed = rock_thresh(warped)
    obstacle_threshed = obst_thresh(warped)

    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
    Rover.vision_image[:, :, 0] = obstacle_threshed * 255
    Rover.vision_image[:, :, 1] = rock_threshed * 255
    Rover.vision_image[:, :, 2] = threshed * 255

    # 5) Convert map image pixel values to rover-centric coords
    xpix_navi, ypix_navi = rover_coords(threshed)
    xpix_rock, ypix_rock = rover_coords(rock_threshed)
    xpix_obst, ypix_obst = rover_coords(obstacle_threshed)

    # 6) Convert rover-centric pixel values to world coordinates
    x_world_navi, y_world_navi = pix_to_world(xpix_navi, ypix_navi, Rover.pos[0], Rover.pos[1], Rover.yaw,
                                              Rover.worldmap.shape[0], Rover.scale)
    x_world_rock, y_world_rock = pix_to_world(xpix_rock, ypix_rock, Rover.pos[0], Rover.pos[1], Rover.yaw,
                                              Rover.worldmap.shape[0], Rover.scale)
    x_world_obst, y_world_obst = pix_to_world(xpix_obst, ypix_obst, Rover.pos[0], Rover.pos[1], Rover.yaw,
                                              Rover.worldmap.shape[0], Rover.scale)

    # 7) Update Rover worldmap (to be displayed on right side of screen)
    if (Rover.roll < 1.0 or Rover.roll < 359.0) and (Rover.pitch < 1.0 or Rover.pitch < 359.0):
        Rover.worldmap[y_world_obst, x_world_obst, 0] = 255
        Rover.worldmap[y_world_rock, x_world_rock, 1] = 255
        Rover.worldmap[y_world_navi, x_world_navi, 2] = 255

    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
    Rover.nav_dists, Rover.nav_angles = to_polar_coords(xpix_navi, ypix_navi)
    Rover.obst_dists, Rover.obst_angles = to_polar_coords(xpix_obst, ypix_obst)
    Rover.rock_dists, Rover.rock_angles = to_polar_coords(xpix_rock, ypix_rock)

    if Rover.mode == 'home':
        Rover.home_dists, Rover.home_angles = to_polar_coords(Rover.start_pos)

    return Rover


if __name__ == '__main__':
    pass
