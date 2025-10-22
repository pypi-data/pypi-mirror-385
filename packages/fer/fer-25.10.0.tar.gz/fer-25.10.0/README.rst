FER
===

Facial expression recognition.

|image|

|PyPI version| |Build Status| |Downloads|

|Open In Colab|

INSTALLATION
============

Currently FER only supports Python 3.6 onwards. It can be installed
through pip:

.. code:: bash

   $ pip install fer

This implementation requires OpenCV>=3.2 and Tensorflow>=1.7.0 installed
in the system, with bindings for Python3.

They can be installed through pip (if pip version >= 9.0.1):

.. code:: bash

   $ pip install tensorflow>=1.7 opencv-contrib-python==3.3.0.9

or compiled directly from sources
(`OpenCV3 <https://github.com/opencv/opencv/archive/3.4.0.zip>`__,
`Tensorflow <https://www.tensorflow.org/install/install_sources>`__).

Note that a tensorflow-gpu version can be used instead if a GPU device
is available on the system, which will speedup the results. It can be
installed with pip:

.. code:: bash

   $ pip install tensorflow-gpu\>=1.7.0

USAGE
=====

The following example illustrates the ease of use of this package:

.. code:: python

   from fer import FER
   import cv2

   img = cv2.imread("justin.jpg")
   detector = FER()
   detector.detect_emotions(img)

Sample output:

::

   [{'box': [277, 90, 48, 63], 'emotions': {'angry': 0.02, 'disgust': 0.0, 'fear': 0.05, 'happy': 0.16, 'neutral': 0.09, 'sad': 0.27, 'surprise': 0.41}]

Pretty print it with ``import pprint; pprint.pprint(result)``.

Just want the top emotion? Try:

.. code:: python

   emotion, score = detector.top_emotion(img) # 'happy', 0.99

MTCNN Facial Recognition
^^^^^^^^^^^^^^^^^^^^^^^^

Faces by default are detected using OpenCV's Haar Cascade classifier. To
use the more accurate MTCNN network, add the parameter:

.. code:: python

   detector = FER(mtcnn=True)

Video
^^^^^

For recognizing facial expressions in video, the ``Video`` class splits
video into frames. It can use a local Keras model (default) or Peltarion
API for the backend:

.. code:: python

   from fer import Video
   from fer import FER

   video_filename = "tests/woman2.mp4"
   video = Video(video_filename)

   # Analyze video, displaying the output
   detector = FER(mtcnn=True)
   raw_data = video.analyze(detector, display=True)
   df = video.to_pandas(raw_data)

The detector returns a list of JSON objects. Each JSON object contains
two keys: 'box' and 'emotions':

-  The bounding box is formatted as [x, y, width, height] under the key
   'box'.
-  The emotions are formatted into a JSON object with the keys 'anger',
   'disgust', 'fear', 'happy', 'sad', surprise', and 'neutral'.

Other good examples of usage can be found in the files
`example.py <example.py>`__ and `video-example.py <video-example.py>`__
located in the root of this repository.

MODEL
=====

FER bundles a Keras model.

The model is a convolutional neural network with weights saved to HDF5
file in the ``data`` folder relative to the module's path. It can be
overriden by injecting it into the ``FER()`` constructor during
instantiation with the ``emotion_model`` parameter.

LICENSE
=======

`MIT License <LICENSE>`__.

CREDIT
======

This code includes methods and package structure copied or derived from
Iván de Paz Centeno's
`implementation <https://github.com/ipazc/mtcnn/>`__ of MTCNN and
Octavio Arriaga's `facial expression recognition
repo <https://github.com/oarriaga/face_classification/>`__.

REFERENCE
---------

FER 2013 dataset curated by Pierre Luc Carrier and Aaron Courville,
described in:

"Challenges in Representation Learning: A report on three machine
learning contests," by Ian J. Goodfellow, Dumitru Erhan, Pierre Luc
Carrier, Aaron Courville, Mehdi Mirza, Ben Hamner, Will Cukierski,
Yichuan Tang, David Thaler, Dong-Hyun Lee, Yingbo Zhou, Chetan Ramaiah,
Fangxiang Feng, Ruifan Li, Xiaojie Wang, Dimitris Athanasakis, John
Shawe-Taylor, Maxim Milakov, John Park, Radu Ionescu, Marius Popescu,
Cristian Grozea, James Bergstra, Jingjing Xie, Lukasz Romaszko, Bing Xu,
Zhang Chuang, and Yoshua Bengio,
`arXiv:1307.0414 <https://arxiv.org/abs/1307.0414>`__.

.. |image| image:: https://github.com/justinshenk/fer/raw/master/result.jpg
.. |PyPI version| image:: https://badge.fury.io/py/fer.svg
   :target: https://badge.fury.io/py/fer
.. |Build Status| image:: https://travis-ci.org/justinshenk/fer.svg?branch=master
   :target: https://travis-ci.org/justinshenk/fer
.. |Downloads| image:: https://pepy.tech/badge/fer
   :target: https://pepy.tech/project/fer
.. |Open In Colab| image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: http://colab.research.google.com/github/justinshenk/fer/blob/master/fer-video-demo.ipynb
