#### Put the config file called `dev.ini`:
```
aws ssm put-parameter \
    --name /api/stock/dev.ini \
    --value "$(cat dev.ini)" \
    --type SecureString
```

---

#### Get the config file:
```
python extract-config.py | tee dev.ini
```
