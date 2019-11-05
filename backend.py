import os
import sys

from frontend import TransactionSummary, TransactionSummaryKeys


def parse_to_summary_file(file: str):
    summary = TransactionSummary()
    with open(file, 'r') as fp:
        for line in fp.readline():
            transaction_row = line.split(' ')
            if transaction_row[0] == TransactionSummaryKeys.end_of_file:
                return summary
            summary.add_row(TransactionSummaryKeys(transaction_row[0]), transaction_row[1], transaction_row[2],
                            transaction_row[3])


def parse_master_account_file(file: str):
    accounts = {}
    with open(file, 'r') as fp:
        for line in fp.readline():
            account_row = line.split(' ')
            accounts[account_row[0]] = (account_row[1], account_row[2])  # number, balance, name
    return accounts


def write_master_account_file(file: str, accounts):
    with open(file, 'w') as fp:
        fp.writelines([key + " " + acct[0] + " " + acct[1] for key, acct in accounts.items()])


def parse_backend(master_accounts_file, merged_transaction_summary_file):
    # self.master_accounts_file = master_accounts_file
    # self.merged_transaction_summary_file = merged_transaction_summary_file
    transaction_summary = parse_to_summary_file(merged_transaction_summary_file)
    master_accounts = parse_master_account_file(master_accounts_file)
    for row in transaction_summary:
        if row is TransactionSummary.TransactionSummaryRow:
            if row.transaction_type == TransactionSummaryKeys.deposit:
                if row.to in master_accounts:
                    master_accounts[row.to][0] = int(master_accounts[row.to][0]) + int(row.cents)
            elif row.transaction_type == TransactionSummaryKeys.withdraw:
                if row.from_act in master_accounts:
                    if int(master_accounts[row.from_act][0]) > int(row.cents):
                        master_accounts[row.from_act][0] = int(master_accounts[row.from_act][0]) - int(row.cents)
                    else:
                        print("Can't transfer more money than account has")
            elif row.transaction_type == TransactionSummaryKeys.transfer:
                if row.from_act in master_accounts and row.to in master_accounts:
                    if int(master_accounts[row.from_act][0]) > int(row.cents):
                        master_accounts[row.from_act][0] = int(master_accounts[row.from_act][0]) - int(row.cents)
                        master_accounts[row.to][0] = int(master_accounts[row.to][0]) + int(row.cents)
                    else:
                        print("Can't withdraw more money than account has")
            elif row.transaction_type == TransactionSummaryKeys.createacct:
                if row.to not in master_accounts:
                    master_accounts[row.to] = (0, row.name)
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


def main():
    parse_backend(os.path.normpath(sys.argv[1]), os.path.normpath(sys.argv[2]))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Invalid usage, must be of the format "backend master_accounts_file.txt merged_transaction_summary.txt"')
        exit(1)
    main()
