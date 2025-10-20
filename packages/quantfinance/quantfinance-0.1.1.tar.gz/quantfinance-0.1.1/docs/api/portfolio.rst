Portfolio Module
================

Ce module fournit des outils pour l'optimisation et la gestion de portefeuille.

Portfolio Optimizer
-------------------

.. autoclass:: mon_package.portfolio.optimization.PortfolioOptimizer
   :members:
   :undoc-members:
   :show-inheritance:

Méthodes d'optimisation :

* **Variance minimale** : Minimise le risque
* **Sharpe maximum** : Maximise le ratio rendement/risque
* **Risk Parity** : Égalise les contributions au risque
* **Rendement cible** : Maximise le rendement pour un risque donné

Exemple :

.. code-block:: python

   from mon_package.portfolio.optimization import PortfolioOptimizer

   optimizer = PortfolioOptimizer(returns, risk_free_rate=0.02)

   # Sharpe maximum
   max_sharpe = optimizer.maximize_sharpe()

   # Variance minimale
   min_vol = optimizer.minimize_volatility()

Efficient Frontier
------------------

.. autoclass:: mon_package.portfolio.optimization.EfficientFrontier
   :members:
   :undoc-members:
   :show-inheritance:

Asset Allocator
---------------

.. autoclass:: mon_package.portfolio.allocation.AssetAllocator
   :members:
   :undoc-members:
   :show-inheritance:

Backtester
----------

.. autoclass:: mon_package.portfolio.backtesting.Backtester
   :members:
   :undoc-members:
   :show-inheritance: