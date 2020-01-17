### Introduction

CN Final 2019

### Environment

For the setup:

```bash
git clone https://github.com/Ching-Chu-Lin/CN_Final2019.git 
cd 2019_CN_Final/
```

Run on Server:

```bash
./build_server.sh
```

Run on Client:

```bash
./build_client.sh
```

Usage:

```bash
# Register
>> reg
Register
Username:[username]
password:[password]

# Change Password
>> chg admin
Change Password
password:[old password]
new password:[new password]
new password confirm:[confirm]

# Login
>> login
Login
Username:[username]
password:[password]

# Logout
logout

# Show all Record
show

# Send Messages
send [text] [receiver] [content]
send [file] [receiver] [[content1] [content2]...] # available when receiver online

# Receive Messages
get [text or file] [person] [content]

# Exit
exit
```

### Sample

```bash
$ ./build_client.sh
sym at client: b'UG_FihMm0r_qn-bwi0-HPKzxjVi0LVpCv2saBuYy6b8='
>> reg
Register
Username:demo
password:
done
>> login
Login
Username:demo
password:
71f351649b62a110b442033f9f315f20
>> send text admin "I am demo"
done
>> send text demo "I am you"
done
>> send file demo ccf_pub.txt
done
>> show
+-------+---------------------+----------+-------------------+-----------+
|  User |         Time        |  Status  |      Message      | Direction |
+-------+---------------------+----------+-------------------+-----------+
|  demo | 2020-01-17 22:12:51 | (unread) | [file]ccf_pub.txt |    self   |
| admin | 2020-01-17 22:12:27 | (unread) |     I am demo     |    out    |
+-------+---------------------+----------+-------------------+-----------+
>> get text demo all
+---------------------+----------+-------------------+-----------+
|         Time        |  Status  |      Message      | Direction |
+---------------------+----------+-------------------+-----------+
| 2020-01-17 22:12:51 | (unread) | [file]ccf_pub.txt |    self   |
| 2020-01-17 22:12:39 | (unread) |      I am you     |    self   |
+---------------------+----------+-------------------+-----------+
>> get file demo ccf_pub.txt
done
>> exit
bye
```

### Feature

* Auto Reconnect
* Message Status
* Change Password
* Race Condition Avoid
* Password hiding
* List latest message for each user
* Encryption
