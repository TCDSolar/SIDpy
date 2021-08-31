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
