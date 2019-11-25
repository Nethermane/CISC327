import os
import sys

from frontend import TransactionSummary, TransactionSummaryKeys

'''
Overall, the backend takes in the previous day’s master accounts file and then applies all of
the transactions in the merged transaction summary file to the accounts to produce today’s new
master accounts file. It also produces a new valid accounts list for tomorrow’s Front End runs,
as accounts may be added or deleted. The backend is intended to run every, after a full day of
transactions is complete (this could be done using a script for example).
'''


# Takes in the merged transaction summary file and parses it's contents to build a TransactionSummary object to return.
def parse_to_summary_file(file: str):
    summary = TransactionSummary()
    with open(file, 'r') as fp:
        for line in fp:
            transaction_row = line.replace('\n', '').split(' ')
            if transaction_row[0] == TransactionSummaryKeys.end_of_file:
                return summary
            summary.add_row(TransactionSummaryKeys(transaction_row[0]), transaction_row[1], transaction_row[2],
                            transaction_row[3], transaction_row[4])
    return summary


# Takes in the old master accounts file and parses it's contents, making a dictionary of accounts which is returned
def parse_master_account_file(file: str):
    accounts = {}
    with open(file, 'r') as fp:
        for line in fp:
            account_row = line.replace('\n', '').split(' ')
            accounts[account_row[0]] = (account_row[1], account_row[2])  # number, balance, name
    return accounts


# Writes the contents of the accounts dictionary (parameter) to the new master accounts file (filename passed in).
def write_master_account_file(file: str, accounts):
    with open(file, 'w') as fp:
        fp.writelines(
            [key + " " + str(acct[0]) + " " + str(acct[1]) + "\n" for key, acct in reversed(sorted(accounts.items()))])


# Writes the new accounts file
def write_new_valid_accounts_file(accounts):
    with open("valid_accounts.txt", 'w') as fp:
        fp.writelines([key + "\n" for key, acct in reversed(sorted(accounts.items()))])
        fp.write('0000000\n')


# Takes in the old master accounts file and merged transaction summary file, and calls the function to parse them.
# Then, for each transaction, the transaction type is checked to determine the action needed to appropriately update 
# the master accounts. write_master_account_file is called, being passed the path to the old master accounts file, and
# the contents to be written to the new master accounts file. 
def parse_backend(master_accounts_file, merged_transaction_summary_file):
    transaction_summary = parse_to_summary_file(merged_transaction_summary_file)
    master_accounts = parse_master_account_file(master_accounts_file)
    for row in transaction_summary:
        if row.transaction_type == TransactionSummaryKeys.deposit:
            if row.to in master_accounts:
                # Because tuples are immutable it must replace the whole value
                master_accounts[row.to] = (int(master_accounts[row.to][0]) + int(row.cents), master_accounts[row.to][1])
        elif row.transaction_type == TransactionSummaryKeys.withdraw:
            if row.from_act in master_accounts:
                if int(master_accounts[row.from_act][0]) >= int(row.cents):
                    master_accounts[row.from_act] = (
                        int(master_accounts[row.from_act][0]) - int(row.cents), master_accounts[row.from_act][1])
                else:
                    print("Can't withdraw more money than account has")
        elif row.transaction_type == TransactionSummaryKeys.transfer:
            if row.from_act in master_accounts and row.to in master_accounts:
                if int(master_accounts[row.from_act][0]) >= int(row.cents):
                    # Because tuples are immutable it must replace the whole value
                    master_accounts[row.from_act] = (
                        int(master_accounts[row.from_act][0]) - int(row.cents), master_accounts[row.from_act][1])
                    # Because tuples are immutable it must replace the whole value
                    master_accounts[row.to] = (
                        int(master_accounts[row.to][0]) + int(row.cents), master_accounts[row.to][1])
                else:
                    print("Can't transfer more money than account has")
        elif row.transaction_type == TransactionSummaryKeys.createacct:
            if row.to not in master_accounts:
                # Add new account to list
                master_accounts[row.to] = (0, row.name)
            else:
                print('Error: account already exists')
        elif row.transaction_type == TransactionSummaryKeys.deleteacct:
            if row.to in master_accounts:
                if row.name == master_accounts[row.to][1]:
                    if int(master_accounts[row.cents][0]) == 0:
                        del master_accounts[row.to]
                    else:
                        print("Can't delete an account with a non-zero balance")
                else:
                    print("Account name didn't match delete command")
    write_master_account_file(master_accounts_file, master_accounts)
    write_new_valid_accounts_file(master_accounts)


# Calls parse_backend, passing in the paths to the merged transaction summary file and the old master accounts file.
def main():
    parse_backend(os.path.normpath(sys.argv[1]), os.path.normpath(sys.argv[2]))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Invalid usage, must be of the format "backend master_accounts_file.txt merged_transaction_summary.txt"')
        exit(1)
    main()
