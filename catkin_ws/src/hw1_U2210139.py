#!/usr/bin/env python3
"""
Homework #1 – TurtleSim Digit Drawing
Course  : Capstone Design [202601-ICE/CSE4020]
Student : U2210139
Digits  : 0  1  3  9   (last four digits of student ID)
GitHub link: https://github.com/abduxakim/Capstone_HW1git
"""

import rospy
import threading
import math
from geometry_msgs.msg import Twist
from turtlesim.srv import Spawn, TeleportAbsolute, SetPen
from turtlesim.srv import Kill


# ===========================================================================

def pen_up(name):
    svc = f"/{name}/set_pen"
    rospy.wait_for_service(svc)
    rospy.ServiceProxy(svc, SetPen)(0, 0, 0, 3, 1)

def pen_down(name, r=255, g=255, b=255, w=4):
    svc = f"/{name}/set_pen"
    rospy.wait_for_service(svc)
    rospy.ServiceProxy(svc, SetPen)(r, g, b, w, 0)

def tp(name, x, y, angle_deg=0.0):
    svc = f"/{name}/teleport_absolute"
    rospy.wait_for_service(svc)
    rospy.ServiceProxy(svc, TeleportAbsolute)(x, y, math.radians(angle_deg))

def move(pub, rate, lx, az, duration):
    msg = Twist()
    msg.linear.x = lx
    msg.angular.z = az
    t_end = rospy.Time.now() + rospy.Duration(duration)
    while rospy.Time.now() < t_end and not rospy.is_shutdown():
        pub.publish(msg)
        rate.sleep()
    pub.publish(Twist())   # стоп
    rospy.sleep(0.05)

def forward(pub, rate, dist, speed=1.8):
    move(pub, rate, speed, 0.0, dist / speed)

def turn_deg(pub, rate, deg, speed=2.5):
    rad = math.radians(abs(deg))
    sign = 1.0 if deg > 0 else -1.0
    move(pub, rate, 0.0, sign * speed, rad / speed)

def arc(pub, rate, radius, deg, speed=1.6):
    rad = math.radians(abs(deg))
    length = radius * rad
    sign = 1.0 if deg > 0 else -1.0
    az = sign * speed / radius
    move(pub, rate, speed, az, length / speed)

def remove_turtle(name):
    try:
        rospy.wait_for_service('/kill')
        kill = rospy.ServiceProxy('/kill', Kill)
        kill(name)
        rospy.loginfo(f"Turtle {name} removed")
    except rospy.ServiceException as e:
        rospy.logerr(f"Failed to remove {name}: {e}")


# ===========================================================================

def draw_0(name, pub, rate, cx, cy):

    a = 0.75
    b = 1.40

    steps = 200
    dt = 2 * math.pi / steps

    pen_up(name)

    start_x = cx + a * math.cos(-math.pi/2)
    start_y = cy + b * math.sin(-math.pi/2)

    tp(name, start_x, start_y, 0.0)

    pen_down(name, 255, 0, 0, 4)

    for i in range(steps + 1):

        t = -math.pi/2 + i * dt

        x = cx + a * math.cos(t)
        y = cy + b * math.sin(t)

        dx = -a * math.sin(t)
        dy =  b * math.cos(t)

        theta = math.atan2(dy, dx)

        tp(name, x, y, theta)

        if rospy.is_shutdown():
            return

        rospy.sleep(0.01)

    rospy.sleep(0.05)


def draw_1(name, pub, rate, cx, cy):

   
    pen_up(name)
    tp(name, cx - 0.4, cy + 1.2, 45)
    pen_down(name, 255, 0, 0, 4)   
    forward(pub, rate, 0.5)

    
    pen_up(name)
    tp(name, cx, cy + 1.6, -90)
    pen_down(name, 255, 0, 0, 4)
    forward(pub, rate, 3.0)

  
    pen_up(name)
    tp(name, cx - 0.8, cy - 1.5, 0)
    pen_down(name, 255, 0, 0, 4)
    forward(pub, rate, 1.6)

def draw_3(name, pub, rate, cx, cy):

    R = 0.85


    x_offset = -1.2
    y_offset = -0.75

    cx += x_offset
    cy += y_offset

 
    pen_up(name)
    tp(name, cx - R, cy + R, 0)      
    pen_down(name, 255, 0, 0, 4)     
    arc(pub, rate, R, 180)

   
    pen_up(name)
    lower_offset = 0.85             
    tp(name, cx - R, cy - lower_offset, 0)
    pen_down(name, 255, 0, 0, 4)
    arc(pub, rate, R, 180)

def draw_9(name, pub, rate, cx, cy):

    R = 0.7
    y_offset = 0.3  

    top = cy + 1.4 + y_offset
    bottom = cy - 1.4 + y_offset

    head_cy = top - R

    tail_start_x = cx + R*0.7
    tail_start_y = head_cy - R*0.8

    tail_length = (tail_start_y - bottom) - 0.2

    tail_radius = 0.7
    tail_angle = -135

    pen_up(name)
    tp(name, cx, head_cy - R, 0)

    pen_down(name, 255, 0, 0, 4)   

    for _ in range(4):
        arc(pub, rate, R, 90)


    pen_up(name)
    tp(name, tail_start_x, tail_start_y, -90)

    pen_down(name, 255, 0, 0, 4)   

    forward(pub, rate, tail_length)

    arc(pub, rate, tail_radius, tail_angle)


# ===========================================================================

DIGIT_FUNCS = {
    0: draw_0,
    1: draw_1,
    3: draw_3,
    9: draw_9,
}

def worker(name, digit, cx, cy):
    topic = f"/{name}/cmd_vel"
    pub = rospy.Publisher(topic, Twist, queue_size=10)
    rate = rospy.Rate(20)

    rospy.sleep(0.4) 

    rospy.loginfo(f"[{name}] Starting to draw digit {digit}")
    DIGIT_FUNCS[digit](name, pub, rate, cx, cy)
    rospy.loginfo(f"[{name}] Finished drawing digit {digit}")

# ===========================================================================

def main():
    rospy.init_node('digit_drawer_U2210139')
    rospy.loginfo("Start! ID: U2210139 → digits 0, 1, 3, 9")

 
    zones = [
        ('turtle1', 0, 1.5, 5.5),
        ('turtle2', 1, 4.0, 5.5),
        ('turtle3', 3, 8.2, 5.5),
        ('turtle4', 9, 9.5, 5.5),
    ]

    rospy.wait_for_service('/spawn')
    spawn = rospy.ServiceProxy('/spawn', Spawn)

  
    pen_up('turtle1')
    tp('turtle1', zones[0][2], zones[0][3])

    # Spawn other turtles
    for name, digit, cx, cy in zones[1:]:
        try:
            resp = spawn(cx, cy, 0.0, name)
            rospy.loginfo(f"Spawned {resp.name} at ({cx}, {cy})")
        except rospy.ServiceException as e:
            rospy.logerr(f"Spawn error: {e}")
        pen_up(name)

    rospy.sleep(0.6)

    rospy.loginfo("Starting all drawing threads...")

  
    threads = [
        threading.Thread(target=worker, args=(name, digit, cx, cy), daemon=True)
        for name, digit, cx, cy in zones
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    rospy.loginfo("All digits drawn successfully! 0 1 3 9")


    for name, _, _, _ in zones:
        remove_turtle(name)

    rospy.spin()


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass

