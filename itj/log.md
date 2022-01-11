# Nine-pieces

## FD

### ff_eager
84, Expanded 778, Evaluated 2055
<details>
  <summary>log</summary>
    [t=0.0326323s, 1080 KB] Plan length: 84 step(s).
    [t=0.0326323s, 1080 KB] Plan cost: 84
    [t=0.0326323s, 1080 KB] Expanded 778 state(s).
    [t=0.0326323s, 1080 KB] Reopened 0 state(s).
    [t=0.0326323s, 1080 KB] Evaluated 2055 state(s).
    [t=0.0326323s, 1080 KB] Evaluations: 2055
    [t=0.0326323s, 1080 KB] Generated 3045 state(s).
    [t=0.0326323s, 1080 KB] Dead ends: 581 state(s).
    [t=0.0326323s, 1080 KB] Number of registered states: 2055
    [t=0.0326323s, 1080 KB] Int hash set load factor: 2055/4096 = 0.501709
    [t=0.0326323s, 1080 KB] Int hash set resizes: 12
    [t=0.0326323s, 1080 KB] Search time: 0.0268593s
    [t=0.0326323s, 1080 KB] Total time: 0.0326323s
</details>

### max-astar
78, Expand 10465, Evaluated 24410

<details>
  <summary>log</summary>
	[t=0.253117s, 2484 KB] Plan length: 78 step(s).
	[t=0.253117s, 2484 KB] Plan cost: 78
	[t=0.253117s, 2484 KB] Expanded 10465 state(s).
	[t=0.253117s, 2484 KB] Reopened 0 state(s).
	[t=0.253117s, 2484 KB] Evaluated 24410 state(s).
	[t=0.253117s, 2484 KB] Evaluations: 24410
	[t=0.253117s, 2484 KB] Generated 43785 state(s).
	[t=0.253117s, 2484 KB] Dead ends: 13861 state(s).
	[t=0.253117s, 2484 KB] Expanded until last jump: 10461 state(s).
	[t=0.253117s, 2484 KB] Reopened until last jump: 0 state(s).
	[t=0.253117s, 2484 KB] Evaluated until last jump: 24404 state(s).
	[t=0.253117s, 2484 KB] Generated until last jump: 43774 state(s).
	[t=0.253117s, 2484 KB] Number of registered states: 24410
	[t=0.253117s, 2484 KB] Int hash set load factor: 24410/32768 = 0.744934
	[t=0.253117s, 2484 KB] Int hash set resizes: 15
	[t=0.253117s, 2484 KB] Search time: 0.247097s
	[t=0.253117s, 2484 KB] Total time: 0.253117s
</details>

### Dijstra

78, Expand 29644, Evaluated 29671

<details>
  <summary>log</summary>
	[t=0.222225s, 2716 KB] Plan length: 78 step(s).
	[t=0.222225s, 2716 KB] Plan cost: 78
	[t=0.222225s, 2716 KB] Expanded 29644 state(s).
	[t=0.222225s, 2716 KB] Reopened 0 state(s).
	[t=0.222225s, 2716 KB] Evaluated 29671 state(s).
	[t=0.222225s, 2716 KB] Evaluations: 29671
	[t=0.222225s, 2716 KB] Generated 91120 state(s).
	[t=0.222225s, 2716 KB] Dead ends: 0 state(s).
	[t=0.222225s, 2716 KB] Expanded until last jump: 29642 state(s).
	[t=0.222225s, 2716 KB] Reopened until last jump: 0 state(s).
	[t=0.222225s, 2716 KB] Evaluated until last jump: 29670 state(s).
	[t=0.222225s, 2716 KB] Generated until last jump: 91118 state(s).
	[t=0.222225s, 2716 KB] Number of registered states: 29671
	[t=0.222225s, 2716 KB] Int hash set load factor: 29671/32768 = 0.905487
	[t=0.222225s, 2716 KB] Int hash set resizes: 15
	[t=0.222225s, 2716 KB] Search time: 0.217229s
	[t=0.222225s, 2716 KB] Total time: 0.222225s
</details>

## pyplanners

## ff-Eager
	Iterations: 1349 | State Space: 1173 | Expanded: 1172 | Generations: 1172 | Heuristic: 0 | Time: 7.551
	Plan operators # 84

## ff-a_star
	Iterations: 519 | State Space: 2159 | Expanded: 1233 | Generations: 1233 | Heuristic: 0 | Time: 8.640
	Plan operators # 84

## max-a_star
	Iterations: 2237 | State Space: 9563 | Expanded: 7231 | Generations: 7231 | Heuristic: 0 | Time: 35.824
	Plan operators # 78

## Blind-a_star (dijkstra)

	Iterations: 29288 | State Space: 29392 | Expanded: 29359 | Generations: 29359 | Heuristic: 0 | Time: 51.299
	Plan operators # 78


# Cantibox

## FD

### ff-eager

254, Expanded 23924, Evaluated 76099
<details>
  <summary>log</summary>
    [t=3.41972s, 7968 KB] Plan length: 254 step(s).
    [t=3.41972s, 7968 KB] Plan cost: 254
    [t=3.41972s, 7968 KB] Expanded 23924 state(s).
    [t=3.41972s, 7968 KB] Reopened 0 state(s).
    [t=3.41972s, 7968 KB] Evaluated 76099 state(s).
    [t=3.41972s, 7968 KB] Evaluations: 76099
    [t=3.41972s, 7968 KB] Generated 299532 state(s).
    [t=3.41972s, 7968 KB] Dead ends: 35048 state(s).
    [t=3.41972s, 7968 KB] Number of registered states: 76099
    [t=3.41972s, 7968 KB] Int hash set load factor: 76099/131072 = 0.580589
    [t=3.41972s, 7968 KB] Int hash set resizes: 17
    [t=3.41972s, 7968 KB] Search time: 3.40296s
    [t=3.41972s, 7968 KB] Total time: 3.41972s
</details>

### max-astar

222, Expanded 4148777, Evaluated 15337429
<details>
  <summary>log</summary>
    [t=561.035s, 1280988 KB] Plan length: 222 step(s).
    [t=561.035s, 1280988 KB] Plan cost: 222
    [t=561.035s, 1280988 KB] Expanded 4148777 state(s).
    [t=561.035s, 1280988 KB] Reopened 0 state(s).
    [t=561.035s, 1280988 KB] Evaluated 15337429 state(s).
    [t=561.035s, 1280988 KB] Evaluations: 15337429
    [t=561.035s, 1280988 KB] Generated 72218044 state(s).
    [t=561.035s, 1280988 KB] Dead ends: 11186040 state(s).
    [t=561.035s, 1280988 KB] Expanded until last jump: 4148773 state(s).
    [t=561.035s, 1280988 KB] Reopened until last jump: 0 state(s).
    [t=561.035s, 1280988 KB] Evaluated until last jump: 15337419 state(s).
    [t=561.035s, 1280988 KB] Generated until last jump: 72217993 state(s).
    [t=561.035s, 1280988 KB] Number of registered states: 15337429
    [t=561.035s, 1280988 KB] Int hash set load factor: 15337429/33554432 = 0.457091
    [t=561.035s, 1280988 KB] Int hash set resizes: 25
    [t=561.035s, 1280988 KB] Search time: 561.021s
    [t=561.035s, 1280988 KB] Total time: 561.035s
</details>

----

In a problem where each object has a set of predetermined poses and a fixed construction sequence, given that we have the current performance difference between `FD` and `pyplanner`, what modeling choice can we make to make the planning faster?
- Should we "open the blackbox" and delegate all the collision checking to the PDDL and stream level so we can use FD?
- Or should we use the fluents and get the stream function sample more efficiently, but we have to bear with pyplanners' slowness...

My plan for now is to model everything in a symbolic fashion in the PDDL level (so no poses, conf and trajectory predicates in the pddl domain, and hide all of these in the stream function). 