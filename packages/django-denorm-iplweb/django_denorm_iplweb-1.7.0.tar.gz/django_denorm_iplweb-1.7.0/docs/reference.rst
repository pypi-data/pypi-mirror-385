=========
Reference
=========


Decorators
==========

.. autofunction:: denorm.denormalized

.. autofunction:: denorm.depend_on_related(othermodel,foreign_key=None,type=None)

Fields
======

.. autoclass:: denorm.CacheKeyField
   :members: __init__,depend_on_related

.. autoclass:: denorm.CountField
   :members: __init__


Functions
=========

.. autofunction:: denorm.flush

Middleware
==========

.. autoclass:: denorm.middleware.DenormMiddleware


Management commands
===================

**denorm_init**
    .. automodule:: denorm.management.commands.denorm_init

**denorm_drop**
    .. automodule:: denorm.management.commands.denorm_drop

**denorm_rebuild**
    .. automodule:: denorm.management.commands.denorm_rebuild

**denorm_flush**
    .. automodule:: denorm.management.commands.denorm_flush

**denorm_queue**
    .. automodule:: denorm.management.commands.denorm_queue

**denorm_sql**
    .. automodule:: denorm.management.commands.denorm_sql
