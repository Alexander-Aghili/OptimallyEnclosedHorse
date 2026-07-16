# TODO

- [ ] Python scripts to fetch all maps and format them into a directory
- [ ] Support `main.cpp` reading from a map directory and writing a solution file
- [ ] Support all features (cherries, bees, portals, ...)
- [ ] Optimizations

  Ideas to explore, not a checklist — none of these are decided:
  - Warm-start the MIP from a greedy/heuristic wall placement
  - Presolve away water and tiles unreachable from the horse instead of constraining them to zero
  - Lazy escape constraints — add neighbor constraints on demand rather than all upfront
  - Symmetry breaking / dominance cuts on equivalent wall placements
  - Restrict the wall search to a bounded region around the horse
  - Tune HiGHS (threads, MIP gap, branching) and reuse one solver instance across maps
  - Solve maps in parallel across cores

- [ ] Writeup
