import setuptools

with open('README.md', 'r') as f:
    readme = ''.join(f.readlines())

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name='jwt_flask_ext',
    version='0.0.2',
    install_requires=required,
    author='Eteil Junior Djoumatchoua',
    description=""" Provide an  easy way to handle authentication
    (login with jwt generated, token required decorator)
    in flask applications""",
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=['jwt_flask_ext']
)
