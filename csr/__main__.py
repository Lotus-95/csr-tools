import os
import pickle
import argparse
from getpass import getpass
from csr.csr import CsrCluster
from csr.utils import get_color_text, clear_shell
from csr import CsrCluster
from prettytable import PrettyTable
from csr.ssh_tunel import ssh_tunel
from sshconf import read_ssh_config

def get_jobs_info(config):
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
    
    return jobs_info

def main(args, config):
    jobs_info = get_jobs_info(config)

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

def quota(args, config):
    cluster = args.cluster
    client = CsrCluster(config['username'], config['passwd'], cluster)
    quota_info = client.get_quota()[0]

    from prettytable import PrettyTable
    table = PrettyTable(['Item', 'Info'])
    table.add_row(['Jobs', quota_info['activeJobs']])
    table.add_row(['CPU', quota_info['cpuUsed'] + '/' + quota_info['cpuTotal']])
    table.add_row(['GPU', quota_info['gpuUsed'][0]['number'] + '/' + quota_info['gpuTotal'][0]['number']])
    table.add_row(['Memory', quota_info['memoryUsed'] + '/' + quota_info['memoryTotal']])
    table.add_row(['Storage', quota_info['storageUsed'] + '/' + quota_info['storageTotal']])
    print(table)

def delete(args, config):
    cluster, job_name = args.job_name.split(':')
    client = CsrCluster(config['username'], config['passwd'], cluster)

    print(client.delete_job(job_name))

def update_config(args, config):
    jobs_info = get_jobs_info(config)
    c = read_ssh_config(os.path.expanduser("~/.ssh/config"))
    for host in c.hosts():
        if host.startswith('CSR-'):
            c.remove(host)

    for job in jobs_info:
        client = job['client']
        job_name = job['name']
        client_name = job['description']['virtualGroup']
        private_key_file_path = client.download_job_private_key(
            job_name)
        host, port = client.get_job_host_port(job_name)

        if job['state'] == 'RUNNING':
            c.add(f'CSR-{client_name}-{job_name}', Hostname=host,
                                                   Port=port,
                                                   User='root',
                                                   IdentityFile=private_key_file_path)
        c.save()


def cmd():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=main)
    subparser = parser.add_subparsers()

    init_parser = subparser.add_parser('init')
    init_parser.set_defaults(func=init)

    download_parser = subparser.add_parser('download')
    download_parser.set_defaults(func=download)
    download_parser.add_argument('filename', type=str)
    
    quota_parser = subparser.add_parser('quota')
    quota_parser.set_defaults(func=quota)
    quota_parser.add_argument('cluster', type=str)

    delete_parser = subparser.add_parser('delete')
    delete_parser.set_defaults(func=delete)
    delete_parser.add_argument('job_name', type=str)

    update_config_parser = subparser.add_parser('update-config')
    update_config_parser.set_defaults(func=update_config)

    args = parser.parse_args()

    if args.func != init:
        with open(os.path.join(os.environ['HOME'], '.csr_config'), 'rb') as f:
            config = pickle.load(f)
    else:
        config = None
    args.func(args, config)
