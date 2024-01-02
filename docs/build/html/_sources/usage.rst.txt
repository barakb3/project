Usage
=====

.. _installation:


Installation
------------

To use Project, first clone the git repository to your computer from `here <https://github.com/barakb3/project/>`_ and then run:

.. code-block:: console

   $ scripts/install.sh


Uploading thoughts
------------------

To run the server you can use the ``project.run_server(address, data_dir)`` function:

.. autofunction:: project.run_server(address, data_dir)


To upload a thought you can use the ``project.upload_thought(address, user_id, thought)`` function:

.. autofunction:: project.upload_thought(address, user_id, thought)


To run the server you can use the ``project.run_server(address, data_dir)`` function:

.. autofunction:: project.run_webserver(address, data_dir)

Every thought is represented by the ``project.Tought`` class:

.. autoclass:: project.Thought
