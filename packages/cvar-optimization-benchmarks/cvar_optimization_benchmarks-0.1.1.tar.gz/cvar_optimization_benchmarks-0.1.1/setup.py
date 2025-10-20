# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['src']

package_data = \
{'': ['*']}

install_requires = \
['fortitudo-tech>=1.1.11,<2.0.0', 'notebook']

setup_kwargs = {
    'name': 'cvar-optimization-benchmarks',
    'version': '0.1.1',
    'description': 'Conditional Value-at-Risk (CVaR) portfolio optimization benchmark problems in Python.',
    'long_description': "# CVaR optimization benchmark problems\nThis repository contains Conditional Value-at-Risk (CVaR) portfolio optimization benchmark\nproblems for fully general Monte Carlo distributions and derivatives portfolios.\n\nThe starting point is the [next-generation investment framework's market representation](https://youtu.be/4ESigySdGf8?si=yWYuP9te1K1RBU7j&t=46)\ngiven by the matrix $R\\in \\mathbb{R}^{S\\times I}$ and associated joint scenario probability\nvectors $p,q\\in \\mathbb{R}^{S}$.\n\nThe [1_CVaROptBenchmarks notebook](https://github.com/fortitudo-tech/cvar-optimization-benchmarks/blob/main/1_CVaROptBenchmarks.ipynb)\nillustrates how the benchmark problems can be solved using Fortitudo Technologies' Investment\nAnalysis module.\n\nThe [2_OptimizationExample notebook](https://github.com/fortitudo-tech/cvar-optimization-benchmarks/blob/main/2_OptimizationExample.ipynb)\nshows how you can replicate the results using the [fortitudo.tech open-source Python package](https://github.com/fortitudo-tech/fortitudo.tech)\nfor the efficient frontier optimizations of long-only cash portfolios, which are the easiest problems to solve.\n\n## Installation Instructions\nIt is recommended to install the code dependencies in a \n[conda environment](https://conda.io/projects/conda/en/latest/user-guide/concepts/environments.html):\n\n    conda create -n cvar-optimization-benchmarks python=3.13\n    conda activate cvar-optimization-benchmarks\n    pip install cvar-optimization-benchmarks\n\nAfter this, you should be able to run the code in the [2_OptimizationExample notebook](https://github.com/fortitudo-tech/cvar-optimization-benchmarks/blob/main/2_OptimizationExample.ipynb).\n\nThe code in [1_CVaROptBenchmarks notebook](https://github.com/fortitudo-tech/cvar-optimization-benchmarks/blob/main/1_CVaROptBenchmarks.ipynb)\ncan only be run by people who subscribe to the Investment Analysis module.\n\n## Portfolio Construction and Risk Management book\nYou can read much more about the [next-generation investment framework](https://antonvorobets.substack.com/p/anton-vorobets-next-generation-investment-framework)\nin the [Portfolio Construction and Risk Management book](https://antonvorobets.substack.com/p/pcrm-book),\nincluding a thorough description of CVaR optimization problems and\n[Resampled Portfolio Stacking](https://antonvorobets.substack.com/p/resampled-portfolio-stacking).\n",
    'author': 'Fortitudo Technologies',
    'author_email': 'software@fortitudo.tech',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://fortitudo.tech',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.14',
}


setup(**setup_kwargs)
