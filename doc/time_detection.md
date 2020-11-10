# Time Detection

The [OnEarth Time Service](../src/modules/time_service/utils/README.md) has the ability to detect time ranges for a given layer.  This is accomplished by the use of special keywords in the [layer configuration file](configuration.md).

## Time Element Options

1) Known date range in ISO 8601 format with start time, end time, and duration.
```json
time_config: "2013-01-01/2014-03-28/P1D"
```

2) Automatically detect the start time, end time, and duration.
```json
time_config: "DETECT"
```

3) Automatically detect only the start time.
```json
time_config: "DETECT/2014-03-28/P1D"
```

4) Automatically detect only the end time.
```json
time_config: "2013-01-01/DETECT/P1D"
```

5) Automatically detect the start and end times but use a predetermined period.
```json
time_config: "DETECT/DETECT/P5D"
```

6) Automatically detect the start and end times but use a predetermined period; create multiple date ranges if breaks are detected.
```json
time_config: "DETECT/P5D"
```

Sub-daily periods are also supported.
```json
time_config: "2000-01-01T00:00:00Z/DETECT/PT5M"
```

Note: The period detection is determined by the first two intervals in the image archive for the given layer.  Time detection may not be accurate if there are less than three files or if they are not continuous.