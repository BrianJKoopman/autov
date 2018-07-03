Decenters
=========

Code V Decenters are used to offset a surface in X, Y, or Z as well as to tilt
the surface around the X, Y and Z axes, referred to as alpha, beta and gamma
tilts. There are several different types of decenters available. The three I
have seen used in ACTPol designs are Basic Decenters, Reverse Decenters and a
Decenter and Return.

Decenters are cumulative. For more information and figures demonstrating how
decenters combine, see the section in Chapter 8 of the Code V documentation
titled "Decentered System Philosophy" (reference in version 10.5.473).

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

Coordinate Systems Definitions
------------------------------
Decenters in X, Y, and Z are fairly self explainatory. Code V also uses tilts
in what it refers to as alpha, beta, and gamma. These are tilts around the X,
Y, and Z axes, respectively. Alpha and beta tilts are left-handed, while gamma
tilts are right handed. For more information and illustrations showing these
tilts, see Chapter 8, "Tilt and Decenter Definitions" in the Code V
documentation (reference in version 10.5.473).

AutoV's Decenter Methods
-------------------------
For decentering the entire cryostat
:meth:`autov.autoact.AutoACT.decenter_cryostat` applies a decenter to the "window
clamp" surface, which doesn't have a corresponding reverse decenter. This
should have the effect that the entire cryostat is decentered by the given
amount.

.. automodule:: autov.autoact
.. autoclass:: AutoACT
    :members: decenter_cryostat
    :noindex:
