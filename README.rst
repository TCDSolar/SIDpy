SIDpy
-----
Collection of Python scripts used to process and archive data from the SID and SuperSID receivers.
Designed to be run on Windows 10. Requires Anaconda3.
The scripts may be automatically run using Windows Task Scheduler. To do this, the processing_script.bat needs to be configured.

Installation
------------
1. Clone repository to a convenient location eg. Desktop.
2. Open Windows command prompt, and cd into the repo.
3. Run "pip install requirements.txt"
4. Open the supersid_config.py and change the corresponding paths to those which suit your machine. N.B. use absolute paths to ensure that windows scheduler can run the scripts.
5. Running supersid_run.py will proceed to process all files in the specified path before archiving the png along with the corresponding csv.

.. image:: http://img.shields.io/badge/powered%20by-SunPy-orange.svg?style=flat
    :target: http://www.sunpy.org
    :alt: Powered by SunPy Badge

License
-------

This project is Copyright (c) Oscar Sage David O'Hara and licensed under
the terms of the Mozilla Public License. This package is based upon
the `Openastronomy packaging guide <https://github.com/OpenAstronomy/packaging-guide>`_
which is licensed under the BSD 3-clause licence. See the licenses folder for
more information.


Contributing
------------

We love contributions! SIDpy is open source,
built on open source, and we'd love to have you hang out in our community.

**Imposter syndrome disclaimer**: We want your help. No, really.

There may be a little voice inside your head that is telling you that you're not
ready to be an open source contributor; that your skills aren't nearly good
enough to contribute. What could you possibly offer a project like this one?

We assure you - the little voice in your head is wrong. If you can write code at
all, you can contribute code to open source. Contributing to open source
projects is a fantastic way to advance one's coding skills. Writing perfect code
isn't the measure of a good developer (that would disqualify all of us!); it's
trying to create something, making mistakes, and learning from those
mistakes. That's how we all improve, and we are happy to help others learn.

Being an open source contributor doesn't just mean writing code, either. You can
help out by writing documentation, tests, or even giving feedback about the
project (and yes - that includes giving feedback about the contribution
process). Some of these contributions may be the most valuable to the project as
a whole, because you're coming to the project with fresh eyes, so you can see
the errors and assumptions that seasoned contributors have glossed over.

Note: This disclaimer was originally written by
`Adrienne Lowe <https://github.com/adriennefriend>`_ for a
`PyCon talk <https://www.youtube.com/watch?v=6Uj746j9Heo>`_, and was adapted by
supersid based on its use in the README file for the
`MetPy project <https://github.com/Unidata/MetPy>`_.
