
import rosbag
import math
import matplotlib.pyplot as plt

# --- Helper vector functions ---
def vec_add(a, b):
    return (a[0] + b[0], a[1] + b[1])

def vec_sub(a, b):
    return (a[0] - b[0], a[1] - b[1])

def vec_scale(a, s):
    return (a[0] * s, a[1] * s)

def vec_norm(a):
    return math.sqrt(a[0]**2 + a[1]**2)

def vec_unit(a):
    n = vec_norm(a)
    if n == 0:
        return (0, 0)
    return (a[0] / n, a[1] / n)

def main():
    bag_file = "/home/roboticslab229l/Downloads/Mobile-Robotics-3/moved.bag" 
    topic = "/csc22943//wheels_driver_node/wheels_cmd"  
    
    # Define the initial base line S (10 cm long horizontal line).
    # We'll set the left endpoint at (0, 0) and the right endpoint at (0.1, 0).
    S_left  = (0.0, 0.0)
    S_right = (0.1, 0.0)
    
    # Store the midpoints of S for plotting a trajectory.
    trajectory = []
    midpoint = ((S_left[0] + S_right[0]) / 2.0, (S_left[1] + S_right[1]) / 2.0)
    trajectory.append(midpoint)
    
    prev_time = None
    
    bag = rosbag.Bag(bag_file, 'r')
    try:
        for topic_name, msg, _ in bag.read_messages(topics=[topic]):
            # Compute current time in seconds.
            current_time = msg.header.stamp.secs + msg.header.stamp.nsecs * 1e-9
            if prev_time is None:
                prev_time = current_time
                continue
            dt = current_time - prev_time
            prev_time = current_time
            
            # Get wheel velocities.
            v_left  = msg.vel_left*0.4
            v_right = msg.vel_right*0.4
            
            # Compute displacements along the "vertical" (perpendicular to S).
            d_left  = v_left * dt
            d_right = v_right * dt
            
            # Compute S's direction vector.
            S_vec = vec_sub(S_right, S_left)
            # Compute a unit vector perpendicular to S.
            # We choose the perpendicular by rotating S_vec by +90°.
            u_perp = vec_unit((-S_vec[1], S_vec[0]))
            
            # Compute the new endpoints by "raising" the old endpoints.
            new_S_left  = vec_add(S_left,  vec_scale(u_perp, d_left))
            new_S_right = vec_add(S_right, vec_scale(u_perp, d_right))
        
            
            # Update S for the next iteration.
            S_left, S_right = new_S_left, new_S_right
            
            # Compute the midpoint of the new S and store it.
            mid = ((S_left[0] + S_right[0]) / 2.0, (S_left[1] + S_right[1]) / 2.0)
            trajectory.append(mid)
    finally:
        bag.close()
    
    # ----- Plot the Trajectory (midpoints of S) -----
    xs = [p[0] for p in trajectory]
    ys = [p[1] for p in trajectory]
    plt.figure()
    plt.plot(xs, ys, linestyle='-', label='Trajectory')
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.title("Trajectory")
    plt.legend()
    plt.grid(True)
    plt.axis("equal")
    plt.show()

if __name__ == '__main__':
    main()
