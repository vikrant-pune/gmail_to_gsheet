from setuptools import setup

setup(
    name='gsheet',
    version='1.0.0',
    packages=[],
    url='',
    license='',
    author='Dhanashri',
    author_email='patildhanashri910@gmail.com',
    description='',
    install_requires=['gspread==3.7.0','df2gspread==1.0.4','oauth2client==4.1.3','pandas==1.1.2'],
                      # 'google_api_python_client==2.0.2'],
#    entry_points="""['console_scripts': [ 'project=project.module:main']]"""
#     entry_points={
#         'console_scripts': [ 'code=code.module:getEmails']
#     }
    scripts = ['code/gmail_gsheet.py']

)


# from setuptools import setup
#
# setup(
#     name="click-example-colors",
#     version="1.0",
#     py_modules=["colors"],
#     include_package_data=True,
#     install_requires=["click"],
#     entry_points="""
#         [console_scripts]
#         colors=colors:cli
#     """,
# )

