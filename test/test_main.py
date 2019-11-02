import io
import os
import sys
import tempfile
from importlib import reload

import frontend as app

path = os.path.dirname(os.path.abspath(__file__))


# def test_r1_t1(capsys):
#
#     helper(
#         capsys=capsys,
#         terminal_input=[
#             'login', 'quit'
#         ],
#         input_valid_accounts=[],
#         expected_tail_of_terminal_output=[app.FrontEndInstance.LOGIN_MESSAGE],
#         expected_output_transactions=[]
#     )


# def test_r17_t1(capsys):
#
#     '''
#     ATM transfers can't be greater than $10000
#     '''
#
#     helper(
#         capsys=capsys,
#         terminal_input=['login', 'machine', 'transfer', '1234567', '1000001', 'logout', 'quit'],
#         input_valid_accounts=['1234567', '1234566', '0000000'],
#         expected_tail_of_terminal_output=['Successful transaction'],
#         expected_output_transactions=['XFR 1234567 1000000 1234566 ***', 'EOS 1234567 000 0000000 ***']
#     )
#
#
# def test_r17_t2(capsys):
#
#     '''
#     Atm transfers should work for <=$10000
#     '''
#
#     helper(
#         capsys=capsys,
#         terminal_input=['login', 'machine', 'transfer', '1234567', '1234566', '1000000', 'logout', 'quit'],
#         input_valid_accounts=['1234567', '1234566', '0000000'],
#         expected_tail_of_terminal_output=['Successful transaction'],
#         expected_output_transactions=['XFR 1234567 1000000 1234566 ***', 'EOS 1234567 000 0000000 ***']
#     )
def test_r7_t1(capsys):
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'createacct', '1234567', 'q', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Error: Account number already exists',
                                          'Account Number: ',
                                          'Command: '],
        expected_output_transactions=[]
    )
def test_r8_t1(capsys):
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'createacct', '1234567', 'ab', 'q', 'quit'],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Invalid account name. Account number must be between 3 and 30 alphanumeric '
                                          'characters, not beginning or ending with a space',
                                          'Account Name: ',
                                          'Command: '],
        expected_output_transactions=[]
    )
def test_r8_t2(capsys):
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'createacct', '1234567', 'abcdefghijklmnopqrstuvwxyzabcde', 'q', 'quit'],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Invalid account name. Account number must be between 3 and 30 alphanumeric '
                                          'characters, not beginning or ending with a space',
                                          'Account Name: ',
                                          'Command: '],
        expected_output_transactions=[]
    )
def test_r8_t3(capsys):
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'createacct', '1234567', ' ab', 'q', 'quit'],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Invalid account name. Account number must be between 3 and 30 alphanumeric '
                                          'characters, not beginning or ending with a space',
                                          'Account Name: ',
                                          'Command: '],
        expected_output_transactions=[]
    )
def test_r8_t4(capsys):
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'createacct', '1234567', 'ab ', 'q', 'quit'],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Invalid account name. Account number must be between 3 and 30 alphanumeric '
                                          'characters, not beginning or ending with a space',
                                          'Account Name: ',
                                          'Command: '],
        expected_output_transactions=[]
    )
def test_r8_t5(capsys):
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'createacct', '1234567', 'abc', 'logout', 'quit'],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Command: ',
                                          'Successfully logged out',
                                          'Command: '],
        expected_output_transactions=['NEW 1234567 000 0000000 abc', 'EOS 0000000 000 0000000 ***']
    )
def test_r9_t1(capsys):
    helper(
        capsys=capsys,
        terminal_input=['login', 'machine', 'deleteacct', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Error: agent session required for deleteacct command',
                                          'Command: '],
        expected_output_transactions=[]
    )
# def test_r9_t2(capsys):
#     helper(
#         capsys=capsys,
#         terminal_input=['login', 'agent', 'deleteacct', '1234566', 'quit'],
#         input_valid_accounts=['1234567', '0000000'],
#         expected_tail_of_terminal_output=['Error: agent session required for deleteacct command',
#                                           'Command: '],
#         expected_output_transactions=[]
#     )


def helper(
        capsys,
        terminal_input,
        expected_tail_of_terminal_output,
        input_valid_accounts,
        expected_output_transactions
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

    # create a temporary file in the system to store output transactions
    temp_fd, temp_file = tempfile.mkstemp()
    transaction_summary_file = temp_file

    # create a temporary file in the system to store the valid accounts:
    temp_fd2, temp_file2 = tempfile.mkstemp()
    valid_account_list_file = temp_file2
    with open(valid_account_list_file, 'w') as wf:
        wf.write('\n'.join(input_valid_accounts))

    # prepare program parameters
    sys.argv = [
        'frontend.py',
        valid_account_list_file,
        transaction_summary_file]

    # set terminal input
    sys.stdin = io.StringIO(
        '\n'.join(terminal_input))
    # run the program
    app.main(valid_account_list_file, transaction_summary_file)

    # capture terminal output / errors
    # assuming that in this case we don't use stderr
    out, err = capsys.readouterr()

    # split terminal output in lines
    out_lines = out.splitlines()
    # compare terminal outputs at the end.`
    for i in range(1, len(expected_tail_of_terminal_output) + 1):
        index = i * -1
        assert expected_tail_of_terminal_output[index] == out_lines[index]

    # compare transactions:
    with open(transaction_summary_file, 'r') as of:
        content = of.read().splitlines()
        for ind in range(len(content)):
            assert content[ind] == expected_output_transactions[ind]

    # clean up
    os.close(temp_fd)
    os.remove(temp_file)
