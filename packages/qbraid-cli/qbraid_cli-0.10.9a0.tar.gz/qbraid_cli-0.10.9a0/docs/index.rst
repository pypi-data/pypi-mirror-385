Documentation
==============

.. raw:: html

   <br />
   
   <h1 style="text-align: center">
      <img src="_static/logo.png" alt="qbraid logo" style="width:50px;height:50px;">
      <span> qBraid</span>
      <span style="color:#808080"> | CLI</span>
   </h1>
   <p style="text-align:center;font-style:italic;color:#808080">
      Command Line Interface for interacting with all parts of the qBraid platform.
   </p>

:Release: |version|


The **qBraid CLI** is a comprehensive command-line interface tool designed for seamless interaction with
qBraid cloud services and quantum software management tools. Initially exclusive to the qBraid Lab platform,
the CLI now supports local installations as well. This enhancement broadens access to features including:

- **Quantum Jobs**: Manage and monitor quantum jobs across 20+ QPUs and on-demand simulators available from qBraid
- **Environment Management**: Create, activate, and manage Python environments with quantum software installations
- **Device Catalog**: Browse and query quantum device capabilities and specifications
- **Cloud Storage**: Manage files in qBraid's cloud storage system
- **AI Chat Integration**: Interact with qBraid's AI chat service for quantum computing assistance
- **MCP Aggregator**: Unified Model Context Protocol server for Claude Desktop integration with automatic authentication and tool routing
- **Jupyter Integration**: Manage kernels and access CLI commands directly from notebooks using magic commands

Installation
--------------

the qBraid CLI can be intalled using `pip <https://pypi.org/project/qbraid-cli/>`_:

.. code-block:: bash

   pip install qbraid-cli

To use the qBraid CLI, login to qBraid (or create an account), launch Lab, and then open Terminal.
You can also access the CLI directly from within `Notebooks <https://docs.qbraid.com/lab/user-guide/notebooks>`_
using the ``!`` operator. See `quantum jobs example <https://github.com/qBraid/qbraid-lab-demo/blob/045c7a8fbdcae66a7e64533dd9fe0e981dc02cf4/qbraid_lab/quantum_jobs/aws_quantum_jobs.ipynb>`_.

- `Launch qBraid Lab → <https://lab.qbraid.com/>`_
- `Make an account → <https://account.qbraid.com/>`_


Quick start
------------

.. code-block:: console

   $ qbraid
   ---------------------------------
    * Welcome to the qBraid CLI! * 
   ---------------------------------

          ____            _     _  
     __ _| __ ) _ __ __ _(_) __|  | 
    / _  |  _ \|  __/ _  | |/ _   | 
   | (_| | |_) | | | (_| | | (_|  | 
    \__  |____/|_|  \__ _|_|\__ _ | 
       |_|                     


   - Use `qbraid --help` to see available commands.

   - Use `qbraid --version` to display the current version.

   Reference Docs: https://docs.qbraid.com/projects/cli/en/stable/guide/overview.html


**List environments** installed in your qBraid Lab instance using:

.. code-block:: console
   
   $ qbraid envs list
   # qbraid environments:
   #

   qsharp                         /opt/.qbraid/environments/qsharp_b54crn
   default                        /opt/.qbraid/environments/qbraid_000000
   qbraid_sdk                     /home/jovyan/.qbraid/environments/qbraid_sdk_9j9sjy
   custom_env                     /home/jovyan/.qbraid/environments/custom_env_lj3zlt

Environments with the ``jobs`` keyword listed before their path support
qBraid Quantum Jobs. To use qBraid Quantum Jobs in an environment, it must have
`Amazon Braket <https://docs.aws.amazon.com/braket/index.html>`_ installed.

By default, your qBraid terminal opens using Python (and pip) from ``/opt/conda/bin``.
Packages that are installed directly at this top-level will *not* persist between sessions.
Instead, use the qBraid CLI to **install new packages** directly into one of your listed
qBraid environments:

.. code-block:: console

   $ qbraid envs activate custom_env          # activate environment
   $ python -m pip install amazon-braket-sdk  # pip install package
   $ deactivate

Once Amazon Braket is installed in an environment, **add** and **enable quantum jobs**:

.. code-block:: console

   $ qbraid jobs enable braket      # toggle quantum jobs on
   $ qbraid jobs state              # verify quantum jobs enabled

Congrats! Every AWS job you run in this environment will now be submitted through the qBraid API,
so **no access keys are necessary**. At any time, you can switch back to using your own AWS credentials
by disabling quantum jobs:

.. code-block:: console

   $ qbraid jobs disable braket  # toggle quantum jobs off


.. toctree::
   :maxdepth: 1
   :caption: CLI API Reference
   :hidden:

   tree/qbraid
   tree/qbraid_account
   tree/qbraid_admin
   tree/qbraid_chat
   tree/qbraid_configure
   tree/qbraid_devices
   tree/qbraid_envs
   tree/qbraid_files
   tree/qbraid_jobs
   tree/qbraid_kernels
   tree/qbraid_mcp
   tree/qbraid_pip