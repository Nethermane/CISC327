import constants
import re
import os.path
import sys


class FrontEndInstance(object):

    def __init__(self, accounts_file: str, transaction_summary_file: str):
        self.accounts_file = accounts_file
        self.transaction_summary_file = transaction_summary_file
        self.user_status = constants.idle_state
        self.current_file_output = []
        self.accounts_list = []

    def front_end_loop(self):
        print(constants.first_launch_message)
        while True:
            user_command = input(constants.enter_command_text)
            parsed_command = user_command.lower().strip()
            # Prevent all commands but login before logging in
            if self.user_status == constants.idle_state and parsed_command != constants.login_command:
                print(constants.not_logged_in_message)
            # login
            elif user_command == constants.login_command:
                self.login()
            # logout
            elif user_command == constants.logout_command:
                self.logout()
            # createacct
            elif user_command == constants.createacct_command:
                self.create_account()
            # deleteacct
            elif user_command == constants.deleteacct_command:
                self.delete_account()
            # deposit
            elif user_command == constants.deposit_command:
                self.deposit()
            # withdraw
            elif user_command == constants.withdraw_command:
                self.withdraw()
            # transfer
            elif user_command == constants.transfer_command:
                self.transfer()
            elif user_command == constants.help_command:
                print(constants.help_text)
            else:
                print(constants.unrecognized_command)

    def login(self):
        if self.user_status != constants.idle_state:
            print(constants.logged_in_login)
            return
        while True:
            user_input = input(constants.login_message)
            parsed_login = user_input.lower().strip()
            if parsed_login in [constants.atm_state, constants.agent_state]:
                self.user_status = parsed_login
                print(constants.successful_login(parsed_login))
                with open(self.accounts_file) as fp:
                    self.accounts_list = fp.readlines()
                return
            elif parsed_login == constants.cancel_command:
                return
            else:
                self.user_status = constants.idle_state
                print(constants.unrecognized_login_command(user_input))

    def logout(self):
        if self.user_status == constants.idle_state:
            print(constants.logged_out_logout_message)
            return
        else:
            print(constants.logout_message)
            self.current_file_output.append([constants.end_of_file_key,
                                             constants.empty_account_number,
                                             constants.empty_money_amount,
                                             constants.empty_account_number,
                                             constants.empty_account_name
                                             ])
            with open(self.transaction_summary_file, 'w') as fp:
                for transaction in self.current_file_output:
                    fp.write(' '.join(transaction) + '\n')
                    self.current_file_output = []
            self.user_status = constants.idle_state

    def create_account(self):
        if self.user_status != constants.agent_state:
            print(constants.create_account_without_privilege)
            return
        account_number = self.get_valid_account_number()
        if account_number is None:
            return
        account_name = self.get_valid_account_name()
        if account_name is None:
            return
        self.current_file_output.append([constants.new_account_output_key,
                                         account_number,
                                         constants.empty_money_amount,
                                         constants.empty_account_number,
                                         account_name
                                         ])
        print(constants.successful_delete)

    def delete_account(self):
        if self.user_status != constants.agent_state:
            print(constants.create_account_without_privilege)
            return
        account_number = self.get_valid_account_number()
        if account_number is None:
            return
        account_name = self.get_valid_account_name()
        if account_name is None:
            return
        self.current_file_output.append([constants.delete_account_output_key,
                                         account_number,
                                         constants.empty_money_amount,
                                         constants.empty_account_number,
                                         account_name
                                         ])
        print(constants.successful_delete)

    def deposit(self):
        if self.user_status == constants.idle_state:
            print(constants.must_be_signed_in_for_command(constants.deposit_command))
            return
        account_number = self.get_account_number_in_list()
        # Check number less than max single transaction
        cents = FrontEndInstance.get_valid_numeric_amount(
            constants.max_deposit_atm_once if self.user_status == constants.atm_state else constants.max_deposit_teller_once)
        if cents is None:
            return
        # Check if total deposits that day less than total
        if (self.user_status == constants.agent_state or self.total_less_than_daily_limit(constants.deposit_output_key,
                                                                                          account_number,
                                                                                          constants.max_deposit_atm_daily)):
            self.current_file_output.append([constants.deposit_output_key,
                                             account_number,
                                             cents,
                                             constants.empty_account_number,
                                             constants.empty_account_name
                                             ])
            print(constants.successful_deposit)
        else:
            print(constants.deposit_over_max)

    def withdraw(self):
        if self.user_status == constants.idle_state:
            print(constants.must_be_signed_in_for_command(constants.withdraw_command))
            return
        account_number = self.get_account_number_in_list()
        # Check number less than max single transaction
        cents = FrontEndInstance.get_valid_numeric_amount(
            constants.max_withdraw_atm_once if self.user_status == constants.atm_state
            else constants.max_withdraw_agent_once)
        if cents is None:
            return
        # Check if total withdrawl less than total limit
        if (self.user_status == constants.agent_state or self.total_less_than_daily_limit(constants.withdraw_output_key,
                                                                                          account_number,
                                                                                          constants.max_withdraw_atm_daily)):
            self.current_file_output.append([constants.deposit_output_key,
                                             constants.empty_account_number,
                                             cents,
                                             account_number,
                                             constants.empty_account_name
                                             ])
            print(constants.successful_withdraw)
        else:
            print(constants.withdraw_over_max)

    def transfer(self):
        if self.user_status == constants.idle_state:
            print(constants.must_be_signed_in_for_command(constants.withdraw_command))
            return
        from_account = self.get_account_number_in_list()
        to_account = self.get_account_number_in_list()
        # Check number less than max single transaction
        cents = self.get_valid_numeric_amount(
            constants.max_transfer_atm_once if self.user_status == constants.atm_state else constants.max_transfer_agent_once)
        if cents is None:
            return
        # Check if total withdrawl less than total limit
        if (self.user_status == constants.agent_state or self.total_less_than_daily_limit(constants.transfer_output_key,
                                                                                          from_account,
                                                                                          constants.max_transfer_atm_once)):
            self.current_file_output.append([constants.deposit_output_key,
                                             to_account,
                                             cents,
                                             from_account,
                                             constants.empty_account_name
                                             ])
            print(constants.successful_withdraw)
        else:
            print(constants.withdraw_over_max)

    @staticmethod
    def valid_account_name(name: str):
        return name is not None and re.search('^[\w][\w ]{1,28}[\w]$', name) is not None

    @staticmethod
    def valid_account_number(number: str):
        return number is not None and re.search('^[1-9][0-9]{6}$', number) is not None

    @staticmethod
    def valid_cents_amount(number: int, max_value: int):
        return number is not None and number <= max_value

    # Determines if account has had more than specified limit amount of transactions done to it
    def total_less_than_daily_limit(self, output_key: str, account_number: str, limit: int):
        account_num_pos = 3 if output_key in [constants.transfer_output_key, constants.withdraw_output_key] else 1
        return sum(
            map(lambda row: int(row[2]),
                filter(lambda row: row[0] == output_key and account_number == row[account_num_pos],
                       self.current_file_output))) <= limit

    # returns a valid account number from user input
    # If check_accounts_list is True, requires the number to be in the accounts list
    # returns None if exit command is provided
    @staticmethod
    def get_valid_account_number():
        while True:
            account_number = input(constants.account_number_input)
            if FrontEndInstance.valid_account_number(account_number):
                return account_number
            elif account_number == constants.cancel_command:
                return None
            else:
                print(constants.invalid_account_number)

    def get_account_number_in_list(self):
        while True:
            account_number = input(constants.account_number_input)
            if account_number in self.accounts_list:
                return account_number
            elif account_number == constants.cancel_command:
                return None
            else:
                print(constants.account_number_not_in_list)

    # returns a valid account name from user input
    # returns None if exit command is provided
    @staticmethod
    def get_valid_account_name():
        while True:
            account_name = input(constants.account_name_input)
            if FrontEndInstance.valid_account_name(account_name):
                return account_name
            elif account_name == constants.cancel_command:
                return None
            else:
                print(constants.invalid_account_name)

    # returns a valid cents amount less than or equal to max value
    # returns None if exit command provided
    # returns a string, ensuring it is validly numeric.
    @staticmethod
    def get_valid_numeric_amount(max_value: int):
        while True:
            cents = input(constants.cents_value).replace(',', '')
            try:
                cents_int = int(cents)
                if FrontEndInstance.valid_cents_amount(cents_int, max_value):
                    return str(cents_int)
                else:
                    print(constants.error_cents_less_than(str(max_value)))
            except ValueError:
                if cents == constants.cancel_command:
                    return None
                print(constants.parse_number_error)


def main(front_end_instance: FrontEndInstance):
    front_end_instance.front_end_loop()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Invalid usage, must be of the format "frontend accounts_file.txt transaction_summary.txt"')
        exit(1)
    accounts_file_input = os.path.normpath(sys.argv[1])
    transaction_summary_file_input = os.path.normpath(sys.argv[2])
    main(FrontEndInstance(accounts_file_input, transaction_summary_file_input))
