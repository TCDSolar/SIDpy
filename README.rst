SIDpy
-----
A Python 3 package aimed to process and archive Very Low Frequency Sudden Ionospheric Disturbance data produced by
the `Stanford SID & SolarSID Monitors <http://solar-center.stanford.edu/SID/sidmonitor/>`_. The config.py file must
contain the correct data & archive directory paths in order to function as intended. Installation & configuration
instructions alongside a "How To Guide" on the SIDpy package may be found below.

.. image:: http://img.shields.io/badge/powered%20by-SunPy-orange.svg?style=flat
    :target: http://www.sunpy.org
    :alt: Powered by SunPy Badge

.. image:: https://dev.azure.com/OHARAO/SIDpy/_apis/build/status/TCDSolar.SIDpy?repoName=TCDSolar%2FSIDpy&branchName=main
    :target: https://dev.azure.com/OHARAO/SIDpy/_build
    :alt: Build Status

.. image:: https://readthedocs.org/projects/sidpy/badge/?version=latest
    :target: https://sidpy.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Installation Guide
------------------
1. Open the chosen OS terminal (Mac/Linux/Windows).
2. The package may be installed using pip directly from GitHub using the following terminal command:
   ``pip install git+https://github.com/TCDSolar/SIDpy``
3. The package should now be installed within the current python environment. To verify ``pip show sidpy`` may be ran,
   if an exception does not occur the SIDpy package is present and the installation has been successful

Transmitter Configuration
-------------------------
1. Open the chosen OS terminal (Mac/Linux/Windows).
2. Run ``pip show sidpy``
    - Information on the local installation of the SIDpy package should be returned, including Name, Version, Summary,
      Home-page, etc...
    - If an Exception is raised the SIDpy package has not been properly installed to rectify this follow the steps
      contained within the Instillation Guide outlined above.
3. The location field specifies the directory where the local installation is held. Using your OS file explorer navigate
   to this specified directory.
4. From here open "./config/config.py".
5. The Python dict ``transmitters`` contains the currently supported transmitters. If your data
   set contains additional transmitters they must be added in the format:
   ``'{Transmitter_ID}': [{Latitude}, {Longitude}, '{Location}']``
6. Additional ``transmitters`` may be added to the dictionary depending on the data being processed.

Quickstart
----------

This guide will show how to configure, plot and archive basic Very Low Frequency Sudden Ionospheric Disturbance data
produced by the
`Stanford SID & SolarSID Monitors <http://solar-center.stanford.edu/SID/sidmonitor/>`_.

To install please follow the above installation guide. Once installed correctly, SIDpy may be imported into any standard
Python3 script.

.. code-block:: python

    import sidpy.run as sid

Example data may be obtained from the Dublin Institute for Advanced Studies at ``https://vlf.ap.dias.ie/data`` using the
following code snippet,

.. code-block:: python

    import pandas as pd
    import requests
    from pathlib import Path

    url = 'https://vlf.ap.dias.ie/data/dunsink/super_sid/2021/04/22/csv/Dunsink_HWU_2021-04-22_000000.csv'
    req = requests.get(url)
    url_content = req.content

    file = 'Dunsink_HWU_2021-04-22_000000.csv'
    csv_file = open(file, 'wb')
    csv_file.write(url_content)
    csv_file.close()


Once Obtained Sidpy may then be used to plot and archive all data contained within a directory:

.. code-block:: python

   sid.process_directory([Path.cwd()], Path.cwd() / './data')

Or just a single file:

.. code-block:: python

   sid.process_file(Path(file), Path.cwd() / './data')

In both cases the data and processed pngs should be found at
``./data/dunsink/super_sid/2021/04/22/png/Dunsink_HWU_2021-04-22_000000.png``:

.. image:: https://raw.githubusercontent.com/TCDSolar/SIDpy/main/sidpy/tests/data/Dunsink_HWU_2021-04-22_000000.png
    :target: https://vlf.ap.dias.ie/data/dunsink/super_sid/2021/04/22/png/

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
