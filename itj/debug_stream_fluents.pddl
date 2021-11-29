(define (stream itj_clamp_only)

  (:stream sample-place-element
    :inputs (?element)
    :domain (IsElement ?element)
    :fluents (Assembled)
    :outputs (?traj) ; ?conf1 ?conf2 
    :certified (and
                    (PlaceElementAction ?element ?traj)
                    (Traj ?traj)
                    ;; (PlaceStartRobotConf ?conf1)
                    ;; (PlaceEndRobotConf ?conf2)
                )
  )
)
