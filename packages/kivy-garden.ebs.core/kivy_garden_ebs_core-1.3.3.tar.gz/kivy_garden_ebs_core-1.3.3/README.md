Core Widgets for EBS Kivy GUIs and Widgets
==========================================

[![Github Build Status](https://github.com/chintal/ebs-widgetset-kivy/workflows/Garden%20flower/badge.svg)](https://github.com/chintal/ebs-widgetset-kivy/actions)

This library provides a collection of reusable widgets and pure python 
widget-infrastructure. These are used internally by the EBS GUI stack. 
Most things here are trivially reusable and easily replicated in kv 
directly. 

It is unlikely you'd ever want to use this library directly. In most 
cases, it would be simpler to just use this library as a collection of 
examples and reimplement elements as needed.

I'm just parcelling it out into its own package for convenience and to 
be able to publish other more complex widgets. Other EBS kivy widgets 
assume that this library is available, and when they do, the dependency 
will be explicit in the other widget's setup.py.

See https://kivy-garden.github.io/flower/ for the rendered flower docs.

Please see the garden [instructions](https://kivy-garden.github.io) for 
how to use kivy garden flowers.


Why Pure Python
---------------

EBS widgets are generally designed to be used in a context that has a 
twisted reactor, and need to interact with existing twisted codebases. 
kv can certainly do the job in most (if not all) cases, but I find it 
more comfortable having everything in python. 

Doing this does have its drawbacks : 

  - It results in much more verbose code.
  - It is entirely possible it is slower than kv (I have not checked)
  - Getting good examples is harder, and the chorus of 'Use kv instead' 
  is unavoidable.

It does have (mostly subjective) advantages too, though :

  - Not having to think in kv, especially when the gui is only a small 
  part of a much larger application and a lot of the gui is dynamically 
  generated.
  - Explicit is better than implicit. Being able to easily look through
  the bindings has made tracking down strange behaviors easier.  
  

Library Contents
----------------

The core widget infrastructure provided by this library includes:

  - Colors :
    - Color Manipulation Utilities
      - color_set_alpha
      - Gradient
    - GuiPalette class
    - BackgroundColorMixin and its many derivatives:
      - ColorBoxLayout
      - RoundedColorBoxLayout
      - other color primitives to be added as needed
  - Labels : 
    - WrappingLabel
    - ColorLabel
    - SelfScalingLabel
    - SelfScalingColorLabel
  - Images :
    - SizeProofImage
    - BleedImage
  - Buttons : 
    - BleedImageButton
    - RoundedBleedImageButton
  - Animations : 
    - CompositeAnimationManager
    

Derived EBS Kivy Widgets 
------------------------

Published Derived Widgets

  - [MarqueeLabel](https://github.com/ebs-universe/kivy_garden.ebs.marquee)
  - [CefBrowser](https://github.com/ebs-universe/kivy_garden.ebs.cefkivy)
  - [Clocks](https://github.com/ebs-universe/kivy_garden.ebs.clocks)
    - SimpleDigitalClock
  - [ImageGallery](https://github.com/ebs-universe/kivy_garden.ebs.gallery)
  - [PDFPlayer](https://github.com/ebs-universe/kivy_garden.ebs.pdfplayer)

Unrelated other widgets (no kivy_garden.ebs dependency)

  - [ProgressSpinner](https://github.com/ebs-universe/kivy_garden.ebs.progressspinner)

CI
--

Every push or pull request run the [GitHub Action](https://github.com/kivy-garden/flower/actions) CI.
It tests the code on various OS and also generates wheels that can be released on PyPI upon a
tag. Docs are also generated and uploaded to the repo as well as artifacts of the CI.


TODO
-------

* add your code

Contributing
--------------

Check out our [contribution guide](CONTRIBUTING.md) and feel free to improve the flower.

License
---------

This software is released under the terms of the MIT License.
Please see the [LICENSE.txt](LICENSE.txt) file.

How to release
===============

See the garden [instructions](https://kivy-garden.github.io/#makingareleaseforyourflower) for how to make a new release.
