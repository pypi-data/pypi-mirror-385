# grader
Automatic grading for DLAI courses. Designed to be compatible with Coursera's grading requirements.

# Requirements

To use this library you will need to have Python, Docker and [coursera-autograder](https://github.com/coursera/coursera_autograder) installed in your pc.

# Installation

You can use pip to install it!
```bash
pip install dlai_grader
```


# How to use it

## Initialize a grader

To start building your grader `cd` into the directory where you will be working and use the following command:

```bash
dlai_grader --init
```

This will ask you for:
- Name of the course (abbreviation is recommended)
- Number of the course
- Number of the week or module
- Version of the grader (defaults to 1 but can be 2 or any other number)

This will generate a file system tree like this:

```
.
└── grader (directory you invoked the command from)
    ├── data/               -> To store datasets (csv, TF Datasets, etc).
    ├── learner/            -> The learner facing version will be generated here.
    ├── solution/           -> Place solution.ipynb here
    ├── submission/         -> Necessary only in debug mode (no need to place anything here).
    ├── mount/              -> This mocks the bind mount that coursera will attach to the container. Should contain submission.ipynb or other file required for grading.
    ├── .conf               -> Configuration variables.
    ├── Dockerfile          -> Uses frolvlad/alpine-miniconda3:python3.7 as base image.
    ├── Makefile            -> Useful commands.
    ├── requirements.txt    -> Python dependencies.
    ├── entry.py            -> Entrypoint of the grader.
    └── grader.py           -> Grading logic.
```

## Placing the solution and submission

Now that you have the layout of the grader you will need to place the solution of the assignment within the `solution/` directory. **This file must be named `solution.ipynb`**.

A good starting point is to use the solution to create the first iteration of the grader. To do this place the solution within the `mount/` directory and **rename it to `submission.ipynb`**. You can use the `make submit-solution` command to do this.

Your filesystem tree should look like this:

```
.
└── grader
    ├── ... 
    ├── solution/
    │    └── solution.ipynb
    ├── mount/ 
    │    └── submission.ipynb
    └── ...
```

Note that the grader can be used to grade files other than Jupyter notebooks. If this is the case you can leave the `solution/` directory empty and place the file to grade within `mount/`. This file can be anything (`.h5, .tar.gz, .zip, etc`) the only requirement is that it should match the name of the file to submit in the coursera programming item.

# Add versioning to the notebook

## Why is this useful?

We have seen many learners facing issues when submitting their assignments because coursera does not show them the latest version. To address this, a good alternative it to always check that the submission of the learner is up to date and if not, tell them how they can upgrade to the latest version.

To ensure that a submission is compatible with a particular version of the grader the versioning feature has been created.

Within the `.conf` file you will find the current version of the grader under the variable `GRADER_VERSION`.

To compare against this version the submission notebook must include a variable called `grader_version` in its metadata. To add this variable to the `submission.ipynb` file you can use the `make versioning` command (this is just a wrapper of the `dlai_grader --versioning` command). This will add the variable matching the same version as the one found in the `.conf` file.


## Upgrading the grader and notebook version

After a refactor with breaking changes to the grader it is a good idea to upgrade the version to a newer one. You can do this be using the `make upgrade` command. This will add 1 to the current version in the `.conf` file and in the notebook.

# Tagging graded cells

You might decide to filter out cells created by learners (or other ones such as the ones that train models). If you take this approach you can add a tag to each cell's metadata and then filter out the ones that don't have this tag .

If you wish to add the `graded` tag to each cell in the `submission.ipynb` notebook you can use the `make tag` command. 

# Important note for make commands

Note that the `make tag`, `make upgrade` and `make versioning` commands change only the `mount/submission.ipynb` file. 


# Adding Python dependencies

The next step is to include all the necessary Python dependencies. For this add them to the `requirements.txt` file. By default only `dlai_grader` is included.

# Building the grading

Notice that two blank Python files were created during the `init` step. These are `grader.py` and `entry.py`. It might be odd to have two separate files if ony could do the trick. 

However it is usually best to separate the grading logic from the entrypoint of the application, as the names suggest, these should be placed within `grader.py` and `entry.py`, respectively.


# Building the Docker image

Every time you make changes to any file that the grader is dependant-on, you should rebuild the Docker image used for grading. You can do this by using the `make build` command.

# Grading

To grade, simply use the `make grade` command. This will spin up the coursera-autograder tool to simulate Coursera's grading environment.

# Debugging

Some times when using this command you will be presented with a not so descriptive error by coursera-autograder such as "Problem when running command. Sorry!". This happens because this tool does not transparently exposes the errors.

When you face this error you can enter debug mode by using the `make debug` command. This will spin up a container using the image you created and configuring it in the same way as coursera-autograder would. 

Within the container you have a command line where you can test your code directly. To do this, export the partid you are currently working on as an environment variable.  `export partId=XxXx` will do the trick. And then use the entrypoint of the application by running `python entry.py`.

By doing this you can actually see the error messages that are being generated and another nice feature of this mode is that you don't need to rebuild the image, you can simply edit `grading.py` and run `python entry.py` to try out the grader.

# Building by Example

To better ilustrate how to use the library, an example will be used. The [assignment](https://github.com/https-deeplearning-ai/tensorflow-1-public/blob/main/C1/W1/assignment/C1W1_Assignment.ipynb) for the first week of the first course of the Tensorflow 1 specialization will be used.

Trimming the markdown and including the solution, the assignment looks like this:

```python
import tensorflow as tf
import numpy as np

# GRADED FUNCTION: house_model
def house_model():
    ### START CODE HERE
    
    # Define input and output tensors with the values for houses with 1 up to 6 bedrooms
    # Hint: Remember to explictly set the dtype as float
    xs = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], dtype=float)
    ys = np.array([1.0, 1.5, 2.0, 2.5, 3.0, 3.5], dtype=float)
    
    # Define your model (should be a model with 1 dense layer and 1 unit)
    model = tf.keras.Sequential([tf.keras.layers.Dense(units=1, input_shape=[1])])
    
    # Compile your model
    # Set the optimizer to Stochastic Gradient Descent
    # and use Mean Squared Error as the loss function
    model.compile(optimizer='sgd', loss='mean_squared_error') # @REPLACE model.compile(optimizer=None, loss=None)
    
    # Train your model for 1000 epochs by feeding the i/o tensors
    model.fit(xs, ys, epochs=1000) # @REPLACE model.fit(None, None, epochs=None)
    
    ### END CODE HERE
    return model

# Get your trained model
model = house_model()

new_y = 7.0
prediction = model.predict([new_y])[0]
print(prediction)
```

## Download the assignment

