(define (stream itj_clamp_only)

  (:stream sample-place-element
    :inputs (?element)
    :domain (IsElement ?element)
    :outputs (?traj)
    :certified (and
                    (PlaceElementAction ?element ?traj)
                    (Traj ?traj)
                )
  )
)
