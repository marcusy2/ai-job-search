"""Generate AMCA / Apex tailored CVs from the master. Locked blocks (preamble, header,
education rows, skills, leadership entries) are sliced verbatim out of main_example.tex."""
import re, sys
from pathlib import Path

MASTER = Path(r"C:\Users\marcu\ai-job-search\cv\main\main_example.tex").read_text(encoding="utf-8")
OUT = Path(__file__).parent

pre = MASTER[:MASTER.index(r"\textbf{Relevant Coursework:}")]
skills = MASTER[MASTER.index(r"\section{Technical Skills}"):MASTER.index("% ====", MASTER.index(r"\section{Technical Skills}"))].rstrip() + "\n"
lead_start = MASTER.index(r"\section{Leadership and Activities}")
aaa = MASTER[MASTER.index(r"\erow{\textbf{Asian American Association}"):MASTER.index(r"\entrygap", lead_start)].rstrip() + "\n"
fc = MASTER[MASTER.index(r"\erow{\textbf{Flight Club Aerospace}"):MASTER.rindex(r"\end{document}")].rstrip() + "\n"

def entry(title, date, bullets):
    items = "\n".join(f"  \\item {b}" for b in bullets)
    return f"\\erow{{{title}}}{{{date}}}\n\\begin{{itemize}}\n{items}\n\\end{{itemize}}\n"

def build(coursework, entries, fc_first=True):
    body = pre + r"\textbf{Relevant Coursework:} " + ", ".join(coursework) + "\n\n"
    body += "\\section{Organizational and Technical Experience}\n\n"
    body += "\\entrygap\n\n".join(entry(*e) for e in entries) + "\n"
    body += skills + "\n\\section{Leadership and Activities}\n\n"
    first, second = (fc, aaa) if fc_first else (aaa, fc)
    body += first + "\\entrygap\n\n" + second + "\n\\end{document}\n"
    return body

# ---------------------------------------------------------------- bullet pool
TVC_BUILD   = r"Designed and fabricated a 2-axis TVC gimbal, avionics bay, and recovery system by integrating a Teensy 4.1 flight computer, IMU, and servo actuators into a commercial rocket body."
TVC_PROTO   = r"Designed and prototyped a 2-axis TVC gimbal, avionics bay, and recovery system by integrating a Teensy 4.1 flight computer, IMU, and servo actuators into a commercial rocket body."
TVC_NX      = r"Designed engine mount and structural parts in Siemens NX (NXOpen/Python) and 3D printed them in PETG/PLA."
TVC_RCA     = r"Performed root cause analysis on two static fire test failures from telemetry logs and frame-by-frame video, isolating a misreferenced attitude axis and an inverted control loop sign."
TVC_DIAG    = r"Diagnosed two static fire test failures on the TVC gimbal by analyzing telemetry logs and frame-by-frame video, isolating a misreferenced attitude axis and inverted control loop signs."
TVC_LINK    = r"Traced a servo linkage resolution bottleneck in the TVC gimbal by characterizing the mechanical actuation ratio, then redesigned the control path to reach sub-degree pointing precision."
TVC_BENCH   = r"Bench tested closed loop PID control against a live IMU feed to confirm gimbal response before static fire."
TVC_MC      = r"Simulated rocket descent dynamics in Python by sweeping sensor noise, motor burn variance, and wind disturbance across hundreds of Monte Carlo trials to validate a real-time landing-burn control law."
TVC_MC_FIND = r"Ran a Python Monte Carlo sensitivity analysis across hundreds of trials, finding landing performance was more sensitive to accelerometer bias than servo speed and redirecting effort toward sensor calibration."
TVC_TLM     = r"Logged telemetry at 83 Hz with zero dropouts across two static fires (15,728 and 12,611 samples)."
TVC_FW      = r"Wrote C++ flight firmware on the Teensy 4.1, fusing MPU-6050 IMU data with a complementary filter to drive a closed-loop PID gimbal controller."
TVC_AVBAY   = r"Built a TVC rocket avionics bay integrating a Teensy 4.1 flight computer, MPU-6050 IMU, and servo actuators."
TVC_GIMBAL  = r"Designed and fabricated a 2-axis TVC gimbal and recovery system for a commercial rocket body."
TVC_SF      = r"Designed, built, and static fire tested a 2-axis TVC gimbal, avionics bay, and recovery system."

LRI_PID     = r"Modeled P\&ID system architecture in Siemens NX and integrated fluid-handling components into the pressurant tank assembly of a liquid-propulsion vehicle."
LRI_PID_IPA = r"Modeled the P\&ID system architecture of the team's IPA/LOX liquid rocket in Siemens NX and integrated components into its pressurant tank assembly."
LRI_SRC     = r"Modeled P\&ID system architecture in Siemens NX and integrated components into the pressurant tank assembly, sourcing and constraining CAD hardware to spatial requirements."
LRI_TANK    = r"Assessed pressurant tank options, produced mechanical integration models (CAD) and verified fit against vehicle structural constraints and P\&ID."
LRI_CFD     = r"Created CAD geometries for canard-grid fins and ran Ansys Fluent CFD cases across 0--20\textdegree{} deflection."
LRI_PCB     = r"Engineered a KiCad PCB radio transmitter (USB-C + MCU) prototype enabling ground-test telemetry links."

F101_1 = r"Recreated a full McDonnell F-101 Voodoo in Siemens NX by extracting and scaling geometric dimensions from multi-view engineering drawings to reconstruct fuselage, wing, and tail geometry."
F101_2 = r"Integrated articulated control surfaces (ailerons, elevators, rudder) using parametric assemblies and constraints."
MR_1 = r"Designed custom fin geometry in Siemens NX and fabricated a physical prototype to hit a target apogee."
MR_2 = r"Validated against OpenRocket simulations; flight reached 430 ft apogee with 25 ft downrange drift."
GL_1 = r"Fabricated and iteratively tested gliders, tuning mass distribution and wing geometry for lift-to-drag performance."
GL_2 = r"Achieved 101 ft glide distance and 3.9 s flight time, ranking 6th in class."
INV_1 = r"Built a solo Python/Flask research platform (4,200+ lines) running an 8-agent pipeline on four schedules."
INV_2 = r"Built a SQL database layer and dashboards that score prior predictions against realized 7-day returns."
INV_3 = r"Integrated the yfinance, NewsAPI, and Anthropic Claude APIs behind a shared base-agent class."

TVC = r"\textbf{TVC Rocket} (Independent Project)"
LRI = r"\textbf{Liquid Rocketry at Illinois} (Project Team)"
CAD = r"\textbf{CAD Project}"
MR  = r"\textbf{Model Rocket Project} (Siemens NX, OpenRocket)"
GL  = r"\textbf{Glider Project}"
INV = r"\textbf{Investment Research Automation Platform} (Independent Project)"
S26, S25P, S25, F24, S26b = "Summer 2026", "Spring 2025 - Present", "Spring 2025", "Fall 2024", "Spring 2026"

CVS = {
 "main_amca_mechanical_engineering_intern": dict(
   coursework=["Thermodynamics", "Incompressible Flow", "Aerospace Structures", "Statics", "Dynamics", "Engineering Materials", "Aerospace Control Systems", "Electrical and Electronic Circuits", "Linear Algebra"],
   entries=[(r"\textbf{TVC Rocket} (Design, Build, Test)", S26, [TVC_PROTO, TVC_NX, TVC_LINK, TVC_FW, TVC_RCA, TVC_BENCH, TVC_MC, TVC_TLM]),
            (r"\textbf{Liquid Rocketry at Illinois} (Siemens NX, Fluid Systems)", S25P, [LRI_PID, LRI_TANK, LRI_CFD, LRI_PCB]),
            (r"\textbf{CAD Project} (Siemens NX)", S25, [F101_1, F101_2])]),
 "main_amca_production_operations_intern": dict(
   coursework=["Engineering Materials", "Aerospace Structures", "Statics", "Dynamics", "Thermodynamics", "Electrical and Electronic Circuits", "Aerospace Control Systems", "Incompressible Flow", "Linear Algebra"],
   entries=[(r"\textbf{TVC Rocket} (Fabrication, 3D Printing)", S26, [TVC_BUILD, TVC_NX, TVC_RCA, TVC_LINK, TVC_BENCH, TVC_TLM, TVC_MC_FIND]),
            (r"\textbf{Liquid Rocketry at Illinois} (Siemens NX, Assembly Integration)", S25P, [LRI_SRC, LRI_TANK, LRI_PCB, LRI_CFD]),
            (MR, F24, [MR_1, MR_2]),
            (GL, S26b, [GL_1, GL_2])]),
 "main_amca_supply_chain_engineering_intern": dict(
   coursework=["Engineering Materials", "Aerospace Structures", "Statics", "Dynamics", "Thermodynamics", "Electrical and Electronic Circuits", "Aerospace Control Systems", "Linear Algebra", "Discrete Structures"],
   entries=[(r"\textbf{TVC Rocket} (Independent Project)", S26, [TVC_BUILD, TVC_RCA, TVC_LINK, TVC_NX, TVC_FW, TVC_BENCH, TVC_TLM, TVC_MC_FIND]),
            (r"\textbf{Liquid Rocketry at Illinois} (Siemens NX, Assembly Integration)", S25P, [LRI_SRC, LRI_TANK, LRI_PCB, LRI_CFD]),
            (r"\textbf{CAD Project} (Siemens NX)", S25, [F101_1, F101_2])]),
 "main_amca_business_operations_intern": dict(
   coursework=["Aerospace Structures", "Engineering Materials", "Thermodynamics", "Aerospace Control Systems", "Incompressible Flow", "Linear Algebra", "Discrete Structures", "Intro to Computer Science II"],
   entries=[(TVC, S26, [TVC_BUILD, TVC_NX, TVC_RCA, TVC_LINK, TVC_FW, TVC_BENCH, TVC_MC_FIND, TVC_TLM]),
            (r"\textbf{Liquid Rocketry at Illinois} (Project Team)", S25P, [LRI_SRC, LRI_TANK, LRI_CFD, LRI_PCB]),
            (INV, "Ongoing", [INV_1, INV_2, INV_3])],
   fc_first=False),
 "main_apex_propulsion_intern": dict(
   coursework=["Thermodynamics", "Incompressible Flow", "Aerospace Structures", "Engineering Materials", "Statics", "Dynamics", "Aerospace Control Systems", "Electrical and Electronic Circuits"],
   entries=[(r"\textbf{Liquid Rocketry at Illinois} (Fluid Systems, Siemens NX)", S25P, [LRI_PID_IPA, LRI_TANK, LRI_CFD, LRI_PCB]),
            (r"\textbf{TVC Rocket} (Static Fire Testing, Python)", S26, [TVC_SF, TVC_NX, TVC_RCA, TVC_TLM, TVC_BENCH, TVC_MC, TVC_LINK]),
            (MR, F24, [MR_1, MR_2]),
            (GL, S26b, [GL_1, GL_2])]),
 "main_apex_avionics_intern": dict(
   coursework=["Electrical and Electronic Circuits", "Aerospace Control Systems", "Linear Algebra", "Discrete Structures", "Intro to Computer Science II", "Dynamics", "Thermodynamics", "Aerospace Structures"],
   entries=[(r"\textbf{TVC Rocket} (Embedded C++, Avionics)", S26, [TVC_AVBAY, TVC_FW, TVC_BENCH, TVC_TLM, TVC_RCA, TVC_GIMBAL, TVC_NX, TVC_LINK, TVC_MC]),
            (r"\textbf{Liquid Rocketry at Illinois} (KiCad, Siemens NX)", S25P, [LRI_PCB, LRI_PID, LRI_TANK, LRI_CFD]),
            (MR, F24, [MR_1, MR_2])],
   fc_first=False),
 "main_apex_avionics_test_engineering_intern": dict(
   coursework=["Electrical and Electronic Circuits", "Aerospace Control Systems", "Intro to Computer Science II", "Discrete Structures", "Linear Algebra", "Dynamics", "Thermodynamics", "Aerospace Structures"],
   entries=[(r"\textbf{TVC Rocket} (Hardware Test, Python, C++)", S26, [TVC_AVBAY, TVC_BENCH, TVC_RCA, TVC_TLM, TVC_FW, TVC_MC_FIND, TVC_GIMBAL, TVC_NX, TVC_LINK]),
            (r"\textbf{Liquid Rocketry at Illinois} (KiCad, Siemens NX)", S25P, [LRI_PCB, LRI_PID, LRI_TANK, LRI_CFD]),
            (MR, F24, [MR_1, MR_2])],
   fc_first=False),
}

only = sys.argv[1:]
for name, cfg in CVS.items():
    if only and name not in only:
        continue
    (OUT / f"{name}.tex").write_text(build(**cfg), encoding="utf-8")
    print("wrote", name)
