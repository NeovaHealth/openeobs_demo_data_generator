import sys
import unittest
import argparse
from smoke_test import SmokeTest

PARSER = argparse.ArgumentParser('Run smoke tests for Open-eObs')
PARSER.add_argument('database', type=str,
                    help='Database to run tests against',
                    default='nhclinical')
PARSER.add_argument('--server', type=str,
                    help='Server to run tests against',
                    default='http://localhost:8069')
PARSER.add_argument('--user', type=str,
                    help='User to run tests as',
                    default='admin')
PARSER.add_argument('--password', type=str,
                    help='Password for testing user', default='admin')


def main():
    args = PARSER.parse_args()
    SmokeTest.SERVER = args.server
    SmokeTest.DATABASE = args.database
    SmokeTest.USER = 'adt'
    SmokeTest.PASSWORD = 'adt'

    suite = unittest.TestLoader().loadTestsFromTestCase(SmokeTest)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    sys.exit(main())
