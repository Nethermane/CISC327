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
            'login', 'q', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Select session type (machine or agent): ', 'Command: '],
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


def test_r2_t1(capsys):
    # Verify that user can login for an atm session
    helper(
        capsys=capsys,
        terminal_input=[
            'login', 'machine', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Successfully logged in as "machine"', 'Command: '],
        expected_output_transactions=[]
    )


def test_r2_t2(capsys):
    # Verify that user can login for an agent session
    helper(
        capsys=capsys,
        terminal_input=[
            'login', 'agent', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Successfully logged in as "agent"', 'Command: '],
        expected_output_transactions=[]
    )


def test_r2_t3(capsys):
    # Verify that user cannot login for a non-existent session
    helper(
        capsys=capsys,
        terminal_input=[
            'login', 'mouahaha', 'q', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Error: unrecognized command: "mouahaha", login with either machine or agent',
                                          'Select session type (machine or agent): ', 'Command: '],
        expected_output_transactions=[]
    )


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


def test_r4_t1(capsys):
    # Logout should only be accepted when logged in – machine
    helper(
        capsys=capsys,
        terminal_input=[
            'login', 'machine', 'logout'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Successfully logged out'],
        expected_output_transactions=['EOS 0000000 000 0000000 ***']
    )


def test_r4_t2(capsys):
    # Logout should only be accepted when logged in – agent
    helper(
        capsys=capsys,
        terminal_input=[
            'login', 'agent', 'logout'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Successfully logged out'],
        expected_output_transactions=["EOS 0000000 000 0000000 ***"]
    )


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


def test_r5_t2(capsys):
    # Priviledged transaction create account should be accepted in agent mode
    helper(
        capsys=capsys,
        terminal_input=[
            'login', 'agent', 'createacct', 'q', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Account Number: ', 'Command: '],
        expected_output_transactions=[]
    )


def test_r6_t1(capsys):
    # Create account: account number must not be < 7 numbers
    helper(
        capsys=capsys,
        terminal_input=[
            'login', 'agent', 'createacct', '123456', 'q', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Invalid account number, must be 7 digits, not beginning with a 0',
                                          'Account Number: ', 'Command: '],
        expected_output_transactions=[]
    )


def test_r6_t2(capsys):
    # Create account: account number must not start with a 0
    helper(
        capsys=capsys,
        terminal_input=[
            'login', 'agent', 'createacct', '0123456', 'q', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Invalid account number, must be 7 digits, not beginning with a 0',
                                          'Account Number: ', 'Command: '],
        expected_output_transactions=[]
    )


def test_r6_t3(capsys):
    # Create account: account number must not be > 7 numbers
    helper(
        capsys=capsys,
        terminal_input=[
            'login', 'agent', 'createacct', '12345678', 'q', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Invalid account number, must be 7 digits, not beginning with a 0',
                                          'Account Number: ', 'Command: '],
        expected_output_transactions=[]
    )


def test_r6_t4(capsys):
    # Account number must not contain non-numeric characters
    helper(
        capsys=capsys,
        terminal_input=[
            'login', 'agent', 'createacct', 'a123456', 'q', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Invalid account number, must be 7 digits, not beginning with a 0',
                                          'Account Number: ', 'Command: '],
        expected_output_transactions=[]
    )


def test_r6_t5(capsys):
    # Account number is valid
    helper(
        capsys=capsys,
        terminal_input=[
            'login', 'agent', 'createacct', '1234567', 'q', 'quit'
        ],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Command: '],
        expected_output_transactions=[]
    )


def test_r7_t1(capsys):
    # Account numbers cannot be repeated
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
    # Account name can't have less than 3 characters
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'createacct', '1234567', 'ab', 'q', 'quit'],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Invalid account name. Account name must be between 3 and 30 alphanumeric '
                                          'characters, not beginning or ending with a space',
                                          'Account Name: ',
                                          'Command: '],
        expected_output_transactions=[]
    )


def test_r8_t2(capsys):
    # Account name can't have more than 30 characters
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'createacct', '1234567', 'abcdefghijklmnopqrstuvwxyzabcde', 'q', 'quit'],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Invalid account name. Account name must be between 3 and 30 alphanumeric '
                                          'characters, not beginning or ending with a space',
                                          'Account Name: ',
                                          'Command: '],
        expected_output_transactions=[]
    )


def test_r8_t3(capsys):
    # Account name can't start with a space
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'createacct', '1234567', ' ab', 'q', 'quit'],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Invalid account name. Account name must be between 3 and 30 alphanumeric '
                                          'characters, not beginning or ending with a space',
                                          'Account Name: ',
                                          'Command: '],
        expected_output_transactions=[]
    )


def test_r8_t4(capsys):
    # Account name can't end with a space
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'createacct', '1234567', 'ab ', 'q', 'quit'],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Invalid account name. Account name must be between 3 and 30 alphanumeric '
                                          'characters, not beginning or ending with a space',
                                          'Account Name: ',
                                          'Command: '],
        expected_output_transactions=[]
    )


def test_r8_t5(capsys):
    # Positive test case for a valid account name
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'createacct', '1234567', 'abc', 'logout'],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Command: ',
                                          'Successfully logged out'],
        expected_output_transactions=['NEW 1234567 000 0000000 abc', 'EOS 0000000 000 0000000 ***']
    )


def test_r9_t1(capsys):
    # Verify ATM user cannot delete accounts
    helper(
        capsys=capsys,
        terminal_input=['login', 'machine', 'deleteacct', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Error: agent session required for deleteacct command',
                                          'Command: '],
        expected_output_transactions=[]
    )


def test_r9_t2(capsys):
    # Verify tellers can delete accounts
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'deleteacct', 'q', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Account Number: ',
                                          'Command: '],
        expected_output_transactions=[]
    )


def test_r10_t1(capsys):
    # Verify numbers must be valid
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'deleteacct', '1234566', 'q', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Error: account number not found',
                                          'Account Number: ',
                                          'Command: '],
        expected_output_transactions=[]
    )


def test_r10_t2(capsys):
    # Verify transaction accepted with valid account number
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'deleteacct', '1234566', 'q', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Error: account number not found',
                                          'Account Number: ',
                                          'Command: '],
        expected_output_transactions=[]
    )


def test_r10_t3(capsys):
    # Verify transaction accepted with valid account number and provided name
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'deleteacct', '1234567', 'f12rf', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=[],
        expected_output_transactions=['DEL 1234567 000 0000000 f12rf', 'EOS 0000000 000 0000000 ***']
    )


def test_r11_t1(capsys):
    # verify deposit checks for valid account number in valid accounts list
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'deposit', '1234567', 'q', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Amount(cents): ', 'Command: '],
        expected_output_transactions=[]
    )


def test_r11_t2(capsys):
    # Verify invalid accounts can't deposit
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'deposit', '1234567', 'q', 'quit'],
        input_valid_accounts=['0000000'],
        expected_tail_of_terminal_output=['Error: account number not found', 'Account Number: ', 'Command: '],
        expected_output_transactions=[]
    )


def test_r11_t3(capsys):
    # Ensure that the amount deposited is a valid number
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'deposit', '1234567', '1a2b', 'q', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Error:parsing input', 'Amount(cents): ', 'Command: '],
        expected_output_transactions=[]
    )


def test_r12_t1(capsys):
    # Agent deposits can't be greater than $999999.99
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'deposit', '1234567', '100000000', 'q', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Error: must be less than or equal to 99999999 cents', 'Amount(cents): ',
                                          'Command: '],
        expected_output_transactions=[]
    )


def test_r12_t2(capsys):
    # Verify agent can deposit less than or equal to $999999.99
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'deposit', '1234567', '99999999', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Deposit successful', 'Command: '],
        expected_output_transactions=['DEP 1234567 99999999 0000000 ***', 'EOS 0000000 000 0000000 ***']
    )


def test_r12_t3(capsys):
    # ATM deposits can't be greater than $2000
    helper(
        capsys=capsys,
        terminal_input=['login', 'machine', 'deposit', '1234567', '200001', 'q', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Error: must be less than or equal to 200000 cents', 'Amount(cents): ',
                                          'Command: '],
        expected_output_transactions=[]
    )


def test_r12_t4(capsys):
    # Verify atm deposits below $2000 can be made
    helper(
        capsys=capsys,
        terminal_input=['login', 'machine', 'deposit', '1234567', '200000', 'q', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Deposit successful', 'Command: ', 'Command: '],
        expected_output_transactions=[]
    )


def test_r12_t5(capsys):
    # ATM desposits over a single day can not total greater than $5000
    helper(
        capsys=capsys,
        terminal_input=['login', 'machine', 'deposit', '1234567', '200000',
                        'deposit', '1234567', '200000',
                        'deposit', '1234567', '100001', 'q', 'logout'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Error: deposit over limit', 'Amount(cents): ', 'Command: ',
                                          'Successfully logged out'],
        expected_output_transactions=['DEP 1234567 200000 0000000 ***',
                                      'DEP 1234567 200000 0000000 ***',
                                      'EOS 0000000 000 0000000 ***']
    )


def test_r13_t1(capsys):
    # Prevent withdrawls from invalid accounts
    helper(
        capsys=capsys,
        terminal_input=['login', 'machine', 'withdraw', '1234567', 'q', 'quit'],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Error: account number not found', 'Account Number: ', 'Command: '],
        expected_output_transactions=[]
    )


def test_r13_t2(capsys):
    # Prevent withdrawls of invalid amounts
    helper(
        capsys=capsys,
        terminal_input=['login', 'machine', 'withdraw', '1234567', 'a12', 'q', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Error:parsing input', 'Amount(cents): ', 'Command: '],
        expected_output_transactions=[]
    )


def test_r14_t1(capsys):
    # ATM withdrawls can't be above $1000
    helper(
        capsys=capsys,
        terminal_input=['login', 'machine', 'withdraw', '1234567', '100001', 'q', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Error: must be less than or equal to 100000 cents', 'Amount(cents): ',
                                          'Command: '],
        expected_output_transactions=[]
    )


def test_r14_t2(capsys):
    # Verify ATM withdrawl less than $1,000 work
    helper(
        capsys=capsys,
        terminal_input=['login', 'machine', 'withdraw', '1234567', '100000', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Withdraw successful', 'Command: '],
        expected_output_transactions=['WDR 1234567 99999999 0000000 ***', 'EOS 0000000 000 0000000 ***']
    )


def test_r14_t3(capsys):
    # Agent withdrawls can't be greater than $999999.99
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'withdraw', '1234567', '100000000', 'q', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Error: must be less than or equal to 99999999 cents', 'Amount(cents): ',
                                          'Command: '],
        expected_output_transactions=[]
    )


def test_r14_t4(capsys):
    # Verify agent withdrawls <=$999,999.99 work
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'withdraw', '1234567', '99999999', 'logout', 'quit'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=[],
        expected_output_transactions=['WDR 0000000 99999999 1234567 ***', 'EOS 0000000 000 0000000 ***']
    )


def test_r15_t1(capsys):
    # ATM withdrawls over a single day can not total greater than $5000
    helper(
        capsys=capsys,
        terminal_input=['login', 'machine', 'withdraw', '1234567', '100000',
                        'withdraw', '1234567', '100000',
                        'withdraw', '1234567', '100000',
                        'withdraw', '1234567', '100000',
                        'withdraw', '1234567', '100000',
                        'withdraw', '1234567', '1', 'q', 'logout'],
        input_valid_accounts=['1234567', '0000000'],
        expected_tail_of_terminal_output=['Error: withdraw over limit', 'Amount(cents): ', 'Command: ',
                                          'Successfully logged out'],
        expected_output_transactions=['WDR 0000000 100000 1234567 ***',
                                      'WDR 0000000 100000 1234567 ***',
                                      'WDR 0000000 100000 1234567 ***',
                                      'WDR 0000000 100000 1234567 ***',
                                      'WDR 0000000 100000 1234567 ***',
                                      'EOS 0000000 000 0000000 ***']
    )


def test_r16_t1(capsys):
    # Prevent transfers from invalid accounts
    helper(
        capsys=capsys,
        terminal_input=['login', 'machine', 'transfer', '1234567', 'q', 'quit'],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Error: account number not found',
                                          'From: ',
                                          'Command: '],
        expected_output_transactions=[]
    )


def test_r16_t2(capsys):
    # Prevent tansfers to invalid account
    helper(
        capsys=capsys,
        terminal_input=['login', 'machine', 'transfer', '1234567', '1234566', 'q', 'quit'],
        input_valid_accounts=['1234567'],
        expected_tail_of_terminal_output=['Error: account number not found',
                                          'To: ',
                                          'Command: '],
        expected_output_transactions=[]
    )


def test_r16_t3(capsys):
    # Prevent withdrawls of invalid amounts
    helper(
        capsys=capsys,
        terminal_input=['login', 'machine', 'withdraw', '1234567', 'q', 'quit'],
        input_valid_accounts=[],
        expected_tail_of_terminal_output=['Error: account number not found',
                                          'Account Number: ',
                                          'Command: '],
        expected_output_transactions=[]
    )


def test_r17_t1(capsys):
    # ATM transfers can't be greater than $10000
    helper(
        capsys=capsys,
        terminal_input=['login', 'machine', 'transfer', '1234566', '1234567', '1000001', 'q', 'quit'],
        input_valid_accounts=['1234567', '1234566'],
        expected_tail_of_terminal_output=['Error: must be less than or equal to 1000000 cents',
                                          'Amount(cents): ',
                                          'Command: '],
        expected_output_transactions=['EOS 0000000 000 0000000 ***']
    )


def test_r17_t2(capsys):
    # Atm transfers should work for <=$10000
    helper(
        capsys=capsys,
        terminal_input=['login', 'machine', 'transfer', '1234566', '1234567', '1000000', 'logout'],
        input_valid_accounts=['1234567', '1234566'],
        expected_tail_of_terminal_output=['Command: ',
                                          'Select session type (machine or agent): ',
                                          'Successfully logged in as "machine"',
                                          'Command: ',
                                          'From: ',
                                          'To: ',
                                          'Amount(cents): ',
                                          'Transfer successful',
                                          'Command: ',
                                          'Successfully logged out'],
        expected_output_transactions=['XFR 1234567 1000000 1234566 ***', 'EOS 0000000 000 0000000 ***']
    )


def test_r17_t3(capsys):
    # Total number of ATM transfers out of an account cannot be >$10,000
    helper(
        capsys=capsys,
        terminal_input=['login', 'machine', 'transfer', '1234566', '1234567', '500000',
                        'transfer', '1234566', '1234567', '500001', 'q', 'quit'],
        input_valid_accounts=['1234567', '1234566'],
        expected_tail_of_terminal_output=['Error: transfer over limit',
                                          'Amount(cents): ',
                                          'Command: '],
        expected_output_transactions=['XFR 1234567 500000 1234566 ***']
    )


def test_r17_t4(capsys):
    # Teller mode transfers can't be greater than $999999.99
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'transfer', '1234566', '1234567', '100000000', 'q', 'quit'],
        input_valid_accounts=['1234567', '1234566'],
        expected_tail_of_terminal_output=['Error: must be less than or equal to 99999999 cents',
                                          'Amount(cents): ',
                                          'Command: '],
        expected_output_transactions=[]
    )


def test_r17_t5(capsys):
    # Teller should be able to transfer <= 999,999.99
    helper(
        capsys=capsys,
        terminal_input=['login', 'agent', 'transfer', '1234566', '1234567', '99999999', 'logout'],
        input_valid_accounts=['1234567', '1234566'],
        expected_tail_of_terminal_output=['Command: ',
                                          'Select session type (machine or agent): ',
                                          'Successfully logged in as "agent"',
                                          'Command: ',
                                          'From: ',
                                          'To: ',
                                          'Amount(cents): ',
                                          'Transfer successful',
                                          'Command: ',
                                          'Successfully logged out'],
        expected_output_transactions=['XFR 1234567 99999999 1234566 ***', 'EOS 0000000 000 0000000 ***']
    )


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
    app.main()

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
