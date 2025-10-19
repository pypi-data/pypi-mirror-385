{% extends "!autosummary/module.rst" %}

{#- Modify standard block for "modules" to include links, and avoid #}
{#- documenting ".config", that requires special handling (and another #}
{#- template). #}

{%- block modules %}
{%- if modules %}
.. rubric:: Modules

.. autosummary::
   :toctree:
   :recursive:
   :template: mednet/submodule.rst
{% for item in modules %}
   {%- if not item.startswith('config') %}
   {{ item }}
   {%- endif %}
{%- endfor %}
{% endif %}

.. include:: ../links.rst
{%- endblock %}
