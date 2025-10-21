from os import path
from setuptools import setup, find_packages


# Read the contents of the README file
directory = path.abspath(path.dirname(__file__))
with open(path.join(directory, 'README'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='quantizeml',
      version='1.0.1',
      description='Base layers and quantization tools',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Kevin Tsiknos',
      author_email='ktsiknos@brainchip.com',
      maintainer='Kevin Tsiknos',
      maintainer_email='ktsiknos@brainchip.com',
      url='https://doc.brainchipinc.com',
      license='Apache 2.0',
      license_files=['LICENSE'],
      packages=find_packages(),
      entry_points={
        'console_scripts': [
            'quantizeml = quantizeml.cli:main',
        ]
      },
      install_requires=['tf_keras~=2.19.0',
                        'onnxruntime==1.19.2', 'onnxscript~=0.4.0', 'onnx_ir<=0.1.8',
                        'onnxruntime_extensions<0.14.0',
                        'scipy'],
       extras_require={
          'test': ['pytest', 'pytest-rerunfailures', 'pytest-console-scripts',
                   'pytest-xdist', 'tensorflow_datasets', 'keras_hub'],
          'analysis': ['matplotlib', 'tensorboardX'],
      },
      python_requires='>=3.10')
