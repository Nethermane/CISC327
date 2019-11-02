import enum
import os.path
import re
import sys
from typing import List


class FrontEndInstance:
    """
    This is a class to represent an instance of the front end.
    This requires a list of accounts to use and a file name transactions output to
    This class prompts users for inputs and, if completed/correct stores the transactions
    Once the logout transaction is entered it outputs the transaction to the summary file

    :param accounts_file: The file that this instance will read accounts from
    :param transaction_summary_file: The file that will be written to once logout is inputted
    """

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

    class UserState(enum.Enum):
        """Enum to represent the current user state"""
        idle: str = 'idle'
        atm: str = 'machine'
        agent: str = 'agent'

        def __str__(self):
            return self.value

    class Commands(enum.Enum):
        """Enum for all the commands a user can enter from the main loop"""
        login: str = 'login'
        logout: str = 'logout'
        createacct: str = 'createacct'
        deleteacct: str = 'deleteacct'
        deposit: str = 'deposit'
        withdraw: str = 'withdraw'
        transfer: str = 'transfer'
        cancel: str = 'q'
        help: str = 'help'
        quit: str = 'quit'

        def __str__(self):
            return self.value

    class TransactionSummary:
        """
        Object to represent a transaction summary, has functionality to write to file
        :param summary_file: The file which will be written to
        """

        def __init__(self, summary_file) -> None:
            self._summary: List[self.TransactionSummaryRow] = []
            self.summary_file = summary_file

        class TransactionSummaryRow:
            """
            Object to represent a single row in a transaction summary.
            :param transaction_type: The transactionType
            :param to: The account to send to
            :param cents: The cents to write to
            :param from_act: The account to send from
            :param name: the account name
            """

            class TransactionSummaryKeys(enum.Enum):
                """Enum for all the Transaction summary acronyms"""
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
            """
            Method to add a new row to the transaction summary
            :param transaction_type: The transactionType
            :param to: The account to send to
            :param cents: The cents to write to
            :param from_act: The account to send from
            :param name: the account name
            """
            self._summary.append(self.TransactionSummaryRow(transaction_type, to, cents, from_act, name))

        def clear(self) -> None:
            """
            Method to clear the current transaction summary
            """
            self._summary.clear()

        def total_within_daily_limit(self, output_key: TransactionSummaryRow.TransactionSummaryKeys,
                                     account_number: str, amount: int, limit: int) -> bool:
            """
            Check if a transaction is within the current daily limit, by summing the interactions of the same type on
            the specific account
            :param output_key: The transactionType
            :param account_number: The account number to check against
            :param amount: The amount of cents to add/transfer/withdraw
            :param limit: The limit for that type of transaction
            :return: Returns true if transaction within daily limit
            """
            # If transfer or withdraw match the from account
            if (output_key == self.TransactionSummaryRow.TransactionSummaryKeys.transfer
                    or output_key == self.TransactionSummaryRow.TransactionSummaryKeys.withdraw):
                transactions_to_sum = filter(
                    lambda row: row.transaction_type == output_key and account_number == row.from_act, self._summary)
            # Otherwise look at the to account
            else:
                transactions_to_sum = filter(
                    lambda row: row.transaction_type == output_key and account_number == row.to, self._summary)

            return sum(map(lambda row: int(row.cents), transactions_to_sum)) <= (limit - amount)

        def to_file(self) -> None:
            """
            Writes the transaction summary to file and clears it
            """
            self.add_row(self.TransactionSummaryRow.TransactionSummaryKeys.end_of_file)
            os.makedirs(os.path.dirname(self.summary_file), exist_ok=True)  # make all folders and file if necessary
            with open(self.summary_file, 'w') as fp:
                fp.write('\n'.join(map(lambda row: str(row), self._summary)))
            self.clear()

    # Constant strings that are used for printing
    PRIVILEGED_COMMANDS: List[Commands] = [Commands.createacct, Commands.deleteacct]
    ATM_COMMANDS: List[Commands] = [Commands.login, Commands.logout, Commands.deposit, Commands.withdraw,
                                    Commands.transfer]
    LOGIN_MESSAGE: str = 'Select session type (' + UserState.atm.value + ' or ' + UserState.agent.value + '): \n'
    HELP_TEXT: str = 'Accepted commands: ' + ', '.join(map(lambda c: c.value, ATM_COMMANDS)) + ', ' \
                     + ', '.join(map(lambda c: c.value, PRIVILEGED_COMMANDS))
    error_account_not_found: str = 'Error: account number not found'
    error_deposit_over_max: str = 'Error: deposit over limit'
    error_logged_in_login: str = 'Error: already logged in'
    error_logged_out_logout_message: str = 'Error: not logged in'
    error_unrecognized_command: str = 'Error: unrecognized command'
    error_withdraw_over_max: str = 'Error: withdraw over limit'
    error_transfer_over_max: str = 'Error: transfer over limit'
    error_account_number_already_exists: str = 'Error: Account number already exists'
    first_launch_message: str = 'Welcome to Quinterac banking, type login to begin'
    input_account_name: str = 'Account Name: \n'
    input_account_number: str = 'Account Number: \n'
    input_cents: str = 'Amount(cents): \n'
    input_command: str = 'Command: \n'
    input_from: str = 'From: \n'
    input_to: str = 'To: \n'
    invalid_account_name: str = 'Invalid account name. Account number must be between 3 and 30 alphanumeric ' \
                                'characters, not beginning or ending with a space'
    invalid_account_number: str = 'Invalid account number, must be 7 digits, not beginning with a 0'
    not_logged_in_message: str = 'In idle state, please login before use'
    parse_number_error: str = 'Error:parsing input'
    successful_create: str = "Create account successful"
    successful_delete: str = 'Delete account successful'
    successful_deposit: str = 'Deposit successful'
    successful_logout: str = 'Successfully logged out'
    successful_withdraw: str = 'Withdraw successful'
    successful_transfer: str = 'Transfer successful'

    @staticmethod
    def missing_user_state_for_command(state: UserState, command: Commands) -> str:
        """
        Makes error string for commands missing required state
        :param state: state that is required
        :param command: command being entered
        :return: string stating an error for missing command
        """
        return 'Error: ' + state.value + ' session required for ' + command.value + ' command'

    @staticmethod
    def successful_login(session_type: UserState) -> str:
        """
        Makes message stating successful login to a session type
        :param session_type: the session type logged into
        :return: successful login message
        """
        return 'Successfully logged in as "' + session_type.value + '"'

    @staticmethod
    def unrecognized_login_command(command: str) -> str:
        """
        Error message for unrecognized command when trying to login
        :param command: user inputs
        :return: an error message about unrecognized command
        """
        return 'Error: unrecognized command: "' + command + '", login with either ' \
               + FrontEndInstance.UserState.atm.value + ' or ' + FrontEndInstance.UserState.atm.agent.value

    @staticmethod
    def must_be_signed_in_for_command(command: Commands) -> str:
        """
        Error message stating command requires a logged in session
        :param command: command in question
        :return: message stating a command requires the user to be logged in
        """
        return 'Command: "' + command.value + '" requires a logged in session'

    @staticmethod
    def error_cents_less_than_or_equal(max_value: str) -> str:
        """
        Error message for cents being less than a specific value
        :param max_value: the amount the cents were greater than
        :return: an error message stating the cents must be less than or equal to value
        """
        return 'Error: must be less than or equal to ' + max_value + ' cents'

    def front_end_loop(self) -> None:
        """
        Method called by constructor to loop through user input and handle appropriately
        """
        print(FrontEndInstance.first_launch_message)
        while True:
            user_command = input(FrontEndInstance.input_command)
            try:
                parsed_command = self.Commands(user_command.lower().strip())
                if parsed_command == self.Commands.quit:
                    return
                # Prevent all other commands but login before logging in
                elif self.user_status == self.UserState.idle and parsed_command != self.Commands.login:
                    print(FrontEndInstance.not_logged_in_message)
                # login
                elif parsed_command == self.Commands.login:
                    if self.login():
                        return
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
            except ValueError:
                print(FrontEndInstance.error_unrecognized_command)

    def login(self) -> bool:
        """
        Method allowing users to log into a user state (atm or teller)
        Returns true if the user entered exit
        """
        if self.user_status != self.UserState.idle:  # if already signed in
            print(FrontEndInstance.error_logged_in_login)
            return False
        while True:
            user_input = input(self.LOGIN_MESSAGE)
            try:
                parsed_login = self.UserState(user_input.lower().strip())
                if parsed_login == self.UserState.atm or parsed_login == self.UserState.agent:  # Input is atm or agent
                    self.user_status = parsed_login
                    with open(self.accounts_file) as fp:
                        self.accounts_list = fp.read().splitlines()  # Load the accounts
                        if '0000000' in self.accounts_list: self.accounts_list.remove('0000000')
                    print(FrontEndInstance.successful_login(parsed_login))
                    return False
            except ValueError:
                if user_input == self.Commands.cancel.value:  # If cancel command inputted
                    return False
                elif user_input == self.Commands.quit.value:
                    return True
                print(FrontEndInstance.unrecognized_login_command(user_input))
                continue

    def logout(self) -> bool:
        """
        Method allowing users to log out of a user state
        """
        if self.user_status == self.UserState.idle:  # If user not logged in
            print(FrontEndInstance.error_logged_out_logout_message)
            return False
        self.transaction_summary.to_file()  # Write the transaction to summary file
        self.accounts_list.clear()  # Clear the accounts list (login populates it again if logged in again)
        self.user_status = self.UserState.idle  # Actually set the session to logged out
        print(FrontEndInstance.successful_logout)

    def create_account(self) -> None:
        """
        Method allowing users to create an account
        """
        if self.user_status != self.UserState.agent:  # If user not in agent state
            print(self.missing_user_state_for_command(self.UserState.agent, self.Commands.createacct))
            return
        while True:
            account_number = self.get_valid_account_number()
            if account_number is None:  # If cancel command
                return
            if account_number in self.accounts_list:
                print(FrontEndInstance.error_account_number_already_exists)
                continue
            break
        account_name = self.get_valid_account_name()
        if account_name is None:  # If cancel command
            return
        self.transaction_summary.add_row(
            self.TransactionSummary.TransactionSummaryRow.TransactionSummaryKeys.createacct,
            to=account_number, name=account_name)
        print(FrontEndInstance.successful_create)

    def delete_account(self) -> None:
        """
        Method allowing users to delete accounts
        """
        if self.user_status != self.UserState.agent:  # If user not in agent state
            print(self.missing_user_state_for_command(self.UserState.agent, self.Commands.deleteacct))
            return
        account_number = self.get_account_number_in_list()
        if account_number is None:  # If cancel command inputted
            return
        account_name = self.get_valid_account_name()
        if account_name is None:  # If cancel command inputted
            return
        self.transaction_summary.add_row(
            self.TransactionSummary.TransactionSummaryRow.TransactionSummaryKeys.deleteacct,
            to=account_number, name=account_name)
        print(FrontEndInstance.successful_delete)

    def deposit(self) -> None:
        """
        Method allowing users to deposit an amount of money into an account
        """
        if self.user_status == self.UserState.idle:  # If user not logged in
            print(FrontEndInstance.must_be_signed_in_for_command(self.Commands.deposit))
            return
        account_number = self.get_account_number_in_list()
        while True:
            # Check number less than max single transaction
            cents = FrontEndInstance.get_valid_numeric_amount(
                self.MAX_DEPOSIT_ATM_ONCE if self.user_status == self.UserState.atm else self.MAX_DEPOSIT_TELLER_ONCE)
            if cents is None:  # If cancel command inputted
                return
            # Check if total deposits that day less than total or in agent mode
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
        """
        Method allowing users to withdraw an amount of money from an account
        """
        if self.user_status == self.UserState.idle:  # If user not logged in
            print(FrontEndInstance.must_be_signed_in_for_command(self.Commands.withdraw))
            return
        account_number = self.get_account_number_in_list()
        if account_number is None:
            return
        while True:
            # Get number less than max single transaction
            cents = FrontEndInstance.get_valid_numeric_amount(
                self.MAX_WITHDRAW_ATM_ONCE if self.user_status == self.UserState.atm
                else self.MAX_WITHDRAW_AGENT_ONCE)
            if cents is None:  # If cancel command inputted
                return
            # Check if total withdraw less than total limit, or in agent mode
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
        """
        Method allowing users to transfer money between accounts
        """
        if self.user_status == self.UserState.idle:
            print(FrontEndInstance.must_be_signed_in_for_command(self.Commands.withdraw))
            return

        from_account = self.get_account_number_in_list(self.input_from)
        if from_account is None:
            return

        to_account = self.get_account_number_in_list(self.input_to)
        if to_account is None:
            return

        while True:
            # Check number less than max single transaction
            cents = self.get_valid_numeric_amount(
                self.MAX_TRANSFER_ATM_ONCE if self.user_status == self.UserState.atm else self.MAX_TRANSFER_AGENT_ONCE)
            if cents is None:  # If cancel command inputted
                return
            # Check if total transfer less than total limit, or in agent mode
            if (self.user_status == self.UserState.agent or self.transaction_summary.total_within_daily_limit(
                    self.TransactionSummary.TransactionSummaryRow.TransactionSummaryKeys.transfer,
                    from_account,
                    int(cents),
                    self.MAX_TRANSFER_ATM_ONCE)):
                self.transaction_summary.add_row(
                    self.TransactionSummary.TransactionSummaryRow.TransactionSummaryKeys.transfer,
                    to_account, cents, from_account)
                print(FrontEndInstance.successful_transfer)
                return
            else:
                print(FrontEndInstance.error_transfer_over_max)

    @staticmethod
    def valid_account_name(name: str) -> bool:
        """
        Method to check if an account name is valid
        :param name: name to check
        :return: True if valid 3-30 characters not starting/ending with whitespace
        """
        return name is not None and re.search(r'^[\w][\w ]{1,28}[\w]$', name) is not None

    @staticmethod
    def valid_account_number(number: str) -> bool:
        """
        Checks if an account number is valid
        :param number: the number to check
        :return: True if account number exactly 7 digits, not starting with 0
        """
        return number is not None and re.search(r'^[1-9][0-9]{6}$', number) is not None

    @staticmethod
    def get_valid_account_number() -> str or None:
        """
        Gets a syntactically correct account number
        :return: Account number or None if cancel command inputted
        """
        while True:
            account_number = input(FrontEndInstance.input_account_number)
            if FrontEndInstance.valid_account_number(account_number):
                return account_number
            elif account_number == FrontEndInstance.Commands.cancel.value:
                return None
            else:
                print(FrontEndInstance.invalid_account_number)

    def get_account_number_in_list(self, prompt=input_account_number) -> str or None:
        """
        Gets a valid account number, validating against the accounts_list
        :param prompt: the user prompt to provide the user
        :return: The account number or None if exit command inputted
        """
        while True:
            account_number = input(prompt)
            if account_number in self.accounts_list:
                return account_number
            elif account_number == self.Commands.cancel.value:
                return None
            else:
                print(FrontEndInstance.error_account_not_found)

    @staticmethod
    def get_valid_account_name() -> str or None:
        """
        Gets a syntactically correct account name
        :return: a valid account name from user input or None if exit command inputted
        """
        while True:
            account_name = input(FrontEndInstance.input_account_name)
            if FrontEndInstance.valid_account_name(account_name):
                return account_name
            elif account_name == FrontEndInstance.Commands.cancel.value:
                return None
            else:
                print(FrontEndInstance.invalid_account_name)

    @staticmethod
    def get_valid_numeric_amount(max_value: int) -> str or None:
        """
        Get valid numeric string representing an amount of cents
        :param max_value: The max amount of cents to accept
        :return: a valid cents amount less than or equal to max value or None if exit command provided
        """
        while True:
            cents = input(FrontEndInstance.input_cents).replace(',', '')
            try:
                cents_int = int(cents)
                if cents_int <= max_value:
                    return str(cents_int)
                else:
                    print(FrontEndInstance.error_cents_less_than_or_equal(str(max_value)))
            except ValueError:
                if cents == FrontEndInstance.Commands.cancel.value:
                    return None
                print(FrontEndInstance.parse_number_error)


def main(accounts_file_input, transaction_summary_file_input):
    FrontEndInstance(accounts_file_input, transaction_summary_file_input).front_end_loop()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Invalid usage, must be of the format "frontend accounts_file.txt transaction_summary.txt"')
        exit(1)
    main(os.path.normpath(sys.argv[1]), os.path.normpath(sys.argv[2]))
