# lmh config

lmh config is used to configure different settings for lmh.

All config settings are stored in  the file bin/lmh.cfg relative to the root directory of the lmh installation in json format.

To view all available config settings, use:

```bash
lmh config
```

To get information about a specific config settings, use:

```bash
lmh config name_of_setting
```

To change a config setting, use:

```bash
lmh config name_of_setting new_value
```

In addition, a config setting can be rese to the default value:

```bash
lmh config --reset name_of_setting
```

If you want to reset all config settings, use:

```bash
lmh config --reset-all
```
# List of config settings

Name  | Help | Type | Default
------------ | ------------- | ------------
Content Cell | Content Cell  | Content Cell | null
Content Cell | Content Cell  | Content Cell | null
