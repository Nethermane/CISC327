first_launch_message = 'Welcome to Quinterac banking, type login to begin'
unrecognized_command = 'Error: unrecognized command'
not_logged_in_message = 'In idle state, please login before use'
logged_out_logout_message = 'Error not logged in'
logged_in_login = 'Error: already logged in'
logout_message = 'Sucessfully logged out'
enter_command_text = 'Command: '
idle_state = 'idle'
atm_state = 'atm'
agent_state = 'machine'
cancel_command = 'q'
login_command = 'login'
logout_command = 'logout'
createacct_command = 'createacct'
deleteacct_command = 'deleteacct'
deposit_command = 'deposit'
withdraw_command = 'withdraw'
transfer_command = 'transfer'
help_command = 'help'
privileged_commands = [createacct_command, deleteacct_command]
atm_commands = [login_command, logout_command, deposit_command, withdraw_command, transfer_command]
help_text = 'Accepted commands: ' + ', '.join(atm_commands) + ', ' + ', '.join(privileged_commands)
login_message = 'Select session type ('+atm_state+' or '+agent_state + '): '
create_account_without_privilege = 'Error: ' + agent_state + ' session required for createacct command'
invalid_account_name = 'Error: invalid account name. Account number must be between 3 and 30 alphanumeric characters, not beginning or ending with a space'
account_number_input = 'Account Number: '
account_name_input = 'Account Name: '
invalid_account_number = 'Invalid account number, must be 7 digits, not beginning with a 0'
account_number_not_in_list = 'Error: accout number not found'
cents_value = 'Amount(cents): '
deposit_output_key = 'DEP'
withdraw_output_key = 'WDR'
transfer_output_key = 'XFR'
new_account_output_key = 'NEW'
delete_account_output_key = 'DEL'
end_of_file_key = 'EOS'
empty_account_number = '0000000'
empty_money_amount = '000'
empty_account_name = '***'
max_deposit_atm_once = 200000
max_deposit_atm_daily = 500000
max_deposit_teller_once = 99999999
max_withdraw_atm_once = 100000
max_withdraw_atm_daily = 500000
max_withdraw_agent_once = 99999999
max_transfer_atm_once = 1000000
max_transfer_atm_daily = 1000000
max_transfer_agent_once = 99999999
successful_deposit = 'Deposit successful'
successful_withdraw = 'Withdraw successful'
successful_delete = 'Delete sucessful'
deposit_over_max = 'Error: deposit over limit'
withdraw_over_max = 'Error: withdraw over limit'
from_account_prompt = 'From: '
to_account_prompt = 'To: '

parse_number_error = 'Error parsing input'
def successful_login(session_type):
    return 'Successfully logged in as "' + session_type +'"'
def unrecognized_login_command(command):
    return 'Error unrecognized command: "'+command+'", login with either ' + atm_state + ' or ' + agent_state
def must_be_signed_in_for_command(command):
    return 'Command: "' + command + '" requires logged in session'
def error_cents_less_than(max_value):
    return 'Error: must be less than or equal to ' + max_value + ' cents'
