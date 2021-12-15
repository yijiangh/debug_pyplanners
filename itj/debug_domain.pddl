(define (domain itj_clamp_only)
  (:requirements :strips :equality)
  (:predicates
    ; * Static predicates (predicates that do not change over time)
    (Element ?element)
    (GroundContactElement ?element)
    (Scaffold ?element) ;; ManualAssembly
    (ClampedElement ?element)
    (ScrewedWithGripperElement ?element)
    (ScrewedWithoutGripperElement ?element)

    (Joint ?element1 ?element2)
    (JointToolTypeMatch ?element1 ?element2 ?tool)
    (GripperToolTypeMatch ?element ?tool)

    (Gripper ?g)
    (Clamp ?c)
    (ScrewDriver ?sd)
    (Tool ?tool)

    ; * static predicates but will be produced by stream functions
    (Traj ?traj)
    (PlaceElementAction ?element ?traj)

    ; * optional
    (Order ?element1 ?element2)

    ; * Fluent predicates (predicates that change over time, which describes the state of the sytem)
    (Attached ?object) ; o can be element, gripper or clamp
    (RobotToolChangerEmpty)
    (RobotGripperEmpty)

    (ToolNotOccupiedOnJoint ?tool)
    (ToolAtJoint ?tool ?element1 ?element2)
    (JointOccupiedByTool ?element1 ?element2)

    (AtRack ?object) ; object can be either element or tool
    (Assembled ?element)

    ;; * derived
    (Connected ?element)
    ;; ? (EitherGroundContactElementAllToolAtJoints ?element)
    (EitherGroundContactElementExistToolAtJoints ?element)
    ;; (EitherAssembled ?e1 ?e2)
    ;; (NotGripper ?tool)

    (JointMade ?e1 ?e2)

    ; ? equivalent
    ;; (AllToolAtJoints ?element)
    ;; (AllToolAtAssembledJoints ?element)
    (ExistNoToolAtOneAssembledJoints ?element)
  )

  (:action pick_element_from_rack
    :parameters (?element ?tool)
    :precondition (and
                    (Gripper ?tool)
                    (GripperToolTypeMatch ?element ?tool)
                    (Attached ?tool)
                    (RobotGripperEmpty)
                    (Element ?element)
                    (AtRack ?element)
                    ; ! assembly state precondition
                    (Connected ?element)
                    ; ! tool state precondition
                    ;; (EitherGroundContactElementExistToolAtJoints ?element)
                    ; ! e2 must be assembled before e encoded in the given partial ordering
                    (forall (?ei) (imply (Order ?ei ?element) (Assembled ?ei)))
                    ; ! sampled
                  )
    :effect (and (not (AtRack ?element))
                 (Attached ?element)
                 (not (RobotGripperEmpty))
            )
  )

  ; an element can only be placed if all the clamps are (attached) to the corresponding joints
  ; we can query a partial structure and a new element's connection joints using fluent
  (:action place_element_on_structure
    :parameters (?element ?traj ?tool)
    :precondition (and
                    (Gripper ?tool)
                    (Attached ?tool)
                    (Attached ?element)
                    (Element ?element)
                    ; ! assembly state precondition
                    (Connected ?element)
                    ; ! tool state precondition
                    (EitherGroundContactElementExistToolAtJoints ?element)
                    ; ! e2 must be assembled before e encoded in the given partial ordering
                    (forall (?ei) (imply (Order ?ei ?element) (Assembled ?ei)))
                    ; ! sampled
                    (PlaceElementAction ?element ?traj)
                    )
    :effect (and (Assembled ?element)
                 (not (Attached ?element))
                 (RobotGripperEmpty)
                 )
  )

  ;; (:action retract_gripper_from_beam

  ;; (:action AssembleBeamWithScrewdriversAction
  ;; (:action RetractScrewdriverFromBeamAction

  (:action manual_assemble_element
    :parameters (?element)
    :precondition (and
                    (Scaffold ?element)
                    ; ! e2 must be assembled before e encoded in the given partial ordering
                    (forall (?ei) (imply (Order ?ei ?element) (Assembled ?ei)))
                    )
    :effect (and (Assembled ?element)
                 )
  )

  (:action pick_tool_from_rack
    :parameters (?tool) ;?conf1 ?conf2 ?traj)
    :precondition (and
                    (RobotToolChangerEmpty)
                    (Tool ?tool)
                    (AtRack ?tool)
                    ; ! sampled
                  )
    :effect (and (Attached ?tool)
                 (not (RobotToolChangerEmpty))
                 ; ! tool status
                 (not (AtRack ?tool))
                 (when (Gripper ?tool) (RobotGripperEmpty))
            )
  )

  (:action place_tool_at_rack
    :parameters (?tool)
    :precondition (and
                    (Attached ?tool)
                    (Tool ?tool)
                    (imply (Gripper ?tool) (RobotGripperEmpty))
                    ; ! sampled
                    )
    :effect (and (not (Attached ?tool))
                 (RobotToolChangerEmpty)
                 ; ! tool status
                 (AtRack ?tool)
                 )
  )
  
  ;; tool is attached to the robot
  ;; a tool (gripper, clamp) can be placed if the goal place is clear of collision
  (:action place_clamp_at_joint
    :parameters (?tool ?element1 ?element2) ; ?conf1 ?conf2 ?traj)
    :precondition (and
                    (Attached ?tool)
                    (Clamp ?tool)
                    (Joint ?element1 ?element2)
                    (ToolNotOccupiedOnJoint ?tool)
                    (JointToolTypeMatch ?element1 ?element2 ?tool)
                    ;; ? (or (Assembled ?element1) (Assembled ?element2))
                    ;; ! (EitherAssembled ?element1 ?element2)
                    (Assembled ?element1)
                    (not (JointOccupiedByTool ?element1 ?element2))
                    ; ! switch for cutting down meaningless clamp placements
                    (not (JointMade ?element1 ?element2))
                    ; ! assembly state precondition
                    ; ! sampled
                    )
    :effect (and (not (Attached ?tool))
                 (RobotToolChangerEmpty)
                 ; ! tool status
                 (ToolAtJoint ?tool ?element1 ?element2)
                ;;  (ToolAtJoint ?tool ?element2 ?element1)
                 (JointOccupiedByTool ?element1 ?element2)
                ;;  (JointOccupiedByTool ?element2 ?element1)
                 (not (ToolNotOccupiedOnJoint ?tool))
                 )
  )

  ;; * Specific pick_from_joint action for clamps only
  (:action pick_clamp_from_joint
    :parameters (?tool ?element1 ?element2) ; ?conf1 ?conf2 ?traj)
    :precondition (and
                    (RobotToolChangerEmpty)
                    (Clamp ?tool)
                    (Joint ?element1 ?element2)
                    (ToolAtJoint ?tool ?element1 ?element2)
                    (JointOccupiedByTool ?element1 ?element2)
                    (JointMade ?element1 ?element2)
                    ; ! sampled
                  )
    :effect (and (Attached ?tool)
                 (not (RobotToolChangerEmpty))
                 ; ! tool status
                 (ToolNotOccupiedOnJoint ?tool)
                 (not (ToolAtJoint ?tool ?element1 ?element2))
                ;;  (not (ToolAtJoint ?tool ?element2 ?element1))
                 (not (JointOccupiedByTool ?element1 ?element2))
                ;;  (not (JointOccupiedByTool ?element2 ?element1))
            )
  )

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  (:derived (Connected ?element)
   (or (GroundContactElement ?element)
       (exists (?ei) (and 
                          ;; (Element ?ei)
                          (Joint ?ei ?element)
                          (Assembled ?ei)
                          (Connected ?ei)
                     )
       )
   )
  )

  (:derived (JointMade ?e1 ?e2)
    (imply (Joint ?e1 ?e2) 
           (and (Assembled ?e1) (Assembled ?e2))
    )
  )

  ; ! workaround for a bug in the adaptive algorithm
  ;; (:derived (EitherAssembled ?e1 ?e2)
  ;;     ;; (and 
  ;;       ;; (Joint ?e1 ?e2)
  ;;       (or (Assembled ?e1) (Assembled ?e2))
  ;;     ;; )
  ;; )

  ; * if there is a joint between the current element and an **assembled** element, the clamp must be there
  ;; (:derived (ExistNoToolAtOneAssembledJoints ?element)
  ;;      (forall (?ei) (imply (and (Joint ?ei ?element) (Assembled ?ei))
  ;;                           (JointOccupiedByTool ?ei ?element)
  ;;                    )
  ;;      )
  ;; )

  (:derived (ExistNoToolAtOneAssembledJoints ?element)
       (exists (?ei) (and (Joint ?ei ?element) (Assembled ?ei)
                          (not (JointOccupiedByTool ?ei ?element))
                     )
       )
  )

  (:derived (EitherGroundContactElementExistToolAtJoints ?element)
    (and
        (Element ?element)
        (or (GroundContactElement ?element) (not (ExistNoToolAtOneAssembledJoints ?element)))
        ;; (or (GroundContactElement ?element) (ExistNoToolAtOneAssembledJoints ?element))
    )
  )

)
