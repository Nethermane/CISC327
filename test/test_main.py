import io
import os
import sys
import tempfile
from importlib import reload

import frontend as app

path = os.path.dirname(os.path.abspath(__file__))


def test_r1_t1(capsys):
    # Test login
    helper(
        capsys=capsys,
        terminal_input=[
            'login', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Select session type (machine or agent): '],
        expected_output_transactions=[]
    )

def test_r1_t2(capsys):
    # Cannot logout in idle state
    helper(
        capsys=capsys,
        terminal_input=[
            'logout', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['In idle state, please login before use', 'Command: '],
        expected_output_transactions=[]
    )

def test_r1_t3(capsys):
    # Cannot create account in idle state
    helper(
        capsys=capsys,
        terminal_input=[
            'createacct', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['In idle state, please login before use', 'Command: '],
        expected_output_transactions=[]
    )

def test_r1_t4(capsys):
    # Cannot delete account in idle state
    helper(
        capsys=capsys,
        terminal_input=[
            'deleteacct', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['In idle state, please login before use', 'Command: '],
        expected_output_transactions=[]
    )

def test_r1_t5(capsys):
    # Cannot deposit in idle state
    helper(
        capsys=capsys,
        terminal_input=[
            'deposit', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['In idle state, please login before use', 'Command: '],
        expected_output_transactions=[]
    )

def test_r1_t6(capsys):
    # Cannot withdraw in idle state
    helper(
        capsys=capsys,
        terminal_input=[
            'withdraw', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['In idle state, please login before use', 'Command: '],
        expected_output_transactions=[]
    )
    
def test_r1_t7(capsys):
    # Cannot transfer in idle state
    helper(
        capsys=capsys,
        terminal_input=[
            'transfer', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['In idle state, please login before use', 'Command: '],
        expected_output_transactions=[]
    )

# def test_r2_t1(capsys):
#     # Verify that user can login for an atm session
#     helper(
#         capsys=capsys,
#         terminal_input=[
#             'login', 'machine', 'quit'
#         ],
#         input_valid_accounts=[],
#         expected_tail_of_terminal_output=['Successfully logged in as " machine "', 'Command: '],
#         expected_output_transactions=[]
#     )

# def test_r2_t2(capsys):
#     # Verify that user can login for an agent session
#     helper(
#         capsys=capsys,
#         terminal_input=[
#             'login', 'agent', 'quit'
#         ],
#         input_valid_accounts=[],
#         expected_tail_of_terminal_output=['Successfully logged in as " agent "'],
#         expected_output_transactions=[]
#     )

# def test_r2_t3(capsys):
#     # Verify that user cannot login for a non-existent session
#     helper(
#         capsys=capsys,
#         terminal_input=[
#             'login', 'mouahaha', 'quit'
#         ],
#         input_valid_accounts=[],
#         expected_tail_of_terminal_output=['In idle state, please login before use'],
#         expected_output_transactions=[]
#     )

def test_r3_t1(capsys):
    # No subsequent login acceted in machine mode
    helper(
        capsys=capsys,
        terminal_input=[
            'login', 'machine', 'login', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Error: already logged in', 'Command: '],
        expected_output_transactions=[]
    )

def test_r3_t2(capsys):
    # No subsequent login accepted in agent mode
    helper(
        capsys=capsys,
        terminal_input=[
            'login', 'agent', 'login', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Error: already logged in', 'Command: '],
        expected_output_transactions=[]
    )

# def test_r4_t1(capsys):
#     # Logout should only be accepted when logged in – machine 
#     helper(
#         capsys=capsys,
#         terminal_input=[
#             'login', 'machine', 'logout', 'quit'
#         ],
#         input_valid_accounts=[],
#         expected_tail_of_terminal_output=['Successfully logged out', 'Command: '],
#         expected_output_transactions=[]
#     )

# def test_r4_t2(capsys):
#     # Logout should only be accepted when logged in – agent 
#     helper(
#         capsys=capsys,
#         terminal_input=[
#             'login', 'agent', 'logout', 'quit'
#         ],
#         input_valid_accounts=[],
#         expected_tail_of_terminal_output=['Successfully logged out', 'Command: '],
#         expected_output_transactions=[]
#     )

def test_r5_t1(capsys):
    # Priviledged transaction create account should not be accepted in machine mode 
    helper(
        capsys=capsys,
        terminal_input=[
            'login', 'machine', 'createacct', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Error: agent session required for createacct command', 'Command: '],
        expected_output_transactions=[]
    )

# def test_r5_t2(capsys):
#     # Priviledged transaction create account should be accepted in agent mode 
#     helper(
#         capsys=capsys,
#         terminal_input=[
#             'login', 'agent', 'createacct', 'quit'
#         ],
#         input_valid_accounts=[],
#         expected_tail_of_terminal_output=['Successfully logged out', 'Command: '],
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

    for i in range(len(terminal_input)):
        terminal_input[i] += '\n'
    # set terminal input
    sys.stdin = io.StringIO(
        os.linesep.join(terminal_input))

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
