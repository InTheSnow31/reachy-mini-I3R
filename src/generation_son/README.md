Sound generation involves four steps:
* Pre-training an AI on a dataset
* Continuous training of the dataset with human feedback (RLHF)
* Sound prediction
* Synthesis of the generated sound

The neural network takes an emotion as input, expressed in a chosen emotional space (the final space is characterized by three metrics: positivity, explosiveness, and interrogation of the emotion to be conveyed), and outputs a sound, defined by a variable-length sequence of notes, characterized by their pitch, intensity, and duration.

The architecture of the src folder is therefore as follows:
* dataset/: Creation of an emotion <--> sound dataset, including an interface for manually labeling sounds from a sound bank of non-player characters in video games. Another algorithm transforms these sounds into the same encoding as the neural network input.
* synthesis/: Algorithms designed to transform the sequence of notes into sound. Several attempts are made to obtain a result close to R2D2.
* interface_input.py: Interface displayed to the user so that they can give feedback on the sound played.
* SoundGenEnv.py: Reinforcement learning environment
* train.py: Algorithm for pre-training, training, and prediction of the neural network.
