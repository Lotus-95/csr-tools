import subprocess


def ssh_tunel(private_file_path, host, port):
    ssh_command = 'ssh -i {private_file_path} -p {port} root@{host}'
    ssh_command = ssh_command.format(private_file_path=private_file_path,
                                      host=host, port=port)
    ssh_command = ssh_command.split()
    ssh_command += ['-o', 'ProxyCommand=nc -X 5 -x localhost:1080 %h %p']
    subprocess.run(ssh_command)
    import pdb; pdb.set_trace()
