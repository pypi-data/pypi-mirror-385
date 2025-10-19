{% extends "mednet/module.rst" %}

{#- Re-modify extended block for "modules" to include all submodules normally, #}
{#- but also to add a include section. #}

{%- block modules %}
{%- if modules %}
.. rubric:: Modules

.. autosummary::
   :toctree:
   :recursive:
   :template: mednet/submodule.rst
{% for item in modules %}
   {{ item }}
{%- endfor %}
{% endif %}

.. include:: ../links.rst
{%- endblock %}
