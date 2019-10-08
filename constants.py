first_launch_message = 'Welcome to Quinterac banking, type login to begin'
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
privileged_commands = [createacct_command, deleteacct_command]
atm_commands = [login_command, logout_command, deposit_command, withdraw_command, transfer_command]
login_message = 'Select session type ('+atm_state+' or '+agent_state + '):'
def successful_login(session_type):
    return 'Successfully logged in as "' + session_type +'"'
def unrecognized_login_command(command):
    return 'Error unrecognized command: "'+command+'", login with either ' + atm_state + ' or ' + agent_state
