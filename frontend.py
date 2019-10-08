import constants
import re
import os.path
import sys
import enum
from typing import List


class FrontEndInstance(object):
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
    Enum for all the Transaction summary acronyms
    '''

    class TransactionSummaryValues(enum.Enum):
        deposit: str = 'DEP'
        withdraw: str = 'WDR'
        transfer: str = 'XFR'
        createacct: str = 'NEW'
        deleteacct: str = 'DEL'
        end_of_file: str = 'EOS'

        def __str__(self):
            return self.value

    # Constant strings that are defined by members of FrontEndInstance
    PRIVILEGED_COMMANDS: List[Commands] = [Commands.createacct, Commands.deleteacct]
    ATM_COMMANDS: List[Commands] = [Commands.login, Commands.logout, Commands.deposit, Commands.withdraw,
                                    Commands.transfer]
    LOGIN_MESSAGE: str = 'Select session type (' + UserState.atm.value + ' or ' + UserState.agent.value + '): '
    HELP_TEXT: str = 'Accepted commands: ' + ', '.join(map(lambda c: c.value, ATM_COMMANDS)) + ', ' \
                     + ', '.join(map(lambda c: c.value, PRIVILEGED_COMMANDS))

    @staticmethod
    def missing_user_state_for_command(state: UserState, command: Commands):
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

    def __init__(self, accounts_file: str, transaction_summary_file: str):
        self.accounts_file: str = accounts_file
        self.transaction_summary_file: str = transaction_summary_file
        self.user_status: self.UserState = self.UserState('idle')
        self.current_file_output: List[List[self.TransactionSummaryValues or str]] = []
        self.accounts_list: List[str] = []

    def front_end_loop(self) -> None:
        print(constants.first_launch_message)
        while True:
            user_command = input(constants.input_command)
            try:
                parsed_command = self.Commands(user_command.lower().strip())
            except ValueError:
                print(constants.error_unrecognized_command)
                continue
            # Prevent all commands but login before logging in
            if self.user_status == self.UserState.idle and parsed_command != self.Commands.login:
                print(constants.not_logged_in_message)
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
            print(constants.error_logged_in_login)
            return
        while True:
            user_input = input(self.LOGIN_MESSAGE)
            try:
                parsed_login = self.UserState(user_input.lower().strip())
            except ValueError:
                if user_input == self.Commands.cancel.value:
                    return
                print(FrontEndInstance.unrecognized_login_command(user_input))
                continue
            if parsed_login == self.UserState.atm \
                    or parsed_login == self.UserState.agent:
                self.user_status = parsed_login
                print(FrontEndInstance.successful_login(parsed_login))
                with open(self.accounts_file) as fp:
                    self.accounts_list = fp.readlines()
                return

    def logout(self) -> None:
        if self.user_status == self.UserState.idle:
            print(constants.error_logged_out_logout_message)
            return
        self.write_to_transaction_log(self.TransactionSummaryValues.end_of_file)
        os.makedirs(os.path.dirname(self.transaction_summary_file), exist_ok=True)  # make folders if necessary
        with open(self.transaction_summary_file, 'w') as fp:
            for transaction in self.current_file_output:
                fp.write(' '.join(map(lambda part: str(part), transaction)) + '\n')
        self.current_file_output.clear()
        self.user_status = self.UserState.idle
        print(constants.successful_logout)

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
        self.write_to_transaction_log(self.TransactionSummaryValues.createacct, to=account_number, name=account_name)
        print(constants.successful_create)

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
        self.write_to_transaction_log(self.TransactionSummaryValues.deleteacct, to=account_number, name=account_name)
        print(constants.successful_delete)

    def deposit(self) -> None:
        if self.user_status == self.UserState.idle:
            print(FrontEndInstance.must_be_signed_in_for_command(self.Commands.deposit))
            return
        account_number = self.get_account_number_in_list()
        # Check number less than max single transaction
        cents = FrontEndInstance.get_valid_numeric_amount(
            self.MAX_DEPOSIT_ATM_ONCE if self.user_status == self.UserState.atm else self.MAX_DEPOSIT_TELLER_ONCE)
        if cents is None:
            return
        # Check if total deposits that day less than total
        if (self.user_status == self.UserState.agent or self.total_within_daily_limit(
                FrontEndInstance.TransactionSummaryValues.deposit,
                account_number,
                self.MAX_DEPOSIT_ATM_DAILY)):
            self.write_to_transaction_log(self.TransactionSummaryValues.withdraw, to=account_number, cents=cents)
            print(constants.successful_deposit)
        else:
            print(constants.error_deposit_over_max)

    def withdraw(self) -> None:
        if self.user_status == self.UserState.idle:
            print(FrontEndInstance.must_be_signed_in_for_command(self.Commands.withdraw))
            return
        account_number = self.get_account_number_in_list()
        # Check number less than max single transaction
        cents = FrontEndInstance.get_valid_numeric_amount(
            self.MAX_WITHDRAW_ATM_ONCE if self.user_status == self.UserState.atm
            else self.MAX_WITHDRAW_AGENT_ONCE)
        if cents is None:
            return
        # Check if total withdrawl less than total limit
        if (self.user_status == self.UserState.agent or self.total_within_daily_limit(
                FrontEndInstance.TransactionSummaryValues.withdraw,
                account_number,
                self.MAX_WITHDRAW_ATM_DAILY)):
            self.write_to_transaction_log(self.TransactionSummaryValues.withdraw, cents=cents, from_act=account_number)
            print(constants.successful_withdraw)
        else:
            print(constants.error_withdraw_over_max)

    def transfer(self) -> None:
        if self.user_status == self.UserState.idle:
            print(FrontEndInstance.must_be_signed_in_for_command(self.Commands.withdraw))
            return
        from_account = self.get_account_number_in_list()
        to_account = self.get_account_number_in_list()
        # Check number less than max single transaction
        cents = self.get_valid_numeric_amount(
            self.MAX_TRANSFER_ATM_ONCE if self.user_status == self.UserState.atm else self.MAX_TRANSFER_AGENT_ONCE)
        if cents is None:
            return
        # Check if total withdrawl less than total limit
        if (self.user_status == self.UserState.agent or self.total_within_daily_limit(
                FrontEndInstance.TransactionSummaryValues.transfer,
                from_account,
                self.MAX_TRANSFER_ATM_ONCE)):
            self.write_to_transaction_log(self.TransactionSummaryValues.transfer, to_account, cents, from_account)
            print(constants.successful_withdraw)
        else:
            print(constants.error_withdraw_over_max)

    def write_to_transaction_log(self, transaction_type: TransactionSummaryValues, to: str = '0000000',
                                 cents: str = '000', from_act: str = '0000000',
                                 name: str = '***') -> None:
        self.current_file_output.append([transaction_type, to, cents, from_act, name])

    @staticmethod
    def valid_account_name(name: str) -> bool:
        return name is not None and re.search('^[\w][\w ]{1,28}[\w]$', name) is not None

    @staticmethod
    def valid_account_number(number: str) -> bool:
        return number is not None and re.search('^[1-9][0-9]{6}$', number) is not None

    @staticmethod
    def valid_cents_amount(number: int, max_value: int) -> bool:
        return number is not None and number <= max_value

    # Determines if account has had more than specified limit amount of transactions done to it
    def total_within_daily_limit(self, output_key: TransactionSummaryValues, account_number: str, limit: int) -> bool:
        account_num_pos = 3 if output_key in [FrontEndInstance.TransactionSummaryValues.transfer,
                                              FrontEndInstance.TransactionSummaryValues.withdraw] else 1
        return sum(
            map(lambda row: int(row[2]),
                filter(lambda row: row[0] == output_key and account_number == row[account_num_pos],
                       self.current_file_output))) <= limit

    # returns a valid account number from user input
    # If check_accounts_list is True, requires the number to be in the accounts list
    # returns None if exit command is provided
    @staticmethod
    def get_valid_account_number() -> str or None:
        while True:
            account_number = input(constants.input_account_number)
            if FrontEndInstance.valid_account_number(account_number):
                return account_number
            elif account_number == FrontEndInstance.Commands.cancel:
                return None
            else:
                print(constants.invalid_account_number)

    def get_account_number_in_list(self) -> str or None:
        while True:
            account_number = input(constants.input_account_number)
            if account_number in self.accounts_list:
                return account_number
            elif account_number == self.Commands.cancel:
                return None
            else:
                print(constants.error_account_not_found)

    # returns a valid account name from user input
    # returns None if exit command is provided
    @staticmethod
    def get_valid_account_name() -> str or None:
        while True:
            account_name = input(constants.input_account_name)
            if FrontEndInstance.valid_account_name(account_name):
                return account_name
            elif account_name == FrontEndInstance.Commands.cancel:
                return None
            else:
                print(constants.invalid_account_name)

    # returns a valid cents amount less than or equal to max value
    # returns None if exit command provided
    # returns a string, ensuring it is validly numeric.
    @staticmethod
    def get_valid_numeric_amount(max_value: int) -> str or None:
        while True:
            cents = input(constants.input_cents).replace(',', '')
            try:
                cents_int = int(cents)
                if FrontEndInstance.valid_cents_amount(cents_int, max_value):
                    return str(cents_int)
                else:
                    print(FrontEndInstance.error_cents_less_than(str(max_value)))
            except ValueError:
                if cents == FrontEndInstance.Commands.cancel:
                    return None
                print(constants.parse_number_error)


def main(front_end_instance: FrontEndInstance) -> None:
    front_end_instance.front_end_loop()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Invalid usage, must be of the format "frontend accounts_file.txt transaction_summary.txt"')
        exit(1)
    accounts_file_input = os.path.normpath(sys.argv[1])
    transaction_summary_file_input = os.path.normpath(sys.argv[2])
    main(FrontEndInstance(accounts_file_input, transaction_summary_file_input))
