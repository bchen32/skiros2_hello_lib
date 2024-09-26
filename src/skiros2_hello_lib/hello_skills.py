from skiros2_skill.core.skill import SkillDescription, SkillBase
from skiros2_common.core.params import ParamTypes
from skiros2_common.core.world_element import Element
from skiros2_common.core.primitive import PrimitiveBase
import rospy

#################################################################################
# Descriptions
#################################################################################

class ScanPrimitive(SkillDescription):
    def createDescription(self):
        self.addParam("Target", Element("skiros:TransformationPose"), ParamTypes.Optional)
        self.addPostCondition(self.getHasPropCond("HasPositionX", "skiros:PositionX", "Target", True))

class MovePrimitive(SkillDescription):
    def createDescription(self):
        self.addParam("Robot", Element("cora:Robot"), ParamTypes.Required)
        self.addParam("Target1", Element("skiros:TransformationPose"), ParamTypes.Required)
        self.addPreCondition(self.getPropCond("TargetExists", "skiros:PositionX", "Target1", "=", 5.0, True))
        self.addPostCondition(self.getPropCond("RobotAtTarget", "skiros:PositionX", "Robot", "=", 5.0, True))

#################################################################################
# Implementations
#################################################################################

class scan_primitive(PrimitiveBase):
    """
    This primitive has 3 states
    """
    def createDescription(self):
        """Set the primitive type"""
        self.setDescription(ScanPrimitive(), self.__class__.__name__)

    def onInit(self):
        """Called once when loading the primitive. If return False, the primitive is not loaded"""
        return True

    def onPreempt(self):
        """ Called when skill is requested to stop. """
        return self.fail("Stopped", -1)

    def onStart(self):
        """Called just before 1st execute"""
        return True

    def execute(self):
        """ Main execution function. Should return with either: self.fail, self.step or self.success """
        if self._progress_code<10:
            return self.step("Step")
        else:
            pose = self.params["Target"].value
            pose.setData(":Position", [5.0 , 0.0, 0.0])
            self.wmi.add_element(pose)
            return self.success("Done")

    def onEnd(self):
        """Called just after last execute OR preemption"""
        return True

class move_primitive(PrimitiveBase):
    """
    This primitive has 3 states
    """
    def createDescription(self):
        """Set the primitive type"""
        self.setDescription(MovePrimitive(), self.__class__.__name__)

    def onInit(self):
        """Called once when loading the primitive. If return False, the primitive is not loaded"""
        return True

    def onPreempt(self):
        """ Called when skill is requested to stop. """
        return self.fail("Stopped", -1)

    def onStart(self):
        """Called just before 1st execute"""
        self.temp_pos = 0.0
        return True

    def execute(self):
        """ Main execution function. Should return with either: self.fail, self.step or self.success """
        self.temp_pos += 1.0
        bot = self.params["Robot"].value
        bot_pos = bot.getData(":Position")[0]
        target_pos = self.params["Target1"].value.getData(":Position")[0]
        rospy.loginfo(f"Robot pos {bot_pos} target pos {target_pos}")
        if bot_pos != target_pos:
            rospy.loginfo("Changing")
            bot.setData(":Position", [self.temp_pos, 0.0, 0.0])
            self.params["Robot"].value = bot
            return self.step("Step")
        else:
            return self.success("Done")

    def onEnd(self):
        """Called just after last execute OR preemption"""
        return True
