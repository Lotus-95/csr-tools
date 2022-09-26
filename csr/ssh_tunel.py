import subprocess


def ssh_tunel(private_file_path, host, port):
    ssh_command = 'ssh -i {private_file_path} -p {port} root@{host}'
    subprocess.run(ssh_command.format(private_file_path=private_file_path,
                                      host=host, port=port).split())
