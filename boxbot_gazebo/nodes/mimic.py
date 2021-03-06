#!/usr/bin/env python

"""
  A script to support mimicking in Gazebo with the parallel grippers on the
  WidowX arms of Boxbot.

  Copyright 2018 University of Cincinnati
  All rights reserved. See LICENSE file at:
  https://github.com/MatthewVerbryke/inmoov-ros
  Additional copyright may be held by others, as reflected in the commit history.
  
"""


import sys
import thread

from std_msgs.msg import Float64
import rospy


class ParallelGripperMimic:
    """
    A ROS node that allows for mimicing joint commands on a parallel gripper
    (such as that on the WidowX) in Gazebo.
    
    TODO: TEST
    """
    
    def __init__(self):
        """
        
        """
        
        # Initialize node
        rospy.init_node("parallel_gripper_mimic")
        
        # Initialize cleanup
        rospy.on_shutdown(self.cleanup)
        
        # Get initial gripper states
        self.left_start = rospy.get_param("~left_gripper_start", 0.0)
        self.right_start = rospy.get_param("~right_gripper_start", 0.0)
        
        # Get a lock
        self.lock = thread.allocate_lock()
        
        # Define topics 
        init_string = '/boxbot/'
        final_string = '/command'
        leaders = ["left_gripper_joint_controller", "right_gripper_joint_controller"]
        mimics = ["left_gripper_mimic_controller", "right_gripper_mimic_controller"]
        callbacks = [self.get_left_command, self.get_right_command]
        
        self.pubs = []
        self.subs = []
        self.left_command = None
        self.right_command = None
        
        # Setup publishers and subscribers
        for i in range(0,len(leaders)):
            hold_sub = rospy.Subscriber(init_string + leaders[i] + final_string, Float64, callbacks[i])
            hold_pub = rospy.Publisher(init_string + mimics[i] + final_string, Float64, queue_size=1)
            self.subs.append(hold_sub)
            self.pubs.append(hold_pub)
        
        # Wait for topics to start publishing before continuing
        rospy.sleep(5)
        rospy.loginfo("Parallel gripper mimic node initialized")
        
        # Run main script
        self.main()
        
    def main(self):
        """
        Calculate and publish the nessecary commands for all mimiced joints.
        """
        
        while not rospy.is_shutdown():
            
            # Acquire a lock
            self.lock.acquire()
            
            try:
                # Update current commands
                current_goal = [self.left_command, self.right_command]
                
                # Go to the start state if we aren't getting anything yet
                if (self.left_command==None):
                    self.left_command = self.left_start
                if (self.right_command==None):
                    self.right_command = self.right_start
                
                # Publish the current commands to the parallel gripper
                for i in range(0,len(current_goal)):
                    self.pubs[i].publish(current_goal[i])
                    
            finally:
                
                # Release the lock
                self.lock.release()
                
    def get_left_command(self, msg):
        """
        Callback for the left gripper command.
        """
        self.left_command = msg.data
        
    def get_right_command(self, msg):
        """
        Callback for the right gripper command.
        """
        self.right_command = msg.data
        
    def cleanup(self):
        """
        Things to do on shutdown.
        """
        rospy.loginfo("Shutting down node 'parallel_gripper_mimic'")
        rospy.sleep(1)
        

if __name__ == "__main__":
    try:
        ParallelGripperMimic()
    except rospy.ROSInterruptException:
        pass

