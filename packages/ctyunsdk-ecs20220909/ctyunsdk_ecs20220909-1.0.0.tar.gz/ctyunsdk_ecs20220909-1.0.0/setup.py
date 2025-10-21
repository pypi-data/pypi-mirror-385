from setuptools import setup, find_packages

setup(
    name='ctyunsdk_ecs20220909',
    version='1.0.0',
    author='Ctyun Cloud SDK',
    author_email='ctyunsdk@chinatelecom.cn',
    packages=find_packages(exclude=['ctyunsdk_ecs20220909.tests', 'ctyunsdk_ecs20220909.tests.*']),
    python_requires='>=3.9',
    license='LICENSE.txt',
    install_requires=[
        'requests>=2.32.4'
    ],
    url='https://github.com/ctyunsdk/ctyun-python-sdk',
    project_urls={
        'Source': 'https://github.com/ctyunsdk/ctyun-python-sdk'
    }
)
