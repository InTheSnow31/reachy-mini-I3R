Sound generation involves four steps:
* Pre-training an AI on a dataset
* Continuous training of the dataset with human feedback (RLHF)
* Sound prediction
* Synthesis of the generated sound

The neural network takes an emotion as input, expressed in a chosen emotional space (the final space is characterized by three metrics: positivity, explosiveness, and interrogation of the emotion to be conveyed), and outputs a sound, defined by a variable-length sequence of notes, characterized by their pitch, intensity, and duration.

/!\ All the code has to be executed in the src/ folder.

The architecture of the src folder is therefore as follows:
* __dataset/__: Creation of an emotion <--> sound dataset, including an interface for manually labeling sounds from a sound bank of non-player characters in video games. Another algorithm transforms these sounds into the same encoding as the neural network input.
    * __labelisation_interface.py__: Interface that allows you to easily evaluate or delete a sound from the “sources/” folder. Evaluated sounds are found in the “labeled/” folder.
    * __labelised_to_encoded.py__: Transforms non-player character sounds into sequences of notes in the same format as the AI model output.
* __synthesis/__: Algorithms designed to transform the sequence of notes into sound. Several attempts are made to obtain a result close to R2D2.
    * __synthesize_whistle_with_harmonics.py__: Transforms a sequence of notes and converts it into sound in .wav format. The fundamental notes are textured with harmonics to reproduce whistling. Sounds other than whistling were tried.
    *__synthesize_whistle_from_sample.py__: Another approach to generating whistling sounds, similar to VSTs. The goal is to “copy and paste” a flute sound by adjusting its frequency to the desired one.
* __RLHF_interface.py__: Interface displayed to the user so that they can give feedback on the sound played.
* SoundGenEnv.py: Reinforcement learning environment
* __pretraining.py__: Algorithm for offline pre-training of the RL's policy.
* __training.py__: Algorithm for RL's training.
* __pretraining.py__: Algorithm in order to test the generation on an input emotion.
