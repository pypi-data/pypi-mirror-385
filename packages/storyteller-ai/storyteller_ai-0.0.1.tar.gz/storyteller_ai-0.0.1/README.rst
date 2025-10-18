===========
Storyteller
===========
.. image:: storyteller.jpg
   :width: 100%
   :alt: Storyteller - where your imagination meets state-of-the-art AI creativity
   :align: center

A storyteller project - where your imagination meets state-of-the-art AI creativity.

Concept
=======

Simply share a brief message outlining the story you envision, upload photos of characters (or even multiple images to bring diverse personas to life), and select key settings that shape tone, setting, and style. The system converts these inputs into an engaging narrative using OpenAI's LLMs while DALL-E3 generates amazing visuals - all compiled into a polished PDF that tells your own unique personalised fairytale.

Background
==========
When my first son (now 20) was little, around age of 3 and beyond, he enjoyed listening to the stories I made up for him. These stories were about his favourite things, places he wanted to go, with him being the lead character.

I told many stories over the years. Whether we were riding bikes, waiting for a bus, relaxing at home, or even as a bedtime story alternative, these moments became very special to both of us.

I love to read and I love art.

Around that time, about 15 years ago, I was considering turning my experience into a small side hobby/business where parents would request a personalised stories for their children that I would work on from both visual and narrative perspective and produce a printed book - a special gift to their beloved child, almost exactly as I described in the Concept section. However, as time went on and other responsibilities took over, I set the idea aside.

When LLM breakout happened, the first thing that came into my mind was that I actually can revisit my concept and bring it to life.

Quick start
===========
Create venv and install requirements
------------------------------------
.. code-block:: sh

    make create-venv
    make install

Run the marimo app
------------------
.. code-block:: sh

    make run

Open
----

Go to `localhost:8000/storyteller/ <http://localhost:8000/storyteller/>`_


Presentation
============
See the `presentation.rst`.

Build
-----
.. code-block:: sh

    make revealjs

Serve
-----
.. code-block:: sh

    make serve-docs

Open
----

Go to `localhost:5001/revealjs/ <http://localhost:5001/revealjs/>`_
