import os
import sys

from frontend import TransactionSummary, TransactionSummaryKeys


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


def parse_master_account_file(file: str):
    accounts = {}
    with open(file, 'r') as fp:
        for line in fp:
            account_row = line.replace('\n', '').split(' ')
            accounts[account_row[0]] = (account_row[1], account_row[2])  # number, balance, name
    return accounts


def write_master_account_file(file: str, accounts):
    with open(file, 'w') as fp:
        fp.writelines(
            [key + " " + str(acct[0]) + " " + str(acct[1]) + "\n" for key, acct in reversed(sorted(accounts.items()))])


def parse_backend(master_accounts_file, merged_transaction_summary_file):
    # self.master_accounts_file = master_accounts_file
    # self.merged_transaction_summary_file = merged_transaction_summary_file
    transaction_summary = parse_to_summary_file(merged_transaction_summary_file)
    master_accounts = parse_master_account_file(master_accounts_file)
    for row in transaction_summary:
        if row.transaction_type == TransactionSummaryKeys.deposit:
            if row.to in master_accounts:
                # Because tuples are immutable it must replace the whole value
                master_accounts[row.to] = (int(master_accounts[row.to][0]) + int(row.cents), master_accounts[row.to][1])
        elif row.transaction_type == TransactionSummaryKeys.withdraw:
            if row.from_act in master_accounts:
                if int(master_accounts[row.from_act][0]) > int(row.cents):
                    master_accounts[row.from_act] = (
                        int(master_accounts[row.from_act][0]) - int(row.cents), master_accounts[row.from_act][1])
                else:
                    print("Can't transfer more money than account has")
        elif row.transaction_type == TransactionSummaryKeys.transfer:
            if row.from_act in master_accounts and row.to in master_accounts:
                if int(master_accounts[row.from_act][0]) > int(row.cents):
                    # Because tuples are immutable it must replace the whole value
                    master_accounts[row.from_act] = (
                        int(master_accounts[row.from_act][0]) - int(row.cents), master_accounts[row.from_act][1])
                    # Because tuples are immutable it must replace the whole value
                    master_accounts[row.to] = (
                        int(master_accounts[row.to][0]) + int(row.cents), master_accounts[row.to][1])
                else:
                    print("Can't withdraw more money than account has")
        elif row.transaction_type == TransactionSummaryKeys.createacct:
            if row.to not in master_accounts:
                # Add new account to list
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
