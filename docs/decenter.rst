Decenters
=========

Code V Decenters are used to offset a surface in X, Y, or Z as well as to tilt
the surface around the X, Y and Z axes, referred to as alpha, beta and gamma
tilts. There are several different types of decenters available. The three I
have seen used in ACTPol designs are Basic Decenters, Reverse Decenters and a
Decenter and Return.

Decenters are cumulative, as demonstrated here, in a figure from the Code V
documentation.

.. image:: _static/cumulative_decenter_codev.png

Basic Decenter
--------------
Basic decenters defines a new axis for current and succeeding surfaces.

Reverse Decenter
----------------
A reverse decenter applys the decenter values with opposite signs. They do this
so that the values in a basic decenter and reverse decenter can match. I'm not
sure the advantage of this, since you'll likely do a "Pickup" anyway, and you
could just have a scale of -1. However, a decenter is essentially undone once a
Basic and Reverse Decenter pair have occurred. Surfaces further down from the
reverse, are no longer decentered by the Basic Decenter amount.

Decenter and Return
-------------------
Decenters only the current surface.

AutoV's Decenter Methods
-------------------------
For decentering the entire cryostat
:meth:`modules.autov.AutoV.decenter_cryostat` applies a decenter to the "window
clamp" surface, which doesn't have a corresponding reverse decenter. This
should have the effect that the entire cryostat is decentered by the given
amount.

.. automodule:: modules.autov
.. autoclass:: AutoV
    :members: decenter_cryostat
    :noindex:
