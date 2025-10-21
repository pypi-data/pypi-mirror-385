# New signup approval flow
So you need to change how we approve users on signup **in production**. There are a couple constance values that will need to be changed depending on the level of approval we want to require on user signup. 

Constance values can be modified [here on production](https://app.baseten.co/billip/constance/config/).

## 🟠 Manual approval
Constance values:
* `APPROVAL_METHOD` needs to be: 
  ```
  {
    "OUTBOUND_DOMAINS": false,
    "CLEARBIT_AND_PEOPLE_DATA_LABS": false, 
    "MINFRAUD_RISK_SCORE": false
  }
  ```

## 🟢 Auto-approval

### Using Clearbit and People Data Labs ONLY

Constance values:
* `APPROVAL_METHOD` needs to be: 
  ```
  {
    "OUTBOUND_DOMAINS": false,
    "CLEARBIT_AND_PEOPLE_DATA_LABS": true, 
    "MINFRAUD_RISK_SCORE": false
  }
  ```

### Using minFraud risk scores ONLY

Constance values:
* `APPROVAL_METHOD` needs to be: 
  ```
  {
    "OUTBOUND_DOMAINS": false,
    "CLEARBIT_AND_PEOPLE_DATA_LABS": false, 
    "MINFRAUD_RISK_SCORE": true
  }
  ```

### Using EITHER Outbound domains, Clearbit and People Data Labs, or minFraud risk scores

Constance values:
* `APPROVAL_METHOD` needs to be: 
  ```
  {
    "OUTBOUND_DOMAINS": true,
    "CLEARBIT_AND_PEOPLE_DATA_LABS": true, 
    "MINFRAUD_RISK_SCORE": true
  }
  ```


## minFraud risk scoring
It is worth noting that regardless of whether any `APPROVAL_METHOD`s are enabled, **we will always query minFraud for risk score data and save it**.

### Update minFraud risk score threshold
The default upper limit we use for minFraud risk scores is `50`. That can easily be updated by changing the `MINFRAUD_RISK_SCORE_THRESHOLD` constance. This value needs to be an integer, so the lowest value possible will be `1`. Read more about setting thresholds for minFraud risk scores [here](https://support.maxmind.com/hc/en-us/articles/4408220055195-Set-Thresholds-for-the-Risk-Score).
