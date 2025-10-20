QuantFinance Documentation
==========================

.. image:: https://img.shields.io/pypi/v/quantfinance.svg
   :target: https://pypi.org/project/quantfinance/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/quantfinance.svg
   :target: https://pypi.org/project/quantfinance/
   :alt: Python versions

.. image:: https://img.shields.io/github/license/votre-username/quantfinance.svg
   :target: https://github.com/votre-username/quantfinance/blob/main/LICENSE
   :alt: License

.. image:: https://github.com/votre-username/quantfinance/workflows/CI/badge.svg
   :target: https://github.com/votre-username/quantfinance/actions
   :alt: Build status

Bienvenue dans la documentation de **QuantFinance** !

QuantFinance est un package Python complet pour la finance quantitative, offrant des outils pour :

* 📊 **Pricing d'instruments financiers** : Options, obligations, dérivés
* 📉 **Gestion des risques** : VaR, CVaR, métriques de performance
* 📈 **Optimisation de portefeuille** : Markowitz, Risk Parity, Black-Litterman
* 🔄 **Backtesting** : Test de stratégies de trading
* 📐 **Analyse quantitative** : Outils mathématiques et statistiques

Installation
------------

Installation via pip :

.. code-block:: bash

   pip install quantfinance

Installation depuis les sources :

.. code-block:: bash

   git clone https://github.com/votre-username/quantfinance.git
   cd quantfinance
   pip install -e .

Démarrage rapide
----------------

Pricing d'une option
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from quantfinance.pricing.options import BlackScholes

   # Créer une option call
   option = BlackScholes(
       S=100,      # Prix spot
       K=105,      # Strike
       T=1,        # Maturité (années)
       r=0.05,     # Taux sans risque
       sigma=0.25, # Volatilité
       option_type='call'
   )

   # Calculer le prix et les grecques
   print(f"Prix: {option.price():.2f}")
   print(f"Delta: {option.delta():.4f}")
   print(f"Gamma: {option.gamma():.6f}")

Optimisation de portefeuille
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from quantfinance.portfolio.optimization import PortfolioOptimizer
   import pandas as pd

   # Charger les rendements
   returns = pd.read_csv('returns.csv', index_col=0)

   # Optimiser
   optimizer = PortfolioOptimizer(returns, risk_free_rate=0.02)
   max_sharpe = optimizer.maximize_sharpe()

   print(f"Rendement: {max_sharpe['return']:.2%}")
   print(f"Volatilité: {max_sharpe['volatility']:.2%}")
   print(f"Sharpe: {max_sharpe['sharpe_ratio']:.3f}")

Calcul de VaR
~~~~~~~~~~~~~

.. code-block:: python

   from quantfinance.risk.var import VaRCalculator

   # VaR historique
   var_95 = VaRCalculator.historical_var(returns, confidence_level=0.95)
   print(f"VaR 95%: {var_95:.2%}")

   # Expected Shortfall
   es_95 = VaRCalculator.expected_shortfall(returns, confidence_level=0.95)
   print(f"CVaR 95%: {es_95:.2%}")

Table des matières
------------------

.. toctree::
   :maxdepth: 2
   :caption: Guide utilisateur

   user_guide/installation
   user_guide/quickstart
   user_guide/tutorials
   user_guide/examples

.. toctree::
   :maxdepth: 2
   :caption: Référence API

   api/pricing
   api/risk
   api/portfolio
   api/utils

.. toctree::
   :maxdepth: 2
   :caption: Développement

   development/contributing
   development/testing
   development/architecture
   development/changelog

.. toctree::
   :maxdepth: 1
   :caption: Liens

   GitHub <https://github.com/votre-username/quantfinance>
   PyPI <https://pypi.org/project/quantfinance/>
   Issues <https://github.com/votre-username/quantfinance/issues>

Indices et tables
-----------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`