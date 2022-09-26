import os
from tqdm import tqdm


def clear_shell():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def get_color_text(s):
    p = '\033[1;{color}m' + s + '\033[0m'
    if s == 'STOPPED':
        s = p.format(color=31)
    elif s == 'RUNNING':
        s = p.format(color=32)
    else:
        s = p.format(color=33)
    return s

def download_file(sess, url):
    local_filename = url.split('/')[-1]
    with sess.get(url, stream=True, params={'download': True}) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            file_iter = r.iter_content(chunk_size=8192)
            for chunk in tqdm(file_iter, desc=local_filename): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return local_filename