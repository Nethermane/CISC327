import glob
import os
import sys
import tempfile

import backend
import frontend


# simulates 3 separate sessions for 1 day
def main(number_of_sessions=3):
    for i in range(number_of_sessions):  # run the front end instance 3 times with appropriate inputs
        # prepare program parameters
        sys.argv = [
            'frontend.py',
            'valid_accounts.txt',
            'new_transactions/transaction_' + str(i) + '.txt']
        frontend.main()
    temp_fd, temp_file = tempfile.mkstemp()
    merged_transaction_file = temp_file
    transaction_files = glob.glob("new_transactions/*.txt")  # list of transaction summary files
    with open(merged_transaction_file, 'w') as wf:  # create merged txn summary file
        for file in transaction_files:
            with open(file, 'r') as tf:
                for line in tf:
                    if line != 'EOS 0000000 000 0000000 ***':
                        wf.write(line)
        wf.write('EOS 0000000 000 0000000 ***')
    for transaction in transaction_files:
        os.remove(transaction)
    # run backend with updated files
    sys.argv = [
        'backend.py',
        'master_accounts.txt',
        merged_transaction_file]
    backend.main()
    os.close(temp_fd)
    os.remove(temp_file)


if __name__ == "__main__":
    main()
