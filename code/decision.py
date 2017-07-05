from random import uniform
import numpy as np


def decision_step(Rover):
    # Check if a rock is in sight
    if Rover.picking_up:
        return Rover
    if len(Rover.rock_angles) > 1:
        # Checks if the Rover is already in picking up range
        if Rover.near_sample:
            Rover.brake = Rover.brake_set * 5
            Rover.send_pickup = True
        # If not then reduce speed so it can steadily approach
        elif Rover.vel >= 0.8:
            Rover.brake = Rover.brake_set * 5
        elif Rover.vel < 0.8 and Rover.vel >= 0.5:
            Rover.brake = 0
            Rover.throttle = 0
        elif Rover.vel < 0.5:
            Rover.brake = 0
            Rover.throttle = Rover.throttle_set
        # Keep steering towards the rock
        Rover.steer = np.clip(np.mean(Rover.rock_angles * 180 / np.pi), -15, 15)
    # Otherwise check for navigable terrain
    elif Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.mode == 'forward':
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:
                # If mode is forward, navigable terrain looks good
                # and velocity is below max, then throttle
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else:
                    # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                tmp = np.clip(np.mean(Rover.nav_angles * 180 / np.pi), -15, 15)
                Rover.steer = np.clip(tmp - 3 if tmp <= 0 else tmp + 3, -8, 8)

                if(Rover.vel > 0.05 and Rover.mode == 'forward'):
                    Rover.stuck_time = 0
                elif (Rover.total_time > 1 and Rover.vel == 0.0):
                    if Rover.stuck_time == 0:
                        Rover.stuck_time = Rover.total_time
                    elif (Rover.total_time - Rover.stuck_time) > 1:
                        Rover.mode = 'turn'

            if Rover.samples_to_find == 0:
                Rover.mode = 'home'

            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                # Set mode to "stop" and hit the brakes!
                Rover.throttle = 0
                # Set brake to stored brake value
                Rover.brake = Rover.brake_set
                Rover.steer = 0
                Rover.mode = 'stop'
        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.5:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.5:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    # tmp = np.clip(np.mean(Rover.nav_angles * 180 / np.pi), -15, 15)
                    Rover.steer = -15
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180 / np.pi), -10, 10)
                    if Rover.samples_to_find == 0:
                        Rover.mode = 'home'
                    else:
                        Rover.mode = 'forward'
        # Check for Rover.mode status
        elif Rover.mode == 'turn':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.5:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.5:
                Rover.throttle = 0
                # Release the brake to allow turning
                Rover.brake = 0
                # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                tmp = np.clip(np.mean(Rover.nav_angles * 180 / np.pi), -15, 15)
                Rover.steer = -15 if tmp <= 5 else 15
                if len(Rover.nav_angles) >= Rover.stop_forward:
                    Rover.mode = 'forward'

        # If we have collected all the samples, return home
        elif Rover.mode =='home':
            # Check the extent of navigable terrain
            # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
            Rover.steer = np.clip(np.mean(Rover.home_angles * 180 / np.pi), -15, 15)
            if len(Rover.nav_angles) >= Rover.stop_forward:
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else:
                    # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                # Set mode to "stop" and hit the brakes!
                Rover.throttle = 0
                # Set brake to stored brake value
                Rover.brake = Rover.brake_set
                Rover.steer = 0
                Rover.mode = 'stop'

    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0

    return Rover
