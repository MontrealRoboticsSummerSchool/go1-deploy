# go1-deploy

Deployment kit for Unitree Go1 Edu. Modified for MRSS to support sending joint commands at lower frequencies and external policy mode.

This repository can be deployed in the following configurations:
1. External PC/NUC with LAN (Preferred) (Tested)
2. External PC/NUC with WiFi 
3. Internal Computer of the Go1 

> [!NOTE]
> **Documentation**
> - [Go1 Documentation - Unitree](https://unitree-docs.readthedocs.io/en/latest/get_started/Go1_Edu.html#)
> - [Go1 Documentation - Trossen Robotics](https://docs.trossenrobotics.com/unitree_go1_docs/index.html)
> - [Controlling Unitree Robots with Unitree\_legged\_sdk - YouTube](https://youtu.be/tTCbdul7xsc?si=oxI43LnGKkvNAQ99&t=495) 
> - [Docs Downloads](https://docs.trossenrobotics.com/unitree_go1_docs/downloads.html)
> - [Go1 Cameras](https://unitree-docs.readthedocs.io/en/latest/get_started/Go1_Edu.html#development-and-use-of-go1-binocular-fisheye-camera)
> - [Unitree Software Downloads](https://www.unitree.com/download)
> - - -

## Dependencies 
- Python 3.8
- PyTorch
- matplotlib
- numpy<1.24
- scipy
- Additional dependencies for unitree_legged_sdk

## Initial Setup

### 1. Network Configuration

The first step is to configure your network to connect to the Go1. Connect to the robot with an Ethernet cable and follow the wired instructions on [this page](https://docs.trossenrobotics.com/unitree_go1_docs/getting_started/network.html#remote-pc-network-setup).

To verify the connection works, ping one of the onboard computers:
```bash
ping 192.168.123.10
```

After this setup, your network configuration should be:
- IP Address: 192.168.123.162
- Subnet Mask: 255.255.255.0
- Default Gateway: 192.168.123.1

The internal network architecture of the Go1 is shown below:

![Go1 Network Architecture](https://docs.trossenrobotics.com/unitree_go1_docs/_images/go1_edu_architecture.png)

**Important IP Addresses:**
- Raspberry Pi: 192.168.123.161
- Motors: 192.168.123.10
- Jetson 1: 192.168.123.13
- Jetson 2: 192.168.123.14
- Main Nano: 192.168.123.15

You should now be able to SSH to any of the computers:
```bash
ssh unitree@192.168.123.15
# password: 123
```

For more information about SSH, see the [network documentation](https://docs.trossenrobotics.com/unitree_go1_docs/getting_started/network.html#ssh).

#### Connecting the robot to the internet

An internet connection can be shared with the robot over ethernet.

<details>
  <summary>If the robot has not previously been configured</summary>

   Edit /etc/rc.local and add the following:
   ```
   ip addr add 10.42.0.50/24 dev eth0 label eth0:1
   ```

Edit /etc/dhcpcd.conf and add nogateway in the section for eth0:
   ```
   interface eth0
   static ip_address=192.168.123.161/24
   nogateway
   ```

Add this to /lib/dhcpcd/dhcpcd-hooks/99-remote-gateway (create this file):

```
if [ "$reason" = "BOUND" ] || [ "$reason" = "STATIC" ] || [ "$reason" = "ROUTERADVERT" ]; then
    
    ip route replace default via 10.42.0.1 dev eth0 metric 100
    
    echo "nameserver 8.8.8.8" > /etc/resolv.conf
    echo "nameserver 8.8.4.4" >> /etc/resolv.conf
fi
```
</details>

**On the machine connected to the go1 by ethernet**

Edit the wired connection that you previously configured:

In ipv4 settings, tab IPv4, switch IPv4 method from manual to 'Shared to other computers', Apply and then toggle the connection off then on.

This should give your machine's ethernet interface the ip 10.42.0.1, the IP on the robot that you should connect to is 10.42.0.50:

```
ssh pi@10.42.0.50 # passwd 123
```

### 2. Installation 

On one of the robot's Jetsons, we have been using 192.168.123.14, run the following commands:


1. **Clone the repository:**
   ```bash
   mkdir /home/unitree/MRSS
   cd /home/unitree/MRSS
   git clone https://github.com/MontrealRoboticsSummerSchool/go1-deploy
   cd go1-deploy
   ```

2. **Build the unitree_legged_sdk:**
   ```bash
   cd unitree_legged_sdk
   mkdir build
   cd build
   cmake ../
   make
   ```
3. **Set the python path for the SDK**
   ```bash
   echo "export PYTHONPATH="/home/unitree/MRSS/go1-deploy/unitree_legged_sdk/lib/python/arm64/:${PYTHONPATH}"" >> ~/.bashrc
   ```

4. **Test the installation:**
   1. **Kill sport mode** (required to prevent command conflicts):
      - Lay down the robot: L2 + B
      - Run: `./unitree_legged_sdk/kill-sport-mode.sh`
   
   2. **Run a test example:**
      ```bash
      cd unitree_legged_sdk/example_py/
      python example_position.py
      ```

### 3. Conda Environment
Conda is installed on the robots and there should be an existing environment called depl.
If you need to reinstall:

1. **Install conda**
   ```bash
   curl -L -o miniforge.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh \
    && bash miniforge.sh -b -p /root/miniforge3 && rm miniforge.sh
    ```

2. **Create the environment:**
   ```bash
   cd /home/unitree/MRSS/go1-deploy
   conda env create -f environment.yml
   ```

3. **Activate environment:**
   ```bash
   conda activate depl
   ```
## Docker
The go1-deploy code can be run in a docker container.

Clone this repository:
```bash
mkdir /home/unitree/MRSS
cd /home/unitree/MRSS
git clone https://github.com/MontrealRoboticsSummerSchool/go1-deploy
cd go1-deploy
```
There are two versions of the docker image, one for Jetpack 4.4 and one for jetpack 4.5.

To build for jetpack 4.4:
```
docker compose build go1-deploy_jp44
```

And for jetpack 4.5:
```
docker compose build go1-deploy_jp45
```

Then bring up the container:
```
docker compose up go1-deploy_jp44 -d
```
OR
```
docker compose up go1-deploy_jp45 -d
```

Enter the container:
```
docker exec -it go1_deploy_container44 bash
```

OR
```
docker exec -it go1_deploy_container45 bash
```
activate the conda environment:
```
conda activate depl
```

and launch the deploy script with high priority:
```
chrt -f 99 $(which python) deploy.py --model weights/policy.pt
```

## Deployment

### 1. Boot the Robot and Prepare for Control

1. **Connect the LAN cable** to the robot before booting
2. **Turn on the robot** and the Unitree joystick, then wait for it to automatically stand up (this can take a few minutes)
3. **Lay down the robot:** L2 + B
4. **Enter low-level mode** using one of the following methods:
   
   **Option 1:** Use the script
   ```bash
   ./unitree_legged_sdk/kill-sport-mode.sh
   # password: 123
   ```
   
   **Option 2:** Use the controller
   - L2 + A
   - L2 + A
   - L2 + B
   - L1 + L2 + Start

5. **Validate connectivity** to the motor controller:
   ```bash
   ping 192.168.123.10
   ```

### 2. Running Policies

The `deploy.py` script initializes the [`PolicyRunner`](policy_runner.py), which handles the interface between policy actions and the `unitree_legged_sdk`. It can operate in several modes:

#### Local Policy Mode

Run policy inference onboard the robot at 50 Hz. Specify the model file when calling the deploy script:

```bash
# 1. Copy your policy to the robot
scp ~/path/to/your/policy/_exported.pt unitree@192.168.123.14:~/MRSS/go1-deploy/weights/policy.pt

# 2. SSH to the robot and run
ssh 192.168.123.14
# password: 123
conda activate depl
cd ~/MRSS/go1-deploy
bash unitree_legged_sdk/kill-sport-mode.sh # password: 123
sudo chrt -f 99 $(which python) deploy.py --model weights/policy.pt # runs deploy.py with high priority
```

**Safety procedure:**
1. **Suspend the robot in the air** before starting
2. Run the deploy script while suspended
3. **Wait 2-3 seconds** for the robot to reach standing pose
4. **Slowly lower the robot** to the ground
5. **Do not use the joystick** until the counter reaches 2300
6. After 2300, you can control the robot:
   - Left joystick: Linear velocity commands
   - Right joystick: Yaw commands

#### External Policy Mode

In this mode, actions are computed externally and sent to the robot via TCP commands:

```bash
ssh 192.168.123.14 # password: 123
conda activate depl
cd ~/MRSS/go1-deploy
bash unitree_legged_sdk/kill-sport-mode.sh # password: 123
python deploy.py --server --external-policy
sudo chrt -f 99 $(which python) deploy.py --server --external-policy # runs deploy.py with high priority
```

The robot will wait to receive actions over the TCP connection.

#### Server Mode (Velocity Commands)

Enable server mode to receive velocity commands via TCP instead of the joystick:

```bash
sudo chrt -f 99 $(which python) deploy.py --model weights/policy.pt --server # runs deploy.py with high priority
```

> [!NOTE]
> In **external policy** mode, velocity commands are ignored since the remote machine sends joint positions directly.

### 3. Message Format

The system supports two types of TCP messages:

**Action Commands** (50 bytes):
- Code: 2 (short, 2 bytes) 
- Actions: 12 floats (48 bytes) - joint angles for each motor

**Velocity Commands** (14 bytes):
- Code: 1 (short, 2 bytes)
- x, y, r: 3 floats (12 bytes) - linear and angular velocities

### 4. Running the Navigation Controller

> [!CAUTION]
> This section is not yet complete. See the TODOs in [`run_nav_controller`](scripts/run_nav_controller.py).

When a team wants to test their Navigation Controller on the real robot:

1. Copy the team's `nav_controller.py` file to `go1_navigation/`
2. Copy their policy to the robot
3. Run the robot in local policy with `--server` mode
4. On your laptop connected to the robot via Ethernet, launch `scripts/run_nav_controller.py`

> [!TIP]
> **Recommended conda environments:**
> 1. `depl`: Deployment environment (Go1 computers, Python 3.8)
> 2. `isaaclab`: Simulation environment (student laptops, Python 3.10)
> 3. `controller`: Environment for the MILA laptop connected to the robot (should have NavController dependencies and eventually crossformer) (Python 3.10)

> [!WARNING]
> OpenCV cannot be installed in the same environment as Isaac Sim conda environment due to version conflicts.

## Testing

We provide scripts to test that server mode (bidirectional communication) works properly.

### 1. Test Server Mode

1. **Start robot in server mode with local policy:**
   ```bash
   ssh 192.168.123.14
   # password: 123
   conda activate depl
   cd ~/MRSS/go1-deploy
   bash unitree_legged_sdk/kill-sport-mode.sh # password: 123
   python deploy.py --model weights/<policy>.pt --server
   ```

2. **Test observations and send velocity commands from remote machine:**
   ```bash
   python scripts/test_bidirectional_comm.py
   ```
   > [!TIP]
   > Uncomment line 103 of `test_bidirectional_comm.py` to send velocity commands.

### 2. Test External Policy Mode

1. **Start robot in external policy mode:**
   ```bash
   # On the robot
   python deploy.py --server --external-policy
   ```

2. **Send actions from external controller:**
   ```bash
   # On your machine
   python scripts/test_external_policy.py
   ```

The robot will receive observations and send them to connected clients. Clients must send action commands (12 joint angles) via TCP. Use `test_external_policy.py` as a reference implementation.


## Cameras

> [!NOTE]
> **Resources**
> - [Transfer Image using Camera SDK - YouTube](https://www.youtube.com/watch?v=nafv21HeeEM)
> - [Go1 Fisheye Camera Documentation](https://unitree-docs.readthedocs.io/en/latest/get_started/Go1_Edu.html#development-and-use-of-go1-binocular-fisheye-camera)

I didn't have time to integrate camera data with the NavController. There are two options: 
1. Use an Intel camera
2. Use the Go1's built-in camera

Florian mentioned that after correcting for the fisheye distortion, the image resolution is quite low.

### Go1 Built-in Camera

I was able to view camera images on my laptop following the [Go1 fisheye camera guide](https://unitree-docs.readthedocs.io/en/latest/get_started/Go1_Edu.html#development-and-use-of-go1-binocular-fisheye-camera) and the [Camera SDK YouTube tutorial](https://www.youtube.com/watch?v=nafv21HeeEM).

#### Setup Process:

**1. View Camera on Local Board (.13)**

SSH with X11 forwarding:
```bash
ssh -X unitree@192.168.123.13
```

Navigate to camera SDK and run example:
```bash
cd UnitreecameraSDK/
./bins/example_getRectFrame 
```

**2. Stream to Your Laptop**

**On Jetson .13:**
1. **Configure the YAML file:**
   - Set `IpLastSegment` to your laptop's IP
   - Set `DeviceNode` to 1 (for front camera)
   - Set `TransMode` to 2 or 3 (rectified image - right, or rectified stereo)

2. **Start transmission:**
   ```bash
   cd UnitreecameraSDK/
   ./bins/example_putImagetrans 
   ```

**On Your Laptop:**
Test if the stream appears:
```bash
gst-launch-1.0 udpsrc port=9201 ! application/x-rtp, media=video, encoding-name=H264 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink
```

> [!TIP]
> There are several test scripts available (created with help from Claude) to test camera functionality. You probably don't need to install UnitreecameraSDK on your laptop - you can likely read the images directly with Python.

