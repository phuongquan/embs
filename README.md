# EMBS Urban Nature Garden

Environmental monitoring of allotment space used by EMBS Community College. Part of Science Together: Oxford Researchers and Communities 2022/23.

## Deployment to pythonanywhere.com

For dash apps, start with a flask app then update the WSGI configuration file, replacing

```
from app import app as application
```

with

```
from app import app
application = app.server
```
