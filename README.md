[![Donate](https://img.shields.io/badge/donate-Coffee-yellow.svg)](https://www.buymeacoffee.com/renierm)
![Upload Python Package](https://github.com/RenierM26/pyHyypApi/workflows/Upload%20Python%20Package/badge.svg)

# pyHyypApi
API for ADT Secure Home and IDS Hyyp. There could be more variants but it's easy to add package names to the constants.py file.

How to use:

  1. Install:

```pip install pyHyypApi```

  2.1. Login (ADT Secure Home):


```
import pyhyypapi
import json
client = pyhyypapi.hyypclient(email="",password="")
client.login()
```

**OR**

  2.2. Login (IDT Hyyp):

```
import pyhyypapi
import json
client = pyhyypapi.hyypclient(email="",password="",pkg=pyhyypapi.HyypPkg.IDS_HYYP_GENERIC.value)
client.login()

```


3. Get site/partition/user/zone info:

```
print(json.dumps(client.get_sync_info(),indent=2))

```

TO Do:

- CLI usage. (GCF client is there, just needs some more automation.)
- Capture panic api...for obvious reasons.
- What zone caused arm/arm stay not to work. - Looks like GCM/Firebase push messages. Added GCM client...just run main program and register GCF code in function called register gcf. It works.
