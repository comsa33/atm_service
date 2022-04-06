# atm_service
simple ATM service

## instruction for test
1. create environment (Python3.8)
```
conda create -n atm python=3.8
conda activate atm
```
2. execute `run.py` file
```
python run.py
```
3. under `./logs/` directory, log files will be saved after ATM service.
```
{
    "id": "ruo33",
    "name": "Ruo Lee",
    "transaction_start": "20220406Z143647",
    "transactions": {
        "123-456-789": {
            "transaction": {
                "20220406Z143649": "check_balance : 100000",
                "20220406Z143702": "withdraw : 300, balance : 99700",
                "20220406Z143715": "deposit : 250, balance : 99950",
                "20220406Z143720": "check_balance : 99950"
            }
        }
    }
}
```
