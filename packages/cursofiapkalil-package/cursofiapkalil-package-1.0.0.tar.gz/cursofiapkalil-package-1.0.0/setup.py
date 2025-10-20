from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name='cursofiapkalil-package',
    version='1.0.0',
    packages=find_packages(),
    description='Descricao da sua lib cursofiapkalil',
    author='Kali Gadben',
    author_email='kalil.gadben@gmail.com',
    url='https://github.com/tadrianonet/cursofiapkalil',  
    license='MIT',  
    long_description=long_description,
    long_description_content_type='text/markdown'
)
