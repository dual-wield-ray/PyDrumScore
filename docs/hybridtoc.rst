
.. Redirect to landing page instead of global toc.
.. Needed because the global toc is sent to when clicking on main title, logo...
.. raw:: html

      <script type="text/javascript">

         currpath = window.location.pathname + "/../../index.html"
         console.log(currpath)
         window.location.pathname = currpath
      </script>

.. toctree::
   :titlesonly:
   :caption: Main documentation

   index
   musescore
   philosophy
   contributing


.. toctree::
   :titlesonly:
   :caption: API Reference

   modindex
   genindex

.. toctree::
   :titlesonly:
   :caption: Other

   license
