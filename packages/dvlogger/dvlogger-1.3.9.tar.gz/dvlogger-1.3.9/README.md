# dvlogger (v1.3.9)

## Requirements

- colorama

## Todo

- `file_config.level` - Take list of multiple levels to create multiple files
- `file_config.file_mode` - Implement CSV
- Add `send_file` method to Telegram handler
- Asyncio patch - add support for `uvloop` (patch `asyncio.DefaultEventLoopPolicy.new_event_loop`) and other implementations

## Usage

```
import logging
import dvlogger

dvlogger.setup(level=logging.DEBUG, capture_warnings=True, exception_hook=True, use_tg_handler=False, use_file_handler=False, file_config=None, tg_config=None)
```

```
file_config
    name [os.path.basename(sys.argv[0]).strip(), dvlogger]
    kind [BASIC] # ROTATING, TIMED, BASIC
    level [logging.DEBUG]
    file_mode [text]

    rotating_size [1e6]
    rotating_count [3]

    timed_when ['midnight']
    timed_interval [1]
    timed_count [7]

    basic_date_format ['%Y_%m_%d_%H_%M%_S_%f']
    basic_put_date [False]
    basic_append [True]

tg_config
    level [logging.ERROR]
    level_bypass_prefix ["TG - "]
    message_skip_prefix ["NTG - "]
    bot_key
    chat_id
    thread_id [None]
    flush_interval [5000] # ms
```

## Cleanup

```
if dvlogger.TG_HANDLER:
    dvlogger.TG_HANDLER.stop()
```
