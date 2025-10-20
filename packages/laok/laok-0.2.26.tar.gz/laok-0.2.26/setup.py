from setuptools import setup, find_packages

setup(
    name='laok',
    version='0.2.26',
    keywords=['_lk', 'dump', 'run'],
    license='MIT License',
    author='Liu Kuan',
    author_email='1306743659@qq.com',
    description='laok utils library, simplify my daily programming work',
    packages=find_packages(),
    include_package_data=True,
    package_data = {"":["*.*"]}
)
