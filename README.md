## How to use it

### 1. About this repository

Use the fork button in the top-right corner of the github page to fork this template repository. 

/Mobile-Robotics/packages/my_package/src/wheel_control_encoders.py has all the code for drive forwards, backwards, rotate, D shape. We control the power percentage and distance of both wheels to make robots drive in different modes.


### 2. Change important variables

Before running the code, please navigate to /Mobile-Robotics/packages/my_package/src/wheel_control_encoders.py and make changes to the radius of the wheels and the length between the wheels and centre of rotation if necessary.


### 3. Build the program

After that open this folder in the terminal. Once you are in the folder, type in the terminal: dts devel build -f to build the program in the duckiebot.


### 4. Run the program

Driving part: To run the program, type in the terminal: dts devel run -R [Vehicle_name] -L wheel-control. Replace [Vehicle_name] with your robot's name.

Camera part: To run the program, type in the terminal: dts devel run -R [Vehicle_name] -L camera-reader -X. Replace [Vehicle_name] with your robot's name.


### 5. Plotting trajectory

Once you have recorded the rosbag, put it in /Mobile-Robotics and run plot.py in /Mobile-Robotics/packages/my_package/src.
