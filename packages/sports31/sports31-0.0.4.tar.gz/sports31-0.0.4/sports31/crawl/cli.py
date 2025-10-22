import click
from sports31.crawl.login import getToken
from sports31.crawl.crawler import get_configdict, crawl


@click.command()
@click.option("-a", "--account", help="account", type=click.STRING)
@click.option("-p", "--password", help="password", type=click.STRING)
@click.option("-t", "--token", help="token", type=click.STRING, default=None)
@click.option("-d", "--directory", help="directory", type=click.STRING, default=None)
@click.option("-f", "--filetype", help="file type", type=click.INT, default=4)
def cli(account, password, token, directory, filetype):
    if token is None:
        token = getToken(account, password)
    configdict = get_configdict(token)
    if directory is None:
        directory = "./"
    crawl(configdict, directory, filetype)


if __name__ == "__main__":
    cli()
