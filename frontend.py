import enum
import os.path
import re
import sys
from typing import List, Iterator


class FrontEndInstance(object):
    def __init__(self, accounts_file: str, transaction_summary_file: str) -> None:
        self.accounts_file: str = accounts_file
        self.user_status: self.UserState = self.UserState('idle')
        self.transaction_summary: self.TransactionSummary = self.TransactionSummary(transaction_summary_file)
        self.accounts_list: List[str] = []

    # Const max values that are relevant to this class and should be easy to find
    MAX_DEPOSIT_ATM_ONCE: int = 200000
    MAX_DEPOSIT_ATM_DAILY: int = 500000
    MAX_DEPOSIT_TELLER_ONCE: int = 99999999
    MAX_WITHDRAW_ATM_ONCE: int = 100000
    MAX_WITHDRAW_ATM_DAILY: int = 500000
    MAX_WITHDRAW_AGENT_ONCE: int = 99999999
    MAX_TRANSFER_ATM_ONCE: int = 1000000
    MAX_TRANSFER_ATM_DAILY: int = 1000000
    MAX_TRANSFER_AGENT_ONCE: int = 99999999

    '''
    Enum to represent the current user state
    '''

    class UserState(enum.Enum):
        idle: str = 'idle'
        atm: str = 'atm'
        agent: str = 'machine'

        def __str__(self):
            return self.value

    '''
    Enum for all the commands a user can enter from the main loop
    '''

    class Commands(enum.Enum):
        login: str = 'login'
        logout: str = 'logout'
        createacct: str = 'createacct'
        deleteacct: str = 'deleteacct'
        deposit: str = 'deposit'
        withdraw: str = 'withdraw'
        transfer: str = 'transfer'
        cancel: str = 'q'
        help: str = 'help'

        def __str__(self):
            return self.value

    '''
    Object that represents a transaction summary
    '''

    class TransactionSummary(object):
        """
        Object that represents a row to be written to summary file
        """

        def __init__(self, summary_file) -> None:
            self._summary: List[self.TransactionSummaryRow] = []
            self.summary_file = summary_file

        class TransactionSummaryRow(object):
            """
            Enum for all the Transaction summary acronyms
            """

            class TransactionSummaryKeys(enum.Enum):
                deposit: str = 'DEP'
                withdraw: str = 'WDR'
                transfer: str = 'XFR'
                createacct: str = 'NEW'
                deleteacct: str = 'DEL'
                end_of_file: str = 'EOS'

                def __str__(self) -> str:
                    return self.value

            # TransactionSummaryRow
            def __init__(self, transaction_type: TransactionSummaryKeys, to: str, cents: str,
                         from_act: str, name: str) -> None:
                self.transaction_type: self.TransactionSummaryKeys = transaction_type
                self.to: str = to
                self.cents: str = cents
                self.from_act: str = from_act
                self.name: str = name

            def __str__(self) -> str:
                return str(self.transaction_type) \
                       + ' ' + self.to \
                       + ' ' + self.cents \
                       + ' ' + self.from_act \
                       + ' ' + self.name

        def add_row(self, transaction_type: TransactionSummaryRow.TransactionSummaryKeys, to: str = '0000000',
                    cents: str = '000',
                    from_act: str = '0000000', name: str = '***') -> None:
            self._summary.append(self.TransactionSummaryRow(transaction_type, to, cents, from_act, name))

        def clear(self) -> None:
            self._summary.clear()

        def total_within_daily_limit(self, output_key: TransactionSummaryRow.TransactionSummaryKeys,
                                     account_number: str, amount_to_add: int, limit: int) -> bool:
            return sum(self._map_row_to_cents(self._get_rows_by_num_and_transaction(output_key, account_number))) \
                   <= (limit - amount_to_add)

        @staticmethod
        def _map_row_to_cents(rows: Iterator[TransactionSummaryRow]):
            return map(lambda row: int(row.cents), rows)

        def to_file(self) -> str:
            return '\n'.join(map(lambda row: str(row), self._summary))

        def _get_rows_by_num_and_transaction(self, output_key: TransactionSummaryRow.TransactionSummaryKeys,
                                             account_number: str):
            if (output_key == self.TransactionSummaryRow.TransactionSummaryKeys.transfer
                    or output_key == self.TransactionSummaryRow.TransactionSummaryKeys.withdraw):
                # return interactions matching the from account number
                return filter(lambda row: row.transaction_type == output_key and account_number == row.from_act,
                              self._summary)
            # return interactions matching to function
            return filter(lambda row: row.transaction_type == output_key and account_number == row.to, self._summary)

    # Constant strings that are used for printing
    PRIVILEGED_COMMANDS: List[Commands] = [Commands.createacct, Commands.deleteacct]
    ATM_COMMANDS: List[Commands] = [Commands.login, Commands.logout, Commands.deposit, Commands.withdraw,
                                    Commands.transfer]
    LOGIN_MESSAGE: str = 'Select session type (' + UserState.atm.value + ' or ' + UserState.agent.value + '): '
    HELP_TEXT: str = 'Accepted commands: ' + ', '.join(map(lambda c: c.value, ATM_COMMANDS)) + ', ' \
                     + ', '.join(map(lambda c: c.value, PRIVILEGED_COMMANDS))
    error_account_not_found: str = 'Error: account number not found'
    error_deposit_over_max: str = 'Error: deposit over limit'
    error_logged_in_login: str = 'Error: already logged in'
    error_logged_out_logout_message: str = 'Error not logged in'
    error_unrecognized_command: str = 'Error: unrecognized command'
    error_withdraw_over_max: str = 'Error: withdraw over limit'
    first_launch_message: str = 'Welcome to Quinterac banking, type login to begin'
    input_account_name: str = 'Account Name: '
    input_account_number: str = 'Account Number: '
    input_cents: str = 'Amount(cents): '
    input_command: str = 'Command: '
    input_from: str = 'From: '
    input_to: str = 'To: '
    invalid_account_name: str = 'Invalid account name. Account number must be between 3 and 30 alphanumeric ' \
                                'characters, not beginning or ending with a space '
    invalid_account_number: str = 'Invalid account number, must be 7 digits, not beginning with a 0'
    not_logged_in_message: str = 'In idle state, please login before use'
    parse_number_error: str = 'Error parsing input'
    successful_create: str = "Create account successful"
    successful_delete: str = 'Delete account successful'
    successful_deposit: str = 'Deposit successful'
    successful_logout: str = 'Successfully logged out'
    successful_withdraw: str = 'Withdraw successful'

    @staticmethod
    def missing_user_state_for_command(state: UserState, command: Commands) -> str:
        return 'Error: ' + state.value + 'session required for ' + command.value + ' command '

    @staticmethod
    def successful_login(session_type: UserState) -> str:
        return 'Successfully logged in as "' + session_type.value + '"'

    @staticmethod
    def unrecognized_login_command(command: str) -> str:
        return 'Error unrecognized command: "' + command + '", login with either ' \
               + FrontEndInstance.UserState.atm.value + ' or ' + FrontEndInstance.UserState.atm.agent.value

    @staticmethod
    def must_be_signed_in_for_command(command: Commands) -> str:
        return 'Command: "' + command.value + '" requires a logged in session'

    @staticmethod
    def error_cents_less_than(max_value: str) -> str:
        return 'Error: must be less than or equal to ' + max_value + ' cents'

    def front_end_loop(self) -> None:
        print(FrontEndInstance.first_launch_message)
        while True:
            user_command = input(FrontEndInstance.input_command)
            try:
                parsed_command = self.Commands(user_command.lower().strip())
            except ValueError:
                print(FrontEndInstance.error_unrecognized_command)
                continue
            # Prevent all commands but login before logging in
            if self.user_status == self.UserState.idle and parsed_command != self.Commands.login:
                print(FrontEndInstance.not_logged_in_message)
            # login
            elif parsed_command == self.Commands.login:
                self.login()
            # logout
            elif parsed_command == self.Commands.logout:
                self.logout()
            # createacct
            elif parsed_command == self.Commands.createacct:
                self.create_account()
            # deleteacct
            elif parsed_command == self.Commands.deleteacct:
                self.delete_account()
            # deposit
            elif parsed_command == self.Commands.deposit:
                self.deposit()
            # withdraw
            elif parsed_command == self.Commands.withdraw:
                self.withdraw()
            # transfer
            elif parsed_command == self.Commands.transfer:
                self.transfer()
            elif parsed_command == self.Commands.help:
                print(self.HELP_TEXT)

    def login(self) -> None:
        if self.user_status != self.UserState.idle:
            print(FrontEndInstance.error_logged_in_login)
            return
        while True:
            user_input = input(self.LOGIN_MESSAGE)
            try:
                parsed_login = self.UserState(user_input.lower().strip())
                if parsed_login == self.UserState.atm or parsed_login == self.UserState.agent:
                    self.user_status = parsed_login
                    with open(self.accounts_file) as fp:
                        self.accounts_list = fp.readlines()
                    print(FrontEndInstance.successful_login(parsed_login))
                    return
            except ValueError:
                if user_input == self.Commands.cancel.value:
                    return
                print(FrontEndInstance.unrecognized_login_command(user_input))
                continue

    def logout(self) -> None:
        if self.user_status == self.UserState.idle:
            print(FrontEndInstance.error_logged_out_logout_message)
            return
        self.transaction_summary.add_row(
            self.TransactionSummary.TransactionSummaryRow.TransactionSummaryKeys.end_of_file)
        os.makedirs(os.path.dirname(self.transaction_summary.summary_file), exist_ok=True)  # make folders if necessary
        with open(self.transaction_summary.summary_file, 'w') as fp:
            fp.write(self.transaction_summary.to_file())
        self.transaction_summary.clear()
        self.user_status = self.UserState.idle
        print(FrontEndInstance.successful_logout)

    def create_account(self) -> None:
        if self.user_status != self.UserState.agent:
            print(self.missing_user_state_for_command(self.UserState.agent, self.Commands.createacct))
            return
        account_number = self.get_valid_account_number()
        if account_number is None:
            return
        account_name = self.get_valid_account_name()
        if account_name is None:
            return
        self.transaction_summary.add_row(
            self.TransactionSummary.TransactionSummaryRow.TransactionSummaryKeys.createacct,
            to=account_number, name=account_name)
        print(FrontEndInstance.successful_create)

    def delete_account(self) -> None:
        if self.user_status != self.UserState.agent:
            print(self.missing_user_state_for_command(self.UserState.agent, self.Commands.deleteacct))
            return
        account_number = self.get_valid_account_number()
        if account_number is None:
            return
        account_name = self.get_valid_account_name()
        if account_name is None:
            return
        self.transaction_summary.add_row(
            self.TransactionSummary.TransactionSummaryRow.TransactionSummaryKeys.deleteacct,
            to=account_number, name=account_name)
        print(FrontEndInstance.successful_delete)

    def deposit(self) -> None:
        if self.user_status == self.UserState.idle:
            print(FrontEndInstance.must_be_signed_in_for_command(self.Commands.deposit))
            return
        account_number = self.get_account_number_in_list()
        while True:
            # Check number less than max single transaction
            cents = FrontEndInstance.get_valid_numeric_amount(
                self.MAX_DEPOSIT_ATM_ONCE if self.user_status == self.UserState.atm else self.MAX_DEPOSIT_TELLER_ONCE)
            if cents is None:
                return
            # Check if total deposits that day less than total
            if (self.user_status == self.UserState.agent
                    or self.transaction_summary.total_within_daily_limit(
                        self.TransactionSummary.TransactionSummaryRow.TransactionSummaryKeys.deposit,
                        account_number,
                        int(cents),
                        self.MAX_DEPOSIT_ATM_DAILY)):
                self.transaction_summary.add_row(
                    self.TransactionSummary.TransactionSummaryRow.TransactionSummaryKeys.deposit,
                    to=account_number, cents=cents)
                print(FrontEndInstance.successful_deposit)
                return
            else:
                print(FrontEndInstance.error_deposit_over_max)

    def withdraw(self) -> None:
        if self.user_status == self.UserState.idle:
            print(FrontEndInstance.must_be_signed_in_for_command(self.Commands.withdraw))
            return
        account_number = self.get_account_number_in_list()
        # Check number less than max single transaction
        while True:
            cents = FrontEndInstance.get_valid_numeric_amount(
                self.MAX_WITHDRAW_ATM_ONCE if self.user_status == self.UserState.atm
                else self.MAX_WITHDRAW_AGENT_ONCE)
            if cents is None:
                return
            # Check if total withdraw less than total limit
            if (self.user_status == self.UserState.agent
                    or self.transaction_summary.total_within_daily_limit(
                        self.TransactionSummary.TransactionSummaryRow.TransactionSummaryKeys.withdraw,
                        account_number,
                        int(cents),
                        self.MAX_WITHDRAW_ATM_DAILY)):
                self.transaction_summary.add_row(
                    self.TransactionSummary.TransactionSummaryRow.TransactionSummaryKeys.withdraw,
                    cents=cents, from_act=account_number)
                print(FrontEndInstance.successful_withdraw)
                return
            else:
                print(FrontEndInstance.error_withdraw_over_max)

    def transfer(self) -> None:
        if self.user_status == self.UserState.idle:
            print(FrontEndInstance.must_be_signed_in_for_command(self.Commands.withdraw))
            return
        from_account = self.get_account_number_in_list(self.input_from)
        to_account = self.get_account_number_in_list(self.input_to)
        while True:
            # Check number less than max single transaction
            cents = self.get_valid_numeric_amount(
                self.MAX_TRANSFER_ATM_ONCE if self.user_status == self.UserState.atm else self.MAX_TRANSFER_AGENT_ONCE)
            if cents is None:
                return
            # Check if total withdraw less than total limit
            if (self.user_status == self.UserState.agent or self.transaction_summary.total_within_daily_limit(
                    self.TransactionSummary.TransactionSummaryRow.TransactionSummaryKeys.transfer,
                    from_account,
                    int(cents),
                    self.MAX_TRANSFER_ATM_ONCE)):
                self.transaction_summary.add_row(
                    self.TransactionSummary.TransactionSummaryRow.TransactionSummaryKeys.transfer,
                    to_account, cents, from_account)
                print(FrontEndInstance.successful_withdraw)
                continue
            else:
                print(FrontEndInstance.error_withdraw_over_max)

    @staticmethod
    def valid_account_name(name: str) -> bool:
        return name is not None and re.search('^[\w][\w ]{1,28}[\w]$', name) is not None

    @staticmethod
    def valid_account_number(number: str) -> bool:
        return number is not None and re.search('^[1-9][0-9]{6}$', number) is not None

    @staticmethod
    def valid_cents_amount(number: int, max_value: int) -> bool:
        return number is not None and number <= max_value

    '''
    returns a valid account number from user input
    If check_accounts_list is True, requires the number to be in the accounts list
    returns None if exit command is provided
    '''

    @staticmethod
    def get_valid_account_number() -> str or None:
        while True:
            account_number = input(FrontEndInstance.input_account_number)
            if FrontEndInstance.valid_account_number(account_number):
                return account_number
            elif account_number == FrontEndInstance.Commands.cancel:
                return None
            else:
                print(FrontEndInstance.invalid_account_number)

    '''
    Gets a valid account number, validating against the accounts_list
    '''

    def get_account_number_in_list(self, prompt=input_account_number) -> str or None:
        while True:
            account_number = input(prompt)
            if account_number in self.accounts_list:
                return account_number
            elif account_number == self.Commands.cancel:
                return None
            else:
                print(FrontEndInstance.error_account_not_found)

    '''
    returns a valid account name from user input
    returns None if exit command is provided
    '''

    @staticmethod
    def get_valid_account_name() -> str or None:
        while True:
            account_name = input(FrontEndInstance.input_account_name)
            if FrontEndInstance.valid_account_name(account_name):
                return account_name
            elif account_name == FrontEndInstance.Commands.cancel:
                return None
            else:
                print(FrontEndInstance.invalid_account_name)

    '''
    returns a valid cents amount less than or equal to max value
    returns None if exit command provided
    returns a string, ensuring it is validly numeric.
    '''

    @staticmethod
    def get_valid_numeric_amount(max_value: int) -> str or None:
        while True:
            cents = input(FrontEndInstance.input_cents).replace(',', '')
            try:
                cents_int = int(cents)
                if FrontEndInstance.valid_cents_amount(cents_int, max_value):
                    return str(cents_int)
                else:
                    print(FrontEndInstance.error_cents_less_than(str(max_value)))
            except ValueError:
                if cents == FrontEndInstance.Commands.cancel:
                    return None
                print(FrontEndInstance.parse_number_error)


def main(front_end_instance: FrontEndInstance) -> None:
    front_end_instance.front_end_loop()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Invalid usage, must be of the format "frontend accounts_file.txt transaction_summary.txt"')
        exit(1)
    accounts_file_input = os.path.normpath(sys.argv[1])
    transaction_summary_file_input = os.path.normpath(sys.argv[2])
    main(FrontEndInstance(accounts_file_input, transaction_summary_file_input))
