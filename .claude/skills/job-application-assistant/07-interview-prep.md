---
framework_version: 1.0.0
---

# Interview Preparation Guide

<!-- SETUP: STAR examples are personalized by running /setup based on your actual experience -->

## STAR Format

Structure answers as: **Situation** (context), **Task** (your responsibility), **Action** (what you did), **Result** (outcome).

Keep answers to 1-2 minutes. Be specific. End with what you learned or would do differently.

## Ready-Made STAR Examples

<!-- These are populated by /setup from your actual experience. Below are templates showing the format. -->

### 1. TVC Rocket - Root-Causing the Axis-Convention Bug (Diagnostic troubleshooting)
**S:** During the first static-fire test of a solo-built, two-axis thrust-vector-control rocket, the vehicle rotated roughly 80 degrees from vertical and struck the test stand's mechanical stop; from the outside, the gimbal appeared completely inactive.
**T:** As the sole engineer on the project, needed to determine why the control system failed catastrophically despite passing bench validation before the test.
**A:** Treated it as a data problem rather than assuming a hardware fault: analyzed the attitude estimate across the burn and found it held stable within 0.12 degrees for 95 seconds before suddenly diverging (ruling out a calibration offset, which would show up from power-on); noticed the estimated roll angle swept nearly the entire mathematical output range on a vehicle that was bolted down and physically motionless; cross-validated with frame-by-frame video tracking that confirmed the airframe was still to within about 0.5 degrees. Traced the divergence to a one-line axis-convention error in the attitude estimator that fed it the wrong reference frame for this build's orientation.
**R:** Corrected the estimator, added gyro sensor fusion and boot-time bias calibration, and validated the fix on the bench (0.09 degrees standard deviation over 30 seconds) before committing a second motor to a retest.
**Use for:** "Tell me about a time you debugged a hard technical problem", "Describe a time the data proved your first assumption wrong"

### 2. TVC Rocket - Monte Carlo Analysis Overturning a Design Assumption (Analytical rigor)
**S:** While designing the same thrust-vector-control rocket, the working assumption was that faster servo actuation was the main lever for control performance.
**T:** Needed to validate that assumption before committing further engineering time and cost to actuator selection.
**A:** Built a 6-DOF-informed flight simulation in Python and ran a Monte Carlo sensitivity analysis across hundreds of randomized runs, varying IMU sensor noise, motor burn scatter, and crosswind gusts.
**R:** Found that control performance was far more sensitive to IMU accelerometer bias than to servo actuation speed - the opposite of the initial intuition - and redirected effort from faster actuators toward sensor calibration before any hardware was built.
**Use for:** "Tell me about a time analysis changed a design decision", "How do you approach a new engineering problem"

### 3. TVC Rocket - Second Failure, an Inverted Control Sign (Precision under a costly setback)
**S:** After fixing the first static-fire failure, a second static fire test still diverged immediately at ignition, following a clean 50-second pre-ignition baseline - a new, unrelated failure with no motor left to spare for a blind retry.
**T:** Diagnose the new failure mode from telemetry alone before deciding on a fix.
**A:** Analyzed servo command and attitude data and found the inner servo pinned at its travel limit for 70 of the first 71 samples while pitch error grew monotonically instead of correcting - the signature of an inverted control sign (positive feedback). Recognized this was distinct from an earlier check that had already confirmed which way the servo itself moves for a given command, because loop sign depends on how the vehicle responds to the resulting deflection, a different question entirely.
**R:** Corrected the sign convention and flagged a related actuator-resolution issue for the next design iteration.
**Use for:** "Tell me about a time you failed and what you learned", "Describe a time you had to be precise under pressure"

### 4. Landing Gear Research Lead, Flight Club Aerospace (Team leadership / cross-functional coordination)
**S:** As Landing Gear Research Lead on a student flight club aircraft build, the team needed a working two-wing aircraft with aligned structural and aerodynamic components in time for flight testing.
**T:** Responsible for fabricating wing and control-surface structures and coordinating fit-checks between the structural and aerodynamic sub-teams, plus final landing-gear recommendations.
**A:** Modeled gussets and ribs in Fusion 360, manufactured wing and control surfaces using a hot-wire cutter and circular saw, applied epoxy and fiberglass layups, and organized logistics for transporting, disassembling, and reassembling two 7-ft wings for flight testing.
**R:** Delivered landing-gear recommendations backed by structural load and cost analysis and coordinated the wing build/test cycle across teams through to flight testing.
**Use for:** "Tell me about a time you led a technical team", "Describe managing a hands-on hardware project"

<!-- Add more STAR examples as needed. Aim for 4-6 covering different competencies. -->

## Common Tough Questions

### "Why did you leave [previous company]?"
> [PREPARE YOUR ANSWER - be honest, forward-looking, no negativity about former employer]

### "You don't have [specific skill/experience]."
> [PREPARE YOUR ANSWER - acknowledge the gap, bridge to adjacent experience, show willingness to learn]

### "Where do you see yourself in 5 years?"
> [PREPARE YOUR ANSWER - show ambition aligned with the role's growth path]

### "What's your biggest weakness?"
> [PREPARE YOUR ANSWER - genuine weakness with concrete mitigation strategy]

### "Why this company specifically?"
> Customize per company. Must reference: specific projects, company values, market position, or team structure. Never give a generic answer.

## Questions You Should Ask Interviewers

### About the Role
- "What does a typical week look like in this role?"
- "What would success look like in the first 6 months?"
- "What's the biggest challenge the team is facing right now?"

### About the Team
- "How big is the team, and how do you divide work?"
- "What does the development/project lifecycle look like, from idea to production?"
- "How do you onboard new team members?"

### About Tech & Growth
- "What's your current tech stack for [relevant area]?"
- "Is there room to grow into more architectural or strategic decisions?"
- "How does the team stay current with new tools and methods?"

### About Culture (use these to prevent disappointment)
- "How would you describe the team culture?"
- "What does professional development look like here?"
- "Is there flexibility for remote/hybrid work?"
- "What's the balance between development/new projects and maintenance work?"
- "How would you describe the leadership style in this team?"
- "What do people who thrive here have in common?"

## Phone/Video Interview Tips
- Have STAR examples written out (use this file)
- Keep a glass of water nearby
- Smile when speaking (it changes your tone)
- Ask for clarification if a question is vague
- It's OK to take 5 seconds to think before answering
- End with: "Is there anything else you'd like to know about my background?"

## After the Application (Best Practice)

### Follow-Up Etiquette
- **Don't call to "stand out"** or to learn more about the role post-submission - this risks a negative impression
- If the employer specified a timeline, respect it and wait
- If no timeline was given and significant time has passed (2+ weeks), a brief call to ask about status is acceptable
- If you have genuinely new, relevant information to share, a short follow-up is fine

### Thank-You Notes
- When you receive any update (interview invitation, rejection, or status update), send a brief thank-you message
- Express appreciation for their time and the process
- Keep it short (2-3 sentences)

## Roleplay Guidelines
When the user asks for interview practice:
1. Ask which role/company to simulate
2. Start with easy warm-up questions ("Tell me about yourself")
3. Progress to role-specific technical questions
4. Include 1-2 behavioral questions using the competencies from the job posting
5. End with a tough question or curveball
6. After each answer, give brief feedback: what worked, what to sharpen
7. Suggest which STAR example would work best for each question
