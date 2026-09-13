---
framework_version: 1.1.1
---

# Candidate Profile

## Identity
- **Name:** Marcus D. Yang
- **Location:** Champaign, IL, USA (open to relocating anywhere in the US for the right internship/role)
- **Phone:** (650) 954-0288
- **Email:** yangdmarcus@gmail.com
- **LinkedIn:** https://www.linkedin.com/in/marcusdyang
- **GitHub:** https://github.com/mdyang26
- **Status:** Undergraduate student (rising junior), University of Illinois Urbana-Champaign, expected graduation May 2028. Seeking a paid, in-person Summer 2027 internship in aerospace, mechanical, or manufacturing engineering.
- **Citizenship/Work Authorization:** U.S. Citizen. Clears citizenship/permanent-residency and export-control ("U.S. Person") requirements outright - no work-authorization or sponsorship concerns for domestic roles.
- **Constraints:** Full-time student during the academic year; available for a full-time internship in Summer 2027. Relocation is not a constraint.

### Languages
| Language | Level | Notes |
|----------|-------|-------|
| English | Native | |

- **CV language:** English

## Education

| Degree | Period | Institution | Key Topics |
|--------|--------|-------------|------------|
| B.S. in Aerospace Engineering, Computer Science Minor (James Scholar Honors) | 2024-2028 (in progress, expected May 2028) | University of Illinois Urbana-Champaign | Incompressible Flow, Aerospace Control Systems, Aerospace Structures, Thermodynamics, Engineering Materials, Statics, Dynamics, Linear Algebra, Electrical and Electronic Circuits, Discrete Structures, Intro to Computer Science I/II |

GPA: 3.57/4.0 (as of Fall 2026, in progress).

## Professional Experience
<!-- No formal paid employment yet - these are academic/organizational technical roles, the standard
substitute for "Professional Experience" on a pre-internship student CV. -->

### Member - Liquid Rocketry at Illinois (Spring 2025 - Present)
Champaign, IL (student rocketry organization)
- Modeled P&ID system architecture in Siemens NX and integrated components into the pressurant tank assembly, sourcing, importing, and constraining CAD hardware to satisfy spatial constraints
- Created CAD geometries for canard-grid fin configurations and ran ANSYS Fluent CFD cases to quantify aerodynamic interactions across 0-20 deg deflection
- Assessed pressurant tank options and produced mechanical integration models, verifying fit against vehicle structural constraints and the P&ID
- Engineered a KiCad PCB radio transmitter (USB-C + MCU) prototype enabling basic telemetry links for ground tests

### Landing Gear Research Lead - Flight Club Aerospace (Summer 2021 - Spring 2024)
Student aerospace club
- Manufactured wing and control surfaces: cut foam ribs with a hot-wire cutter, trimmed aluminum spars with a circular saw, and applied epoxy and fiberglass layups to produce aerodynamic skins; aligned two 7-ft wings for flight testing
- Modeled gussets and ribs in Fusion 360 and coordinated fit-checks between structural and aerodynamic components
- Oversaw logistics for wing transport, disassembly, and reassembly; assembled and presented landing-gear recommendations based on structural load and cost analyses

### Treasurer | Fundraising Officer - Asian American Association (Fall 2024 - Present)
University of Illinois Urbana-Champaign
- Managed membership operations for 200+ members, coordinating records and organizational logistics
- Secured partnerships with 15 on-campus sponsors to support events and fundraising initiatives

## Independent Projects

- **TVC Rocket** (solo project, Summer 2026): Designed, built, and tested a 4"-diameter model rocket with an active two-axis gimbaled thrust-vector-control system - covering simulation, CAD (Siemens NX, NXOpen/Python), 3D-printed structures (FDM, PETG/PLA), embedded firmware (Teensy 4.1, C++), closed-loop PID control, static-fire testing, and post-test telemetry analysis. Built a 6-DOF-informed flight simulation and ran Monte Carlo sensitivity analysis (hundreds of runs, randomized IMU noise/motor scatter/crosswind) that found landing performance was far more sensitive to IMU accelerometer bias than servo speed, redirecting effort toward sensor calibration. Root-caused two independent static-fire failures purely from telemetry: an `atan2` axis-convention bug that fed the wrong reference frame into the attitude estimate, and an inverted control-sign bug producing positive feedback - both diagnosed via statistical analysis of attitude logs, frame-by-frame video tracking, and audio-based event timing. Logged telemetry at 83 Hz with zero dropouts across two static fires (15,728 and 12,611 samples). *(AI assistance disclosure: Claude was used as a coding/analysis assistant for simulation implementation, plotting, and analysis support; all engineering judgment, hardware design, firmware, and failure-analysis conclusions were the candidate's own - disclosed on the project's portfolio page.)*
- **Model Rocket Project** (OpenRocket, Excel, Fall 2024): Designed custom fin geometry in Siemens NX, fabricated a prototype to meet a target apogee, and validated performance with OpenRocket simulations; flight reached 430 ft apogee with 25 ft downrange drift.
- **F-101 Voodoo CAD Reconstruction** (Siemens NX, Spring 2025, ~70 hours): Reconstructed from open-source three-view engineering drawings (front, side, top) that became publicly available after the F-101's retirement from service; established scale from known reference dimensions (wingspan, fuselage length) and derived the remaining measurements from the scaled drawings. Reconstructing the wing's true 3D curvature was the hardest part - required plotting points from all three view angles and cross-referencing them, since no single view captures it. Integrated an articulated aileron using parametric assemblies and constraints; the rest of the airframe geometry is complete and dimensionally accurate to the source drawings.
- **Glider Project** (Fall 2024): Fabricated and tested gliders to optimize aerodynamic performance, achieving 101 ft glide distance and 3.9 s flight time (ranked 6th in class), through iterative flight testing and analysis of glide path, mass distribution, and wing geometry.

### CS Coursework Projects (C++)
<!-- Source: documents/projects/MP, verified by reading source directly (2026-09-12). Real, graded,
completed implementations only - excludes any unfinished/stub work found in the same drop
(mp_mosaics was left out: its KD-tree and core mapTiles function are still unimplemented
instructor stubs). -->
- **CS 128 (Introduction to Computer Science II) machine problems** (Spring 2025): six graded C++ programming assignments -
  a rule-based string-processing engine (Hawaiian word pronunciation, character classification via `std::set`);
  a simulated forensic DNA-profiling tool (`std::map`-backed database parsing, substring-repeat-count matching algorithm against a suspect database);
  a 2D-grid pathfinding visualizer (greedy least-elevation-change traversal over terrain data, PPM image output);
  a content-aware image resizer (seam-carving: energy computation and seam removal over 2D pixel arrays);
  a linked-list-based DNA strand model (splice/insert/remove operations on a custom `Node` structure);
  and a small database engine from scratch (manual memory management, Rule-of-Three copy/assignment/destructor semantics, `std::map`-indexed row storage, operator overloading).
- **CS 225 (Data Structures) machine problems** (Spring 2025, graded coursework completed before withdrawing partway through the course):
  implemented a doubly linked list with iterator support and a from-scratch merge sort via list-splitting (`mp_lists`);
  and a layered image-compositing engine with alpha blending and dynamic canvas resizing using raw pointers and manual layer management (`mp_stickers`).

## Technical Skills

### Programming & Engineering Software
- **Python** (proficient): NumPy, pandas, matplotlib, simulation/Monte Carlo methods
- **C++** (proficient): embedded firmware (Teensy/Arduino), closed-loop control
- **Java, JavaScript** (coursework-level)
- **CAD:** Siemens NX (incl. NXOpen scripting), Fusion 360
- **Simulation/Analysis:** Ansys Fluent (CFD), XFLR5, OpenRocket
- **Electronics/PCB:** KiCad, Eagle PCB

### Domain Expertise
- Aerospace systems: propulsion, aerodynamics, structures, P&ID system architecture
- Embedded controls: PID control loops, sensor fusion (IMU/complementary filter), telemetry logging and analysis
- Manufacturing and fabrication: composite layups (fiberglass/epoxy), CNC/laser cutting, FDM 3D printing and print-parameter tuning for structural parts
- Data structures & general C++ programming (CS 128/225 coursework): linked lists, custom memory management (Rule-of-Three), hash-map-backed lookups, 2D-array/grid algorithms, greedy pathfinding, operator overloading - *no formal Data Structures & Algorithms course completed yet; DSA enrollment planned for a future semester*

### Software & Tools
Siemens NX, Fusion 360, Ansys Fluent, XFLR5, OpenRocket, KiCad, Eagle PCB, Excel
Shop tools: spot welder, belt sander, laser cutter, CNC plasma cutter, table saw, drill press, band saw
Materials: epoxy resin, fiberglass, sheet metal, aluminum, plywood

## Publications
None yet.

## Awards
None recorded yet.

## References
None recorded yet - add before an application requires them.
