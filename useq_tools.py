#!/env/bin/python
"""USEQ tools"""

import sys
import argparse


from genologics.lims import Lims

# import resources
import utilities
import epp
import daemons
import config


#Commandline utility Functions
def manage_accounts(args):
    """Create,Edit,Retrieve accounts (labs)"""
    utilities.useq_manage_accounts.run(lims, args.mode, args.csv, args.account)

def client_mail(args):
    """Send email to all specific USEQ clients, all clients belonging to an account or a single specific client."""
    utilities.useq_client_mail.run(lims, config.MAIL_SENDER, args.content, args.mode, args.attachment, args.name)

def share_run(args):
    """Encrypt and Share one or more sequencing runs"""
    utilities.useq_share_run.run(lims, args.ids)


#Clarity epp scripts
def run_status_mail(args):
    """Send run started mail"""
    epp.useq_run_status_mail.run(lims, config.MAIL_SENDER, config.MAIL_ANALYSIS, args.mode ,args.step_uri)

def modify_samplesheet(args):
    """Reverse complements the barcodes in a samplesheet"""
    epp.useq_modify_samplesheet.run(lims, args.step, args.aid, args.output_file)

def group_permissions(args):
    """Checks if a user trying to execute a LIMS step is part of the specified group(s)"""
    epp.useq_group_permissions.run(lims,args.step, args.groups)

def finance_overview(args):
    """Creates a finance overview, used for billing, for all runs in the current step"""
    epp.useq_finance_overview.run(lims, args.step, args.output_file)

def route_artifacts(args):
    """Route artifacts to the appropriate step in a workflow"""
    epp.useq_route_artifacts.run(lims, args.step, args.input)

def close_projects(args):
    """Close all projects included in the current step"""
    epp.useq_close_projects.run(lims, args.step)

#Daemon scripts
def check_nextcloud_storage(args):
    """Is intended to run as a daemon to check the space remaining on the Nextcloud storage"""
    daemons.useq_check_nextcloud_storage.run()

def manage_runs(args):
    """Script responsible for starting conversion, transfer, cleanup and archiving of sequencing runs"""
    daemons.useq_manage_runs.run(lims, args.missing_bcl, args.barcode_mismatches, args.fastq_for_index, args.short_reads)


if __name__ == "__main__":
    global lims

    # Setup lims connection
    lims = Lims(config.BASEURI, config.USERNAME, config.PASSWORD)

    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()

    #Utility parsers
    parser_utilities = subparser.add_parser('utilities',help="Utility functions: manage_accounts, client_mail, share_run")
    subparser_utilities = parser_utilities.add_subparsers()

    parser_manage_accounts = subparser_utilities.add_parser('manage_accounts', help='Create, Edit & Retrieve accounts (labs)')
    parser_manage_accounts.add_argument('-m','--mode',choices=['create','edit','retrieve'])
    parser_manage_accounts.add_argument('-c','--csv', help='Path to input or output csv file')
    parser_manage_accounts.add_argument('-a','--account', help='Account name or ID. Leave empty for mode "create"', default=None)
    parser_manage_accounts.set_defaults(func=manage_accounts)

    parser_client_mail = subparser_utilities.add_parser('client_mail', help='Send email to all specific USEQ users, all clients belonging to an account or a single specific client.')
    parser_client_mail.add_argument('-m','--mode',choices=['all','labs','accounts'])
    parser_client_mail.add_argument('-c','--content', help='Path to content file (see resources for example)', nargs='?' ,type=argparse.FileType('r'))
    parser_client_mail.add_argument('-n','--name', help='Lab or Account name(s) separated by comma. Leave empty for mode "all"')
    parser_client_mail.add_argument('-a','--attachment', help='Path to attachment file')
    parser_client_mail.set_defaults(func=client_mail)

    parser_share_run = subparser_utilities.add_parser('share_run', help='Encrypts and shares 1 or more sequencing runs to the appropriate client')
    parser_share_run.add_argument('-i', '--ids', help='One or more Project ID(s) to share, separated by comma')
    parser_share_run.set_defaults(func=share_run)

    #epp parsers
    parser_epp = subparser.add_parser('epp',help='Clarity epp functions: run_status_mail, modify_samplesheet, group_permissions, finance_overview, route_artifacts, close_projects ')
    subparser_epp = parser_epp.add_subparsers()

    parser_run_status_mail = subparser_epp.add_parser('run_status', help='Sends a status email about a run depending on the mode, mail type depends on mode')
    parser_run_status_mail.add_argument('-m', '--mode' ,choices=['run_started','run_finished'])
    parser_run_status_mail.add_argument('-s', '--step_uri', help="The URI of the step that launched this script. Needed for modes: 'run_status', 'run_finished'", default=None)
    parser_run_status_mail.set_defaults(func=run_status_mail)

    parser_modify_samplesheet = subparser_epp.add_parser('modify_samplesheet', help='This script is used to modify a samplesheet to work with either NextSeq or MiSeq/HiSeq. Currently all it does is reverse complement the barcodes when needed')
    parser_modify_samplesheet.add_argument('-s', '--step', help='Step URI', required=True)
    parser_modify_samplesheet.add_argument('-a', '--aid', help='Artifact ID', required=True)
    parser_modify_samplesheet.add_argument('-o','--output_file',  nargs='?', type=argparse.FileType('w'), default=sys.stdout, help='Output file path (default=stdout)')
    parser_modify_samplesheet.set_defaults(func=modify_samplesheet)

    parser_group_permissions = subparser_epp.add_parser('group_permissions', help='Script that checks if a user trying to execute a LIMS step is part of the specified group(s)')
    parser_group_permissions.add_argument('-s', '--step', help='Step URI', required=True)
    parser_group_permissions.add_argument('-g', '--groups', help='Groups to give permission to', required=True)
    parser_group_permissions.set_defaults(func=group_permissions)

    parser_finance_overview = subparser_epp.add_parser('finance_overview', help='Creates a finance overview for all runs included in the step')
    parser_finance_overview.add_argument('-s', '--step', help='Step URI', required=True)
    parser_finance_overview.add_argument('-o','--output_file',  nargs='?', type=argparse.FileType('w'), default=sys.stdout, help='Output file path (default=stdout)')
    parser_finance_overview.set_defaults(func=finance_overview)

    parser_route_artifacts = subparser_epp.add_parser('route_artifacts', help='Route artifacts to the next appropriate step in the workflow')
    parser_route_artifacts.add_argument('-s', '--step', help='Step URI', required=True)
    parser_route_artifacts.add_argument('-i', '--input', help='Use input artifact', default=False)
    parser_route_artifacts.set_defaults(func=route_artifacts)

    parser_close_projects = subparser_epp.add_parser('close_projects', help='Close all projects included in the specified step')
    parser_close_projects.add_argument('-s', '--step', help='Step URI', required=True)
    parser_close_projects.set_defaults(func=close_projects)

    #Daemon parsers
    parser_daemons = subparser.add_parser('daemons', help='USEQ daemon scripts: check_nextcloud_storage,manage_runs ')
    subparser_daemons = parser_daemons.add_subparsers()

    parser_check_nextcloud_storage = subparser_daemons.add_parser('check_nextcloud_storage', help='Daemon that monitors the NextCloud storage and sends a mail when the threshold has been reached.')
    parser_check_nextcloud_storage.set_defaults(func=check_nextcloud_storage)

    parser_manage_runs = subparser_daemons.add_parser('manage_runs', help='Daemon responsible for starting conversion, transfer, cleanup and archiving of sequencing runs')
    parser_manage_runs.add_argument('-m', '--missing_bcl', help='Run conversion with --ignore-missing-bcls flag', default=False)
    parser_manage_runs.add_argument('-b', '--barcode_mismatches', help='Run conversion with n mismatches allowed in index', default=1)
    parser_manage_runs.add_argument('-f', '--fastq_for_index', help='Create FastQ for index reads', default=False)
    parser_manage_runs.add_argument('-s', '--short_reads', help='Sets --minimum-trimmed-read-length and --mask-short-adapter-reads to 0 allowing short reads to pass filter', default=False)
    parser_manage_runs.set_defaults(func=manage_runs)



    args = parser.parse_args()
    # print args
    args.func(args)





#EPP Functions
