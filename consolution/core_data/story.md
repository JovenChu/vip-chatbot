## story greet
* greet
  - utter_greet

## story goodbye
* goodbye
  - utter_goodbye

## story greet goodbye
* greet
  - utter_greet
* goodbye
  - utter_goodbye

## story inform num
* inform_num{"num":"1"} OR inform_num{"num":"2"} OR inform_num{"num":"3"} OR inform_num{"num":"4"} OR inform_num{"num":"5"} OR inform_num{"num":"6"} OR inform_num{"num":"7"} OR inform_num{"num":"8"} OR inform_num{"num":"9"} OR inform_num{"num":"0"}
  - Numaction

## story banka_fangshi
* banka_fangshi
  - Bankafangshi

## story chaxun_work with kind
* chaxun_work{"bill_item":"订单"}  OR chaxun_work{"bill_item":"余额"} OR chaxun_work{"bill_item":"明细"} 
  - Chaxunwork

## story chaxun_work without kind 1
* chaxun_work
  - utter_ask_chaxun
* inform_chaxun{"bill_item":"订单"}  OR inform_chaxun{"bill_item":"余额"} OR inform_chaxun{"bill_item":"明细"}
  - Chaxunwork

## story chaxun_work without kind 2
* chaxun_work
  - utter_ask_chaxun
* chaxun_work{"bill_item":"订单"}  OR chaxun_work{"bill_item":"余额"} OR chaxun_work{"bill_item":"明细"} 
  - Chaxunwork

## story use_fanwei
* use_fanwei
  - Usefanwei
