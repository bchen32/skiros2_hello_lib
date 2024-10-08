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
        self.addParam("TargetLoc", Element("skiros:Location"), ParamTypes.Required)
        self.addParam("TargetPose", Element("skiros:TransformationPose"), ParamTypes.Required)

class MovePrimitive(SkillDescription):
    def createDescription(self):
        self.addParam("Robot", Element("cora:Robot"), ParamTypes.Required)
        self.addParam("TargetPose", Element("skiros:TransformationPose"), ParamTypes.Required)

class Look(SkillDescription):
    def createDescription(self):
        self.addParam("TargetLoc", Element("skiros:Location"), ParamTypes.Required)
        self.addParam("TargetPose", Element("skiros:TransformationPose"), ParamTypes.Required)
        self.addParam("ParentScene", Element("skiros:Scene"), ParamTypes.Required)
        self.addPreCondition(self.getRelationCond("SceneHasTarget", "skiros:contain", "ParentScene", "TargetLoc", True))
        self.addPostCondition(self.getHasPropCond("HasPositionXPost", "skiros:PositionX", "TargetPose", True))
        self.addPostCondition(self.getRelationCond("TargetPoseAtLocPost", "skiros:at", "TargetPose", "TargetLoc", True))

class Drive(SkillDescription):
    def createDescription(self):
        self.addParam("Robot", Element("cora:Robot"), ParamTypes.Required)
        self.addParam("StartLocation", Element("skiros:Location"), ParamTypes.Inferred)
        self.addParam("TargetPose", Element("skiros:TransformationPose"), ParamTypes.Required)
        self.addParam("TargetLoc", Element("skiros:Location"), ParamTypes.Required)
        self.addPreCondition(self.getRelationCond("RobotAtPre", "skiros:at", "Robot", "StartLocation", True))
        self.addPreCondition(self.getHasPropCond("HasPositionXPre", "skiros:PositionX", "TargetPose", True))
        self.addPreCondition(self.getRelationCond("TargetPoseAtLocPre", "skiros:at", "TargetPose", "TargetLoc", True))
        self.addPostCondition(self.getRelationCond("NoRobotAt", "skiros:at", "Robot", "StartLocation", False))
        self.addPostCondition(self.getRelationCond("RobotAtPost", "skiros:at", "Robot", "TargetLoc", True))

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
            pose = self.params["TargetPose"].value
            pose.setData(":Position", [5.0 , 0.0, 0.0])
            self.params["TargetPose"].value = pose
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
        self.pos = 0.0
        return True

    def execute(self):
        """ Main execution function. Should return with either: self.fail, self.step or self.success """
        self.pos += 1.0
        bot = self.params["Robot"].value
        bot_pos = bot.getData(":Position")[0]
        target_pos = self.params["TargetPose"].value.getData(":Position")[0]
        rospy.loginfo(f"Robot pos {bot_pos} target pos {target_pos}")
        if bot_pos != target_pos:
            rospy.loginfo("Changing")
            bot.setData(":Position", [self.pos, 0.0, 0.0])
            self.params["Robot"].value = bot
            return self.step("Step")
        else:
            return self.success("Done")

    def onEnd(self):
        """Called just after last execute OR preemption"""
        return True

class look(SkillBase):
    def createDescription(self):
        self.setDescription(Look(), self.__class__.__name__)

    def set_at(self, src, dst, state):
      return self.skill("WmSetRelation", "wm_set_relation",
          remap={'Dst': dst},
          specify={'Src': self.params[src].value, 'Relation': 'skiros:at', 'RelationState': state})

    def expand(self, skill):
        skill(
            self.skill("ScanPrimitive", "scan_primitive", specify={"TargetLoc": self.params["TargetLoc"].value, "TargetPose": self.params["TargetPose"].value}),
            self.set_at("TargetPose", "TargetLoc", True)
        )

class drive(SkillBase):
    def createDescription(self):
        self.setDescription(Drive(), self.__class__.__name__)

    def set_at(self, src, dst, state):
      return self.skill("WmSetRelation", "wm_set_relation",
          remap={'Dst': dst},
          specify={'Src': self.params[src].value, 'Relation': 'skiros:at', 'RelationState': state})

    def expand(self, skill):
        skill(
            self.skill("MovePrimitive", "move_primitive", specify={"Robot": self.params["Robot"].value, "TargetPose": self.params["TargetPose"].value}),
            self.set_at("Robot", "TargetLoc", True),
            self.set_at("Robot", "StartLocation", False)
        )