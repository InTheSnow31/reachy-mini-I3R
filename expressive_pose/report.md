# Expressive Movements Creation

_Anaelle Jaffré_

A methodology has been put in place to bring expressive movements to the robot Reachy Mini. This document is an explanation of the different steps of this methodology.

The whole scripts are available on the following Github repo : [InTheSnow31/reachy-mini-I3R](https://github.com/InTheSnow31/reachy-mini-I3R). The experiments made throughout this report are available in the "expressive-pose" folder of the branch I created, named "anaelle".

## Table of Contents
- [Expressive Movements Creation](#expressive-movements-creation)
  - [Table of Contents](#table-of-contents)
  - [Objective Description](#objective-description)
  - [Robot Configuration Space](#robot-configuration-space)
    - [Definition of Parameters](#definition-of-parameters)
    - [Feasibility Problem](#feasibility-problem)
    - [Empirical Exploration of Limits](#empirical-exploration-of-limits)
      - [Methodology](#methodology)
      - [Results](#results)
    - [Statistical Analysis of Dependencies](#statistical-analysis-of-dependencies)
      - [Variable Correlation Analysis](#variable-correlation-analysis)
      - [Results](#results-1)
    - [Implementation of Rules in the Robot Configuration Space](#implementation-of-rules-in-the-robot-configuration-space)
      - [Definition of Rules](#definition-of-rules)
        - [The gain $a$ (slope)](#the-gain-a-slope)
        - [The offset $b$ (intercept)](#the-offset-b-intercept)
        - [The standard deviation $sigma$ (tolerance)](#the-standard-deviation-sigma-tolerance)
      - [Limit Values Extraction Script](#limit-values-extraction-script)
        - [Results](#results-2)
      - [Discussion on Variables](#discussion-on-variables)
    - [Final Pose](#final-pose)
  - [Emotional Space](#emotional-space)
  - [General Algorithm](#general-algorithm)
    - [User choice](#user-choice)
    - [PAD correspondance](#pad-correspondance)
    - [Pose generation from PAD](#pose-generation-from-pad)
    - [Execution](#execution)
  - [From Emotion to Pose](#from-emotion-to-pose)
  - [Experiment Results Analysis](#experiment-results-analysis)

## Objective Description

The aim of the final algorithm is to take an input command, through the form of an emotional state, and to render an execution of an expressive movement, corresponding to this emotional state.

The global structure of the algorithm should correspond to the following steps:

1. **Emotional state input.** For instance, `("happy", 2)` could rely to a happy state executed for 2 seconds.
2. **Emotional space fitting coordinates finding**. An algorithm should take the emotional state and timing order as input, and return the coordinates of the corresponding point into the emotional space.

   For instance, if "happy" does have corrdinates into this space, then it will directly find the coordinates.

   **Note :** for a more complex order, such as "clumsy", the algorithm should be able to find the right point after being trained on a large set of emotional states.

3. **Robot configuration space fitting coordinates finding**. An algorithm should take the emotional state coordinates as input, and return an adapted pose that is executable by the robot.

   For instance, a "happy" emotional state as input could mean wide movements for the robot, of short timing.

   **Notes :**

   - The poses made by the robot should be executable in real life, and should not cause any bug.

   - In order not to generate always the same pose on a specific point, a randomness factor can be added, influencing the direction of the movement for instance.

4. **Timing verification**. If the generated pose takes less time than the order, then another pose should be generated.

To build the general algorithm, the robot configuration space and emotional space should first be generated. Their programmation will be descripted throughout the following paragraphs.

## Robot Configuration Space

The robot configuration space is the one that will generate the outputs, and should then be operational in a first place, to make the appropriate tests. Hence, this is the first thing that is being programmed.

### Definition of Parameters

The robot configuration space is defined by the following parameters : 
1. ``head`` (4x4 matrice)
2. ``antennas`` (1D vector)
3. ``duration`` (float)
4. ``method`` ("linear", "minjerk", "ease", "cartoon")
5. ``body_yaw`` (float)

The duration parameter will be defined by the input, but the 4 other parameters can be influenced by the emotional state. An important thing to take into account is the formation of the head matrice. It can be created by the `create_head_pose()` command, which takes as input these parameters:
1. ``x``: float = 0,
2. ``y``: float = 0,
3. ``z``: float = 0,
4. ``roll``: float = 0,
5. ``pitch``: float = 0,
6. ``yaw``: float = 0,
7. ``mm``: bool = False,
8. ``degrees``: bool = True

For this experiment, the parameters ``mm`` and ``degrees`` will be let as default.

### Feasibility Problem

The aim of this first part is to find limitations for each of the possible variables. Some poses are theoretically possible to execute, but convey to an error if they are physically executed by the robot. The `method` parameter only has 4 possible values, but the other ones have an infinity of possibilities. Hence, to begin, we aim to obtain an output of this form : 

```
def pose():
    return {
        "x": int(-40, 40),
        "y": int(-60, 60),
        "z": int(-60, 60),
        "roll": int(-50, 50),
        "pitch": int(-50, 50),
        "yaw": int(-65, 65),
        "body_yaw": int(-20, 20),
        "antennas": [
            rfloat_1(0.0, 3.16),
            rfloat_1(0.0, 3.16),
        ],
    }
```

However, these values are not always reachable without generating a bug. They represent the current limits of the robot movements, but are inacurate. In order to generate an executable pose, they must be defined by realistic values. For this, a set of rules can be defined.

### Empirical Exploration of Limits 

No anlytical model of the physical constraints of the robot was found. Hence, a data-driven approach was adopted.

In order to extract coherent values for the limits of the robot poses, a dataset have been created by hand. The dataset creation is available in the [`robot_space_limit_testing.py`](robot_config_space/robot_space_limit_testing.py) script.

#### Methodology

The script generates a set of random poses for the robot. The evaluator has to label it as 1 if OK, and 0 if non-OK, into the terminal. The number of randomly generated poses can be changed. Once the script has generated the given number of poses and the evaluator has labelled them, a .json file is generated, containing the poses parameters values and their label.

#### Results

The final dataset can be found under the name [`pose_dataset_2.json`](robot_config_space/pose_datasets/pose_dataset_2.json).

**Note :** There is also a dataset named [`pose_dataset_1.json`](robot_config_space/pose_datasets/pose_dataset_1.json), but it is now obsolete due to structural change into the analysis scripts. However, it can be used. Only the analysis scripts need to be adapted.

### Statistical Analysis of Dependencies

Some variables are highly correlated with others, and knowing this will help defining limitation rules. For instance, when the robot has the head rather down, then it cannot really rotate it from backwards to forwards.

To be able to see which variables are intrinsically correlated, a **Principal Component Analysis (PCA)**. This can be done with the Python library `sklearn.decomposition`, from which the `PCA` module can be imported.

#### Variable Correlation Analysis

The [`correlation_analysis.py`](robot_config_space/correlation_analysis.py) script browses a given dataset to make a PCA on the data. It collects the **features** in a vector $X$ containing the following columns:

- x
- y
- z
- roll
- pitch
- yaw
- body_yaw
- ant1 (first antenna)
- ant2 (second antenna)

Then, these variables are standardized, by the following formula:

$X = \frac{X - \mu}{\sigma}$,

with $\mu$ the mean $X$ of the dataset and $\sigma$ the standard deviation. After this, the PCA can be exectued with the line `X = pca.fit_transform(X)`. This allows to project $X$ onto the computed components. Here, `pca` is an instance of the object `PCA`, which has some attributes line the components and variables, and to which are associated some methods, as `fit_transform`.

Finally, the components can be extracted from the object, and shown onto the correlation circle.

**NB:** Two dimensions have been used to represent data, for clarity.

#### Results

The correlation circle obtained from the dataset is the following one:
![Correlation circle](images/correlation_circle.png "Correlation circle")

It can be observed that $pitch$ is highly correlated with $z$, $roll$ with $y$ and $x$ with $yaw$ and $body$ $yaw$.

The antenas do not seem to be correlated with $z$, nor with $x$, due to the angle that is close to 90°. At least, $ant1$ with $x$, and $ant2$ with $yaw$, knowing that $x$ and $yaw$ are highly correlated. However, they do seem to be inversely correlated with $roll$. If we observe the impact of $roll$ which is correlated to $y$ on Reachy Mini, here is what we get:

|                              Classic                              |                        Impact of $roll$                         |                       Impact of $y$                       |
| :---------------------------------------------------------------: | :-------------------------------------------------------------: | :-------------------------------------------------------: |
| ![Reachy Mini simulation in the neutral pose](images/neutral.png) | ![Reachy Mini simulation while roll is active](images/roll.png) | ![Reachy Mini simulation while y is active](images/y.png) |

It can be confirmed that these variable do influence if the antennas will go through the body of the robot or not, however, so do the other ones, mostly $pitch$ and $yaw$. Hence, the analysis concerning the antennas needs to be reviewed.

In the future, for more precision, it will be possible to proceed to a **multiple linear regression** to analyse the model, so that the most significant variables can be extracted in the interest of the antennas. In a first place, only the 7 other variables will be used to define space constraints.

### Implementation of Rules in the Robot Configuration Space

Based on the observed correlations, **linear dependency rules** are defined to restrict the robot configuration space to physically reachable poses.

In order to define them, it is necessary to check which position is right, which one is wrong. As shown in the correlation analysis, $pitch$ is highly correlated with $z$, $roll$ with $y$ and $x$ with $yaw$ and $body$ $yaw$.

#### Definition of Rules

Hence, 3 two-by-two dependent rules can be set. For each of these rules, 3 parameters are calculated, from each pose :

1. The gain $a$,
2. The offset $b$,
3. The standard deviation $sigma$.

Let $r$ be a rotationnal parameter such as $roll$, $pitch$ or $yaw$, and $p$ a prismatic one, such as $x$, $y$ or $z$. A rule should be of the following form:

$r = ap + b \pm sigma$

The extracted rules do not represent exact physical constraints, but rather a linear approximation of the feasible region, sufficient for pose generation purposes. Its parameters are described in the 3 following paragraphs.

##### The gain $a$ (slope)

It represents how much the first variable is influenced by the second one. For instance, for $pitch = a \times z$, it shows how much the head pitch changes when the vertical translation $z$ changes by one unit. If $a$ is really small, $z$ will not have a high influence on the pitch. On the contrary, if $a$ is high, then there is a high geometrical constraint.

##### The offset $b$ (intercept)

It represents the neutral position of the head, when the second variables is equal to 0. For instance, for $pitch = az + b$, then $b$ will be the initial point from where the head will rotate of an $a$ factor towards $z$.

##### The standard deviation $sigma$ (tolerance)

It quantifies possible variability around a neutral pose. For instance, in $pitch = az + b \pm sigma$, $sigma$ defines a tolerance band around the mean relation, within which poses are considered reachable.

This form will allow to set coherent limitation rules to the robot poses.

#### Limit Values Extraction Script

The [`rules_extraction.py`](robot_config_space/rules_extraction.py) script has been created in order to extract rules from a given dataset. If a pose is labelled as non-OK, then this position should not be reached. The script uses multiple linear regression to extract all the fitting values from the dataset, and thus proposes limit values.

##### Results
The results of the limit values are available into the [`rules_1.json`](robot_config_space/rules/rules_1.json) file. They have been computed according to the [`pose_dataset_2.json`](robot_config_space/pose_datasets/pose_dataset_2.json) dataset, and propose $a$, $b$ and $sigma$ values for each one of the 3 rules.

A second iteration have been made, with these extracted rules taken into account to create poses. The corresponding dataset is [`pose_dataset_3.json`](robot_config_space/pose_datasets/pose_dataset_3.json). It has been combined to the previous one to extract new rules, available in the [`rules_2.json`](robot_config_space/rules/rules_2.json) file.

#### Discussion on Variables

During the tests, it has been realised that not all of the variables had an important impact on the final pose. Hence, for clarity reason, at this point of the experiment, new decisions have been made : 

1. **Antennas** movement will be wider as the robot goes higher and forward.
   
2. The **`body_yaw`** parameter will not be taken into account into the rules.

### Final Pose

The final pose is materialised by a function which takes as input:

1. ``head`` (4x4 matrice)
2. ``antennas`` (1D vector)
3. ``duration`` (float)
4. ``method`` ("linear", "minjerk", "ease", "cartoon")
5. ``body_yaw`` (float)

For the head, depending on rules:
1. ``roll``,  ``pitch``, ``yaw``
2. ``x``, ``y``, ``z``

Each of these factors will have a part of randomness and of amplitude, defined by the emotional state.

Two functions to generate it are defined in the [`pose_generation.py`](robot_config_space/pose_generation.py) file. The first one, `sample_pose()`, generates a random pose according to the defined rules, of a fixed duration.

The second one, `generate_pose_from_pad(P, A, D)`, takes into account the influence of emotional parameters into the final pose, and also returns a duration accordint to it. It will be desicribed in the [From Emotion to Pose](#from-emotion-to-pose) part.

## Emotional Space

The emotional space that is used for this experiment is the PAD model, of 3 dimensions:
- Pleasure,
- Arousal,
- Dominance.

A first version of the model has been created in the [`pad.json`](emotional_space/pad.json) file. Some elementary emotions have been placed indicatively, in a first place, such as joy, sadness or anger. Their coordinates will be adjusted with the experimentation.

Each of these points correspond to parameters influencing the final robot pose. Each pose will be generated according to a random factor.

## General Algorithm

The objective of the general algorithm is to ask the user to choose an emotional state and a minimal duration, so that the robot can execute an apropriate movement.

The program associated is available in the [`main.py`](main.py) file. Its process will be described in the following paragraphs.

### User choice

At first, the program asks the user to enter:
1. An emotional state. For the first version of this project, this state can only be one of the emotions to which coordinates exist in the [`pad.json`](emotional_space/pad.json) file.
   
2. A minimal duration. During this timing, the robot will execute a certain number of poses. This sequence creates an expressive movement.

### PAD correspondance

The program browses the [`pad.json`](emotional_space/pad.json) file to look for the emotion, and collects the associated values for P, A and D.

While the minimum duration is not reached, the following steps are followed:

1. Generate the pose from the PAD,
2. Execute the pose on the robot.

### Pose generation from PAD

The program calls the `generate_pose_from_pad(P, A, D)` function, defined in the [`pose_generation.py`](robot_config_space/pose_generation.py) file. It allows to generate a pose fitting the emotional state. It is the core of the project, and will hence be described in the next part.

### Execution

The pose is executed thanks to the `reachy.goto_target()` function, described in the [Definition of Parameters](#definition-of-parameters) part. The head movement is created in a first place, thanks to previously computed pose parameters.

**Note:** it can be remarked, during the tests, that the robot takes a certain time to concatenate the poses to create the movement. This point can be enhanced in future work.

## From Emotion to Pose

Now that all of the frame is in place, the main focus of the experiment is to correctly transmit the emotional state into the robot poses. This part is ensured by the `generate_pose_from_pad(P, A, D)` function, defined in the [`pose_generation.py`](robot_config_space/pose_generation.py) file.

To this aim, the function is divided in consecutive steps which allow the final parameters to be influenced by the emotional state.

1. Prismatic centers are initialized to 0.
   
2. Prismatic positions of the head are computed according to a difference between the center and the maximum value influenced by either arousal for $x$ and $y$, either pleasure for $z$.
   
3. $roll$, $pitch$ and $yaw$ are defined according to their rule, taking the values from the [`rules_2.json`](robot_config_space/rules/rules_2.json) file. A rule has the following form: $r = ap + b \pm sigma$, with $r$ the rotoid parameter and $p$ the prismatic one, $a$ the gain, $b$ the offset and $sigma$ the standard deviation.
   
4. $roll$ and $yaw$ are influenced by the dominance factor.
   
5. The body $yaw$ is set according to the movement of the head $yaw$, and influenced by arousal.
   
6. Antennas take random values in a realistic range, and are influence by arousal and dominance. The higher their value, the lower their maximum value.
  **Note:** this "maximal" value is a trap, as 0, the minimal one, is equivalent to 3.14. Antennas values are set according to a circle tour, 3.14 being the rouded value of $pi$.
   
7. Dominance influences head $yaw$ and body $yaw$: the higher it is, the smaller they will be. Additionnally, if dominance exceeds 0.5, antennas will have a symetrical behavior: the robot is "in control".
  
8. Safety clamps are set: maximal values should not be exceeded.
   
9.  Duration is computed according to arousal: the higher the arousal value, the shorter the duration value.
    
10. Method is set to ``minjerk`` by default.

## Experiment Results Analysis

Here are some fatal conclusions that have been observed throughout the tests.

1. The robot takes too much **time** between each pose. A sequence does not seem natural.
   
2. For some emotional states, such as when **dominance** is high, its movements should **depend** on the previous ones. Otherwise, they do not seem correlated.
   
3. **Sound** should be added, to enhance realism.
   
4. More **emotions** or emotional states should be added to the PAD model, to create diversity.
   
5. The `body_yaw` parameter seem to **reset** at 0 for each pose, taking the previous `body_yaw` value as the default value. Hence, a solution must be found if we want the robot to turn towards the user.
   
6. The **antennas** turn into the wrong sense: when they go down, for a weak dominance for instance, they turn towards the interior, and not the exterior. It does not seem natural. Additionnally, their movement should be reviewed, as the maximal value, 3.14, is equivalent to the minimal one, 0, where antenas are set to the top.
   
7. Only $roll$ and $yaw$ are influenced by the dominance factor. Should arousal and pleasure also influence them? Should $pitch$ be influenced by any factor?
   
8. The **method** used should also depend on emotional factors. 