import tempfile
from importlib import reload
import os
import io
import sys
import frontend as app

path = os.path.dirname(os.path.abspath(__file__))


def test_r1_t1(capsys):
    """Testing r2. Self-contained (i.e. everything in the code approach)
    [my favorite - all in one place with the code]

    Arguments:
        capsys -- object created by pytest to capture stdout and stderr
    """
    helper(
        capsys=capsys,
        terminal_input=[
            'login', 'quit'
        ],
        intput_valid_accounts=[],
        expected_tail_of_terminal_output=[app.FrontEndInstance.input_command + app.FrontEndInstance.LOGIN_MESSAGE],
        expected_output_transactions=[]
    )

def helper(
        capsys,
        terminal_input,
        expected_tail_of_terminal_output,
        intput_valid_accounts,
        expected_output_transactions
):
    """Helper function for testing

    Arguments:
        capsys -- object created by pytest to capture stdout and stderr
        terminal_input -- list of string for terminal input
        expected_tail_of_terminal_output list of expected string at the tail of terminal
        intput_valid_accounts -- list of valid accounts in the valid_account_list_file
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
        wf.write('\n'.join(intput_valid_accounts))

    # prepare program parameters
    sys.argv = [
        'frontend.py',
        valid_account_list_file,
        transaction_summary_file]

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
    for i in range(1, len(expected_tail_of_terminal_output)+1):
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