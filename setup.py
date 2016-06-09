from setuptools import setup

setup(
    name='openeobs_demo_data_generator',
    version="0.1",
    description="A set of tools to assist in the generation of demo data for"
                "Open eObs",
    author="NeovaHealth",
    author_email="office@neovahealth.co.uk",
    url="https://github.com/NeovaHealth/openeobs_demo_data_generator",
    provides=["openeobs_demo_data_generator"],
    packages=[
        'demo_data_generators',
        'demo_setup_tools',
        'smoketest',
        'smoketest_production',
        'security',
        'demo_refresh_tools'],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "generate_openeobs_demo_data = demo_data_generators.__main__:main",
            "run_smoke_tests = smoketest.__main__:main",
            "run_production_smoke_tests = smoketest_production.__main__:main",
            "setup_openeobs_demo = demo_setup_tools.__main__:main",
            "change_odoo_admin_password = security.__main__:main",
            "refresh_openeobs_demo = demo_refresh_tools.__main__:main"
        ]
    },
    install_requires=[
        'ERPPeek==1.6.1',
        'argparse>=1.2.1'
    ],
    license="GPL",
    zip_safe=True,
)
