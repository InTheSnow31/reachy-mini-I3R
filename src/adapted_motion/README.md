# Code Organization of the Adapted Motion Approach 🗂️

_**Author:** Amandine GARCIA_

In the following sections, Approach #1 for generating an expressive behavior on Reachy Mini will be presented.  
This approach focuses on **adapting a functional movement** (such as YES/NO) based on emotional parameters.  
It follows the methodology described in the [report](../../docs/report/README.md) and adjusts the robot’s motion according to the PAD coordinates corresponding to a selected emotion.

The approach is organized into clearly separated modules.
You can jump directly to each part:

- [Main Files ⚡](#main-files-)
  - [`adapt.py` 🏁](#adaptpy-)
  - [`timestep.py` ⏳](#timesteppy-)
- [Folders 📂](#folders-)
  - [`prompts/` 💬](#prompts-)
  - [`normalisation_PAD/` 📏](#normalisation_pad-)
  - [`antennas_params/` 🐜](#antennas_params-)
  - [`head_params/` 🧍‍♂️](#head_params-)
  - [`brouillons/` 📝](#brouillons-)
  - [`__pycache__/` ⚡](#__pycache__)
---
## Main Files ⚡

### `adapt.py` 🏁

This is the **main entry point** of this approach.

It:
- Selects the motion type (YES / NO) ✅/❌
- Select PAD values and motion duration ⏱️
- Applies adapted motion parameters 🎛️
- Executes movements on the robot 🤖

**Execution flow:**
1. Reachy first moves to the **head/antenna center position** in 1 second using the `goto_target` function ⏩.  
2. Then, the oscillatory movement is played by repeatedly calling `set_target` at each **timestep** for the specified duration ⏳.  
3. At the end, Reachy **remains in the emotional posture** reflecting PAD values, unless he is manually interrupted, but **no longer performs the functional motion**.

> **Note:** No parameter calculation is implemented in this file; it only orchestrates the sequence of motions.

---

### `timestep.py` ⏳

This file manages **discrete time control**.

It is used to:
- Control motion duration  
- Ensure temporal consistency  
- Synchronize movements across components  

The timestep is **dynamically computed from arousal**: it modulates the *overall speed* of the movement (high arousal → faster updates ⚡, low arousal → slower ones 🐢).

This design ensures that motion speed is **emotion-dependent**, producing movements that are more energetic in a coherent and physically plausible way, rather than relying on a fixed or arbitrary time step.

---

### Folders 📂
Each folder corresponds to a specific responsibility.  
This structure avoids coupling and improves maintainability.

---

### `prompts/` 💬

This folder contains **high-level prompts**.

It is used to:
- Retrieve motion type (YES/NO) ✅/❌
- Retrieve emotional information (PAD) 🧠
- Retrieve motion duration ⏱️

Prompts act as an interface between intention and execution.

---

### `normalisation_PAD/` 📏

This folder handles **PAD values normalization**.

Although PAD values are theoretically defined in the range `[-1, 1]`,
the actual values associated with the six basic emotions often lie
far from these bounds.

As a result:
- Variations between emotions may become too small
- Motion differences may appear weak or hardly perceptible

To address this, normalization is applied in two steps.

---

#### Step 1 — Clipping and Stretching ✂️↔️

Raw PAD values are first **clipped** to a reduced interval.

This allows:
- Increasing the relative importance of emotional variations
- Avoiding extreme or unstable values

After clipping, values are effectively **stretched** to better occupy the target range.

---

#### Step 2 — Range Normalization ⚖️

Depending on the use case, PAD values are normalized to:

- `[-1, 1]`  
  - Used when the **sign matters**
  - Typical case: *Pleasure (valence)*

- `[0, 1]`  
  - Used when only **intensity** is relevant
  - Typical case: amplitude or energy-related parameters

This choice is made explicitly for each motion parameter.

---

#### Design Choice 🎨

Normalization is centralized in a single module to:
- Ensure numerical consistency
- Avoid duplicated scaling logic
- Make PAD-to-motion mappings easier to tune

This separation also allows quick adjustments without modifying motion code.

---

### `antennas_params/` 🐜

This folder contains all parameters related to **antenna motion**.

It defines the specific behaviors of the antennas at each instant, thanks to its main function *ant_angles* which returns an angle for each antenna. 

The antennas are treated as **secondary expressive actuators**:
- They reinforce intention
- They convey affective nuances
- They do not carry the main semantic load (unlike head motion)

#### Summary of PAD Mapping for Antennas 📊

| PAD Dimension | Used For                        | Rationale                                         |
|---------------|---------------------------------|--------------------------------------------------|
| Pleasure      | Center offset 🡅/🡇           | Valence controls the vertical position of antennas |
| Arousal       | Amplitude ↕️                    | Higher arousal → larger motion amplitude        |
| Dominance     | Frequency & Micro-Modulations ⚡ | Low dominance → quick, nervous movements; high → slow, confident |

---

### `head_params/` 🧍‍♂️

The head motion is composed of two main parts: **center positioning** and **oscillatory movement**. Each is influenced by the robot’s emotional state (PAD: Pleasure, Arousal, Dominance).

#### 1️⃣ Head Center 🎯

The **head center** defines the “main” position around which the oscillations occur. Each PAD dimension affects it differently:

| PAD Dimension | Head Center Components | Effect |
|---------------|----------------------|--------|
| **Pleasure**  | Pitch (up/down) ⬆️/⬇️      | Positive pleasure → head slightly up, negative → down. Determines vertical orientation. |
| **Dominance** | Z (forward/back tilt), X (forward/back position), Yaw (slight rotation) ↔️ | Positive dominance → confident, forward tilt, neutral yaw. Negative dominance → withdrawn, backward tilt, yaw excursions. |
| **Arousal**   | Scaling factor 📈       | Amplifies how far the movement can deviate from the neutral head position. Higher arousal → more pronounced inclination. |

> **Note:** All rotations and positions are in meters (X, Z) or degrees (Yaw, Pitch) in the robot frame.

#### 2️⃣ Head Oscillation: Amplitude & Frequency 🎢

Once the center is defined, **oscillatory motion** is applied around it. The oscillations are shaped by the PAD values as follows:

| PAD Dimension | Oscillation Aspect         | Rationale |
|---------------|---------------------------|-----------|
| **Pleasure**  | Instantaneous amplitude over time ↕️ | Absolute pleasure → larger head swings at each moment (more expressive). Neutral → subtle movements. |
| **Dominance** | Temporal shaping (crescendo/decrescendo) ⬆️⬇️ | Positive dominance → crescendo (amplitude grows over time). Negative dominance → decrescendo (amplitude fades). |
| **Dominance** | Frequency & micro-modulation ⚡ | Controls “liveliness” of the oscillation. Low dominance → faster, small jittery movements. High dominance → slower, controlled swings. |
| **Arousal**   | Maximum amplitude (+ Timestep) 🏋️ | Sets the physical limit of the oscillation. Higher arousal → higher potential amplitude. |

> **Note:** Amplitude is always clamped to the robot’s physical limits (`A_phys_max`), and small smoothing functions (sin/cos) are used to make movements natural and organic.

---

### `brouillons/` 📝

This folder contains **experimental or deprecated code**.

It is intentionally kept to:
- Preserve alternative ideas
- Avoid polluting the main codebase
- Allow future reuse if needed

This code is **not used** in the final system.

---

### `__pycache__/` ⚡

This folder contains Python cache files.

- Automatically generated
- Not part of the project logic
- Can be ignored or removed safely

---