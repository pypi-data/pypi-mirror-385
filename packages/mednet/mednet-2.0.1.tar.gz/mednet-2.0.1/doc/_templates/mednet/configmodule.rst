{% extends "!autosummary/module.rst" %}

{#- Modify modules block so that, if no submodules detected, then just dump the #}
{# contents of the current module.  Otherwise, recurse. #}

{%- block modules %}
{%- if modules %}
.. rubric:: Modules

.. autosummary::
   :toctree:
   :recursive:
   :template: mednet/configmodule.rst
{% for item in modules %}
   {{ item }}
{%- endfor %}
{%- else %}

.. literalinclude:: ../../src/{{ fullname.replace(".", "/") }}.py
{% endif %}

.. include:: ../links.rst
{%- endblock %}
