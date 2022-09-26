import os
import pickle
import argparse
from getpass import getpass
from csr.csr import CsrCluster
from csr.utils import get_color_text, clear_shell


def main(args, config):
    from csr import CsrCluster
    from prettytable import PrettyTable
    from csr.ssh_tunel import ssh_tunel

    username = config['username']
    passwd = config['passwd']
    clusters = config['cluster']
    clients = [CsrCluster(username, passwd, cluster) for cluster in clusters]

    jobs_info = []
    for client in clients:
        info = client.get_jobs_info()
        for i in info:
            i.update({'client': client})
        jobs_info += info

    host_table = PrettyTable(['ID', 'Cluster', 'Job Name', 'Status'])
    for i, job in enumerate(jobs_info):
        host_table.add_row([i, job['description']['virtualGroup'], job['name'],
                            get_color_text(job['state'])])
    clear_shell()
    print(host_table)
    connect_to_id = int(input('Input host id: '))

    while 0 <= connect_to_id < len(jobs_info):
        client = jobs_info[connect_to_id]['client']
        private_key_file_path = client.download_job_private_key(
            jobs_info[connect_to_id]['name'])
        host, port = client.get_job_host_port(jobs_info[connect_to_id]['name'])

        clear_shell()
        ssh_tunel(private_key_file_path, host, port)
        clear_shell()
        print(host_table)
        connect_to_id = int(input('Input host id: '))

def init(args, config):
    username = input("username: ")
    passwd = getpass("password: ")
    cluster = input("cluster[2080ti,v100]:")
    if not cluster:
        cluster = "2080ti,v100"

    cluster = cluster.split(',')

    with open(os.path.join(os.environ['HOME'], '.csr_config'), 'wb') as f:
        pickle.dump(dict(
            username=username,
            passwd=passwd,
            cluster=cluster), f)

def download(args, config):
    assert ':' in args.filename, 'filename should input as cluster:filename (e.g. v100:test.zip).'
    cluster, filename = args.filename.split(':')
    client = CsrCluster(config['username'], config['passwd'], cluster)
    client.get_nfs_file(filename)

def cmd():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=main)
    subparser = parser.add_subparsers()

    init_parser = subparser.add_parser('init')
    init_parser.set_defaults(func=init)

    download_parser = subparser.add_parser('download')
    download_parser.set_defaults(func=download)
    download_parser.add_argument('filename', type=str)
    
    args = parser.parse_args()
    if args.func != init:
        with open(os.path.join(os.environ['HOME'], '.csr_config'), 'rb') as f:
            config = pickle.load(f)
    else:
        config = None
    args.func(args, config)
