(define (domain itj_clamp_only)
  (:requirements :strips :equality)
  (:predicates
    ; switch for including move action or not
    (ConsiderTransition)

    ; * Static predicates (predicates that do not change over time)
    (Element ?element)
    (Scaffold ?element)

    (Joint ?element1 ?element2)
    (Grounded ?element)
    (JointToolTypeMatch ?element1 ?element2 ?tool)
    (GripperToolTypeMatch ?element ?tool)

    (Gripper ?g)
    (Clamp ?c)
    (ScrewDriver ?sd)
    (Tool ?tool)

    ; * static predicates but will be produced by stream functions
    (Pose ?pose)
    (Traj ?traj)
    (RobotConf ?conf)

    (PlaceElementAction ?element ?traj)

    ; * optional
    (Order ?element1 ?element2)

    ; * Fluent predicates (predicates that change over time, which describes the state of the sytem)
    (RobotAtConf ?conf)
    (Attached ?object) ; o can be element, gripper or clamp
    (RobotToolChangerEmpty)
    (RobotGripperEmpty)
    (CanFreeMove)

    (ToolAtJoint ?tool ?element1 ?element2)
    (ToolNotOccupiedOnJoint ?tool)
    (NoToolAtJoint ?element1 ?element2)

    (AtRack ?object) ; object can be either element or tool
    (Assembled ?element)

    ;; * derived
    (Connected ?element)
    (EitherGroundedAllToolAtJoints ?element)
    (EitherAssembled ?e1 ?e2)
    (NotGripper ?tool)

    ; ? equivalent
    (AllToolAtJoints ?element)
    (ExistNoToolAtJoints ?element)
  )

  (:action pick_element_from_rack
    :parameters (?element ?tool)
    :precondition (and
                    ; ! state precondition
                    ;; (imply (ConsiderTransition) (and (not (CanFreeMove)) (RobotAtConf ?conf1)))
                    (Gripper ?tool)
                    (GripperToolTypeMatch ?element ?tool)
                    (Attached ?tool)
                    (RobotGripperEmpty)
                    (Element ?element)
                    (AtRack ?element)
                    ; ! assembly state precondition
                    (Connected ?element)
                    ; ! e2 must be assembled before e encoded in the given partial ordering
                    (forall (?ei) (imply (Order ?ei ?element) (Assembled ?ei)))
                    ; ! sampled
                  )
    :effect (and (not (AtRack ?element))
                 (Attached ?element)
                 (not (RobotGripperEmpty))
                 ; ! switch for move
                 (CanFreeMove)
            )
  )

  ; an element can only be placed if all the clamps are (attached) to the corresponding joints
  ; we can query a partial structure and a new element's connection joints using fluent
  (:action place_element_on_structure
    :parameters (?element ?traj ?tool)
    :precondition (and
                    ; ! robot state precondition
                    ;; (imply (ConsiderTransition) (and (not (CanFreeMove)) (RobotAtConf ?conf1)))
                    (Gripper ?tool)
                    (Attached ?tool)
                    (Attached ?element)
                    (Element ?element)
                    ; ! assembly state precondition
                    (Connected ?element)
                    ; ! tool state precondition
                    ;; (or (Grounded ?element) (AllToolAtJoints ?element))
                    ;; (EitherGroundedAllToolAtJoints ?element)
                    ; ! e2 must be assembled before e encoded in the given partial ordering
                    (forall (?ei) (imply (Order ?ei ?element) (Assembled ?ei)))
                    ; ! sampled
                    (PlaceElementAction ?element ?traj)
                    )
    :effect (and (Assembled ?element)
                 (not (Attached ?element))
                 (RobotGripperEmpty)
                 ; ! switch for move
                 (CanFreeMove)
                 )
  )

  (:action pick_tool_from_rack
    :parameters (?tool) ;?conf1 ?conf2 ?traj)
    :precondition (and
                    ; ! state precondition
                    ;; (imply (ConsiderTransition) (and (not (CanFreeMove)) (RobotAtConf ?conf1)))
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
                 ; ! switch for move
                 (CanFreeMove)
            )
  )

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

  (:action place_tool_at_rack
    :parameters (?tool) ; ?conf1 ?conf2 ?traj)
    :precondition (and
                    ; ! robot state precondition
                    ;; (imply (ConsiderTransition) (and (not (CanFreeMove)) (RobotAtConf ?conf1)))
                    (Attached ?tool)
                    (Tool ?tool)
                    (imply (Gripper ?tool) (RobotGripperEmpty))
                    ; ! sampled
                    )
    :effect (and (not (Attached ?tool))
                 (RobotToolChangerEmpty)
                 ; ! tool status
                 (AtRack ?tool)
                 ; ! switch for move
                 (CanFreeMove)
                 )
  )

  ;; * Specific pick_from_joint action for clamps only
  (:action pick_clamp_from_joint
    :parameters (?tool ?element1 ?element2) ; ?conf1 ?conf2 ?traj)
    :precondition (and
                    ; ! state precondition
                    ;; (imply (ConsiderTransition) (and (not (CanFreeMove)) (RobotAtConf ?conf1)))
                    (RobotToolChangerEmpty)
                    ;; (Clamp ?tool)
                    ;; (or (Clamp ?tool) (ScrewDriver ?tool))
                    (NotGripper ?tool)
                    (Element ?element1)
                    (Element ?element2)
                    (ToolAtJoint ?tool ?element1 ?element2)
                    ; ! sampled
                  )
    :effect (and (Attached ?tool)
                 (not (RobotToolChangerEmpty))
                 ; ! tool status
                 (ToolNotOccupiedOnJoint ?tool)
                 (not (ToolAtJoint ?tool ?element1 ?element2))
                 (not (ToolAtJoint ?tool ?element2 ?element1))
                 (NoToolAtJoint ?element1 ?element2)
                 (NoToolAtJoint ?element2 ?element1)
                 ; ! switch for move
                 (CanFreeMove)
            )
  )

  ;; tool is attached to the robot
  ;; a tool (gripper, clamp) can be placed if the goal place is clear of collision
  (:action place_clamp_at_joint
    :parameters (?tool ?element1 ?element2) ; ?conf1 ?conf2 ?traj)
    :precondition (and
                    ; ! robot state precondition
                    ;; (imply (ConsiderTransition) (and (not (CanFreeMove)) (RobotAtConf ?conf1)))
                    (Attached ?tool)
                    ;; (Clamp ?tool)
                    ;; (or (Clamp ?tool) (ScrewDriver ?tool))
                    (NotGripper ?tool)
                    (Joint ?element1 ?element2)
                    (Element ?element1)
                    (Element ?element2)
                    (ToolNotOccupiedOnJoint ?tool)
                    (JointToolTypeMatch ?element1 ?element2 ?tool)
                    ;; (or (Assembled ?element1) (Assembled ?element2))
                    (EitherAssembled ?element1 ?element2)
                    (NoToolAtJoint ?element1 ?element2)
                    ; ! assembly state precondition
                    ; ! sampled
                    )
    :effect (and (not (Attached ?tool))
                 (RobotToolChangerEmpty)
                 ; ! tool status
                 (ToolAtJoint ?tool ?element1 ?element2)
                 (ToolAtJoint ?tool ?element2 ?element1)
                 (not (NoToolAtJoint ?element1 ?element2))
                 (not (NoToolAtJoint ?element2 ?element1))
                 (not (ToolNotOccupiedOnJoint ?tool))
                 ; ! switch for move
                 (CanFreeMove)
                 )
  )

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  (:derived (Connected ?element)
   (or (Grounded ?element)
       (exists (?ei) (and 
                          ;; (Element ?ei)
                          (Joint ?ei ?element)
                          (Assembled ?ei)
                          (Connected ?ei)
                     )
       )
   )
  )

  ; ! workaround for a bug in the adaptive algorithm
  (:derived (EitherAssembled ?e1 ?e2)
      (and 
        (Joint ?e1 ?e2)
        (or (Assembled ?e1) (Assembled ?e2))
      )
  )

  (:derived (NotGripper ?tool)
    (or (Clamp ?tool) (ScrewDriver ?tool))
  )

  ;; (:derived (AllToolAtJoints ?element)
  ;;  (and 
  ;;   (IsElement ?element)
  ;;   (forall (?ei) (imply 
  ;;                        (and (Joint ?ei ?element)
  ;;                             (IsElement ?ei)
  ;;                        )
  ;;                        (not (NoToolAtJoint ?ei ?element))
  ;;                       ;;  (exists (?tool)
  ;;                       ;;      (and (Clamp ?tool) ; (Joint ?ei ?element)
  ;;                       ;;           (JointToolTypeMatch ?ei ?element ?tool)
  ;;                       ;;           (ToolAtJoint ?tool ?ei ?element)
  ;;                       ;;      )
  ;;                       ;;  )
  ;;                 )
  ;;   )
  ;;  )
  ;; )

  (:derived (ExistNoToolAtJoints ?element)
       (exists (?ei) (and (Joint ?ei ?element)
                          (NoToolAtJoint ?ei ?element)
                          ;; (forall (?tool) 
                          ;;   (and (Clamp ?tool)
                          ;;        (JointToolTypeMatch ?ei ?element ?tool)
                          ;;        (not (ToolAtJoint ?tool ?ei ?element))
                          ;;   )
                          ;; )
                     )
       )
  )

  (:derived (EitherGroundedAllToolAtJoints ?element)
    (and
        (Element ?element)
        ;; (or (Grounded ?element) (AllToolAtJoints ?element))
        (or (Grounded ?element) (not (ExistNoToolAtJoints ?element)))
    )
  )

)
