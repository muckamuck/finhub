#### The URL for this service:
```
https://finnhub.io/docs/api/quote
```

#### Put the config file called `dev.ini`:
```
cd stocks/config
aws ssm put-parameter \
    --name /api/stock/dev.ini \
    --value "$(cat dev.ini)" \
    --type SecureString
```

---

#### Get the config file:
```
cd stocks/config
python extract-config.py | tee dev.ini
```


#### Deploy the function:
```
cd stocks/
lambdautil deploy -f config/dev.ini
```
