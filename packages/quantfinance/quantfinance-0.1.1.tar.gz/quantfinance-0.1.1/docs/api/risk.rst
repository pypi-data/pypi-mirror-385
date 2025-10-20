Risk Module
===========

Ce module fournit des outils pour la gestion des risques.

VaR Calculator
--------------

.. autoclass:: quantfinance.risk.var.VaRCalculator
   :members:
   :undoc-members:
   :show-inheritance:

Méthodes de calcul de VaR :

* **Historique** : Basée sur les percentiles historiques
* **Paramétrique** : Assume une distribution (normale ou Student-t)
* **EWMA** : Avec volatilité pondérée exponentiellement
* **Monte Carlo** : Par simulation

Exemple :

.. code-block:: python

   from quantfinance.risk.var import VaRCalculator

   # VaR historique
   var = VaRCalculator.historical_var(returns, confidence_level=0.95)

   # Expected Shortfall
   es = VaRCalculator.expected_shortfall(returns, confidence_level=0.95)

Risk Metrics
------------

.. autoclass:: quantfinance.risk.metrics.RiskMetrics
   :members:
   :undoc-members:
   :show-inheritance:

Performance Analyzer
--------------------

.. autoclass:: quantfinance.risk.metrics.PerformanceAnalyzer
   :members:
   :undoc-members:
   :show-inheritance: