from setuptools import setup, find_packages

setup(
   name='my_investments',
   version='0.1',
   packages=find_packages(),
   install_requires=[],
   author='Roberto Barbosa Costa',
   author_email='rbt.desenvolvimentos@gmail.com',
   description='Uma biblioteca para cálculos de investimentos criada no curso IA para devs da FIAP em 2025.',
   url='https://github.com/RobertoCosta33/my_investments',
   classifiers=[
       'Programming Language :: Python :: 3',
       'License :: OSI Approved :: MIT License',
       'Operating System :: OS Independent',
   ],
   python_requires='>=3.6',
)
