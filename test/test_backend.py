import os
import sys
import tempfile
from importlib import reload

import backend as app

path = os.path.dirname(os.path.abspath(__file__))


def test_create_p1(capsys):
    helper(capsys,
           merged_transaction_summary=['NEW 1234567 000 0000000 nam\nEOS 0000000 000 0000000 ***'],
           master_accounts_list=[],
           expected_output_transactions=['1234567 0 nam'],
           expected_tail_of_terminal_output=[]
           )


def test_create_p2(capsys):
    helper(capsys,
           merged_transaction_summary=['NEW 1234567 000 nam nam\nEOS 0000000 000 0000000 ***'],
           master_accounts_list=['1234567 0 nam'],
           expected_output_transactions=['1234567 0 nam'],
           expected_tail_of_terminal_output=['Error: account already exists']
           )


def test_withdraw_P1(capsys):
    helper(capsys,
           merged_transaction_summary=[],
           master_accounts_list=[],
           expected_output_transactions=[],
           expected_tail_of_terminal_output=[]
           )


def test_withdraw_P2(capsys):
    helper(capsys,
           merged_transaction_summary=['WDR 0000000 1000 7654321 nam'],
           master_accounts_list=['1234567 1000 nam'],
           expected_output_transactions=['1234567 1000 nam'],
           expected_tail_of_terminal_output=[]
           )


def test_withdraw_P3(capsys):
    helper(capsys,
           merged_transaction_summary=['WDR 0000000 1000 1234567 *nam'],
           master_accounts_list=['1234567 1000 nam'],
           expected_output_transactions=['1234567 0 nam'],
           expected_tail_of_terminal_output=[]
           )


def test_withdraw_P4(capsys):
    helper(capsys,
           merged_transaction_summary=['WDR 0000000 1000 1234567 nam'],
           master_accounts_list=['1234567 100 nam'],
           expected_output_transactions=['1234567 100 nam'],
           expected_tail_of_terminal_output=["Can't withdraw more money than account has"]
           )


def helper(capsys,
           merged_transaction_summary,
           master_accounts_list,
           expected_output_transactions,
           expected_tail_of_terminal_output
           ):
    """Helper function for testing

    Arguments:
        capsys -- object created by pytest to capture stdout and stderr
        terminal_input -- list of string for terminal input
        expected_tail_of_terminal_output list of expected string at the tail of terminal
        input_valid_accounts -- list of valid accounts in the valid_account_list_file
        expected_output_transactions -- list of expected output transactions
    """

    # cleanup package
    reload(app)

    # create a temporary file in the system to store the valid accounts:
    temp_fd2, temp_file2 = tempfile.mkstemp()
    master_accounts_file = temp_file2
    with open(master_accounts_file, 'w') as wf:
        wf.write('\n'.join(master_accounts_list))
    temp_fd, temp_file = tempfile.mkstemp()
    merged_transaction_file = temp_file
    with open(merged_transaction_file, 'w') as wf:
        wf.write('\n'.join(merged_transaction_summary))

    # prepare program parameters
    sys.argv = [
        'backend.py',
        master_accounts_file,
        merged_transaction_file]
    # run the program
    app.main()

    out, err = capsys.readouterr()

    # split terminal output in lines
    out_lines = out.splitlines()
    # compare terminal outputs at the end.`
    for i in range(1, len(expected_tail_of_terminal_output) + 1):
        index = i * -1
        assert expected_tail_of_terminal_output[index] == out_lines[index]

    # compare transactions:
    with open(master_accounts_file, 'r') as of:
        content = of.read().splitlines()
        for ind in range(len(content)):
            assert content[ind] == expected_output_transactions[ind]

    # clean up
    os.close(temp_fd)
    os.remove(temp_file)
    os.close(temp_fd2)
    os.remove(temp_file2)
