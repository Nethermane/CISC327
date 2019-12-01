import glob
import io
import os
import sys
import tempfile

import backend
import frontend


def main():
    for i in range(3):
        # prepare program parameters
        print('Front end instance', i)
        sys.argv = [
            'frontend.py',
            'valid_accounts.txt',
            'new_transactions/transaction_' + str(i) + '.txt']
        frontend.main()
    temp_fd, temp_file = tempfile.mkstemp()
    merged_transaction_file = temp_file
    transaction_files = glob.glob("new_transactions/*.txt")
    with open(merged_transaction_file, 'w') as wf:
        for file in transaction_files:
            with open(file, 'r') as tf:
                for line in tf:
                    if line != 'EOS 0000000 000 0000000 ***':
                        wf.write(line)
        wf.write('EOS 0000000 000 0000000 ***')
    for transaction in transaction_files:
        os.remove(transaction)
    with open(merged_transaction_file, 'r') as rf:
        print(rf.readlines())
    sys.argv = [
        'backend.py',
        'master_accounts.txt',
        merged_transaction_file]
    backend.main()
    os.close(temp_fd)
    os.remove(temp_file)


if __name__ == "__main__":
    main()
