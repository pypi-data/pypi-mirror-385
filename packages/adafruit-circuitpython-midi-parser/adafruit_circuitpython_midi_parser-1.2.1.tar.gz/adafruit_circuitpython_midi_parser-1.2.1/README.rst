Introduction
============


.. image:: https://readthedocs.org/projects/adafruit-circuitpython-midi-parser/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/midi_parser/en/latest/
    :alt: Documentation Status


.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/adafruit/Adafruit_CircuitPython_MIDI_Parser/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_MIDI_Parser/actions
    :alt: Build Status


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

CircuitPython helper for parsing MIDI files


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-midi-parser/>`_.
To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-midi-parser

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-midi-parser

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install adafruit-circuitpython-midi-parser

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install adafruit_midi_parser

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python

    import os

    import adafruit_midi_parser

    parser = adafruit_midi_parser.MIDIParser()

    midi_file = "/song.mid"

    print("MIDI File Analyzer")
    print("=================")
    print(f"Looking for: {midi_file}")
    file_list = os.listdir("/")
    if midi_file[1:] in file_list:
        print(f"\nFound MIDI file {midi_file}")
        print("\nParsing MIDI file...")
        parser.parse(midi_file)
        print("\nMIDI File Information:")
        print("=====================")
        print(f"Format Type: {parser.format_type}")
        print(f"Number of Tracks: {parser.num_tracks}")
        print(f"Ticks per Beat: {parser.ticks_per_beat}")
        print(f"Tempo: {parser.tempo} microseconds per quarter note")
        print(f"BPM: {parser.bpm:.1f}")
        print(f"Total Events: {len(parser.events)}")
        print(f"Note Count: {parser.note_count}")
    else:
        print(f"MIDI file {midi_file} not found!")
    print("\nDone!")

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/midi_parser/en/latest/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_MIDI_Parser/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
