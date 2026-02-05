FOR /L %%i IN (1,1,254) DO (
    ping -n 1 172.16.101.%%i | FIND /i "Reply">>c:\ipaddresses.txt
)