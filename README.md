### Introduction

CN Final 2019

### Environment

For the setup:

```bash
git clone https://github.com/hc07180011/mainpage.git
cd mainpage/2019_CN_Final/
```

Run:

```bash
python3 client.py
```

Usage:

```bash
#Account
reg [account] [password]
chg [account] [pasword] [new password]
login [account] [password]
logout
#Send
send [text] [receiver] [content]
send [file] [receiver] [[content1] [content2]...] # available when receiver online
#Get
get [text or file] [person] [content]
#Exit
exit
```

### Sample

```bash
>> reg test test
done
>> login test test
2cf22a2d436117649286ebafe915c624
>> send text admin "Hello I am test"               
done
>> get text admin all
Message History:
[out ] 2019-12-25 15:33:56 (unread):Hello I am test
>>  logout
you have logged out
```

### Feature

* Auto Reconnect
* Message Status
* Change Password
* Race Condition Avoid
