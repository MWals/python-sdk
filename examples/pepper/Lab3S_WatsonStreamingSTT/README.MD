# This Choregraphe projects shows how to use Watson Speech-To-Text streaming API
Copyright 2017 IBM All Rights Reserved.
## How to use
You will need to set-up your Watson STT API username and key.

The Watson STT python box is setup to get the Watson STT API key from either
  * the box parameters:  
![img-paste-20171218143216224.png](readme_images\theWatsonSTTPythonBoxIsSetupToGetTheWatsonSTTAPIKeyFromEitherTheBoxParameters.png)  
  * or from the ALPreferenceManager preferences' ```watson``` domain, that you can setup either through python code or from the robot shell using ```qicli``` command:
```
qicli call ALPreferenceManager.setValue 'watson' 'watsonSTTUsername' '125604b9-9876-ab12-1234-6bd0f53430e7'
qicli call ALPreferenceManager.setValue 'watson' 'watsonSTTPassword' 'rrVMTw0NcvLH'
```

## Operating principles
The code uses the ```arecord``` linux command to capture the audio stream from the robot's microphones, launched in raw mode as a subprocess. The raw audio data is captured from the subprocess's stdout pipe as a byte stream.

This audio stream is then funelled into the Watson STT websocket API using the ```ws4py``` package (see https://pypi.python.org/pypi/ws4py). The ```ws4py``` package is provisionned in the ```lib``` directory of the Choregraphe project which is itself added to the python ```sys.path```

This connection is implemented in the [StreamSTT.py](lib\StreamSTT.py) file through the ```WatsonSTTWebSocketClient``` subclass of ```WebSocketClient```. This class exposes 2 call-backs that can subsequently be overidden:
   * ``` received_transcript(self,final,confidence,transcript) ```
   * ``` info(self,msg) ```

## Tablet UI
The Pepper behavior displays a very simple Tablet UI that shows the spoken text as it is returned from the Watson STT API, both intermediate and final results are displayed.

This uses ```ALMemory``` keys to communicate with the main Choregraphe code.