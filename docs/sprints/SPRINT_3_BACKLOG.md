# Sprint 3 Backlog: Gazebo-Focused LOTUSim Onboarding and Scenario Contribution

Sprint length: 2 weeks

Assumed sprint dates: 2026-04-13 to 2026-04-24

Sprint owner: Student contributor

Sprint focus: Build practical Gazebo/SDF understanding and produce a small
LOTUSim scenario/model contribution that can be demonstrated and documented.

## Sprint Goal

By the end of Sprint 3, I should be able to explain how LOTUSim loads Gazebo
worlds and models, identify the key Gazebo-related source files, and deliver a
small scenario/model change that demonstrates my understanding of the
`assets/worlds`, `assets/models`, and `systems` structure.

## Sprint Outcome

Expected deliverables:

- A documented Gazebo-focused learning pathway for this repo.
- A clear folder/file map for Gazebo-related LOTUSim work.
- A small copied or new scenario world that includes at least one existing model.
- A short validation note showing what was changed and how it was tested.
- A list of next candidate contribution areas for Sprint 4.

## Sprint Assumptions

- The main learning focus is Gazebo, not deep ROS 2 yet.
- The first practical contribution should be low-risk and mostly SDF/world based.
- The scenario should use existing assets before creating a complex new model.
- ROS 2 is only touched where needed to understand plugin wiring.

## Definition Of Done

A Sprint 3 item is done when:

- The relevant file or documentation has been created or updated.
- The work is linked to the sprint goal.
- Acceptance criteria are satisfied.
- The change is easy for a supervisor or teammate to review.
- Any testing or validation result is written down.

## Jira-Style Backlog

| Key | Type | Priority | Estimate | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| LOTUS-S3-EPIC-1 | Epic | High | 2 weeks | Gazebo-first onboarding and first scenario contribution | To Do |
| LOTUS-S3-1 | Story | High | 3 pts | Document the Gazebo-focused learning pathway for LOTUSim | Done |
| LOTUS-S3-2 | Story | High | 3 pts | Map folders and files related to Gazebo worlds, models, and plugins | Done |
| LOTUS-S3-3 | Story | High | 5 pts | Create a simple Sprint 3 demonstration scenario using existing Gazebo assets | To Do |
| LOTUS-S3-4 | Task | Medium | 2 pts | Study default world and circling ship example world | To Do |
| LOTUS-S3-5 | Task | Medium | 2 pts | Study simple model SDF files and identify reusable model patterns | To Do |
| LOTUS-S3-6 | Task | Medium | 2 pts | Trace one Gazebo plugin from world file to C++ source registration | To Do |
| LOTUS-S3-7 | Task | High | 3 pts | Add an existing model to a copied scenario world | To Do |
| LOTUS-S3-8 | Task | Medium | 2 pts | Validate the scenario loads and document observed behavior | To Do |
| LOTUS-S3-9 | Task | Medium | 2 pts | Prepare Sprint 3 review notes and Sprint 4 recommendations | To Do |

Total estimate: 24 story points

Recommended committed sprint scope: 16 to 18 story points

Stretch scope: remaining tasks if build/run environment is stable.

## Detailed Tickets

### LOTUS-S3-EPIC-1: Gazebo-first onboarding and first scenario contribution

Type: Epic

Priority: High

Estimate: 2 weeks

Description:

Build the foundation needed to contribute to LOTUSim through Gazebo worlds,
models, and scenario work. The epic focuses on understanding the simulator
structure, documenting the learning pathway, and producing a small demonstrable
scenario contribution.

Acceptance criteria:

- Gazebo-related folders are identified.
- A beginner reading order exists.
- At least one practical Gazebo/SDF task is completed.
- Sprint review notes explain what was learned and what should come next.

### LOTUS-S3-1: Document the Gazebo-focused learning pathway for LOTUSim

Type: Story

Priority: High

Estimate: 3 points

Status: Done

Description:

Create a beginner-friendly learning pathway that explains what to study first
when focusing on Gazebo, worlds, models, and plugin source code.

Acceptance criteria:

- A dedicated Gazebo learning document exists.
- It explains what technologies to learn first.
- It includes a week-by-week learning plan.
- It includes practical exercises for adding or modifying a model/world.
- It is linked from existing onboarding docs.

Repo reference:

- `docs/GAZEBO_LEARNING_PATHWAY.md`
- `docs/STUDENT_PROJECT_GUIDE.md`
- `docs/BEGINNER_SYSTEM_ARCHITECTURE.md`

### LOTUS-S3-2: Map folders and files related to Gazebo worlds, models, and plugins

Type: Story

Priority: High

Estimate: 3 points

Status: Done

Description:

Create a clear file and folder map that explains where Gazebo-related work
happens in the repository.

Acceptance criteria:

- `assets/worlds/` is explained.
- `assets/models/` is explained.
- `systems/` Gazebo plugins are explained.
- Key files are listed in reading order.
- The map separates beginner files from advanced files.

Repo reference:

- `docs/GAZEBO_LEARNING_PATHWAY.md`

### LOTUS-S3-3: Create a simple Sprint 3 demonstration scenario using existing Gazebo assets

Type: Story

Priority: High

Estimate: 5 points

Status: To Do

Description:

Create a small scenario world by copying an existing example world and adding at
least one existing model asset, such as `mine`, `wamv`, or `dtmb_hull`. The
goal is not to build a complex new feature yet, but to demonstrate that the
world/model loading flow is understood.

Suggested implementation:

- Copy `assets/worlds/circling_ship_example.world`.
- Create `assets/worlds/sprint3_gazebo_scenario.world`.
- Add one extra `<include>` block for `model://mine`.
- Set a clear pose so the object appears near the existing vessel.
- Keep the existing LOTUSim plugin setup unchanged.

Acceptance criteria:

- A new world file exists under `assets/worlds/`.
- The world includes at least one existing model through `<include>`.
- The scenario still loads the core LOTUSim plugins.
- The scenario can be run with `lotusim run sprint3_gazebo_scenario.world`.
- A short validation note describes what should appear in Gazebo.

Suggested repo reference:

- `assets/worlds/circling_ship_example.world`
- `assets/models/mine/model.sdf`

### LOTUS-S3-4: Study default world and circling ship example world

Type: Task

Priority: Medium

Estimate: 2 points

Status: To Do

Description:

Read the default and beginner scenario worlds to understand the world structure,
loaded plugins, model includes, and `lotus_param` usage.

Files to study:

- `assets/worlds/lotusim.world`
- `assets/worlds/circling_ship_example.world`

Acceptance criteria:

- Notes identify all plugins loaded by `lotusim.world`.
- Notes explain what model is included in `circling_ship_example.world`.
- Notes explain what the `waypoint_follower` block does at a high level.
- Notes explain what the `render_interface` block does at a high level.

### LOTUS-S3-5: Study simple model SDF files and identify reusable model patterns

Type: Task

Priority: Medium

Estimate: 2 points

Status: To Do

Description:

Read simple model SDF files to understand the model folder structure, mesh URI
usage, collision geometry, and sensor declarations.

Files to study:

- `assets/models/mine/model.sdf`
- `assets/models/wamv/model.sdf`
- `assets/models/dtmb_hull/model.sdf`

Acceptance criteria:

- Notes explain the difference between a world file and a model file.
- Notes identify where mesh files are referenced.
- Notes identify at least one model with a custom sensor.
- Notes identify which model is easiest to reuse for a first scenario.

### LOTUS-S3-6: Trace one Gazebo plugin from world file to C++ source registration

Type: Task

Priority: Medium

Estimate: 2 points

Status: To Do

Description:

Trace the `waypoint_plugin` from its world file declaration to its C++ plugin
class and registration macro.

Files to study:

- `assets/worlds/circling_ship_example.world`
- `systems/waypoint_follower/include/waypoint_follower/waypoint_follower.hpp`
- `systems/waypoint_follower/src/waypoint_follower.cpp`

Acceptance criteria:

- Notes identify the `<plugin filename="waypoint_plugin">` world block.
- Notes identify the `WaypointFollowerPlugin` class.
- Notes identify the `GZ_ADD_PLUGIN` registration.
- Notes explain `Configure` and `Update` at a beginner level.

### LOTUS-S3-7: Add an existing model to a copied scenario world

Type: Task

Priority: High

Estimate: 3 points

Status: To Do

Description:

Add an existing model, preferably `mine`, to a copied scenario world using a
Gazebo `<include>` block.

Suggested snippet:

```xml
<include>
  <uri>model://mine</uri>
  <name>mine_01</name>
  <pose>30 0 0 0 0 0</pose>
</include>
```

Acceptance criteria:

- The copied world includes `model://mine`.
- The model has a unique name.
- The model pose is intentionally chosen.
- The original example world remains unchanged.
- The new scenario file name clearly indicates Sprint 3 or its purpose.

### LOTUS-S3-8: Validate the scenario loads and document observed behavior

Type: Task

Priority: Medium

Estimate: 2 points

Status: To Do

Description:

Run or inspect the new scenario and document what should happen. If the local
environment cannot run Gazebo, document that limitation and validate through
file review instead.

Suggested command:

```bash
lotusim run sprint3_gazebo_scenario.world
```

Acceptance criteria:

- Validation notes exist.
- Notes include the command used or explain why it could not be run.
- Notes describe expected visible models.
- Notes describe any errors or blockers.
- Notes include next debugging step if validation fails.

### LOTUS-S3-9: Prepare Sprint 3 review notes and Sprint 4 recommendations

Type: Task

Priority: Medium

Estimate: 2 points

Status: To Do

Description:

Prepare a short sprint review summary explaining what was learned, what was
created, what was validated, and what should be attempted next.

Acceptance criteria:

- Review notes summarize completed work.
- Review notes include screenshots or validation observations if available.
- Review notes list blockers.
- Review notes propose 2 to 3 Sprint 4 options.

Suggested Sprint 4 options:

- Create a new model variant.
- Add a sensor to an existing model.
- Improve waypoint scenario validation.
- Start learning ROS 2 topics/services used by the scenario.

## Suggested Sprint 3 Board

### To Do

- LOTUS-S3-3: Create a simple Sprint 3 demonstration scenario using existing Gazebo assets
- LOTUS-S3-4: Study default world and circling ship example world
- LOTUS-S3-5: Study simple model SDF files and identify reusable model patterns
- LOTUS-S3-6: Trace one Gazebo plugin from world file to C++ source registration
- LOTUS-S3-7: Add an existing model to a copied scenario world
- LOTUS-S3-8: Validate the scenario loads and document observed behavior
- LOTUS-S3-9: Prepare Sprint 3 review notes and Sprint 4 recommendations

### In Progress

- None

### Done

- LOTUS-S3-1: Document the Gazebo-focused learning pathway for LOTUSim
- LOTUS-S3-2: Map folders and files related to Gazebo worlds, models, and plugins

## Recommended Sprint 3 Review Script

Use this structure for the sprint submission:

1. Sprint goal: Explain Gazebo-first onboarding and create a small scenario contribution.
2. Work completed: Mention documentation, file mapping, and any scenario work.
3. Demo: Run or show `sprint3_gazebo_scenario.world`.
4. Validation: Explain what was tested and what appeared in Gazebo.
5. Learning: Explain worlds, models, plugins, and `lotus_param`.
6. Blockers: Mention build/run issues if any.
7. Sprint 4 plan: Propose the next model, sensor, or scenario enhancement.

## Sprint 3 Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Gazebo environment does not run locally | Scenario cannot be visually validated | Validate SDF structure and document run blocker clearly |
| Scope becomes too broad | Sprint may not finish | Keep Sprint 3 focused on existing assets and one scenario |
| ROS 2 complexity slows progress | Gazebo learning gets delayed | Avoid ROS 2 implementation unless needed for validation |
| New model creation takes too long | No demonstrable output | Use existing models first, create new models in Sprint 4 |

## Sprint 3 Definition Of Ready

Before starting a ticket:

- The target file is known.
- The expected output is clear.
- The ticket can be completed in 1 to 2 days.
- The task supports the Sprint 3 goal.

## Sprint 3 Definition Of Done Checklist

Use this before submission:

- Documentation is readable by a beginner.
- File paths are correct.
- Scenario file, if created, uses existing models correctly.
- Validation notes are written.
- Sprint review notes are prepared.
- Sprint 4 recommendation is included.
