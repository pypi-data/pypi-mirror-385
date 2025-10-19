# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deqr']

package_data = \
{'': ['*']}

extras_require = \
{'dev': ['cython==3.1.2', 'pytest>=7.0.0', 'Pillow>=8.0.0', 'numpy>=1.20.0'],
 'documentation': ['sphinx==7.4.7',
                   'sphinx-copybutton==0.5.2',
                   'furo==2024.4.27',
                   'sphinx-inline-tabs==2023.4.21']}

setup_kwargs = {
    'name': 'deqr',
    'version': '0.2.4',
    'description': 'qr code decoding library',
    'long_description': '## deqr\n\nA python library for decoding QR codes. Implemented as a cython wrapper around\ntwo different QR code decoding backends (quirc and qrdec).\n\n### Install\n\n```\npip install deqr\n```\n\n### [Documentation][documentation]\n\n[documentation]: https://torque.github.io/deqr-docs/latest-dev/\n',
    'author': 'torque',
    'author_email': 'torque@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/torque/deqr',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
