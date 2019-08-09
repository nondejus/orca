import click

from modules import orca_helpers
from modules.orca_dbconn import OrcaDbConnector

from . import CONTEXT_SETTINGS

@click.group(context_settings=CONTEXT_SETTINGS, short_help='Add/Import asset data which you would like to enumerate.')
def add():
    pass


def add_asset(orca_dbconn, asset, asset_type, source):

    click.echo(click.style("[+]", fg='green') + " Adding asset: {}".format(asset))
    if asset_type == 'ipaddr':
        if orca_helpers.is_ipaddr(asset):
            orca_dbconn.store_asset(asset, asset_type=asset_type, source=source)
    elif asset_type == 'cidr':
        if orca_helpers.is_cidr(asset):
            orca_dbconn.store_asset(asset, asset_type=asset_type, source=source)
    elif asset_type == 'hostname':
        orca_dbconn.store_asset(asset, asset_type=asset_type, source=source)
    elif asset_type == 'domain':
        orca_dbconn.store_asset(asset, asset_type=asset_type, source=source)
    else:
        click.secho("[+] No valid asset data type provided", bg='red')


@add.command('from_cli', short_help='Import asset data from the command line.')
@click.option('--ip', '-i', 'ip_', callback=orca_helpers.validate_ip, help='IP address for scanning')
@click.option('--cidr', '-c', 'cidr_', callback=orca_helpers.validate_cidr, help='IP range for scanning')
@click.option('--hostname', '-o', 'hostname', callback=orca_helpers.validate_domain, help='Hostname for scanning')
@click.option('--domain', '-d', 'domain', callback=orca_helpers.validate_domain, help='Domain for scanning')
@click.argument('project', callback=orca_helpers.validate_projectname)
def import_asset_cli(project, ip_, cidr_, hostname, domain):
    if ip_:
        add_asset(OrcaDbConnector(project), ip_, 'ipaddr', source='cli')

    if cidr_:
        add_asset(OrcaDbConnector(project), cidr_, 'cidr', source='cli')

    if hostname:
        add_asset(OrcaDbConnector(project), hostname, 'hostname', source='cli')

    if domain:
        add_asset(OrcaDbConnector(project), domain, 'domain', source='cli')

    if not (ip_ or cidr_ or hostname or domain):

        click.secho("[!] No asset data provided", bg='red')
        ctx = click.get_current_context()
        click.echo(ctx.get_help())


@add.command('from_domaintools', short_help='Import asset data from Domaintools CSV file.')
@click.option('--input_file', 'if_', prompt=True, type=click.File('r'))
@click.argument('project', callback=orca_helpers.validate_projectname)
def import_asset_domaintools(project, if_):
    orca_dbconn = OrcaDbConnector(project)

    for line in if_:
        if not 'Domain' in line:
            domain_name = line.split(',')[0]
            add_asset(orca_dbconn, domain_name, 'domain', source='domaintools')


@add.command('from_file', short_help='Import asset data from a line delimited file')
@click.option('--input_file', '-f', 'input_file', help='File path', type=click.File('r'), prompt=True)
@click.option('--type', '-t', 'type_', help='What does the file contain',
              type=click.Choice(["ip", "cidr", "hostname", "domain"]), prompt=True)
@click.argument('project', callback=orca_helpers.validate_projectname)
def import_asset_file(project, type_, input_file):
    orca_dbconn = OrcaDbConnector(project)

    if type_ == "ip":
        for line in input_file:
            ipaddr = line.rstrip('\r\n')
            if orca_helpers.is_ipaddr(ipaddr):
                add_asset(orca_dbconn, ipaddr, 'ipaddr', source='file')
    elif type_ == "cidr":
        for line in input_file:
            cidr = line.rstrip('\r\n')
            if orca_helpers.is_cidr(cidr):
                add_asset(orca_dbconn, cidr, 'cidr', source='file')
    elif type_ == "hostname":
        for line in input_file:
            add_asset(orca_dbconn, line.rstrip('\r\n'), 'hostname', source='file')
    elif type_ == "domain":
        for line in input_file:
            add_asset(orca_dbconn, line.rstrip('\r\n'), 'domain', source='file')
    else:
        click.secho("No asset data provided!", fg='red')
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
