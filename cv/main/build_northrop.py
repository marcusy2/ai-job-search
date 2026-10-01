"""Build the Northrop Grumman CVs from main_example.tex.

Only the Relevant Coursework line and the Organizational and Technical Experience
section are replaced; everything else is copied byte-for-byte from the master.
"""
import re
from pathlib import Path

HERE = Path(__file__).parent
master = (HERE / "main_example.tex").read_text(encoding="utf-8")

EXP_START = master.index(r"\section{Organizational and Technical Experience}")
EXP_END = master.index("% ===========================================================================\n%  TECHNICAL SKILLS")
CW = re.search(r"\\textbf\{Relevant Coursework:\} [^\n]*", master)


def build(name, coursework, experience):
    out = master[:EXP_START] + experience.strip() + "\n\n" + master[EXP_END:]
    out = out.replace(CW.group(0), r"\textbf{Relevant Coursework:} " + coursework, 1)
    (HERE / f"main_northropgrumman_{name}.tex").write_text(out, encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Hardware Mechanical Engineer Intern - Rolling Meadows IL (R10252778)
# ---------------------------------------------------------------------------
build("hardware_mechanical_engineer_intern",
      "Aerospace Structures, Engineering Materials, Thermodynamics, Electrical and Electronic Circuits, Aerospace Control Systems, Incompressible Flow, Statics, Dynamics",
      r"""
\section{Organizational and Technical Experience}

\erow{\textbf{TVC Rocket} (Siemens NX, Additive Manufacturing, C++)}{Summer 2026}
\begin{itemize}
  \item Designed a 2-axis TVC gimbal, avionics bay, and recovery system in Siemens NX and fabricated the structures by FDM additive manufacturing in PETG and PLA.
  \item Packaged a Teensy 4.1 flight computer, IMU sensor, and servo actuators into the 3D-printed avionics bay and integrated them into a commercial rocket body.
  \item Traced a servo linkage resolution bottleneck in the TVC gimbal by characterizing the mechanical actuation ratio, then redesigned the control path to reach sub-degree pointing precision.
  \item Engineered a closed-loop PID flight-control system in C++ on a Teensy 4.1 microcontroller, fusing IMU data to steer the TVC gimbal in real time.
  \item Bench tested the PID control system against a live IMU feed to confirm gimbal response before static fire.
  \item Diagnosed two static fire test failures on the TVC gimbal by analyzing telemetry logs and frame-by-frame video, isolating a misreferenced attitude axis and inverted control loop signs.
\end{itemize}
\entrygap

\erow{\textbf{Liquid Rocketry at Illinois}}{Spring 2025 - Present}
\begin{itemize}
  \item Modeled P\&ID system architecture in Siemens NX and installed components into the pressurant tank assembly by sourcing, importing, and constraining CAD hardware to satisfy spatial constraints.
  \item Assessed pressurant tank options, produced mechanical integration models (CAD) and verified fit against vehicle structural constraints and P\&ID.
  \item Engineered a KiCad PCB radio transmitter (USB-C + MCU) prototype enabling ground-test telemetry links.
  \item Created CAD geometries for canard-grid fin configurations and ran ANSYS Fluent CFD cases to quantify aerodynamic interactions across 0--20° deflection.
\end{itemize}
\entrygap

\erow{\textbf{CAD Project} (Siemens NX)}{Spring 2025}
\begin{itemize}
  \item Recreated a full McDonnell F-101 Voodoo in Siemens NX by extracting and scaling geometric dimensions from multi-view engineering drawings to accurately reconstruct fuselage, wing, and tail geometry.
  \item Incorporated articulated ailerons using parametric assemblies and constraints to render realistic aircraft deflection.
\end{itemize}
""")

# ---------------------------------------------------------------------------
# 2. Systems Engineer Intern - Rolling Meadows IL (R10252497)
# ---------------------------------------------------------------------------
build("systems_engineer_intern",
      "Aerospace Control Systems, Electrical and Electronic Circuits, Linear Algebra, Discrete Structures, Intro to Computer Science II, Dynamics, Aerospace Structures, Thermodynamics",
      r"""
\section{Organizational and Technical Experience}

\erow{\textbf{TVC Rocket} (Python, C++, Embedded Systems)}{Summer 2026}
\begin{itemize}
  \item Integrated a Teensy 4.1 flight computer, IMU, and servo actuators with a 2-axis TVC gimbal, avionics bay, and recovery system on a commercial rocket body.
  \item Engineered a closed-loop PID flight-control system in C++ on a Teensy 4.1 microcontroller, fusing IMU data to steer the gimbal in real time.
  \item Built a Python 6-DOF flight simulation and ran Monte Carlo sensitivity sweeps of sensor noise, motor burn variance, and wind across hundreds of trials to validate the control algorithm.
  \item Found from the sweep data that landing performance was far more sensitive to IMU accelerometer bias than servo speed, redirecting effort toward sensor calibration.
  \item Ran hardware-in-the-loop integration testing of the PID firmware against a live IMU feed to verify gimbal servo response before static fire.
  \item Root-caused two static fire test failures by analyzing telemetry logs and frame-by-frame video, isolating a misreferenced attitude axis and an inverted control loop sign.
  \item Logged onboard telemetry at 83 Hz with zero dropouts across two test campaigns (15,728 and 12,611 samples).
\end{itemize}
\entrygap

\erow{\textbf{Liquid Rocketry at Illinois}}{Spring 2025 - Present}
\begin{itemize}
  \item Modeled P\&ID system architecture in Siemens NX and integrated components into the pressurant tank assembly, sourcing and constraining CAD hardware to spatial requirements.
  \item Assessed pressurant tank options, produced mechanical integration models (CAD) and verified fit against vehicle structural constraints and P\&ID.
  \item Engineered a KiCad PCB radio transmitter (USB-C + MCU) prototype enabling ground-test telemetry links.
  \item Created CAD geometries for canard-grid fin configurations and ran ANSYS Fluent CFD cases to quantify aerodynamic interactions across 0--20° deflection.
\end{itemize}
\entrygap

\erow{\textbf{Model Rocket Project} (Siemens NX, OpenRocket)}{Fall 2024}
\begin{itemize}
  \item Designed custom fin geometry in Siemens NX and fabricated a physical prototype to hit a target apogee.
  \item Validated performance against OpenRocket simulations; flight reached 430 ft apogee with 25 ft downrange drift.
\end{itemize}
""")

# ---------------------------------------------------------------------------
# 3. Guidance Navigation and Control Intern - Dulles VA (R10250744)
# ---------------------------------------------------------------------------
build("gnc_intern",
      "Aerospace Control Systems, Dynamics, Linear Algebra, Incompressible Flow, Thermodynamics, Electrical and Electronic Circuits, Aerospace Structures, Intro to Computer Science II",
      r"""
\section{Organizational and Technical Experience}

\erow{\textbf{TVC Rocket} (C++, Embedded Systems, Python)}{Summer 2026}
\begin{itemize}
  \item Implemented a closed-loop PID attitude control loop in C++ on a Teensy 4.1, fusing IMU data with a complementary filter to steer a 2-axis TVC gimbal in real time.
  \item Built a Python 6-DOF flight simulation and ran Monte Carlo sweeps of IMU noise, motor burn variance, and crosswind across hundreds of trials to validate a landing-burn control law.
  \item Found from the sweep data that landing performance was far more sensitive to IMU accelerometer bias than servo speed, redirecting effort toward sensor calibration.
  \item Ran hardware-in-the-loop bench tests of the PID firmware against a live IMU feed, confirming correct gimbal servo response in real time before static fire.
  \item Root-caused two static fire failures from telemetry and video: an \texttt{atan2} axis-convention bug corrupting the attitude estimate and an inverted control sign.
  \item Traced a servo linkage resolution bottleneck in the TVC gimbal by characterizing the mechanical actuation ratio, then redesigned the control path to reach sub-degree pointing precision.
  \item Logged onboard telemetry at 83 Hz with zero dropouts across two test campaigns (15,728 and 12,611 samples).
\end{itemize}
\entrygap

\erow{\textbf{Liquid Rocketry at Illinois}}{Spring 2025 - Present}
\begin{itemize}
  \item Created CAD geometries for canard-grid fin configurations and ran ANSYS Fluent CFD cases to quantify aerodynamic interactions across 0--20° deflection.
  \item Engineered a KiCad PCB radio transmitter (USB-C + MCU) prototype enabling ground-test telemetry links.
  \item Modeled P\&ID system architecture in Siemens NX and integrated components into the pressurant tank assembly, sourcing and constraining CAD hardware to spatial requirements.
  \item Assessed pressurant tank options, produced mechanical integration models (CAD) and verified fit against vehicle structural constraints and P\&ID.
\end{itemize}
\entrygap

\erow{\textbf{Model Rocket Project} (Siemens NX, OpenRocket)}{Fall 2024}
\begin{itemize}
  \item Designed custom fin geometry in Siemens NX and fabricated a physical prototype to hit a target apogee.
  \item Validated performance against OpenRocket simulations; flight reached 430 ft apogee with 25 ft downrange drift.
\end{itemize}
""")

# ---------------------------------------------------------------------------
# 4/5. Engineering Intern (Evergreen) - Melbourne FL (R10253720) / Hollywood MD
#      Identical posting text apart from location, so identical content.
# ---------------------------------------------------------------------------
EVERGREEN = r"""
\section{Organizational and Technical Experience}

\erow{\textbf{TVC Rocket} (3d Printing, C++, Python)}{Summer 2026}
\begin{itemize}
  \item Designed and fabricated a 2-axis TVC gimbal, avionics bay, and recovery system by integrating a Teensy 4.1 flight computer, IMU, and servo actuators into a commercial rocket body.
  \item Bench tested the PID control system against a live IMU feed to confirm gimbal response before static fire.
  \item Traced a servo linkage resolution bottleneck in the TVC gimbal by characterizing the mechanical actuation ratio, then redesigned the control path to reach sub-degree pointing precision.
  \item Diagnosed two static fire test failures on the TVC gimbal by analyzing telemetry logs and frame-by-frame video, isolating a misreferenced attitude axis and inverted control loop signs.
  \item Logged onboard telemetry at 83 Hz with zero dropouts across two test campaigns (15,728 and 12,611 samples).
\end{itemize}
\entrygap

\erow{\textbf{Liquid Rocketry at Illinois}}{Spring 2025 - Present}
\begin{itemize}
  \item Modeled P\&ID system architecture in Siemens NX and installed components into the pressurant tank assembly by sourcing, importing, and constraining CAD hardware to satisfy spatial constraints.
  \item Engineered a KiCad PCB radio transmitter (USB-C + MCU) prototype enabling ground-test telemetry links.
  \item Assessed pressurant tank options, produced mechanical integration models (CAD) and verified fit against vehicle structural constraints and P\&ID.
\end{itemize}
\entrygap

\erow{\textbf{CAD Project} (Siemens NX)}{Spring 2025}
\begin{itemize}
  \item Recreated a full McDonnell F-101 Voodoo in Siemens NX by extracting and scaling geometric dimensions from multi-view engineering drawings to accurately reconstruct fuselage, wing, and tail geometry.
  \item Incorporated articulated ailerons using parametric assemblies and constraints to render realistic aircraft deflection.
\end{itemize}
\entrygap

\erow{\textbf{Glider Project}}{Spring 2026}
\begin{itemize}
  \item Built and tested gliders to optimize aerodynamic performance, achieving 101 ft glide distance and 3.9 s flight time, ranking 6th in class.
  \item Performed iterative flight testing and analysis of glide path, mass distribution, and wing geometry to maximize lift-to-drag performance and flight endurance.
\end{itemize}
"""
CW_EVERGREEN = "Electrical and Electronic Circuits, Engineering Materials, Aerospace Structures, Aerospace Control Systems, Thermodynamics, Incompressible Flow, Statics, Dynamics"
build("engineering_intern_melbourne", CW_EVERGREEN, EVERGREEN)
build("engineering_intern_hollywood", CW_EVERGREEN, EVERGREEN)
print("built")
