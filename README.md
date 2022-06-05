# Discord Coding Challenge
🤖 A discord bot that send a new coding challenge everyday (C language)

## How to use it :

Firstly you need to configure your bot:

### config.json

|Field|Description|
|-|-|
|bot_token|The token of your discord bot.|
|channel|The ID of the channel where you want the game to be played.|
|schedule|The file that you want to use as planning of execises.|
|exercises|The folder where the exercises can be found.|
|hour|The hour of the day where the exercise will be sent|
|after_win|Time after the first win during which the correction will stay opened.|
|messages|Defining the messages that will be sent in the channel.|
|badges|Discord emojis according to exercises difficulties.|

### schedule.json

Each index must be a date in `dd/mm/yyyy` format.

The values must be set like this way:

```json
{
    "file": "path/to/exercise.json",
    "announced": false,
    "winner": null,
    "win_time": null
 }
 ```
 
 The three last values are used by the bot to remember datas about the exercise, let it as described.
 
 ### Exercise file
 
 This is an exercise file template:
 
 ```json
 {
    "title": "Exercise Title",
    "difficulty": "easy|medium|hard",
    "description": "Provide description and examples of your exercise in DiscordMD.",
    "allowed_functions": [
        "printf",
        "write"
    ],
    "proto": "Protoype arguments of the tested functions (eg: int a, int b)",
    "asserts": [
        {
            "args": "Arguments to test the function (eg: 0, 1)",
            "stdout": "Expected stdout",
            "return": 0
        }
    ]
}
```

## Security and limitations

### Allowed Functions

At the moment, the code submitted is compiled and run in the temp file of the bot's server. The program automatically timeout after 1s to prevent usebug or memory exploits.

Be careful when you allow functions, for exemple, avoid allowing of `system` or `execve` functions that can allow users to interact with the machine.

### Return assert

In the current version, the return value is checked using exit status of the program. So don't make asserts that expect a greater return value than 255 due to byte overflow.

If you want your user to return negative numbers or big numbers, prefer the stdout assert and ask user to print the result.

## How to play ?

The bot will send automatically the subject at the specified hour.

The players must send a code block message in the same channel containing inline code (no functions), if you provide arguments in the exercise file, the variables will directly be accessible by the code (no need to redeclare them).

Example: 
![](https://raw.githubusercontent.com/MathiDEV/discord_coding_challenge/main/Capture%20d%E2%80%99%C3%A9cran%20du%202022-06-05%2016-48-06.png)

Once the message is sent, the bot will correct the exercise and provide a result within a second.

When there is a winner, his ID will be stored in the schedule.json file, then you can use this data to give rewards on the server or maintain a top players list for example.
