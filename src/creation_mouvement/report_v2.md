# Expressive Movements Creation

_Anaelle Jaffré_

A methodology has been put in place to bring expressive movements to the robot Reachy Mini. This document is an explanation of the different steps of this methodology.

The whole scripts are available on the following Github repo : [InTheSnow31/reachy-mini-I3R](https://github.com/InTheSnow31/reachy-mini-I3R). The experiments made throughout this report are available in the "expressive-pose" folder of the branch I created, named "anaelle".

## Traduction of Emotions in Movements

Into the [`pose_generation.py`](robot_config_space/pose_generation.py) script, there are two main functions which allow to convert emotions into movements. More precisely, they take as input 3 values: P, A and D. These are the PAD coordinates of the emotion in the PAD space, from the [`pad.json`](emotional_space/pad.json) file. P stands for Pleasure, A for Arousal and D for Dominance.

As output, they return a pose. The timing of the pose is supposed to be short enough so that within 10 seconds, the robot is able to create a sequence of approximately 3 to 10 poses.

The two main functions which allow the influence of emotions in the movement are `moving_antennas(P, A, D, t)` and `generate_pose_from_pad(P, A, D)`. This second one calls the first one, according to the generated timing of the pose.

### Pleasure $P$ influence

In the two functions, the pleasure parameter $P$ influences the following movement variables:

- $pitch$ | The pitch is the rotation of the read, in the same sense as saying "yes". If $P$ is weak, $pitch$ will go high so that the head will wind down, and inversely.

- $antennas$ | The higher the value of $P$, the upper the direction of the antennas, and inversely. Hence, if there is no pleasure at all, antennas are supposed to wind down.

### Arousal $A$ influence

Overall, the Arousal parameter $A$ has the role of an amplifier. Hence, almost all of the variables are modified by it:

- $x$ | This variable is the forward-backward translation made by the head. The more arousal there is, then the wider movements will be.

- $y$ | The same thing is done for $y$, the right-left translation of the head. At the difference that here, $A$ is squared, for more impact, as there is more free space.

- $roll$, $pitch$ and $yaw$ | All of the head rotations are amplified by an $A$ factor: the more energy there is in the emotional state, the more the robot will make wide movements.

- $body\_yaw$ | $A$ influences the $body\_yaw$ amplitude, which also depends on the head $yaw$ variable.

- $duration$ | The duration of the pose is influenced by arousal. It is longer for low Arousal, shorter for high Arousal. Hence, an emotional state with a high arousal value will have a tendency to concatenate short poses, and inversely.

- $antennas$ | 
  - Arousal distorts the base movement of the antennas.
  
  - The `non_symmetric` condition is defined thanks to $A$ and $D$. Weak dominance and a bit of arousal means confusion, which illustrates on the robot as a lack of symmetry.

  - Antennas can have a random drift, which is arousal-dependant. The higher the value of $A$, the higher can be the drift.

### Dominance $D$ influence

The Dominance parameter $D$ influences the following movement variables:

- $z$ | This variable is the up-down translation of the head. If one is very confident, which illustrates by a high value for $D$, then the head will be upper, and inversely.
  
- $yaw$ and $body\_yaw$ | If the robot is in control, then it will have a higher tendency to look forward. This is made by multiplicating $yaw$ and $body\_yaw$ by an $\frac{1}{D}$ factor, as their center is 0.

- $antennas$ |

  - As precised upper, the `non_symmetric` condition is defined thanks to $A$ and $D$.
  
  - The random drift of the antennas is also influenced by dominance. The more confident the robot should seem, the less the antennas should have random movements. Hence, here also, there is an $\frac{1}{D}$ factor.

### Randomness

To generate different poses each time, randomness must be added to the model. Here are the variables it impacts:

- $x$, $y$ and $z$ | The prismatic position of the head is generated randomly within a realistic range, which depend itself on emotional parameters.

- $roll$, $pitch$ and $yaw$ | The rotational variables depend on rules, set by experiment in the [`rules_2.json`](rules_2.json) file, wo that the robot tries not to reach unreachable position.

    These rules imply that they depend on their most correlated prismatic variable, and so on randomness. For instance, $roll$ is highly correlated with $y$; thus, it will be influenced by its new value for each pose.

    Additionally, a small random noise is being added, for more chaos.

- $body\_yaw$ | The direction of the robot in front of the user is created by a random choice in a range that depends on the head $yaw$ and $A$ values.

- $duration$ | The duration of the pose is multiplicated by a random factor, which also depends on arousal.

- $antennas$ | The drift of the antennas is a random number taken within a determined range, which depends on $A$ and $D$.





